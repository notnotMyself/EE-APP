"use client";

import { useState } from "react";

interface MessageActionBarProps {
  content: string;
}

// ─── MessageActionBar ─────────────────────────────────────────────────────────
// AI 消息底部的操作栏：复制 / 分享 / 下载。
// 仅在消息流式结束且有内容时由 AIMessage 渲染。

export default function MessageActionBar({ content }: MessageActionBarProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(content);
      } else {
        // 降级：非 HTTPS 环境 / 旧浏览器
        const el = document.createElement("textarea");
        el.value = content;
        el.style.position = "fixed";
        el.style.opacity = "0";
        document.body.appendChild(el);
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // 复制失败时静默处理，不影响用户交互
    }
  };

  return (
    <div className="flex items-center justify-between">
      {/* 左侧：复制 + 分享 */}
      <div className="flex items-center gap-[8px]">
        <div className="relative">
          <button
            type="button"
            className="w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
            style={{ backgroundColor: "rgba(0,0,0,0.04)" }}
            title={copied ? "已复制" : "复制"}
            onClick={handleCopy}
          >
            <img src="/icons/chat/copy.svg" width={13} height={13} alt="复制" />
          </button>
          {/* 复制成功气泡：动画生命周期与 copied state 的 1500ms 精确对齐 */}
          {copied && <div className="copied-toast">已复制</div>}
        </div>
        <button
          type="button"
          className="w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
          style={{ backgroundColor: "rgba(0,0,0,0.04)" }}
          title="分享"
        >
          <img src="/icons/chat/forward_icon.svg" width={16} height={16} alt="分享" />
        </button>
      </div>

      {/* 右侧：下载 */}
      <button
        type="button"
        className="w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
        style={{ backgroundColor: "rgba(0,0,0,0.04)" }}
        title="下载"
      >
        <img src="/icons/chat/regenerate.svg" width={13} height={13} alt="下载" />
      </button>
    </div>
  );
}
