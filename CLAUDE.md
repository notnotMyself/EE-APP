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
---

## 测试与验收规范

### 验收原则

**核心要求**: 任何功能实现都必须经过严格的测试验收，确保代码真正可用，而不仅仅是"文件存在"。

### 强制要求

1. **数据库迁移必须执行**
   - 创建迁移文件后，必须执行 `supabase db push`
   - 验证表结构和字段是否正确创建
   - 检查 RLS 策略是否生效

2. **后端服务必须启动并测试**
   - 启动后端：`cd backend/agent_orchestrator && python3 main.py`
   - 验证健康检查：`curl http://localhost:8000/health`
   - 测试所有新增的 API 端点

3. **功能端到端验证**
   - 运行 acceptance 测试脚本（如有）
   - 手动验证关键功能流程
   - 使用 webapp-testing skill 测试 Flutter 应用（当可用时）

4. **集成测试**
   - 新 Agent 必须能在 `/api/v1/agents` 列表中显示
   - 新 Agent 的 `/api/v1/agents/{id}` 端点必须返回正确信息
   - Skills 和工具必须能正常调用

### 验收检查清单

#### 后端功能验收

```bash
# 1. 启动后端
cd backend/agent_orchestrator
python3 main.py

# 2. 健康检查
curl http://localhost:8000/health | jq .

# 3. 列出所有 Agents
curl http://localhost:8000/api/v1/agents | jq '.total'

# 4. 测试新增 Agent 详情
curl http://localhost:8000/api/v1/agents/{agent_id} | jq .

# 5. 测试新增 API（如 Skill Templates）
curl http://localhost:8000/api/v1/agents/skill-templates | jq '.success'
```

#### 数据库验收

```bash
# 1. 检查迁移文件
ls -la supabase/migrations/*.sql

# 2. 执行迁移
supabase db push --db-url <connection_string>

# 3. 验证表结构（在 Supabase Dashboard）
# - 表是否创建
# - 字段类型是否正确
# - 索引是否存在
# - RLS 策略是否配置
```

#### Agent 验收

```bash
# 1. 检查文件结构
ls -la backend/agents/{agent_id}/
# 必须包含: agent.yaml, CLAUDE.md, .claude/skills/

# 2. 验证 agent.yaml
python3 -c "import yaml; print(yaml.safe_load(open('backend/agents/{agent_id}/agent.yaml'))['metadata']['id'])"

# 3. 测试 Agent 注册
# Agent 应该出现在 /api/v1/agents 列表中

# 4. 测试 Skills（如果有）
cd backend/agents/{agent_id}
echo '{"action": "test"}' | python3 .claude/skills/skill_name.py
```

### 自动化验收脚本

创建 `test_acceptance.py` 脚本来自动化验收流程：

```python
#!/usr/bin/env python3
"""
综合验收测试脚本
"""
import requests

BASE_URL = "http://localhost:8000"

def test_backend_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Backend healthy")

def test_new_agents():
    response = requests.get(f"{BASE_URL}/api/v1/agents")
    agents = response.json()['agents']
    agent_roles = [a['role'] for a in agents]
    
    # 检查新增的 agents
    assert 'new_agent_role' in agent_roles
    print("✅ New agent registered")

def test_new_api_endpoints():
    # 测试新增的 API 端点
    response = requests.get(f"{BASE_URL}/api/v1/new-endpoint")
    assert response.status_code == 200
    print("✅ New API endpoint works")

if __name__ == "__main__":
    test_backend_health()
    test_new_agents()
    test_new_api_endpoints()
    print("\n✅ All acceptance tests passed!")
```

### webapp-testing Skill

当需要测试 Flutter 应用时，使用 webapp-testing skill：

```python
# 示例：测试登录流程
from webapp_testing import test_workflow

test_workflow({
    "url": "http://localhost:5000",
    "credentials": {
        "email": "test@example.com",
        "password": "password"
    },
    "steps": [
        {"action": "navigate", "target": "/login"},
        {"action": "fill", "selector": "#email", "value": "test@example.com"},
        {"action": "fill", "selector": "#password", "value": "password"},
        {"action": "click", "selector": "button[type=submit]"},
        {"action": "assert", "selector": ".dashboard", "exists": True}
    ]
})
```

### 常见验收失败原因

1. **API 路由未注册**
   - 问题：创建了 API 文件但没有在 `main.py` 中注册
   - 解决：检查 `app.include_router()` 调用

2. **导入路径错误**
   - 问题：使用相对导入但目录结构不支持
   - 解决：改用绝对导入或修复 `sys.path`

3. **Agent 未注册到 AgentRegistry**
   - 问题：agent.yaml 存在但 `visibility: private` 导致权限问题
   - 解决：改为 `visibility: public` 或实现正确的权限检查

4. **数据库迁移未执行**
   - 问题：创建了迁移文件但表不存在
   - 解决：执行 `supabase db push`

5. **环境变量未配置**
   - 问题：依赖 API Key 但未设置
   - 解决：检查 `.env` 文件和环境变量

### 验收报告模板

每次重大功能实现后，应该生成验收报告：

```markdown
# 功能验收报告

## 功能概述
[简要说明实现的功能]

## 验收结果
- ✅ 后端健康检查通过
- ✅ API 端点测试通过 (X/Y)
- ✅ Agent 注册成功
- ✅ 数据库迁移执行成功
- ⚠️  Flutter UI 待开发

## 测试覆盖率
- 单元测试：X%
- 集成测试：Y%
- 端到端测试：Z%

## 发现的问题
1. [问题描述]
2. [问题描述]

## 待完成工作
1. [任务描述]
2. [任务描述]

## 验收结论
[✅ 通过 / ⚠️ 部分通过 / ❌ 未通过]
```

### 最后提醒

**记住：验收不是走形式，而是确保代码真正可用。如果测试失败，必须修复问题，而不是声称"功能已完成"。**

测试是质量的保证，是对用户负责，也是对自己负责。

