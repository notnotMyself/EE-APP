import type { Attachment } from "@/lib/upload";

interface PendingImagesBarProps {
  attachments: Attachment[];
  uploading: boolean;
  onRemove: (id: string) => void;
}

export default function PendingImagesBar({ attachments, uploading, onRemove }: PendingImagesBarProps) {
  if (attachments.length === 0 && !uploading) return null;

  return (
    <div className="flex items-center gap-[6px] flex-wrap px-[4px] pb-[4px]">
      {attachments.map((att) => (
        <div key={att.id} className="relative group">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={att.url}
            alt={att.filename}
            className="w-[56px] h-[56px] rounded-[8px] object-cover border border-[rgba(0,0,0,0.08)]"
          />
          <button
            type="button"
            onClick={() => onRemove(att.id)}
            className="absolute -top-[6px] -right-[6px] w-[18px] h-[18px] rounded-full bg-[rgba(0,0,0,0.6)] border-none cursor-pointer flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
            title="移除"
          >
            <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
              <path d="M1 1L7 7M7 1L1 7" stroke="white" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      ))}
      {uploading && (
        <div className="w-[56px] h-[56px] rounded-[8px] bg-[rgba(0,0,0,0.04)] flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-[rgba(0,0,0,0.15)] border-t-[rgba(0,0,0,0.5)] rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}
