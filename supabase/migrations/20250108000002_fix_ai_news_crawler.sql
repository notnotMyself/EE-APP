-- 修复：添加 AI资讯追踪官 Agent 和定时任务
-- 上一个迁移因 ON CONFLICT 语法问题失败，这个迁移重新执行

-- 1. 添加 Agent（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM agents WHERE role = 'ai_news_crawler') THEN
        INSERT INTO agents (
          name, role, description, avatar_url, is_builtin, is_active,
          capabilities, trigger_conditions, data_sources, metadata
        ) VALUES (
          'AI资讯追踪官',
          'ai_news_crawler',
          '每日追踪AI行业重要资讯，包括产业动态、技术发布、融资消息等。帮助你第一时间掌握AI领域的关键信息。

我会关注：
• 产业重磅：融资、上市、收购等重大事件
• 前沿技术：新模型、新框架、开源项目
• 工具发布：新产品、新功能上线
• 安全合规：行业监管动态

当有重要资讯时，我会：
✓ 每天早上9点推送简报
✓ 按重要性筛选资讯
✓ 提供快速摘要
✓ 附带原文链接',
          NULL, true, true,
          '{"can_generate_reports": true, "can_crawl_news": true, "can_categorize_news": true, "can_summarize": true}'::jsonb,
          '{"major_news_threshold": 2, "daily_push_time": "09:00"}'::jsonb,
          '{"ai_bot_cn": {"enabled": true, "url": "https://ai-bot.cn/daily-ai-news/"}}'::jsonb,
          '{"version": "1.0", "category": "information"}'::jsonb
        );
        RAISE NOTICE 'Created ai_news_crawler agent';
    ELSE
        RAISE NOTICE 'ai_news_crawler agent already exists';
    END IF;
END $$;

-- 2. 添加定时任务（如果不存在）
DO $$
DECLARE
    v_agent_id UUID;
BEGIN
    SELECT id INTO v_agent_id FROM agents WHERE role = 'ai_news_crawler' LIMIT 1;

    IF v_agent_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM scheduled_jobs WHERE job_name = 'daily_ai_news_briefing') THEN
            INSERT INTO scheduled_jobs (
                agent_id, job_name, job_type, schedule_type, cron_expression, timezone,
                task_prompt, briefing_config, is_active
            ) VALUES (
                v_agent_id,
                'daily_ai_news_briefing',
                'daily_news',
                'cron',
                '0 9 * * *',
                'Asia/Shanghai',
                '执行每日AI资讯抓取和简报生成任务：
1. 运行 python3 crawl_aibot.py --days 1 --report all
2. 检查 briefing_YYYY-MM-DD.json 的 should_push 字段
3. 如果值得推送，准备简报数据',
                '{"enabled": true, "min_importance_score": 0.5, "max_daily_briefings": 1, "briefing_type": "insight", "default_priority": "P2"}'::jsonb,
                TRUE
            );
            RAISE NOTICE 'Created scheduled job for ai_news_crawler (agent_id: %)', v_agent_id;
        ELSE
            RAISE NOTICE 'Scheduled job daily_ai_news_briefing already exists';
        END IF;
    ELSE
        RAISE NOTICE 'ai_news_crawler agent not found, cannot create scheduled job';
    END IF;
END $$;
