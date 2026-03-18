import Image from "next/image";
import chrisChenAvatar from "@/assets/images/chris_chen_avatar.jpeg";
import type { ChatMessage } from "./ChatMessage";

interface UserMessageProps {
  message: ChatMessage;
}

// ─── UserMessage ─────────────────────────────────────────────────────────────
// 用户消息气泡（蓝色背景，右对齐）。纯展示组件，无内部状态。

export default function UserMessage({ message }: UserMessageProps) {
  return (
    <div className="flex justify-end">
      <div
        className="flex flex-col gap-[10px] max-w-[480px]"
        style={{
          backgroundColor: "#2C69FF",
          borderRadius: 24,
          padding: 16,
        }}
      >
        {message.hasImages && (
          <div className="flex items-center gap-[3px]">
            <div className="w-[43px] h-[43px] rounded-[8px] bg-white/20 overflow-hidden">
              <Image
                src={chrisChenAvatar}
                alt="Design attachment 1"
                width={43}
                height={43}
                className="w-full h-full object-cover opacity-70"
              />
            </div>
            <div className="w-[43px] h-[43px] rounded-[8px] bg-white/20 overflow-hidden">
              <Image
                src={chrisChenAvatar}
                alt="Design attachment 2"
                width={43}
                height={43}
                className="w-full h-full object-cover opacity-70"
              />
            </div>
          </div>
        )}
        <p className="m-0 text-[14px] font-normal leading-[1.65em] text-white whitespace-pre-wrap overflow-wrap-break-word break-words">
          {message.content}
        </p>
      </div>
    </div>
  );
}
