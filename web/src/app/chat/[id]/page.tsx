"use client";

import { useState, useRef, useEffect, use, useCallback } from "react";
import Image from "next/image";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import AttachmentMenu from "@/components/AttachmentMenu";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";

// ─── Inline SVG Icons ───────────────────────────────────────────────────────

function AtIcon() {
  return (
    <span className="text-[16px] font-medium leading-[1.17em] text-[rgba(0,0,0,0.9)] select-none">
      @
    </span>
  );
}

function AttachmentIcon() {
  return (
    <svg
      width="17"
      height="15"
      viewBox="0 0 17 15"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M15.5 7.14L8.86 13.78a4.5 4.5 0 0 1-6.36-6.36l6.64-6.64a3 3 0 0 1 4.24 4.24l-6.63 6.63a1.5 1.5 0 0 1-2.12-2.12L11.27 3"
        stroke="rgba(0,0,0,0.9)"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 14 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M7 12V2M7 2L2 7M7 2L12 7"
        stroke="white"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function MicIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 14 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect x="5" y="1" width="4" height="7" rx="2" stroke="white" strokeWidth="1.4" />
      <path d="M3 6.5a4 4 0 008 0" stroke="white" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M7 11.5v1.5" stroke="white" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 15 15"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect
        x="1.5"
        y="1.5"
        width="8.5"
        height="8.5"
        rx="1"
        stroke="rgba(0,0,0,0.9)"
        strokeWidth="1.26"
      />
      <rect
        x="5"
        y="5"
        width="8.5"
        height="8.5"
        rx="1"
        stroke="rgba(0,0,0,0.9)"
        strokeWidth="1.26"
      />
    </svg>
  );
}

function RegenerateIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 15 15"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M1.5 7.5a6 6 0 0 1 11-3.2M13.5 7.5a6 6 0 0 1-11 3.2"
        stroke="rgba(0,0,0,0.9)"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12.5 1v3.5H9M2.5 14v-3.5H6"
        stroke="rgba(0,0,0,0.9)"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 15 15"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M7.5 1.5v8M4.5 7.5l3 3 3-3M2.5 12.5h10"
        stroke="rgba(0,0,0,0.9)"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── Mock Data ──────────────────────────────────────────────────────────────

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  hasImages?: boolean;
}

const initialMockMessages: ChatMessage[] = [
  {
    id: "1",
    role: "user",
    content: "\u70B9\u6309\u624B\u5199\u7B14\u673A\u8EAB\u7684\u6309\u952E\uFF0C\u51FA\u73B0\u7684\u8F6E\u76D8\u65B9\u6848\u9009\u62E9\u5BF9\u6BD4",
    hasImages: true,
  },
  {
    id: "2",
    role: "assistant",
    content:
      "\u4F60\u5E0C\u671B\u8FD9\u4E2A\u8F6E\u76D8\u89E3\u51B3\u7684\u6838\u5FC3\u95EE\u9898\u662F\u4EC0\u4E48\uFF1F\n\u51CF\u5C11\u64CD\u4F5C\u8DEF\u5F84\uFF1F\n\u964D\u4F4E\u624B\u5199\u8FC7\u7A0B\u4E2D\u7684\u4E2D\u65AD\u611F\uFF1F\n\u8FD8\u662F\u4E3A\u4E86\u5BB9\u7EB3\u66F4\u591A\u80FD\u529B\u800C\u4E0D\u5360\u753B\u5E03\u7A7A\u95F4\uFF1F",
  },
  {
    id: "3",
    role: "user",
    content: "\u5BB9\u7EB3\u66F4\u591A\u80FD\u529B\u800C\u4E0D\u5360\u753B\u5E03\u7A7A\u95F4\uFF0C\u7528\u6237\u53EF\u4EE5\u5FEB\u901F\u8BC6\u522B\u5DE5\u5177",
  },
  {
    id: "4",
    role: "assistant",
    content:
      "\u6211\u4F1A\u9009\u4E0B\u9762\u8FD9\u4E2A\u65B9\u6848\uFF08\u7B2C\u4E8C\u5F20\uFF1A\u56FE\u6807\u5728\u8F6E\u76D8\u5185\uFF0C\u6587\u6848\u5916\u6D6E\u63D0\u793A\uFF09\uFF0C\u4F46\u524D\u63D0\u662F\u4F60\u628A\u5B83\u5F53\u6210\u300C\u5B66\u4E60\u671F / \u4F4E\u9891\u529F\u80FD\u786E\u8BA4\u6001\u300D\u65B9\u6848\uFF1B\n\u5982\u679C\u76EE\u6807\u662F\u300C\u5DF2\u7ECF\u719F\u7EC3\u4F7F\u7528\u7684\u9AD8\u9891\u5DE5\u5177\u300D\uFF0C\u7B2C\u4E00\u5F20\u66F4\u4F18\u3002",
  },
];

const mockConversationTitle = "\u624B\u5199\u7B14\u8F6E\u76D8\u8BBE\u8BA1\u5BF9\u6BD4";

// ─── User Message Bubble ────────────────────────────────────────────────────

function UserMessage({ message }: { message: ChatMessage }) {
  return (
    <div className="flex flex-col items-end gap-[10px]">
      <div className="flex flex-col items-center gap-[10px] max-w-[480px]">
        <div className="bg-[#2C69FF] rounded-[12px] px-[16px] py-[12px]">
          {message.hasImages && (
            <div className="flex items-center gap-[3px] mb-[10px]">
              <div className="w-[43px] h-[43px] rounded-[8px] bg-white/20 overflow-hidden">
                <Image
                  src={chrisChenAvatar}
                  alt="Design attachment 1"
                  width={43}
                  height={43}
                  className="w-full h-full object-cover opacity-70"
                />
              </div>
              <div className="w-[43px] h-[43px] rounded-[8px] bg-white/20 overflow-hidden">
                <Image
                  src={chrisChenAvatar}
                  alt="Design attachment 2"
                  width={43}
                  height={43}
                  className="w-full h-full object-cover opacity-70"
                />
              </div>
            </div>
          )}
          <p className="m-0 text-[16px] font-medium leading-[1.5em] text-white whitespace-pre-wrap text-justify">
            {message.content}
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── AI Message Bubble ──────────────────────────────────────────────────────

function AIMessage({ message }: { message: ChatMessage }) {
  return (
    <div className="flex flex-col gap-[8px] max-w-[600px]">
      {/* Message bubble */}
      <div
        className="bg-[rgba(0,0,0,0.04)] rounded-[12px] px-[16px] pt-[12px] pb-[16px] flex flex-col gap-[8px]"
        style={{
          boxShadow: "0px 2px 8px rgba(0,0,0,0.04)",
        }}
      >
        {/* Message text */}
        <div className="w-full">
          <p className="m-0 text-[16px] font-normal leading-[1.4em] text-[rgba(0,0,0,0.9)] whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-between gap-[9px]">
          <div className="flex items-center gap-[8px]">
            <button
              type="button"
              className="w-9 h-9 rounded-full bg-[rgba(0,0,0,0.04)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
              title="复制"
            >
              <CopyIcon />
            </button>
            <button
              type="button"
              className="w-9 h-9 rounded-full bg-[rgba(0,0,0,0.04)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
              title="重新生成"
            >
              <RegenerateIcon />
            </button>
          </div>
          <button
            type="button"
            className="w-9 h-9 rounded-full bg-[rgba(0,0,0,0.04)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
            title="下载"
          >
            <DownloadIcon />
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Page Component ─────────────────────────────────────────────────────────

export default function ChatDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: _conversationId } = use(params);
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(initialMockMessages);
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = useCallback(() => {
    if (!inputValue.trim()) return;
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: inputValue.trim(),
    };

    // Simulate AI reply
    const aiReply: ChatMessage = {
      id: `ai-${Date.now()}`,
      role: "assistant",
      content: `\u6536\u5230\u4F60\u7684\u6D88\u606F\uFF1A\u201C${inputValue.trim()}\u201D\n\n\u8FD9\u662F\u4E00\u4E2A\u6A21\u62DF\u56DE\u590D\uFF0C\u5B9E\u9645\u7684 AI \u56DE\u590D\u5C06\u7531\u540E\u7AEF\u670D\u52A1\u63D0\u4F9B\u3002`,
    };

    setMessages((prev) => [...prev, userMessage, aiReply]);
    setInputValue("");
  }, [inputValue]);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSubmit();
  };

  const handleAtClick = () => {
    setInputValue((prev) => prev + "@");
    textareaRef.current?.focus();
  };

  const handleSendOrMicClick = () => {
    if (inputValue.trim()) {
      handleSubmit();
    } else {
      alert("\u8BED\u97F3\u8F93\u5165\u529F\u80FD\u5F00\u53D1\u4E2D");
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#F0F1F2]">
      {/* Left Sidebar */}
      <Sidebar isLoggedIn={true} />

      {/* Right Content */}
      <div className="relative flex flex-col flex-1 min-w-0">
        {/* Top Bar with conversation title */}
        <TopBar showNewChat={true} title={mockConversationTitle} />

        {/* Chat Content Area */}
        <div className="flex-1 flex flex-col min-h-0">
          {/* Messages List (scrollable) */}
          <div className="flex-1 overflow-y-auto px-[60px] py-[10px]">
            <div className="flex flex-col gap-[10px] max-w-[780px] mx-auto">
              {messages.map((message) =>
                message.role === "user" ? (
                  <UserMessage key={message.id} message={message} />
                ) : (
                  <AIMessage key={message.id} message={message} />
                )
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Bottom Input Area (fixed to bottom) */}
          <div className="shrink-0 px-[60px] pb-[40px] pt-[10px]">
            <div className="max-w-[780px] mx-auto flex flex-col gap-[10px]">
              {/* Input Container with gradient border */}
              <form onSubmit={handleFormSubmit} className="input-gradient-border">
                <div className="input-gradient-border-inner px-[16px] py-[12px] flex flex-col gap-[2px]">
                  {/* Text Input Area */}
                  <div className="flex-1 py-[8px]">
                    <textarea
                      ref={textareaRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSubmit();
                        }
                      }}
                      placeholder={"简单描述设计方案背景与目标"}
                      className="w-full bg-transparent border-none outline-none resize-none text-[16px] leading-[1.4em] text-[rgba(0,0,0,0.9)] placeholder:text-[rgba(0,0,0,0.54)] font-normal min-h-[60px]"
                      rows={3}
                    />
                  </div>

                  {/* Bottom Toolbar */}
                  <div className="flex items-center justify-between">
                    {/* Left buttons */}
                    <div className="flex items-center gap-[3px] relative">
                      {/* @ Button */}
                      <button
                        type="button"
                        onClick={handleAtClick}
                        className="w-8 h-8 rounded-full bg-[rgba(0,0,0,0.04)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
                      >
                        <AtIcon />
                      </button>
                      {/* Attachment Button */}
                      <button
                        type="button"
                        onClick={() => setShowAttachmentMenu(!showAttachmentMenu)}
                        className="w-8 h-8 rounded-full bg-[rgba(0,0,0,0.04)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
                      >
                        <AttachmentIcon />
                      </button>
                      {/* Attachment Menu Popup */}
                      <AttachmentMenu
                        isOpen={showAttachmentMenu}
                        onClose={() => setShowAttachmentMenu(false)}
                      />
                    </div>

                    {/* Right - Send / Microphone button */}
                    <button
                      type="button"
                      onClick={handleSendOrMicClick}
                      className="w-8 h-8 rounded-full bg-[rgba(0,0,0,0.9)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.8)] transition-colors"
                      title={inputValue.trim() ? "\u53D1\u9001" : "\u8BED\u97F3\u8F93\u5165"}
                    >
                      {inputValue.trim() ? <SendIcon /> : <MicIcon />}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
