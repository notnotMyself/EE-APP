"use client";

import { useState, useRef, useEffect } from "react";

interface MentionItem {
  id: string;
  name: string;
  icon: string;
}

const mentionItems: MentionItem[] = [
  { id: "notepad", name: "便签", icon: "📝" },
  { id: "gallery", name: "相册", icon: "🖼️" },
  { id: "recorder", name: "录音", icon: "🎙️" },
  { id: "camera", name: "相机", icon: "📷" },
  { id: "weather", name: "天气", icon: "🌤️" },
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
        width: 240,
        backgroundColor: "#FFFFFF",
        borderRadius: 16,
        boxShadow: "0px 4px 24px rgba(0,0,0,0.12)",
        border: "1px solid rgba(0,0,0,0.06)",
        overflow: "hidden",
      }}
    >
      {/* Search input */}
      <div className="px-3 pt-3 pb-2">
        <input
          ref={inputRef}
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder="搜索应用..."
          className="w-full h-[32px] bg-[rgba(0,0,0,0.04)] rounded-[8px] px-3 text-[13px] text-[rgba(0,0,0,0.9)] placeholder:text-[rgba(0,0,0,0.3)] border-none outline-none"
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
      <div className="flex flex-col px-1 pb-1 max-h-[200px] overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="px-3 py-3 text-center">
            <span className="text-[12px] text-[rgba(0,0,0,0.3)]">无匹配结果</span>
          </div>
        ) : (
          filtered.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                onSelect(item);
                onClose();
              }}
              className="flex items-center gap-[10px] px-3 h-[40px] rounded-[10px] border-none bg-transparent cursor-pointer hover:bg-[rgba(0,0,0,0.04)] transition-colors w-full text-left"
            >
              <span className="text-[18px] w-6 h-6 flex items-center justify-center">{item.icon}</span>
              <span className="text-[13px] font-medium text-[rgba(0,0,0,0.9)]">{item.name}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

export type { MentionItem };
