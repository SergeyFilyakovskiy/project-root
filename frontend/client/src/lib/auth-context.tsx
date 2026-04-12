import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authApi, userApi } from "./api";

// UserResponseSchema: { id, email, role, profile: { id, username, first_name, last_name, date_of_birth, created_at }, created_at }
export interface UserProfile {
  id: number;
  username: string;
  first_name: string;
  last_name: string | null;
  date_of_birth: string;
  created_at: string;
}

export interface AuthUser {
  id: number;
  email: string;
  role: string;
  profile: UserProfile;
  created_at: string;
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refetch: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refetch = async () => {
    try {
      const me = await userApi.me();
      setUser(me);
    } catch {
      setUser(null);
    }
  };

  useEffect(() => {
    refetch().finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    // OAuth2PasswordRequestForm: поле называется username, но туда передаём email
    await authApi.login(email, password);
    await refetch();
  };

  const logout = async () => {
    try { await authApi.logout(); } catch { /* игнорируем если токен уже истёк */ }
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
