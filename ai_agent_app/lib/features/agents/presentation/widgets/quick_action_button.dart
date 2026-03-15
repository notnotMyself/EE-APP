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
    this.hintText = '简单描述设计方案背景与目标', // Figma: 输入框默认提示文案
  });
}

/// 预定义的快捷功能
class QuickActions {
  static const chat = QuickAction(
    id: 'chat',
    label: '随便聊聊',
    icon: Icons.chat_bubble_outline,
    initialMessage: null,
    hintText: '简单描述设计方案背景与目标', // Figma: 默认模式用相同提示
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

/// Figma 建议纸片样式的快捷按钮行
///
/// Figma (1915:19417): row, gap 8px, padding 8px 0px, width 328
/// 每个纸片 hug 宽度（按内容自适应），不是等宽拉伸
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
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8), // Figma: padding 8px 0px
      child: Wrap(
        spacing: 8, // Figma: gap 8px
        runSpacing: 8,
        children: actions.asMap().entries.map((entry) {
          final index = entry.key;
          final action = entry.value;
          final isHighlighted = selectedAction != null
              ? action.id == selectedAction!.id
              : index == 0;

          return _QuickActionPill(
            label: action.label,
            isHighlighted: isHighlighted,
            onTap: () => onActionTap(action),
          );
        }).toList(),
      ),
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
        // Figma: hug sizing, padding 2px 12px, borderRadius 50px
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
        decoration: ShapeDecoration(
          color: isHighlighted
              ? const Color(0x260066FF) // 彩色/填充色/Blue Halftone
              : Colors.black.withOpacity(0.04), // Figma: 中性色/填充色/4 · Thin
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(50), // Figma: borderRadius 50px
          ),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: isHighlighted
                ? const Color(0xFF0066FF)
                : Colors.black.withOpacity(0.9), // Figma: 中性色/文本&图标（黑）/90 · Primary
            fontSize: 12, // Figma: Body/XS · Regular
            fontFamily: 'OPPO Sans 4.0',
            fontWeight: FontWeight.w400,
            height: 1.3333, // Figma: lineHeight 1.3333em
          ),
        ),
      ),
    );
  }
}

