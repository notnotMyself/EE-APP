"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/contexts/AuthContext";
import { useChatLayout } from "@/contexts/ChatLayoutContext";
import { createConversation } from "@/lib/api";
import AttachmentMenu from "@/components/AttachmentMenu";
import AtMentionPopup from "@/components/AtMentionPopup";
import PendingImagesBar from "@/components/chat/PendingImagesBar";
import PersonalitySelector, { personalities } from "@/components/PersonalitySelector";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";
import { uploadImage, extractImageFiles, type Attachment } from "@/lib/upload";

// Default agent: Chris Chen (design_validator) — UUID from Supabase agents table
const DEFAULT_AGENT_ID = "bba2fa4e-e343-47f4-b58d-3848e6853a6e";

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

const DEFAULT_PLACEHOLDER = "简单描述设计方案背景与目标";

const chipPlaceholders: Record<string, string> = {
  随便聊聊: "这是一个什么产品 / 功能，核心解决什么问题",
  交互验证: "描述产品目标，用户使用的核心路径",
  视觉讨论: "描述产品目标，用户使用的核心路径",
  方案PK: "简单列出两个你在犹豫的方案差异，写清楚你为什么犹豫",
};

// 与 Flutter quick_action_button.dart 对齐：null 表示不拼前缀
const chipModeIds: Record<string, string | null> = {
  随便聊聊: null,
  交互验证: "interaction_check",
  视觉讨论: "visual_consistency",
  方案PK: "compare_designs",
};

const suggestionChips = Object.keys(chipPlaceholders);

export default function ChatPage() {
  const router = useRouter();
  const { accessToken } = useAuth();
  const { setTitle, addConversation } = useChatLayout();
  const [inputValue, setInputValue] = useState("");
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
  const [showAtMention, setShowAtMention] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  const [selectedPersonality, setSelectedPersonality] = useState("default");
  const [isCreating, setIsCreating] = useState(false);
  const [selectedChip, setSelectedChip] = useState<string | null>(null);
  const [pendingAttachments, setPendingAttachments] = useState<Attachment[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Clear TopBar title when entering new chat page
  useEffect(() => {
    setTitle(undefined);
  }, [setTitle]);

  // Handle image file selection (from AttachmentMenu or paste)
  const handleImageFiles = useCallback(async (files: File[]) => {
    setIsUploading(true);
    try {
      const uploaded = await Promise.all(files.map((f) => uploadImage(f)));
      setPendingAttachments((prev) => [...prev, ...uploaded]);
    } catch (err) {
      console.error("Image upload failed:", err);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handlePaste = useCallback(
    (e: React.ClipboardEvent) => {
      const imageFiles = extractImageFiles(e.clipboardData);
      if (imageFiles.length > 0) {
        e.preventDefault();
        handleImageFiles(imageFiles);
      }
    },
    [handleImageFiles]
  );

  const removePendingAttachment = useCallback((id: string) => {
    setPendingAttachments((prev) => prev.filter((a) => a.id !== id));
  }, []);

  const handleSubmit = useCallback(
    async (text?: string) => {
      const valueToSend = text ?? inputValue;
      if ((!valueToSend.trim() && pendingAttachments.length === 0) || isCreating) return;

      setInputValue("");
      if (textareaRef.current) textareaRef.current.style.height = "auto";
      const attachmentsToSend = pendingAttachments.length > 0 ? [...pendingAttachments] : undefined;
      setPendingAttachments([]);

      if (!accessToken) {
        const convId = `new-${Date.now()}`;
        router.push(`/chat/${convId}?q=${encodeURIComponent(valueToSend.trim())}`);
        return;
      }

      setIsCreating(true);
      const modeId = selectedChip ? chipModeIds[selectedChip] : null;
      const msgText = modeId
        ? `[MODE:${modeId}] ${valueToSend.trim()}`
        : valueToSend.trim();
      const title = msgText.length > 20 ? msgText.slice(0, 20) + "…" : msgText;
      try {
        const conv = await createConversation(accessToken, DEFAULT_AGENT_ID, title);
        addConversation(conv);
        // Store attachments in sessionStorage for the chat detail page to pick up
        if (attachmentsToSend && attachmentsToSend.length > 0) {
          sessionStorage.setItem(
            `pending-attachments-${conv.id}`,
            JSON.stringify(attachmentsToSend)
          );
        }
        router.push(
          `/chat/${conv.id}?q=${encodeURIComponent(msgText)}`
        );
      } catch (err) {
        console.error("Failed to create conversation:", err);
        const convId = `new-${Date.now()}`;
        router.push(`/chat/${convId}?q=${encodeURIComponent(msgText)}`);
      } finally {
        setIsCreating(false);
      }
    },
    [inputValue, router, accessToken, isCreating, addConversation, selectedChip, pendingAttachments]
  );

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSubmit();
  };

  const handleAtClick = () => {
    setShowAtMention(!showAtMention);
  };

  const handleSendClick = () => {
    if (inputValue.trim() || pendingAttachments.length > 0) {
      handleSubmit();
    }
  };

  const handleChipClick = (chip: string) => {
    setSelectedChip((prev) => (prev === chip ? null : chip));
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
          <div className="absolute bottom-[60px] left-1/2 -translate-x-1/2 w-full max-w-[915px] px-6 flex flex-col gap-[10px]">
            {/* Input Container with gradient border */}
            <form onSubmit={handleFormSubmit} className="input-gradient-border">
              <div className="input-gradient-border-inner px-[16px] py-[12px] flex flex-col gap-[2px]">
                {/* Pending image previews */}
                <PendingImagesBar
                  attachments={pendingAttachments}
                  uploading={isUploading}
                  onRemove={removePendingAttachment}
                />
                {/* Text Input Area */}
                <div className="flex-1 py-[8px]">
                  <textarea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={(e) => {
                      setInputValue(e.target.value);
                      e.target.style.height = "auto";
                      e.target.style.height = e.target.scrollHeight + "px";
                    }}
                    onPaste={handlePaste}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                    placeholder={selectedChip ? chipPlaceholders[selectedChip] : DEFAULT_PLACEHOLDER}
                    className="w-full bg-transparent border-none outline-none resize-none text-[14px] leading-[1.65em] text-[rgba(0,0,0,0.9)] placeholder:text-[rgba(0,0,0,0.3)] font-normal"
                    rows={1}
                    style={{ maxHeight: 200 }}
                    disabled={isCreating}
                  />
                </div>

                {/* Bottom Toolbar */}
                <div className="flex items-center justify-between">
                  {/* Left buttons */}
                  <div className="flex items-center gap-[3px] relative">
                    {/* @ Button (disabled) */}
                    <button
                      type="button"
                      disabled
                      className="w-8 h-8 rounded-full bg-[rgba(0,0,0,0.04)] grid place-items-center border-none cursor-not-allowed opacity-30 text-[16px] font-medium text-[rgba(0,0,0,0.8)]"
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
                      onImageSelect={handleImageFiles}
                    />
                  </div>

                  {/* Right - Send button */}
                  {(() => {
                    const hasContent = inputValue.trim().length > 0 || pendingAttachments.length > 0;
                    return (
                      <button
                        type="button"
                        onClick={handleSendClick}
                        disabled={isCreating || !hasContent}
                        className={`w-8 h-8 rounded-full flex items-center justify-center border-none transition-colors ${
                          hasContent
                            ? "bg-[rgba(0,0,0,0.9)] cursor-pointer hover:bg-[rgba(0,0,0,0.8)]"
                            : "bg-[rgba(0,0,0,0.04)] cursor-default"
                        }`}
                        title="发送"
                      >
                        <img
                          src={hasContent ? "/icons/chat/send_icon_active.svg" : "/icons/chat/send_icon.svg"}
                          width={20}
                          height={20}
                          alt="发送"
                        />
                      </button>
                    );
                  })()}
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
                  className={`glass-chip${selectedChip === chip ? " glass-chip--selected" : ""}`}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        </div>
  );
}
