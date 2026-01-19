import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/models/conversation.dart';

part 'conversation_state.freezed.dart';

/// 流式状态
@freezed
class StreamingState with _$StreamingState {
  const factory StreamingState.idle() = StreamingStateIdle;
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
    String? error,
    @Default(false) bool isLoading,
  }) = _ConversationViewState;

  factory ConversationViewState.initial(String conversationId) =>
      ConversationViewState(
        conversationId: conversationId,
        messages: [],
        streamingState: const StreamingState.idle(),
        connectionState: const WsConnectionState.disconnected(),
      );
}
