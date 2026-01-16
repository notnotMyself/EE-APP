// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conversation_summary.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ConversationSummaryImpl _$$ConversationSummaryImplFromJson(
        Map<String, dynamic> json) =>
    _$ConversationSummaryImpl(
      id: json['id'] as String,
      agentId: json['agentId'] as String,
      agentName: json['agentName'] as String,
      agentRole: json['agentRole'] as String,
      agentAvatarUrl: json['agentAvatarUrl'] as String?,
      lastMessageContent: json['lastMessageContent'] as String?,
      lastMessageAt: json['lastMessageAt'] == null
          ? null
          : DateTime.parse(json['lastMessageAt'] as String),
      unreadCount: (json['unreadCount'] as num?)?.toInt() ?? 0,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$ConversationSummaryImplToJson(
        _$ConversationSummaryImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'agentId': instance.agentId,
      'agentName': instance.agentName,
      'agentRole': instance.agentRole,
      'agentAvatarUrl': instance.agentAvatarUrl,
      'lastMessageContent': instance.lastMessageContent,
      'lastMessageAt': instance.lastMessageAt?.toIso8601String(),
      'unreadCount': instance.unreadCount,
      'createdAt': instance.createdAt.toIso8601String(),
    };
