"use client";

import { useState } from "react";
import { ChatLayoutContext } from "@/contexts/ChatLayoutContext";
import TopBar from "@/components/TopBar";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  const [title, setTitle] = useState<string | undefined>(undefined);

  return (
    <ChatLayoutContext.Provider value={{ setTitle }}>
      <TopBar showNewChat={true} title={title} />
      {children}
    </ChatLayoutContext.Provider>
  );
}
