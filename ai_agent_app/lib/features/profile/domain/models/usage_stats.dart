import 'package:freezed_annotation/freezed_annotation.dart';

part 'usage_stats.freezed.dart';

/// User usage statistics model
@freezed
class UsageStats with _$UsageStats {
  const factory UsageStats({
    @JsonKey(name: 'total_briefings') @Default(0) int totalBriefings,
    @JsonKey(name: 'weekly_briefings') @Default(0) int weeklyBriefings,
    @JsonKey(name: 'active_conversations') @Default(0) int activeConversations,
    @JsonKey(name: 'total_messages') @Default(0) int totalMessages,
  }) = _UsageStats;

  factory UsageStats.fromJson(Map<String, dynamic> json) =>
      _$UsageStatsFromJson(json);
}
