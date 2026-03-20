import type { ChatMessage } from "./ChatMessage";

interface UserMessageProps {
  message: ChatMessage;
}

// ─── UserMessage ─────────────────────────────────────────────────────────────
// 用户消息（右对齐，蓝色气泡）

export default function UserMessage({ message }: UserMessageProps) {
  const attachments = message.attachments;

  return (
    <div className="flex justify-end">
      <div className="flex flex-col gap-[10px] items-end max-w-[480px]">
        {attachments && attachments.length > 0 && (
          <div className="flex items-center gap-[3px] flex-wrap justify-end">
            {attachments.map((att) => (
              <a
                key={att.id}
                href={att.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-[80px] h-[80px] rounded-[8px] bg-[rgba(255,255,255,0.2)] overflow-hidden shrink-0"
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
          <div
            className="rounded-[20px] px-[16px] py-[10px]"
            style={{ backgroundColor: "#2C69FF" }}
          >
            <p className="m-0 text-[15px] font-normal leading-[1.65em] text-white whitespace-pre-wrap overflow-wrap-break-word break-words">
              {message.content}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
