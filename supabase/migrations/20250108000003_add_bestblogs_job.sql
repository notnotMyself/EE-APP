-- 添加 BestBlogs 定时任务（与 ai-bot.cn 分开推送）
-- 执行时间：每天早上 9:30（比 ai-bot.cn 晚 30 分钟）

DO $$
DECLARE
    v_agent_id UUID;
BEGIN
    SELECT id INTO v_agent_id FROM agents WHERE role = 'ai_news_crawler' LIMIT 1;

    IF v_agent_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM scheduled_jobs WHERE job_name = 'daily_bestblogs_briefing') THEN
            INSERT INTO scheduled_jobs (
                agent_id, job_name, job_type, schedule_type, cron_expression, timezone,
                task_prompt, briefing_config, is_active
            ) VALUES (
                v_agent_id,
                'daily_bestblogs_briefing',
                'daily_articles',
                'cron',
                '30 9 * * *',  -- 每天早上 9:30
                'Asia/Shanghai',
                '执行每日 BestBlogs 技术文章抓取和简报生成任务：

1. 运行爬虫脚本抓取最新文章
   命令: python3 crawl_articles.py --days 7 --report briefing

2. 检查生成的简报文件 (briefing_articles_YYYY-MM-DD.json)
   - 确认 should_push 字段
   - 检查高评分文章数量 (≥90分)
   - 验证文章列表

3. 根据简报内容判断是否值得推送：
   - 高评分文章 >= 3 篇：P1推送
   - 高评分文章 >= 1 篇：P2推送
   - 无高评分文章：跳过推送

4. 如果值得推送，准备简报数据：
   - 标题：今日精选 N 篇
   - 摘要：按评分排序的文章列表
   - 包含来源、评分、分类

注意：BestBlogs 需要网络可访问 bestblogs.dev（可能需要代理）
如果网络不通，跳过本次执行并记录错误。

请在工作目录 /backend/agents/ai_news_crawler 中执行。',
                '{
                    "enabled": true,
                    "min_importance_score": 0.5,
                    "max_daily_briefings": 1,
                    "briefing_type": "summary",
                    "default_priority": "P2"
                }'::jsonb,
                TRUE
            );
            RAISE NOTICE 'Created scheduled job daily_bestblogs_briefing (agent_id: %)', v_agent_id;
        ELSE
            RAISE NOTICE 'Scheduled job daily_bestblogs_briefing already exists';
        END IF;
    ELSE
        RAISE NOTICE 'ai_news_crawler agent not found';
    END IF;
END $$;
