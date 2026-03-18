"use client";

import TopBar from "@/components/TopBar";

export default function LibraryPage() {
  return (
    <>
      <TopBar />
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <p className="text-[20px] font-medium text-[rgba(0,0,0,0.9)] m-0">资料库</p>
          <p className="text-[14px] text-[rgba(0,0,0,0.4)] mt-2">功能开发中，敬请期待</p>
        </div>
      </div>
    </>
  );
}
