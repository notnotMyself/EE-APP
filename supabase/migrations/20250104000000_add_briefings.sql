-- AI Agent Platform - Briefings System
-- Migration: Add briefings and scheduled_jobs tables

-- =============================================================================
-- BRIEFINGS TABLE (AI员工简报表)
-- =============================================================================
-- 用于存储AI员工主动推送的简报信息，遵循"信息流铁律"：
-- 1. 一天 ≤ 3 条
-- 2. 宁可不发，也不刷存在感
-- 3. 每一条都必须能接上对话

CREATE TABLE IF NOT EXISTS briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联关系
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 简报类型
    -- alert: 异常警报（如Review积压严重）
    -- insight: 趋势洞察（如返工率连续上升）
    -- summary: 周期摘要（如每周效能总结）
    -- action: 待办建议（如建议安排培训）
    briefing_type VARCHAR(20) NOT NULL DEFAULT 'insight',

    -- 优先级
    -- P0: 紧急（立即需要关注）
    -- P1: 重要（今日需要处理）
    -- P2: 普通（有空再看）
    priority VARCHAR(5) NOT NULL DEFAULT 'P2',

    -- 简报内容
    title VARCHAR(100) NOT NULL,          -- 一句话标题 (≤30字为佳)
    summary TEXT NOT NULL,                -- 2-3句摘要 (问题+影响+行动)
    impact TEXT,                          -- 影响说明 (对业务的具体影响)

    -- 可操作按钮配置 (JSON数组)
    -- 格式: [{"label": "查看详情", "action": "view_report", "data": {...}}, ...]
    -- action 类型:
    --   - view_report: 查看完整报告
    --   - start_conversation: 开始对话（可带 prompt 预填问题）
    --   - dismiss: 忽略/已处理
    --   - custom: 自定义操作
    actions JSONB DEFAULT '[]'::jsonb,

    -- 关联的完整报告 (artifact_id)
    report_artifact_id UUID REFERENCES artifacts(id) ON DELETE SET NULL,

    -- 关联的对话 (点击简报后创建)
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,

    -- 原始数据/上下文 (用于后续对话)
    -- 包含: analysis_result, task_prompt, data_snapshot 等
    context_data JSONB DEFAULT '{}'::jsonb,

    -- 状态管理
    -- new: 新简报（未读）
    -- read: 已读
    -- actioned: 已处理（用户执行了某个操作）
    -- dismissed: 已忽略
    status VARCHAR(20) NOT NULL DEFAULT 'new',

    -- 重要性分数 (0.0-1.0)，用于过滤低价值简报
    importance_score DECIMAL(3,2) DEFAULT 0.5,

    -- 时间戳
    read_at TIMESTAMP WITH TIME ZONE,
    actioned_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,  -- 过期时间 (可选，过期后自动归档)

    -- 元数据 (任务ID、触发条件、执行批次等)
    metadata JSONB DEFAULT '{}'::jsonb,

    -- 约束检查
    CONSTRAINT briefing_type_check CHECK (briefing_type IN ('alert', 'insight', 'summary', 'action')),
    CONSTRAINT priority_check CHECK (priority IN ('P0', 'P1', 'P2')),
    CONSTRAINT status_check CHECK (status IN ('new', 'read', 'actioned', 'dismissed'))
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_briefings_user_status ON briefings(user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_briefings_user_new ON briefings(user_id, created_at DESC) WHERE status = 'new';
CREATE INDEX IF NOT EXISTS idx_briefings_agent ON briefings(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_briefings_type ON briefings(briefing_type);
CREATE INDEX IF NOT EXISTS idx_briefings_priority ON briefings(priority);
CREATE INDEX IF NOT EXISTS idx_briefings_created ON briefings(created_at DESC);

-- RLS 策略
ALTER TABLE briefings ENABLE ROW LEVEL SECURITY;

-- 用户只能读取自己的简报
CREATE POLICY "Users can read own briefings" ON briefings
    FOR SELECT USING (auth.uid() = user_id);

-- 用户可以更新自己的简报状态
CREATE POLICY "Users can update own briefings" ON briefings
    FOR UPDATE USING (auth.uid() = user_id);

-- 后端服务可以插入简报 (通过 service_role key)
CREATE POLICY "Service can insert briefings" ON briefings
    FOR INSERT WITH CHECK (true);

-- 用户可以删除（忽略）自己的简报
CREATE POLICY "Users can delete own briefings" ON briefings
    FOR DELETE USING (auth.uid() = user_id);


-- =============================================================================
-- SCHEDULED_JOBS TABLE (定时任务配置表)
-- =============================================================================
-- 用于配置AI员工的定时分析任务

CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联的Agent
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

    -- 任务标识
    job_name VARCHAR(100) NOT NULL,       -- 任务名称（如 "daily_efficiency_analysis"）
    job_type VARCHAR(50) NOT NULL,        -- 任务类型（如 "daily_analysis", "weekly_report"）

    -- 调度配置
    schedule_type VARCHAR(20) NOT NULL DEFAULT 'cron',  -- cron 或 interval
    cron_expression VARCHAR(100),         -- cron 表达式，如 "0 9 * * *" (每天早9点)
    interval_seconds INTEGER,             -- 间隔秒数 (用于 interval 类型)
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',  -- 时区

    -- 任务提示词 (给AI的指令)
    task_prompt TEXT NOT NULL,

    -- 简报生成配置
    briefing_config JSONB DEFAULT '{
        "enabled": true,
        "min_importance_score": 0.6,
        "max_daily_briefings": 3
    }'::jsonb,

    -- 目标用户配置
    -- null: 推送给所有订阅该Agent的用户
    -- UUID[]: 只推送给指定用户
    target_user_ids UUID[],

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,

    -- 执行记录
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_result JSONB,                    -- 上次执行结果
    run_count INTEGER DEFAULT 0,          -- 总执行次数
    success_count INTEGER DEFAULT 0,      -- 成功次数
    failure_count INTEGER DEFAULT 0,      -- 失败次数

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 约束检查
    CONSTRAINT schedule_type_check CHECK (schedule_type IN ('cron', 'interval')),
    CONSTRAINT cron_required CHECK (
        (schedule_type = 'cron' AND cron_expression IS NOT NULL) OR
        (schedule_type = 'interval' AND interval_seconds IS NOT NULL)
    )
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_next_run ON scheduled_jobs(next_run_at)
    WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_agent ON scheduled_jobs(agent_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_active ON scheduled_jobs(is_active);

-- 更新时间触发器
CREATE TRIGGER update_scheduled_jobs_updated_at
    BEFORE UPDATE ON scheduled_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS 策略 (定时任务通常只由后端管理，但允许超级用户查看)
ALTER TABLE scheduled_jobs ENABLE ROW LEVEL SECURITY;

-- 后端服务可以完全管理定时任务
CREATE POLICY "Service can manage scheduled_jobs" ON scheduled_jobs
    FOR ALL USING (true) WITH CHECK (true);


-- =============================================================================
-- 初始数据：为研发效能分析官配置定时任务
-- =============================================================================

-- 注意：agent_id 需要根据实际数据库中的 agents 表数据来填充
-- 这里使用占位符，实际部署时需要替换

-- 获取研发效能分析官的 agent_id 并插入定时任务
DO $$
DECLARE
    v_agent_id UUID;
BEGIN
    -- 查找研发效能分析官
    SELECT id INTO v_agent_id
    FROM agents
    WHERE role = 'dev_efficiency_analyst'
    LIMIT 1;

    -- 如果存在，创建定时任务
    IF v_agent_id IS NOT NULL THEN
        INSERT INTO scheduled_jobs (
            agent_id,
            job_name,
            job_type,
            schedule_type,
            cron_expression,
            timezone,
            task_prompt,
            briefing_config,
            is_active
        ) VALUES (
            v_agent_id,
            'daily_efficiency_analysis',
            'daily_analysis',
            'cron',
            '0 9 * * *',  -- 每天早上9点
            'Asia/Shanghai',
            '请执行每日研发效能分析：
1. 从Gerrit数据库获取昨日代码审查数据
2. 分析关键指标：Review耗时、返工率、代码变更量
3. 检测异常值（对比阈值）
4. 如果发现异常，准备推送简报

重点关注：
- Review中位耗时是否超过24小时
- P95耗时是否超过72小时
- 返工率是否超过15%
- 是否有模块或人员效率明显异常',
            '{
                "enabled": true,
                "min_importance_score": 0.6,
                "max_daily_briefings": 3
            }'::jsonb,
            TRUE
        )
        ON CONFLICT DO NOTHING;

        RAISE NOTICE 'Created scheduled job for dev_efficiency_analyst';
    ELSE
        RAISE NOTICE 'dev_efficiency_analyst agent not found, skipping scheduled job creation';
    END IF;
END $$;


-- =============================================================================
-- 注释
-- =============================================================================

COMMENT ON TABLE briefings IS 'AI员工主动推送的简报表，遵循信息流铁律';
COMMENT ON COLUMN briefings.briefing_type IS '简报类型: alert(警报), insight(洞察), summary(摘要), action(待办)';
COMMENT ON COLUMN briefings.priority IS '优先级: P0(紧急), P1(重要), P2(普通)';
COMMENT ON COLUMN briefings.actions IS '可操作按钮配置JSON数组';
COMMENT ON COLUMN briefings.context_data IS '简报上下文数据，用于后续对话';
COMMENT ON COLUMN briefings.importance_score IS '重要性分数(0-1)，用于过滤低价值简报';

COMMENT ON TABLE scheduled_jobs IS '定时任务配置表，用于AI员工定时分析';
COMMENT ON COLUMN scheduled_jobs.cron_expression IS 'Cron表达式，如 "0 9 * * *" 表示每天早9点';
COMMENT ON COLUMN scheduled_jobs.briefing_config IS '简报生成配置，包含最小重要性分数和每日上限';
