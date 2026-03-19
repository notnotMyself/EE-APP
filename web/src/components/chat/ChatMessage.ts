// ─── ChatMessage interface ───────────────────────────────────────────────────
// 单条聊天消息的数据结构，供 page.tsx 及各消息组件共享

import type { Attachment } from "@/lib/upload";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  attachments?: Attachment[];
  isStreaming?: boolean;
}
