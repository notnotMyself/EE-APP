-- Migration: Add Task Templates System
-- Description: Creates task_templates table and extends scheduled_jobs for template-based task framework
-- Date: 2026-01-07

-- ============================================
-- 1. Create task_templates table
-- ============================================

CREATE TABLE IF NOT EXISTS task_templates (
    id TEXT PRIMARY KEY,  -- 使用可读的 ID，如 'tmpl_daily_monitoring'
    name TEXT NOT NULL,  -- 模板名称，如 "每日研发效能监控"
    task_type TEXT NOT NULL,  -- 任务类型：monitoring, trend_analysis, realtime_insight, custom_analysis
    applicable_agent_types TEXT[] NOT NULL,  -- 适用的 Agent 类型，如 ARRAY['dev_efficiency_analyst']
    prompt_template TEXT NOT NULL,  -- Prompt 模板（支持 Jinja2 变量插值）
    default_config JSONB NOT NULL DEFAULT '{}',  -- 默认配置（thresholds、分析窗口等）
    schedule_config JSONB NOT NULL DEFAULT '{}',  -- 调度配置（Cron 表达式或 Interval）
    description TEXT,  -- 模板描述
    is_active BOOLEAN NOT NULL DEFAULT true,  -- 是否启用
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),  -- 创建者

    -- 约束：task_type 必须是有效值
    CONSTRAINT valid_task_type CHECK (
        task_type IN ('monitoring', 'trend_analysis', 'realtime_insight', 'custom_analysis')
    ),

    -- 约束：schedule_config 必须包含 type 字段
    CONSTRAINT valid_schedule_config CHECK (
        schedule_config ? 'type'
    )
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_task_templates_task_type ON task_templates(task_type);
CREATE INDEX IF NOT EXISTS idx_task_templates_active ON task_templates(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_task_templates_created_at ON task_templates(created_at DESC);

-- 注释
COMMENT ON TABLE task_templates IS '任务模板表：定义可复用的任务配置';
COMMENT ON COLUMN task_templates.id IS '模板ID（可读字符串）';
COMMENT ON COLUMN task_templates.name IS '模板名称';
COMMENT ON COLUMN task_templates.task_type IS '任务类型：monitoring|trend_analysis|realtime_insight|custom_analysis';
COMMENT ON COLUMN task_templates.applicable_agent_types IS '适用的 Agent 角色列表';
COMMENT ON COLUMN task_templates.prompt_template IS 'Prompt 模板（支持 {{variable}} 插值）';
COMMENT ON COLUMN task_templates.default_config IS '默认配置（thresholds、days、min_importance_score 等）';
COMMENT ON COLUMN task_templates.schedule_config IS '调度配置（type: cron|interval, expression/minutes）';

-- ============================================
-- 2. Extend scheduled_jobs table
-- ============================================

-- 添加新字段
ALTER TABLE scheduled_jobs
    ADD COLUMN IF NOT EXISTS template_id TEXT REFERENCES task_templates(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS task_type TEXT,
    ADD COLUMN IF NOT EXISTS instance_config JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS last_run_context JSONB DEFAULT '{}';

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_template_id ON scheduled_jobs(template_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_task_type ON scheduled_jobs(task_type);
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_last_run_at ON scheduled_jobs(last_run_at DESC);

-- 注释
COMMENT ON COLUMN scheduled_jobs.template_id IS '关联的任务模板ID（如果基于模板创建）';
COMMENT ON COLUMN scheduled_jobs.task_type IS '任务类型（从模板继承）';
COMMENT ON COLUMN scheduled_jobs.instance_config IS '实例级配置（覆盖模板默认值）';
COMMENT ON COLUMN scheduled_jobs.last_run_context IS '上次执行上下文（用于去重、趋势对比）';

-- ============================================
-- 3. Add content_hash to briefings table (for deduplication)
-- ============================================

ALTER TABLE briefings
    ADD COLUMN IF NOT EXISTS content_hash TEXT;

-- 添加索引（用于快速去重查询）
CREATE INDEX IF NOT EXISTS idx_briefings_content_hash ON briefings(content_hash);
CREATE INDEX IF NOT EXISTS idx_briefings_created_at_hash ON briefings(created_at DESC, content_hash);

COMMENT ON COLUMN briefings.content_hash IS '内容哈希（用于去重检测）';

-- ============================================
-- 4. Create function to update updated_at timestamp
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 添加触发器
DROP TRIGGER IF EXISTS update_task_templates_updated_at ON task_templates;
CREATE TRIGGER update_task_templates_updated_at
    BEFORE UPDATE ON task_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 5. Migrate existing scheduled_jobs to template-based system (optional)
-- ============================================

-- 注意：这是可选步骤，用于将现有的 scheduled_jobs 迁移到模板系统
-- 如果需要保留现有任务的独立性，可以跳过此步骤

-- 为现有的 scheduled_jobs 创建模板（示例）
-- INSERT INTO task_templates (id, name, task_type, applicable_agent_types, prompt_template, default_config, schedule_config)
-- SELECT
--     'tmpl_legacy_' || id,
--     job_name,
--     'monitoring',
--     ARRAY[a.role],
--     task_prompt,
--     briefing_config,
--     jsonb_build_object(
--         'type', 'cron',
--         'expression', cron_expression,
--         'timezone', 'Asia/Shanghai'
--     )
-- FROM scheduled_jobs sj
-- JOIN agents a ON sj.agent_id = a.id
-- WHERE template_id IS NULL;

-- 关联现有任务到新创建的模板
-- UPDATE scheduled_jobs sj
-- SET
--     template_id = 'tmpl_legacy_' || id,
--     task_type = 'monitoring',
--     instance_config = COALESCE(briefing_config, '{}'::jsonb)
-- WHERE template_id IS NULL;

-- ============================================
-- 6. Grant permissions (adjust based on your RLS policy)
-- ============================================

-- 允许认证用户查看任务模板
GRANT SELECT ON task_templates TO authenticated;
GRANT SELECT ON task_templates TO anon;

-- 允许服务角色完全访问
GRANT ALL ON task_templates TO service_role;

-- ============================================
-- Migration completed
-- ============================================

-- 验证查询（可用于检查迁移结果）
-- SELECT
--     'task_templates' AS table_name,
--     COUNT(*) AS row_count
-- FROM task_templates
-- UNION ALL
-- SELECT
--     'scheduled_jobs_with_template' AS table_name,
--     COUNT(*) AS row_count
-- FROM scheduled_jobs
-- WHERE template_id IS NOT NULL;
