# Project Context

## Purpose

**AI数字员工平台** - 基于 Claude AI 的企业智能助手系统

### 核心目标
- 为企业提供专业的 AI 数字员工，帮助团队减少认知负担
- AI 员工持续监控数据，在需要时主动提醒用户
- 支持长期任务托付，而非一次性对话
- 让 AI 真正执行任务（数据分析、报告生成、工具调用）

### 产品定位
> "企业内部的 AI 角色工作台 + 决策前哨站"
> "我把哪些事情交给 AI 员工后，可以放心不盯着了"

### 当前 AI 员工
1. **研发效能分析官** (dev_efficiency_analyst) - 已实现 ✅
   - 监控代码审查效率
   - 分析 Review 耗时、返工率
   - 生成效率报告和改进建议
2. **AI资讯追踪官** (ai_news_crawler) - 已实现 ✅
   - 爬取 AI 前沿资讯和技术博客
   - 保留文章原始格式和图片链接
   - 生成每周资讯摘要报告
3. NPS 洞察官 (nps_insight_analyst) - 待实现
4. 产品需求提炼官 (product_requirement_analyst) - 待实现
5. 竞品追踪分析官 (competitor_tracking_analyst) - 待实现
6. 企业知识管理官 (knowledge_management_assistant) - 待实现

---

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - HTTP/WebSocket API 服务
- **Claude Agent SDK** (`claude-agent-sdk`) - 官方 Agent 框架 🆕
  - 底层调用 Claude Code CLI
  - 内置工具：Read, Write, Edit, Bash, Grep, Glob, WebFetch
  - 支持 Sub-agent、MCP 自定义工具、Hooks
- **Anthropic Python SDK** - 基础 API 调用（旧，待迁移）
- **httpx** - HTTP 客户端
- **anyio** - 异步执行（Agent SDK 依赖）

### Frontend
- **Flutter 3.24.3** - 跨平台移动应用
- **Dart** - 编程语言
- **Riverpod** - 状态管理

### Database & Services
- **Supabase** - PostgreSQL + Auth + Realtime
  - `users` - 用户表
  - `agents` - AI 员工定义
  - `conversations` - 对话记录
  - `messages` - 消息历史
  - `user_agent_subscriptions` - 订阅关系
- **Celery + Redis** - 定时任务（待实现）
- **Firebase Cloud Messaging** - Push 通知（待实现）

### AI & Tools (目标架构)
- **Claude Agent SDK** - 官方 Python SDK
  - 安装：`pip install claude-agent-sdk`
  - 自动捆绑 Claude Code CLI
- **内置工具**: Read, Write, Edit, Bash, Grep, Glob, WebFetch, Task
- **自定义工具**: 通过 MCP 服务器 (`@tool` 装饰器)
- **Model**: sonnet (默认) / opus (复杂任务) / haiku (简单任务)

---

## Project Conventions

### Code Style

**Python (Backend)**
- PEP 8 编码规范
- 使用 type hints
- async/await 异步编程
- 函数命名：snake_case
- 类命名：PascalCase

**Dart/Flutter (Frontend)**
- Effective Dart 规范
- 驼峰命名法（camelCase）
- Widget 组件拆分原则

### Architecture Patterns

**目标架构 (Claude Agent SDK)**
```
Flutter App
    ↓ HTTP/SSE
FastAPI (Backend API)
    ↓
Claude Agent SDK
    ↓ subprocess
Claude Code CLI (bundled)
    ↓
Claude API + Tool Execution
```

**Agent SDK 调用示例**
```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

# 简单查询
async for msg in query(
    prompt="分析研发效能数据",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Bash"],
        cwd="/path/to/agent/workdir"
    )
):
    print(msg)

# Sub-agent 协作
options = ClaudeAgentOptions(
    agents={
        "analyzer": AgentDefinition(
            description="数据分析专家",
            tools=["Read", "Grep", "Bash"],
            model="sonnet"
        ),
        "reporter": AgentDefinition(
            description="报告生成专家",
            tools=["Write"],
            model="haiku"
        )
    }
)
```

**自定义工具 (MCP Server)**
```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("gerrit_query", "查询 Gerrit 代码审查数据", {"project": str, "days": int})
async def gerrit_query(args):
    # 调用 Gerrit API
    result = await fetch_gerrit_data(args["project"], args["days"])
    return {"content": [{"type": "text", "text": json.dumps(result)}]}

# 创建 MCP 服务器
gerrit_server = create_sdk_mcp_server(
    name="gerrit",
    tools=[gerrit_query]
)
```

**工作目录隔离**
- 每个 AI 员工有独立的 workspace：`backend/agents/{agent_role}/`
- 目录结构：
  ```
  agents/{agent_role}/
  ├── CLAUDE.md           # Agent 行为定义（作为 system prompt）
  ├── .claude/
  │   ├── settings.json   # 配置
  │   └── skills/         # 可执行的 Python 脚本
  ├── data/               # 数据缓存
  ├── reports/            # 生成的报告
  └── scripts/            # 分析脚本
  ```

**旧架构 (待迁移)**
```
Flutter App
    ↓
FastAPI (Backend Orchestrator)
    ↓
AgentManager (自实现)
    ↓
Anthropic SDK → Claude API
    ↓
Tool Execution (bash, read_file, write_file, web_fetch)
```

### Testing Strategy

**当前状态**
- 手动测试为主
- 使用 Python 脚本测试工具执行
- 验证 Skills 可执行性

**待实现**
- [ ] Backend 单元测试（pytest）
- [ ] Flutter 集成测试
- [ ] E2E 测试

### Git Workflow

**分支策略**
- `main` - 生产分支
- Feature 分支：直接在 main 开发（小团队）

**Commit 规范**
- 描述性提交信息
- 中英文混合

---

## Domain Context

### 研发效能领域
- **Code Review**: Gerrit 系统，Review 耗时、返工率指标
- **阈值标准**：
  - Review 中位耗时 < 24 小时
  - Review P95 耗时 < 72 小时
  - 返工率 < 15%
- **Gerrit API**: 获取代码审查数据

### NPS 用户满意度（待实现）
- Net Promoter Score
- 用户反馈分析
- 痛点识别

### 产品需求管理（待实现）
- 需求提炼
- 需求清晰度评估

---

## Important Constraints

### 技术约束
1. **使用 Claude Agent SDK**
   - 官方 Python SDK：`claude-agent-sdk`
   - 底层调用 Claude Code CLI（自动捆绑）
   - 保持 Python 后端生态

2. **自定义 API 网关**
   - 使用内部 LLM Gateway：`https://llm-gateway.oppoer.me`
   - 需要配置环境变量或 CLI 参数

3. **Workspace 隔离**
   - AI 只能访问自己的工作目录
   - 通过 `cwd` 参数限制 Agent 范围

### 业务约束
- 企业内部产品（非公开 SaaS）
- 小团队（1-3 人）
- 聚焦 MVP，快速验证

### 安全约束
- 不允许 AI 访问敏感数据
- 工具执行限制在 Agent workspace
- 数据库 RLS 策略

---

## External Dependencies

### API & Services
- **Claude API** (llm-gateway.oppoer.me)
  - Model: saas/claude-sonnet-4.5
  - Tool Calling 支持
- **Supabase**
  - PostgreSQL 数据库
  - Auth 服务
  - Realtime subscriptions

### 待集成
- [ ] **Gerrit API** - 代码审查数据（需要权限）
- [ ] **Jira/Issue API** - 需求跟踪数据
- [ ] **Firebase** - Push 通知
- [ ] **Celery + Redis** - 定时任务调度

### 开发工具
- **OpenSpec** - 规范驱动开发（本工具）
- **Claude Code** - AI 编程助手
- **Supabase Studio** - 数据库管理

---

## Current Status

### Phase 1: MVP ✅
- [x] 数据库 Schema 设计
- [x] 用户认证（Supabase Auth）
- [x] Agent Manager 工具执行能力（旧架构）
- [x] 研发效能分析官实现
- [x] Flutter 前端基础对话功能

### Phase 2: Agent SDK 迁移 🔄 (当前)
- [ ] **POC 验证** - 验证 Claude Agent SDK 可行性
  - [ ] 安装 `claude-agent-sdk`
  - [ ] 验证基础 query() 功能
  - [ ] 验证自定义工具 (MCP Server)
  - [ ] 验证 Sub-agent 协作
- [ ] **研发效能分析官迁移**
  - [ ] 将现有 skills 迁移为 MCP 工具
  - [ ] 测试与旧实现对比
- [ ] **新功能用 Agent SDK 实现**
  - [ ] NPS 洞察官
  - [ ] 竞品追踪分析官

### Phase 3: 完善功能
- [ ] 其他 AI 员工
- [ ] 真实数据源集成（Gerrit API）
- [ ] 定时任务和异常提醒
- [ ] 图表生成 skill

### Phase 4: Multi-Agent 协作
- [ ] Coordinator Agent
- [ ] Agent 间通信协议

---

## Development Notes

### 启动服务
```bash
# Backend
cd backend/agent_orchestrator
python3 main.py  # http://localhost:8000

# Flutter (Web)
cd ai_agent_app
flutter run -d chrome  # http://localhost:60913
```

### 测试工具执行
```bash
python3 /tmp/test_agent.py  # 测试基本工具
python3 /tmp/test_skill.py  # 测试 Skills 执行
```

### 关键文件路径
- Agent 定义：`backend/agents/{role}/CLAUDE.md`
- Agent Manager：`backend/agent_orchestrator/agent_manager.py`
- API 入口：`backend/agent_orchestrator/main.py`
- Flutter 对话：`ai_agent_app/lib/features/conversations/`
