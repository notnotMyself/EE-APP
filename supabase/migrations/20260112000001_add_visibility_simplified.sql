-- 简化版：仅添加可见性字段，不包含 user_teams 依赖的 RLS 策略
-- Migration: 20260112000001_add_visibility_simplified.sql
-- Date: 2026-01-14

-- 1. 为 agents 表添加 visibility 和 owner_team 字段
ALTER TABLE agents
ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
ADD COLUMN IF NOT EXISTS owner_team TEXT;

-- 添加约束：private agent 必须指定 owner_team
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'agents_private_must_have_owner'
    ) THEN
        ALTER TABLE agents
        ADD CONSTRAINT agents_private_must_have_owner
        CHECK (
            (visibility = 'public' AND owner_team IS NULL) OR
            (visibility = 'private' AND owner_team IS NOT NULL)
        );
    END IF;
END $$;

COMMENT ON COLUMN agents.visibility IS 'Agent 可见性：public（所有人可见）或 private（团队私有）';
COMMENT ON COLUMN agents.owner_team IS '私有 Agent 所属团队（仅 visibility=private 时需要）';

-- 2. 为 briefings 表添加 visibility 和 owner_team 字段
ALTER TABLE briefings
ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
ADD COLUMN IF NOT EXISTS owner_team TEXT;

-- 添加约束：private briefing 必须指定 owner_team
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'briefings_private_must_have_owner'
    ) THEN
        ALTER TABLE briefings
        ADD CONSTRAINT briefings_private_must_have_owner
        CHECK (
            (visibility = 'public' AND owner_team IS NULL) OR
            (visibility = 'private' AND owner_team IS NOT NULL)
        );
    END IF;
END $$;

COMMENT ON COLUMN briefings.visibility IS 'Briefing 可见性：public（所有人可见）或 private（团队私有）';
COMMENT ON COLUMN briefings.owner_team IS '私有 Briefing 所属团队（仅 visibility=private 时需要）';

-- 3. 创建索引以优化可见性查询
CREATE INDEX IF NOT EXISTS idx_agents_visibility ON agents(visibility);
CREATE INDEX IF NOT EXISTS idx_agents_owner_team ON agents(owner_team) WHERE owner_team IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_briefings_visibility ON briefings(visibility);
CREATE INDEX IF NOT EXISTS idx_briefings_owner_team ON briefings(owner_team) WHERE owner_team IS NOT NULL;

-- 4. 更新现有 agents 为 public（默认值）
UPDATE agents
SET visibility = 'public'
WHERE visibility IS NULL;

-- 5. 更新现有 briefings 继承其 agent 的可见性
UPDATE briefings b
SET
    visibility = COALESCE(a.visibility, 'public'),
    owner_team = a.owner_team
FROM agents a
WHERE b.agent_id = a.id
AND b.visibility IS NULL;

-- 6. RLS 策略更新：简化版（暂不支持团队功能）

-- 删除旧的 agents 查询策略（如果存在）
DROP POLICY IF EXISTS "Users can view all agents" ON agents;
DROP POLICY IF EXISTS "Users can view agents based on visibility" ON agents;

-- 创建简化的 agents 查询策略（仅支持 public agents）
CREATE POLICY "Users can view public agents"
ON agents
FOR SELECT
TO authenticated
USING (visibility = 'public');

-- 删除旧的 briefings 查询策略（如果存在）
DROP POLICY IF EXISTS "Users can view briefings for their agents" ON briefings;
DROP POLICY IF EXISTS "Users can view briefings based on visibility" ON briefings;

-- 创建简化的 briefings 查询策略（仅支持 public briefings）
CREATE POLICY "Users can view public briefings"
ON briefings
FOR SELECT
TO authenticated
USING (visibility = 'public');

-- 7. 验证数据完整性
DO $$
DECLARE
    invalid_agents_count INT;
    invalid_briefings_count INT;
    total_agents INT;
    total_briefings INT;
BEGIN
    -- 检查 agents 表中的无效数据
    SELECT COUNT(*)
    INTO invalid_agents_count
    FROM agents
    WHERE
        (visibility = 'public' AND owner_team IS NOT NULL) OR
        (visibility = 'private' AND owner_team IS NULL);

    IF invalid_agents_count > 0 THEN
        RAISE WARNING 'Found % agents with invalid visibility/owner_team configuration', invalid_agents_count;
    END IF;

    -- 检查 briefings 表中的无效数据
    SELECT COUNT(*)
    INTO invalid_briefings_count
    FROM briefings
    WHERE
        (visibility = 'public' AND owner_team IS NOT NULL) OR
        (visibility = 'private' AND owner_team IS NULL);

    IF invalid_briefings_count > 0 THEN
        RAISE WARNING 'Found % briefings with invalid visibility/owner_team configuration', invalid_briefings_count;
    END IF;

    SELECT COUNT(*) INTO total_agents FROM agents;
    SELECT COUNT(*) INTO total_briefings FROM briefings;

    RAISE NOTICE 'Visibility migration completed (simplified version without user_teams).';
    RAISE NOTICE 'Total agents: %, Total briefings: %', total_agents, total_briefings;
    RAISE NOTICE 'Note: Team-based access control will be enabled when user_teams table is created.';
END;
$$;
