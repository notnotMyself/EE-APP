import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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

  /// 消息列表滚动控制器
  final ScrollController _scrollController = ScrollController();

  /// 选中的应用
  AppInfo? _selectedApp;

  /// 选中的人物个性
  Personality? _selectedPersonality;

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

    // 检查用户登录状态
    final currentUser = ref.read(currentUserProvider);
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
          debugPrint('📂 找到最新会话: $conversationId');
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

    final currentUser = ref.read(currentUserProvider);
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

  /// 处理快捷功能点击
  void _onQuickActionTap(QuickAction action) {
    String? message = action.initialMessage;

    // 如果有 modeId，构建带模式前缀的消息
    if (action.modeId != null && message != null) {
      message = '[MODE:${action.modeId}] $message';
    }

    if (message != null && message.isNotEmpty) {
      _sendMessageWithAttachments(message, List.from(_attachments));
    }
  }

  /// 处理输入框提交
  void _onInputSubmit(String message) {
    if (message.isNotEmpty || _attachments.isNotEmpty) {
      // 这里的逻辑已经在 _sendMessageWithAttachments 中处理了乐观更新
      _sendMessageWithAttachments(message, List.from(_attachments));
    }
  }

  @override
  Widget build(BuildContext context) {
    // 获取键盘高度
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    final isKeyboardVisible = keyboardHeight > 0;

    // 监听流式状态
    final isStreaming = _conversationId != null
        ? ref.watch(
            conversationNotifierProvider(_conversationId!).select(
              (state) => state.streamingState is StreamingStateStreaming ||
                         state.streamingState is StreamingStateWaiting,
            ),
          )
        : false;

    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: Column(
          children: [
            // 顶部导航栏
            _buildAppBar(),

            // 主内容区域（统一视图）
            Expanded(
              child: _buildUnifiedConversationView(),
            ),

            // 底部输入区域
            _buildInputSection(isKeyboardVisible, isStreaming),
          ],
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
  Widget _buildIntroductionView() {
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    final isKeyboardVisible = keyboardHeight > 0;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(
        horizontal: AgentProfileTheme.horizontalPadding,
      ),
      child: Column(
        children: [
          const SizedBox(height: 40),

          // AI员工介绍卡片（包含人物个性选择）
          AgentProfileCard(
            agent: widget.agent,
            selectedPersonality: _selectedPersonality,
            onPersonalityTap: _showPersonalitySelector,
          ),

          const SizedBox(height: 40),

          // 快捷功能按钮（仅 Chris Chen / design_validator 显示，键盘弹起时隐藏）
          if (!isKeyboardVisible && widget.agent.role == 'design_validator') ...[
            QuickActionRow(
              actions: QuickActions.defaults,
              onActionTap: _onQuickActionTap,
            ),
          ],

          // 底部间距
          SizedBox(height: isKeyboardVisible ? 16 : 32),
        ],
      ),
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
          if (hasMessages) ...[
            // 有消息时显示紧凑 Agent 信息
            const SizedBox(width: 8),
            _buildCompactAgentInfo(),
          ] else ...[
            // 无消息时显示问候语
            const SizedBox(width: 8),
            _buildGreetingHeader(),
          ],
          const Spacer(),
          if (_conversationId != null && hasMessages)
            _buildConnectionStatus(),
          PopupMenuButton<String>(
            icon: const Icon(
              Icons.more_horiz,
              color: AgentProfileTheme.titleColor,
            ),
            onSelected: (value) {
              switch (value) {
                case 'new_conversation':
                  _startNewConversation();
                  break;
                case 'conversation_history':
                  _showConversationSelector();
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem<String>(
                value: 'conversation_history',
                child: Row(
                  children: [
                    Icon(Icons.history, size: 20),
                    SizedBox(width: 12),
                    Text('会话历史'),
                  ],
                ),
              ),
              const PopupMenuItem<String>(
                value: 'new_conversation',
                child: Row(
                  children: [
                    Icon(Icons.add_comment_outlined, size: 20),
                    SizedBox(width: 12),
                    Text('新建对话'),
                  ],
                ),
              ),
            ],
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
    });

    // 创建全新的会话（不是加载已有的）
    final newConversation = await ref
        .read(conversationControllerProvider.notifier)
        .createNewConversation(widget.agent.id);

    if (newConversation != null && mounted) {
      setState(() => _conversationId = newConversation.id);

      // 初始化WebSocket连接
      unawaited(
        ref.read(conversationNotifierProvider(newConversation.id).notifier)
            .initialize(),
      );

      // 显示提示
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('已创建新对话'),
          duration: Duration(seconds: 2),
        ),
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
                fontSize: 12,
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

  /// 构建底部输入区域
  Widget _buildInputSection(bool isKeyboardVisible, bool isStreaming) {
    // 判断是否有消息（用于决定是否显示顶部边框）
    final hasMessages = _conversationId != null &&
        ref.watch(
          conversationNotifierProvider(_conversationId!).select(
            (state) => state.messages.isNotEmpty,
          ),
        );

    return Container(
      padding: EdgeInsets.fromLTRB(
        AgentProfileTheme.horizontalPadding,
        12,
        AgentProfileTheme.horizontalPadding,
        isKeyboardVisible ? 8 : 24,
      ),
      decoration: hasMessages
          ? BoxDecoration(
              color: AgentProfileTheme.backgroundColor,
              border: Border(
                top: BorderSide(
                  color: Colors.black.withOpacity(0.05),
                  width: 1,
                ),
              ),
            )
          : null,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 展开式输入框
          ExpandedChatInput(
            hintText: '简单描述下方案背景与目标',
            onSubmit: _onInputSubmit,
            attachments: _attachments,
            onAttachmentRemove: _onAttachmentRemove,
            onImageTap: _onImageTap,
            onFileTap: _onFileTap,
            onFigmaTap: _onFigmaTap,
            onVoiceTap: _onVoiceTap,
            enabled: !isStreaming && !_isInitializing,
            selectedApp: _selectedApp,
            onAppSelected: _onAppSelected,
          ),
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
