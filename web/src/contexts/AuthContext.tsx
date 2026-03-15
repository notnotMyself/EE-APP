"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import type { Session } from "@supabase/supabase-js";

interface User {
  id: string;
  name: string;
  avatar: string;
  description: string;
}

interface AuthContextType {
  user: User | null;
  session: Session | null;
  accessToken: string | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  login: (account: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

function sessionToUser(session: Session): User {
  const meta = session.user.user_metadata ?? {};
  return {
    id: session.user.id,
    name: meta.display_name ?? meta.full_name ?? session.user.email ?? "User",
    avatar: meta.avatar_url ?? "/assets/images/chris_chen_avatar.jpeg",
    description: meta.description ?? "",
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Restore session on mount & listen for auth changes
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session: s } }) => {
      if (s) {
        setSession(s);
        setUser(sessionToUser(s));
      }
      setIsLoading(false);
    });

    // Listen for auth state changes (token refresh, sign-out, etc.)
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s);
      setUser(s ? sessionToUser(s) : null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const login = useCallback(
    async (account: string, password: string) => {
      if (!account.trim()) throw new Error("请输入账号");
      if (!password.trim()) throw new Error("请输入密码");

      const { data, error } = await supabase.auth.signInWithPassword({
        email: account.trim(),
        password: password.trim(),
      });

      if (error) throw new Error(error.message);
      if (!data.session) throw new Error("登录失败，请重试");

      setSession(data.session);
      setUser(sessionToUser(data.session));
      router.push("/chat");
    },
    [router]
  );

  const logout = useCallback(async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        accessToken: session?.access_token ?? null,
        isLoggedIn: !!session,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
