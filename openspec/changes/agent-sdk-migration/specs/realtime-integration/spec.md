# Realtime 集成规范

## 概述

本文档描述 Supabase Realtime 的集成方案，实现客户端离开后重新进入时能够自动恢复消息流。

## Supabase Realtime 配置

### 1. 启用 Realtime

在 Supabase Dashboard 或通过 SQL 启用表的 Realtime：

```sql
-- 启用 messages 表的 Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE messages;

-- 启用 tasks 表的 Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE tasks;
```

### 2. Realtime 权限

确保 RLS 策略允许用户订阅自己的数据：

```sql
-- messages 表已有的 RLS 策略应该允许 SELECT
-- 确保策略如下：
CREATE POLICY "Users can view own messages" ON messages
    FOR SELECT
    USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );
```

## 客户端集成

### Flutter 订阅实现

```dart
import 'package:supabase_flutter/supabase_flutter.dart';

class RealtimeService {
  final SupabaseClient _supabase;
  RealtimeChannel? _messagesChannel;
  RealtimeChannel? _tasksChannel;

  RealtimeService(this._supabase);

  /// 订阅对话消息
  void subscribeToConversation({
    required String conversationId,
    required Function(Map<String, dynamic>) onMessageInsert,
    required Function(Map<String, dynamic>) onMessageUpdate,
  }) {
    _messagesChannel = _supabase
        .channel('messages:$conversationId')
        .onPostgresChanges(
          event: PostgresChangeEvent.insert,
          schema: 'public',
          table: 'messages',
          filter: PostgresChangeFilter(
            type: PostgresChangeFilterType.eq,
            column: 'conversation_id',
            value: conversationId,
          ),
          callback: (payload) => onMessageInsert(payload.newRecord),
        )
        .onPostgresChanges(
          event: PostgresChangeEvent.update,
          schema: 'public',
          table: 'messages',
          filter: PostgresChangeFilter(
            type: PostgresChangeFilterType.eq,
            column: 'conversation_id',
            value: conversationId,
          ),
          callback: (payload) => onMessageUpdate(payload.newRecord),
        )
        .subscribe();
  }

  /// 订阅任务状态
  void subscribeToTask({
    required String taskId,
    required Function(Map<String, dynamic>) onTaskUpdate,
  }) {
    _tasksChannel = _supabase
        .channel('task:$taskId')
        .onPostgresChanges(
          event: PostgresChangeEvent.update,
          schema: 'public',
          table: 'tasks',
          filter: PostgresChangeFilter(
            type: PostgresChangeFilterType.eq,
            column: 'id',
            value: taskId,
          ),
          callback: (payload) => onTaskUpdate(payload.newRecord),
        )
        .subscribe();
  }

  /// 取消订阅
  Future<void> unsubscribe() async {
    await _messagesChannel?.unsubscribe();
    await _tasksChannel?.unsubscribe();
  }
}
```

### 消息同步状态机

```dart
enum SyncState {
  disconnected,  // 未连接
  syncing,       // 同步中
  synced,        // 已同步
  error,         // 错误
}

class ConversationSyncManager {
  SyncState _state = SyncState.disconnected;
  String? _lastMessageId;
  final List<Message> _localMessages = [];

  /// 重新连接时同步
  Future<void> reconnect(String conversationId) async {
    _state = SyncState.syncing;

    // 1. 获取本地最后一条消息的时间戳
    final lastLocalMessage = _localMessages.lastOrNull;
    final lastTimestamp = lastLocalMessage?.createdAt;

    // 2. 从数据库获取新消息
    final query = supabase
        .from('messages')
        .select()
        .eq('conversation_id', conversationId)
        .order('created_at');

    if (lastTimestamp != null) {
      query.gt('created_at', lastTimestamp.toIso8601String());
    }

    final newMessages = await query;

    // 3. 合并消息
    for (final msg in newMessages) {
      final existingIndex = _localMessages.indexWhere((m) => m.id == msg['id']);
      if (existingIndex >= 0) {
        // 更新现有消息
        _localMessages[existingIndex] = Message.fromJson(msg);
      } else {
        // 添加新消息
        _localMessages.add(Message.fromJson(msg));
      }
    }

    // 4. 检查是否有进行中的任务
    final runningTask = await supabase
        .from('tasks')
        .select()
        .eq('conversation_id', conversationId)
        .eq('status', 'running')
        .maybeSingle();

    if (runningTask != null) {
      // 订阅进行中任务的更新
      _subscribeToTask(runningTask['id']);
    }

    _state = SyncState.synced;
  }
}
```

## 服务端实现

### 消息写入触发 Realtime

后端在写入消息时，Supabase 会自动广播变更：

```python
# backend/agent_sdk/agent_sdk_service.py

class AgentSDKService:
    async def execute_agent_task(
        self,
        task_id: str,
        agent_role: str,
        prompt: str,
        conversation_id: str
    ):
        # 创建 AI 消息记录
        message_result = await self.supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "task_id": task_id,
            "role": "assistant",
            "content": "",
            "status": "streaming"
        }).execute()

        message_id = message_result.data[0]["id"]

        # 更新任务状态 → 触发 Realtime
        await self.supabase.table("tasks").update({
            "status": "running",
            "started_at": datetime.utcnow().isoformat()
        }).eq("id", task_id).execute()

        # 流式执行
        content_buffer = ""
        last_update_time = time.time()
        UPDATE_INTERVAL = 0.5  # 500ms

        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        content_buffer += block.text

                        # 批量更新（触发 Realtime）
                        if time.time() - last_update_time > UPDATE_INTERVAL:
                            await self.supabase.table("messages").update({
                                "content": content_buffer
                            }).eq("id", message_id).execute()
                            last_update_time = time.time()

        # 最终更新
        await self.supabase.table("messages").update({
            "content": content_buffer,
            "status": "completed"
        }).eq("id", message_id).execute()

        await self.supabase.table("tasks").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", task_id).execute()
```

## 数据流时序图

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Flutter │     │ FastAPI │     │Supabase │     │Realtime │
└────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
     │               │               │               │
     │ POST /chat    │               │               │
     │──────────────>│               │               │
     │               │ INSERT task   │               │
     │               │──────────────>│               │
     │               │               │               │
     │   {task_id}   │               │               │
     │<──────────────│               │               │
     │               │               │               │
     │ subscribe(messages)           │               │
     │───────────────────────────────────────────────>
     │               │               │               │
     │               │ asyncio.create_task()         │
     │               │─ ─ ─ ─ ─ ─ ─ ─│               │
     │               │               │               │
     │               │ (background)  │               │
     │               │ UPDATE message│               │
     │               │──────────────>│  broadcast    │
     │               │               │──────────────>│
     │               │               │               │
     │        Realtime: message updated              │
     │<──────────────────────────────────────────────│
     │               │               │               │
     │  [用户离开]   │               │               │
     │ ════════════ │               │               │
     │               │               │               │
     │               │ UPDATE message│               │
     │               │──────────────>│  broadcast    │
     │               │               │──────────────>│
     │               │               │    (no sub)   │
     │               │               │               │
     │  [用户返回]   │               │               │
     │ ════════════ │               │               │
     │               │               │               │
     │ GET /messages │               │               │
     │──────────────>│               │               │
     │               │ SELECT        │               │
     │               │──────────────>│               │
     │   [历史消息]  │               │               │
     │<──────────────│               │               │
     │               │               │               │
     │ subscribe(messages)           │               │
     │───────────────────────────────────────────────>
     │               │               │               │
     │        Realtime: message updated              │
     │<──────────────────────────────────────────────│
     │               │               │               │
```

## 断线恢复策略

### 1. 客户端检测断线

```dart
class ConnectionMonitor {
  Timer? _heartbeatTimer;
  bool _isConnected = true;

  void startMonitoring() {
    _heartbeatTimer = Timer.periodic(Duration(seconds: 30), (_) async {
      try {
        // 检查连接状态
        final status = supabase.realtime.connState;
        _isConnected = status == SocketStates.open;

        if (!_isConnected) {
          await _handleDisconnect();
        }
      } catch (e) {
        _isConnected = false;
        await _handleDisconnect();
      }
    });
  }

  Future<void> _handleDisconnect() async {
    // 尝试重新连接
    await supabase.realtime.connect();

    // 重新同步数据
    await syncManager.reconnect(currentConversationId);

    // 重新订阅
    realtimeService.subscribeToConversation(
      conversationId: currentConversationId,
      onMessageInsert: handleNewMessage,
      onMessageUpdate: handleMessageUpdate,
    );
  }
}
```

### 2. 增量同步

```dart
Future<void> incrementalSync(String conversationId, DateTime lastSyncTime) async {
  // 获取增量更新
  final updates = await supabase
      .from('messages')
      .select()
      .eq('conversation_id', conversationId)
      .gt('updated_at', lastSyncTime.toIso8601String())
      .order('updated_at');

  for (final update in updates) {
    final localMessage = localMessages.firstWhere(
      (m) => m.id == update['id'],
      orElse: () => null,
    );

    if (localMessage == null) {
      // 新消息
      localMessages.add(Message.fromJson(update));
    } else if (DateTime.parse(update['updated_at']).isAfter(localMessage.updatedAt)) {
      // 更新本地消息
      final index = localMessages.indexOf(localMessage);
      localMessages[index] = Message.fromJson(update);
    }
  }
}
```

## 性能优化

### 1. 消息更新节流

后端避免过于频繁的数据库更新：

```python
class ThrottledMessageUpdater:
    def __init__(self, supabase, message_id: str, interval: float = 0.5):
        self.supabase = supabase
        self.message_id = message_id
        self.interval = interval
        self.content = ""
        self.pending_update = False
        self.last_update = 0

    async def append(self, text: str):
        self.content += text

        current_time = time.time()
        if current_time - self.last_update >= self.interval:
            await self._flush()
        elif not self.pending_update:
            self.pending_update = True
            asyncio.create_task(self._delayed_flush())

    async def _flush(self):
        await self.supabase.table("messages").update({
            "content": self.content
        }).eq("id", self.message_id).execute()
        self.last_update = time.time()
        self.pending_update = False

    async def _delayed_flush(self):
        await asyncio.sleep(self.interval)
        if self.pending_update:
            await self._flush()
```

### 2. 客户端消息合并

```dart
class MessageMerger {
  final _pendingUpdates = <String, Map<String, dynamic>>{};
  Timer? _mergeTimer;

  void onRealtimeUpdate(Map<String, dynamic> payload) {
    final messageId = payload['id'] as String;
    _pendingUpdates[messageId] = payload;

    // 延迟合并，避免频繁 UI 更新
    _mergeTimer?.cancel();
    _mergeTimer = Timer(Duration(milliseconds: 100), _applyUpdates);
  }

  void _applyUpdates() {
    for (final entry in _pendingUpdates.entries) {
      // 批量应用更新
      updateMessageInUI(entry.key, entry.value);
    }
    _pendingUpdates.clear();
  }
}
```

### 3. Realtime Channel 优化

```dart
// 使用单一 channel 减少连接数
final channel = supabase.channel('conversation:$conversationId')
    .onPostgresChanges(
      event: PostgresChangeEvent.all,
      schema: 'public',
      table: 'messages',
      filter: PostgresChangeFilter(
        type: PostgresChangeFilterType.eq,
        column: 'conversation_id',
        value: conversationId,
      ),
      callback: handleMessageChange,
    )
    .onPostgresChanges(
      event: PostgresChangeEvent.update,
      schema: 'public',
      table: 'tasks',
      filter: PostgresChangeFilter(
        type: PostgresChangeFilterType.eq,
        column: 'conversation_id',
        value: conversationId,
      ),
      callback: handleTaskChange,
    )
    .subscribe();
```

## 错误处理

### 连接错误

```dart
supabase.realtime.onError((error) {
  print('Realtime error: $error');

  // 指数退避重连
  _scheduleReconnect();
});

int _retryCount = 0;
void _scheduleReconnect() {
  final delay = Duration(seconds: pow(2, _retryCount).toInt().clamp(1, 60));
  _retryCount++;

  Future.delayed(delay, () async {
    try {
      await supabase.realtime.connect();
      _retryCount = 0;  // 重置
    } catch (e) {
      _scheduleReconnect();
    }
  });
}
```

### 数据冲突

```dart
void handleMessageUpdate(Map<String, dynamic> payload) {
  final messageId = payload['id'];
  final serverUpdatedAt = DateTime.parse(payload['updated_at']);

  final localMessage = localMessages.firstWhere((m) => m.id == messageId);
  if (localMessage != null && serverUpdatedAt.isAfter(localMessage.updatedAt)) {
    // 服务端数据较新，使用服务端版本
    updateLocalMessage(Message.fromJson(payload));
  }
}
```

## 测试场景

1. **正常流程**：发送消息 → 实时接收 AI 响应
2. **断线恢复**：发送消息 → 断开连接 → 重新连接 → 自动获取完整响应
3. **多端同步**：手机发送 → 平板实时接收
4. **长任务**：发送复杂任务 → 关闭 App → 重新打开 → 看到完整结果
5. **错误处理**：网络抖动 → 自动重连 → 数据不丢失
