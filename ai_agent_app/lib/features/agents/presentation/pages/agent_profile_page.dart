import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import '../../domain/models/agent.dart';
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
import '../widgets/quick_action_button.dart';
import '../widgets/voice_input_dialog.dart';

/// AI员工详情页面（整合对话功能）
///
/// 基于 Figma 设计稿实现，展示AI员工信息和对话功能
/// 当用户开始对话后，页面会转换为对话模式，但保持设计风格一致
class AgentProfilePage extends ConsumerStatefulWidget {
  final Agent agent;

  const AgentProfilePage({
    super.key,
    required this.agent,
  });

  @override
  ConsumerState<AgentProfilePage> createState() => _AgentProfilePageState();
}

class _AgentProfilePageState extends ConsumerState<AgentProfilePage> {
  /// 附件列表
  final List<ChatAttachment> _attachments = [];

  /// 对话ID
  String? _conversationId;

  /// 是否已开始对话
  bool _hasStartedConversation = false;

  /// 是否正在初始化
  bool _isInitializing = false;

  /// 消息列表滚动控制器
  final ScrollController _scrollController = ScrollController();

  /// 选中的应用
  AppInfo? _selectedApp;

  @override
  void dispose() {
    // 释放 conversation notifier
    if (_conversationId != null) {
      ref.invalidate(conversationNotifierProvider(_conversationId!));
    }
    _scrollController.dispose();
    super.dispose();
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
      final conversation = await ref
          .read(conversationControllerProvider.notifier)
          .createConversation(widget.agent.id);

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

    // 确保对话已创建
    await _ensureConversation();
    if (_conversationId == null) return;

    // 标记已开始对话
    if (!_hasStartedConversation) {
      setState(() => _hasStartedConversation = true);
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

      // 发送消息
      await ref
          .read(conversationNotifierProvider(_conversationId!).notifier)
          .sendMessageWithAttachments(message, uploadedAttachments);

      // 清空附件
      setState(() => _attachments.clear());

      // 滚动到底部
      _scrollToBottom();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送消息失败: $e')),
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

            // 主内容区域
            Expanded(
              child: _hasStartedConversation
                  ? _buildConversationView()
                  : _buildProfileView(isKeyboardVisible),
            ),

            // 底部输入区域
            _buildInputSection(isKeyboardVisible, isStreaming),
          ],
        ),
      ),
    );
  }

  /// 构建顶部导航栏
  Widget _buildAppBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(
              Icons.arrow_back_ios_new,
              color: AgentProfileTheme.titleColor,
            ),
          ),
          if (_hasStartedConversation) ...[
            // 对话模式显示 Agent 信息
            const SizedBox(width: 8),
            _buildCompactAgentInfo(),
          ],
          const Spacer(),
          if (_conversationId != null && _hasStartedConversation)
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
              }
            },
            itemBuilder: (context) => [
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

  /// 开始新对话
  void _startNewConversation() {
    // 清除当前对话状态
    if (_conversationId != null) {
      ref.invalidate(conversationNotifierProvider(_conversationId!));
    }

    setState(() {
      _conversationId = null;
      _hasStartedConversation = false;
      _attachments.clear();
    });

    // 显示提示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('已创建新对话'),
        duration: Duration(seconds: 2),
      ),
    );
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

  /// 构建个人资料视图（未开始对话时）
  Widget _buildProfileView(bool isKeyboardVisible) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(
        horizontal: AgentProfileTheme.horizontalPadding,
      ),
      child: Column(
        children: [
          const SizedBox(height: 16),

          // 问候区域
          _buildGreetingSection(),

          const SizedBox(height: 40),

          // AI员工信息区域
          _buildAgentInfoSection(),

          const SizedBox(height: 40),

          // 快捷功能按钮（键盘弹起时隐藏）
          if (!isKeyboardVisible) ...[
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

  /// 构建对话视图（开始对话后）
  Widget _buildConversationView() {
    if (_conversationId == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return OptimizedMessageList(
      conversationId: _conversationId!,
      scrollController: _scrollController,
    );
  }

  /// 构建问候区域
  Widget _buildGreetingSection() {
    const userName = 'User';

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _getGreeting(),
              style: AgentProfileTheme.greetingStyle,
            ),
            const SizedBox(height: 6),
            Text(
              userName,
              style: AgentProfileTheme.userNameStyle,
            ),
          ],
        ),
        // 通知图标
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.68),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.notifications_outlined,
            color: AgentProfileTheme.titleColor,
          ),
        ),
      ],
    );
  }

  /// 构建AI员工信息区域
  Widget _buildAgentInfoSection() {
    final isChrisChen = widget.agent.role == 'design_validator' ||
        widget.agent.name.contains('Chris');

    return Column(
      children: [
        // 头像
        AgentAvatar(
          avatarUrl: widget.agent.avatarUrl,
          assetPath: isChrisChen ? AgentProfileTheme.chrisChenAvatar : null,
          fallbackText: widget.agent.name,
        ),

        const SizedBox(height: 14),

        // 名称
        Text(
          widget.agent.name,
          style: AgentProfileTheme.agentNameStyle,
        ),

        const SizedBox(height: 4),

        // 描述
        Text(
          widget.agent.description,
          textAlign: TextAlign.center,
          style: AgentProfileTheme.agentDescriptionStyle,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  /// 构建底部输入区域
  Widget _buildInputSection(bool isKeyboardVisible, bool isStreaming) {
    return Container(
      padding: EdgeInsets.fromLTRB(
        AgentProfileTheme.horizontalPadding,
        12,
        AgentProfileTheme.horizontalPadding,
        isKeyboardVisible ? 8 : 24,
      ),
      decoration: _hasStartedConversation
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
            onAttachmentTap: _onAttachmentTap,
            onBackgroundDescTap: _onBackgroundDescTap,
            onModeTap: _onModeTap,
            onVoiceTap: _onVoiceTap,
            enabled: !isStreaming && !_isInitializing,
            selectedApp: _selectedApp,
            onAppSelected: _onAppSelected,
          ),

          // 快捷功能按钮（对话开始后，键盘收起时显示）
          if (_hasStartedConversation && !isKeyboardVisible) ...[
            const SizedBox(height: 12),
            QuickActionRow(
              actions: QuickActions.defaults,
              onActionTap: _onQuickActionTap,
            ),
          ],
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

  /// 添加附件 - 弹出选择菜单
  Future<void> _onAttachmentTap() async {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 20),
            ListTile(
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.photo_library_rounded, color: Colors.blue),
              ),
              title: const Text('从相册选择图片'),
              subtitle: const Text('支持 JPG、PNG、GIF、WebP'),
              onTap: () async {
                Navigator.pop(context);
                await _pickImageFromGallery();
              },
            ),
            ListTile(
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.camera_alt_rounded, color: Colors.orange),
              ),
              title: const Text('拍照'),
              subtitle: const Text('使用相机拍摄照片'),
              onTap: () async {
                Navigator.pop(context);
                await _takePhoto();
              },
            ),
            ListTile(
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.insert_drive_file_rounded, color: Colors.green),
              ),
              title: const Text('选择文件'),
              subtitle: const Text('支持 PDF、Word、Excel 等'),
              onTap: () async {
                Navigator.pop(context);
                await _pickFile();
              },
            ),
            const SizedBox(height: 20),
          ],
        ),
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

  /// 背景描述
  void _onBackgroundDescTap() {
    _showBackgroundDescriptionSheet();
  }

  /// 显示背景描述输入面板
  void _showBackgroundDescriptionSheet() {
    final controller = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          left: 24,
          right: 24,
          top: 24,
          bottom: MediaQuery.of(context).viewInsets.bottom + 24,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '方案背景',
                  style: AgentProfileTheme.agentNameStyle.copyWith(fontSize: 18),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '描述你的设计方案背景和目标，帮助AI更好地理解需求',
              style: AgentProfileTheme.agentDescriptionStyle,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              maxLines: 5,
              autofocus: true,
              decoration: InputDecoration(
                hintText: '例如：这是一个电商APP的商品详情页改版方案，目标是提升转化率...',
                hintStyle: TextStyle(
                  color: Colors.black.withOpacity(0.4),
                  fontSize: 14,
                ),
                filled: true,
                fillColor: Colors.black.withOpacity(0.04),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  final text = controller.text.trim();
                  Navigator.pop(context);
                  if (text.isNotEmpty) {
                    _sendMessageWithAttachments('【方案背景】\n$text', List.from(_attachments));
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0066FF),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('开始评审'),
              ),
            ),
          ],
        ),
      ),
    );
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

  /// 模式选择
  void _onModeTap() {
    _showModeSelector();
  }

  /// 显示模式选择器
  void _showModeSelector() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '选择对话模式',
              style: AgentProfileTheme.agentNameStyle.copyWith(fontSize: 18),
            ),
            const SizedBox(height: 16),
            _buildModeOption('默认', '自动选择最佳回复方式', Icons.auto_awesome, true),
            _buildModeOption('深度分析', '详细分析设计方案', Icons.analytics_outlined, false),
            _buildModeOption('快速评审', '快速给出关键意见', Icons.flash_on_outlined, false),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  /// 构建模式选项
  Widget _buildModeOption(String title, String subtitle, IconData icon, bool isSelected) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFF0066FF).withOpacity(0.1)
              : Colors.black.withOpacity(0.04),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(
          icon,
          color: isSelected ? const Color(0xFF0066FF) : AgentProfileTheme.labelColor,
        ),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: isSelected
          ? const Icon(Icons.check_circle, color: Color(0xFF0066FF))
          : null,
      onTap: () => Navigator.pop(context),
    );
  }
}
