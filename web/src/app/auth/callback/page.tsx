"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase } from "@/lib/supabase";

function AuthCallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");

    if (code) {
      // PKCE flow: exchange code for session
      supabase.auth.exchangeCodeForSession(code).then(({ error }) => {
        if (error) {
          setError("验证失败：" + error.message);
        } else {
          router.replace("/chat");
        }
      });
    } else {
      // Implicit flow: Supabase JS SDK auto-handles the hash fragment
      // onAuthStateChange in AuthContext will fire; wait briefly then redirect
      const timer = setTimeout(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
          if (session) {
            router.replace("/chat");
          } else {
            setError("验证链接无效或已过期，请重新注册或重发验证邮件");
          }
        });
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [router, searchParams]);

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <p className="text-[16px] text-red-500">{error}</p>
        <button
          onClick={() => router.replace("/login")}
          className="rounded-[40px] bg-black px-6 py-3 text-[14px] font-semibold text-white"
        >
          返回登录
        </button>
      </div>
    );
  }

  return <p className="text-[16px] text-black/60">正在验证邮箱，请稍候…</p>;
}

export default function AuthCallbackPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-[#F0F1F2]">
      <Suspense fallback={<p className="text-[16px] text-black/60">加载中…</p>}>
        <AuthCallbackInner />
      </Suspense>
    </div>
  );
}
