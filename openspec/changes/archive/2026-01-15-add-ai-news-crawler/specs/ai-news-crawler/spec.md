## ADDED Requirements

### Requirement: AI资讯追踪官角色定义

系统 SHALL 提供一个名为 `ai_news_crawler` 的 AI 员工，专注于抓取和整理 AI 前沿资讯。

该 Agent 的核心职责包括：
1. 爬取指定网站的 AI 相关文章
2. 保留文章原始格式（标题、正文、代码块、图片链接）
3. 生成结构化的资讯摘要
4. 支持按时间范围和分类筛选

#### Scenario: Agent 成功创建

- **GIVEN** 系统已部署 AI 员工框架
- **WHEN** 用户请求使用 AI资讯追踪官
- **THEN** 系统返回该 Agent 的能力描述和可用命令

---

### Requirement: Bestblogs 文章列表爬取

系统 SHALL 支持从 https://www.bestblogs.dev/articles 爬取文章列表。

爬取参数：
- `days`: 获取最近 N 天的文章（默认 7 天）
- `language`: 文章语言（默认中文）
- `category`: 文章分类（可选，如"人工智能"、"软件编程"等）

返回数据结构：
```json
{
  "articles": [
    {
      "title": "文章标题",
      "url": "文章链接",
      "source": "来源网站",
      "date": "2024-01-06",
      "word_count": 7469,
      "read_time": "约 30 分钟",
      "score": 93,
      "category": "人工智能",
      "summary": "LLM 摘要..."
    }
  ],
  "total": 50,
  "crawled_at": "2024-01-06T10:00:00Z"
}
```

#### Scenario: 成功获取最近一周中文文章

- **GIVEN** bestblogs.dev 网站可访问
- **WHEN** 执行 `python crawl_articles.py --days 7 --language zh`
- **THEN** 返回最近一周的中文文章列表
- **AND** 每篇文章包含标题、链接、来源、日期、摘要等元数据

#### Scenario: 网站不可访问时的错误处理

- **GIVEN** 网络异常或网站不可访问
- **WHEN** 执行爬取命令
- **THEN** 脚本输出清晰的错误信息
- **AND** 退出码为非零

---

### Requirement: 文章详情爬取与格式保留

系统 SHALL 支持爬取单篇文章的完整内容，并保留原始格式。

保留的格式元素：
- Markdown 标题层级（h1-h6）
- 段落和换行
- 代码块（带语言标识）
- 列表（有序/无序）
- 图片（保留 URL 和 alt 文本）
- 链接
- 粗体/斜体强调

存储格式：
```markdown
---
title: 文章标题
source: 来源网站
url: 原文链接
date: 2024-01-06
category: 人工智能
---

# 文章标题

文章正文内容...

![图片描述](https://example.com/image.png)

```python
代码示例
```
```

#### Scenario: 成功爬取并保留文章格式

- **GIVEN** 文章 URL 有效
- **WHEN** 执行详情爬取
- **THEN** 生成 Markdown 文件，保留原始格式
- **AND** 文件头部包含 YAML frontmatter 元数据

#### Scenario: 处理包含代码块的技术文章

- **GIVEN** 文章包含多个代码块
- **WHEN** 执行详情爬取
- **THEN** 代码块正确保留语言标识和缩进
- **AND** 代码内容不被截断

---

### Requirement: 文章索引与增量更新

系统 SHALL 维护一个文章索引，支持增量更新以避免重复爬取。

索引文件 (`data/index.json`) 结构：
```json
{
  "last_updated": "2024-01-06T10:00:00Z",
  "articles": {
    "article-url-hash": {
      "url": "...",
      "title": "...",
      "crawled_at": "...",
      "file_path": "articles/2024-01-06-xxx.md"
    }
  }
}
```

#### Scenario: 增量更新只爬取新文章

- **GIVEN** 索引中已有 20 篇文章记录
- **WHEN** 执行爬取命令
- **AND** 列表中有 25 篇文章（5 篇是新的）
- **THEN** 只爬取并存储 5 篇新文章
- **AND** 更新索引文件

#### Scenario: 强制全量更新

- **GIVEN** 用户需要重新爬取所有文章
- **WHEN** 执行 `python crawl_articles.py --force`
- **THEN** 忽略索引，重新爬取所有文章

---

### Requirement: 资讯摘要报告生成

系统 SHALL 支持生成每日/每周的资讯摘要报告。

报告包含以下内容：
- 标题：AI资讯周报 - 日期
- 统计：本周收录文章数量
- 热门文章 TOP 5（按评分排序，含标题、来源、评分、摘要）
- 按分类浏览（人工智能、软件编程等分类，列出文章标题和链接）
- 页脚：自动生成标识

#### Scenario: 生成每周资讯摘要

- **GIVEN** 本周已爬取 50 篇文章
- **WHEN** 执行 `python crawl_articles.py --report weekly`
- **THEN** 在 `reports/` 目录生成周报 Markdown 文件
- **AND** 按评分排序展示热门文章
- **AND** 按分类归纳所有文章

