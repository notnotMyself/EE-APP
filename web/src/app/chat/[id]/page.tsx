"use client";

import { useState, useRef, useEffect, use, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/contexts/AuthContext";
import { listMessages, type Message as ApiMessage } from "@/lib/api";
import { ConversationWebSocket } from "@/lib/websocket";
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
      <rect x="1.5" y="1.5" width="8.5" height="8.5" rx="1" stroke="rgba(0,0,0,0.9)" strokeWidth="1.26" />
      <rect x="5" y="5" width="8.5" height="8.5" rx="1" stroke="rgba(0,0,0,0.9)" strokeWidth="1.26" />
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

// ─── Types ──────────────────────────────────────────────────────────────────

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  hasImages?: boolean;
  isStreaming?: boolean;
}

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
      <div
        className="bg-[rgba(0,0,0,0.04)] rounded-[12px] px-[16px] pt-[12px] pb-[16px] flex flex-col gap-[8px]"
        style={{ boxShadow: "0px 2px 8px rgba(0,0,0,0.04)" }}
      >
        <div className="w-full">
          <p className="m-0 text-[16px] font-normal leading-[1.4em] text-[rgba(0,0,0,0.9)] whitespace-pre-wrap">
            {message.content}
            {message.isStreaming && (
              <span className="inline-block w-[2px] h-[1em] bg-[rgba(0,0,0,0.6)] ml-[1px] align-middle animate-pulse" />
            )}
          </p>
        </div>

        {/* Action buttons - hidden while streaming */}
        {!message.isStreaming && message.content && (
          <div className="flex items-center justify-between gap-[9px]">
            <div className="flex items-center gap-[8px]">
              <button
                type="button"
                className="w-9 h-9 rounded-full bg-[rgba(0,0,0,0.04)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors"
                title="复制"
                onClick={() => navigator.clipboard.writeText(message.content)}
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
        )}
      </div>
    </div>
  );
}

// ─── Streaming buffer ───────────────────────────────────────────────────────
// 2-level buffer matching the Flutter app:
// Level 1: Network chunks accumulate in a buffer (50ms flush interval)
// Level 2: Display buffer renders chars with a typewriter effect (30ms per chunk)

function useStreamingBuffer() {
  const networkBuffer = useRef("");
  const displayedRef = useRef("");
  const flushTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const typeTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const setContentFn = useRef<((s: string) => void) | null>(null);

  const startTypewriter = useCallback(() => {
    if (typeTimer.current) return;
    typeTimer.current = setInterval(() => {
      const target = networkBuffer.current;
      const displayed = displayedRef.current;
      if (displayed.length >= target.length) {
        // caught up — stop typewriter until more data arrives
        if (typeTimer.current) {
          clearInterval(typeTimer.current);
          typeTimer.current = null;
        }
        return;
      }
      const chunkSize = Math.min(6, target.length - displayed.length);
      displayedRef.current = target.slice(0, displayed.length + chunkSize);
      setContentFn.current?.(displayedRef.current);
    }, 30);
  }, []);

  const pushChunk = useCallback(
    (chunk: string) => {
      networkBuffer.current += chunk;
      startTypewriter();
    },
    [startTypewriter]
  );

  const finish = useCallback(() => {
    // Immediately display all remaining content
    if (typeTimer.current) {
      clearInterval(typeTimer.current);
      typeTimer.current = null;
    }
    if (flushTimer.current) {
      clearInterval(flushTimer.current);
      flushTimer.current = null;
    }
    displayedRef.current = networkBuffer.current;
    setContentFn.current?.(displayedRef.current);
  }, []);

  const reset = useCallback(() => {
    networkBuffer.current = "";
    displayedRef.current = "";
    if (typeTimer.current) {
      clearInterval(typeTimer.current);
      typeTimer.current = null;
    }
    if (flushTimer.current) {
      clearInterval(flushTimer.current);
      flushTimer.current = null;
    }
  }, []);

  const bindSetter = useCallback((fn: (s: string) => void) => {
    setContentFn.current = fn;
  }, []);

  return { pushChunk, finish, reset, bindSetter, displayedRef };
}

// ─── Page Component ─────────────────────────────────────────────────────────

export default function ChatDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: conversationId } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isLoggedIn, isLoading, accessToken } = useAuth();
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
  const [conversationTitle, setConversationTitle] = useState("新对话");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const wsRef = useRef<ConversationWebSocket | null>(null);
  const initialMessageSent = useRef(false);
  const streamingMessageId = useRef<string | null>(null);

  const streamBuffer = useStreamingBuffer();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isLoggedIn) {
      router.replace("/login");
    }
  }, [isLoading, isLoggedIn, router]);

  // Load existing messages from API
  useEffect(() => {
    if (!accessToken || !conversationId || conversationId.startsWith("new-"))
      return;

    listMessages(accessToken, conversationId)
      .then(({ messages: apiMessages }) => {
        const loaded: ChatMessage[] = apiMessages
          .filter((m: ApiMessage) => m.role === "user" || m.role === "assistant")
          .map((m: ApiMessage) => ({
            id: m.id,
            role: m.role as "user" | "assistant",
            content: m.content_type === "briefing_card" ? "[简报卡片]" : m.content,
          }));
        // Only replace messages if API returned actual history;
        // don't wipe out the initial ?q= message for a fresh conversation.
        if (loaded.length > 0) {
          setMessages(loaded);
        }
        // Use first user message as title hint
        const firstUser = apiMessages.find((m: ApiMessage) => m.role === "user");
        if (firstUser) {
          setConversationTitle(
            firstUser.content.slice(0, 20) + (firstUser.content.length > 20 ? "..." : "")
          );
        }
      })
      .catch((err) => console.error("Failed to load messages:", err));
  }, [accessToken, conversationId]);

  // Show initial user message from ?q= param immediately (before WS connects)
  useEffect(() => {
    if (initialMessageSent.current) return;
    const q = searchParams.get("q");
    if (q) {
      initialMessageSent.current = true;
      // Show user message bubble right away
      const userMsg: ChatMessage = {
        id: `user-init-${Date.now()}`,
        role: "user",
        content: q,
      };
      setMessages((prev) => (prev.length === 0 ? [userMsg] : prev));
      // Store the pending initial query for WS to pick up
      pendingInitialQuery.current = q;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const pendingInitialQuery = useRef<string | null>(null);

  // Connect WebSocket
  useEffect(() => {
    if (!accessToken || !conversationId || conversationId.startsWith("new-"))
      return;

    const ws = new ConversationWebSocket(conversationId, accessToken, {
      onConnected: () => {
        // If there's a pending initial query, send it via WS now
        const q = pendingInitialQuery.current;
        if (q) {
          pendingInitialQuery.current = null;
          // Add AI streaming placeholder and send
          const aiId = `ai-${Date.now()}`;
          streamingMessageId.current = aiId;
          setMessages((prev) => [
            ...prev,
            { id: aiId, role: "assistant", content: "", isStreaming: true },
          ]);
          setIsGenerating(true);
          streamBuffer.reset();
          ws.sendMessage(q);
        }
      },
      onTextChunk: (content) => {
        streamBuffer.pushChunk(content);
      },
      onDone: () => {
        streamBuffer.finish();
        const finalContent = streamBuffer.displayedRef.current;
        // Mark streaming message as complete
        if (streamingMessageId.current) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageId.current
                ? { ...m, content: finalContent, isStreaming: false }
                : m
            )
          );
          streamingMessageId.current = null;
        }
        setIsGenerating(false);
        streamBuffer.reset();
      },
      onError: (content) => {
        console.error("WS error:", content);
        if (streamingMessageId.current) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageId.current
                ? {
                    ...m,
                    content: m.content || `[Error: ${content}]`,
                    isStreaming: false,
                  }
                : m
            )
          );
          streamingMessageId.current = null;
        }
        setIsGenerating(false);
        streamBuffer.reset();
      },
      onClose: () => {
        // Connection lost — if we had a pending initial query that never got sent, show fallback
        if (pendingInitialQuery.current) {
          const q = pendingInitialQuery.current;
          pendingInitialQuery.current = null;
          // Show fallback response
          const aiId = `ai-fallback-${Date.now()}`;
          const fallbackReply = `收到你的消息："${q}"\n\n当前无法连接到后端服务，请检查网络连接后重试。`;
          setMessages((prev) => [
            ...prev,
            { id: aiId, role: "assistant", content: fallbackReply, isStreaming: false },
          ]);
        }
        // Stop streaming if active
        if (streamingMessageId.current) {
          streamBuffer.finish();
          const finalContent = streamBuffer.displayedRef.current;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageId.current
                ? { ...m, content: finalContent || "[连接断开]", isStreaming: false }
                : m
            )
          );
          streamingMessageId.current = null;
          setIsGenerating(false);
          streamBuffer.reset();
        }
      },
    });

    wsRef.current = ws;
    ws.connect();

    return () => {
      ws.disconnect();
      wsRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken, conversationId]);

  // Bind the streaming buffer setter to update the streaming message's content
  useEffect(() => {
    streamBuffer.bindSetter((displayedContent) => {
      if (!streamingMessageId.current) return;
      const msgId = streamingMessageId.current;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === msgId ? { ...m, content: displayedContent } : m
        )
      );
    });
  }, [streamBuffer]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function sendMessageViaWS(ws: ConversationWebSocket, text: string) {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
    };

    const aiId = `ai-${Date.now()}`;
    streamingMessageId.current = aiId;

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: aiId, role: "assistant", content: "", isStreaming: true },
    ]);
    setIsGenerating(true);

    streamBuffer.reset();
    ws.sendMessage(text);
  }

  const handleSubmit = useCallback(() => {
    if (!inputValue.trim() || isGenerating) return;
    const userText = inputValue.trim();
    setInputValue("");

    if (wsRef.current?.isConnected) {
      sendMessageViaWS(wsRef.current, userText);
    } else {
      // Fallback: mock streaming for when WS is not connected
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: userText,
      };
      const aiId = `ai-${Date.now()}`;
      const fallbackReply = `收到你的消息："${userText}"\n\n当前无法连接到后端服务，请检查网络连接后重试。`;

      setMessages((prev) => [
        ...prev,
        userMessage,
        { id: aiId, role: "assistant", content: "", isStreaming: true },
      ]);
      setIsGenerating(true);

      let charIndex = 0;
      const interval = setInterval(() => {
        const chunkSize = Math.floor(Math.random() * 3) + 2;
        charIndex = Math.min(charIndex + chunkSize, fallbackReply.length);
        if (charIndex >= fallbackReply.length) {
          clearInterval(interval);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiId
                ? { ...m, content: fallbackReply, isStreaming: false }
                : m
            )
          );
          setIsGenerating(false);
        } else {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiId
                ? { ...m, content: fallbackReply.slice(0, charIndex) }
                : m
            )
          );
        }
      }, 30);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inputValue, isGenerating]);

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
      alert("语音输入功能开发中");
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#F0F1F2]">
      {/* Left Sidebar */}
      <Sidebar isLoggedIn={isLoggedIn} />

      {/* Right Content */}
      <div className="relative flex flex-col flex-1 min-w-0">
        {/* Top Bar with conversation title */}
        <TopBar showNewChat={true} title={conversationTitle} />

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
                      title={inputValue.trim() ? "发送" : "语音输入"}
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
