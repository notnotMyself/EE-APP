// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conversation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ConversationImpl _$$ConversationImplFromJson(Map<String, dynamic> json) =>
    _$ConversationImpl(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      agentId: json['agent_id'] as String,
      startedAt: DateTime.parse(json['started_at'] as String),
      lastMessageAt: json['last_message_at'] == null
          ? null
          : DateTime.parse(json['last_message_at'] as String),
      status: json['status'] as String?,
      context: json['context'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ConversationImplToJson(_$ConversationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'agent_id': instance.agentId,
      'started_at': instance.startedAt.toIso8601String(),
      'last_message_at': instance.lastMessageAt?.toIso8601String(),
      'status': instance.status,
      'context': instance.context,
    };

_$MessageImpl _$$MessageImplFromJson(Map<String, dynamic> json) =>
    _$MessageImpl(
      id: json['id'] as String,
      conversationId: json['conversation_id'] as String,
      role: json['role'] as String,
      content: json['content'] as String,
      attachments: (json['attachments'] as List<dynamic>?)
          ?.map((e) => e as Map<String, dynamic>)
          .toList(),
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$$MessageImplToJson(_$MessageImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'conversation_id': instance.conversationId,
      'role': instance.role,
      'content': instance.content,
      'attachments': instance.attachments,
      'created_at': instance.createdAt.toIso8601String(),
    };
