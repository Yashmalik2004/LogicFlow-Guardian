import { createContext, useState, useEffect, ReactNode } from 'react';
import { loginUser, registerUser, getCurrentUser, AuthUser, LoginPayload, RegisterPayload } from '../services/authService';

export interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // On mount, try to restore session from stored JWT
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    getCurrentUser()
      .then((res) => {
        if (res.success && res.data) {
          setUser({
            userId: res.data.userId as number,
            name: (res.data as AuthUser).name,
            email: (res.data as AuthUser).email,
          });
          setToken(storedToken);
        } else {
          // Token invalid — clear storage
          localStorage.removeItem('authToken');
          setToken(null);
        }
      })
      .catch(() => {
        localStorage.removeItem('authToken');
        setToken(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  async function login(payload: LoginPayload): Promise<void> {
    const res = await loginUser(payload);
    if (!res.success || !res.data?.token || !res.data?.user) {
      throw new Error(res.message || 'Login failed.');
    }
    localStorage.setItem('authToken', res.data.token);
    setToken(res.data.token);
    setUser(res.data.user);
  }

  async function register(payload: RegisterPayload): Promise<void> {
    const res = await registerUser(payload);
    if (!res.success) {
      throw new Error(res.message || 'Registration failed.');
    }
  }

  function logout(): void {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
  }

  const value: AuthContextValue = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
