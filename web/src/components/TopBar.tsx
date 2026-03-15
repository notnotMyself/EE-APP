"use client";

import Link from "next/link";

function SidebarNavIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="3" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8"/>
      <line x1="10" y1="3" x2="10" y2="21" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8"/>
      <line x1="5.5" y1="8" x2="8" y2="8" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8" strokeLinecap="round"/>
      <line x1="5.5" y1="12" x2="8" y2="12" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8" strokeLinecap="round"/>
      <line x1="5.5" y1="16" x2="8" y2="16" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8" strokeLinecap="round"/>
    </svg>
  );
}

function NewChatIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="3" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
      <line x1="12" y1="8" x2="12" y2="16" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8" strokeLinecap="round"/>
      <line x1="8" y1="12" x2="16" y2="12" stroke="rgba(0,0,0,0.5)" strokeWidth="1.8" strokeLinecap="round"/>
    </svg>
  );
}

interface TopBarProps {
  showNewChat?: boolean;
  title?: string;
}

export default function TopBar({ showNewChat = false, title }: TopBarProps) {
  return (
    <header className="flex items-center justify-between h-[61px] px-[23px] pr-[17px] bg-white w-full shrink-0">
      <div className="flex items-center gap-[18px]">
        <button className="hover:opacity-80 transition-opacity bg-transparent border-none cursor-pointer p-0">
          <SidebarNavIcon />
        </button>
        {showNewChat && (
          <Link href="/chat" className="hover:opacity-80 transition-opacity p-0">
            <NewChatIcon />
          </Link>
        )}
      </div>

      {/* Conversation title - centered */}
      {title && (
        <span className="absolute left-1/2 -translate-x-1/2 text-[14px] font-medium leading-[1.43em] text-black">
          {title}
        </span>
      )}

      {/* Spacer for layout balance */}
      <div className="flex gap-0" />
    </header>
  );
}
