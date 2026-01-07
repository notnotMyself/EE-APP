---
title: "2025：大语言模型年度回顾"
source: "Simon Willison's Weblog"
url: "https://simonwillison.net/2025/Dec/31/llms-in-2025/"
date: "2025-12-31"
category: "人工智能"
score: 93
word_count: 7469
crawled_at: "2025-01-06T10:00:00"
---

# 2025：大语言模型年度回顾

> 本文对 2025 年 LLM 领域的重大趋势和发展进行了全面的年度回顾，延续了 Simon Willison 的系列文章。

## 核心亮点

### 1. 推理能力的突破 (RLVR)

LLM 在 2025 年实现了关键的"推理"能力突破，能够处理复杂的多步骤任务。这一进步直接推动了高性能 AI 智能体的广泛应用。

推理能力（Reasoning）的出现带来了：
- 更强的工具使用能力
- 高效的智能体执行
- 尤其在编程领域表现突出

### 2. 编程智能体的崛起

以"编码智能体"为代表的 AI 应用已能自主完成编写、执行与调试代码的全流程：

- **Claude Code** - Anthropic 推出的编程智能体，支持 CLI 操作
- **Cursor** - AI 驱动的代码编辑器
- **Windsurf** - 新兴的 AI 编程工具
- 某款 CLI 产品达到 **10 亿美元年营收额**的惊人表现

```python
# Claude Agent SDK 示例
from claude_agent_sdk import query, ClaudeAgentOptions

async for msg in query(
    prompt="分析这段代码并修复 bug",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        model="sonnet"
    )
):
    print(msg)
```

### 3. 行业竞争格局的变化

**中国开源模型崛起**：
- 排名领先的中国开源权重模型的戏剧性崛起
- 在多项能力排行榜上占据主导地位
- 展现出强大的技术实力

**谷歌 Gemini 的进展**：
- "Nano Banana" 等新模型发布
- 提示词驱动的图像编辑功能
- 对 OpenAI 领先地位发起挑战

**OpenAI 与 Meta 的观察**：
- Llama 和 OpenAI 领导地位下降
- 行业正在迎头赶上并趋于多元化

### 4. 新概念与范式

AI 专家安德烈·卡帕西提出了两个重要概念：

1. **幽灵智能 (Summoning Ghosts)**
   - 形象描述了当前 AI 的发展模式
   - AI 就像召唤"幽灵"来完成任务

2. **氛围编程 (Vibe Coding)**
   - 新兴的编程范式
   - 通过自然语言描述意图，让 AI 理解"氛围"来生成代码
   - 人类对这一新计算范式潜力的挖掘尚不足 10%

### 5. 安全担忧

文章探讨了多项安全问题：

- **YOLO 模式** - 让 AI 自主执行命令的风险
- **偏差正常化** - AI 输出中的偏见问题
- **高价订阅模式** - 向每月 200 美元的高价 LLM 订阅模式转变

### 6. 长任务处理能力

LLM 处理"长任务"的能力显著提升：
- 可以执行持续数小时的复杂任务
- 支持更深层次的问题分析
- 在学术竞赛中夺金（如数学奥林匹克）

## 总结

> 2025年描绘了一个快速演进、竞争激烈且能力日益增强的 AI 景观。

这是大语言模型技术从基础能力构建向深度应用与产业落地的关键转折点。未来的发展空间依旧广阔，人类对这一新计算范式潜力的挖掘尚不足 10%。

---

*原文链接: https://simonwillison.net/2025/Dec/31/llms-in-2025/*
*本文由 AI资讯追踪官 自动抓取整理*
