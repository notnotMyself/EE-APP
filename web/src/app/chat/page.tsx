"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import AttachmentMenu from "@/components/AttachmentMenu";
import PersonalitySelector, { personalities } from "@/components/PersonalitySelector";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";

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

const suggestionChips = ["\u968F\u4FBF\u804A\u804A", "\u4EA4\u4E92\u9A8C\u8BC1", "\u89C6\u89C9\u8BA8\u8BBA", "\u65B9\u6848PK"];

export default function ChatPage() {
  const router = useRouter();
  const [inputValue, setInputValue] = useState("");
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  const [selectedPersonality, setSelectedPersonality] = useState("default");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback(
    (text?: string) => {
      const valueToSend = text ?? inputValue;
      if (!valueToSend.trim()) return;
      setInputValue("");
      router.push("/chat/new");
    },
    [inputValue, router]
  );

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

  const handleChipClick = (chip: string) => {
    setInputValue(chip);
    handleSubmit(chip);
  };

  const selectedPersonalityLabel =
    personalities.find((p) => p.id === selectedPersonality)?.label ?? "\u9ED8\u8BA4";

  return (
    <div className="flex h-screen w-full bg-[#F0F1F2]">
      {/* Left Sidebar */}
      <Sidebar isLoggedIn={true} />

      {/* Right Content */}
      <div className="relative flex flex-col flex-1 min-w-0">
        {/* Top Bar */}
        <TopBar showNewChat={true} />

        {/* Main Content Area */}
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
                  {"\u8EAB\u7ECF\u767E\u6218\uFF0C\u773C\u5149\u5982\u70AC\u7684\u8BBE\u8BA1\u8001\u6CD5\u5E08"}
                </span>
                <span className="w-1 h-1 rounded-full bg-[#3A3A3A] inline-block" />
                <button
                  type="button"
                  onClick={() => setShowPersonalitySelector(!showPersonalitySelector)}
                  className="flex items-center gap-[2px] bg-transparent border-none cursor-pointer p-0 hover:opacity-70 transition-opacity"
                >
                  <span className="text-[14px] font-normal leading-[1.43em] text-black/[0.54]">
                    {selectedPersonalityLabel === "\u9ED8\u8BA4" ? "\u9009\u62E9\u4E2A\u6027" : selectedPersonalityLabel}
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

            {/* Suggestion Chips */}
            <div className="flex items-end gap-[5px]">
              {suggestionChips.map((chip) => (
                <button
                  key={chip}
                  type="button"
                  onClick={() => handleChipClick(chip)}
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
      </div>
    </div>
  );
}
