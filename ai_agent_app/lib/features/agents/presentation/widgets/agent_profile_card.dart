import 'package:flutter/material.dart';
import '../../domain/models/agent.dart';
import '../theme/agent_profile_theme.dart';
import 'agent_avatar.dart';

/// AI员工介绍卡片
///
/// 用于空会话时显示Agent的介绍信息
/// 包括头像、名称、描述等
class AgentProfileCard extends StatelessWidget {
  final Agent agent;
  final String? greeting;

  const AgentProfileCard({
    super.key,
    required this.agent,
    this.greeting,
  });

  @override
  Widget build(BuildContext context) {
    final isChrisChen = agent.role == 'design_validator' ||
        agent.name.contains('Chris');

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 问候语（如果有）
        if (greeting != null) ...[
          Text(
            greeting!,
            style: AgentProfileTheme.greetingStyle,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
        ],

        // 头像
        AgentAvatar(
          avatarUrl: agent.avatarUrl,
          assetPath: isChrisChen ? AgentProfileTheme.chrisChenAvatar : null,
          fallbackText: agent.name,
        ),

        const SizedBox(height: 14),

        // 名称
        Text(
          agent.name,
          style: AgentProfileTheme.agentNameStyle,
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 4),

        // 描述
        Text(
          agent.description,
          style: AgentProfileTheme.agentDescriptionStyle,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
