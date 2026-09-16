import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api, TOKEN_KEY, type BackendUser } from '../services/api';

export type UserRole = 'admin' | 'consultor' | 'cliente';

interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  createdAt: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const USER_KEY = 'ecoregion_user';

function toUser(data: BackendUser): User {
  return {
    id: data.id,
    email: data.email,
    name: data.nombre,
    role: (['admin', 'consultor', 'cliente'] as UserRole[]).includes(data.rol as UserRole)
      ? (data.rol as UserRole)
      : 'cliente',
    createdAt: data.creado_en,
  };
}

function authError(err: unknown, fallback: string): Error {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response?: { status?: number; data?: { detail?: unknown } } }).response;
    const detail = response?.data?.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((d) => (typeof d === 'object' && d && 'msg' in d ? String((d as { msg: unknown }).msg) : JSON.stringify(d))).join('. ')
        : fallback;
    if (response?.status === 401) return new Error('Email o contraseña incorrectos.');
    if (response?.status === 409) return new Error('Ya existe un usuario con ese email.');
    return new Error(message || fallback);
  }
  return new Error('Error de conexión. Verifica que el backend esté disponible.');
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem(USER_KEY);
    const token = localStorage.getItem(TOKEN_KEY);
    if (stored && token) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem(USER_KEY);
      }
      // Revalida el token contra el backend; si expiró, cierra sesión.
      api.me()
        .then((data) => {
          const fresh = toUser(data);
          setUser(fresh);
          localStorage.setItem(USER_KEY, JSON.stringify(fresh));
        })
        .catch(() => {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const { access_token } = await api.login(email.trim(), password);
      localStorage.setItem(TOKEN_KEY, access_token);
      const data = await api.me();
      const mapped = toUser(data);
      setUser(mapped);
      localStorage.setItem(USER_KEY, JSON.stringify(mapped));
    } catch (err) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      throw authError(err, 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    try {
      await api.register({ email: email.trim(), nombre: name.trim(), password });
      await login(email, password);
    } catch (err) {
      if (err instanceof Error) throw err;
      throw authError(err, 'Error al crear la cuenta');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      login,
      register,
      logout,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
