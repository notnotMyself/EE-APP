-- AI News Crawler 定时任务配置
-- 每天早上9点执行爬虫并生成简报

DO $$
DECLARE
    v_agent_id UUID;
BEGIN
    -- 查找 AI资讯追踪官
    SELECT id INTO v_agent_id
    FROM agents
    WHERE role = 'ai_news_crawler'
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
            'daily_ai_news_briefing',
            'daily_news',
            'cron',
            '0 9 * * *',  -- 每天早上9点
            'Asia/Shanghai',
            '执行每日AI资讯抓取和简报生成任务：

1. 运行爬虫脚本抓取最新资讯
   命令: python3 crawl_aibot.py --days 1 --report all

2. 检查生成的简报文件 (briefing_YYYY-MM-DD.json)
   - 确认 should_push 字段
   - 检查 priority 优先级
   - 验证 key_news 关键新闻

3. 根据简报内容判断是否值得推送：
   - 产业重磅新闻 >= 2 条：P1推送
   - 重要技术/融资新闻 >= 1 条：P2推送
   - 无重要新闻：跳过推送

4. 如果值得推送，准备简报数据：
   - 标题：动词开头，说清核心发现
   - 摘要：3条关键新闻的一句话概括
   - 关键新闻列表：按重要性排序

请在工作目录 /backend/agents/ai_news_crawler 中执行。',
            '{
                "enabled": true,
                "min_importance_score": 0.5,
                "max_daily_briefings": 1,
                "briefing_type": "insight",
                "default_priority": "P2"
            }'::jsonb,
            TRUE
        )
        ON CONFLICT DO NOTHING;

        RAISE NOTICE 'Created scheduled job for ai_news_crawler agent';
    ELSE
        RAISE NOTICE 'ai_news_crawler agent not found, skipping scheduled job creation';
    END IF;
END $$;

-- 添加注释
COMMENT ON TABLE scheduled_jobs IS '定时任务配置表 - 用于Agent自动执行任务';
