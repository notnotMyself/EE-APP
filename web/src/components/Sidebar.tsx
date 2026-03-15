"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";

const navItems = [
  { id: "review", label: "AI 评审", icon: "review", active: true },
  { id: "inspiration", label: "灵感资讯", icon: "tips" },
  { id: "library", label: "资料库", icon: "bookshelf" },
];

interface SidebarProps {
  isLoggedIn?: boolean;
}

function AIReviewIcon({ active }: { active: boolean }) {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="20" height="16" rx="3" stroke={active ? "#0066FF" : "rgba(0,0,0,0.9)"} strokeWidth="1.5" />
      <path d="M7 10.5h4M7 13.5h7" stroke={active ? "#0066FF" : "rgba(0,0,0,0.9)"} strokeWidth="1.3" strokeLinecap="round" />
      <circle cx="17.5" cy="8.5" r="3.5" fill={active ? "#0066FF" : "rgba(0,0,0,0.6)"} />
      <text x="17.5" y="10.2" textAnchor="middle" fontSize="5" fill="white" fontWeight="700">AI</text>
    </svg>
  );
}

export default function Sidebar({ isLoggedIn = false }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="w-[238px] h-full bg-[#F8F8F8] flex flex-col relative shrink-0">
      {/* Logo */}
      <div className="px-6 pt-[22px] pb-[28px]">
        <span className="text-black text-[18px] font-medium leading-[26px]">
          Chris AI
        </span>
      </div>

      {/* Nav Items */}
      <div className="flex flex-col mx-[6px] gap-[2px]">
        {navItems.map((item) => {
          const isActive = item.active;
          return (
            <Link
              key={item.id}
              href={item.id === "review" ? "/chat" : "#"}
              className={`flex items-center gap-[10px] px-[18px] h-[44px] no-underline rounded-[14px] transition-colors ${
                isActive
                  ? "bg-white"
                  : "hover:bg-[rgba(0,0,0,0.04)]"
              }`}
            >
              <span className="w-6 h-6 flex items-center justify-center shrink-0">
                {item.icon === "review" ? (
                  <AIReviewIcon active={isActive} />
                ) : (
                  <img src={`/icons/${item.icon}.svg`} width={24} height={24} alt={item.label} />
                )}
              </span>
              <span
                className={`text-[13px] font-medium leading-[16px] ${
                  isActive ? "text-[#0066FF]" : "text-[rgba(0,0,0,0.9)]"
                }`}
              >
                {item.label}
              </span>
            </Link>
          );
        })}

        {/* Divider */}
        <div className="mx-[18px] h-px bg-black/10 my-[6px]" />

        {/* History - dimmed */}
        <div className="flex items-center gap-[10px] px-[18px] h-[44px] opacity-40">
          <span className="text-[13px] font-medium text-[rgba(0,0,0,0.9)]">
            历史对话
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-auto mx-[6px] pb-4">
        <Link
          href={isLoggedIn ? "/profile" : "/login"}
          className="flex items-center gap-[10px] px-[18px] h-[44px] no-underline rounded-[14px] hover:bg-[rgba(0,0,0,0.04)] transition-colors"
        >
          <img src="/icons/account.svg" width={24} height={24} alt="账户" />
          <span className="text-[13px] font-medium leading-[14px] text-[rgba(0,0,0,0.9)]">
            {isLoggedIn ? "我的" : "登录"}
          </span>
        </Link>
      </div>
    </aside>
  );
}
