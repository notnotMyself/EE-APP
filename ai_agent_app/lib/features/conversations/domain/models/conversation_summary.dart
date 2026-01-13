import 'package:freezed_annotation/freezed_annotation.dart';

part 'conversation_summary.freezed.dart';
part 'conversation_summary.g.dart';

/// Summary of a conversation with an AI employee
/// Used in the conversations list page
@freezed
class ConversationSummary with _$ConversationSummary {
  const factory ConversationSummary({
    required String id,
    required String agentId,
    required String agentName,
    required String agentRole,
    String? agentAvatarUrl,
    String? lastMessageContent,
    DateTime? lastMessageAt,
    @Default(0) int unreadCount,
    required DateTime createdAt,
  }) = _ConversationSummary;

  factory ConversationSummary.fromJson(Map<String, dynamic> json) =>
      _$ConversationSummaryFromJson(json);
}
