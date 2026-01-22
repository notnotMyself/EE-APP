import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../controllers/conversation_controller.dart';
import '../../../agents/domain/models/agent.dart';
import '../../../agents/presentation/widgets/expanded_chat_input.dart';
import '../../../agents/presentation/services/image_upload_service.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';
import '../state/conversation_notifier.dart';
import '../state/conversation_state.dart';
import '../widgets/optimized_message_list.dart';

/// 对话页面（优化版）
///
/// 使用新的WebSocket通信和批量状态更新。
class ConversationPage extends ConsumerStatefulWidget {
  const ConversationPage({
    super.key,
    required this.agent,
    this.conversationId,
    this.initialMessage,
    this.initialAttachments,
  });

  final Agent agent;
  final String? conversationId;
  final String? initialMessage;
  final List<ChatAttachment>? initialAttachments;

  @override
  ConsumerState<ConversationPage> createState() => _ConversationPageState();
}

class _ConversationPageState extends ConsumerState<ConversationPage> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  String? _currentConversationId;
  bool _initialMessageSent = false;
  bool _isInitializing = true;

  @override
  void initState() {
    super.initState();
    _currentConversationId = widget.conversationId;

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeConversation();
    });
  }

  @override
  void dispose() {
    // 主动释放 conversation notifier，确保 WS 连接被关闭，避免残留连接导致后端互相替换/重连循环
    if (_currentConversationId != null) {
      ref.invalidate(conversationNotifierProvider(_currentConversationId!));
    }
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _initializeConversation() async {
    if (_currentConversationId == null) {
      await _createNewConversation();
    }

    if (_currentConversationId != null) {
      // 初始化状态管理器
      await ref
          .read(conversationNotifierProvider(_currentConversationId!).notifier)
          .initialize();

      setState(() {
        _isInitializing = false;
      });

      // 发送初始消息（带附件）
      final initial = widget.initialMessage?.trim();
      final attachments = widget.initialAttachments;
      if (!_initialMessageSent && (initial != null && initial.isNotEmpty || attachments != null && attachments.isNotEmpty)) {
        _initialMessageSent = true;
        await _sendMessageWithAttachments(initial ?? '', attachments ?? []);
      }
    }
  }

  Future<void> _createNewConversation() async {
    final currentUser = ref.read(currentUserProvider);
    if (currentUser == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('请先登录')),
        );
      }
      return;
    }

    try {
      final conversation = await ref
          .read(conversationControllerProvider.notifier)
          .createConversation(widget.agent.id);

      if (conversation != null) {
        setState(() {
          _currentConversationId = conversation.id;
        });
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('创建对话失败')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('创建对话失败: $e')),
        );
      }
    }
  }

  Future<void> _sendMessageText(String text) async {
    if (text.trim().isEmpty || _currentConversationId == null) return;
    await _sendMessageWithAttachments(text.trim(), []);
  }

  Future<void> _sendMessageWithAttachments(String text, List<ChatAttachment> attachments) async {
    if ((text.trim().isEmpty && attachments.isEmpty) || _currentConversationId == null) return;

    // 检查网络连接
    final connectivityResult = await Connectivity().checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('无网络连接，请检查您的网络设置'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 3),
          ),
        );
      }
      return;
    }

    try {
      // 上传附件
      List<Map<String, dynamic>>? uploadedAttachments;
      if (attachments.isNotEmpty) {
        final uploadService = ref.read(imageUploadServiceProvider);
        final uploaded = await uploadService.uploadAttachments(attachments);
        uploadedAttachments = uploaded
            .where((a) => a.isUploaded)
            .map((a) => a.toJson())
            .toList();
      }

      await ref
          .read(conversationNotifierProvider(_currentConversationId!).notifier)
          .sendMessageWithAttachments(text.trim(), uploadedAttachments);

      _scrollToBottom();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('发送消息失败: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
            action: SnackBarAction(
              label: '重试',
              textColor: Colors.white,
              onPressed: () => _sendMessageWithAttachments(text, attachments),
            ),
          ),
        );
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.jumpTo(0);
      }
    });
  }

  Future<void> _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    final userMessage = _messageController.text.trim();
    _messageController.clear();
    await _sendMessageText(userMessage);
  }

  @override
  Widget build(BuildContext context) {
    // 监听流式状态以判断是否正在发送
    final isStreaming = _currentConversationId != null
        ? ref.watch(
            conversationNotifierProvider(_currentConversationId!).select(
              (state) => state.streamingState is StreamingStateStreaming,
            ),
          )
        : false;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.agent.name),
            Row(
              children: [
                Text(
                  widget.agent.role,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                if (_currentConversationId != null) ...[
                  const SizedBox(width: 8),
                  ConnectionStatusIndicator(
                    conversationId: _currentConversationId!,
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: _isInitializing
                ? const Center(child: CircularProgressIndicator())
                : _currentConversationId == null
                    ? const Center(child: Text('正在创建对话...'))
                    : OptimizedMessageList(
                        conversationId: _currentConversationId!,
                        scrollController: _scrollController,
                      ),
          ),

          // 输入框
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              border: Border(
                top: BorderSide(
                  color: Theme.of(context).dividerColor,
                ),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: '输入消息...',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: null,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                    enabled: !isStreaming,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: isStreaming ? null : _sendMessage,
                  icon: isStreaming
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
