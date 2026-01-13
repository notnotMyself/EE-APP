import 'package:flutter/material.dart';
import '../../domain/models/briefing.dart';

/// 简报卡片组件
class BriefingCard extends StatelessWidget {
  const BriefingCard({
    super.key,
    required this.briefing,
    required this.onTap,
  });

  final Briefing briefing;
  final VoidCallback onTap;

  /// 判断是否为资讯类简报（使用紧凑样式）
  bool get _isNewsType => briefing.coverStyle == 'news_list';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUnread = briefing.status == BriefingStatus.newItem;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: isUnread ? 2 : 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: _getPriorityColor(briefing.priority).withOpacity(0.3),
          width: isUnread ? 2 : 1,
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 根据类型选择封面样式
            if (_isNewsType)
              _buildCompactCover(context)
            else
              _buildCoverImage(context),

            // 信息区域
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 头部：Agent头像 + 类型标签 + 时间
                  _buildHeader(context),
                  const SizedBox(height: 12),

                  // 标题
                  Text(
                    briefing.title,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isUnread ? null : Colors.grey[600],
                      height: 1.3,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 12),

                  // 根据类型选择摘要样式
                  if (_isNewsType && briefing.summaryStructured.isNotEmpty)
                    _buildNewsListPreview(context, theme)
                  else
                    _buildSummaryText(context, theme),

                  // 影响说明（如果有）
                  if (briefing.impact != null && briefing.impact!.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: _getPriorityColor(briefing.priority).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.info_outline,
                            size: 16,
                            color: _getPriorityColor(briefing.priority),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              briefing.impact!,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: _getPriorityColor(briefing.priority),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建紧凑封面（资讯类型专用）
  Widget _buildCompactCover(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      height: 60,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            Color(0xFF4F46E5), // Indigo
            Color(0xFF7C3AED), // Purple
          ],
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          children: [
            const Icon(Icons.newspaper, color: Colors.white, size: 24),
            const SizedBox(width: 12),
            Text(
              briefing.agentName ?? 'AI资讯追踪官',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const Spacer(),
            // 优先级标签
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                _getPriorityLabel(briefing.priority),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            // 未读标记
            if (briefing.status == BriefingStatus.newItem) ...[
              const SizedBox(width: 8),
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF4F46E5), width: 2),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// 构建结构化新闻列表预览
  Widget _buildNewsListPreview(BuildContext context, ThemeData theme) {
    final items = briefing.summaryStructured.take(3).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var item in items) ...[
          _buildNewsItem(theme, item),
          if (item != items.last) const SizedBox(height: 8),
        ],
        if (briefing.summaryStructured.length > 3) ...[
          const SizedBox(height: 8),
          Text(
            '还有 ${briefing.summaryStructured.length - 3} 条...',
            style: theme.textTheme.bodySmall?.copyWith(
              color: Colors.grey[500],
            ),
          ),
        ],
      ],
    );
  }

  /// 构建单条新闻项
  Widget _buildNewsItem(ThemeData theme, BriefingNewsItem item) {
    final categoryColor = _getCategoryColor(item.category);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 序号标签
        Container(
          width: 20,
          height: 20,
          decoration: BoxDecoration(
            color: categoryColor,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Center(
            child: Text(
              '${item.index}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        // 标题 + 来源
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                item.title,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              if (item.source != null && item.source!.isNotEmpty)
                Text(
                  item.source!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: Colors.grey[500],
                    fontSize: 11,
                  ),
                ),
            ],
          ),
        ),
        // 分类标签
        if (item.tag != null && item.tag!.isNotEmpty) ...[
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: categoryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              item.tag!,
              style: TextStyle(
                fontSize: 10,
                color: categoryColor,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ],
    );
  }

  /// 构建普通摘要文本
  Widget _buildSummaryText(BuildContext context, ThemeData theme) {
    return Text(
      briefing.summary,
      style: theme.textTheme.bodyMedium?.copyWith(
        color: Colors.grey[700],
      ),
      maxLines: 3,
      overflow: TextOverflow.ellipsis,
    );
  }

  /// 获取分类颜色
  Color _getCategoryColor(String? category) {
    switch (category) {
      case '产业重磅':
        return const Color(0xFFEA580C); // Orange
      case '前沿技术':
        return const Color(0xFF2563EB); // Blue
      case '工具发布':
        return const Color(0xFF16A34A); // Green
      case '安全合规':
        return const Color(0xFFDC2626); // Red
      default:
        return const Color(0xFF6B7280); // Gray
    }
  }

  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: [
        // Agent头像
        CircleAvatar(
          radius: 16,
          backgroundColor: theme.colorScheme.primaryContainer,
          backgroundImage: briefing.agentAvatarUrl != null
              ? NetworkImage(briefing.agentAvatarUrl!)
              : null,
          child: briefing.agentAvatarUrl == null
              ? Icon(
                  _getTypeIcon(briefing.briefingType),
                  size: 16,
                  color: theme.colorScheme.primary,
                )
              : null,
        ),
        const SizedBox(width: 8),

        // Agent名称
        Text(
          briefing.agentName ?? '未知',
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),

        const SizedBox(width: 8),

        // 类型标签
        _buildTypeChip(context),

        const Spacer(),

        // 时间
        Text(
          _formatTime(briefing.createdAt),
          style: theme.textTheme.bodySmall?.copyWith(
            color: Colors.grey[500],
          ),
        ),

        // 未读标记
        if (briefing.status == BriefingStatus.newItem) ...[
          const SizedBox(width: 8),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: _getPriorityColor(briefing.priority),
              shape: BoxShape.circle,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildTypeChip(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: _getTypeColor(briefing.briefingType).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        _getTypeLabel(briefing.briefingType),
        style: theme.textTheme.labelSmall?.copyWith(
          color: _getTypeColor(briefing.briefingType),
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  /// 构建封面图区域
  Widget _buildCoverImage(BuildContext context) {
    final theme = Theme.of(context);

    // TODO: 当有真实封面图时，这里会显示网络图片
    // 当前显示占位符（降级方案：渐变背景 + 图标）
    return Stack(
      children: [
        // 封面图或占位符
        Container(
          width: double.infinity,
          height: 240,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: _getCoverGradientColors(briefing.briefingType),
            ),
          ),
          child: Center(
            child: Icon(
              _getTypeIcon(briefing.briefingType),
              size: 96,
              color: Colors.white.withOpacity(0.4),
            ),
          ),
        ),

        // 状态指示器（左上角）
        Positioned(
          top: 12,
          left: 12,
          child: Row(
            children: [
              // 优先级标签
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: _getPriorityColor(briefing.priority),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  _getPriorityLabel(briefing.priority),
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),

        // 未读标记（右上角）
        if (briefing.status == BriefingStatus.newItem)
          Positioned(
            top: 12,
            right: 12,
            child: Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: _getPriorityColor(briefing.priority),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 2),
              ),
            ),
          ),
      ],
    );
  }

  /// 获取封面渐变色
  List<Color> _getCoverGradientColors(BriefingType type) {
    switch (type) {
      case BriefingType.alert:
        return [const Color(0xFFFEE2E2), const Color(0xFFFECACA)];
      case BriefingType.insight:
        return [const Color(0xFFEDE9FE), const Color(0xFFDDD6FE)];
      case BriefingType.summary:
        return [const Color(0xFFDBEAFE), const Color(0xFFBFDBFE)];
      case BriefingType.action:
        return [const Color(0xFFD1FAE5), const Color(0xFFA7F3D0)];
    }
  }

  String _getPriorityLabel(BriefingPriority priority) {
    switch (priority) {
      case BriefingPriority.p0:
        return 'P0';
      case BriefingPriority.p1:
        return 'P1';
      case BriefingPriority.p2:
        return 'P2';
    }
  }

  Color _getPriorityColor(BriefingPriority priority) {
    switch (priority) {
      case BriefingPriority.p0:
        return Colors.red;
      case BriefingPriority.p1:
        return Colors.orange;
      case BriefingPriority.p2:
        return Colors.blue;
    }
  }

  Color _getTypeColor(BriefingType type) {
    switch (type) {
      case BriefingType.alert:
        return Colors.red;
      case BriefingType.insight:
        return Colors.purple;
      case BriefingType.summary:
        return Colors.blue;
      case BriefingType.action:
        return Colors.green;
    }
  }

  String _getTypeLabel(BriefingType type) {
    switch (type) {
      case BriefingType.alert:
        return '警报';
      case BriefingType.insight:
        return '洞察';
      case BriefingType.summary:
        return '摘要';
      case BriefingType.action:
        return '待办';
    }
  }

  IconData _getTypeIcon(BriefingType type) {
    switch (type) {
      case BriefingType.alert:
        return Icons.warning_rounded;
      case BriefingType.insight:
        return Icons.lightbulb_rounded;
      case BriefingType.summary:
        return Icons.summarize_rounded;
      case BriefingType.action:
        return Icons.task_alt_rounded;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 60) {
      return '${diff.inMinutes}分钟前';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}小时前';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}天前';
    } else {
      return '${time.month}/${time.day}';
    }
  }
}
