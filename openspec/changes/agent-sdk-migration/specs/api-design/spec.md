# API 设计规范

## 概述

本文档描述 Agent SDK 迁移后的 API 端点设计，包括 REST API、SSE 流式端点和 Realtime 订阅接口。

## API 端点一览

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/chat` | 创建对话任务 |
| GET | `/api/v1/chat/{conversation_id}/stream` | SSE 流式输出 |
| GET | `/api/v1/chat/{conversation_id}/messages` | 获取历史消息 |
| GET | `/api/v1/tasks/{task_id}` | 获取任务状态 |
| POST | `/api/v1/tasks/{task_id}/cancel` | 取消任务 |

## 详细设计

### 1. 创建对话任务

**POST** `/api/v1/chat`

创建新的对话任务，立即返回 task_id，后台异步执行。

#### 请求

```json
{
  "conversation_id": "conv_123",  // 可选，不传则创建新对话
  "agent_role": "dev_efficiency_analyst",
  "message": "分析最近一周的代码审查效率"
}
```

#### 响应

```json
{
  "task_id": "task_abc123",
  "conversation_id": "conv_123",
  "status": "pending",
  "created_at": "2026-01-03T10:00:00Z"
}
```

#### 实现

```python
@app.post("/api/v1/chat")
async def create_chat_task(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    supabase: SupabaseClient = Depends(get_supabase)
):
    """创建对话任务"""

    # 1. 获取或创建对话
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # 2. 保存用户消息
    await supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": "user",
        "content": request.message,
        "status": "completed"
    }).execute()

    # 3. 创建任务记录
    task = await supabase.table("tasks").insert({
        "conversation_id": conversation_id,
        "agent_role": request.agent_role,
        "prompt": request.message,
        "status": "pending"
    }).execute()

    task_id = task.data[0]["id"]

    # 4. 异步执行任务（不阻塞响应）
    asyncio.create_task(
        agent_service.execute_agent_task(
            task_id=task_id,
            agent_role=request.agent_role,
            prompt=request.message,
            conversation_id=conversation_id
        )
    )

    return {
        "task_id": task_id,
        "conversation_id": conversation_id,
        "status": "pending",
        "created_at": task.data[0]["created_at"]
    }
```

### 2. SSE 流式输出

**GET** `/api/v1/chat/{conversation_id}/stream?task_id={task_id}`

实时流式输出 AI 响应内容。

#### SSE 事件格式

```
event: chunk
data: {"type": "chunk", "content": "这是增量内容"}

event: tool_use
data: {"type": "tool_use", "tool": "gerrit_query", "input": {...}}

event: tool_result
data: {"type": "tool_result", "tool": "gerrit_query", "output": {...}}

event: done
data: {"type": "done", "message_id": "msg_123"}

event: error
data: {"type": "error", "error": "任务执行失败", "code": "EXECUTION_ERROR"}
```

#### 实现

```python
@app.get("/api/v1/chat/{conversation_id}/stream")
async def chat_stream_sse(
    conversation_id: str,
    task_id: str,
    supabase: SupabaseClient = Depends(get_supabase)
):
    """SSE 流式输出"""

    async def generate():
        last_content_length = 0
        poll_interval = 0.1  # 100ms
        max_wait_time = 300  # 5 分钟超时
        waited_time = 0

        while waited_time < max_wait_time:
            # 查询任务状态
            task = await supabase.table("tasks").select("*").eq(
                "id", task_id
            ).single().execute()

            if not task.data:
                yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': 'Task not found'})}\n\n"
                break

            # 查询消息内容
            message = await supabase.table("messages").select("*").eq(
                "task_id", task_id
            ).eq("role", "assistant").single().execute()

            if message.data:
                content = message.data.get("content", "")
                new_content = content[last_content_length:]

                if new_content:
                    yield f"event: chunk\ndata: {json.dumps({'type': 'chunk', 'content': new_content})}\n\n"
                    last_content_length = len(content)

            # 检查任务状态
            status = task.data["status"]
            if status == "completed":
                yield f"event: done\ndata: {json.dumps({'type': 'done', 'message_id': message.data['id'] if message.data else None})}\n\n"
                break
            elif status == "failed":
                yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': task.data.get('error', 'Unknown error')})}\n\n"
                break

            await asyncio.sleep(poll_interval)
            waited_time += poll_interval

        if waited_time >= max_wait_time:
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': 'Timeout'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )
```

### 3. 获取历史消息

**GET** `/api/v1/chat/{conversation_id}/messages`

获取对话的历史消息列表。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| limit | int | 否 | 返回数量，默认 50 |
| before | string | 否 | 游标，获取此 ID 之前的消息 |

#### 响应

```json
{
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "分析最近一周的代码审查效率",
      "status": "completed",
      "created_at": "2026-01-03T10:00:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "根据分析...",
      "status": "completed",
      "tool_calls": [...],
      "created_at": "2026-01-03T10:00:05Z"
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

#### 实现

```python
@app.get("/api/v1/chat/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    supabase: SupabaseClient = Depends(get_supabase)
):
    """获取历史消息"""

    query = supabase.table("messages").select("*").eq(
        "conversation_id", conversation_id
    ).order("created_at", desc=True).limit(limit)

    if before:
        # 获取 before 消息的 created_at
        before_msg = await supabase.table("messages").select(
            "created_at"
        ).eq("id", before).single().execute()
        if before_msg.data:
            query = query.lt("created_at", before_msg.data["created_at"])

    result = await query.execute()
    messages = list(reversed(result.data))  # 按时间正序返回

    return {
        "messages": messages,
        "has_more": len(result.data) == limit,
        "next_cursor": messages[0]["id"] if messages else None
    }
```

### 4. 获取任务状态

**GET** `/api/v1/tasks/{task_id}`

查询任务的当前状态。

#### 响应

```json
{
  "id": "task_abc123",
  "conversation_id": "conv_123",
  "agent_role": "dev_efficiency_analyst",
  "status": "running",
  "progress": {
    "current_step": "analyzing",
    "tool_calls_count": 3
  },
  "created_at": "2026-01-03T10:00:00Z",
  "updated_at": "2026-01-03T10:00:15Z"
}
```

### 5. 取消任务

**POST** `/api/v1/tasks/{task_id}/cancel`

取消正在执行的任务。

#### 响应

```json
{
  "id": "task_abc123",
  "status": "cancelled",
  "cancelled_at": "2026-01-03T10:01:00Z"
}
```

## 错误响应

### 错误格式

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID task_xxx not found",
    "details": {}
  }
}
```

### 错误码

| 错误码 | HTTP 状态码 | 描述 |
|--------|-------------|------|
| INVALID_REQUEST | 400 | 请求参数无效 |
| UNAUTHORIZED | 401 | 未授权 |
| TASK_NOT_FOUND | 404 | 任务不存在 |
| CONVERSATION_NOT_FOUND | 404 | 对话不存在 |
| TASK_ALREADY_COMPLETED | 409 | 任务已完成，无法取消 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 内部错误 |

## 认证

所有 API 端点需要在 Header 中携带认证信息：

```
Authorization: Bearer <access_token>
```

Token 来自 Supabase Auth，通过 Flutter App 登录获取。

## 速率限制

| 端点 | 限制 |
|------|------|
| POST /api/v1/chat | 10 次/分钟/用户 |
| GET /api/v1/chat/*/stream | 5 并发连接/用户 |
| GET /api/v1/chat/*/messages | 60 次/分钟/用户 |

## Flutter 客户端使用示例

```dart
// 1. 创建任务
final response = await dio.post('/api/v1/chat', data: {
  'conversation_id': conversationId,
  'agent_role': 'dev_efficiency_analyst',
  'message': userMessage,
});
final taskId = response.data['task_id'];

// 2. 订阅 SSE 流
final sseClient = SSEClient(
  '/api/v1/chat/$conversationId/stream?task_id=$taskId'
);

sseClient.onMessage.listen((event) {
  final data = jsonDecode(event.data);
  switch (data['type']) {
    case 'chunk':
      // 追加内容到 UI
      appendContent(data['content']);
      break;
    case 'done':
      // 完成
      sseClient.close();
      break;
    case 'error':
      // 错误处理
      showError(data['error']);
      break;
  }
});

// 3. 同时订阅 Supabase Realtime（用于断线恢复）
supabase
  .from('messages')
  .stream(primaryKey: ['id'])
  .eq('conversation_id', conversationId)
  .listen((messages) {
    // 更新本地消息列表
    updateMessages(messages);
  });
```
