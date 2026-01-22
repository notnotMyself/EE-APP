-- ========================================
-- 多会话支持迁移
-- 移除 UNIQUE(user_id, agent_id) 约束,支持一个用户和一个Agent创建多个会话
-- ========================================

-- Step 1: 移除唯一约束
ALTER TABLE conversations
DROP CONSTRAINT IF EXISTS conversations_user_agent_unique;

-- Step 2: 添加会话标题字段
ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS title TEXT;

-- Step 3: 更新现有数据（幂等操作）
UPDATE conversations
SET title = 'Conversation ' || TO_CHAR(started_at, 'YYYY-MM-DD HH24:MI')
WHERE title IS NULL OR title = '';

-- Step 4: 优化索引（支持按Agent查询用户会话）
CREATE INDEX IF NOT EXISTS idx_conversations_user_agent_time
ON conversations(user_id, agent_id, last_message_at DESC);

-- Step 5: 添加会话状态枚举约束
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'conversations_status_check'
  ) THEN
    ALTER TABLE conversations
    ADD CONSTRAINT conversations_status_check
    CHECK (status IN ('active', 'archived', 'closed'));
  END IF;
END $$;

-- 注释
COMMENT ON COLUMN conversations.title IS '会话标题（用户自定义或自动生成）';
COMMENT ON INDEX idx_conversations_user_agent_time IS '支持多会话场景：按Agent查询用户会话列表';

-- 验证脚本
-- 查询是否有用户-Agent对有多个会话
-- SELECT user_id, agent_id, COUNT(*) as conversation_count
-- FROM conversations
-- GROUP BY user_id, agent_id
-- HAVING COUNT(*) > 1;
