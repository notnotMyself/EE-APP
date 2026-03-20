"use client";

import { Streamdown } from "streamdown";
import { code } from "@streamdown/code";
import { cjk } from "@streamdown/cjk";
import MessageActionBar from "./MessageActionBar";
import type { ChatMessage } from "./ChatMessage";

interface AIMessageProps {
  message: ChatMessage;
}

// ─── AIMessage ────────────────────────────────────────────────────────────────
// AI 回复气泡，使用 streamdown 渲染 Markdown：
//   - animated：启用字符逐步出现动画，完全替代原 typeTimer 方案
//   - isAnimating：绑定 isStreaming，流式结束后动画自动收尾
//   - plugins.code：shiki 代码块高亮（github-light 主题）
//   - plugins.cjk：中文标点排版优化
//
// 样式系统：使用 .ai-prose 自定义类（定义在 globals.css）替代 prose prose-sm，
// 精确控制字号、行高、间距、代码块、表格与气泡背景 #F7F8FD 的协调关系。

export default function AIMessage({ message }: AIMessageProps) {
  return (
    <div className="flex justify-start">
      <div className="flex flex-col gap-[5px] w-full">
        {/* 等待 AI 首个 token 期间显示 thinking 动画，内容到达后无缝切换 */}
        {message.isStreaming && !message.content ? (
          <div className="thinking-dots">
            <span />
            <span />
            <span />
          </div>
        ) : (
          <div className="ai-prose">
            <Streamdown
              animated
              isAnimating={message.isStreaming}
              plugins={{ code, cjk }}
              shikiTheme={["github-light", "github-dark"]}
              controls={false}
            >
              {message.content}
            </Streamdown>
          </div>
        )}

        {/* 底部操作栏：流式结束且有内容时显示 */}
        {!message.isStreaming && message.content && (
          <MessageActionBar content={message.content} />
        )}
      </div>
    </div>
  );
}
