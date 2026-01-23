import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../domain/models/conversation.dart';
import '../state/conversation_notifier.dart';
import '../state/conversation_state.dart';
import 'tool_execution_card.dart';

/// OPPO Sans 字体家族名称
const String _oppoSansFamily = 'OPPO Sans';

/// 优化的消息列表组件
///
/// 使用记忆化和选择性重建来优化性能：
/// - 只监听消息ID列表变化，不监听完整消息内容
/// - 每个消息使用独立的Widget，避免不必要的重建
/// - 流式消息使用RepaintBoundary隔离重绘
class OptimizedMessageList extends ConsumerWidget {
  final String conversationId;
  final ScrollController scrollController;

  const OptimizedMessageList({
    super.key,
    required this.conversationId,
    required this.scrollController,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 只监听消息ID列表，不监听完整消息
    final messageIds = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) => state.messages.map((m) => m.id).toList(),
      ),
    );

    // 监听流式状态
    final streamingState = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) => state.streamingState,
      ),
    );

    final isStreaming = streamingState is StreamingStateStreaming;
    final isWaiting = streamingState is StreamingStateWaiting;

    // 监听工具执行状态
    final toolState = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) => state.toolState,
      ),
    );

    // 判断是否需要显示工具状态卡片
    final showToolCard = toolState is! ToolExecutionStateIdle;

    return CustomScrollView(
      controller: scrollController,
      reverse: true,
      slivers: [
        // 工具执行状态卡片（在最顶部显示）
        if (showToolCard)
          SliverToBoxAdapter(
            child: ToolExecutionCard(toolState: toolState),
          ),

        // 等待AI响应的指示器（发送消息后立即显示）
        if (isWaiting && !isStreaming && !showToolCard)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: WaitingIndicator(),
            ),
          ),

        // 流式消息（正在生成中）
        if (isStreaming)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: StreamingMessageBubble(conversationId: conversationId),
            ),
          ),

        // 历史消息列表
        SliverList.builder(
          itemCount: messageIds.length,
          itemBuilder: (context, index) {
            // 反向索引（因为reverse: true）
            final messageId = messageIds[messageIds.length - 1 - index];
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: MemoizedMessageBubble(
                key: ValueKey(messageId),
                conversationId: conversationId,
                messageId: messageId,
              ),
            );
          },
        ),
      ],
    );
  }
}

/// 记忆化消息气泡
///
/// 只在特定消息内容变化时重建
class MemoizedMessageBubble extends ConsumerWidget {
  final String conversationId;
  final String messageId;

  const MemoizedMessageBubble({
    super.key,
    required this.conversationId,
    required this.messageId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 只选择特定消息
    final message = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) => state.messages.firstWhere(
          (m) => m.id == messageId,
          orElse: () => Message(
            id: messageId,
            conversationId: conversationId,
            role: 'unknown',
            content: '',
            createdAt: DateTime.now(),
          ),
        ),
      ),
    );

    return MessageBubbleContent(message: message);
  }
}

/// 流式消息气泡
///
/// 使用RepaintBoundary隔离重绘，避免影响其他消息
class StreamingMessageBubble extends ConsumerWidget {
  final String conversationId;

  const StreamingMessageBubble({
    super.key,
    required this.conversationId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 使用单个 select 同时获取流式内容和最新消息，避免状态不同步
    final data = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) {
          final streamingContent = state.streamingState.maybeMap(
            streaming: (s) => s.content,
            orElse: () => null,
          );
          // 获取最新的 assistant 消息内容，用于去重检查
          final lastAssistantContent = state.messages.isNotEmpty &&
                  state.messages.last.role == 'assistant'
              ? state.messages.last.content
              : null;
          return (streamingContent, lastAssistantContent);
        },
      ),
    );

    final streamingContent = data.$1;
    final lastAssistantContent = data.$2;

    // 如果没有流式内容，不显示
    if (streamingContent == null || streamingContent.isEmpty) {
      return const SizedBox.shrink();
    }

    // 防止重复：如果流式内容与最新消息内容相同，说明消息已经添加到列表，不再显示流式气泡
    if (lastAssistantContent != null && lastAssistantContent == streamingContent) {
      return const SizedBox.shrink();
    }

    return RepaintBoundary(
      child: MessageBubbleContent(
        message: Message(
          id: 'streaming',
          conversationId: conversationId,
          role: 'assistant',
          content: streamingContent,
          createdAt: DateTime.now(),
        ),
        isStreaming: true,
      ),
    );
  }
}

/// 消息气泡内容
/// 
/// Figma设计规范：
/// - 用户消息：蓝色背景(0xFF2C69FF) + 白色文字
/// - AI消息：白色背景 + 深色文字
class MessageBubbleContent extends StatefulWidget {
  final Message message;
  final bool isStreaming;

  const MessageBubbleContent({
    super.key,
    required this.message,
    this.isStreaming = false,
  });

  @override
  State<MessageBubbleContent> createState() => _MessageBubbleContentState();
}

class _MessageBubbleContentState extends State<MessageBubbleContent> {

  @override
  Widget build(BuildContext context) {
    final isUser = widget.message.role == 'user';

    // Figma设计规范：用户蓝色，AI白色
    final backgroundColor = isUser
        ? const Color(0xFF2C69FF)  // 用户消息：蓝色
        : Colors.white;            // AI消息：白色
    
    final textColor = isUser
        ? Colors.white             // 用户消息：白色文字
        : const Color(0xFF1A1A1A); // AI消息：深色文字

    final borderRadius = BorderRadius.circular(24); // Figma design radius

    return Column(
      crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
      children: [
        Align(
          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.8,
              ),
              decoration: ShapeDecoration(
                color: backgroundColor,
                shape: RoundedRectangleBorder(
                  borderRadius: borderRadius,
                ),
                // AI消息添加轻微阴影，增强层次感
                shadows: isUser ? null : [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // 消息文本内容
                  if (isUser) ...[
                    if (widget.message.content.isNotEmpty)
                      Text(
                        widget.message.content,
                        textAlign: TextAlign.justify,
                        style: TextStyle(
                          fontFamily: _oppoSansFamily,
                          color: textColor,
                          fontSize: 14,
                          fontWeight: FontWeight.w400,
                          height: 1.40,
                        ),
                      ),
                    // 显示附件（用户消息）
                    if (widget.message.attachments != null && widget.message.attachments!.isNotEmpty) ...[
                      if (widget.message.content.isNotEmpty) const SizedBox(height: 10),
                      _buildAttachments(context, widget.message.attachments!),
                    ],
                  ] else ...[
                    // AI消息使用Markdown渲染
                    MarkdownBody(
                      data: widget.message.content,
                      styleSheet: MarkdownStyleSheet(
                        p: TextStyle(
                          fontFamily: _oppoSansFamily,
                          color: textColor,
                          fontSize: 14,
                          fontWeight: FontWeight.w400,
                          height: 1.50,
                        ),
                        h1: TextStyle(
                          fontFamily: _oppoSansFamily,
                          color: textColor,
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                        ),
                        h2: TextStyle(
                          fontFamily: _oppoSansFamily,
                          color: textColor,
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                        h3: TextStyle(
                          fontFamily: _oppoSansFamily,
                          color: textColor,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                        code: TextStyle(
                          backgroundColor: const Color(0xFFF5F5F5),
                          fontSize: 13,
                          color: const Color(0xFF333333),
                          fontFamily: 'monospace',
                        ),
                        codeblockDecoration: BoxDecoration(
                          color: const Color(0xFFF5F5F5),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        listBullet: TextStyle(
                          fontFamily: _oppoSansFamily,
                          color: textColor,
                        ),
                        blockquoteDecoration: BoxDecoration(
                          border: Border(
                            left: BorderSide(
                              color: const Color(0xFF2C69FF),
                              width: 3,
                            ),
                          ),
                        ),
                      ),
                      selectable: true,
                    ),
                  ],
                  // 流式传输指示器
                  if (widget.isStreaming) ...[
                    const SizedBox(height: 8),
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation(
                          isUser ? Colors.white : const Color(0xFF2C69FF),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        // AI消息操作按钮（复制、转发、保存）- 固定显示
        if (!isUser && !widget.isStreaming) ...[
          const SizedBox(height: 8),
          _buildMessageActions(context),
        ],
      ],
    );
  }

  /// 构建消息操作按钮（复制、转发、保存）
  /// 基于 Figma message_button 设计
  Widget _buildMessageActions(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 复制按钮
        _buildSvgActionButton(
          assetPath: 'assets/icons/copy.svg',
          onTap: () => _handleCopy(context),
        ),
        const SizedBox(width: 9),
        // 转发按钮
        _buildSvgActionButton(
          assetPath: 'assets/icons/forward.svg',
          onTap: () => _showDevelopingDialog(context, '转发'),
        ),
        const SizedBox(width: 9),
        // 保存按钮
        _buildSvgActionButton(
          assetPath: 'assets/icons/save.svg',
          onTap: () => _showDevelopingDialog(context, '保存'),
        ),
      ],
    );
  }

  /// 操作按钮样式（使用 SVG 图标，基于 Figma 规范）
  Widget _buildSvgActionButton({
    required String assetPath,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 36,
        height: 36,
        clipBehavior: Clip.antiAlias,
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.04),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(90),
          ),
        ),
        child: Center(
          child: SvgPicture.asset(
            assetPath,
            width: 15,
            height: 15,
            colorFilter: ColorFilter.mode(
              Colors.black.withOpacity(0.9),
              BlendMode.srcIn,
            ),
          ),
        ),
      ),
    );
  }

  /// 复制消息内容
  void _handleCopy(BuildContext context) {
    Clipboard.setData(ClipboardData(text: widget.message.content));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('已复制到剪贴板'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  /// 显示正在开发中对话框
  void _showDevelopingDialog(BuildContext context, String feature) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        title: Row(
          children: [
            Icon(
              Icons.construction_rounded,
              color: const Color(0xFF2C69FF),
              size: 24,
            ),
            const SizedBox(width: 8),
            Text(
              '$feature功能',
              style: const TextStyle(
                fontFamily: _oppoSansFamily,
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        content: Text(
          '正在开发中，敬请期待...',
          style: TextStyle(
            fontFamily: _oppoSansFamily,
            fontSize: 14,
            color: Colors.black.withOpacity(0.6),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(
              '知道了',
              style: TextStyle(fontFamily: _oppoSansFamily),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建附件展示区域
  /// Figma设计规范：图片缩略图43x43，圆角4px，间距3px
  Widget _buildAttachments(BuildContext context, List<Map<String, dynamic>> attachments) {
    return Container(
      width: double.infinity,
      child: Wrap(
        spacing: 3,
        runSpacing: 3,
        children: attachments.map((attachment) {
          final url = attachment['url'] as String?;
          if (url == null || url.isEmpty) return const SizedBox.shrink();

          return _AttachmentThumbnail(url: url);
        }).toList(),
      ),
    );
  }
}

/// 附件缩略图组件
/// 
/// 支持本地文件和网络URL，兼容 Web 和移动端
class _AttachmentThumbnail extends StatelessWidget {
  final String url;

  const _AttachmentThumbnail({required this.url});

  @override
  Widget build(BuildContext context) {
    // 判断是本地文件还是网络URL
    final isNetworkUrl = url.startsWith('http://') || url.startsWith('https://');
    final isLocalFile = !isNetworkUrl && (url.startsWith('/') || url.startsWith('file://') || url.startsWith('blob:'));
    final cleanPath = url.startsWith('file://') ? url.substring(7) : url;

    return Container(
      width: 43,
      height: 43,
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.04),
        borderRadius: BorderRadius.circular(4),
      ),
      clipBehavior: Clip.antiAlias,
      child: _buildImage(isNetworkUrl, isLocalFile, cleanPath),
    );
  }

  Widget _buildImage(bool isNetworkUrl, bool isLocalFile, String cleanPath) {
    if (isNetworkUrl) {
      // 网络URL
      return Image.network(
        url,
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => _buildImagePlaceholder(),
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return Center(
            child: SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                value: loadingProgress.expectedTotalBytes != null
                    ? loadingProgress.cumulativeBytesLoaded /
                        loadingProgress.expectedTotalBytes!
                    : null,
              ),
            ),
          );
        },
      );
    } else if (isLocalFile) {
      // 本地文件 - Web 平台使用 blob URL，移动端使用 File
      if (url.startsWith('blob:')) {
        // Web 平台的 blob URL 可以直接用 Image.network
        return Image.network(
          url,
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => _buildImagePlaceholder(),
        );
      } else {
        // 移动端使用 File
        return Image.file(
          File(cleanPath),
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => _buildImagePlaceholder(),
        );
      }
    } else {
      return _buildImagePlaceholder();
    }
  }

  Widget _buildImagePlaceholder() {
    return Container(
      color: Colors.black.withOpacity(0.04),
      child: const Icon(
        Icons.image_outlined,
        size: 20,
        color: Colors.grey,
      ),
    );
  }
}

/// 连接状态指示器
class ConnectionStatusIndicator extends ConsumerWidget {
  final String conversationId;

  const ConnectionStatusIndicator({
    super.key,
    required this.conversationId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectionState = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) => state.connectionState,
      ),
    );

    return connectionState.when(
      disconnected: () => _buildIndicator(
        context,
        icon: Icons.cloud_off,
        color: Colors.grey,
        text: '未连接',
      ),
      connecting: () => _buildIndicator(
        context,
        icon: Icons.cloud_queue,
        color: Colors.orange,
        text: '连接中...',
      ),
      connected: () => _buildIndicator(
        context,
        icon: Icons.cloud_done,
        color: Colors.green,
        text: '已连接',
      ),
      reconnecting: (attempt) => _buildIndicator(
        context,
        icon: Icons.cloud_sync,
        color: Colors.orange,
        text: '重连中 ($attempt)',
      ),
    );
  }

  Widget _buildIndicator(
    BuildContext context, {
    required IconData icon,
    required Color color,
    required String text,
  }) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(
            fontFamily: _oppoSansFamily,
            color: color,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}

/// 等待AI响应的指示器
///
/// 在用户发送消息后立即显示，让用户知道系统正在处理
/// 优化：使用蓝色主题色，添加友好的文字提示
class WaitingIndicator extends StatefulWidget {
  const WaitingIndicator({super.key});

  @override
  State<WaitingIndicator> createState() => _WaitingIndicatorState();
}

class _WaitingIndicatorState extends State<WaitingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  // 品牌蓝色
  static const Color _brandBlue = Color(0xFF2C69FF);

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
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 三个跳动的点
            _buildDot(0),
            const SizedBox(width: 4),
            _buildDot(1),
            const SizedBox(width: 4),
            _buildDot(2),
            const SizedBox(width: 10),
            // 友好的文字提示
            Text(
              '正在思考...',
              style: TextStyle(
                fontFamily: _oppoSansFamily,
                color: Colors.black.withOpacity(0.5),
                fontSize: 13,
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDot(int index) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        // 错开动画时间
        final delay = index * 0.2;
        final value = ((_controller.value + delay) % 1.0);
        // 使用 sin 曲线实现上下跳动
        final offset = (value < 0.5)
            ? (value * 2) // 0 -> 1
            : (2 - value * 2); // 1 -> 0

        return Transform.translate(
          offset: Offset(0, -3 * offset),
          child: Container(
            width: 7,
            height: 7,
            decoration: BoxDecoration(
              color: _brandBlue.withOpacity(0.5 + 0.5 * offset),
              shape: BoxShape.circle,
            ),
          ),
        );
      },
    );
  }
}
