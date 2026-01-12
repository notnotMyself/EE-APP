-- 添加可见性控制字段到 briefings 和 agents 表
-- Migration: 20260112000000_add_visibility_to_briefings.sql
-- Date: 2026-01-12

-- 1. 为 agents 表添加 visibility 和 owner_team 字段
ALTER TABLE agents
ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
ADD COLUMN IF NOT EXISTS owner_team TEXT;

-- 添加约束：private agent 必须指定 owner_team
ALTER TABLE agents
ADD CONSTRAINT agents_private_must_have_owner
CHECK (
    (visibility = 'public' AND owner_team IS NULL) OR
    (visibility = 'private' AND owner_team IS NOT NULL)
);

COMMENT ON COLUMN agents.visibility IS 'Agent 可见性：public（所有人可见）或 private（团队私有）';
COMMENT ON COLUMN agents.owner_team IS '私有 Agent 所属团队（仅 visibility=private 时需要）';

-- 2. 为 briefings 表添加 visibility 和 owner_team 字段
ALTER TABLE briefings
ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
ADD COLUMN IF NOT EXISTS owner_team TEXT;

-- 添加约束：private briefing 必须指定 owner_team
ALTER TABLE briefings
ADD CONSTRAINT briefings_private_must_have_owner
CHECK (
    (visibility = 'public' AND owner_team IS NULL) OR
    (visibility = 'private' AND owner_team IS NOT NULL)
);

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
    visibility = a.visibility,
    owner_team = a.owner_team
FROM agents a
WHERE b.agent_id = a.id
AND b.visibility IS NULL;

-- 6. RLS 策略更新：支持基于可见性的访问控制

-- 删除旧的 agents 查询策略（如果存在）
DROP POLICY IF EXISTS "Users can view all agents" ON agents;

-- 创建新的 agents 查询策略（支持可见性控制）
CREATE POLICY "Users can view agents based on visibility"
ON agents
FOR SELECT
TO authenticated
USING (
    visibility = 'public' OR
    (visibility = 'private' AND owner_team IN (
        SELECT team_id FROM user_teams WHERE user_id = auth.uid()
    ))
);

-- 删除旧的 briefings 查询策略（如果存在）
DROP POLICY IF EXISTS "Users can view briefings for their agents" ON briefings;

-- 创建新的 briefings 查询策略（支持可见性控制）
CREATE POLICY "Users can view briefings based on visibility"
ON briefings
FOR SELECT
TO authenticated
USING (
    visibility = 'public' OR
    (visibility = 'private' AND owner_team IN (
        SELECT team_id FROM user_teams WHERE user_id = auth.uid()
    ))
);

-- 7. 创建辅助函数：检查用户是否可以访问 agent
CREATE OR REPLACE FUNCTION can_user_access_agent(
    p_agent_id UUID,
    p_user_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_visibility TEXT;
    v_owner_team TEXT;
    v_user_team TEXT;
BEGIN
    -- 获取 agent 的可见性信息
    SELECT visibility, owner_team
    INTO v_visibility, v_owner_team
    FROM agents
    WHERE id = p_agent_id;

    -- 如果 agent 不存在
    IF v_visibility IS NULL THEN
        RETURN FALSE;
    END IF;

    -- 如果是公开 agent
    IF v_visibility = 'public' THEN
        RETURN TRUE;
    END IF;

    -- 如果是私有 agent，检查用户团队
    IF v_visibility = 'private' THEN
        SELECT team_id INTO v_user_team
        FROM user_teams
        WHERE user_id = p_user_id AND team_id = v_owner_team
        LIMIT 1;

        RETURN v_user_team IS NOT NULL;
    END IF;

    RETURN FALSE;
END;
$$;

COMMENT ON FUNCTION can_user_access_agent IS '检查用户是否有权限访问指定 agent';

-- 8. 验证数据完整性
DO $$
DECLARE
    invalid_agents_count INT;
    invalid_briefings_count INT;
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

    RAISE NOTICE 'Visibility migration completed. Agents: %, Briefings: %',
        (SELECT COUNT(*) FROM agents),
        (SELECT COUNT(*) FROM briefings);
END;
$$;
