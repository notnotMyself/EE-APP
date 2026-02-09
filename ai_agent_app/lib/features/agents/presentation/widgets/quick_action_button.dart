import 'package:flutter/material.dart';
import '../theme/agent_profile_theme.dart';

/// 快捷功能按钮数据模型
class QuickAction {
  final String id;
  final String label;
  final IconData icon;
  final String? initialMessage;
  final String? modeId; // 映射到后端 skill/评审模式
  final String hintText; // 选中该模式时输入框的提示文字

  const QuickAction({
    required this.id,
    required this.label,
    required this.icon,
    this.initialMessage,
    this.modeId,
    this.hintText = '这是一个什么产品 / 功能，核心解决什么问题',
  });
}

/// 预定义的快捷功能
class QuickActions {
  static const chat = QuickAction(
    id: 'chat',
    label: '随便聊聊',
    icon: Icons.chat_bubble_outline,
    initialMessage: null,
    hintText: '这是一个什么产品 / 功能，核心解决什么问题',
  );

  static const interaction = QuickAction(
    id: 'interaction',
    label: '交互验证',
    icon: Icons.touch_app_outlined,
    initialMessage: null,
    modeId: 'interaction_check',
    hintText: '描述产品目标，用户使用的核心路径',
  );

  static const visual = QuickAction(
    id: 'visual',
    label: '视觉讨论',
    icon: Icons.palette_outlined,
    initialMessage: null,
    modeId: 'visual_consistency',
    hintText: '描述产品目标，用户使用的核心路径',
  );

  static const compare = QuickAction(
    id: 'compare',
    label: '方案PK',
    icon: Icons.compare_outlined,
    initialMessage: null,
    modeId: 'compare_designs',
    hintText: '简单列出两个你在犹豫的方案差异，写清楚你为什么犹豫',
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

/// Figma 胶囊药丸样式的快捷按钮行
///
/// 基于 chris-ai-fuction 设计稿：
/// - 4 个胶囊按钮等宽排列
/// - 选中的按钮蓝色高亮
/// - 其余为次要灰色
class QuickActionPillRow extends StatelessWidget {
  final List<QuickAction> actions;
  final Function(QuickAction) onActionTap;
  final QuickAction? selectedAction;

  const QuickActionPillRow({
    super.key,
    required this.actions,
    required this.onActionTap,
    this.selectedAction,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: actions.asMap().entries.map((entry) {
        final index = entry.key;
        final action = entry.value;
        // 如果有选中状态就用选中状态，否则默认第一个高亮
        final isHighlighted = selectedAction != null
            ? action.id == selectedAction!.id
            : index == 0;

        return Expanded(
          child: Padding(
            padding: EdgeInsets.only(
              left: index == 0 ? 0 : 2.5,
              right: index == actions.length - 1 ? 0 : 2.5,
            ),
            child: _QuickActionPill(
              label: action.label,
              isHighlighted: isHighlighted,
              onTap: () => onActionTap(action),
            ),
          ),
        );
      }).toList(),
    );
  }
}

/// 单个胶囊药丸按钮
class _QuickActionPill extends StatelessWidget {
  final String label;
  final bool isHighlighted;
  final VoidCallback onTap;

  const _QuickActionPill({
    required this.label,
    required this.isHighlighted,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 32,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        clipBehavior: Clip.antiAlias,
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.04),
          shape: RoundedRectangleBorder(
            side: const BorderSide(width: 0.51, color: Colors.white),
            borderRadius: BorderRadius.circular(84.27),
          ),
        ),
        child: Center(
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isHighlighted
                  ? const Color(0xFF0066FF)
                  : Colors.black.withOpacity(0.54),
              fontSize: 12,
              fontFamily: 'OPPO Sans 4.0',
              fontWeight: isHighlighted ? FontWeight.w500 : FontWeight.w400,
              height: 1.40,
            ),
          ),
        ),
      ),
    );
  }
}

