-- AI Agent Platform - Conversation-Briefing Integration
-- Migration: Enable persistent conversations with briefing card messages

-- =============================================================================
-- PART 1: Enhance Messages Table for Polymorphic Content
-- =============================================================================

-- Add content_type column to support different message types
-- 'text': Regular user/assistant messages
-- 'briefing_card': Briefing embedded as a card in conversation
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS content_type TEXT NOT NULL DEFAULT 'text';

-- Add briefing_id column to link briefing cards to original briefings
-- NULL for regular text messages, populated for briefing_card messages
-- ON DELETE SET NULL preserves message content even if briefing is deleted
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS briefing_id UUID REFERENCES briefings(id) ON DELETE SET NULL;

-- Add constraint to ensure content_type is valid
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'messages_content_type_check'
    ) THEN
        ALTER TABLE messages
        ADD CONSTRAINT messages_content_type_check
        CHECK (content_type IN ('text', 'briefing_card'));
    END IF;
END $$;

-- Create index for fast briefing message lookups
CREATE INDEX IF NOT EXISTS idx_messages_briefing
ON messages(briefing_id)
WHERE briefing_id IS NOT NULL;

-- =============================================================================
-- PART 2: Ensure Unique Conversations per User-Agent Pair
-- =============================================================================

-- Step 1: 清理重复的对话记录（保留最早创建的）
DO $$
BEGIN
    -- 删除重复记录，保留每个(user_id, agent_id)对中started_at最早的记录
    DELETE FROM conversations
    WHERE id IN (
        SELECT c1.id
        FROM conversations c1
        INNER JOIN (
            SELECT user_id, agent_id, MIN(started_at) as earliest_started_at
            FROM conversations
            GROUP BY user_id, agent_id
            HAVING COUNT(*) > 1
        ) c2 ON c1.user_id = c2.user_id
            AND c1.agent_id = c2.agent_id
            AND c1.started_at > c2.earliest_started_at
    );

    RAISE NOTICE 'Cleaned up duplicate conversations';
END $$;

-- Step 2: 添加唯一约束
DO $$
BEGIN
    -- Check if constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'conversations_user_agent_unique'
    ) THEN
        ALTER TABLE conversations
        ADD CONSTRAINT conversations_user_agent_unique
        UNIQUE (user_id, agent_id);

        RAISE NOTICE 'Added unique constraint: conversations_user_agent_unique';
    ELSE
        RAISE NOTICE 'Unique constraint already exists: conversations_user_agent_unique';
    END IF;
END $$;

-- Create index for fast conversation lookups by user-agent pair
-- This supports the get-or-create pattern efficiently
CREATE INDEX IF NOT EXISTS idx_conversations_user_agent
ON conversations(user_id, agent_id);

-- =============================================================================
-- PART 3: Update Existing Data (Idempotent)
-- =============================================================================

-- Ensure all existing messages have content_type='text'
-- This is idempotent - safe to run multiple times
UPDATE messages
SET content_type = 'text'
WHERE content_type IS NULL OR content_type = '';

-- =============================================================================
-- PART 4: Add Helpful Comments
-- =============================================================================

COMMENT ON COLUMN messages.content_type IS 'Message type: text (regular message) or briefing_card (briefing embedded in conversation)';
COMMENT ON COLUMN messages.briefing_id IS 'Reference to original briefing (for briefing_card messages only)';
COMMENT ON CONSTRAINT conversations_user_agent_unique ON conversations IS 'Ensures one conversation per user-agent pair (shared conversation model)';

-- =============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- =============================================================================

-- Verify schema changes
-- SELECT column_name, data_type, column_default, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'messages' AND column_name IN ('content_type', 'briefing_id');

-- Verify unique constraint
-- SELECT constraint_name, constraint_type
-- FROM information_schema.table_constraints
-- WHERE table_name = 'conversations' AND constraint_name = 'conversations_user_agent_unique';

-- Verify indexes
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename IN ('messages', 'conversations')
-- AND indexname LIKE '%briefing%' OR indexname LIKE '%user_agent%';
