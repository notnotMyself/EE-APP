# AI资讯追踪官 - 技能清单

本文档定义了 AI资讯追踪官 的所有可用技能及其接口规范。

---

## 技能概览

| 技能 ID | 名称 | 说明 | 优先级 |
|---------|------|------|--------|
| `news_crawler` | AI资讯爬取与简报生成 | 爬取 AI 资讯并生成标准化简报 | 核心 |

---

## 1. news_crawler - AI资讯爬取与简报生成

### 概述

爬取多个 AI 资讯源（ai-bot.cn、bestblogs.dev），生成标准化简报，支持推送到 Supabase 信息流。

### 脚本位置

```
.claude/skills/news_crawler.py
```

### 调用方式

```bash
echo '<JSON参数>' | python3 .claude/skills/news_crawler.py
```

### 输入格式 (stdin JSON)

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `action` | string | ❌ | `briefing` | 执行动作：`crawl` / `briefing` / `push` / `full` |
| `source` | string | ❌ | `aibot` | 数据源：`aibot` / `bestblogs` / `all` |
| `days` | int | ❌ | `3` | 爬取天数范围 (1-7) |
| `push` | bool | ❌ | `false` | 是否推送到信息流 |

#### Action 说明

| Action | 说明 |
|--------|------|
| `crawl` | 仅爬取数据，不生成简报 |
| `briefing` | 爬取并生成简报（默认） |
| `push` | 爬取、生成简报并推送 |
| `full` | 完整流程（等同于 `push`） |

### 输出格式 (stdout JSON)

```json
{
    "success": true,
    "action": "full",
    "source": "all",
    "timestamp": "2026-01-13T10:00:00",
    "crawl_results": [
        {
            "success": true,
            "source": "aibot",
            "output": "...",
            "briefing": {...}
        }
    ],
    "briefing": {
        "briefing_type": "summary",
        "priority": "P1",
        "title": "...",
        "summary": "...",
        "should_push": true,
        "context_data": {...}
    },
    "pushed": true,
    "message": "生成简报成功，已推送到信息流"
}
```

### 简报字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `briefing_type` | string | 固定为 `summary` |
| `priority` | string | 优先级：`P1`（重要）/ `P2`（普通） |
| `title` | string | 简报标题 |
| `summary` | string | Markdown 格式摘要 |
| `impact` | string | 影响说明 |
| `actions` | array | 操作按钮配置 |
| `context_data` | object | 完整文章数据 |
| `should_push` | bool | 是否值得推送 |
| `importance_score` | float | 重要性评分 (0-1) |

### 使用示例

```bash
# 爬取 ai-bot.cn 最近 1 天资讯，生成简报
echo '{"action": "briefing", "source": "aibot", "days": 1}' | python3 .claude/skills/news_crawler.py

# 爬取所有源，生成简报并推送
echo '{"action": "full", "source": "all", "days": 3, "push": true}' | python3 .claude/skills/news_crawler.py

# 仅爬取 bestblogs，不生成简报
echo '{"action": "crawl", "source": "bestblogs", "days": 7}' | python3 .claude/skills/news_crawler.py

# 交互模式（无参数，使用默认配置）
python3 .claude/skills/news_crawler.py
```

### 依赖的底层脚本

| 脚本 | 说明 |
|------|------|
| `crawl_aibot.py` | ai-bot.cn 爬虫 |
| `crawl_articles.py` | bestblogs.dev 爬虫 |

### 环境变量（推送功能）

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

### 错误处理

```json
{
    "success": false,
    "error": "Invalid JSON input: ...",
    "usage": {
        "action": "crawl|briefing|push|full",
        "source": "aibot|bestblogs|all",
        "days": "1-7",
        "push": "true|false"
    }
}
```

---

## 技能扩展指南

### 添加新技能

1. 在 `.claude/skills/` 目录下创建新的 Python 脚本
2. 遵循标准接口规范：stdin JSON 输入，stdout JSON 输出
3. 更新本文档，添加新技能的接口说明
4. 更新 `CLAUDE.md` 中的能力描述

### 接口规范

所有技能脚本应遵循：

```python
#!/usr/bin/env python3
"""
Skill Name
技能描述
"""

import json
import sys

def main():
    # 从 stdin 读取 JSON 参数
    input_data = sys.stdin.read().strip()
    params = json.loads(input_data) if input_data else {}
    
    # 执行技能逻辑
    result = run_skill(params)
    
    # 输出 JSON 结果到 stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

