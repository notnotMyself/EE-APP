# Design: AI资讯追踪官

## Context

团队需要持续跟踪 AI 前沿资讯，目标网站 bestblogs.dev 是一个聚合了顶级编程、人工智能、产品、科技文章的中文站点，使用 LLM 进行摘要评分辅助阅读。

### 目标网站分析

**bestblogs.dev/articles 页面结构**：
- 文章卡片列表，包含标题、来源、日期、字数、评分
- 支持时间筛选（过去1周）和语言筛选（中文）
- 文章详情页包含完整内容、格式和图片

## Goals / Non-Goals

**Goals:**
- 自动抓取 bestblogs.dev 最近一周的中文文章
- 保留文章原始格式（标题、段落、代码块、图片链接）
- 生成结构化的资讯摘要供用户快速浏览
- 支持增量更新，避免重复抓取

**Non-Goals:**
- 不实现完整的通用爬虫框架
- 不下载和存储图片文件（仅保留链接）
- 不进行文章内容的二次 AI 分析（用户可手动触发）

## Decisions

### 技术选型

- **爬虫库**: `httpx` + `beautifulsoup4` + `selectolax`
  - httpx: 异步 HTTP 客户端，与项目现有依赖一致
  - beautifulsoup4: HTML 解析，成熟稳定
  - selectolax: 备选，性能更好

- **数据存储格式**: JSON + Markdown
  - JSON: 结构化元数据（标题、来源、日期、链接、分类）
  - Markdown: 文章正文，保留格式

- **运行方式**: Python 脚本，通过 Agent 的 Bash 工具调用

### 目录结构

```
backend/agents/ai_news_crawler/
├── CLAUDE.md              # Agent 角色定义
├── crawl_articles.py      # 爬虫主脚本
├── data/
│   ├── articles/          # 文章详情 (markdown)
│   │   └── 2024-01-06-xxx.md
│   └── index.json         # 文章索引
├── reports/
│   └── weekly_digest.md   # 周报
└── 使用指南.md
```

### 爬取策略

1. **请求频率**: 间隔 1-2 秒，避免被封禁
2. **User-Agent**: 使用标准浏览器 UA
3. **错误处理**: 重试 3 次，失败后跳过并记录
4. **增量更新**: 基于文章 URL 去重

## Risks / Trade-offs

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 网站结构变化导致爬虫失效 | 无法获取数据 | 模块化选择器，易于维护更新 |
| 被网站封禁 IP | 爬取中断 | 控制频率，使用合理 UA |
| 文章格式复杂导致解析不完整 | 内容丢失 | 保留原始 HTML 备份 |

## Open Questions

- [ ] 是否需要支持代理配置？
- [ ] 是否需要集成到定时任务系统？
- [ ] 后续是否扩展支持更多网站？

