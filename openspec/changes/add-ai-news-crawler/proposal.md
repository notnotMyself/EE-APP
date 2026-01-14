# Change: 新增 AI资讯追踪官 (AI News Crawler Agent)

## Why

团队需要持续跟踪 AI 前沿资讯和技术博客，但手动浏览各类网站耗时且容易遗漏重要信息。通过新增一个专门的 AI 员工来自动抓取、整理和呈现 AI 相关内容，可以帮助团队保持对行业动态的敏感度。

## What Changes

- 新增 AI 员工：`ai_news_crawler` (AI资讯追踪官)
- 核心能力：爬取指定网站的中文文章，保留原始格式和图片
- 首个数据源：https://www.bestblogs.dev/articles（获取最近一周的中文 AI 文章）
- 生成结构化的资讯摘要和原文存档

## Impact

- Affected specs: 新增 `specs/ai-news-crawler/` 能力定义
- Affected code: 
  - `backend/agents/ai_news_crawler/` - 新 Agent 工作目录
  - `backend/agents/ai_news_crawler/CLAUDE.md` - Agent 角色定义
  - `backend/agents/ai_news_crawler/crawl_articles.py` - 爬虫核心脚本


