"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Sidebar from "@/components/Sidebar";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isLoggedIn) router.replace("/login");
  }, [isLoading, isLoggedIn, router]);

  return (
    <div className="flex h-screen w-full bg-[#F0F1F2]">
      <Sidebar />
      <div className="relative flex flex-col flex-1 min-w-0">
        {children}
      </div>
    </div>
  );
}
