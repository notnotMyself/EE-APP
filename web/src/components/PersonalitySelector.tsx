"use client";

import { useEffect, useRef } from "react";

// ─── Icons ───────────────────────────────────────────────────────────────────

function PersonIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="10" cy="7" r="3" stroke="currentColor" strokeWidth="1.4" />
      <path d="M4 17c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

function SmileIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="10" cy="10" r="7.5" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="7.5" cy="8.5" r="1" fill="currentColor" />
      <circle cx="12.5" cy="8.5" r="1" fill="currentColor" />
      <path d="M7 12.5c1 1.5 5 1.5 6 0" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

function VoiceIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 10h2l2-4 3 8 2-6 2 2h3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function VerifiedIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 2l2.1 2.3H15v2.9L17 10l-2 2.8v2.9h-2.9L10 18l-2.1-2.3H5v-2.9L3 10l2-2.8V4.3h2.9L10 2z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
      <path d="M7 10l2 2 4-4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function AutoAwesomeIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 2l1.5 4.5L16 8l-4.5 1.5L10 14l-1.5-4.5L4 8l4.5-1.5L10 2z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
      <path d="M15 12l.75 2.25L18 15l-2.25.75L15 18l-.75-2.25L12 15l2.25-.75L15 12z" stroke="currentColor" strokeWidth="1" strokeLinejoin="round" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 8l3.5 3.5L13 5" stroke="#0066FF" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ─── Types ───────────────────────────────────────────────────────────────────

export interface Personality {
  id: string;
  label: string;
  icon: React.ReactNode;
}

export const personalities: Personality[] = [
  { id: "default", label: "\u9ED8\u8BA4", icon: <PersonIcon /> },
  { id: "friendly", label: "\u4EB2\u548C\u53CB\u5584", icon: <SmileIcon /> },
  { id: "straightforward", label: "\u76F4\u8A00\u4E0D\u8BB3", icon: <VoiceIcon /> },
  { id: "professional", label: "\u4E13\u4E1A\u53EF\u9760", icon: <VerifiedIcon /> },
  { id: "creative", label: "\u5929\u9A6C\u884C\u7A7A", icon: <AutoAwesomeIcon /> },
];

interface PersonalitySelectorProps {
  isOpen: boolean;
  onClose: () => void;
  selectedId: string;
  onSelect: (id: string) => void;
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function PersonalitySelector({
  isOpen,
  onClose,
  selectedId,
  onSelect,
}: PersonalitySelectorProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    const timer = setTimeout(() => {
      document.addEventListener("mousedown", handleClickOutside);
    }, 0);

    return () => {
      clearTimeout(timer);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      className="absolute z-50 glass-popup"
      style={{ width: 196 }}
    >
      <div className="flex flex-col py-[8px]">
        {/* Title */}
        <div className="px-[20px] py-[6px]">
          <span className="text-[12px] font-normal leading-[1.33em] text-[rgba(0,0,0,0.54)]">
            {"\u9009\u62E9 Chris Chen \u4EBA\u7269\u4E2A\u6027"}
          </span>
        </div>

        {/* Options */}
        {personalities.map((personality) => {
          const isSelected = personality.id === selectedId;
          return (
            <button
              key={personality.id}
              type="button"
              onClick={() => {
                onSelect(personality.id);
                onClose();
              }}
              className="flex items-center gap-[12px] px-[20px] py-[10px] border-none bg-transparent cursor-pointer hover:bg-[rgba(0,0,0,0.06)] transition-colors"
            >
              <span
                className="flex items-center justify-center w-[20px] h-[20px]"
                style={{ color: isSelected ? "#0066FF" : "rgba(0,0,0,0.7)" }}
              >
                {personality.icon}
              </span>
              <span
                className="flex-1 text-left text-[14px] font-medium leading-[1.4em]"
                style={{ color: isSelected ? "#0066FF" : "rgba(0,0,0,0.9)" }}
              >
                {personality.label}
              </span>
              {isSelected && (
                <span className="flex items-center justify-center w-[16px] h-[16px]">
                  <CheckIcon />
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
