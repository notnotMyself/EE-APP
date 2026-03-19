import { supabase } from "./supabase";

export interface Attachment {
  id: string;
  url: string;
  mime_type: string;
  filename: string;
}

/**
 * Upload an image file to Supabase Storage "attachments" bucket.
 * Returns attachment metadata matching the backend's expected format.
 */
export async function uploadImage(file: File): Promise<Attachment> {
  const ext = file.name.split(".").pop() || "png";
  const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const path = `uploads/${id}.${ext}`;

  const { error } = await supabase.storage.from("attachments").upload(path, file, {
    contentType: file.type,
  });
  if (error) throw new Error(`上传失败: ${error.message}`);

  const { data } = supabase.storage.from("attachments").getPublicUrl(path);

  return {
    id,
    url: data.publicUrl,
    mime_type: file.type,
    filename: file.name,
  };
}

/**
 * Extract image files from a ClipboardEvent (paste) or DataTransfer (drop).
 */
export function extractImageFiles(dataTransfer: DataTransfer): File[] {
  const files: File[] = [];
  for (let i = 0; i < dataTransfer.files.length; i++) {
    const file = dataTransfer.files[i];
    if (file.type.startsWith("image/")) {
      files.push(file);
    }
  }
  return files;
}
