-- Seed data for AI Agent Platform
-- Insert built-in AI agents

-- 1. 研发效能分析官
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
  '研发效能分析官',
  'dev_efficiency_analyst',
  '持续监控团队的研发效能数据，包括代码Review耗时、返工率、需求交付周期等关键指标。当发现异常趋势时主动提醒，帮助团队及时调整。

我会关注：
• 代码Review中位耗时和P95
• PR返工率和合并成功率
• 需求从开始到上线的周期
• 团队成员负载分布

当指标出现异常时，我会：
✓ 主动提醒你关注
✓ 分析可能的原因
✓ 给出优化建议
✓ 生成可视化报告',
  NULL,
  true,
  true,
  '{
    "can_generate_reports": true,
    "can_create_charts": true,
    "can_analyze_trends": true,
    "can_compare_periods": true
  }'::jsonb,
  '{
    "review_time_threshold": 24,
    "rework_rate_threshold": 0.15,
    "cycle_time_threshold": 168
  }'::jsonb,
  '{
    "gerrit": {"enabled": false},
    "jira": {"enabled": false},
    "github": {"enabled": false}
  }'::jsonb,
  '{
    "version": "1.0",
    "category": "engineering"
  }'::jsonb
);

-- 2. NPS洞察官
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
  'NPS洞察官',
  'nps_analyst',
  '监控产品的NPS分数变化，分析用户反馈趋势。当NPS出现下降或收到负面反馈集中时，及时提醒并提供改进建议。

我会关注：
• NPS整体分数和趋势
• 推荐者、中立者、贬损者比例
• 负面反馈的主题聚类
• 不同用户群体的满意度差异

当发现问题时，我会：
✓ 分析NPS下降的可能原因
✓ 识别用户反馈中的关键问题
✓ 建议优先改进方向
✓ 生成用户洞察报告',
  NULL,
  true,
  true,
  '{
    "can_generate_reports": true,
    "can_analyze_sentiment": true,
    "can_cluster_feedback": true,
    "can_segment_users": true
  }'::jsonb,
  '{
    "nps_threshold": 40,
    "detractor_threshold": 0.2,
    "decline_rate_threshold": 0.1
  }'::jsonb,
  '{
    "nps_system": {"enabled": false},
    "user_feedback": {"enabled": false}
  }'::jsonb,
  '{
    "version": "1.0",
    "category": "product"
  }'::jsonb
);

-- 3. 竞品情报官
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
  '竞品情报官',
  'competitor_analyst',
  '持续追踪主要竞品动态，包括新功能发布、产品更新、市场策略变化等。帮助你及时了解行业趋势，避免被竞品超越。

我会关注：
• 竞品的产品更新和新功能
• 竞品的市场活动和营销策略
• 行业趋势和用户反馈对比
• 竞品的技术架构变化

当发现重要变化时，我会：
✓ 第一时间通知你
✓ 分析竞品动作的意图
✓ 评估对我们的影响
✓ 给出应对建议',
  NULL,
  true,
  true,
  '{
    "can_generate_reports": true,
    "can_track_changes": true,
    "can_compare_features": true,
    "can_analyze_strategy": true
  }'::jsonb,
  '{
    "update_frequency": "daily",
    "importance_threshold": "medium"
  }'::jsonb,
  '{
    "web_monitoring": {"enabled": false},
    "app_store": {"enabled": false},
    "news": {"enabled": false}
  }'::jsonb,
  '{
    "version": "1.0",
    "category": "market"
  }'::jsonb
);

-- 4. 舆情哨兵
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
  '舆情哨兵',
  'sentiment_monitor',
  '监控社交媒体、论坛、评论区等渠道的用户讨论，识别负面舆情和热点话题。帮助你及时发现并应对潜在的PR危机。

我会关注：
• 社交媒体上关于产品的讨论
• 应用商店的评论变化
• 技术社区的反馈
• 舆情情感走势

当发现异常时，我会：
✓ 识别负面舆情集中爆发
✓ 分析负面情绪的主要来源
✓ 评估影响范围和严重程度
✓ 建议应对策略',
  NULL,
  true,
  true,
  '{
    "can_analyze_sentiment": true,
    "can_detect_crisis": true,
    "can_track_topics": true,
    "can_generate_alerts": true
  }'::jsonb,
  '{
    "negative_sentiment_threshold": 0.3,
    "mention_spike_threshold": 2.0,
    "crisis_threshold": "high"
  }'::jsonb,
  '{
    "social_media": {"enabled": false},
    "app_reviews": {"enabled": false},
    "forums": {"enabled": false}
  }'::jsonb,
  '{
    "version": "1.0",
    "category": "public_relations"
  }'::jsonb
);

-- 5. AI营运助理
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
  'AI营运助理',
  'operations_assistant',
  '帮助你处理日常营运工作，包括数据报表生成、异常监控、日常巡检等。让你从重复性工作中解放出来。

我可以帮你：
• 自动生成周报、月报
• 监控系统关键指标
• 执行定期巡检任务
• 整理会议记录和TODO

我的特点：
✓ 7x24小时工作
✓ 严格按照SOP执行
✓ 异常及时提醒
✓ 自动归档整理',
  NULL,
  true,
  true,
  '{
    "can_generate_reports": true,
    "can_monitor_metrics": true,
    "can_execute_tasks": true,
    "can_organize_data": true
  }'::jsonb,
  '{
    "metric_threshold": {"cpu": 0.8, "memory": 0.9},
    "check_frequency": "hourly"
  }'::jsonb,
  '{
    "monitoring_system": {"enabled": false},
    "log_system": {"enabled": false},
    "database": {"enabled": false}
  }'::jsonb,
  '{
    "version": "1.0",
    "category": "operations"
  }'::jsonb
);

-- Add comments
COMMENT ON TABLE agents IS 'AI员工定义表 - 包含内置和用户创建的AI员工';

-- 6. AI资讯追踪官
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

-- 7. Chris Chen 设计评审员
-- 基于Figma设计稿定义
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
  'Chris Chen',
  'design_validator',
  '身经百战，眼光如炬的设计老法师',
  NULL,
  true,
  true,
  '{
    "can_analyze_designs": true,
    "can_validate_interactions": true,
    "can_check_visual_consistency": true,
    "can_compare_designs": true,
    "can_search_cases": true,
    "multimodal": true
  }'::jsonb,
  '{
    "supported_file_types": ["image/png", "image/jpeg", "image/webp"]
  }'::jsonb,
  '{
    "knowledge_base": {"enabled": true}
  }'::jsonb,
  '{
    "version": "1.0",
    "category": "design",
    "figma_name": "Chris Chen",
    "figma_description": "身经百战，眼光如炬的设计老法师"
  }'::jsonb
);
