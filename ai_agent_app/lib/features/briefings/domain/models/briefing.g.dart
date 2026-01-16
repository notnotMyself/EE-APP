// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'briefing.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$BriefingActionImpl _$$BriefingActionImplFromJson(Map<String, dynamic> json) =>
    _$BriefingActionImpl(
      label: json['label'] as String,
      action: json['action'] as String,
      data: json['data'] as Map<String, dynamic>?,
      prompt: json['prompt'] as String?,
    );

Map<String, dynamic> _$$BriefingActionImplToJson(
        _$BriefingActionImpl instance) =>
    <String, dynamic>{
      'label': instance.label,
      'action': instance.action,
      'data': instance.data,
      'prompt': instance.prompt,
    };

_$BriefingNewsItemImpl _$$BriefingNewsItemImplFromJson(
        Map<String, dynamic> json) =>
    _$BriefingNewsItemImpl(
      index: (json['index'] as num).toInt(),
      title: json['title'] as String,
      fullTitle: json['full_title'] as String?,
      source: json['source'] as String?,
      category: json['category'] as String?,
      tag: json['tag'] as String?,
      url: json['url'] as String?,
    );

Map<String, dynamic> _$$BriefingNewsItemImplToJson(
        _$BriefingNewsItemImpl instance) =>
    <String, dynamic>{
      'index': instance.index,
      'title': instance.title,
      'full_title': instance.fullTitle,
      'source': instance.source,
      'category': instance.category,
      'tag': instance.tag,
      'url': instance.url,
    };

_$BriefingImpl _$$BriefingImplFromJson(Map<String, dynamic> json) =>
    _$BriefingImpl(
      id: json['id'] as String,
      agentId: json['agent_id'] as String,
      userId: json['user_id'] as String,
      briefingType: $enumDecode(_$BriefingTypeEnumMap, json['briefing_type']),
      priority: $enumDecode(_$BriefingPriorityEnumMap, json['priority']),
      title: json['title'] as String,
      summary: json['summary'] as String,
      impact: json['impact'] as String?,
      actions: (json['actions'] as List<dynamic>?)
              ?.map((e) => BriefingAction.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      reportArtifactId: json['report_artifact_id'] as String?,
      conversationId: json['conversation_id'] as String?,
      contextData: json['context_data'] as Map<String, dynamic>?,
      status: $enumDecode(_$BriefingStatusEnumMap, json['status']),
      importanceScore: (json['importance_score'] as num?)?.toDouble(),
      readAt: json['read_at'] == null
          ? null
          : DateTime.parse(json['read_at'] as String),
      actionedAt: json['actioned_at'] == null
          ? null
          : DateTime.parse(json['actioned_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      expiresAt: json['expires_at'] == null
          ? null
          : DateTime.parse(json['expires_at'] as String),
      agentName: json['agent_name'] as String?,
      agentAvatarUrl: json['agent_avatar_url'] as String?,
      agentRole: json['agent_role'] as String?,
      summaryStructured: (json['summary_structured'] as List<dynamic>?)
              ?.map((e) => BriefingNewsItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      coverStyle: json['cover_style'] as String?,
    );

Map<String, dynamic> _$$BriefingImplToJson(_$BriefingImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'agent_id': instance.agentId,
      'user_id': instance.userId,
      'briefing_type': _$BriefingTypeEnumMap[instance.briefingType]!,
      'priority': _$BriefingPriorityEnumMap[instance.priority]!,
      'title': instance.title,
      'summary': instance.summary,
      'impact': instance.impact,
      'actions': instance.actions,
      'report_artifact_id': instance.reportArtifactId,
      'conversation_id': instance.conversationId,
      'context_data': instance.contextData,
      'status': _$BriefingStatusEnumMap[instance.status]!,
      'importance_score': instance.importanceScore,
      'read_at': instance.readAt?.toIso8601String(),
      'actioned_at': instance.actionedAt?.toIso8601String(),
      'created_at': instance.createdAt.toIso8601String(),
      'expires_at': instance.expiresAt?.toIso8601String(),
      'agent_name': instance.agentName,
      'agent_avatar_url': instance.agentAvatarUrl,
      'agent_role': instance.agentRole,
      'summary_structured': instance.summaryStructured,
      'cover_style': instance.coverStyle,
    };

const _$BriefingTypeEnumMap = {
  BriefingType.alert: 'alert',
  BriefingType.insight: 'insight',
  BriefingType.summary: 'summary',
  BriefingType.action: 'action',
};

const _$BriefingPriorityEnumMap = {
  BriefingPriority.p0: 'P0',
  BriefingPriority.p1: 'P1',
  BriefingPriority.p2: 'P2',
};

const _$BriefingStatusEnumMap = {
  BriefingStatus.newItem: 'new',
  BriefingStatus.read: 'read',
  BriefingStatus.actioned: 'actioned',
  BriefingStatus.dismissed: 'dismissed',
};

_$BriefingListResponseImpl _$$BriefingListResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$BriefingListResponseImpl(
      items: (json['items'] as List<dynamic>)
          .map((e) => Briefing.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      unreadCount: (json['unread_count'] as num).toInt(),
    );

Map<String, dynamic> _$$BriefingListResponseImplToJson(
        _$BriefingListResponseImpl instance) =>
    <String, dynamic>{
      'items': instance.items,
      'total': instance.total,
      'unread_count': instance.unreadCount,
    };

_$BriefingUnreadCountImpl _$$BriefingUnreadCountImplFromJson(
        Map<String, dynamic> json) =>
    _$BriefingUnreadCountImpl(
      count: (json['count'] as num).toInt(),
      byPriority: (json['by_priority'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, (e as num).toInt()),
          ) ??
          const {},
    );

Map<String, dynamic> _$$BriefingUnreadCountImplToJson(
        _$BriefingUnreadCountImpl instance) =>
    <String, dynamic>{
      'count': instance.count,
      'by_priority': instance.byPriority,
    };

_$StartConversationResponseImpl _$$StartConversationResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$StartConversationResponseImpl(
      conversationId: json['conversation_id'] as String,
      briefingId: json['briefing_id'] as String,
    );

Map<String, dynamic> _$$StartConversationResponseImplToJson(
        _$StartConversationResponseImpl instance) =>
    <String, dynamic>{
      'conversation_id': instance.conversationId,
      'briefing_id': instance.briefingId,
    };
