"use client";
import { createContext, useContext } from "react";

interface ChatLayoutContextType {
  setTitle: (title: string | undefined) => void;
}

export const ChatLayoutContext = createContext<ChatLayoutContextType | null>(null);

export function useChatLayout() {
  const ctx = useContext(ChatLayoutContext);
  if (!ctx) throw new Error("useChatLayout must be used within ChatLayout");
  return ctx;
}
