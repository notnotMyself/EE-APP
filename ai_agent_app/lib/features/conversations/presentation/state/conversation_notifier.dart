import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../../../core/config/timeout_config.dart';
import '../../data/conversation_repository.dart';
import '../../data/websocket_client.dart';
import '../../domain/models/conversation.dart';
import 'conversation_state.dart';

/// 对话状态Notifier
///
/// 管理对话页面的状态，包括：
/// - 消息列表
/// - 流式内容缓冲和批量更新
/// - WebSocket连接状态
class ConversationNotifier extends StateNotifier<ConversationViewState> {
  final String conversationId;
  final ConversationRepository _repository;

  ConversationWebSocketClient? _wsClient;
  Timer? _flushTimer;
  final List<String> _contentBuffer = [];

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
    state = state.copyWith(
      connectionState: const WsConnectionState.connected(),
    );
  }

  void _handleDisconnected() {
    state = state.copyWith(
      connectionState: const WsConnectionState.disconnected(),
    );
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
        break;

      case WSMessageType.error:
        state = state.copyWith(
          streamingState: StreamingState.error(message.content ?? '未知错误'),
        );
        break;

      case WSMessageType.taskStart:
      case WSMessageType.taskProgress:
      case WSMessageType.briefingCreated:
      case WSMessageType.taskComplete:
        // 任务相关事件，可以用来更新UI
        break;

      case WSMessageType.toolUse:
      case WSMessageType.toolResult:
        // 工具调用事件
        break;

      default:
        break;
    }
  }

  /// 追加流式内容到缓冲区（批量更新优化）
  void _appendStreamingContent(String content) {
    _contentBuffer.add(content);
    _scheduleBufferFlush();
  }

  /// 安排缓冲区刷新（50ms批量更新）
  void _scheduleBufferFlush() {
    _flushTimer?.cancel();
    _flushTimer = Timer(TimeoutConfig.streamingUpdateInterval, () {
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
            startedAt: DateTime.now(),
          ),
        ),
      );
    });
  }

  /// 完成消息
  void _finalizeMessage() {
    // 先刷新所有缓冲
    _flushTimer?.cancel();
    if (_contentBuffer.isNotEmpty) {
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
            startedAt: DateTime.now(),
          ),
        ),
      );
    }

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
    if (content.trim().isEmpty) return;

    // 添加用户消息到列表
    final userMessage = Message(
      id: 'msg-user-${DateTime.now().millisecondsSinceEpoch}',
      conversationId: conversationId,
      role: 'user',
      content: content.trim(),
      createdAt: DateTime.now(),
    );

    state = state.copyWith(
      messages: [...state.messages, userMessage],
      streamingState: const StreamingState.idle(),
    );

    // 检查WebSocket连接
    if (_wsClient == null || !_wsClient!.isConnected) {
      // 如果WebSocket未连接，尝试重连或使用SSE fallback
      if (_wsClient != null) {
        await _wsClient!.connect();
      }

      if (_wsClient == null || !_wsClient!.isConnected) {
        // 使用SSE fallback
        await _sendViaSse(content.trim());
        return;
      }
    }

    // 通过WebSocket发送
    _wsClient!.sendMessage(content.trim());
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
