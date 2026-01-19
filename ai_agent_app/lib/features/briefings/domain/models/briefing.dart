import 'package:freezed_annotation/freezed_annotation.dart';

part 'briefing.freezed.dart';
part 'briefing.g.dart';

/// 简报类型枚举
enum BriefingType {
  @JsonValue('alert')
  alert,
  @JsonValue('insight')
  insight,
  @JsonValue('summary')
  summary,
  @JsonValue('action')
  action,
}

/// 优先级枚举
enum BriefingPriority {
  @JsonValue('P0')
  p0,
  @JsonValue('P1')
  p1,
  @JsonValue('P2')
  p2,
}

/// 简报状态枚举
enum BriefingStatus {
  @JsonValue('new')
  newItem,
  @JsonValue('read')
  read,
  @JsonValue('actioned')
  actioned,
  @JsonValue('dismissed')
  dismissed,
}

/// 简报操作按钮
@freezed
class BriefingAction with _$BriefingAction {
  const factory BriefingAction({
    required String label,
    required String action,
    Map<String, dynamic>? data,
    String? prompt,
  }) = _BriefingAction;

  factory BriefingAction.fromJson(Map<String, dynamic> json) =>
      _$BriefingActionFromJson(json);
}

/// 简报新闻项（用于结构化展示）
@freezed
class BriefingNewsItem with _$BriefingNewsItem {
  const factory BriefingNewsItem({
    required int index,
    required String title,
    @JsonKey(name: 'full_title') String? fullTitle,
    String? source,
    String? category,
    String? tag,
    String? url,
  }) = _BriefingNewsItem;

  factory BriefingNewsItem.fromJson(Map<String, dynamic> json) =>
      _$BriefingNewsItemFromJson(json);
}

/// 简报数据模型
@freezed
class Briefing with _$Briefing {
  const factory Briefing({
    required String id,
    @JsonKey(name: 'agent_id') required String agentId,
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'briefing_type') required BriefingType briefingType,
    required BriefingPriority priority,
    required String title,
    required String summary,
    String? impact,
    @Default([]) List<BriefingAction> actions,
    @JsonKey(name: 'report_artifact_id') String? reportArtifactId,
    @JsonKey(name: 'conversation_id') String? conversationId,
    @JsonKey(name: 'context_data') Map<String, dynamic>? contextData,
    required BriefingStatus status,
    @JsonKey(name: 'importance_score') double? importanceScore,
    @JsonKey(name: 'read_at') DateTime? readAt,
    @JsonKey(name: 'actioned_at') DateTime? actionedAt,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'expires_at') DateTime? expiresAt,
    // 关联的Agent信息
    @JsonKey(name: 'agent_name') String? agentName,
    @JsonKey(name: 'agent_avatar_url') String? agentAvatarUrl,
    @JsonKey(name: 'agent_role') String? agentRole,
    // 结构化新闻列表（用于AI资讯类简报）
    @JsonKey(name: 'summary_structured') @Default([]) List<BriefingNewsItem> summaryStructured,
    // 封面样式提示（废弃字段，保留兼容性）
    @JsonKey(name: 'cover_style') @Deprecated('Use ui_schema instead') String? coverStyle,
    // A2UI 动态 UI Schema（新增）
    @JsonKey(name: 'ui_schema') Map<String, dynamic>? uiSchema,
    @JsonKey(name: 'ui_schema_version') String? uiSchemaVersion,
  }) = _Briefing;

  factory Briefing.fromJson(Map<String, dynamic> json) =>
      _$BriefingFromJson(json);
}

/// 简报列表响应
@freezed
class BriefingListResponse with _$BriefingListResponse {
  const factory BriefingListResponse({
    required List<Briefing> items,
    required int total,
    @JsonKey(name: 'unread_count') required int unreadCount,
  }) = _BriefingListResponse;

  factory BriefingListResponse.fromJson(Map<String, dynamic> json) =>
      _$BriefingListResponseFromJson(json);
}

/// 未读数量响应
@freezed
class BriefingUnreadCount with _$BriefingUnreadCount {
  const factory BriefingUnreadCount({
    required int count,
    @JsonKey(name: 'by_priority') @Default({}) Map<String, int> byPriority,
  }) = _BriefingUnreadCount;

  factory BriefingUnreadCount.fromJson(Map<String, dynamic> json) =>
      _$BriefingUnreadCountFromJson(json);
}

/// 开始对话响应
@freezed
class StartConversationResponse with _$StartConversationResponse {
  const factory StartConversationResponse({
    @JsonKey(name: 'conversation_id') required String conversationId,
    @JsonKey(name: 'briefing_id') required String briefingId,
  }) = _StartConversationResponse;

  factory StartConversationResponse.fromJson(Map<String, dynamic> json) =>
      _$StartConversationResponseFromJson(json);
}
