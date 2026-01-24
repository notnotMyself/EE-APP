import 'package:flutter/material.dart';
import '../../domain/models/agent.dart';
import '../theme/agent_profile_theme.dart';
import 'agent_avatar.dart';
import 'personality_selector.dart';

/// OPPO Sans 字体家族名称
const String _oppoSansFamily = 'PingFang SC';

/// AI员工介绍卡片
///
/// 用于空会话时显示Agent的介绍信息
/// 包括头像、名称、描述、人物个性等
class AgentProfileCard extends StatelessWidget {
  final Agent agent;
  final Personality? selectedPersonality;
  final VoidCallback? onPersonalityTap;

  const AgentProfileCard({
    super.key,
    required this.agent,
    this.selectedPersonality,
    this.onPersonalityTap,
  });

  @override
  Widget build(BuildContext context) {
    // 根据 Agent role 映射到对应的头像
    String? roleAvatar;
    switch (agent.role) {
      case 'design_validator':
        roleAvatar = AgentProfileTheme.chrisChenAvatar;
        break;
      case 'ai_news_crawler':
        roleAvatar = 'assets/images/secretary-girl-avatar.png'; // 码码
        break;
      case 'dev_efficiency_analyst':
        // 研发效能分析官使用商商头像
        roleAvatar = 'assets/images/secretary-woman-avatar.png';
        break;
      case 'ee_developer':
        // EE研发员工使用fallback显示"EE"文字
        roleAvatar = null;
        break;
      case 'general':
        // 小知使用小智头像
        roleAvatar = 'assets/images/secretary-boy-avatar.png';
        break;
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // 头像
        AgentAvatar(
          avatarUrl: agent.avatarUrl,
          assetPath: roleAvatar,
          fallbackText: agent.role == 'ee_developer' ? 'EE' : agent.name,
        ),

        const SizedBox(height: 14),

        // 名称
        Text(
          agent.name,
          style: AgentProfileTheme.agentNameStyle,
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 4),

        // 描述 + 人物个性（按 Figma 设计）
        _buildDescriptionWithPersonality(),
      ],
    );
  }

  /// 构建描述和人物个性行
  /// 基于 Figma 设计：描述 · 个性名称 [下拉图标]
  Widget _buildDescriptionWithPersonality() {
    final personalityName = selectedPersonality?.name ?? '默认';

    return GestureDetector(
      onTap: onPersonalityTap,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // 描述文字 + 分隔点 + 个性名称（使用 Flexible 避免溢出）
          Flexible(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // 描述（限制最大宽度避免溢出）
                Flexible(
                  child: Text(
                    agent.description,
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: Colors.black.withOpacity(0.54),
                      fontSize: 14,
                      fontFamily: _oppoSansFamily,
                      fontWeight: FontWeight.w400,
                      height: 1.43,
                    ),
                  ),
                ),
                const SizedBox(width: 4),
                // 分隔点
                Container(
                  width: 4,
                  height: 4,
                  decoration: const ShapeDecoration(
                    color: Color(0xFF393939),
                    shape: OvalBorder(),
                  ),
                ),
                const SizedBox(width: 4),
                // 个性名称
                Text(
                  personalityName,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: selectedPersonality != null
                        ? const Color(0xFF0066FF)
                        : Colors.black.withOpacity(0.54),
                    fontSize: 14,
                    fontFamily: _oppoSansFamily,
                    fontWeight: FontWeight.w400,
                    height: 1.43,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 2),
          // 下拉图标
          Icon(
            Icons.keyboard_arrow_down_rounded,
            size: 20,
            color: Colors.black.withOpacity(0.54),
          ),
        ],
      ),
    );
  }
}
