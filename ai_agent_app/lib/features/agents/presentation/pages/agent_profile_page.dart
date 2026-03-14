import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../domain/models/agent.dart';
import '../../../conversations/domain/models/conversation.dart';
import '../../../conversations/presentation/controllers/conversation_controller.dart';
import '../../../conversations/presentation/state/conversation_notifier.dart';
import '../../../conversations/presentation/state/conversation_state.dart';
import '../../../conversations/presentation/widgets/optimized_message_list.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';
import '../services/attachment_service.dart';
import '../services/image_upload_service.dart';
import '../theme/agent_profile_theme.dart';
import '../widgets/agent_avatar.dart';
import '../widgets/app_selector_popup.dart';
import '../widgets/expanded_chat_input.dart';
import '../widgets/personality_selector.dart';
import '../widgets/quick_action_button.dart';
import '../widgets/agent_profile_card.dart';
import '../widgets/conversation_selector.dart';
import '../widgets/voice_input_dialog.dart';

/// 全局聊天模式状态 Provider
///
/// 当用户进入聊天模式（有消息）时设为 true，
/// MainScaffold 监听此 Provider 来决定是否隐藏底部导航栏
final chatModeActiveProvider = StateProvider<bool>((ref) => false);

/// Debug 模拟键盘弹起状态 Provider
///
/// 仅用于 Web/桌面端调试，模拟手机键盘弹起效果。
/// 在 kDebugMode 下可通过 MainScaffold 的调试按钮切换。
final debugKeyboardVisibleProvider = StateProvider<bool>((ref) => false);

/// AI员工详情页面（整合对话功能）
///
/// 基于 Figma 设计稿实现，展示AI员工信息和对话功能
/// 当用户开始对话后，页面会转换为对话模式，但保持设计风格一致
class AgentProfilePage extends ConsumerStatefulWidget {
  final Agent agent;
  final String? initialConversationId;
  /// 是否显示返回按钮（嵌入首页时设为 false）
  final bool showBackButton;

  const AgentProfilePage({
    super.key,
    required this.agent,
    this.initialConversationId,
    this.showBackButton = true,
  });

  @override
  ConsumerState<AgentProfilePage> createState() => _AgentProfilePageState();
}

class _AgentProfilePageState extends ConsumerState<AgentProfilePage> {
  /// 附件列表
  final List<ChatAttachment> _attachments = [];

  /// 对话ID
  String? _conversationId;

  /// 是否正在初始化
  bool _isInitializing = false;

  /// 待发送的消息（用于乐观UI）
  String? _pendingMessageContent;
  List<ChatAttachment>? _pendingAttachments;
  bool _isSendingInitialMessage = false;

  /// 是否需要自动设置会话标题（新建会话后首次发消息时设置）
  bool _needsAutoTitle = false;

  /// 判断会话标题是否为默认标题（需要自动替换）
  static bool _isDefaultTitle(String? title) {
    if (title == null || title.isEmpty) return true;
    final lower = title.trim().toLowerCase();
    return lower == 'new conversation' || lower == '未命名会话' || lower == '新对话';
  }

  /// 消息列表滚动控制器
  final ScrollController _scrollController = ScrollController();

  /// 选中的应用
  AppInfo? _selectedApp;

  /// 选中的人物个性
  Personality? _selectedPersonality;

  /// 当前选中的评审模式（默认为"随便聊聊"）
  QuickAction _selectedMode = QuickActions.chat;

  @override
  void initState() {
    super.initState();

    // ⚡ 立即加载或创建会话
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadOrCreateConversation();
    });
  }

  @override
  void dispose() {
    // 重置聊天模式状态，恢复导航栏显示
    ref.read(chatModeActiveProvider.notifier).state = false;
    // 释放 conversation notifier
    if (_conversationId != null) {
      ref.invalidate(conversationNotifierProvider(_conversationId!));
    }
    _scrollController.dispose();
    super.dispose();
  }

  /// 加载或创建会话
  ///
  /// 优先使用 initialConversationId，否则加载该 AI 员工的最新对话，如果没有则创建新会话
  Future<void> _loadOrCreateConversation() async {
    // 检查是否已经有会话ID
    if (_conversationId != null) return;

    // 直接从 Supabase 检查用户登录状态（避免 StreamProvider 时序问题）
    final currentUser = Supabase.instance.client.auth.currentUser;
    if (currentUser == null) {
      debugPrint('⚠️ 加载会话失败: 用户未登录');
      return;
    }

    try {
      debugPrint('⚡ 开始加载 ${widget.agent.name} 的会话...');
      final startTime = DateTime.now();

      String? conversationId;

      // 优先使用 initialConversationId
      if (widget.initialConversationId != null) {
        conversationId = widget.initialConversationId;
        debugPrint('📂 使用指定会话: $conversationId');
      } else {
        // 1. 先尝试获取该 Agent 的最新对话
        final conversations = await ref
            .read(conversationControllerProvider.notifier)
            .getAgentConversations(widget.agent.id);

        if (conversations.isNotEmpty) {
          // 有历史对话，使用最新的一个
          final latestConversation = conversations.first; // 已按时间排序，最新的在前
          conversationId = latestConversation.id;
          _needsAutoTitle = _isDefaultTitle(latestConversation.title);
          debugPrint('📂 找到最新会话: $conversationId (needsAutoTitle: $_needsAutoTitle)');
        } else {
          // 没有历史对话，创建新会话
          debugPrint('📝 没有历史会话，创建新会话...');
          final newConversation = await ref
              .read(conversationControllerProvider.notifier)
              .createNewConversation(widget.agent.id);

          if (newConversation == null) {
            debugPrint('⚠️ 会话创建失败(将在发送时重试)');
            return;
          }
          conversationId = newConversation.id;
          _needsAutoTitle = _isDefaultTitle(newConversation.title);
          debugPrint('✅ 新会话创建完成: $conversationId');
        }
      }

      final loadDuration = DateTime.now().difference(startTime);
      debugPrint('✅ 会话加载完成: $conversationId (耗时: ${loadDuration.inMilliseconds}ms)');

      if (!mounted) return;

      setState(() => _conversationId = conversationId);

      // 2. 初始化WebSocket连接
      unawaited(
        ref.read(conversationNotifierProvider(conversationId!).notifier)
            .initialize()
            .then((_) {
              final totalDuration = DateTime.now().difference(startTime);
              debugPrint('🔌 WebSocket连接完成 (总耗时: ${totalDuration.inMilliseconds}ms)');
              // 会话加载完成后，如果标题是默认的且已有消息，用第一条用户消息更新标题
              _tryFixTitleFromExistingMessages();
            })
            .catchError((e) {
              debugPrint('⚠️ WebSocket连接失败: $e');
            }),
      );
    } catch (e, stack) {
      debugPrint('❌ 加载会话异常: $e');
      // 静默失败,不显示错误给用户
      // 发送消息时会触发 _ensureConversation() 重试
    }
  }

  /// 获取问候语
  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 6) return '夜深了';
    if (hour < 9) return '早上好';
    if (hour < 12) return '上午好';
    if (hour < 14) return '中午好';
    if (hour < 18) return '下午好';
    if (hour < 22) return '晚上好';
    return '夜深了';
  }

  /// 获取用户显示名称
  String _getUserDisplayName() {
    final user = Supabase.instance.client.auth.currentUser;
    if (user == null) return '用户';

    // 优先使用 user_metadata 中的 username
    final username = user.userMetadata?['username'] as String?;
    if (username != null && username.isNotEmpty) {
      return username;
    }

    // 回退到 email 前缀
    final email = user.email ?? '';
    if (email.isEmpty || !email.contains('@')) {
      return '用户';
    }
    return email.split('@')[0];
  }

  /// 创建或获取对话
  Future<void> _ensureConversation() async {
    if (_conversationId != null) return;

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

    setState(() => _isInitializing = true);

    try {
      // 使用多会话模式创建新会话
      final conversation = await ref
          .read(conversationControllerProvider.notifier)
          .createNewConversation(widget.agent.id);

      if (conversation != null && mounted) {
        setState(() {
          _conversationId = conversation.id;
          _isInitializing = false;
          // 新建的会话没有标题（或默认标题），标记需要自动设置
          _needsAutoTitle = _isDefaultTitle(conversation.title);
        });

        // 初始化 WebSocket 连接
        await ref
            .read(conversationNotifierProvider(_conversationId!).notifier)
            .initialize();
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isInitializing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('创建对话失败: $e')),
        );
      }
    }
  }

  /// 发送消息（带附件）
  Future<void> _sendMessageWithAttachments(String message, List<ChatAttachment> attachments) async {
    // 检查网络连接
    final connectivityResult = await Connectivity().checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('无网络连接，请检查您的网络设置'),
            backgroundColor: Colors.red,
          ),
        );
      }
      return;
    }

    // 设置乐观UI状态（立即显示消息）
    setState(() {
      _isSendingInitialMessage = true;
      _pendingMessageContent = message;
      _pendingAttachments = List.from(attachments);
      _attachments.clear(); // 立即清空输入框附件
    });

    // 确保对话已创建
    await _ensureConversation();
    if (_conversationId == null) {
      // 创建失败，清理乐观UI
      if (mounted) {
        setState(() {
          _isSendingInitialMessage = false;
          _pendingMessageContent = null;
          _pendingAttachments = null;
        });
      }
      return;
    }

    try {
      // 上传附件
      List<Map<String, dynamic>>? uploadedAttachments;
      final attachmentsToSend = _pendingAttachments ?? attachments;

      if (attachmentsToSend.isNotEmpty) {
        final uploadService = ref.read(imageUploadServiceProvider);
        final uploaded = await uploadService.uploadAttachments(attachmentsToSend);
        uploadedAttachments = uploaded
            .where((a) => a.isUploaded)
            .map((a) => a.toJson())
            .toList();
      }

      // 发送消息
      await ref
          .read(conversationNotifierProvider(_conversationId!).notifier)
          .sendMessageWithAttachments(message, uploadedAttachments);

      // 发送成功，清理乐观UI
      if (mounted) {
        setState(() {
          _isSendingInitialMessage = false;
          _pendingMessageContent = null;
          _pendingAttachments = null;
        });
      }

      // 自动设置会话标题：用第一条消息内容作为标题
      if (_needsAutoTitle && _conversationId != null && message.isNotEmpty) {
        _needsAutoTitle = false;
        _autoSetConversationTitle(message);
      }

      // 滚动到底部
      _scrollToBottom();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送消息失败: $e')),
        );
        setState(() {
          _isSendingInitialMessage = false;
        });
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

  /// 尝试从已有消息中修复默认标题
  ///
  /// 当加载一个已有消息但标题仍为"New Conversation"的会话时调用
  void _tryFixTitleFromExistingMessages() {
    if (!_needsAutoTitle || _conversationId == null) return;

    final convState = ref.read(conversationNotifierProvider(_conversationId!));
    final messages = convState.messages;

    // 找到第一条用户消息
    final firstUserMessage = messages
        .where((m) => m.role == 'user' && m.content.trim().isNotEmpty)
        .toList();

    if (firstUserMessage.isNotEmpty) {
      _needsAutoTitle = false;
      _autoSetConversationTitle(firstUserMessage.first.content);
      debugPrint('📝 从已有消息中修复会话标题');
    }
  }

  /// 自动设置会话标题（取第一条消息内容，超长截断加省略号）
  void _autoSetConversationTitle(String firstMessage) {
    // 清理消息内容：去掉模式前缀、换行符等
    String title = firstMessage.replaceAll(RegExp(r'^\[MODE:\w+\]\s*'), '').trim();
    // 取第一行
    final firstLine = title.split('\n').first.trim();
    // 截断：最多 30 个字符
    const maxLen = 30;
    if (firstLine.length > maxLen) {
      title = '${firstLine.substring(0, maxLen)}...';
    } else {
      title = firstLine;
    }

    if (title.isEmpty) return;

    // 异步更新标题，不阻塞消息发送流程
    ref
        .read(conversationControllerProvider.notifier)
        .updateConversationTitle(
          conversationId: _conversationId!,
          title: title,
        )
        .then((_) {
      // 刷新对话列表
      ref.invalidate(agentConversationsProvider(widget.agent.id));
    });
  }

  /// 处理快捷功能点击 - 选择评审模式
  ///
  /// 点击按钮不直接发消息，而是切换模式，
  /// 输入框的 hintText 会随之变化
  void _onQuickActionTap(QuickAction action) {
    setState(() {
      _selectedMode = action;
    });
  }

  /// 处理输入框提交
  ///
  /// 如果当前选中了非默认模式（有 modeId），
  /// 自动在消息前加上 [MODE:xxx] 前缀
  void _onInputSubmit(String message) {
    if (message.isNotEmpty || _attachments.isNotEmpty) {
      String finalMessage = message;
      // 如果选中了非默认模式，添加模式前缀
      if (_selectedMode.modeId != null && message.isNotEmpty) {
        finalMessage = '[MODE:${_selectedMode.modeId}] $message';
      }
      _sendMessageWithAttachments(finalMessage, List.from(_attachments));
    }
  }

  @override
  Widget build(BuildContext context) {
    // 获取键盘高度（真实 + debug 模拟）
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    final debugKeyboard = ref.watch(debugKeyboardVisibleProvider);
    final isKeyboardVisible = keyboardHeight > 0 || debugKeyboard;

    // 监听流式状态
    final isStreaming = _conversationId != null
        ? ref.watch(
            conversationNotifierProvider(_conversationId!).select(
              (state) => state.streamingState is StreamingStateStreaming ||
                         state.streamingState is StreamingStateWaiting,
            ),
          )
        : false;

    // 判断是否有消息（决定输入框位置 + 导航栏显隐）
    final hasMessages = _conversationId != null &&
        ref.watch(
          conversationNotifierProvider(_conversationId!).select(
            (state) => state.messages.isNotEmpty,
          ),
        );
    final isChatMode = hasMessages || _isSendingInitialMessage;

    // 通知 MainScaffold 是否隐藏底部导航栏
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        ref.read(chatModeActiveProvider.notifier).state = isChatMode;
      }
    });

    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      resizeToAvoidBottomInset: false,
      body: AnimatedPadding(
        padding: EdgeInsets.only(bottom: keyboardHeight),
        duration: const Duration(milliseconds: 160),
        curve: Curves.easeOut,
        child: SafeArea(
          child: Column(
            children: [
              // 顶部导航栏：键盘弹起且非聊天模式时隐藏，腾出空间给头像
              if (isChatMode || !isKeyboardVisible)
                _buildAppBar()
              else
                const SizedBox.shrink(),

              // 主内容区域（统一视图）
              Expanded(
                child: _buildUnifiedConversationView(),
              ),

              // 底部输入区域（仅在聊天模式下显示）
              if (isChatMode)
                _buildChatModeInputSection(isKeyboardVisible, isStreaming),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建统一的对话视图
  ///
  /// 根据消息数量决定显示内容:
  /// - 有消息: 只显示消息列表
  /// - 无消息: 显示介绍卡片 + 快捷按钮
  Widget _buildUnifiedConversationView() {
    // 正在发送初始消息,显示乐观UI
    if (_isSendingInitialMessage) {
      return _buildPendingMessageList();
    }

    // 还没有创建会话,显示加载
    if (_conversationId == null) {
      // 如果正在初始化,显示加载指示器
      if (_isInitializing) {
        return const Center(child: CircularProgressIndicator());
      }

      // 否则显示介绍页面
      return _buildIntroductionView();
    }

    // 已创建会话,监听消息
    final messagesAsync = ref.watch(
      conversationNotifierProvider(_conversationId!).select(
        (state) => state.messages,
      ),
    );

    final messages = messagesAsync;

    // 如果有消息,只显示消息列表
    if (messages.isNotEmpty) {
      return OptimizedMessageList(
        conversationId: _conversationId!,
        scrollController: _scrollController,
      );
    }

    // 无消息,显示介绍视图
    return _buildIntroductionView();
  }

  /// 构建介绍视图（空会话时显示）
  ///
  /// 基于 Figma chris_chat_with_kb 设计稿:
  /// - 头像+名称在上方
  /// - 输入框在中间位置
  /// - 胶囊快捷按钮在输入框下方
  ///
  /// 键盘行为:
  /// - 键盘未弹起: Expanded(头像) + 输入框 + Spacer() → 输入框大致居中
  /// - 键盘弹起: Expanded 折叠（头像隐藏），输入框推至底部，距键盘 15dp
  ///
  /// 关键设计：使用 **同一棵 Widget 树**，仅通过属性值变化来切换布局。
  /// 这样 ExpandedChatInput 始终在 Column children[1] 位置，
  /// Flutter 的 reconcile 机制会保留其 State 和 FocusNode，
  /// 避免键盘弹起时因 widget 重建而丢失焦点导致键盘自动收起。
  Widget _buildIntroductionView() {
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    final debugKeyboard = ref.watch(debugKeyboardVisibleProvider);
    final isKeyboardVisible = keyboardHeight > 0 || debugKeyboard;

    // 监听流式状态（用于禁用输入框）
    final isStreaming = _conversationId != null
        ? ref.watch(
            conversationNotifierProvider(_conversationId!).select(
              (state) => state.streamingState is StreamingStateStreaming ||
                         state.streamingState is StreamingStateWaiting,
            ),
          )
        : false;

    // 头像介绍区域
    final avatarSection = Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AgentProfileTheme.horizontalPadding,
      ),
      child: AgentProfileCard(
        agent: widget.agent,
        selectedPersonality: _selectedPersonality,
        onPersonalityTap: _showPersonalitySelector,
      ),
    );

    // 输入框和功能键区域（Figma: spacing 10 between input & pills）
    final inputSection = Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AgentProfileTheme.horizontalPadding,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 输入框
          ExpandedChatInput(
            hintText: _selectedMode.hintText,
            onSubmit: _onInputSubmit,
            attachments: _attachments,
            onAttachmentRemove: _onAttachmentRemove,
            onImageTap: _onImageTap,
            onFileTap: _onFileTap,
            onFigmaTap: _onFigmaTap,
            onVoiceTap: _onVoiceTap,
            enabled: !isStreaming && !_isInitializing,
            initiallyExpanded: true,
            selectedApp: _selectedApp,
            onAppSelected: _onAppSelected,
          ),

          const SizedBox(height: 10), // Figma: spacing 10

          // 胶囊快捷按钮
          if (widget.agent.role == 'design_validator') ...[
            QuickActionPillRow(
              actions: QuickActions.defaults,
              selectedAction: _selectedMode,
              onActionTap: _onQuickActionTap,
            ),
          ],
        ],
      ),
    );

    // ── 统一树结构：只改变属性值，不改变树形状 ──
    //
    // children[0]: Expanded — 头像始终显示，键盘弹起时空间缩小、头像上移;
    //                          键盘收起时居中显示
    // children[1]: inputSection — 始终在同一位置，FocusNode 不丢失
    // children[2]: SizedBox — 键盘弹起时 15dp 底部间距，否则 0
    // children[3]: Spacer (仅键盘收起时) — 使输入框垂直居中
    return Column(
      children: [
        // 上部区域：头像始终显示
        // 键盘弹起时 Expanded 空间缩小 → 头像自然上移（可滚动）
        // 键盘收起时 Expanded 空间充足 → 头像居中
        Expanded(
          child: Center(
            child: SingleChildScrollView(
              child: avatarSection,
            ),
          ),
        ),

        // 输入框 + 胶囊按钮（始终在 children[1]，保持焦点）
        inputSection,

        // 底部间距：键盘弹起时 15dp（Figma），收起时 0
        SizedBox(height: isKeyboardVisible ? 15 : 0),

        // 下部空间：键盘收起时占据下半部分，使输入框垂直居中
        if (!isKeyboardVisible) const Spacer(),
      ],
    );
  }

  /// 构建顶部导航栏
  Widget _buildAppBar() {
    // 判断是否有消息（用于决定是否显示紧凑Agent信息）
    final hasMessages = _conversationId != null &&
        ref.watch(
          conversationNotifierProvider(_conversationId!).select(
            (state) => state.messages.isNotEmpty,
          ),
        );

    // 有消息时使用 Figma 风格的顶部栏
    if (hasMessages) {
      return _buildChatAppBar();
    }

    // 无消息时使用原有的顶部栏
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: Row(
        children: [
          if (widget.showBackButton)
            IconButton(
              onPressed: () => Navigator.of(context).pop(),
              icon: const Icon(
                Icons.arrow_back_ios_new,
                color: AgentProfileTheme.titleColor,
              ),
            ),
          const SizedBox(width: 8),
          _buildGreetingHeader(),
          const Spacer(),
          // History button
          GestureDetector(
            onTap: _showConversationSelector,
            behavior: HitTestBehavior.opaque,
            child: SizedBox(
              width: 40,
              height: 40,
              child: Container(
                decoration: ShapeDecoration(
                  color: Colors.black.withOpacity(0.04),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(90),
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
        ],
      ),
    );
  }

  /// 构建聊天模式的顶部栏（Figma 设计风格）
  Widget _buildChatAppBar() {
    return Container(
      width: double.infinity,
      height: 52,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Left: back button + agent name
          Expanded(
            child: SizedBox(
              height: 52,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // Back button - 48px touch area, 40x40 circle bg (Figma)
                  GestureDetector(
                    onTap: () {
                      if (widget.showBackButton) {
                        // 推送进入的页面：返回上一页
                        Navigator.of(context).pop();
                      } else {
                        // 首页嵌入模式：返回到问候/空白状态（新建会话）
                        _startNewConversation();
                      }
                    },
                    behavior: HitTestBehavior.opaque,
                    child: SizedBox(
                      width: 48,
                      height: 52,
                      child: Center(
                        child: Container(
                          width: 40,
                          height: 40,
                          decoration: ShapeDecoration(
                            color: Colors.black.withOpacity(0.04),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(90),
                            ),
                          ),
                          child: Center(
                            child: SvgPicture.asset(
                              'assets/icons/chat/back_arrow.svg',
                              width: 24,
                              height: 24,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  // Agent name
                  Expanded(
                    child: Container(
                      constraints: const BoxConstraints(minHeight: 52),
                      padding: const EdgeInsets.symmetric(vertical: 2),
                      alignment: Alignment.centerLeft,
                      child: Text(
                        widget.agent.name,
                        style: TextStyle(
                          color: Colors.black.withOpacity(0.90),
                          fontSize: 18,
                          fontFamily: 'OPPO Sans 4.0',
                          fontWeight: FontWeight.w500,
                          height: 1.44,
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
            height: 52,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.end,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Add new conversation button
                GestureDetector(
                  onTap: _startNewConversation,
                  behavior: HitTestBehavior.opaque,
                  child: SizedBox(
                    width: 48,
                    height: 52,
                    child: Center(
                      child: Container(
                        width: 40,
                        height: 40,
                        decoration: ShapeDecoration(
                          color: Colors.black.withOpacity(0.04),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(90),
                          ),
                        ),
                        child: SvgPicture.asset(
                          'assets/icons/chat/add_circle.svg',
                          width: 40,
                          height: 40,
                        ),
                      ),
                    ),
                  ),
                ),
                // History button
                GestureDetector(
                  onTap: _showConversationSelector,
                  behavior: HitTestBehavior.opaque,
                  child: SizedBox(
                    width: 48,
                    height: 52,
                    child: Center(
                      child: Container(
                        width: 40,
                        height: 40,
                        decoration: ShapeDecoration(
                          color: Colors.black.withOpacity(0.04),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(90),
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
    );
  }

  /// 构建问候语头部（基于 Figma greeting 设计）
  Widget _buildGreetingHeader() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 问候语
        Text(
          _getGreeting(),
          style: AgentProfileTheme.greetingStyle,
        ),
        const SizedBox(height: 2),
        // 用户名
        Text(
          _getUserDisplayName(),
          style: AgentProfileTheme.userNameStyle,
        ),
      ],
    );
  }

  /// 显示人物个性选择弹窗
  void _showPersonalitySelector() async {
    final RenderBox overlay =
        Navigator.of(context).overlay!.context.findRenderObject() as RenderBox;

    // 计算弹窗位置（屏幕中央偏上）
    final screenWidth = overlay.size.width;
    final screenHeight = overlay.size.height;
    
    final position = RelativeRect.fromLTRB(
      (screenWidth - 196) / 2, // 弹窗宽度196，居中
      screenHeight * 0.35,     // 屏幕35%位置
      (screenWidth - 196) / 2,
      screenHeight * 0.35,
    );

    final selected = await showPersonalitySelectorPopup(
      context,
      selectedPersonality: _selectedPersonality,
      position: position,
      agentName: widget.agent.name,
    );

    if (selected != null) {
      setState(() {
        _selectedPersonality = selected;
      });
    }
  }

  /// 开始新对话
  void _startNewConversation() async {
    // 清除当前对话状态
    if (_conversationId != null) {
      ref.invalidate(conversationNotifierProvider(_conversationId!));
    }

    setState(() {
      _conversationId = null;
      _attachments.clear();
      _pendingMessageContent = null;
      _pendingAttachments = null;
      _isSendingInitialMessage = false;
      _selectedMode = QuickActions.chat; // 重置模式
    });

    // 创建全新的会话（不是加载已有的）
    final newConversation = await ref
        .read(conversationControllerProvider.notifier)
        .createNewConversation(widget.agent.id);

    if (newConversation != null && mounted) {
      setState(() {
        _conversationId = newConversation.id;
        _needsAutoTitle = true; // 新建会话，需要自动设置标题
      });

      // 初始化WebSocket连接
      unawaited(
        ref.read(conversationNotifierProvider(newConversation.id).notifier)
            .initialize(),
      );

    }
  }

  /// 显示会话选择器
  void _showConversationSelector() async {
    // 获取该Agent的所有会话
    final conversations = await ref
        .read(conversationControllerProvider.notifier)
        .getAgentConversations(widget.agent.id);

    if (!mounted) return;

    ConversationSelector.show(
      context,
      agentId: widget.agent.id,
      currentConversationId: _conversationId,
      conversations: conversations,
      onNewConversation: _startNewConversation,
      onSelectConversation: _switchToConversation,
      onRenameConversation: _renameConversation,
    );
  }

  /// 切换到指定会话
  void _switchToConversation(String conversationId) {
    // 清除当前对话状态
    if (_conversationId != null) {
      ref.invalidate(conversationNotifierProvider(_conversationId!));
    }

    // 切换会话
    setState(() {
      _conversationId = conversationId;
      _attachments.clear();
      _pendingMessageContent = null;
      _pendingAttachments = null;
      _isSendingInitialMessage = false;
      _needsAutoTitle = false; // 已有会话不需要自动设置标题
    });

    // 初始化新会话的WebSocket连接
    ref
        .read(conversationNotifierProvider(conversationId).notifier)
        .initialize()
        .then((_) {
      debugPrint('✅ 切换到会话: $conversationId');
    }).catchError((e) {
      debugPrint('⚠️ 切换会话失败: $e');
    });

    // 显示提示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('已切换会话'),
        duration: Duration(seconds: 1),
      ),
    );
  }

  /// 重命名会话
  void _renameConversation(String conversationId, String newTitle) async {
    final result = await ref
        .read(conversationControllerProvider.notifier)
        .updateConversationTitle(
          conversationId: conversationId,
          title: newTitle,
        );

    if (mounted) {
      if (result != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('会话标题已更新'),
            duration: Duration(seconds: 1),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('更新失败，请重试'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// 紧凑的 Agent 信息（对话模式使用）
  Widget _buildCompactAgentInfo() {
    final isChrisChen = widget.agent.role == 'design_validator' ||
        widget.agent.name.contains('Chris');

    return Row(
      children: [
        // 小头像
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.grey[200],
          ),
          clipBehavior: Clip.antiAlias,
          child: isChrisChen
              ? Image.asset(
                  AgentProfileTheme.chrisChenAvatar,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _buildFallbackAvatar(),
                )
              : _buildFallbackAvatar(),
        ),
        const SizedBox(width: 10),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              widget.agent.name,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AgentProfileTheme.titleColor,
              ),
            ),
            Text(
              widget.agent.description,
              style: const TextStyle(
                fontSize: 14,
                color: AgentProfileTheme.labelColor,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildFallbackAvatar() {
    return Center(
      child: Text(
        widget.agent.name.isNotEmpty ? widget.agent.name[0] : '?',
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: Colors.grey,
        ),
      ),
    );
  }

  /// 连接状态指示器
  Widget _buildConnectionStatus() {
    if (_conversationId == null) return const SizedBox.shrink();

    final connectionState = ref.watch(
      conversationNotifierProvider(_conversationId!).select(
        (state) => state.connectionState,
      ),
    );

    return connectionState.when(
      disconnected: () => _buildStatusDot(Colors.grey, '未连接'),
      connecting: () => _buildStatusDot(Colors.orange, '连接中'),
      connected: () => _buildStatusDot(Colors.green, '已连接'),
      reconnecting: (attempt) => _buildStatusDot(Colors.orange, '重连($attempt)'),
    );
  }

  Widget _buildStatusDot(Color color, String tooltip) {
    return Tooltip(
      message: tooltip,
      child: Container(
        width: 8,
        height: 8,
        margin: const EdgeInsets.only(right: 8),
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
        ),
      ),
    );
  }

  /// 构建待发送消息列表（乐观UI）
  ///
  /// 立即显示用户消息，同时在后台处理创建对话和上传附件
  Widget _buildPendingMessageList() {
    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
            reverse: true, // 保持与 OptimizedMessageList 一致
            children: [
              // AI正在思考的指示器
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: _buildThinkingIndicator(),
                ),
              ),
              // 显示用户消息（带图片）
              if (_pendingMessageContent != null || (_pendingAttachments != null && _pendingAttachments!.isNotEmpty))
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: MessageBubbleContent(
                    message: Message(
                      id: 'pending',
                      conversationId: 'pending',
                      role: 'user',
                      content: _pendingMessageContent ?? '',
                      createdAt: DateTime.now(),
                      attachments: _pendingAttachments?.map((a) => {
                        'url': a.displayUrl ?? a.localPath ?? '', // 优先使用displayUrl
                        'type': a.mimeType ?? 'image',
                        'filename': a.filename,
                      }).toList(),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }

  /// 构建AI思考中的指示器
  Widget _buildThinkingIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
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
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(const Color(0xFF2C69FF)),
            ),
          ),
          const SizedBox(width: 10),
          Text(
            _isInitializing ? '正在连接...' : '正在思考...',
            style: TextStyle(
              color: Colors.black.withOpacity(0.6),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建聊天模式的底部输入区域
  ///
  /// 使用与无消息状态相同的 ExpandedChatInput 组件，
  /// 保持一致的按钮和交互模式（附件、应用选择、语音等）。
  /// 默认收起状态（单行输入框），点击后展开为完整输入卡片。
  Widget _buildChatModeInputSection(bool isKeyboardVisible, bool isStreaming) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AgentProfileTheme.horizontalPadding,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 使用和无消息状态一样的 ExpandedChatInput
          ExpandedChatInput(
            hintText: _selectedMode.hintText,
            onSubmit: _onInputSubmit,
            attachments: _attachments,
            onAttachmentRemove: _onAttachmentRemove,
            onImageTap: _onImageTap,
            onFileTap: _onFileTap,
            onFigmaTap: _onFigmaTap,
            onVoiceTap: _onVoiceTap,
            enabled: !isStreaming && !_isInitializing,
            initiallyExpanded: false, // 聊天模式默认收起
            selectedApp: _selectedApp,
            onAppSelected: _onAppSelected,
          ),

          // 胶囊快捷按钮（仅 design_validator）
          if (widget.agent.role == 'design_validator') ...[
            const SizedBox(height: 10),
            QuickActionPillRow(
              actions: QuickActions.defaults,
              selectedAction: _selectedMode,
              onActionTap: _onQuickActionTap,
            ),
          ],

          SizedBox(height: isKeyboardVisible ? 8 : 8),
        ],
      ),
    );
  }

  /// 移除附件
  void _onAttachmentRemove(ChatAttachment attachment) {
    setState(() {
      _attachments.removeWhere((a) => a.id == attachment.id);
    });
  }

  /// 添加图片
  void _onImageTap() async {
    await _pickImageFromGallery();
  }

  /// 添加文件
  void _onFileTap() async {
    await _pickFile();
  }

  /// 添加 Figma 链接
  void _onFigmaTap() {
    _showFigmaLinkDialog();
  }

  /// 显示 Figma 链接输入对话框
  void _showFigmaLinkDialog() {
    final controller = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加 Figma 链接'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: InputDecoration(
            hintText: '粘贴 Figma 链接...',
            hintStyle: TextStyle(color: Colors.black.withOpacity(0.4)),
            filled: true,
            fillColor: Colors.black.withOpacity(0.04),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              final link = controller.text.trim();
              Navigator.pop(context);
              if (link.isNotEmpty && link.contains('figma.com')) {
                // 将 Figma 链接作为消息发送
                _sendMessageWithAttachments(
                  '请分析这个 Figma 设计：\n$link',
                  List.from(_attachments),
                );
              } else if (link.isNotEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('请输入有效的 Figma 链接')),
                );
              }
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  /// 从相册选择图片
  Future<void> _pickImageFromGallery() async {
    final attachmentService = ref.read(attachmentServiceProvider);
    final attachments = await attachmentService.pickMultipleImages(maxImages: 9 - _attachments.length);

    if (attachments.isNotEmpty) {
      setState(() {
        _attachments.addAll(attachments);
      });
    }
  }

  /// 拍照
  Future<void> _takePhoto() async {
    final attachmentService = ref.read(attachmentServiceProvider);
    final attachment = await attachmentService.takePhoto();

    if (attachment != null) {
      setState(() {
        _attachments.add(attachment);
      });
    }
  }

  /// 选择文件
  Future<void> _pickFile() async {
    final attachmentService = ref.read(attachmentServiceProvider);
    final attachment = await attachmentService.pickFile();

    if (attachment != null) {
      setState(() {
        _attachments.add(attachment);
      });
    }
  }

  /// 语音输入
  void _onVoiceTap() {
    showVoiceInputDialog(
      context,
      onResult: (text) {
        if (text.isNotEmpty) {
          _sendMessageWithAttachments(text, List.from(_attachments));
        }
      },
    );
  }

  /// 应用选择
  void _onAppSelected(AppInfo? app) {
    setState(() {
      _selectedApp = app;
    });
  }

}
