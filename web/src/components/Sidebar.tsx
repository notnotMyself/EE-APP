"use client";

import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";
import { listConversations, deleteConversation, type Conversation } from "@/lib/api";

const navItems = [
  { id: "review", label: "AI 评审", icon: "review", href: "/chat" },
  { id: "inspiration", label: "灵感资讯", icon: "tips", href: "/inspiration" },
  { id: "library", label: "资料库", icon: "bookshelf", href: "/library" },
];

function ChatBubbleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M2 3a1 1 0 011-1h10a1 1 0 011 1v7a1 1 0 01-1 1H5l-3 3V3z"
        stroke="rgba(0,0,0,0.4)"
        strokeWidth="1.2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { logout, accessToken, isLoggedIn } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);

  // Fetch real conversation history
  useEffect(() => {
    if (!isLoggedIn || !accessToken) {
      setConversations([]);
      return;
    }

    listConversations(accessToken)
      .then((convs) => setConversations(convs))
      .catch(() => setConversations([]));
  }, [isLoggedIn, accessToken]);

  const handleDelete = async (convId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!accessToken) return;

    const prev = [...conversations];
    setConversations((c) => c.filter((x) => x.id !== convId));

    try {
      await deleteConversation(accessToken, convId);
      if (pathname === `/chat/${convId}`) {
        router.push("/chat");
      }
    } catch {
      setConversations(prev);
    }
  };

  return (
    <aside className="w-[238px] h-full bg-[#F8F8F8] flex flex-col relative shrink-0">
      {/* Logo */}
      <div className="px-6 pt-[22px] pb-[28px]">
        <Link href="/chat" className="no-underline">
          <span className="text-black text-[18px] font-medium leading-[26px]">
            Chris AI
          </span>
        </Link>
      </div>

      {/* Nav Items */}
      <div className="flex flex-col mx-[6px] gap-[2px] shrink-0">
        {navItems.map((item) => {
          const isActive =
            item.id === "review"
              ? pathname === "/chat" || pathname.startsWith("/chat/")
              : pathname === item.href;
          const iconSrc = isActive
            ? `/icons/${item.icon}_on.svg`
            : `/icons/${item.icon}_off.svg`;
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`flex items-center gap-[10px] px-[18px] h-[44px] no-underline rounded-[14px] transition-colors ${
                isActive
                  ? "bg-white"
                  : "hover:bg-[rgba(0,0,0,0.04)]"
              }`}
            >
              {item.id === "review" && isLoggedIn ? (
                <img
                  src={chrisChenAvatar.src}
                  width={24}
                  height={24}
                  alt="头像"
                  className="w-6 h-6 rounded-full object-cover shrink-0"
                />
              ) : (
                <span className="w-6 h-6 flex items-center justify-center shrink-0">
                  <img src={iconSrc} width={24} height={24} alt={item.label} />
                </span>
              )}
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
      </div>

      {/* Divider */}
      <div className="mx-[24px] h-px bg-black/10 my-[6px] shrink-0" />

      {/* History section - scrollable */}
      <div className="flex flex-col mx-[6px] flex-1 min-h-0">
        <div className="flex items-center gap-[10px] px-[18px] h-[32px] shrink-0">
          <span className="text-[12px] font-medium text-[rgba(0,0,0,0.4)] uppercase tracking-wider">
            历史对话
          </span>
        </div>

        <div className="flex-1 overflow-y-auto min-h-0">
          {isLoggedIn && conversations.length > 0 && (
            <div className="flex flex-col gap-[1px]">
              {conversations.map((conv) => {
                const isConvActive = pathname === `/chat/${conv.id}`;
                return (
                  <Link
                    key={conv.id}
                    href={`/chat/${conv.id}`}
                    className={`group flex items-center gap-[8px] px-[18px] h-[38px] no-underline rounded-[14px] transition-colors shrink-0 ${
                      isConvActive
                        ? "bg-white"
                        : "hover:bg-[rgba(0,0,0,0.04)]"
                    }`}
                  >
                    <ChatBubbleIcon />
                    <span className={`text-[13px] leading-[16px] truncate flex-1 ${
                      isConvActive
                        ? "font-medium text-[rgba(0,0,0,0.9)]"
                        : "font-normal text-[rgba(0,0,0,0.6)]"
                    }`}>
                      {conv.title ?? conv.agent_name ?? "对话"}
                    </span>
                    <button
                      type="button"
                      onMouseDown={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDelete(conv.id, e);
                      }}
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                      className="opacity-0 group-hover:opacity-100 w-5 h-5 flex items-center justify-center rounded bg-transparent border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-all shrink-0 z-10"
                      title="删除对话"
                    >
                      <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.5 1.5L8.5 8.5M8.5 1.5L1.5 8.5" stroke="rgba(0,0,0,0.4)" strokeWidth="1.2" strokeLinecap="round" />
                      </svg>
                    </button>
                  </Link>
                );
              })}
            </div>
          )}

          {isLoggedIn && conversations.length === 0 && (
            <div className="px-[18px] py-[8px]">
              <span className="text-[12px] text-[rgba(0,0,0,0.3)]">
                暂无历史对话
              </span>
            </div>
          )}

          {!isLoggedIn && (
            <div className="px-[18px] py-[8px]">
              <span className="text-[12px] text-[rgba(0,0,0,0.3)]">
                登录后查看历史对话
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-auto mx-[6px] pb-4 flex flex-col gap-[2px]">
        {isLoggedIn && (
          <button
            type="button"
            onClick={logout}
            className="flex items-center gap-[10px] px-[18px] h-[44px] rounded-[14px] hover:bg-[rgba(0,0,0,0.04)] transition-colors border-none bg-transparent cursor-pointer w-full text-left"
          >
            <span className="text-[13px] font-medium leading-[14px] text-[rgba(0,0,0,0.54)]">
              退出登录
            </span>
          </button>
        )}
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
