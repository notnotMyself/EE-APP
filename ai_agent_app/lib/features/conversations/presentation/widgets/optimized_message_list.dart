import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import '../../domain/models/conversation.dart';
import '../state/conversation_notifier.dart';
import '../state/conversation_state.dart';

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

    final isStreaming = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) => state.streamingState is StreamingStateStreaming,
      ),
    );

    return CustomScrollView(
      controller: scrollController,
      reverse: true,
      slivers: [
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
    final streamingContent = ref.watch(
      conversationNotifierProvider(conversationId).select(
        (state) => state.streamingState.maybeMap(
          streaming: (s) => s.content,
          orElse: () => null,
        ),
      ),
    );

    if (streamingContent == null || streamingContent.isEmpty) {
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
class MessageBubbleContent extends StatelessWidget {
  final Message message;
  final bool isStreaming;

  const MessageBubbleContent({
    super.key,
    required this.message,
    this.isStreaming = false,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == 'user';
    final theme = Theme.of(context);

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        decoration: BoxDecoration(
          color: isUser
              ? theme.colorScheme.primary
              : theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (isUser)
              Text(
                message.content,
                style: TextStyle(
                  color: theme.colorScheme.onPrimary,
                  fontSize: 15,
                ),
              )
            else
              MarkdownBody(
                data: message.content,
                styleSheet: MarkdownStyleSheet(
                  p: TextStyle(
                    color: theme.colorScheme.onSurface,
                    fontSize: 15,
                    height: 1.5,
                  ),
                  code: TextStyle(
                    backgroundColor: theme.colorScheme.surfaceContainerHigh,
                    fontSize: 13,
                  ),
                  codeblockDecoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHigh,
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                selectable: true,
              ),
            if (isStreaming) ...[
              const SizedBox(height: 8),
              SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation(
                    theme.colorScheme.primary,
                  ),
                ),
              ),
            ],
          ],
        ),
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
            color: color,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}
