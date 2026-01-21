import 'package:flutter/material.dart';
import '../theme/agent_profile_theme.dart';

/// 快捷功能按钮数据模型
class QuickAction {
  final String id;
  final String label;
  final IconData icon;
  final String? initialMessage;

  const QuickAction({
    required this.id,
    required this.label,
    required this.icon,
    this.initialMessage,
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
    initialMessage: '帮我验证一下这个交互设计',
  );

  static const visual = QuickAction(
    id: 'visual',
    label: '视觉讨论',
    icon: Icons.palette_outlined,
    initialMessage: '我想讨论一下视觉设计',
  );

  static const compare = QuickAction(
    id: 'compare',
    label: '方案选择',
    icon: Icons.compare_outlined,
    initialMessage: '帮我对比一下这几个方案',
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

/// 快捷功能按钮行
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
      mainAxisAlignment: MainAxisAlignment.start,
      children: actions.map((action) {
        return Padding(
          padding: EdgeInsets.only(
            right: action != actions.last 
                ? AgentProfileTheme.quickActionSpacing 
                : 0,
          ),
          child: QuickActionButton(
            action: action,
            onTap: () => onActionTap(action),
          ),
        );
      }).toList(),
    );
  }
}

