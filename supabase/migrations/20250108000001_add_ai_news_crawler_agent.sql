-- 添加 AI资讯追踪官 到 agents 表（检查是否已存在）
DO $$
BEGIN
    -- 检查是否已存在
    IF NOT EXISTS (SELECT 1 FROM agents WHERE role = 'ai_news_crawler') THEN
        INSERT INTO agents (
          name,
          role,
          description,
          avatar_url,
          is_builtin,
          is_active,
          capabilities,
          trigger_conditions,
          data_sources,
          metadata
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
          NULL,
          true,
          true,
          '{
            "can_generate_reports": true,
            "can_crawl_news": true,
            "can_categorize_news": true,
            "can_summarize": true
          }'::jsonb,
          '{
            "major_news_threshold": 2,
            "daily_push_time": "09:00"
          }'::jsonb,
          '{
            "ai_bot_cn": {"enabled": true, "url": "https://ai-bot.cn/daily-ai-news/"}
          }'::jsonb,
          '{
            "version": "1.0",
            "category": "information"
          }'::jsonb
        );
        RAISE NOTICE 'Created ai_news_crawler agent';
    ELSE
        RAISE NOTICE 'ai_news_crawler agent already exists';
    END IF;
END $$;

-- 创建定时任务（需要先有 agent 记录）
DO $$
DECLARE
    v_agent_id UUID;
BEGIN
    SELECT id INTO v_agent_id
    FROM agents
    WHERE role = 'ai_news_crawler'
    LIMIT 1;

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
            '0 9 * * *',
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

        RAISE NOTICE 'Created scheduled job for ai_news_crawler agent (id: %)', v_agent_id;
    ELSE
        RAISE NOTICE 'ai_news_crawler agent not found';
    END IF;
END $$;
