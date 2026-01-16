// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_stats.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$UsageStatsImpl _$$UsageStatsImplFromJson(Map<String, dynamic> json) =>
    _$UsageStatsImpl(
      totalBriefings: (json['total_briefings'] as num?)?.toInt() ?? 0,
      weeklyBriefings: (json['weekly_briefings'] as num?)?.toInt() ?? 0,
      activeConversations: (json['active_conversations'] as num?)?.toInt() ?? 0,
      totalMessages: (json['total_messages'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$UsageStatsImplToJson(_$UsageStatsImpl instance) =>
    <String, dynamic>{
      'total_briefings': instance.totalBriefings,
      'weekly_briefings': instance.weeklyBriefings,
      'active_conversations': instance.activeConversations,
      'total_messages': instance.totalMessages,
    };
