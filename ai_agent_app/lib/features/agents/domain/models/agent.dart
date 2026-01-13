import 'package:freezed_annotation/freezed_annotation.dart';

part 'agent.freezed.dart';
part 'agent.g.dart';

@freezed
class Agent with _$Agent {
  const factory Agent({
    required String id,
    required String name,
    required String description,
    required String role,
    @JsonKey(name: 'avatar_url') String? avatarUrl,
    @JsonKey(name: 'data_sources') Map<String, dynamic>? dataSources,
    @JsonKey(name: 'trigger_conditions') Map<String, dynamic>? triggerConditions,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @JsonKey(name: 'created_at') DateTime? createdAt,
    @JsonKey(name: 'created_by') String? createdBy,
  }) = _Agent;

  factory Agent.fromJson(Map<String, dynamic> json) => _$AgentFromJson(json);
}

@freezed
class UserAgentSubscription with _$UserAgentSubscription {
  const factory UserAgentSubscription({
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'agent_id') required String agentId,
    @JsonKey(name: 'subscribed_at') required DateTime subscribedAt,
    Map<String, dynamic>? config,
    Agent? agent,
  }) = _UserAgentSubscription;

  factory UserAgentSubscription.fromJson(Map<String, dynamic> json) =>
      _$UserAgentSubscriptionFromJson(json);
}
