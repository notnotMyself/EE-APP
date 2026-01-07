# AI 数字员工平台 - 项目指南

## 产品定位

**核心定位**：企业内部的 AI 角色工作台 + 决策前哨站

**一句话价值**：让用户可以说"这件事我不管了，让 AI 帮我盯着"

### 产品理念

1. **不是信息流 APP**：不追求内容丰富度，追求"错过有成本"的价值信息
2. **不是问答机器人**：AI 员工能主动提醒、持续跟踪、执行任务
3. **任务托付**：用户订阅的不是"内容"，而是把某块职责外包给 AI

### AI 员工设计原则

每个 AI 员工必须回答三个问题：
1. 它替谁负责？
2. 它盯什么长期问题？
3. 什么时候会主动找人？

### 信息流铁律

- 一天 ≤ 3 条
- 宁可不发，也不刷存在感
- 每一条都必须能接上对话

---

## AI 技术方向

### 技术选型：Claude Agent SDK

**选择 Claude Agent SDK 而非直接调用 Claude API 的原因**：

| 对比项 | Claude API (直接调用) | Claude Agent SDK |
|-------|----------------------|------------------|
| 能力 | 基础问答 + Tool Use | 完整 Agent 框架 |
| 工具调用 | 需自己实现循环 | SDK 自动处理 |
| 多步骤任务 | 需自己维护状态 | 自动管理 |
| Sub-agent | 需自己实现 | 内置支持 |
| Skills | 需自己封装 | 通过 MCP 服务器 |
| 适用场景 | 简单问答 | 任务委派 |

### Claude Agent SDK 核心能力

```python
# 安装
pip install claude-agent-sdk

# 基础用法
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="分析最近的研发效能数据",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        cwd="/path/to/agent/workdir"
    )
):
    print(message)
```

### 核心特性

1. **工具调用 (Tool Use)**
   - 内置：Read, Write, Edit, Bash, Grep, Glob, WebFetch
   - 自定义：通过 `@tool` 装饰器 + MCP 服务器

2. **Sub-agent 协作**
   ```python
   options = ClaudeAgentOptions(
       agents={
           "analyzer": AgentDefinition(
               description="分析代码结构",
               tools=["Read", "Grep"],
               model="sonnet"
           ),
           "reporter": AgentDefinition(
               description="生成报告",
               tools=["Write"],
               model="haiku"
           )
       }
   )
   ```

3. **Skills 执行**
   - 通过 MCP 服务器定义可复用技能
   - 支持进程内服务器，无需单独进程

4. **Hooks**
   - PreToolUse：工具调用前拦截
   - PostToolUse：工具调用后处理

### 迁移策略

**当前状态** → **目标状态**
- 现有：Anthropic Python SDK + 自实现工具层
- 目标：Claude Agent SDK + MCP 自定义工具

**迁移路径**：先做 POC 验证，新功能用 SDK，旧功能逐步迁移

---

## 项目结构

```
ee_app_claude/
├── ai_agent_app/                 # Flutter 前端
├── ai_agent_platform/backend/    # FastAPI 后端（待迁移到 Agent SDK）
├── backend/
│   ├── agent_orchestrator/       # Agent 管理器（当前实现）
│   └── agents/                   # AI 员工工作目录
│       └── {agent_role}/
│           ├── CLAUDE.md         # Agent 行为定义
│           ├── .claude/skills/   # 可执行技能脚本
│           └── reports/          # 生成的报告
├── supabase/                     # 数据库配置
└── openspec/                     # 规范文档
```

---

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->