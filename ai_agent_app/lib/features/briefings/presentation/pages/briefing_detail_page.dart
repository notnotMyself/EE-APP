import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../domain/models/briefing.dart';
import '../controllers/briefing_controller.dart';
import '../../../conversations/presentation/pages/conversation_page.dart';
import '../../../agents/data/agent_repository.dart';
import '../../data/briefing_repository.dart';
import '../widgets/dynamic_briefing_renderer.dart';

/// 报告章节数据类
class ReportSection {
  final String title;
  final String icon;
  final String content;
  final int level;
  
  const ReportSection({
    required this.title,
    required this.icon,
    required this.content,
    this.level = 2,
  });
}

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

  // ========================================
  // 报告内容解析和展示
  // ========================================
  
  /// 解析报告为结构化章节
  List<ReportSection> _parseReportSections() {
    final contextData = widget.briefing.contextData;
    String rawContent = widget.briefing.summary;
    
    // 尝试获取完整报告
    if (contextData != null) {
      final analysisResult = contextData['analysis_result'];
      if (analysisResult is Map<String, dynamic>) {
        final response = analysisResult['response'] as String?;
        if (response != null && response.isNotEmpty) {
          rawContent = response;
        }
      }
    }
    
    // 清理思考过程（开头的探索性内容）
    rawContent = _cleanThinkingProcess(rawContent);
    
    // 解析 Markdown 章节
    return _parseMarkdownSections(rawContent);
  }
  
  /// 清理 Agent 思考过程
  String _cleanThinkingProcess(String content) {
    final lines = content.split('\n');
    final cleanedLines = <String>[];
    bool foundRealContent = false;
    
    for (final line in lines) {
      final trimmed = line.trim();
      
      // 跳过开头的思考过程
      if (!foundRealContent) {
        // 找到第一个 ## 标题开始算正式内容
        if (trimmed.startsWith('## ') || trimmed.startsWith('# 研发效能')) {
          foundRealContent = true;
        } else if (_isThinkingLine(trimmed)) {
          continue; // 跳过思考行
        }
      }
      
      if (foundRealContent || trimmed.startsWith('#')) {
        cleanedLines.add(line);
      }
    }
    
    return cleanedLines.join('\n').trim();
  }
  
  bool _isThinkingLine(String line) {
    final patterns = [
      '我来', '让我', '首先', '接下来', '现在', '好的', '看起来',
      '需要先', '我需要', '执行', '脚本', '位置', '数据显示', '尝试'
    ];
    for (final p in patterns) {
      if (line.startsWith(p)) return true;
    }
    return false;
  }
  
  /// 解析 Markdown 为章节列表
  List<ReportSection> _parseMarkdownSections(String content) {
    final sections = <ReportSection>[];
    final lines = content.split('\n');
    
    String? currentTitle;
    String? currentIcon;
    final currentContent = StringBuffer();
    int sectionLevel = 0;
    
    for (final line in lines) {
      final trimmed = line.trim();
      
      // 检测 H2 标题（主章节）
      if (trimmed.startsWith('## ')) {
        // 保存上一个章节
        if (currentTitle != null) {
          sections.add(ReportSection(
            title: currentTitle,
            icon: currentIcon ?? '📌',
            content: currentContent.toString().trim(),
            level: sectionLevel,
          ));
        }
        
        // 开始新章节
        final titleText = trimmed.substring(3).trim();
        currentIcon = _extractEmoji(titleText);
        currentTitle = _removeEmoji(titleText);
        currentContent.clear();
        sectionLevel = 2;
      }
      // H3 标题作为子内容
      else if (trimmed.startsWith('### ')) {
        currentContent.writeln(line);
      }
      // 普通内容
      else {
        currentContent.writeln(line);
      }
    }
    
    // 保存最后一个章节
    if (currentTitle != null) {
      sections.add(ReportSection(
        title: currentTitle,
        icon: currentIcon ?? '📌',
        content: currentContent.toString().trim(),
        level: sectionLevel,
      ));
    }
    
    return sections;
  }
  
  String? _extractEmoji(String text) {
    final emojiRegex = RegExp(r'^[\p{Emoji}]+', unicode: true);
    final match = emojiRegex.firstMatch(text);
    return match?.group(0);
  }
  
  String _removeEmoji(String text) {
    return text.replaceFirst(RegExp(r'^[\p{Emoji}]+\s*', unicode: true), '').trim();
  }
  
  /// 判断章节是否默认展开
  bool _isDefaultExpanded(String title) {
    final expandedKeywords = ['核心发现', '关键发现', '关键指标', '建议行动', '建议'];
    return expandedKeywords.any((k) => title.contains(k));
  }
  
  /// 构建报告内容区域（优先使用 A2UI Schema）
  Widget _buildReportSections(BuildContext context, ThemeData theme) {
    final contextData = widget.briefing.contextData;

    // 1. 优先检查是否有 ui_schema，使用 A2UI 渲染
    if (contextData != null) {
      final uiSchema = contextData['ui_schema'];
      if (uiSchema is Map<String, dynamic>) {
        final content = uiSchema['content'];
        if (content is Map<String, dynamic>) {
          final sections = content['sections'];
          if (sections is List && sections.isNotEmpty) {
            return _buildA2UIContent(context, theme, sections, contextData);
          }
        }
      }
    }

    // 2. 回退到 Markdown 分章节展示
    final sections = _parseReportSections();

    // 如果没有解析到章节，显示原始 summary
    if (sections.isEmpty) {
      return MarkdownBody(
        data: widget.briefing.summary,
        selectable: true,
        styleSheet: _getMarkdownStyle(theme),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 章节列表
        for (int i = 0; i < sections.length; i++) ...[
          _buildSectionCard(context, theme, sections[i]),
          if (i < sections.length - 1) const SizedBox(height: 16),
        ],

        // 查看完整报告按钮
        const SizedBox(height: 24),
        Center(
          child: TextButton.icon(
            icon: Icon(Icons.article_outlined, size: 18, color: Colors.grey.shade600),
            label: Text(
              '查看原始报告',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            onPressed: () => _showFullReport(context),
          ),
        ),

        // 底部留白
        const SizedBox(height: 120),
      ],
    );
  }

  /// 构建 A2UI 内容（指标卡片、图表、表格等）
  Widget _buildA2UIContent(
    BuildContext context,
    ThemeData theme,
    List<dynamic> sections,
    Map<String, dynamic> contextData,
  ) {
    final renderer = DynamicBriefingRenderer();
    final uiSchemas = sections
        .whereType<Map<String, dynamic>>()
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // A2UI 动态组件渲染
        renderer.renderComponents(uiSchemas),

        const SizedBox(height: 24),

        // 详细分析（如果有 full_report）
        _buildDetailedAnalysis(context, theme, contextData),

        // 查看完整报告按钮
        const SizedBox(height: 24),
        Center(
          child: TextButton.icon(
            icon: Icon(Icons.article_outlined, size: 18, color: Colors.grey.shade600),
            label: Text(
              '查看原始报告',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            onPressed: () => _showFullReport(context),
          ),
        ),

        // 底部留白
        const SizedBox(height: 120),
      ],
    );
  }

  /// 构建详细分析区域（从 findings 生成）
  Widget _buildDetailedAnalysis(
    BuildContext context,
    ThemeData theme,
    Map<String, dynamic> contextData,
  ) {
    // 尝试获取 findings
    final findings = contextData['findings'] as List<dynamic>?;
    if (findings == null || findings.isEmpty) {
      return const SizedBox.shrink();
    }

    return _ExpandableSection(
      title: '详细发现',
      icon: '🔍',
      content: findings.map((f) {
        if (f is Map<String, dynamic>) {
          final title = f['title'] ?? f['finding'] ?? '';
          final detail = f['detail'] ?? '';
          final severity = f['severity'] ?? 'medium';
          final severityIcon = severity == 'high' ? '🔴' : (severity == 'medium' ? '🟡' : '🟢');
          return '- $severityIcon **$title**\n  $detail';
        }
        return '- $f';
      }).join('\n\n'),
      initiallyExpanded: true,
      theme: theme,
    );
  }
  
  /// 构建单个章节卡片
  Widget _buildSectionCard(BuildContext context, ThemeData theme, ReportSection section) {
    final isExpanded = _isDefaultExpanded(section.title);
    
    return _ExpandableSection(
      title: section.title,
      icon: section.icon,
      content: section.content,
      initiallyExpanded: isExpanded,
      theme: theme,
    );
  }
  
  /// 获取 Markdown 样式
  MarkdownStyleSheet _getMarkdownStyle(ThemeData theme) {
    return MarkdownStyleSheet(
      p: theme.textTheme.bodyLarge?.copyWith(height: 1.6),
      h1: theme.textTheme.headlineSmall,
      h2: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
      h3: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
      listBullet: theme.textTheme.bodyLarge,
      tableHead: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
      tableBody: theme.textTheme.bodyMedium,
      tableBorder: TableBorder.all(color: Colors.grey.shade300, width: 1),
      tableColumnWidth: const IntrinsicColumnWidth(),
      tableCellsPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      code: theme.textTheme.bodyMedium?.copyWith(
        fontFamily: 'monospace',
        backgroundColor: Colors.grey.shade100,
      ),
      codeblockDecoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(8),
      ),
      blockquoteDecoration: BoxDecoration(
        border: Border(left: BorderSide(color: theme.primaryColor, width: 4)),
      ),
      blockquotePadding: const EdgeInsets.only(left: 16),
    );
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

                      // 分层展示报告内容
                      _buildReportSections(context, theme),

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
    // 按优先级获取完整报告内容
    String content = widget.briefing.summary;
    String? reportSource;
    final contextData = widget.briefing.contextData;

    if (contextData != null) {
      // 优先级1: structured_data.full_report（技能返回的完整报告）
      final structuredData = contextData['structured_data'];
      if (structuredData is Map<String, dynamic>) {
        final fullReport = structuredData['full_report'] as String?;
        if (fullReport != null && fullReport.isNotEmpty) {
          content = fullReport;
          reportSource = '技能生成报告';
        }
      }

      // 优先级2: key_data.full_report
      if (reportSource == null) {
        final keyData = contextData['key_data'];
        if (keyData is Map<String, dynamic>) {
          final fullReport = keyData['full_report'] as String?;
          if (fullReport != null && fullReport.isNotEmpty) {
            content = fullReport;
            reportSource = '分析报告';
          }
        }
      }

      // 优先级3: analysis_result.response（AI原始响应）
      if (reportSource == null) {
        final analysisResult = contextData['analysis_result'];
        if (analysisResult is Map<String, dynamic>) {
          final response = analysisResult['response'] as String?;
          if (response != null && response.isNotEmpty) {
            content = response;
            reportSource = 'AI分析响应';
          }
        }
      }
    }

    // 如果有 reportArtifactId，尝试从服务器获取（优先级最高）
    if (widget.briefing.reportArtifactId != null) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(child: CircularProgressIndicator()),
      );

      try {
        final repository = BriefingRepository();
        final report = await repository.getBriefingReport(widget.briefing.id);

        if (!mounted) return;
        Navigator.of(context).pop();

        if (report != null && report['content'] != null) {
          content = report['content'];
          reportSource = '存档报告';
        }
      } catch (e) {
        if (mounted) Navigator.of(context).pop();
      }
    }

    if (!mounted) return;

    // 显示全屏报告页面
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => _FullReportPage(
          title: widget.briefing.title,
          content: content,
          reportSource: reportSource,
          createdAt: widget.briefing.createdAt,
        ),
      ),
    );
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
    this.reportSource,
    this.createdAt,
  });

  final String title;
  final String content;
  final String? reportSource;
  final DateTime? createdAt;

  String _formatDateTime(DateTime? time) {
    if (time == null) return '';
    return '${time.year}-${time.month.toString().padLeft(2, '0')}-${time.day.toString().padLeft(2, '0')} '
           '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: theme.textTheme.titleMedium),
            if (reportSource != null || createdAt != null)
              Text(
                [
                  if (reportSource != null) reportSource!,
                  if (createdAt != null) _formatDateTime(createdAt),
                ].join(' · '),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: Colors.grey.shade600,
                ),
              ),
          ],
        ),
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

/// 可展开/收起的章节组件
class _ExpandableSection extends StatefulWidget {
  final String title;
  final String icon;
  final String content;
  final bool initiallyExpanded;
  final ThemeData theme;

  const _ExpandableSection({
    required this.title,
    required this.icon,
    required this.content,
    required this.initiallyExpanded,
    required this.theme,
  });

  @override
  State<_ExpandableSection> createState() => _ExpandableSectionState();
}

class _ExpandableSectionState extends State<_ExpandableSection> {
  late bool _isExpanded;

  @override
  void initState() {
    super.initState();
    _isExpanded = widget.initiallyExpanded;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: widget.theme.cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.grey.shade200,
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题栏（可点击展开/收起）
          InkWell(
            onTap: () {
              setState(() {
                _isExpanded = !_isExpanded;
              });
            },
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              child: Row(
                children: [
                  Text(
                    widget.icon,
                    style: const TextStyle(fontSize: 20),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      widget.title,
                      style: widget.theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  AnimatedRotation(
                    turns: _isExpanded ? 0.5 : 0,
                    duration: const Duration(milliseconds: 200),
                    child: Icon(
                      Icons.keyboard_arrow_down,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          // 内容区域（展开时显示）
          AnimatedCrossFade(
            firstChild: const SizedBox.shrink(),
            secondChild: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Divider(height: 1, color: Colors.grey.shade200),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: MarkdownBody(
                    data: widget.content,
                    selectable: true,
                    styleSheet: MarkdownStyleSheet(
                      p: widget.theme.textTheme.bodyMedium?.copyWith(height: 1.6),
                      h3: widget.theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: widget.theme.primaryColor,
                      ),
                      listBullet: widget.theme.textTheme.bodyMedium,
                      tableHead: widget.theme.textTheme.bodySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      tableBody: widget.theme.textTheme.bodySmall,
                      tableBorder: TableBorder.all(
                        color: Colors.grey.shade300,
                        width: 1,
                      ),
                      tableColumnWidth: const IntrinsicColumnWidth(),
                      tableCellsPadding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      code: widget.theme.textTheme.bodySmall?.copyWith(
                        fontFamily: 'monospace',
                        backgroundColor: Colors.grey.shade100,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            crossFadeState: _isExpanded
                ? CrossFadeState.showSecond
                : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 200),
          ),
        ],
      ),
    );
  }
}
