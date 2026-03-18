"use client";

import { useEffect, useRef } from "react";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface Personality {
  id: string;
  label: string;
  iconFile: string;
}

export const personalities: Personality[] = [
  { id: "default",        label: "默认",     iconFile: "person.svg"       },
  { id: "friendly",       label: "亲和友善", iconFile: "smile.svg"        },
  { id: "straightforward",label: "直言不讳", iconFile: "voice.svg"        },
  { id: "professional",   label: "专业可靠", iconFile: "verified.svg"     },
  { id: "creative",       label: "天马行空", iconFile: "auto-awesome.svg" },
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
            选择 Chris Chen 人物个性
          </span>
        </div>

        {/* Options */}
        {personalities.map((personality) => {
          const isSelected = personality.id === selectedId;
          const iconColor = isSelected ? "#0066FF" : "rgba(0,0,0,0.7)";
          const iconUrl = `/icons/character/${personality.iconFile}`;

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
              {/* Icon — CSS mask lets us recolor a black SVG dynamically */}
              <span
                className="w-[20px] h-[20px] shrink-0"
                style={{
                  backgroundColor: iconColor,
                  WebkitMaskImage: `url('${iconUrl}')`,
                  maskImage: `url('${iconUrl}')`,
                  WebkitMaskRepeat: "no-repeat",
                  maskRepeat: "no-repeat",
                  WebkitMaskSize: "20px 20px",
                  maskSize: "20px 20px",
                }}
              />

              <span
                className="flex-1 text-left text-[14px] font-medium leading-[1.4em]"
                style={{ color: isSelected ? "#0066FF" : "rgba(0,0,0,0.9)" }}
              >
                {personality.label}
              </span>

              {isSelected && (
                <span className="flex items-center justify-center w-[20px] h-[20px]">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src="/icons/character/check.svg"
                    width={20}
                    height={20}
                    alt=""
                    aria-hidden="true"
                  />
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
