import 'package:flutter/material.dart';
import '../state/conversation_state.dart';

/// 工具执行状态指示器（简洁版）
///
/// 在消息列表底部显示工具执行状态，设计简洁不抢眼
class ToolExecutionCard extends StatelessWidget {
  final ToolExecutionState toolState;
  final VoidCallback? onCancel;

  const ToolExecutionCard({
    super.key,
    required this.toolState,
    this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return toolState.maybeMap(
      executing: (state) => _buildExecutingIndicator(context, state),
      completed: (state) => _buildCompletedIndicator(context, state),
      orElse: () => const SizedBox.shrink(),
    );
  }

  Widget _buildExecutingIndicator(
    BuildContext context,
    ToolExecutionStateExecuting state,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 200), // 限制最大宽度
        margin: const EdgeInsets.only(left: 16, right: 16, top: 4, bottom: 4),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerHigh.withOpacity(0.5),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 小圆形图标 + 动画
            _MiniToolIcon(toolName: state.toolName, colorScheme: colorScheme),
            const SizedBox(width: 8),
            // 工具类型 + 状态
            Flexible(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // 工具类型
                  Text(
                    _getToolDisplayName(state.toolName),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: colorScheme.primary,
                      fontWeight: FontWeight.w500,
                      fontSize: 11,
                    ),
                  ),
                  const SizedBox(height: 3),
                  // 质感进度条
                  SizedBox(
                    width: 100, // 固定进度条宽度
                    child: _GlassProgressBar(
                      progress: state.progress,
                      colorScheme: colorScheme,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCompletedIndicator(
    BuildContext context,
    ToolExecutionStateCompleted state,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isError = state.isError ?? false;

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(left: 16, right: 16, top: 4, bottom: 4),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: isError
              ? colorScheme.errorContainer.withOpacity(0.15)
              : colorScheme.primaryContainer.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isError ? Icons.error_outline : Icons.check_circle_outline,
              color: isError
                  ? colorScheme.error.withOpacity(0.7)
                  : colorScheme.primary.withOpacity(0.7),
              size: 12,
            ),
            const SizedBox(width: 5),
            Text(
              '${_getToolDisplayName(state.toolName)} ${isError ? "失败" : "完成"}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: isError
                    ? colorScheme.error.withOpacity(0.7)
                    : colorScheme.primary.withOpacity(0.7),
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getToolDisplayName(String toolName) {
    switch (toolName) {
      case 'Write':
        return '写入文件';
      case 'Bash':
        return '执行命令';
      case 'Read':
        return '读取文件';
      case 'Grep':
        return '搜索内容';
      case 'Glob':
        return '查找文件';
      default:
        return toolName;
    }
  }
}

/// 小型工具图标（带呼吸动画）
class _MiniToolIcon extends StatefulWidget {
  final String toolName;
  final ColorScheme colorScheme;

  const _MiniToolIcon({
    required this.toolName,
    required this.colorScheme,
  });

  @override
  State<_MiniToolIcon> createState() => _MiniToolIconState();
}

class _MiniToolIconState extends State<_MiniToolIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat(reverse: true);
    _animation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  IconData _getIcon() {
    switch (widget.toolName) {
      case 'Write':
        return Icons.edit_note_rounded;
      case 'Bash':
        return Icons.terminal_rounded;
      case 'Read':
        return Icons.article_outlined;
      case 'Grep':
      case 'Glob':
        return Icons.search_rounded;
      default:
        return Icons.settings_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Icon(
          _getIcon(),
          size: 14,
          color: widget.colorScheme.primary.withOpacity(_animation.value),
        );
      },
    );
  }
}

/// 质感进度条（玻璃效果）
class _GlassProgressBar extends StatelessWidget {
  final double progress;
  final ColorScheme colorScheme;

  const _GlassProgressBar({
    required this.progress,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 2,
      decoration: BoxDecoration(
        color: colorScheme.outlineVariant.withOpacity(0.25),
        borderRadius: BorderRadius.circular(1),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          // 不确定进度时使用动画
          if (progress <= 0) {
            return _IndeterminateProgress(
              width: constraints.maxWidth,
              colorScheme: colorScheme,
            );
          }
          // 确定进度
          return FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: progress.clamp(0.0, 1.0),
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    colorScheme.primary.withOpacity(0.6),
                    colorScheme.primary.withOpacity(0.9),
                  ],
                ),
                borderRadius: BorderRadius.circular(1),
                boxShadow: [
                  BoxShadow(
                    color: colorScheme.primary.withOpacity(0.3),
                    blurRadius: 2,
                    offset: const Offset(0, 0),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

/// 不确定进度的动画条
class _IndeterminateProgress extends StatefulWidget {
  final double width;
  final ColorScheme colorScheme;

  const _IndeterminateProgress({
    required this.width,
    required this.colorScheme,
  });

  @override
  State<_IndeterminateProgress> createState() => _IndeterminateProgressState();
}

class _IndeterminateProgressState extends State<_IndeterminateProgress>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final indicatorWidth = widget.width * 0.35;
        final position = _controller.value * (widget.width + indicatorWidth) -
            indicatorWidth;

        return Stack(
          children: [
            Positioned(
              left: position,
              child: Container(
                width: indicatorWidth,
                height: 2,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      widget.colorScheme.primary.withOpacity(0.0),
                      widget.colorScheme.primary.withOpacity(0.7),
                      widget.colorScheme.primary.withOpacity(0.0),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(1),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
