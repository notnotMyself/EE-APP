import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/models/conversation.dart';

part 'conversation_state.freezed.dart';

/// 工具执行状态（参考 claudecodeui 的设计）
@freezed
class ToolExecutionState with _$ToolExecutionState {
  /// 空闲状态
  const factory ToolExecutionState.idle() = ToolExecutionStateIdle;

  /// 正在执行工具（带进度）
  const factory ToolExecutionState.executing({
    required String toolName,
    required String toolId,
    Map<String, dynamic>? toolInput,
    required DateTime startedAt,
    @Default(0.0) double progress, // 0.0 - 1.0
    @Default('executing') String status, // executing, writing, etc.
    String? filePath, // 对于 Write 工具，显示文件路径
    String? statusMessage, // 状态消息
  }) = ToolExecutionStateExecuting;

  /// 工具执行完成
  const factory ToolExecutionState.completed({
    required String toolName,
    required String toolId,
    String? result,
    bool? isError,
  }) = ToolExecutionStateCompleted;
}

/// 流式状态
@freezed
class StreamingState with _$StreamingState {
  const factory StreamingState.idle() = StreamingStateIdle;

  /// 等待AI响应（用户发送消息后立即进入此状态）
  const factory StreamingState.waiting({
    required DateTime startedAt,
  }) = StreamingStateWaiting;

  const factory StreamingState.streaming({
    required String content,
    required DateTime startedAt,
  }) = StreamingStateStreaming;
  const factory StreamingState.completed() = StreamingStateCompleted;
  const factory StreamingState.error(String message) = StreamingStateError;
}

/// WebSocket连接状态
@freezed
class WsConnectionState with _$WsConnectionState {
  const factory WsConnectionState.disconnected() = WsConnectionStateDisconnected;
  const factory WsConnectionState.connecting() = WsConnectionStateConnecting;
  const factory WsConnectionState.connected() = WsConnectionStateConnected;
  const factory WsConnectionState.reconnecting({required int attempt}) =
      WsConnectionStateReconnecting;
}

/// 对话页面状态
@freezed
class ConversationViewState with _$ConversationViewState {
  const factory ConversationViewState({
    required String conversationId,
    required List<Message> messages,
    required StreamingState streamingState,
    required WsConnectionState connectionState,
    /// 工具执行状态（新增：让用户看到工具执行进度）
    @Default(ToolExecutionState.idle()) ToolExecutionState toolState,
    String? error,
    @Default(false) bool isLoading,
  }) = _ConversationViewState;

  factory ConversationViewState.initial(String conversationId) =>
      ConversationViewState(
        conversationId: conversationId,
        messages: [],
        streamingState: const StreamingState.idle(),
        connectionState: const WsConnectionState.disconnected(),
        toolState: const ToolExecutionState.idle(),
      );
}
