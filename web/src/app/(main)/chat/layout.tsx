"use client";

import TopBar from "@/components/TopBar";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <TopBar showNewChat={true} />
      {children}
    </>
  );
}
