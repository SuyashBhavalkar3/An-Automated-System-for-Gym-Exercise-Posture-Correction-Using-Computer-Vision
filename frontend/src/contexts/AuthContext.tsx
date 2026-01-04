import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (email: string, password: string, name: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<{ success: boolean; error?: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY = 'posture_ai_user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load stored session (user + token)
    const storedUser = localStorage.getItem(STORAGE_KEY);
    const storedToken = localStorage.getItem('posture_ai_token');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    if (storedToken) {
      // token present; could validate or refresh if backend provides endpoint
    }
    setIsLoading(false);
  }, []);

  const apiBase = (): string => {
    const env = (import.meta as any).env || {};
    return env.VITE_API_BASE_URL || `http://localhost:${env.VITE_API_PORT || '8000'}`;
  };

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    if (!email || !password) {
      return { success: false, error: 'Email and password are required' };
    }

    try {
      const resp = await fetch(`${apiBase()}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        return { success: false, error: err.detail || 'Invalid credentials' };
      }

      const data = await resp.json();
      const token = data.access_token || data.token || null;
      if (token) {
        localStorage.setItem('posture_ai_token', token);
      }

      // Minimal user info (backend login doesn't return user object here)
      const loggedUser: User = {
        id: crypto.randomUUID(),
        email,
        name: email.split('@')[0],
      };

      setUser(loggedUser);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(loggedUser));

      return { success: true };
    } catch (err: any) {
      return { success: false, error: err?.message || 'Network error' };
    }
  };

  const signup = async (email: string, password: string, name: string): Promise<{ success: boolean; error?: string }> => {
    if (!email || !password || !name) {
      return { success: false, error: 'All fields are required' };
    }

    try {
      const resp = await fetch(`${apiBase()}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        return { success: false, error: err.detail || 'Registration failed' };
      }

      const createdUser = await resp.json();

      // After successful signup, automatically log in to get token
      const loginResult = await login(email, password);
      if (!loginResult.success) {
        return { success: false, error: 'Registration succeeded but login failed' };
      }

      setUser({ id: String(createdUser.id || crypto.randomUUID()), email: createdUser.email, name: createdUser.name });
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ id: String(createdUser.id || ''), email: createdUser.email, name: createdUser.name }));

      return { success: true };
    } catch (err: any) {
      return { success: false, error: err?.message || 'Network error' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem('posture_ai_token');
  };

  const forgotPassword = async (email: string): Promise<{ success: boolean; error?: string }> => {
    // Keep previous mock behaviour; integrate with backend if available
    await new Promise(resolve => setTimeout(resolve, 800));

    if (!email) {
      return { success: false, error: 'Email is required' };
    }

    return { success: true };
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout, forgotPassword }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
