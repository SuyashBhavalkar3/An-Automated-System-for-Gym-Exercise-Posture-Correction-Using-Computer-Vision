import { useState, useEffect, useCallback, useRef } from 'react';

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface PoseMessage {
  type: 'frame';
  exercise: string;
  image: string; // base64 encoded frame
}

export interface PoseResponse {
  status: 'ok' | 'no_pose' | 'incorrect';
  feedback: string;
  confidence?: number;
}

interface UseWebSocketReturn {
  status: ConnectionStatus;
  feedback: PoseResponse | null;
  connect: () => void;
  disconnect: () => void;
  sendFrame: (base64Image: string, exercise: string) => void;
  error: string | null;
}

function resolveWebSocketUrl(): string {
  // Prefer explicit Vite env override: VITE_WS_URL
  // Otherwise derive from current location and default backend port 8000
  // Example result: ws://localhost:8000/ws/posture or wss://example.com/ws/posture
  // Vite exposes env vars via import.meta.env
  const envUrl = (import.meta as any).env?.VITE_WS_URL;
  if (envUrl) return envUrl;

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const hostFromEnv = (import.meta as any).env?.VITE_API_HOST;
  const portFromEnv = (import.meta as any).env?.VITE_API_PORT;

  let host: string;
  if (hostFromEnv) {
    host = hostFromEnv + (portFromEnv ? `:${portFromEnv}` : '');
  } else {
    // If frontend served from a different port, backend likely on 8000 during dev
    const frontendHost = window.location.hostname;
    const backendPort = portFromEnv || '8000';
    host = `${frontendHost}:${backendPort}`;
  }

  return `${protocol}://${host}/ws/posture`;
}

export function useWebSocket(): UseWebSocketReturn {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [feedback, setFeedback] = useState<PoseResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    cleanup();
    setStatus('connecting');
    setError(null);

    try {
      const ws = new WebSocket(resolveWebSocketUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
        setError(null);
      };

      ws.onclose = () => {
        setStatus('disconnected');
        wsRef.current = null;
      };

      ws.onerror = () => {
        setStatus('error');
        setError('Failed to connect to posture detection server. Ensure backend is running.');
        wsRef.current = null;
      };

      ws.onmessage = (event) => {
        try {
          const response: PoseResponse = JSON.parse(event.data);
          setFeedback(response);
        } catch {
          console.error('Failed to parse WebSocket message');
        }
      };
    } catch {
      setStatus('error');
      setError('Failed to create WebSocket connection');
    }
  }, [cleanup]);

  const disconnect = useCallback(() => {
    cleanup();
    setStatus('disconnected');
    setFeedback(null);
  }, [cleanup]);

  const sendFrame = useCallback((base64Image: string, exercise: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      // Backend expects keys: exercise and frame
      const payload = {
        exercise,
        frame: base64Image,
      } as const;
      wsRef.current.send(JSON.stringify(payload));
    }
  }, []);

  useEffect(() => {
    return () => cleanup();
  }, [cleanup]);

  return {
    status,
    feedback,
    connect,
    disconnect,
    sendFrame,
    error,
  };
}
