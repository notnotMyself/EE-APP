"use client";

import { useState, useRef, useEffect } from "react";

interface MentionItem {
  id: string;
  name: string;
  icon: string;
}

// ─── App Icons (inline SVGs matching Flutter's app_selector_popup) ──────────

function NotepadIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="2" width="12" height="16" rx="2" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" />
      <line x1="7" y1="6.5" x2="13" y2="6.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" strokeLinecap="round" />
      <line x1="7" y1="9.5" x2="13" y2="9.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" strokeLinecap="round" />
      <line x1="7" y1="12.5" x2="10" y2="12.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

function GalleryIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2.5" y="3.5" width="15" height="13" rx="2" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" />
      <circle cx="6.5" cy="7.5" r="1.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" />
      <path d="M2.5 13.5L6.5 10L9.5 13L12.5 9.5L17.5 14" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function RecorderIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="7.5" y="2" width="5" height="9" rx="2.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" />
      <path d="M5 10a5 5 0 0010 0" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="10" y1="15" x2="10" y2="18" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

function CameraIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1.5" y="5.5" width="17" height="12" rx="2" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" />
      <path d="M7 5.5L8 3h4l1 2.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="10" cy="11" r="3" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" />
    </svg>
  );
}

function WeatherIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="10" cy="8" r="3.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" />
      <line x1="10" y1="1.5" x2="10" y2="3" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="10" y1="13" x2="10" y2="14.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="3.5" y1="8" x2="5" y2="8" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="15" y1="8" x2="16.5" y2="8" stroke="rgba(0,0,0,0.54)" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M6 16a3 3 0 015 0" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

const iconComponents: Record<string, React.FC> = {
  notepad: NotepadIcon,
  gallery: GalleryIcon,
  recorder: RecorderIcon,
  camera: CameraIcon,
  weather: WeatherIcon,
};

const mentionItems: MentionItem[] = [
  { id: "notepad", name: "便签", icon: "notepad" },
  { id: "gallery", name: "相册", icon: "gallery" },
  { id: "recorder", name: "录音", icon: "recorder" },
  { id: "camera", name: "相机", icon: "camera" },
  { id: "weather", name: "天气", icon: "weather" },
];

interface AtMentionPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (item: MentionItem) => void;
  filterText?: string;
}

export default function AtMentionPopup({
  isOpen,
  onClose,
  onSelect,
  filterText = "",
}: AtMentionPopupProps) {
  const [searchText, setSearchText] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const displaySearch = filterText || searchText;
  const filtered = mentionItems.filter((item) =>
    item.name.toLowerCase().includes(displaySearch.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setSearchText("");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={containerRef}
      className="absolute bottom-full left-0 mb-[6px] z-50"
      style={{
        width: 196,
        backgroundColor: "rgba(239,239,239,0.8)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderRadius: 24,
        boxShadow: "0px 6px 54px rgba(0,0,0,0.14)",
        overflow: "hidden",
      }}
    >
      {/* Search input */}
      <div className="px-2 pt-2 pb-1">
        <input
          ref={inputRef}
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder="搜索应用..."
          className="w-full h-[40px] bg-[rgba(0,0,0,0.04)] rounded-full px-4 text-[13px] text-[rgba(0,0,0,0.9)] placeholder:text-[rgba(0,0,0,0.3)] border-none outline-none"
          onKeyDown={(e) => {
            if (e.key === "Escape") onClose();
            if (e.key === "Enter" && filtered.length > 0) {
              onSelect(filtered[0]);
              onClose();
            }
          }}
        />
      </div>

      {/* Items list */}
      <div className="flex flex-col px-2 pb-2 max-h-[240px] overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="px-3 py-3 text-center">
            <span className="text-[12px] text-[rgba(0,0,0,0.3)]">无匹配结果</span>
          </div>
        ) : (
          filtered.map((item) => {
            const IconComp = iconComponents[item.icon];
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  onSelect(item);
                  onClose();
                }}
                className="flex items-center gap-[12px] px-3 h-[40px] rounded-[12px] border-none bg-transparent cursor-pointer hover:bg-[rgba(0,0,0,0.06)] transition-colors w-full text-left"
              >
                <span className="w-5 h-5 flex items-center justify-center shrink-0">
                  {IconComp && <IconComp />}
                </span>
                <span className="text-[13px] font-medium text-[rgba(0,0,0,0.9)]">{item.name}</span>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}

export type { MentionItem };
