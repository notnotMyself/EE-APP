import type { ChatMessage } from "./ChatMessage";

interface UserMessageProps {
  message: ChatMessage;
}

// ─── UserMessage ─────────────────────────────────────────────────────────────
// 用户消息气泡（蓝色背景，右对齐）。纯展示组件，无内部状态。

export default function UserMessage({ message }: UserMessageProps) {
  const attachments = message.attachments;

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
        {attachments && attachments.length > 0 && (
          <div className="flex items-center gap-[3px] flex-wrap">
            {attachments.map((att) => (
              <a
                key={att.id}
                href={att.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-[80px] h-[80px] rounded-[8px] bg-white/20 overflow-hidden shrink-0"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={att.url}
                  alt={att.filename}
                  className="w-full h-full object-cover"
                />
              </a>
            ))}
          </div>
        )}
        {message.content && (
          <p className="m-0 text-[14px] font-normal leading-[1.65em] text-white whitespace-pre-wrap overflow-wrap-break-word break-words">
            {message.content}
          </p>
        )}
      </div>
    </div>
  );
}
