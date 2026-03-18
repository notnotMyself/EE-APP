"use client";

import { useState, useRef, useEffect } from "react";

interface MentionItem {
  id: string;
  name: string;
  icon: string;
}

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
      className="absolute bottom-full left-0 mb-[6px] z-50 glass-popup"
      style={{ width: 196 }}
    >
      {/* Search input */}
      <div className="px-2 pt-2 pb-1">
        <div className="relative">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/icons/tool/search.svg"
            width={16}
            height={16}
            alt=""
            aria-hidden="true"
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
          />
        <input
          ref={inputRef}
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder="搜索..."
          className="w-full h-[40px] bg-[rgba(0,0,0,0.04)] rounded-full pl-9 pr-4 text-[14px] text-[rgba(0,0,0,0.9)] placeholder:text-[rgba(0,0,0,0.3)] border-none outline-none"
          onKeyDown={(e) => {
            if (e.key === "Escape") onClose();
            if (e.key === "Enter" && filtered.length > 0) {
              onSelect(filtered[0]);
              onClose();
            }
          }}
        />
        </div>
      </div>

      {/* Items list */}
      <div className="flex flex-col px-2 pb-2 max-h-[240px] overflow-y-auto">
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
              className="flex items-center gap-[12px] px-3 h-[40px] rounded-[12px] border-none bg-transparent cursor-pointer hover:bg-[rgba(0,0,0,0.06)] transition-colors w-full text-left"
            >
              <span className="w-5 h-5 flex items-center justify-center shrink-0">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`/icons/tool/${item.icon}.svg`}
                  width={20}
                  height={20}
                  alt={item.name}
                  className="w-5 h-5"
                />
              </span>
              <span className="text-[14px] font-medium text-[rgba(0,0,0,0.9)]">{item.name}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

export type { MentionItem };
