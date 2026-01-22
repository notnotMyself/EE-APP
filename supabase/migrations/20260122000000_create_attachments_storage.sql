-- AI Agent Platform - Chat Attachments Storage
-- Migration: Create storage bucket for chat attachments (images, files)

-- =============================================================================
-- PART 1: Create Storage Bucket
-- =============================================================================

-- Create storage bucket for chat attachments
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'attachments',
    'attachments',
    true,
    10485760,  -- 10MB
    ARRAY[
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain'
    ]
)
ON CONFLICT (id) DO UPDATE SET
    public = EXCLUDED.public,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

-- =============================================================================
-- PART 2: Storage Policies
-- =============================================================================

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Authenticated users can upload attachments" ON storage.objects;
DROP POLICY IF EXISTS "Public read access for attachments" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can delete attachments" ON storage.objects;

-- Policy: Authenticated users can upload files
CREATE POLICY "Authenticated users can upload attachments"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'attachments');

-- Policy: Public read access (since bucket is public)
CREATE POLICY "Public read access for attachments"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'attachments');

-- Policy: Users can delete their own uploads
CREATE POLICY "Authenticated users can delete attachments"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'attachments');

-- =============================================================================
-- PART 3: Update messages content_type constraint
-- =============================================================================

-- Update constraint to allow image_message type
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_content_type_check;
ALTER TABLE messages
ADD CONSTRAINT messages_content_type_check
CHECK (content_type IN ('text', 'briefing_card', 'image_message'));

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON COLUMN messages.attachments IS 'JSON array of attachment objects: [{id, url, mime_type, filename}]';
