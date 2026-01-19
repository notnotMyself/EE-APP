import 'package:flutter/material.dart';
import '../../domain/models/briefing.dart';
import '../widgets/dynamic_briefing_renderer.dart';

/// 动态简报详情页
///
/// 使用 A2UI 的 ui_schema 动态渲染简报内容。
/// 支持多种组件类型：metric_cards, line_chart, bar_chart,
/// alert_list, timeline, table, markdown 等。
class DynamicBriefingDetailPage extends StatelessWidget {
  final Briefing briefing;

  const DynamicBriefingDetailPage({
    super.key,
    required this.briefing,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasUiSchema = briefing.uiSchema != null && briefing.uiSchema!.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          briefing.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        elevation: 0,
        actions: [
          // 优先级指示器
          Container(
            margin: const EdgeInsets.only(right: 16),
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
      body: SafeArea(
        child: hasUiSchema
            ? _buildDynamicContent(context)
            : _buildFallbackContent(context),
      ),
    );
  }

  /// 构建动态内容（使用 ui_schema）
  Widget _buildDynamicContent(BuildContext context) {
    final theme = Theme.of(context);

    try {
      final uiSchema = briefing.uiSchema!;
      final content = uiSchema['content'] as Map<String, dynamic>?;
      final sections = (content?['sections'] as List?)?.cast<Map<String, dynamic>>() ?? [];

      if (sections.isEmpty) {
        return _buildFallbackContent(context);
      }

      final renderer = DynamicBriefingRenderer();

      return SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 简报头部信息
            _buildHeader(context),
            const SizedBox(height: 16),

            // 动态渲染所有 sections
            for (final section in sections) ...[
              renderer.renderComponent(section),
              const SizedBox(height: 16),
            ],

            // 底部元信息
            _buildMetaInfo(context),
          ],
        ),
      );
    } catch (e) {
      // 解析失败时显示 fallback
      return _buildFallbackContent(context);
    }
  }

  /// 构建 Fallback 内容（无 ui_schema 时）
  Widget _buildFallbackContent(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 头部
          _buildHeader(context),
          const SizedBox(height: 24),

          // 标题
          Text(
            briefing.title,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),

          // 摘要
          Text(
            briefing.summary,
            style: theme.textTheme.bodyLarge?.copyWith(
              color: Colors.grey[700],
              height: 1.6,
            ),
          ),

          // 影响说明
          if (briefing.impact != null && briefing.impact!.isNotEmpty) ...[
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _getPriorityColor(briefing.priority).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _getPriorityColor(briefing.priority).withOpacity(0.3),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.warning_amber_rounded,
                        color: _getPriorityColor(briefing.priority),
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '影响说明',
                        style: theme.textTheme.titleSmall?.copyWith(
                          color: _getPriorityColor(briefing.priority),
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    briefing.impact!,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: _getPriorityColor(briefing.priority),
                    ),
                  ),
                ],
              ),
            ),
          ],

          // 结构化新闻列表（如果有）
          if (briefing.summaryStructured.isNotEmpty) ...[
            const SizedBox(height: 24),
            Text(
              '详细内容',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _buildNewsList(context),
          ],

          const SizedBox(height: 24),
          _buildMetaInfo(context),
        ],
      ),
    );
  }

  /// 构建头部信息
  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: [
        // Agent 头像
        CircleAvatar(
          radius: 20,
          backgroundColor: theme.colorScheme.primaryContainer,
          backgroundImage: briefing.agentAvatarUrl != null
              ? NetworkImage(briefing.agentAvatarUrl!)
              : null,
          child: briefing.agentAvatarUrl == null
              ? Icon(
                  _getTypeIcon(briefing.briefingType),
                  size: 20,
                  color: theme.colorScheme.primary,
                )
              : null,
        ),
        const SizedBox(width: 12),

        // Agent 名称和类型
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                briefing.agentName ?? '未知 Agent',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 2),
              Row(
                children: [
                  _buildTypeChip(context),
                  const SizedBox(width: 8),
                  Text(
                    _formatTime(briefing.createdAt),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        // 状态指示
        if (briefing.status == BriefingStatus.newItem)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.blue,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              '新',
              style: theme.textTheme.labelSmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
      ],
    );
  }

  /// 构建类型标签
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

  /// 构建新闻列表
  Widget _buildNewsList(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: briefing.summaryStructured.map((item) {
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey[200]!),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 序号
              Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: _getCategoryColor(item.category),
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
              const SizedBox(width: 12),

              // 内容
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.fullTitle ?? item.title,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    if (item.source != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        item.source!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: Colors.grey[500],
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              // 分类标签
              if (item.tag != null) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: _getCategoryColor(item.category).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    item.tag!,
                    style: TextStyle(
                      fontSize: 10,
                      color: _getCategoryColor(item.category),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ],
          ),
        );
      }).toList(),
    );
  }

  /// 构建元信息
  Widget _buildMetaInfo(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '创建时间: ${_formatDateTime(briefing.createdAt)}',
            style: theme.textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          if (briefing.uiSchemaVersion != null)
            Text(
              'Schema v${briefing.uiSchemaVersion}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: Colors.grey[500],
              ),
            ),
        ],
      ),
    );
  }

  // ==================== Helper Methods ====================

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

  Color _getCategoryColor(String? category) {
    switch (category) {
      case '产业重磅':
        return const Color(0xFFEA580C);
      case '前沿技术':
        return const Color(0xFF2563EB);
      case '工具发布':
        return const Color(0xFF16A34A);
      case '安全合规':
        return const Color(0xFFDC2626);
      default:
        return const Color(0xFF6B7280);
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

  String _formatDateTime(DateTime time) {
    return '${time.year}-${time.month.toString().padLeft(2, '0')}-${time.day.toString().padLeft(2, '0')} '
        '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}
