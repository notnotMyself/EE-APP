"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { ChatLayoutContext } from "@/contexts/ChatLayoutContext";
import { listConversations, type Conversation } from "@/lib/api";
import Sidebar from "@/components/Sidebar";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, isLoading, accessToken } = useAuth();
  const router = useRouter();
  const [title, setTitle] = useState<string | undefined>(undefined);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const toggleSidebar = useCallback(() => setIsCollapsed((v) => !v), []);

  // 会话列表状态（集中管理，Sidebar 和新建页共用）
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [newConvId, setNewConvId] = useState<string | null>(null);

  // 初始加载会话列表
  useEffect(() => {
    if (!isLoggedIn || !accessToken) {
      setConversations([]);
      return;
    }
    listConversations(accessToken)
      .then((convs) => setConversations(convs))
      .catch(() => setConversations([]));
  }, [isLoggedIn, accessToken]);

  // 乐观更新：新建会话后立即追加到列表头部 + 触发高亮
  const addConversation = useCallback((conv: Conversation) => {
    setConversations((prev) => {
      // 避免重复插入
      if (prev.some((c) => c.id === conv.id)) return prev;
      return [conv, ...prev];
    });
    setNewConvId(conv.id);
    // 2 秒后清除高亮标记
    setTimeout(() => setNewConvId(null), 2000);
  }, []);

  // 乐观删除：从列表中移除指定会话
  const removeConversation = useCallback((convId: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== convId));
  }, []);

  // 更新会话字段（如 title）：本地实时同步，无需重新拉取列表
  const updateConversation = useCallback((convId: string, updates: Partial<Conversation>) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === convId ? { ...c, ...updates } : c))
    );
  }, []);

  useEffect(() => {
    if (!isLoading && !isLoggedIn) router.replace("/login");
  }, [isLoading, isLoggedIn, router]);

  return (
    <ChatLayoutContext.Provider
      value={{ title, setTitle, isCollapsed, toggleSidebar, conversations, addConversation, newConvId, removeConversation, updateConversation }}
    >
      <div className="flex h-screen w-full bg-[#F0F1F2]">
        <Sidebar />
        <div className="relative flex flex-col flex-1 min-w-0">
          {children}
        </div>
      </div>
    </ChatLayoutContext.Provider>
  );
}
