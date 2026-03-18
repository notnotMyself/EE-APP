"use client";

import Link from "next/link";
import { useChatLayout } from "@/contexts/ChatLayoutContext";

interface TopBarProps {
  showNewChat?: boolean;
}

export default function TopBar({ showNewChat = false }: TopBarProps) {
  const { title, toggleSidebar, isCollapsed } = useChatLayout();

  return (
    <header className="flex items-center justify-between h-[61px] px-[23px] pr-[17px] bg-white w-full shrink-0 relative">
      <div className="flex items-center gap-[18px]">
        <button
          type="button"
          onClick={toggleSidebar}
          className="hover:opacity-70 transition-opacity bg-transparent border-none cursor-pointer p-0"
          title="收缩侧边栏"
        >
          <img src="/icons/sidebar_nav.svg" width={24} height={24} alt="侧边栏" />
        </button>
        {isCollapsed && (
          <Link href="/chat" className="text-black text-[18px] font-medium leading-[26px] no-underline whitespace-nowrap">
            Chris AI
          </Link>
        )}
        {showNewChat && (
          <Link href="/chat" className="hover:opacity-70 transition-opacity p-0">
            <img src="/icons/new_chat.svg" width={24} height={24} alt="新对话" />
          </Link>
        )}
      </div>

      {/* Conversation title - centered */}
      {title && (
        <span className="absolute left-1/2 -translate-x-1/2 text-[14px] font-medium leading-[1.43em] text-black">
          {title}
        </span>
      )}

      <div className="flex gap-0" />
    </header>
  );
}
