"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/contexts/AuthContext";
import { useChatLayout } from "@/contexts/ChatLayoutContext";
import { createConversation } from "@/lib/api";
import AttachmentMenu from "@/components/AttachmentMenu";
import AtMentionPopup from "@/components/AtMentionPopup";
import PersonalitySelector, { personalities } from "@/components/PersonalitySelector";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";

// Default agent for "AI 评审" tab — matches backend agent_mapping
const DEFAULT_AGENT_ID = "dev_efficiency_analyst";

function DropdownArrowIcon() {
  return (
    <svg
      width="12"
      height="6"
      viewBox="0 0 12 6"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M1 1L6 5L11 1"
        stroke="rgba(0,0,0,0.54)"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const suggestionChips = ["随便聊聊", "交互验证", "视觉讨论", "方案PK"];

export default function ChatPage() {
  const router = useRouter();
  const { accessToken } = useAuth();
  const { setTitle } = useChatLayout();
  const [inputValue, setInputValue] = useState("");
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
  const [showAtMention, setShowAtMention] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  const [selectedPersonality, setSelectedPersonality] = useState("default");
  const [isCreating, setIsCreating] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Clear TopBar title when entering new chat page
  useEffect(() => {
    setTitle(undefined);
  }, [setTitle]);

  const handleSubmit = useCallback(
    async (text?: string) => {
      const valueToSend = text ?? inputValue;
      if (!valueToSend.trim() || isCreating) return;

      setInputValue("");

      if (!accessToken) {
        // Fallback: local-only navigation (should not happen if logged in)
        const convId = `new-${Date.now()}`;
        router.push(`/chat/${convId}?q=${encodeURIComponent(valueToSend.trim())}`);
        return;
      }

      // Create a real conversation via API, then navigate
      setIsCreating(true);
      try {
        const conv = await createConversation(accessToken, DEFAULT_AGENT_ID);
        router.push(
          `/chat/${conv.id}?q=${encodeURIComponent(valueToSend.trim())}`
        );
      } catch (err) {
        console.error("Failed to create conversation:", err);
        // Fallback to local ID
        const convId = `new-${Date.now()}`;
        router.push(`/chat/${convId}?q=${encodeURIComponent(valueToSend.trim())}`);
      } finally {
        setIsCreating(false);
      }
    },
    [inputValue, router, accessToken, isCreating]
  );

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

  const handleChipClick = (chip: string) => {
    setInputValue(chip);
    textareaRef.current?.focus();
  };

  const selectedPersonalityLabel =
    personalities.find((p) => p.id === selectedPersonality)?.label ?? "默认";

  return (
        <div className="flex-1 flex flex-col items-center relative">
          {/* Profile Section - centered in upper area */}
          <div className="flex flex-col items-center gap-[14px] mt-[130px]">
            {/* Avatar */}
            <div className="w-[130px] h-[130px] rounded-full overflow-hidden shadow-[0px_6px_32px_rgba(0,0,0,0.1)]">
              <Image
                src={chrisChenAvatar}
                alt="Chris Chen"
                width={130}
                height={130}
                className="w-full h-full object-cover"
                priority
              />
            </div>

            {/* Name */}
            <h1 className="font-[var(--font-heading)] text-[26px] font-bold leading-[1.1em] text-[#0D1B34] m-0">
              {" "}Chris Chen
            </h1>

            {/* Description Row */}
            <div className="flex items-center gap-[2px] relative">
              <div className="flex items-center gap-1">
                <span className="text-[14px] font-normal leading-[1.43em] text-black/[0.54]">
                  身经百战，眼光如炬的设计老法师
                </span>
                <span className="w-1 h-1 rounded-full bg-[#3A3A3A] inline-block" />
                <button
                  type="button"
                  onClick={() => setShowPersonalitySelector(!showPersonalitySelector)}
                  className="flex items-center gap-[2px] bg-transparent border-none cursor-pointer p-0 hover:opacity-70 transition-opacity"
                >
                  <span className="text-[14px] font-normal leading-[1.43em] text-black/[0.54]">
                    {selectedPersonalityLabel === "默认" ? "选择个性" : selectedPersonalityLabel}
                  </span>
                  <DropdownArrowIcon />
                </button>
              </div>
              {/* Personality Selector Popup */}
              {showPersonalitySelector && (
                <div className="absolute top-[calc(100%+8px)] right-0">
                  <PersonalitySelector
                    isOpen={showPersonalitySelector}
                    onClose={() => setShowPersonalitySelector(false)}
                    selectedId={selectedPersonality}
                    onSelect={setSelectedPersonality}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Input Area - positioned in lower portion */}
          <div className="absolute bottom-[60px] left-1/2 -translate-x-1/2 w-[915px] flex flex-col gap-[10px]">
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
                    disabled={isCreating}
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
                    disabled={isCreating}
                    className="w-8 h-8 rounded-full bg-[rgba(0,0,0,0.9)] flex items-center justify-center border-none cursor-pointer hover:bg-[rgba(0,0,0,0.8)] transition-colors disabled:opacity-50"
                    title="发送"
                  >
                    <img src="/icons/chat/send_icon_active.svg" width={20} height={20} alt="发送" />
                  </button>
                </div>
              </div>
            </form>

            {/* Suggestion Chips */}
            <div className="flex items-end gap-[5px]">
              {suggestionChips.map((chip) => (
                <button
                  key={chip}
                  type="button"
                  onClick={() => handleChipClick(chip)}
                  disabled={isCreating}
                  className="chip-gradient-border"
                >
                  <span className="chip-gradient-border-inner">
                    <span className="text-[12px] font-normal leading-[1.4em] text-[rgba(0,0,0,0.54)] text-center whitespace-nowrap">
                      {chip}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
  );
}
