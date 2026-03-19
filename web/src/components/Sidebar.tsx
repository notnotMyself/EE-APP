"use client";

import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useChatLayout } from "@/contexts/ChatLayoutContext";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";
import { deleteConversation } from "@/lib/api";

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
  const { logout, accessToken, isLoggedIn, user } = useAuth();
  const { isCollapsed, conversations, newConvId, removeConversation } = useChatLayout();

  // 滚动到刚新建的会话条目
  const newConvRef = useRef<HTMLAnchorElement>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (newConvId && newConvRef.current) {
      newConvRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [newConvId]);

  // Close user menu when clicking outside
  useEffect(() => {
    if (!showUserMenu) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showUserMenu]);

  const handleDelete = async (convId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!accessToken) return;

    // 乐观删除
    removeConversation(convId);

    try {
      await deleteConversation(accessToken, convId);
      if (pathname === `/chat/${convId}`) router.push("/chat");
    } catch {
      // 删除失败：重新加载会话列表（暂简单处理，刷新页面可恢复）
    }
  };

  return (
    <aside
      className={`
        h-full bg-[#F8F8F8] flex flex-col relative shrink-0
        transition-[width] duration-300 ease-in-out
        ${isCollapsed ? "w-[72px]" : "w-[238px]"}
      `}
    >
      {/* Header — 收缩时隐藏文字 */}
      <div className="px-6 pt-[22px] pb-[28px] shrink-0">
        <Link href="/chat" className="no-underline">
          <span
            className={`text-black text-[18px] font-medium leading-[26px] whitespace-nowrap transition-[opacity] duration-200 ${
              isCollapsed ? "opacity-0" : "opacity-100"
            }`}
          >
            Chris AI
          </span>
        </Link>
      </div>

      {/* Nav Items */}
      <div className={`flex flex-col shrink-0 ${isCollapsed ? "mx-[6px] gap-[4px]" : "mx-[6px] gap-[2px]"}`}>
        {navItems.map((item) => {
          const isActive =
            item.id === "review"
              ? pathname === "/chat" || pathname.startsWith("/chat/")
              : pathname === item.href;
          // review 项只切换图标，不显示高亮背景和蓝色文字
          const showActive = item.id === "review" ? false : isActive;
          const iconSrc = isActive
            ? `/icons/${item.icon}_on.svg`
            : `/icons/${item.icon}_off.svg`;

          // 收缩态：图标 + 文字纵向居中
          if (isCollapsed) {
            return (
              <Link
                key={item.id}
                href={item.href}
                className={`flex flex-col items-center justify-center gap-[4px] h-[64px] rounded-[14px] transition-colors no-underline ${
                  showActive ? "bg-white" : "hover:bg-[rgba(0,0,0,0.04)]"
                }`}
              >
                {item.id === "review" ? (
                  <img
                    src={chrisChenAvatar.src}
                    width={24}
                    height={24}
                    alt="头像"
                    className="w-6 h-6 rounded-full object-cover shrink-0"
                  />
                ) : (
                  <img src={iconSrc} width={24} height={24} alt={item.label} />
                )}
                <span
                  className={`text-[10px] font-medium leading-[12px] text-center ${
                    showActive ? "text-[#0066FF]" : "text-[rgba(0,0,0,0.6)]"
                  }`}
                >
                  {item.label}
                </span>
              </Link>
            );
          }

          // 展开态：图标 + 文字横向
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`flex items-center gap-[10px] px-[18px] h-[44px] no-underline rounded-[14px] transition-colors ${
                showActive ? "bg-white" : "hover:bg-[rgba(0,0,0,0.04)]"
              }`}
            >
              {item.id === "review" ? (
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
                className={`text-[13px] font-medium leading-[16px] whitespace-nowrap ${
                  showActive ? "text-[#0066FF]" : "text-[rgba(0,0,0,0.9)]"
                }`}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>

      {/* Divider + 历史对话 — 收缩时隐藏 */}
      {!isCollapsed && (
        <>
          <div className="mx-[24px] h-px bg-black/10 my-[6px] shrink-0" />

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
                    const isNew = conv.id === newConvId;
                    return (
                      <Link
                        key={conv.id}
                        ref={isNew ? newConvRef : null}
                        href={`/chat/${conv.id}`}
                        className={`group flex items-center gap-[8px] px-[18px] h-[38px] no-underline rounded-[14px] shrink-0 ${
                          isConvActive
                            ? "bg-[rgba(0,102,255,0.1)] transition-colors"
                            : isNew
                            ? "sidebar-conv-new"
                            : "hover:bg-[rgba(0,0,0,0.04)] transition-colors"
                        }`}
                      >
                        <ChatBubbleIcon />
                        <span
                          className={`text-[13px] leading-[16px] truncate flex-1 ${
                            isConvActive
                              ? "font-medium text-[#0066FF]"
                              : isNew
                              ? "sidebar-conv-new-text"
                              : "font-normal text-[rgba(0,0,0,0.6)]"
                          }`}
                        >
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
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2 2L10 10M10 2L2 10" stroke="rgba(0,0,0,0.4)" strokeWidth="1.5" strokeLinecap="round" />
                          </svg>
                        </button>
                      </Link>
                    );
                  })}
                </div>
              )}

              {isLoggedIn && conversations.length === 0 && (
                <div className="px-[18px] py-[8px]">
                  <span className="text-[12px] text-[rgba(0,0,0,0.3)]">暂无历史对话</span>
                </div>
              )}

              {!isLoggedIn && (
                <div className="px-[18px] py-[8px]">
                  <span className="text-[12px] text-[rgba(0,0,0,0.3)]">登录后查看历史对话</span>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* 收缩时占位，将 footer 推到底部 */}
      {isCollapsed && <div className="flex-1" />}

      {/* Footer */}
      <div className={`mt-auto pb-4 shrink-0 ${isCollapsed ? "mx-[6px]" : "mx-[6px]"}`}>
        {/* 账户按钮 — 登录后点击弹出菜单 */}
        <div className="relative" ref={userMenuRef}>
          {/* 用户菜单弹窗 */}
          {isLoggedIn && (
            <div
              className={`absolute bottom-[calc(100%+8px)] left-0 w-[196px] rounded-[24px] pt-[10px] pb-[8px] z-50 origin-bottom-left transition-all duration-150 ease-out ${
                showUserMenu
                  ? "opacity-100 scale-100 translate-y-0 pointer-events-auto"
                  : "opacity-0 scale-95 translate-y-1 pointer-events-none"
              }`}
              style={{
                background: "rgba(239,239,239,0.85)",
                backdropFilter: "blur(20px)",
                WebkitBackdropFilter: "blur(20px)",
                boxShadow: "0px 8px 32px rgba(0,0,0,0.12), 0px 2px 8px rgba(0,0,0,0.06)",
              }}
            >
              {/* 用户信息区 */}
              <div className="px-[16px] py-[10px]">
                <span className="text-[13px] font-semibold leading-[16px] text-[rgba(0,0,0,0.88)] truncate block">
                  {user?.name ?? "用户"}
                </span>
                {user?.description ? (
                  <span className="text-[11px] font-normal leading-[14px] text-[rgba(0,0,0,0.38)] truncate block mt-[2px]">
                    {user.description}
                  </span>
                ) : null}
              </div>

              {/* 分割线 */}
              <div className="mx-[12px] my-[4px] h-px" style={{ background: "rgba(0,0,0,0.08)" }} />

              {/* 退出登录 */}
              <div className="mx-[6px] mt-[2px]">
                <button
                  type="button"
                  onClick={() => { logout(); setShowUserMenu(false); }}
                  className="w-full flex items-center gap-[8px] px-[12px] py-[10px] rounded-[14px] text-[13px] font-medium text-[#E53E3E] border-none bg-transparent cursor-pointer transition-colors hover:bg-[rgba(229,62,62,0.06)] active:bg-[rgba(229,62,62,0.10)]"
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" className="shrink-0">
                    <path d="M5 2H3a1 1 0 00-1 1v8a1 1 0 001 1h2" stroke="#E53E3E" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M9 10l3-3-3-3" stroke="#E53E3E" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M12 7H5.5" stroke="#E53E3E" strokeWidth="1.3" strokeLinecap="round" />
                  </svg>
                  退出登录
                </button>
              </div>
            </div>
          )}

          {isCollapsed ? (
            isLoggedIn ? (
              <button
                type="button"
                onClick={() => setShowUserMenu((v) => !v)}
                className="flex flex-col items-center justify-center gap-[4px] h-[64px] w-full rounded-[14px] hover:bg-[rgba(0,0,0,0.04)] transition-colors border-none bg-transparent cursor-pointer"
              >
                <img src="/icons/account.svg" width={24} height={24} alt="账户" />
                <span className="text-[10px] font-medium leading-[12px] text-[rgba(0,0,0,0.6)]">我的</span>
              </button>
            ) : (
              <Link
                href="/login"
                className="flex flex-col items-center justify-center gap-[4px] h-[64px] rounded-[14px] no-underline hover:bg-[rgba(0,0,0,0.04)] transition-colors"
              >
                <img src="/icons/account.svg" width={24} height={24} alt="账户" />
                <span className="text-[10px] font-medium leading-[12px] text-[rgba(0,0,0,0.6)]">登录</span>
              </Link>
            )
          ) : (
            isLoggedIn ? (
              <button
                type="button"
                onClick={() => setShowUserMenu((v) => !v)}
                className="flex items-center gap-[10px] px-[18px] h-[44px] rounded-[14px] hover:bg-[rgba(0,0,0,0.04)] transition-colors border-none bg-transparent cursor-pointer w-full text-left"
              >
                <img src="/icons/account.svg" width={24} height={24} alt="账户" />
                <span className="text-[13px] font-medium leading-[14px] text-[rgba(0,0,0,0.9)]">我的</span>
              </button>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-[10px] px-[18px] h-[44px] no-underline rounded-[14px] hover:bg-[rgba(0,0,0,0.04)] transition-colors"
              >
                <img src="/icons/account.svg" width={24} height={24} alt="账户" />
                <span className="text-[13px] font-medium leading-[14px] text-[rgba(0,0,0,0.9)]">登录</span>
              </Link>
            )
          )}
        </div>
      </div>
    </aside>
  );
}
