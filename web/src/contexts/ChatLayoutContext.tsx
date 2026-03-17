"use client";
import { createContext, useContext } from "react";
import type { Conversation } from "@/lib/api";

interface ChatLayoutContextType {
  title: string | undefined;
  setTitle: (title: string | undefined) => void;
  isCollapsed: boolean;
  toggleSidebar: () => void;
  /** 会话列表（从后端拉取 + 乐观更新） */
  conversations: Conversation[];
  /** 新建会话后立即追加到列表头部（乐观更新） */
  addConversation: (conv: Conversation) => void;
  /** 刚新建的会话 id，用于触发高亮动画 */
  newConvId: string | null;
  /** 更新会话的部分字段（如 title），用于本地实时同步侧边栏 */
  updateConversation: (convId: string, updates: Partial<Conversation>) => void;
  /** 删除会话（乐观更新） */
  removeConversation: (convId: string) => void;
}

export const ChatLayoutContext = createContext<ChatLayoutContextType | null>(null);

export function useChatLayout() {
  const ctx = useContext(ChatLayoutContext);
  if (!ctx) throw new Error("useChatLayout must be used within ChatLayout");
  return ctx;
}
