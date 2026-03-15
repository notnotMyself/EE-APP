import 'package:flutter_svg/flutter_svg.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../../core/theme/figma_tokens.dart';
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
  bool _hasInputText = false;

  @override
  void initState() {
    super.initState();
    _currentConversationId = widget.conversationId;
    _messageController.addListener(_onTextChanged);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeConversation();
    });
  }

  void _onTextChanged() {
    final hasText = _messageController.text.trim().isNotEmpty;
    if (hasText != _hasInputText) {
      setState(() {
        _hasInputText = hasText;
      });
    }
  }

  @override
  void dispose() {
    // 主动释放 conversation notifier，确保 WS 连接被关闭，避免残留连接导致后端互相替换/重连循环
    if (_currentConversationId != null) {
      ref.invalidate(conversationNotifierProvider(_currentConversationId!));
    }
    _messageController.removeListener(_onTextChanged);
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
    // 直接从 Supabase 检查用户登录状态（避免 StreamProvider 时序问题）
    final currentUser = Supabase.instance.client.auth.currentUser;
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
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(FigmaTokens.navBarHeight),
        child: SafeArea(
          child: Container(
            width: double.infinity,
            height: FigmaTokens.navBarHeight,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Left: back button + agent name
                Expanded(
                  child: SizedBox(
                    height: FigmaTokens.navBarHeight,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // Back button - 48px touch area, 40x40 circle
                        GestureDetector(
                          onTap: () => Navigator.of(context).pop(),
                          behavior: HitTestBehavior.opaque,
                          child: SizedBox(
                            width: FigmaTokens.navButtonTouchArea,
                            height: FigmaTokens.navBarHeight,
                            child: Center(
                              child: Container(
                                width: FigmaTokens.navButtonSize,
                                height: FigmaTokens.navButtonSize,
                                decoration: ShapeDecoration(
                                  color: FigmaTokens.containerThin,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(FigmaTokens.radiusPill),
                                  ),
                                ),
                                child: SvgPicture.asset(
                                  'assets/icons/chat/back_arrow.svg',
                                  width: FigmaTokens.navButtonSize,
                                  height: FigmaTokens.navButtonSize,
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Agent name
                        Expanded(
                          child: Container(
                            constraints: const BoxConstraints(minHeight: FigmaTokens.navBarHeight),
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            alignment: Alignment.centerLeft,
                            child: Text(
                              widget.agent.name,
                              style: FigmaTokens.titleMMedium.copyWith(
                                color: FigmaTokens.labelPrimary,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Right: add new conversation + history
                SizedBox(
                  height: FigmaTokens.navBarHeight,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    mainAxisAlignment: MainAxisAlignment.end,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      // Add new conversation button
                      GestureDetector(
                        onTap: () {
                          _createNewConversation();
                        },
                        behavior: HitTestBehavior.opaque,
                        child: SizedBox(
                          width: FigmaTokens.navButtonTouchArea,
                          height: FigmaTokens.navBarHeight,
                          child: Center(
                            child: Container(
                              width: FigmaTokens.navButtonSize,
                              height: FigmaTokens.navButtonSize,
                              decoration: ShapeDecoration(
                                color: FigmaTokens.containerThin,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(FigmaTokens.radiusPill),
                                ),
                              ),
                              child: SvgPicture.asset(
                                'assets/icons/chat/add_circle.svg',
                                width: FigmaTokens.navButtonSize,
                                height: FigmaTokens.navButtonSize,
                              ),
                            ),
                          ),
                        ),
                      ),
                      // History button
                      GestureDetector(
                        onTap: () {
                          // TODO: Handle history
                        },
                        behavior: HitTestBehavior.opaque,
                        child: SizedBox(
                          width: FigmaTokens.navButtonTouchArea,
                          height: FigmaTokens.navBarHeight,
                          child: Center(
                            child: Container(
                              width: FigmaTokens.navButtonSize,
                              height: FigmaTokens.navButtonSize,
                              decoration: ShapeDecoration(
                                color: FigmaTokens.containerThin,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(FigmaTokens.radiusPill),
                                ),
                              ),
                              alignment: Alignment.center,
                              child: SvgPicture.asset(
                                'assets/icons/chat/history.svg',
                                width: 24,
                                height: 24,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
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
          SafeArea(
            top: false,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Container(
                height: FigmaTokens.inputHeight,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: FigmaTokens.containerThin,
                  borderRadius: BorderRadius.circular(FigmaTokens.inputRadius),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _messageController,
                        decoration: InputDecoration(
                          hintText: '简单描述下方案背景与目标',
                          hintStyle: TextStyle(
                            color: FigmaTokens.labelPlaceholder,
                            fontSize: 14,
                            fontFamily: FigmaTokens.fontPrimary,
                            fontWeight: FontWeight.w400,
                          ),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.zero,
                          isDense: true,
                        ),
                        style: TextStyle(
                          color: FigmaTokens.labelPrimary,
                          fontSize: 14,
                          fontFamily: FigmaTokens.fontPrimary,
                          fontWeight: FontWeight.w400,
                        ),
                        maxLines: 1,
                        textInputAction: TextInputAction.send,
                        onSubmitted: (_) => _sendMessage(),
                        enabled: !isStreaming,
                      ),
                    ),
                    const SizedBox(width: 8),
                    if (isStreaming)
                      const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    else if (_hasInputText)
                      GestureDetector(
                        onTap: _sendMessage,
                        child: const Icon(
                          Icons.send_rounded,
                          color: FigmaTokens.labelSecondary,
                          size: 24,
                        ),
                      )
                    else
                      const Icon(
                        Icons.mic_none_rounded,
                        color: FigmaTokens.labelSecondary,
                        size: 24,
                      ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
