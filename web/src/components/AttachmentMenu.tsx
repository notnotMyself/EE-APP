"use client";

import { useEffect, useRef } from "react";

// ─── Icons ───────────────────────────────────────────────────────────────────

function ImageIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect
        x="2"
        y="3"
        width="16"
        height="14"
        rx="2"
        stroke="rgba(0,0,0,0.54)"
        strokeWidth="1.4"
      />
      <circle cx="7" cy="8" r="1.5" stroke="rgba(0,0,0,0.54)" strokeWidth="1.2" />
      <path
        d="M2 14l4-4 3 3 3-4 6 5"
        stroke="rgba(0,0,0,0.54)"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function FileIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M5 2h7l4 4v11a1 1 0 01-1 1H5a1 1 0 01-1-1V3a1 1 0 011-1z"
        stroke="rgba(0,0,0,0.54)"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12 2v4h4"
        stroke="rgba(0,0,0,0.54)"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function FigmaLinkIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M8.5 10a3 3 0 004.5 2.6M11.5 10a3 3 0 00-4.5-2.6M8.5 13l-1 1a2.83 2.83 0 01-4-4l1-1M11.5 7l1-1a2.83 2.83 0 014 4l-1 1"
        stroke="rgba(0,0,0,0.54)"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── Types ───────────────────────────────────────────────────────────────────

interface AttachmentMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

interface AttachmentOption {
  icon: React.ReactNode;
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
      icon: <ImageIcon />,
      label: "图片",
      action: () => {
        alert("图片上传功能开发中");
        onClose();
      },
    },
    {
      icon: <FileIcon />,
      label: "文件",
      action: () => {
        alert("文件上传功能开发中");
        onClose();
      },
    },
    {
      icon: <FigmaLinkIcon />,
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
              {option.icon}
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
