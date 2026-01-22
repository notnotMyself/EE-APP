import 'package:flutter/material.dart';
import '../theme/agent_profile_theme.dart';

/// 快捷功能按钮数据模型
class QuickAction {
  final String id;
  final String label;
  final IconData icon;
  final String? initialMessage;
  final String? modeId; // 映射到后端 skill/评审模式

  const QuickAction({
    required this.id,
    required this.label,
    required this.icon,
    this.initialMessage,
    this.modeId,
  });
}

/// 预定义的快捷功能
class QuickActions {
  static const chat = QuickAction(
    id: 'chat',
    label: '随便聊聊',
    icon: Icons.chat_bubble_outline,
    initialMessage: null,
  );

  static const interaction = QuickAction(
    id: 'interaction',
    label: '交互验证',
    icon: Icons.touch_app_outlined,
    initialMessage: '请对这个设计进行交互可用性评审',
    modeId: 'interaction_check',
  );

  static const visual = QuickAction(
    id: 'visual',
    label: '视觉讨论',
    icon: Icons.palette_outlined,
    initialMessage: '请检查这个设计的视觉一致性',
    modeId: 'visual_consistency',
  );

  static const compare = QuickAction(
    id: 'compare',
    label: '方案选择',
    icon: Icons.compare_outlined,
    initialMessage: '请帮我对比这几个设计方案',
    modeId: 'compare_designs',
  );

  /// 默认快捷功能列表
  static List<QuickAction> get defaults => [
    chat,
    interaction,
    visual,
    compare,
  ];
}

/// 快捷功能按钮组件
class QuickActionButton extends StatelessWidget {
  final QuickAction action;
  final VoidCallback onTap;

  const QuickActionButton({
    super.key,
    required this.action,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 圆形按钮
          Container(
            width: AgentProfileTheme.quickActionSize,
            height: AgentProfileTheme.quickActionSize,
            decoration: AgentProfileTheme.quickActionDecoration,
            child: Center(
              child: Icon(
                action.icon,
                size: AgentProfileTheme.quickActionIconSize,
                color: AgentProfileTheme.accentBlue,
              ),
            ),
          ),
          const SizedBox(height: 8),
          // 标签
          Text(
            action.label,
            style: AgentProfileTheme.quickActionLabelStyle,
          ),
        ],
      ),
    );
  }
}

/// 快捷功能按钮行（自适应宽度）
class QuickActionRow extends StatelessWidget {
  final List<QuickAction> actions;
  final Function(QuickAction) onActionTap;

  const QuickActionRow({
    super.key,
    required this.actions,
    required this.onActionTap,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: actions.map((action) {
        return Expanded(
          child: QuickActionButton(
            action: action,
            onTap: () => onActionTap(action),
          ),
        );
      }).toList(),
    );
  }
}

