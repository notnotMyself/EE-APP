"use client";

import { useState, useRef, useEffect, use, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useChatLayout } from "@/contexts/ChatLayoutContext";
import { listMessages, updateConversationTitle, type Message as ApiMessage } from "@/lib/api";
import { ConversationWebSocket } from "@/lib/websocket";
import AttachmentMenu from "@/components/AttachmentMenu";
import AtMentionPopup from "@/components/AtMentionPopup";
import { useStreamingBuffer } from "@/hooks/useStreamingBuffer";
import UserMessage from "@/components/chat/UserMessage";
import AIMessage from "@/components/chat/AIMessage";
import type { ChatMessage } from "@/components/chat/ChatMessage";

// ─── Page Component ─────────────────────────────────────────────────────────

export default function ChatDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: conversationId } = use(params);
  const searchParams = useSearchParams();
  const { accessToken } = useAuth();
  const { setTitle, updateConversation } = useChatLayout();
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
  const [showAtMention, setShowAtMention] = useState(false);
  const [conversationTitle, setConversationTitle] = useState("新对话");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isNearBottomRef = useRef(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const wsRef = useRef<ConversationWebSocket | null>(null);
  const initialMessageSent = useRef(false);
  const streamingMessageId = useRef<string | null>(null);

  const streamBuffer = useStreamingBuffer();

  // Sync conversation title up to the persistent ChatLayout TopBar
  useEffect(() => {
    setTitle(conversationTitle);
  }, [conversationTitle, setTitle]);

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
        if (loaded.length > 0) {
          setMessages(loaded);
        }
        const firstUser = apiMessages.find((m: ApiMessage) => m.role === "user");
        if (firstUser) {
          const derived =
            firstUser.content.slice(0, 20) +
            (firstUser.content.length > 20 ? "…" : "");
          setConversationTitle(derived);
          updateConversation(conversationId, { title: derived });
          if (accessToken) {
            updateConversationTitle(accessToken, conversationId, derived).catch(() => {});
          }
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
      console.log("[ChatPage] pendingInitialQuery SET:", q.slice(0, 30));
      const userMsg: ChatMessage = {
        id: `user-init-${Date.now()}`,
        role: "user",
        content: q,
      };
      setMessages((prev) => (prev.length === 0 ? [userMsg] : prev));
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
        const q = pendingInitialQuery.current;
        console.log("[ChatPage] onConnected, pendingInitialQuery:", q ? q.slice(0, 30) : "null");
        if (q) {
          pendingInitialQuery.current = null;
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
        const finalContent = streamBuffer.networkBuffer.current;
        const doneId = streamingMessageId.current;
        if (doneId) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === doneId
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
        const errorId = streamingMessageId.current;
        if (errorId) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === errorId
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
        console.log("[ChatPage] onClose, pendingInitialQuery:", pendingInitialQuery.current ? "has value" : "null", "| streaming:", streamingMessageId.current);
        const closeId = streamingMessageId.current;
        if (closeId) {
          streamBuffer.finish();
          const finalContent = streamBuffer.networkBuffer.current;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === closeId
                ? { ...m, content: finalContent || "[连接断开]", isStreaming: false }
                : m
            )
          );
          streamingMessageId.current = null;
          setIsGenerating(false);
          streamBuffer.reset();
        }
      },
      onPermanentClose: () => {
        console.log("[ChatPage] onPermanentClose, pendingInitialQuery:", pendingInitialQuery.current ? "has value" : "null");
        if (pendingInitialQuery.current) {
          const q = pendingInitialQuery.current;
          pendingInitialQuery.current = null;
          const aiId = `ai-fallback-${Date.now()}`;
          setMessages((prev) => [
            ...prev,
            {
              id: aiId,
              role: "assistant",
              content: `收到你的消息："${q}"\n\n当前无法连接到后端服务，请检查网络连接后重试。`,
              isStreaming: false,
            },
          ]);
        }
      },
    });

    wsRef.current = ws;
    console.log("[ChatPage] WS effect: connect()", { conversationId });
    ws.connect();

    return () => {
      console.log("[ChatPage] WS effect: cleanup → disconnect()", { conversationId, pendingQuery: pendingInitialQuery.current ? "has value" : "null" });
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

  // Auto-scroll to bottom when messages change (only if user is near bottom)
  useEffect(() => {
    if (isNearBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  function sendMessageViaWS(ws: ConversationWebSocket, text: string) {
    isNearBottomRef.current = true;
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

    const connected = wsRef.current?.isConnected ?? false;
    console.log("[ChatPage] handleSubmit, wsConnected:", connected, "| wsRef:", wsRef.current ? "exists" : "null");

    if (connected) {
      sendMessageViaWS(wsRef.current!, userText);
    } else {
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
    setShowAtMention(!showAtMention);
  };

  const handleSendClick = () => {
    if (inputValue.trim()) {
      handleSubmit();
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Messages List (scrollable) */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-[60px] py-[10px]"
        onScroll={(e) => {
          const el = e.currentTarget;
          isNearBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 150;
        }}
      >
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
                    className="w-8 h-8 rounded-full bg-[rgba(0,0,0,0.04)] grid place-items-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.08)] transition-colors text-[16px] font-medium text-[rgba(0,0,0,0.8)]"
                  >
                    <span className="inline-block -translate-y-px">@</span>
                  </button>
                  {/* @ Mention Popup */}
                  <AtMentionPopup
                    isOpen={showAtMention}
                    onClose={() => setShowAtMention(false)}
                    onSelect={(item) => {
                      setInputValue((prev) => prev + `@${item.name} `);
                      textareaRef.current?.focus();
                    }}
                  />
                  {/* Attachment Button */}
                  <button
                    type="button"
                    onClick={() => setShowAttachmentMenu(!showAttachmentMenu)}
                    className="w-8 h-8 flex items-center justify-center border-none cursor-pointer bg-transparent p-0 hover:opacity-80 transition-opacity"
                  >
                    <img src="/icons/chat/attachment_icon.svg" width={32} height={32} alt="附件" />
                  </button>
                  {/* Attachment Menu Popup */}
                  <AttachmentMenu
                    isOpen={showAttachmentMenu}
                    onClose={() => setShowAttachmentMenu(false)}
                  />
                </div>

                {/* Right - Send button */}
                <button
                  type="button"
                  onClick={handleSendClick}
                  className="w-8 h-8 rounded-full bg-[rgba(0,0,0,0.9)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.8)] transition-colors"
                  title="发送"
                >
                  <img src="/icons/chat/send_icon_active.svg" width={20} height={20} alt="发送" />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
