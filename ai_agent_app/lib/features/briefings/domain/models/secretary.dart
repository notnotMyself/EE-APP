class Secretary {
  final String id;
  final String name;
  final String title;
  final String avatar;
  final String? animatedAvatar;
  final String description;

  /// 映射到的 Agent role (如 'ai_news_crawler', 'dev_efficiency_analyst')
  /// null 表示不映射任何 Agent (如 general)
  final String? mappedAgentRole;

  /// 是否需要订阅才显示
  /// false: 始终显示 (如 general)
  /// true: 需要订阅对应的 Agent 才显示
  final bool requiresSubscription;

  const Secretary({
    required this.id,
    required this.name,
    required this.title,
    required this.avatar,
    this.animatedAvatar,
    required this.description,
    this.mappedAgentRole,
    this.requiresSubscription = false,
  });
}
