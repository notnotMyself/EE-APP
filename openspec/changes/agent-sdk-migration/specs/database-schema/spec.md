# 数据库设计规范

## 概述

本文档描述支持 Agent SDK 迁移和实时通信架构所需的数据库表设计。

## 表结构

### 1. tasks 表

存储 Agent 任务的状态和元数据。

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    agent_role VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- 索引
CREATE INDEX idx_tasks_conversation_id ON tasks(conversation_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- 状态约束
ALTER TABLE tasks ADD CONSTRAINT check_task_status
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));

-- 自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2. messages 表（扩展）

在现有 messages 表基础上增加字段。

```sql
-- 新增字段
ALTER TABLE messages ADD COLUMN IF NOT EXISTS task_id UUID REFERENCES tasks(id);
ALTER TABLE messages ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'completed';
ALTER TABLE messages ADD COLUMN IF NOT EXISTS tool_calls JSONB DEFAULT '[]';
ALTER TABLE messages ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- 索引
CREATE INDEX IF NOT EXISTS idx_messages_task_id ON messages(task_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);

-- 状态约束
ALTER TABLE messages ADD CONSTRAINT check_message_status
    CHECK (status IN ('streaming', 'completed', 'failed'));
```

### 3. tool_executions 表

记录工具调用的详细信息（可选，用于调试和审计）。

```sql
CREATE TABLE tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    tool_name VARCHAR(100) NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 索引
CREATE INDEX idx_tool_executions_task_id ON tool_executions(task_id);
CREATE INDEX idx_tool_executions_tool_name ON tool_executions(tool_name);
```

## 表关系图

```
┌─────────────────┐       ┌─────────────────┐
│  conversations  │       │     users       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │───────│ ...             │
│ title           │       └─────────────────┘
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         ↓
┌─────────────────┐       ┌─────────────────┐
│     tasks       │       │    messages     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ conversation_id │       │ conversation_id │
│ agent_role      │       │ task_id (FK)    │←──┐
│ prompt          │       │ role            │   │
│ status          │───────│ content         │   │
│ error           │ 1:1   │ status          │   │
│ metadata        │       │ tool_calls      │   │
│ created_at      │       │ created_at      │   │
└────────┬────────┘       └─────────────────┘   │
         │                                       │
         │ 1:N                                   │
         ↓                                       │
┌─────────────────┐                             │
│ tool_executions │                             │
├─────────────────┤                             │
│ id (PK)         │                             │
│ task_id (FK)    │─────────────────────────────┘
│ message_id (FK) │
│ tool_name       │
│ input           │
│ output          │
│ status          │
│ duration_ms     │
│ created_at      │
└─────────────────┘
```

## 数据流

### 创建任务流程

```sql
-- 1. 插入用户消息
INSERT INTO messages (conversation_id, role, content, status)
VALUES ($conversation_id, 'user', $user_message, 'completed');

-- 2. 创建任务
INSERT INTO tasks (conversation_id, agent_role, prompt, status)
VALUES ($conversation_id, $agent_role, $user_message, 'pending')
RETURNING id;

-- 3. 创建 AI 消息占位
INSERT INTO messages (conversation_id, task_id, role, content, status)
VALUES ($conversation_id, $task_id, 'assistant', '', 'streaming')
RETURNING id;
```

### 流式更新流程

```sql
-- 任务开始
UPDATE tasks
SET status = 'running', started_at = NOW()
WHERE id = $task_id;

-- 流式更新消息内容（高频操作，需要优化）
UPDATE messages
SET content = $new_content
WHERE id = $message_id;

-- 记录工具调用
INSERT INTO tool_executions (task_id, message_id, tool_name, input, status)
VALUES ($task_id, $message_id, $tool_name, $input, 'running');

-- 工具调用完成
UPDATE tool_executions
SET output = $output, status = 'completed', duration_ms = $duration, completed_at = NOW()
WHERE id = $tool_execution_id;

-- 任务完成
UPDATE tasks
SET status = 'completed', completed_at = NOW()
WHERE id = $task_id;

UPDATE messages
SET status = 'completed'
WHERE id = $message_id;
```

## RLS (Row Level Security) 策略

```sql
-- 启用 RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_executions ENABLE ROW LEVEL SECURITY;

-- tasks 策略：用户只能访问自己对话中的任务
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT
    USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create tasks" ON tasks
    FOR INSERT
    WITH CHECK (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

-- tool_executions 策略
CREATE POLICY "Users can view own tool executions" ON tool_executions
    FOR SELECT
    USING (
        task_id IN (
            SELECT t.id FROM tasks t
            JOIN conversations c ON t.conversation_id = c.id
            WHERE c.user_id = auth.uid()
        )
    );
```

## 性能优化

### 1. 消息内容更新批量化

避免每个字符都更新数据库，使用内存缓冲：

```python
class MessageBuffer:
    def __init__(self, message_id: str, flush_interval: float = 0.5):
        self.message_id = message_id
        self.content = ""
        self.flush_interval = flush_interval
        self.last_flush = time.time()

    async def append(self, text: str, supabase):
        self.content += text

        # 每 500ms 或内容超过 1000 字符时刷新
        if (time.time() - self.last_flush > self.flush_interval or
            len(self.content) - self.last_flush_length > 1000):
            await self._flush(supabase)

    async def _flush(self, supabase):
        await supabase.table("messages").update({
            "content": self.content
        }).eq("id", self.message_id).execute()
        self.last_flush = time.time()
        self.last_flush_length = len(self.content)
```

### 2. 索引优化

```sql
-- 复合索引：快速查询对话中的最新任务
CREATE INDEX idx_tasks_conv_created
    ON tasks(conversation_id, created_at DESC);

-- 部分索引：只索引活跃任务
CREATE INDEX idx_tasks_running
    ON tasks(id)
    WHERE status IN ('pending', 'running');
```

### 3. 分区表（未来扩展）

```sql
-- 按月分区 messages 表
CREATE TABLE messages_partitioned (
    LIKE messages INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE messages_2026_01 PARTITION OF messages_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

## 迁移脚本

```sql
-- Migration: 20260103_agent_sdk_tables.sql

BEGIN;

-- 创建 tasks 表
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    agent_role VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    CONSTRAINT check_task_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tasks_conversation_id ON tasks(conversation_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- 扩展 messages 表
ALTER TABLE messages ADD COLUMN IF NOT EXISTS task_id UUID REFERENCES tasks(id);
ALTER TABLE messages ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'completed';
ALTER TABLE messages ADD COLUMN IF NOT EXISTS tool_calls JSONB DEFAULT '[]';

CREATE INDEX IF NOT EXISTS idx_messages_task_id ON messages(task_id);

-- 创建 tool_executions 表
CREATE TABLE IF NOT EXISTS tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    tool_name VARCHAR(100) NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tool_executions_task_id ON tool_executions(task_id);

-- 创建更新触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 启用 RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_executions ENABLE ROW LEVEL SECURITY;

-- RLS 策略
DROP POLICY IF EXISTS "Users can view own tasks" ON tasks;
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT
    USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can create tasks" ON tasks;
CREATE POLICY "Users can create tasks" ON tasks
    FOR INSERT
    WITH CHECK (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

COMMIT;
```

## 回滚脚本

```sql
-- Rollback: 20260103_agent_sdk_tables.sql

BEGIN;

DROP TABLE IF EXISTS tool_executions;
DROP TABLE IF EXISTS tasks CASCADE;

ALTER TABLE messages DROP COLUMN IF EXISTS task_id;
ALTER TABLE messages DROP COLUMN IF EXISTS status;
ALTER TABLE messages DROP COLUMN IF EXISTS tool_calls;

DROP FUNCTION IF EXISTS update_updated_at_column;

COMMIT;
```
