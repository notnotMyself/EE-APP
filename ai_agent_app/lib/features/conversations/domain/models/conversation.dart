import 'package:freezed_annotation/freezed_annotation.dart';

part 'conversation.freezed.dart';
part 'conversation.g.dart';

@freezed
class Conversation with _$Conversation {
  const factory Conversation({
    required String id,
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'agent_id') required String agentId,
    @JsonKey(name: 'started_at') required DateTime startedAt,
    @JsonKey(name: 'last_message_at') DateTime? lastMessageAt,
    String? status,
    Map<String, dynamic>? context,
  }) = _Conversation;

  factory Conversation.fromJson(Map<String, dynamic> json) =>
      _$ConversationFromJson(json);
}

@freezed
class Message with _$Message {
  const factory Message({
    required String id,
    @JsonKey(name: 'conversation_id') required String conversationId,
    required String role,
    required String content,
    List<Map<String, dynamic>>? attachments,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _Message;

  factory Message.fromJson(Map<String, dynamic> json) =>
      _$MessageFromJson(json);
}
