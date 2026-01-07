# 架构设计规范

## 概述

本文档描述从现有架构迁移到 Claude Agent SDK + 实时通信架构的详细设计。

## 架构对比

### 现有架构

```
┌─────────────────────────────────────────────────────────────┐
│                      现有架构                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Flutter App                                                 │
│      │                                                       │
│      ↓ WebSocket / SSE                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │  FastAPI (main.py)                          │            │
│  │      │                                      │            │
│  │      ↓                                      │            │
│  │  AgentManager (agent_manager.py)            │            │
│  │      │                                      │            │
│  │      ├─→ Anthropic SDK (messages.create)    │            │
│  │      │       └─→ 非流式，等待完整响应        │            │
│  │      │                                      │            │
│  │      └─→ 自实现 Agentic Loop                │            │
│  │              ├─→ while True                 │            │
│  │              ├─→ 检测 tool_use              │            │
│  │              └─→ 执行工具 → 继续循环         │            │
│  └─────────────────────────────────────────────┘            │
│                                                              │
│  问题：                                                      │
│  - 客户端断开 → 任务中断                                      │
│  - 非流式 API → 体验差                                       │
│  - 自维护 Agent 框架 → 维护成本高                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 目标架构

```
┌─────────────────────────────────────────────────────────────┐
│                      目标架构                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Flutter App                                                 │
│      │                                                       │
│      ├─→ POST /chat → 创建任务 → 返回 task_id               │
│      │                                                       │
│      ├─→ GET /chat/stream (SSE)                             │
│      │       └─→ 可选：前台实时流式输出                       │
│      │                                                       │
│      └─→ Supabase Realtime                                  │
│              └─→ 订阅 messages 表                            │
│              └─→ 离线后重新进入自动恢复                       │
│                                                              │
│  ┌─────────────────────────────────────────────┐            │
│  │  FastAPI (main.py)                          │            │
│  │      │                                      │            │
│  │      ├─→ 创建 task 记录 (tasks 表)          │            │
│  │      │                                      │            │
│  │      └─→ asyncio.create_task()              │            │
│  │              └─→ 后台执行，不阻塞请求        │            │
│  └─────────────────────────────────────────────┘            │
│                      │                                       │
│                      ↓                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │  AgentSDKService (agent_sdk_service.py)     │            │
│  │      │                                      │            │
│  │      ├─→ Claude Agent SDK                   │            │
│  │      │       └─→ query() / ClaudeSDKClient  │            │
│  │      │       └─→ SDK 自动管理 Agentic Loop   │            │
│  │      │                                      │            │
│  │      ├─→ MCP 自定义工具                      │            │
│  │      │       └─→ @tool gerrit_query         │            │
│  │      │       └─→ @tool efficiency_trend     │            │
│  │      │                                      │            │
│  │      └─→ 流式写入 Supabase                  │            │
│  │              └─→ 实时 INSERT/UPDATE messages │            │
│  └─────────────────────────────────────────────┘            │
│                      │                                       │
│                      ↓                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │  Supabase                                   │            │
│  │      │                                      │            │
│  │      ├─→ tasks 表                           │            │
│  │      │       └─→ 任务状态、元数据            │            │
│  │      │                                      │            │
│  │      ├─→ messages 表                        │            │
│  │      │       └─→ 对话消息（实时追加内容）    │            │
│  │      │                                      │            │
│  │      └─→ Realtime                           │            │
│  │              └─→ 广播 messages 变更          │            │
│  │              └─→ Flutter 实时接收           │            │
│  └─────────────────────────────────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件设计

### 1. AgentSDKService

负责封装 Claude Agent SDK 调用，管理 MCP 工具。

```python
# backend/agent_sdk/agent_sdk_service.py

from claude_agent_sdk import (
    query, ClaudeAgentOptions, AgentDefinition,
    tool, create_sdk_mcp_server,
    AssistantMessage, TextBlock, ToolUseBlock, ResultMessage
)

class AgentSDKService:
    """基于 Claude Agent SDK 的 Agent 服务"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.mcp_server = self._create_mcp_server()

    def _create_mcp_server(self):
        """创建 MCP 自定义工具服务器"""
        return create_sdk_mcp_server(
            name="dev_efficiency",
            tools=[
                gerrit_query_tool,
                efficiency_trend_tool,
                # ... 更多工具
            ]
        )

    async def execute_agent_task(
        self,
        task_id: str,
        agent_role: str,
        prompt: str,
        conversation_id: str
    ):
        """执行 Agent 任务（后台运行）"""

        # 1. 更新任务状态为 running
        await self._update_task_status(task_id, "running")

        # 2. 创建 AI 消息记录
        message_id = await self._create_message(
            conversation_id=conversation_id,
            role="assistant",
            status="streaming"
        )

        # 3. 获取 Agent 配置
        options = self._get_agent_options(agent_role)

        # 4. 流式执行并写入数据库
        try:
            content_buffer = ""
            async for msg in query(prompt=prompt, options=options):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            content_buffer += block.text
                            # 实时更新消息内容
                            await self._update_message_content(
                                message_id, content_buffer
                            )

            # 5. 标记完成
            await self._update_message_status(message_id, "completed")
            await self._update_task_status(task_id, "completed")

        except Exception as e:
            await self._update_task_status(task_id, "failed", error=str(e))
            raise
```

### 2. 任务管理器

负责任务的创建、调度和状态管理。

```python
# backend/agent_sdk/task_manager.py

class TaskManager:
    """任务管理器"""

    def __init__(self, supabase_client, agent_service: AgentSDKService):
        self.supabase = supabase_client
        self.agent_service = agent_service

    async def create_task(
        self,
        conversation_id: str,
        agent_role: str,
        user_message: str
    ) -> str:
        """创建任务并异步执行"""

        # 1. 保存用户消息
        await self._save_user_message(conversation_id, user_message)

        # 2. 创建任务记录
        task = await self.supabase.table("tasks").insert({
            "conversation_id": conversation_id,
            "agent_role": agent_role,
            "prompt": user_message,
            "status": "pending"
        }).execute()

        task_id = task.data[0]["id"]

        # 3. 异步执行（不阻塞请求）
        asyncio.create_task(
            self.agent_service.execute_agent_task(
                task_id=task_id,
                agent_role=agent_role,
                prompt=user_message,
                conversation_id=conversation_id
            )
        )

        return task_id
```

### 3. SSE 流式端点

提供 SSE 实时流式输出（可选，用于前台实时显示）。

```python
# backend/agent_orchestrator/main.py

@app.get("/api/v1/chat/{conversation_id}/stream")
async def chat_stream_sse(conversation_id: str, task_id: str):
    """SSE 流式输出"""

    async def generate():
        # 获取消息记录
        message = await get_message_by_task(task_id)
        last_length = 0

        while True:
            # 查询最新内容
            message = await get_message_by_task(task_id)

            if message:
                # 输出增量内容
                new_content = message.content[last_length:]
                if new_content:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': new_content})}\n\n"
                    last_length = len(message.content)

                # 检查是否完成
                if message.status == "completed":
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break
                elif message.status == "failed":
                    yield f"data: {json.dumps({'type': 'error', 'error': message.error})}\n\n"
                    break

            await asyncio.sleep(0.1)  # 100ms 轮询间隔

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## 数据流设计

### 正常流程

```
1. 用户发送消息
   Flutter → POST /api/v1/chat

2. 创建任务
   FastAPI → INSERT tasks (status=pending)
   FastAPI → INSERT messages (role=user)
   FastAPI → 返回 {task_id, conversation_id}

3. 后台执行
   asyncio.create_task() → AgentSDKService.execute_agent_task()

4. 流式写入
   Agent SDK query() → 每个 TextBlock → UPDATE messages.content

5. 实时同步
   Supabase Realtime → 广播 messages 变更
   Flutter 订阅 → 实时更新 UI

6. 完成
   UPDATE messages (status=completed)
   UPDATE tasks (status=completed)
```

### 客户端离开后重新进入

```
1. 客户端重新打开

2. 加载对话历史
   Flutter → SELECT messages WHERE conversation_id = ?

3. 检查是否有进行中的任务
   Flutter → SELECT tasks WHERE conversation_id = ? AND status = 'running'

4. 订阅实时更新
   Flutter → supabase.from('messages').stream(...)

5. 自动接收后续输出
   Supabase Realtime → 推送新内容
```

## MCP 工具设计

### 研发效能分析官工具

```python
# backend/agent_sdk/mcp_tools/dev_efficiency.py

@tool("gerrit_query", "查询 Gerrit 代码审查数据", {
    "project": str,
    "days": int,
    "status": str  # "open" | "merged" | "abandoned"
})
async def gerrit_query_tool(args: dict) -> dict:
    """查询 Gerrit 代码审查数据"""
    # 调用 Gerrit API
    data = await fetch_gerrit_reviews(
        project=args["project"],
        days=args["days"],
        status=args.get("status", "merged")
    )
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool("efficiency_trend", "获取效能趋势数据", {
    "metric": str,  # "review_time" | "rework_rate" | "throughput"
    "weeks": int
})
async def efficiency_trend_tool(args: dict) -> dict:
    """获取效能指标趋势"""
    data = await calculate_efficiency_trend(
        metric=args["metric"],
        weeks=args["weeks"]
    )
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool("generate_report", "生成效能分析报告", {
    "report_type": str,  # "daily" | "weekly" | "monthly"
    "format": str  # "markdown" | "json"
})
async def generate_report_tool(args: dict) -> dict:
    """生成效能分析报告"""
    report = await build_efficiency_report(
        report_type=args["report_type"],
        format=args["format"]
    )
    return {"content": [{"type": "text", "text": report}]}
```

## 目录结构

```
backend/
├── agent_orchestrator/          # FastAPI 服务（保留）
│   ├── main.py                  # 主入口（新增 SSE 端点）
│   └── agent_manager.py         # 旧实现（废弃，保留兼容）
│
├── agent_sdk/                   # 新增：Agent SDK 服务
│   ├── __init__.py
│   ├── agent_sdk_service.py     # Agent SDK 封装
│   ├── task_manager.py          # 任务管理器
│   ├── config.py                # 配置
│   │
│   └── mcp_tools/               # MCP 自定义工具
│       ├── __init__.py
│       ├── dev_efficiency.py    # 研发效能工具
│       ├── gerrit_client.py     # Gerrit API 客户端
│       └── base.py              # 工具基类
│
├── agents/                      # Agent 工作目录（保留）
│   └── dev_efficiency_analyst/
│       ├── CLAUDE.md            # Agent 行为定义
│       └── ...
│
└── poc/                         # POC 验证代码（保留参考）
    └── ...
```

## 配置管理

```python
# backend/agent_sdk/config.py

from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class AgentSDKConfig:
    """Agent SDK 配置"""

    # API Gateway
    anthropic_base_url: str = os.getenv(
        "ANTHROPIC_BASE_URL",
        "https://llm-gateway.oppoer.me"
    )

    # Agent 工作目录
    agents_base_dir: Path = Path(__file__).parent.parent / "agents"

    # 默认模型
    default_model: str = "sonnet"

    # 消息更新频率（秒）
    message_update_interval: float = 0.5

    # 最大轮数
    max_turns: int = 20

    # 权限模式
    permission_mode: str = "acceptEdits"
```

## 错误处理

```python
class AgentSDKError(Exception):
    """Agent SDK 错误基类"""
    pass

class TaskExecutionError(AgentSDKError):
    """任务执行错误"""
    def __init__(self, task_id: str, message: str):
        self.task_id = task_id
        super().__init__(f"Task {task_id} failed: {message}")

class ToolExecutionError(AgentSDKError):
    """工具执行错误"""
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"Tool {tool_name} failed: {message}")
```

## 性能考虑

1. **消息批量更新**：避免每个字符都更新数据库，使用 500ms 间隔批量更新
2. **连接池**：复用 Supabase 连接
3. **任务队列**：后续可引入 Redis 队列，支持更大并发
4. **超时控制**：设置合理的任务超时时间

## 安全考虑

1. **工作目录隔离**：通过 `cwd` 参数限制 Agent 访问范围
2. **权限控制**：`allowed_tools` 限制可用工具
3. **输入验证**：校验用户输入，防止注入攻击
4. **敏感信息**：不在消息中暴露 API Key 等敏感信息
