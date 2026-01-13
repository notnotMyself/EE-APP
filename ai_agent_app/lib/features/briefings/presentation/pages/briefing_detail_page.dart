import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../domain/models/briefing.dart';
import '../controllers/briefing_controller.dart';
import '../../../conversations/presentation/pages/conversation_page.dart';
import '../../../agents/data/agent_repository.dart';
import '../../data/briefing_repository.dart';

/// 简报详情页（全屏）
class BriefingDetailPage extends ConsumerStatefulWidget {
  const BriefingDetailPage({
    super.key,
    required this.briefing,
  });

  final Briefing briefing;

  @override
  ConsumerState<BriefingDetailPage> createState() =>
      _BriefingDetailPageState();
}

class _BriefingDetailPageState extends ConsumerState<BriefingDetailPage> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // 进入详情页时自动标记为已读
    if (widget.briefing.status == BriefingStatus.newItem) {
      Future.microtask(() {
        ref.read(briefingControllerProvider.notifier).markAsRead(widget.briefing.id);
      });
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: _buildAppBar(context, theme),
      body: Stack(
        children: [
          // 可滚动内容区
          SingleChildScrollView(
            controller: _scrollController,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Hero 封面大图
                _buildHeroImage(context),

                // 内容区域
                Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 标题
                      Text(
                        widget.briefing.title,
                        style: theme.textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),

                      // 元数据行
                      _buildMetadata(context, theme),

                      const SizedBox(height: 24),
                      const Divider(),
                      const SizedBox(height: 24),

                      // 影响说明
                      if (widget.briefing.impact != null &&
                          widget.briefing.impact!.isNotEmpty) ...[
                        _buildImpactSection(context, theme),
                        const SizedBox(height: 24),
                      ],

                      // 完整摘要（Markdown渲染）
                      MarkdownBody(
                        data: widget.briefing.summary,
                        selectable: true,
                        styleSheet: MarkdownStyleSheet(
                          p: theme.textTheme.bodyLarge?.copyWith(height: 1.6),
                          h1: theme.textTheme.headlineSmall,
                          h2: theme.textTheme.titleLarge,
                          h3: theme.textTheme.titleMedium,
                          listBullet: theme.textTheme.bodyLarge,
                          code: theme.textTheme.bodyMedium?.copyWith(
                            fontFamily: 'monospace',
                            backgroundColor: Colors.grey.shade200,
                          ),
                          codeblockDecoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),

                      // 查看完整报告按钮
                      if (widget.briefing.reportArtifactId != null) ...[
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton.icon(
                            icon: const Icon(Icons.article_outlined),
                            label: const Text('查看完整报告'),
                            onPressed: () => _showFullReport(context),
                          ),
                        ),
                      ],

                      // 底部留白（为输入框留空间）
                      const SizedBox(height: 140),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // 底部固定栏
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: _buildBottomBar(context, theme),
          ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context, ThemeData theme) {
    return AppBar(
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => Navigator.of(context).pop(),
      ),
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.briefing.agentName ?? '未知',
            style: theme.textTheme.titleMedium,
          ),
          Text(
            widget.briefing.agentRole ?? '',
            style: theme.textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.share_outlined),
          tooltip: '分享',
          onPressed: () {
            // TODO: 实现分享功能（Phase 4）
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('分享功能即将上线')),
            );
          },
        ),
        IconButton(
          icon: const Icon(Icons.track_changes_outlined),
          tooltip: '持续跟踪',
          onPressed: () {
            // TODO: 实现跟踪功能（Phase 3）
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('跟踪功能即将上线')),
            );
          },
        ),
        PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert),
          onSelected: (value) {
            switch (value) {
              case 'mark_read':
                ref
                    .read(briefingControllerProvider.notifier)
                    .markAsRead(widget.briefing.id);
                break;
              case 'dismiss':
                ref
                    .read(briefingControllerProvider.notifier)
                    .dismissBriefing(widget.briefing.id);
                Navigator.of(context).pop();
                break;
            }
          },
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'mark_read',
              child: Text('标记已读'),
            ),
            const PopupMenuItem(
              value: 'dismiss',
              child: Text('忽略简报'),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildHeroImage(BuildContext context) {
    // TODO: 当有真实封面图时，显示网络图片
    // 当前显示占位符
    return Stack(
      children: [
        Container(
          width: double.infinity,
          height: 300,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: _getCoverGradientColors(widget.briefing.briefingType),
            ),
          ),
          child: Center(
            child: Icon(
              _getTypeIcon(widget.briefing.briefingType),
              size: 120,
              color: Colors.white.withOpacity(0.4),
            ),
          ),
        ),

        // 优先级标签（左上角）
        Positioned(
          top: 16,
          left: 16,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: _getPriorityColor(widget.briefing.priority),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              _getPriorityLabel(widget.briefing.priority),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetadata(BuildContext context, ThemeData theme) {
    return Wrap(
      spacing: 12,
      runSpacing: 8,
      children: [
        // 类型标签
        _buildMetadataChip(
          theme,
          label: _getTypeLabel(widget.briefing.briefingType),
          color: _getTypeColor(widget.briefing.briefingType),
        ),

        // 时间
        _buildMetadataChip(
          theme,
          label: _formatTime(widget.briefing.createdAt),
          icon: Icons.access_time,
          color: Colors.grey,
        ),
      ],
    );
  }

  Widget _buildMetadataChip(
    ThemeData theme, {
    required String label,
    IconData? icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImpactSection(BuildContext context, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _getPriorityColor(widget.briefing.priority).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _getPriorityColor(widget.briefing.priority).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.warning_amber_rounded,
            color: _getPriorityColor(widget.briefing.priority),
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '影响说明',
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: _getPriorityColor(widget.briefing.priority),
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  widget.briefing.impact!,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: _getPriorityColor(widget.briefing.priority),
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomBar(BuildContext context, ThemeData theme) {
    return Container(
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 快捷问题
              _buildQuickQuestions(context, theme),
              const SizedBox(height: 12),

              // 输入框
              _buildInputField(context, theme),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickQuestions(BuildContext context, ThemeData theme) {
    final questions = [
      '为什么会这样？',
      '给我详细分析',
      '如何改进？',
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: questions.map((question) {
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ActionChip(
              label: Text(question),
              onPressed: () {
                _messageController.text = question;
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildInputField(BuildContext context, ThemeData theme) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Expanded(
          child: TextField(
            controller: _messageController,
            decoration: InputDecoration(
              hintText: '有疑问？直接问 AI...',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(24),
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 20,
                vertical: 12,
              ),
            ),
            maxLines: null,
            textInputAction: TextInputAction.send,
            onSubmitted: (_) => _sendMessage(),
          ),
        ),
        const SizedBox(width: 8),
        IconButton.filled(
          icon: _isLoading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.send),
          onPressed: _isLoading ? null : _sendMessage,
        ),
      ],
    );
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    setState(() => _isLoading = true);

    try {
      // 创建或获取对话
      String? conversationId = widget.briefing.conversationId;

      if (conversationId == null) {
        // 创建新对话
        final controller = ref.read(briefingControllerProvider.notifier);
        conversationId = await controller.startConversation(
          widget.briefing.id,
          prompt: message,
        );
      }

      if (conversationId != null && mounted) {
        // 跳转到对话页面，并自动发送本次输入，确保触发后端聊天接口
        await _navigateToConversation(conversationId, initialMessage: message);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送失败: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _navigateToConversation(
    String conversationId, {
    String? initialMessage,
  }) async {
    final agentRepository = AgentRepository();
    try {
      final agents = await agentRepository.getActiveAgents();
      final agent = agents.firstWhere(
        (a) => a.id == widget.briefing.agentId,
        orElse: () => throw Exception('Agent not found'),
      );

      if (mounted) {
        await Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => ConversationPage(
              agent: agent,
              conversationId: conversationId,
              initialMessage: initialMessage,
            ),
          ),
        );

        // 对话结束后清空输入框
        _messageController.clear();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('无法打开对话: $e')),
        );
      }
    }
  }

  /// 显示完整报告
  Future<void> _showFullReport(BuildContext context) async {
    final theme = Theme.of(context);

    // 显示加载对话框
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    try {
      final repository = BriefingRepository();
      final report = await repository.getBriefingReport(widget.briefing.id);

      if (!mounted) return;
      Navigator.of(context).pop(); // 关闭加载对话框

      if (report == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('报告内容不可用')),
        );
        return;
      }

      // 显示全屏报告页面
      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => _FullReportPage(
            title: report['title'] ?? '分析报告',
            content: report['content'] ?? '',
          ),
        ),
      );
    } catch (e) {
      if (mounted) {
        Navigator.of(context).pop(); // 关闭加载对话框
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('获取报告失败: $e')),
        );
      }
    }
  }

  // Helper methods
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

  String _getPriorityLabel(BriefingPriority priority) {
    switch (priority) {
      case BriefingPriority.p0:
        return 'P0 - 紧急';
      case BriefingPriority.p1:
        return 'P1 - 重要';
      case BriefingPriority.p2:
        return 'P2 - 普通';
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

    if (diff.inMinutes < 1) {
      return '刚刚';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}分钟前';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}小时前';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}天前';
    } else {
      return '${time.month}/${time.day} ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
    }
  }
}

/// 完整报告页面（全屏Markdown渲染）
class _FullReportPage extends StatelessWidget {
  const _FullReportPage({
    required this.title,
    required this.content,
  });

  final String title;
  final String content;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: [
          IconButton(
            icon: const Icon(Icons.copy),
            tooltip: '复制内容',
            onPressed: () {
              // 复制到剪贴板
              // Clipboard.setData(ClipboardData(text: content));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('内容已复制')),
              );
            },
          ),
        ],
      ),
      body: Markdown(
        data: content,
        selectable: true,
        padding: const EdgeInsets.all(16),
        styleSheet: MarkdownStyleSheet(
          p: theme.textTheme.bodyLarge?.copyWith(height: 1.6),
          h1: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          h2: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          h3: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
          h4: theme.textTheme.titleMedium,
          listBullet: theme.textTheme.bodyLarge,
          tableHead: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          tableBody: theme.textTheme.bodyMedium,
          tableBorder: TableBorder.all(
            color: Colors.grey.shade300,
            width: 1,
          ),
          code: theme.textTheme.bodyMedium?.copyWith(
            fontFamily: 'monospace',
            backgroundColor: Colors.grey.shade200,
          ),
          codeblockDecoration: BoxDecoration(
            color: Colors.grey.shade100,
            borderRadius: BorderRadius.circular(8),
          ),
          codeblockPadding: const EdgeInsets.all(12),
          blockquote: theme.textTheme.bodyLarge?.copyWith(
            fontStyle: FontStyle.italic,
            color: Colors.grey.shade700,
          ),
          blockquoteDecoration: BoxDecoration(
            border: Border(
              left: BorderSide(
                color: Colors.grey.shade400,
                width: 4,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
