"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useTransition,
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
  register: (email: string, username: string, password: string) => Promise<void>;
  resendConfirmation: (email: string) => Promise<void>;
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
  const [, startTransition] = useTransition();
  const router = useRouter();

  // Restore session on mount & listen for auth changes
  useEffect(() => {
    // Get initial session — clear stale tokens on refresh failure
    supabase.auth.getSession().then(({ data: { session: s }, error }) => {
      if (error) {
        console.warn("Session restore failed, clearing stale tokens:", error.message);
        supabase.auth.signOut();
      } else if (s) {
        setSession(s);
        setUser(sessionToUser(s));
      }
      setIsLoading(false);
    });

    // Listen for auth state changes (token refresh, sign-out, etc.)
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, s) => {
      // Use startTransition to avoid "Cannot update component while rendering" warning
      startTransition(() => {
        setSession(s);
        setUser(s ? sessionToUser(s) : null);
      });
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

      // State is updated by onAuthStateChange listener; just navigate.
      // Defer navigation to next microtask to avoid React render conflict.
      setTimeout(() => router.push("/chat"), 0);
    },
    [router]
  );

  const register = useCallback(
    async (email: string, username: string, password: string) => {
      const { error } = await supabase.auth.signUp({
        email: email.trim(),
        password: password.trim(),
        options: {
          data: { username: username.trim() }, // 存入 raw_user_meta_data，与 Flutter 端一致
        },
      });
      if (error) throw new Error(error.message);
      // 不自动导航，由调用方（LoginModal）处理成功后的 UI 流转
    },
    []
  );

  const resendConfirmation = useCallback(async (email: string) => {
    const { error } = await supabase.auth.resend({
      type: "signup",
      email: email.trim(),
    });
    if (error) throw new Error(error.message);
  }, []);

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
        register,
        resendConfirmation,
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
