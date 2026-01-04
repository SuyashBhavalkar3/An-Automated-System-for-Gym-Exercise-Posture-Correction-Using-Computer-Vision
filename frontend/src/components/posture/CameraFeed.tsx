import { useEffect, useRef } from 'react';
import { Camera, CameraOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCamera } from '@/hooks/useCamera';

interface CameraFeedProps {
  onFrame?: (base64Image: string) => void;
  isCapturing: boolean;
  captureInterval?: number; // ms between captures
  showSkeleton?: boolean;
  skeletonUrl?: string | null; // object URL to draw over video
  verbose?: boolean;
}

export function CameraFeed({ onFrame, isCapturing, captureInterval = 200, showSkeleton = true, skeletonUrl = null, verbose = false }: CameraFeedProps) {
  const { videoRef, canvasRef, isStreaming, error, startCamera, stopCamera, captureFrame } = useCamera();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const overlayRef = useRef<HTMLCanvasElement | null>(null);
  const lastSkeletonUrlRef = useRef<string | null>(null);

  // Handle frame capture
  useEffect(() => {
    if (isCapturing && isStreaming && onFrame) {
      intervalRef.current = setInterval(() => {
        const frame = captureFrame();
        if (frame) {
          onFrame(frame);
        }
      }, captureInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isCapturing, isStreaming, onFrame, captureFrame, captureInterval]);

  // Draw skeleton overlay when skeletonUrl changes
  useEffect(() => {
    const overlay = overlayRef.current;
    const video = videoRef.current;
    if (!overlay || !video) return;

    const ctx = overlay.getContext('2d');
    if (!ctx) return;

    let img: HTMLImageElement | null = null;
    if (!showSkeleton) {
      ctx.clearRect(0, 0, overlay.width, overlay.height);
      return;
    }

    if (!skeletonUrl) {
      // nothing to draw
      ctx.clearRect(0, 0, overlay.width, overlay.height);
      return;
    }

    // Only update if url changed
    if (lastSkeletonUrlRef.current === skeletonUrl) return;
    lastSkeletonUrlRef.current = skeletonUrl;

    img = new Image();
    img.onload = () => {
      // maintain overlay size
      overlay.width = video.videoWidth;
      overlay.height = video.videoHeight;
      ctx.clearRect(0, 0, overlay.width, overlay.height);
      // draw skeleton image stretched to overlay
      ctx.drawImage(img!, 0, 0, overlay.width, overlay.height);
    };
    img.src = skeletonUrl;

    return () => { img = null; };
  }, [skeletonUrl, showSkeleton, verbose, videoRef]);

  // Keep overlay canvas sized to video when streaming
  useEffect(() => {
    const overlay = overlayRef.current;
    const video = videoRef.current;
    if (!overlay || !video) return;
    const resize = () => {
      overlay.width = video.videoWidth || overlay.clientWidth;
      overlay.height = video.videoHeight || overlay.clientHeight;
    };
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, [isStreaming]);

  return (
    <div className="relative w-full aspect-video bg-card rounded-xl overflow-hidden border border-border">
      {/* Video element */}
      <video
        ref={videoRef}
        className={`w-full h-full object-cover ${isStreaming ? 'block' : 'hidden'}`}
        autoPlay
        playsInline
        muted
      />

      {/* Overlay canvas for skeleton rendering (drawn from server images) */}
      <canvas ref={overlayRef} className="absolute inset-0 w-full h-full pointer-events-none" />

      {/* Hidden canvas for frame capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Overlay when not streaming */}
      {!isStreaming && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-secondary/50">
          {error ? (
            <>
              <CameraOff className="h-12 w-12 text-destructive mb-4" />
              <p className="text-destructive text-center px-4 mb-4">{error}</p>
              <Button onClick={startCamera} variant="outline">
                Try Again
              </Button>
            </>
          ) : (
            <>
              <Camera className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-4">Camera not started</p>
              <Button onClick={startCamera}>
                <Camera className="mr-2 h-4 w-4" />
                Start Camera
              </Button>
            </>
          )}
        </div>
      )}

      {/* Recording indicator */}
      {isStreaming && isCapturing && (
        <div className="absolute top-4 left-4 flex items-center gap-2 bg-destructive/90 text-destructive-foreground px-3 py-1.5 rounded-full text-sm font-medium">
          <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
          Analyzing
        </div>
      )}

      {/* Camera controls */}
      {isStreaming && (
        <div className="absolute bottom-4 right-4">
          <Button
            variant="secondary"
            size="sm"
            onClick={stopCamera}
          >
            <CameraOff className="mr-2 h-4 w-4" />
            Stop Camera
          </Button>
        </div>
      )}

      {/* Connecting overlay */}
      {!isStreaming && !error && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <Loader2 className="h-8 w-8 text-primary animate-spin opacity-0" />
        </div>
      )}
    </div>
  );
}
