"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";

export default function InspirationPage() {
  const router = useRouter();
  const { isLoggedIn, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isLoggedIn) {
      router.replace("/login");
    }
  }, [isLoading, isLoggedIn, router]);

  return (
    <div className="flex h-screen w-full bg-[#F0F1F2]">
      <Sidebar isLoggedIn={isLoggedIn} />
      <div className="relative flex flex-col flex-1 min-w-0">
        <TopBar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-[20px] font-medium text-[rgba(0,0,0,0.9)] m-0">灵感资讯</p>
            <p className="text-[14px] text-[rgba(0,0,0,0.4)] mt-2">功能开发中，敬请期待</p>
          </div>
        </div>
      </div>
    </div>
  );
}
