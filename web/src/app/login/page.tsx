"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/contexts/AuthContext";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import LoginModal from "@/components/LoginModal";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";

function ArrowRightIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M4.167 10h11.666M10.833 5l5 5-5 5"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function LoginPage() {
  const { isLoggedIn, isLoading } = useAuth();
  const router = useRouter();
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Redirect to chat if already logged in
  if (!isLoading && isLoggedIn) {
    router.replace("/chat");
    return null;
  }

  const handleLogin = () => {
    setShowLoginModal(true);
  };

  return (
    <div className="flex h-screen w-full bg-[#F0F1F2]">
      {/* Left Sidebar */}
      <Sidebar />

      {/* Right Content */}
      <div className="relative flex flex-col flex-1 min-w-0">
        {/* Top Bar */}
        <TopBar />

        {/* Login Modal */}
        {showLoginModal && (
          <LoginModal onClose={() => setShowLoginModal(false)} />
        )}

        {/* Main Content - centered profile and login */}
        <div className="flex-1 flex flex-col items-center justify-center -mt-[40px]">
          {/* Profile Section */}
          <div className="flex flex-col items-center gap-[14px]">
            {/* Avatar */}
            <div className="w-[130px] h-[130px] rounded-full overflow-hidden shadow-[0px_6px_32px_rgba(0,0,0,0.1)]">
              <Image
                src={chrisChenAvatar}
                alt="Chris Chen"
                width={130}
                height={130}
                className="w-full h-full object-cover"
                priority
              />
            </div>

            {/* Name */}
            <h1 className="font-[var(--font-heading)] text-[26px] font-bold leading-normal text-[#0D1B34] m-0">
              Chris Chen
            </h1>

            {/* Description */}
            <p className="text-[14px] font-normal leading-normal text-black/[0.54] m-0 text-center">
              身经百战，眼光如炬的设计老法师
            </p>
          </div>

          {/* Login Button */}
          <button
            onClick={handleLogin}
            className="mt-[40px] w-[329.3px] h-[55.99px] rounded-[40px] bg-black shadow-[0px_6px_54px_rgba(0,0,0,0.14)] flex items-center justify-center gap-[32px] border-none cursor-pointer transition-opacity hover:opacity-90 active:opacity-80"
          >
            <span className="font-[var(--font-inter)] text-[16px] font-semibold text-white tracking-[-0.0195em]">
              登录开始使用
            </span>
            <ArrowRightIcon />
          </button>
        </div>
      </div>
    </div>
  );
}
