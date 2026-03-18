"use client";

import { useEffect, useRef } from "react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface AttachmentMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

interface AttachmentOption {
  iconSrc: string;
  label: string;
  action: () => void;
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function AttachmentMenu({ isOpen, onClose }: AttachmentMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    // Use setTimeout to avoid the click that opened the menu from immediately closing it
    const timer = setTimeout(() => {
      document.addEventListener("mousedown", handleClickOutside);
    }, 0);

    return () => {
      clearTimeout(timer);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const options: AttachmentOption[] = [
    {
      iconSrc: "/icons/tool/image.svg",
      label: "图片",
      action: () => {
        alert("图片上传功能开发中");
        onClose();
      },
    },
    {
      iconSrc: "/icons/tool/file.svg",
      label: "文件",
      action: () => {
        alert("文件上传功能开发中");
        onClose();
      },
    },
    {
      iconSrc: "/icons/tool/link.svg",
      label: "Figma 链接",
      action: () => {
        alert("Figma 链接功能开发中");
        onClose();
      },
    },
  ];

  return (
    <div
      ref={menuRef}
      className="absolute bottom-[calc(100%+8px)] left-0 z-50 glass-popup"
      style={{ width: 196 }}
    >
      <div className="flex flex-col px-2 py-2">
        {options.map((option) => (
          <button
            key={option.label}
            type="button"
            onClick={option.action}
            className="flex items-center gap-[12px] px-3 h-[40px] w-full rounded-[12px] border-none bg-transparent cursor-pointer hover:bg-[rgba(0,0,0,0.06)] transition-colors text-left"
          >
            <span className="flex items-center justify-center w-[20px] h-[20px]">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={option.iconSrc}
                width={20}
                height={20}
                alt={option.label}
                className="w-5 h-5"
              />
            </span>
            <span className="text-[14px] font-medium text-[rgba(0,0,0,0.9)]">
              {option.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
