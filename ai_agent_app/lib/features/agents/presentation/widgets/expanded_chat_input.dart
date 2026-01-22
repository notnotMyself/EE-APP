import 'package:flutter/material.dart';
import '../theme/agent_profile_theme.dart';
import 'app_selector_popup.dart';

/// 附件上传状态
enum AttachmentStatus {
  pending,   // 待上传
  uploading, // 上传中
  uploaded,  // 已上传
  error,     // 上传失败
}

/// 图片附件数据模型
class ChatAttachment {
  final String id;
  final String? localPath;
  final String? networkUrl;
  final String? thumbnailUrl;
  final String? mimeType;
  final String? filename;
  final AttachmentStatus status;

  const ChatAttachment({
    required this.id,
    this.localPath,
    this.networkUrl,
    this.thumbnailUrl,
    this.mimeType,
    this.filename,
    this.status = AttachmentStatus.pending,
  });

  String? get displayUrl => thumbnailUrl ?? networkUrl ?? localPath;

  /// 创建带有新状态的副本
  ChatAttachment copyWith({
    String? networkUrl,
    String? thumbnailUrl,
    AttachmentStatus? status,
  }) {
    return ChatAttachment(
      id: id,
      localPath: localPath,
      networkUrl: networkUrl ?? this.networkUrl,
      thumbnailUrl: thumbnailUrl ?? this.thumbnailUrl,
      mimeType: mimeType,
      filename: filename,
      status: status ?? this.status,
    );
  }

  /// 转换为 JSON（用于发送给后端）
  Map<String, dynamic> toJson() => {
    'id': id,
    'url': networkUrl,
    'mime_type': mimeType,
    'filename': filename,
  };

  /// 判断是否已上传
  bool get isUploaded => networkUrl != null && status == AttachmentStatus.uploaded;
}

/// 展开式聊天输入卡片
/// 
/// 基于 Figma 设计稿实现，支持：
/// - 图片/附件预览
/// - 文字输入
/// - 操作工具栏（附件、应用选择、背景描述、模式选择）
/// - 语音输入（麦克风按钮）
class ExpandedChatInput extends StatefulWidget {
  final String hintText;
  final ValueChanged<String> onSubmit;
  final VoidCallback? onAttachmentTap;           // 添加附件
  final VoidCallback? onBackgroundDescTap;       // 背景描述
  final VoidCallback? onModeTap;                 // 模式选择
  final VoidCallback? onVoiceTap;                // 语音输入
  final List<ChatAttachment> attachments;
  final ValueChanged<ChatAttachment>? onAttachmentRemove;
  final bool enabled;
  final AppInfo? selectedApp;                    // 当前选中的应用
  final ValueChanged<AppInfo?>? onAppSelected;  // 应用选择回调

  const ExpandedChatInput({
    super.key,
    this.hintText = '简单描述下方案背景与目标',
    required this.onSubmit,
    this.onAttachmentTap,
    this.onBackgroundDescTap,
    this.onModeTap,
    this.onVoiceTap,
    this.attachments = const [],
    this.onAttachmentRemove,
    this.enabled = true,
    this.selectedApp,
    this.onAppSelected,
  });

  @override
  State<ExpandedChatInput> createState() => _ExpandedChatInputState();
}

class _ExpandedChatInputState extends State<ExpandedChatInput> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  bool _isExpanded = false;
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onTextChanged);
    _focusNode.addListener(_onFocusChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_onTextChanged);
    _focusNode.removeListener(_onFocusChanged);
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    final hasText = _controller.text.isNotEmpty;
    if (hasText != _hasText) {
      setState(() => _hasText = hasText);
    }
  }

  void _onFocusChanged() {
    if (_focusNode.hasFocus && !_isExpanded) {
      setState(() => _isExpanded = true);
    }
  }

  void _handleSubmit() {
    final text = _controller.text.trim();
    if (text.isNotEmpty || widget.attachments.isNotEmpty) {
      widget.onSubmit(text);
      _controller.clear();
      setState(() {
        _isExpanded = false;
        _hasText = false;
      });
      _focusNode.unfocus();
    }
  }

  void _collapse() {
    if (_controller.text.isEmpty && widget.attachments.isEmpty) {
      setState(() => _isExpanded = false);
      _focusNode.unfocus();
    }
  }

  @override
  Widget build(BuildContext context) {
    // 如果未展开，显示简单输入框
    if (!_isExpanded) {
      return _buildCollapsedInput();
    }
    
    // 展开状态显示完整输入卡片
    return _buildExpandedCard();
  }

  /// 收起状态的简单输入框
  /// Figma规范: 麦克风按钮(36x36) + 发送按钮(32x32)
  Widget _buildCollapsedInput() {
    return GestureDetector(
      onTap: () {
        setState(() => _isExpanded = true);
        _focusNode.requestFocus();
      },
      child: Container(
        height: AgentProfileTheme.inputHeight,
        decoration: AgentProfileTheme.cardDecoration,
        padding: const EdgeInsets.only(left: 24, right: 10),
        child: Row(
          children: [
            Expanded(
              child: Opacity(
                opacity: 0.6,
                child: Text(
                  widget.hintText,
                  style: AgentProfileTheme.inputHintStyle,
                ),
              ),
            ),
            // 麦克风按钮
            _buildMicrophoneButton(),
            // 发送按钮
            _buildCollapsedSendButton(),
          ],
        ),
      ),
    );
  }

  /// 麦克风按钮 (收起状态)
  /// Figma规范: 36x36, 透明背景
  Widget _buildMicrophoneButton() {
    return GestureDetector(
      onTap: widget.onVoiceTap,
      child: Container(
        width: 36,
        height: 36,
        child: Icon(
          Icons.mic_none_outlined,
          size: 24,
          color: AgentProfileTheme.labelColor,
        ),
      ),
    );
  }

  /// 发送按钮 (收起状态)
  /// Figma规范: 32x32, 90%黑色背景, 圆角88.89
  Widget _buildCollapsedSendButton() {
    return GestureDetector(
      onTap: null, // 收起状态不可点击
      child: Container(
        width: 32,
        height: 32,
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.9),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(88.89),
          ),
        ),
        child: const Icon(
          Icons.arrow_upward_rounded,
          size: 16,
          color: Colors.white,
        ),
      ),
    );
  }

  /// 展开状态的输入卡片
  Widget _buildExpandedCard() {
    return Container(
      decoration: _expandedCardDecoration,
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 附件预览区域
          if (widget.attachments.isNotEmpty) ...[
            _buildAttachmentsPreview(),
            const SizedBox(height: 12),
          ],
          
          // 输入区域
          _buildInputArea(),
          
          const SizedBox(height: 16),
          
          // 操作工具栏
          _buildToolbar(),
        ],
      ),
    );
  }

  /// 展开卡片的装饰样式
  ShapeDecoration get _expandedCardDecoration => ShapeDecoration(
    color: Colors.white.withOpacity(0.50),
    shape: RoundedRectangleBorder(
      side: const BorderSide(
        width: 1.3,
        strokeAlign: BorderSide.strokeAlignOutside,
        color: Color(0xFF0066FF), // 蓝色边框
      ),
      borderRadius: BorderRadius.circular(20),
    ),
    shadows: const [
      BoxShadow(
        color: Color(0x14000000),
        blurRadius: 24,
        offset: Offset(0, 12),
        spreadRadius: 0,
      ),
    ],
  );

  /// 附件预览区域
  Widget _buildAttachmentsPreview() {
    return SizedBox(
      height: 43,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 4),
        itemCount: widget.attachments.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final attachment = widget.attachments[index];
          return _buildAttachmentItem(attachment);
        },
      ),
    );
  }

  /// 单个附件项
  Widget _buildAttachmentItem(ChatAttachment attachment) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          width: 43,
          height: 43,
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.04),
            borderRadius: BorderRadius.circular(4),
            image: attachment.displayUrl != null
                ? DecorationImage(
                    image: NetworkImage(attachment.displayUrl!),
                    fit: BoxFit.cover,
                  )
                : null,
          ),
          child: attachment.displayUrl == null
              ? const Icon(
                  Icons.image_outlined,
                  color: AgentProfileTheme.labelColor,
                  size: 20,
                )
              : null,
        ),
        // 删除按钮
        if (widget.onAttachmentRemove != null)
          Positioned(
            top: -6,
            right: -6,
            child: GestureDetector(
              onTap: () => widget.onAttachmentRemove!(attachment),
              child: Container(
                width: 18,
                height: 18,
                decoration: const BoxDecoration(
                  color: Colors.black54,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.close,
                  color: Colors.white,
                  size: 12,
                ),
              ),
            ),
          ),
      ],
    );
  }

  /// 输入区域
  Widget _buildInputArea() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: TextField(
        controller: _controller,
        focusNode: _focusNode,
        enabled: widget.enabled,
        style: const TextStyle(
          color: Colors.black,
          fontSize: 16,
          fontWeight: FontWeight.w500,
          height: 1,
        ),
        decoration: InputDecoration(
          hintText: widget.hintText,
          hintStyle: TextStyle(
            color: Colors.black.withOpacity(0.4),
            fontSize: 16,
            fontWeight: FontWeight.w400,
          ),
          border: InputBorder.none,
          contentPadding: EdgeInsets.zero,
          isDense: true,
        ),
        maxLines: 3,
        minLines: 1,
        textInputAction: TextInputAction.newline,
      ),
    );
  }

  /// 操作工具栏
  /// 按照Figma设计: 附件按钮 + 应用选择按钮 + 背景描述按钮 + "默认"模式按钮 + 发送按钮
  Widget _buildToolbar() {
    return Row(
      children: [
        // 附件按钮
        _buildToolButton(
          icon: Icons.attach_file_rounded,
          onTap: widget.onAttachmentTap,
        ),
        const SizedBox(width: 3.12),
        
        // 应用选择按钮
        _buildAppSelectorButton(),
        const SizedBox(width: 3.12),
        
        // 模式选择按钮
        _buildModeButton(),
        
        const Spacer(),
        
        // 发送按钮
        _buildSendButton(enabled: _hasText || widget.attachments.isNotEmpty),
      ],
    );
  }

  /// 应用选择按钮
  /// Figma规范: 宽68, 高32, 圆角21.33
  final GlobalKey _appSelectorKey = GlobalKey();
  
  Widget _buildAppSelectorButton() {
    final selectedApp = widget.selectedApp;
    final displayName = selectedApp?.name ?? '默认';
    
    return GestureDetector(
      key: _appSelectorKey,
      onTap: _showAppSelector,
      child: Container(
        height: 32,
        padding: const EdgeInsets.symmetric(horizontal: 11.61),
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.04),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(21.33),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 应用图标
            if (selectedApp != null) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: Image.asset(
                  selectedApp.iconPath,
                  width: 18,
                  height: 18,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => Icon(
                    Icons.apps_rounded,
                    size: 18,
                    color: AgentProfileTheme.titleColor,
                  ),
                ),
              ),
            ] else ...[
              Icon(
                Icons.apps_rounded,
                size: 18,
                color: AgentProfileTheme.titleColor,
              ),
            ],
            const SizedBox(width: 3.56),
            Text(
              displayName,
              style: TextStyle(
                color: Colors.black.withOpacity(0.9),
                fontSize: 12,
                fontWeight: FontWeight.w400,
                height: 1.67,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 显示应用选择弹窗
  void _showAppSelector() async {
    final RenderBox button = _appSelectorKey.currentContext!.findRenderObject() as RenderBox;
    final RenderBox overlay = Navigator.of(context).overlay!.context.findRenderObject() as RenderBox;
    
    final buttonPosition = button.localToGlobal(Offset.zero, ancestor: overlay);
    final buttonSize = button.size;
    
    // 计算弹窗位置（在按钮上方）
    final position = RelativeRect.fromLTRB(
      buttonPosition.dx,
      buttonPosition.dy - 280, // 弹窗高度约256 + 间距
      overlay.size.width - buttonPosition.dx - buttonSize.width,
      overlay.size.height - buttonPosition.dy,
    );
    
    final selectedApp = await showAppSelectorPopup(
      context,
      selectedApp: widget.selectedApp,
      position: position,
    );
    
    if (selectedApp != null) {
      widget.onAppSelected?.call(selectedApp);
    }
  }

  /// 工具按钮
  /// Figma规范: 32x32, 圆角112, 图标约19px
  Widget _buildToolButton({
    required IconData icon,
    VoidCallback? onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 32,
        height: 32,
        padding: const EdgeInsets.symmetric(horizontal: 3.12, vertical: 8.89),
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.04),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(112),
          ),
        ),
        child: Center(
          child: Icon(
            icon,
            size: 19,
            color: AgentProfileTheme.titleColor,
          ),
        ),
      ),
    );
  }

  /// 模式选择按钮
  /// Figma规范: 宽68, 高32, 圆角21.33
  Widget _buildModeButton() {
    return GestureDetector(
      onTap: widget.onModeTap,
      child: Container(
        width: 68,
        height: 32,
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.04),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(21.33),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.tune,
              size: 18,
              color: AgentProfileTheme.titleColor,
            ),
            const SizedBox(width: 3.56),
            Text(
              '默认',
              style: TextStyle(
                color: Colors.black.withOpacity(0.9),
                fontSize: 12,
                fontWeight: FontWeight.w400,
                height: 1.67,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 发送按钮
  Widget _buildSendButton({required bool enabled}) {
    final canSend = enabled && widget.enabled;
    
    return GestureDetector(
      onTap: canSend ? _handleSubmit : null,
      child: Container(
        width: 32,
        height: 32,
        decoration: BoxDecoration(
          color: canSend 
              ? Colors.black.withOpacity(0.9) 
              : Colors.black.withOpacity(0.04),
          borderRadius: BorderRadius.circular(89),
        ),
        child: Icon(
          Icons.arrow_upward_rounded,
          size: 18,
          color: canSend ? Colors.white : AgentProfileTheme.labelColor,
        ),
      ),
    );
  }
}

