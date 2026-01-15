-- Add cover image fields to briefings table
ALTER TABLE briefings
ADD COLUMN cover_image_url TEXT,
ADD COLUMN cover_image_metadata JSONB DEFAULT '{}'::jsonb;

COMMENT ON COLUMN briefings.cover_image_url IS 'Supabase Storage URL for cover image';
COMMENT ON COLUMN briefings.cover_image_metadata IS 'Metadata about cover image generation (model, prompt, timestamp, etc.)';

-- Create briefing-covers bucket if not exists
INSERT INTO storage.buckets (id, name, public)
VALUES ('briefing-covers', 'briefing-covers', true)
ON CONFLICT (id) DO NOTHING;

-- RLS policy for public read access
CREATE POLICY "Public Access" ON storage.objects
FOR SELECT USING (bucket_id = 'briefing-covers');

-- RLS policy for authenticated users to upload
CREATE POLICY "Authenticated users can upload briefing covers" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'briefing-covers'
    AND auth.role() = 'authenticated'
);
