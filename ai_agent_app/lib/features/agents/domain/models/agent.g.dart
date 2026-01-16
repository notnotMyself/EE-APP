// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'agent.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AgentImpl _$$AgentImplFromJson(Map<String, dynamic> json) => _$AgentImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      role: json['role'] as String,
      avatarUrl: json['avatar_url'] as String?,
      dataSources: json['data_sources'] as Map<String, dynamic>?,
      triggerConditions: json['trigger_conditions'] as Map<String, dynamic>?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      createdBy: json['created_by'] as String?,
    );

Map<String, dynamic> _$$AgentImplToJson(_$AgentImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'role': instance.role,
      'avatar_url': instance.avatarUrl,
      'data_sources': instance.dataSources,
      'trigger_conditions': instance.triggerConditions,
      'is_active': instance.isActive,
      'created_at': instance.createdAt?.toIso8601String(),
      'created_by': instance.createdBy,
    };

_$UserAgentSubscriptionImpl _$$UserAgentSubscriptionImplFromJson(
        Map<String, dynamic> json) =>
    _$UserAgentSubscriptionImpl(
      userId: json['user_id'] as String,
      agentId: json['agent_id'] as String,
      subscribedAt: DateTime.parse(json['subscribed_at'] as String),
      config: json['config'] as Map<String, dynamic>?,
      agent: json['agent'] == null
          ? null
          : Agent.fromJson(json['agent'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$UserAgentSubscriptionImplToJson(
        _$UserAgentSubscriptionImpl instance) =>
    <String, dynamic>{
      'user_id': instance.userId,
      'agent_id': instance.agentId,
      'subscribed_at': instance.subscribedAt.toIso8601String(),
      'config': instance.config,
      'agent': instance.agent,
    };
