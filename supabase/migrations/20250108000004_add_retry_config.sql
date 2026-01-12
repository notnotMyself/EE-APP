-- 更新 BestBlogs 定时任务，添加重试配置

UPDATE scheduled_jobs
SET briefing_config = '{
    "enabled": true,
    "min_importance_score": 0.5,
    "max_daily_briefings": 1,
    "briefing_type": "summary",
    "default_priority": "P2",
    "max_retries": 3,
    "retry_delay_minutes": 30
}'::jsonb
WHERE job_name = 'daily_bestblogs_briefing';

-- 确认更新
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM scheduled_jobs WHERE job_name = 'daily_bestblogs_briefing') THEN
        RAISE NOTICE 'Updated daily_bestblogs_briefing with retry config: max_retries=3, retry_delay=30min';
    END IF;
END $$;
