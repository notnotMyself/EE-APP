import 'dart:io';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../controllers/conversation_controller.dart';
import '../../data/conversation_repository.dart';
import '../../domain/models/conversation.dart';
import '../../../agents/domain/models/agent.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';

class ConversationPage extends ConsumerStatefulWidget {
  const ConversationPage({
    super.key,
    required this.agent,
    this.conversationId,
    this.initialMessage,
  });

  final Agent agent;
  final String? conversationId;
  final String? initialMessage;

  @override
  ConsumerState<ConversationPage> createState() => _ConversationPageState();
}

class _ConversationPageState extends ConsumerState<ConversationPage> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  String? _currentConversationId;
  List<Message> _messages = [];
  bool _isStreaming = false;
  String _streamingContent = '';
  bool _initialMessageSent = false;

  @override
  void initState() {
    super.initState();
    _currentConversationId = widget.conversationId;

    // 使用 addPostFrameCallback 在 build 完成后初始化对话
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeConversation();
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _initializeConversation() async {
    if (_currentConversationId != null) {
      await _loadMessages();
    } else {
      await _createNewConversation();
    }

    final initial = widget.initialMessage?.trim();
    if (!_initialMessageSent && initial != null && initial.isNotEmpty) {
      _initialMessageSent = true;
      await _sendMessageText(initial);
    }
  }

  Future<void> _sendMessageText(String text) async {
    if (text.trim().isEmpty) return;

    if (_currentConversationId == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('对话未初始化，请重试')),
        );
      }
      return;
    }

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

    final userMessage = text.trim();

    setState(() {
      _messages.add(Message(
        id: 'temp-${DateTime.now().millisecondsSinceEpoch}',
        conversationId: _currentConversationId!,
        role: 'user',
        content: userMessage,
        createdAt: DateTime.now(),
      ));
      _isStreaming = true;
      _streamingContent = '';
    });

    _scrollToBottom();

    try {
      final repository = ref.read(conversationRepositoryProvider);
      String fullResponse = '';

      // 使用带重试机制的流式接口
      await for (final chunk in repository.sendMessageStreamWithRetry(
        conversationId: _currentConversationId!,
        newMessage: userMessage,
        maxRetries: 3,
        timeout: const Duration(seconds: 60),
      )) {
        fullResponse += chunk;
        setState(() {
          _streamingContent = fullResponse;
        });
        _scrollToBottom();
      }

      setState(() {
        _messages.add(Message(
          id: 'temp-ai-${DateTime.now().millisecondsSinceEpoch}',
          conversationId: _currentConversationId!,
          role: 'assistant',
          content: fullResponse,
          createdAt: DateTime.now(),
        ));
        _isStreaming = false;
        _streamingContent = '';
      });

      _scrollToBottom();
    } on SocketException catch (e) {
      print('Network error: $e');

      setState(() {
        _isStreaming = false;
        _streamingContent = '';
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('网络连接失败，请检查网络后重试'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
            action: SnackBarAction(
              label: '重试',
              textColor: Colors.white,
              onPressed: () => _sendMessageText(userMessage),
            ),
          ),
        );
      }
    } catch (e, stackTrace) {
      print('Error sending message: $e');
      print('StackTrace: $stackTrace');

      setState(() {
        _isStreaming = false;
        _streamingContent = '';
      });

      if (mounted) {
        // 根据错误类型提供不同的提示
        String errorMessage = '发送消息失败';
        if (e.toString().contains('超时')) {
          errorMessage = '请求超时，请检查网络连接';
        } else if (e.toString().contains('网络')) {
          errorMessage = '网络连接失败，请检查网络设置';
        } else if (e.toString().contains('401') || e.toString().contains('认证')) {
          errorMessage = '登录已过期，请重新登录';
        } else {
          errorMessage = '发送消息失败: ${e.toString()}';
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
            action: SnackBarAction(
              label: '重试',
              textColor: Colors.white,
              onPressed: () => _sendMessageText(userMessage),
            ),
          ),
        );
      }
    }
  }

  Future<void> _createNewConversation() async {
    final currentUser = ref.read(currentUserProvider);
    if (currentUser == null) {
      print('Error: currentUser is null');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('请先登录')),
        );
      }
      return;
    }

    try {
      print('Creating conversation for agent: ${widget.agent.id}');
      final conversation = await ref
          .read(conversationControllerProvider.notifier)
          .createConversation(widget.agent.id);

      if (conversation != null) {
        print('Conversation created: ${conversation.id}');
        setState(() {
          _currentConversationId = conversation.id;
        });
      } else {
        print('Failed to create conversation');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('创建对话失败')),
          );
        }
      }
    } catch (e) {
      print('Error creating conversation: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('创建对话失败: $e')),
        );
      }
    }
  }

  Future<void> _loadMessages() async {
    if (_currentConversationId == null) return;

    try {
      final repository = ref.read(conversationRepositoryProvider);
      final messages = await repository.getMessages(_currentConversationId!);

      setState(() {
        _messages = messages;
      });

      _scrollToBottom();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载消息失败: $e')),
        );
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    if (_currentConversationId == null) {
      print('Error: _currentConversationId is null');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('对话未初始化，请重试')),
        );
      }
      return;
    }

    final userMessage = _messageController.text.trim();
    _messageController.clear();
    await _sendMessageText(userMessage);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.agent.name),
            Text(
              widget.agent.role,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isStreaming ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length && _isStreaming) {
                  return MessageBubble(
                    message: Message(
                      id: 'streaming',
                      conversationId: _currentConversationId!,
                      role: 'assistant',
                      content: _streamingContent,
                      createdAt: DateTime.now(),
                    ),
                    isStreaming: true,
                  );
                }

                return MessageBubble(message: _messages[index]);
              },
            ),
          ),

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
                    enabled: !_isStreaming,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _isStreaming ? null : _sendMessage,
                  icon: _isStreaming
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

class MessageBubble extends StatelessWidget {
  const MessageBubble({
    super.key,
    required this.message,
    this.isStreaming = false,
  });

  final Message message;
  final bool isStreaming;

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == 'user';

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Icon(
                Icons.psychology,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser
                    ? Theme.of(context).colorScheme.primary
                    : Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.content,
                    style: TextStyle(
                      color: isUser
                          ? Theme.of(context).colorScheme.onPrimary
                          : Theme.of(context).colorScheme.onSurface,
                    ),
                  ),
                  if (isStreaming)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: SizedBox(
                        width: 12,
                        height: 12,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Theme.of(context).colorScheme.primary,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundColor: Theme.of(context).colorScheme.primary,
              child: Icon(
                Icons.person,
                color: Theme.of(context).colorScheme.onPrimary,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
