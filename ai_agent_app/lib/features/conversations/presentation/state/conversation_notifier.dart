import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../../../core/config/timeout_config.dart';
import '../../data/conversation_repository.dart';
import '../../data/websocket_client.dart';
import '../../domain/models/conversation.dart';
import '../controllers/conversation_controller.dart';
import 'conversation_state.dart';

/// 对话状态Notifier
///
/// 管理对话页面的状态，包括：
/// - 消息列表
/// - 流式内容缓冲和批量更新（参考 claudecodeui 的节流策略）
/// - WebSocket连接状态
/// - 断线恢复机制
class ConversationNotifier extends StateNotifier<ConversationViewState> {
  final String conversationId;
  final ConversationRepository _repository;

  ConversationWebSocketClient? _wsClient;
  Timer? _flushTimer;
  final List<String> _contentBuffer = [];

  // 流式状态跟踪（用于断线恢复）
  bool _isStreaming = false;
  DateTime? _streamingStartTime;

  ConversationNotifier({
    required this.conversationId,
    required ConversationRepository repository,
  })  : _repository = repository,
        super(ConversationViewState.initial(conversationId));

  /// 初始化：加载消息并连接WebSocket
  Future<void> initialize() async {
    state = state.copyWith(isLoading: true);

    try {
      await _loadMessages();
      await _connectWebSocket();
    } catch (e) {
      state = state.copyWith(
        error: e.toString(),
        isLoading: false,
      );
    }
  }

  /// 加载历史消息
  Future<void> _loadMessages() async {
    try {
      final messages = await _repository.getMessages(conversationId);
      state = state.copyWith(
        messages: messages,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        error: '加载消息失败: $e',
        isLoading: false,
      );
    }
  }

  /// 连接WebSocket
  Future<void> _connectWebSocket() async {
    state = state.copyWith(
      connectionState: const WsConnectionState.connecting(),
    );

    // 避免重复创建 WebSocketClient（provider 非 autoDispose 或页面重复初始化时会导致多连接）
    if (_wsClient != null) {
      await _wsClient!.connect();
      return;
    }

    _wsClient = ConversationWebSocketClient(
      baseUrl: _repository.baseUrl,
      conversationId: conversationId,
      getToken: () async {
        final session = Supabase.instance.client.auth.currentSession;
        return session?.accessToken;
      },
      onMessage: _handleMessage,
      onConnected: _handleConnected,
      onDisconnected: _handleDisconnected,
      onError: _handleError,
    );

    await _wsClient!.connect();
  }

  void _handleConnected() {
    final wasStreaming = _isStreaming;

    state = state.copyWith(
      connectionState: const WsConnectionState.connected(),
    );

    // 如果之前在流式传输时断线，重新加载消息以获取完整内容
    // 因为后端可能已经保存了完整的回复
    if (wasStreaming) {
      _isStreaming = false;
      _streamingStartTime = null;
      _reloadMessagesAfterReconnect();
    }
  }

  /// 重连后重新加载消息（恢复可能丢失的内容）
  Future<void> _reloadMessagesAfterReconnect() async {
    try {
      // 等待一小段时间，让后端有机会保存消息
      await Future.delayed(const Duration(milliseconds: 500));

      final messages = await _repository.getMessages(conversationId);

      // 检查是否有新的 assistant 消息（后端可能已经保存了完整回复）
      final currentMessages = state.messages;
      final lastCurrentMsg = currentMessages.isNotEmpty ? currentMessages.last : null;
      final lastNewMsg = messages.isNotEmpty ? messages.last : null;

      // 如果最新消息是 assistant 且内容更长，说明后端有更完整的版本
      if (lastNewMsg != null &&
          lastNewMsg.role == 'assistant' &&
          (lastCurrentMsg == null ||
              lastCurrentMsg.role != 'assistant' ||
              lastNewMsg.content.length > lastCurrentMsg.content.length)) {
        state = state.copyWith(
          messages: messages,
          streamingState: const StreamingState.completed(),
        );
      }
    } catch (e) {
      // 重新加载失败不影响正常使用
    }
  }

  void _handleDisconnected() {
    // 断线时保存当前流式内容（避免丢失）
    if (_isStreaming && _contentBuffer.isNotEmpty) {
      _flushTimer?.cancel();
      _flushTimer = null;
      _flushBuffer();
    }

    state = state.copyWith(
      connectionState: const WsConnectionState.disconnected(),
    );

    // 如果正在流式传输时断线，标记为错误状态
    if (_isStreaming) {
      state = state.copyWith(
        streamingState: const StreamingState.error('连接断开，正在重连...'),
      );
    }
  }

  void _handleError(String error) {
    state = state.copyWith(error: error);
  }

  void _handleMessage(WSMessage message) {
    switch (message.type) {
      case WSMessageType.textChunk:
        _appendStreamingContent(message.content ?? '');
        break;

      case WSMessageType.done:
        _finalizeMessage();
        // 重置工具状态
        state = state.copyWith(toolState: const ToolExecutionState.idle());
        break;

      case WSMessageType.error:
        state = state.copyWith(
          streamingState: StreamingState.error(message.content ?? '未知错误'),
          toolState: const ToolExecutionState.idle(),
        );
        break;

      case WSMessageType.taskStart:
      case WSMessageType.taskProgress:
      case WSMessageType.briefingCreated:
      case WSMessageType.taskComplete:
        // 任务相关事件，可以用来更新UI
        break;

      case WSMessageType.toolUse:
        // 工具开始执行 - 显示进度状态（参考 claudecodeui）
        _handleToolUse(message);
        break;

      case WSMessageType.toolProgress:
        // 工具执行进度更新
        _handleToolProgress(message);
        break;

      case WSMessageType.toolResult:
        // 工具执行完成 - 更新结果
        _handleToolResult(message);
        break;

      default:
        break;
    }
  }

  /// 处理工具调用开始事件
  void _handleToolUse(WSMessage message) {
    final metadata = message.metadata ?? {};
    final toolName = metadata['tool_name'] as String? ?? 'Unknown';
    final toolId = metadata['tool_id'] as String? ?? '';
    final toolInput = metadata['tool_input'] as Map<String, dynamic>?;

    // 提取文件路径（如果有）
    String? filePath;
    String statusMessage = '正在执行...';

    if (toolName == 'Write' && toolInput != null) {
      filePath = toolInput['file_path'] as String?;
      if (filePath != null) {
        final fileName = filePath.split('/').last;
        statusMessage = '正在生成: $fileName';
        _appendStreamingContent('\n📝 *$statusMessage*\n');
      }
    } else if (toolName == 'Bash') {
      final command = toolInput?['command'] as String?;
      if (command != null && command.contains('skill')) {
        statusMessage = '正在执行数据分析...';
        _appendStreamingContent('\n⚙️ *$statusMessage*\n');
      }
    }

    // 更新状态显示工具正在执行
    state = state.copyWith(
      toolState: ToolExecutionState.executing(
        toolName: toolName,
        toolId: toolId,
        toolInput: toolInput,
        startedAt: DateTime.now(),
        progress: 0.0,
        status: 'executing',
        filePath: filePath,
        statusMessage: statusMessage,
      ),
    );
  }

  /// 处理工具执行进度事件（新增）
  void _handleToolProgress(WSMessage message) {
    final metadata = message.metadata ?? {};
    final toolName = metadata['tool_name'] as String? ?? 'Unknown';
    final toolId = metadata['tool_id'] as String? ?? '';
    final progress = (metadata['progress'] as num?)?.toDouble() ?? 0.0;
    final status = metadata['status'] as String? ?? 'executing';
    final filePath = metadata['file_path'] as String?;
    final statusMessage = message.content;

    // 只有当前正在执行的工具才更新进度
    final currentState = state.toolState;
    if (currentState is ToolExecutionStateExecuting && currentState.toolId == toolId) {
      state = state.copyWith(
        toolState: ToolExecutionState.executing(
          toolName: toolName,
          toolId: toolId,
          toolInput: currentState.toolInput,
          startedAt: currentState.startedAt,
          progress: progress,
          status: status,
          filePath: filePath ?? currentState.filePath,
          statusMessage: statusMessage ?? currentState.statusMessage,
        ),
      );
    }
  }

  /// 处理工具执行结果事件
  void _handleToolResult(WSMessage message) {
    final metadata = message.metadata ?? {};
    final toolId = metadata['tool_id'] as String? ?? '';
    final result = metadata['result'];
    final isError = metadata['is_error'] as bool? ?? false;

    // 从当前执行状态获取工具名称
    final currentToolName = state.toolState.maybeMap(
      executing: (s) => s.toolName,
      orElse: () => 'Unknown',
    );

    // 更新状态为完成
    state = state.copyWith(
      toolState: ToolExecutionState.completed(
        toolName: currentToolName,
        toolId: toolId,
        result: result?.toString(),
        isError: isError,
      ),
    );

    // 短暂延迟后重置工具状态（让用户看到完成状态）
    Future.delayed(const Duration(milliseconds: 500), () {
      // StateNotifier 通过检查是否还能更新 state 来判断是否存活
      try {
        state = state.copyWith(
          toolState: const ToolExecutionState.idle(),
        );
      } catch (_) {
        // Notifier 已被销毁，忽略
      }
    });
  }

  /// 追加流式内容到缓冲区（批量更新优化）
  ///
  /// 参考 claudecodeui 的节流策略：
  /// - 只有在没有 timer 时才创建 timer
  /// - 避免连续快速 chunk 导致 timer 被反复取消而永不触发
  void _appendStreamingContent(String content) {
    _contentBuffer.add(content);

    // 标记流式状态开始
    if (!_isStreaming) {
      _isStreaming = true;
      _streamingStartTime = DateTime.now();
    }

    // 关键修复：只有在没有 timer 时才创建
    // 这确保了即使 chunk 快速连续到达，也会在 50ms 后触发 flush
    if (_flushTimer == null) {
      _flushTimer = Timer(TimeoutConfig.streamingUpdateInterval, () {
        _flushBuffer();
        _flushTimer = null;
      });
    }

    // 额外检查：如果缓冲区过大（超过 100 个 chunk），立即刷新
    if (_contentBuffer.length > 100) {
      _flushTimer?.cancel();
      _flushTimer = null;
      _flushBuffer();
    }
  }

  /// 刷新缓冲区到 UI
  void _flushBuffer() {
    if (_contentBuffer.isEmpty) return;

    final buffered = _contentBuffer.join();
    _contentBuffer.clear();

    state = state.copyWith(
      streamingState: state.streamingState.maybeMap(
        streaming: (s) => StreamingState.streaming(
          content: s.content + buffered,
          startedAt: s.startedAt,
        ),
        orElse: () => StreamingState.streaming(
          content: buffered,
          startedAt: _streamingStartTime ?? DateTime.now(),
        ),
      ),
    );
  }

  /// 完成消息
  void _finalizeMessage() {
    // 先刷新所有缓冲
    _flushTimer?.cancel();
    _flushTimer = null;
    _flushBuffer();

    // 重置流式状态
    _isStreaming = false;
    _streamingStartTime = null;

    // 将流式内容转换为消息
    final streamingContent = state.streamingState.maybeMap(
      streaming: (s) => s.content,
      orElse: () => '',
    );

    if (streamingContent.isNotEmpty) {
      final newMessage = Message(
        id: 'msg-${DateTime.now().millisecondsSinceEpoch}',
        conversationId: conversationId,
        role: 'assistant',
        content: streamingContent,
        createdAt: DateTime.now(),
      );

      state = state.copyWith(
        messages: [...state.messages, newMessage],
        streamingState: const StreamingState.completed(),
      );
    } else {
      state = state.copyWith(
        streamingState: const StreamingState.completed(),
      );
    }
  }

  /// 发送消息
  Future<void> sendMessage(String content) async {
    await sendMessageWithAttachments(content, null);
  }

  /// 发送带附件的消息
  Future<void> sendMessageWithAttachments(String content, List<Map<String, dynamic>>? attachments) async {
    if (content.trim().isEmpty && (attachments == null || attachments.isEmpty)) return;

    // 添加用户消息到列表
    final userMessage = Message(
      id: 'msg-user-${DateTime.now().millisecondsSinceEpoch}',
      conversationId: conversationId,
      role: 'user',
      content: content.trim(),
      createdAt: DateTime.now(),
    );

    // 立即设置为 waiting 状态，让用户知道系统正在处理
    state = state.copyWith(
      messages: [...state.messages, userMessage],
      streamingState: StreamingState.waiting(startedAt: DateTime.now()),
    );

    // 检查WebSocket连接
    if (_wsClient == null || !_wsClient!.isConnected) {
      // 如果WebSocket未连接，尝试重连或使用SSE fallback
      if (_wsClient != null) {
        await _wsClient!.connect();
      }

      if (_wsClient == null || !_wsClient!.isConnected) {
        // 使用SSE fallback（不支持附件）
        await _sendViaSse(content.trim());
        return;
      }
    }

    // 通过WebSocket发送
    if (attachments != null && attachments.isNotEmpty) {
      _wsClient!.sendMessageWithAttachments(content.trim(), attachments);
    } else {
      _wsClient!.sendMessage(content.trim());
    }
  }

  /// 使用SSE发送消息（fallback）
  Future<void> _sendViaSse(String content) async {
    try {
      String fullResponse = '';

      await for (final chunk in _repository.sendMessageStream(
        conversationId: conversationId,
        newMessage: content,
      )) {
        fullResponse += chunk;
        state = state.copyWith(
          streamingState: StreamingState.streaming(
            content: fullResponse,
            startedAt: DateTime.now(),
          ),
        );
      }

      _finalizeMessage();
    } catch (e) {
      state = state.copyWith(
        streamingState: StreamingState.error(e.toString()),
      );
    }
  }

  /// 重置流式状态
  void resetStreaming() {
    state = state.copyWith(
      streamingState: const StreamingState.idle(),
    );
  }

  @override
  void dispose() {
    _flushTimer?.cancel();
    _wsClient?.dispose();
    super.dispose();
  }
}

/// 对话状态Provider
final conversationNotifierProvider = StateNotifierProvider.family<
    ConversationNotifier, ConversationViewState, String>(
  (ref, conversationId) {
    final repository = ref.watch(conversationRepositoryProvider);
    final notifier = ConversationNotifier(
      conversationId: conversationId,
      repository: repository,
    );
    // 不在这里调用initialize，让页面来控制
    return notifier;
  },
);
