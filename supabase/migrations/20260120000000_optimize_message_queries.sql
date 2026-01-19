-- Migration: optimize_message_queries
-- Description: Add indexes to optimize message queries for better TTFT (Time to First Token)
-- This migration creates composite indexes for faster recent message queries

-- 1. Composite index for message queries (conversation_id + created_at)
-- Optimizes: get_recent_messages() which orders by created_at DESC
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
ON messages (conversation_id, created_at DESC);

-- 2. Index for conversation user lookup
-- Optimizes: RLS checks and list_by_user() queries
CREATE INDEX IF NOT EXISTS idx_conversations_user_id
ON conversations (user_id);

-- 3. Index for conversation agent lookup
-- Optimizes: get_conversation_by_agent() queries
CREATE INDEX IF NOT EXISTS idx_conversations_agent_id
ON conversations (agent_id);

-- 4. Composite index for conversations (user + last_message_at for sorting)
-- Optimizes: list_user_conversations() which sorts by last_message_at
CREATE INDEX IF NOT EXISTS idx_conversations_user_last_message
ON conversations (user_id, last_message_at DESC);

-- 5. Index for briefing queries by agent
-- Optimizes: briefing listing by agent
CREATE INDEX IF NOT EXISTS idx_briefings_agent_created
ON briefings (agent_id, created_at DESC);

-- 6. Index for briefing queries by user
-- Optimizes: user's briefing feed
CREATE INDEX IF NOT EXISTS idx_briefings_user_created
ON briefings (user_id, created_at DESC);

-- Add helpful comments
COMMENT ON INDEX idx_messages_conversation_created IS 'Speeds up recent message queries for conversation context loading';
COMMENT ON INDEX idx_conversations_user_id IS 'Speeds up user conversation listing and RLS checks';
COMMENT ON INDEX idx_conversations_agent_id IS 'Speeds up agent conversation lookup';
COMMENT ON INDEX idx_conversations_user_last_message IS 'Speeds up user conversation listing with sorting';
COMMENT ON INDEX idx_briefings_agent_created IS 'Speeds up agent briefing queries';
COMMENT ON INDEX idx_briefings_user_created IS 'Speeds up user briefing feed queries';
