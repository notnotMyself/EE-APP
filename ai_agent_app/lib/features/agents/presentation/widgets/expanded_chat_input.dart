import 'package:flutter/material.dart';
import '../theme/agent_profile_theme.dart';

/// 图片附件数据模型
class ChatAttachment {
  final String id;
  final String? localPath;
  final String? networkUrl;
  final String? thumbnailUrl;

  const ChatAttachment({
    required this.id,
    this.localPath,
    this.networkUrl,
    this.thumbnailUrl,
  });

  String? get displayUrl => thumbnailUrl ?? networkUrl ?? localPath;
}

/// 展开式聊天输入卡片
/// 
/// 基于 Figma 设计稿实现，支持：
/// - 图片/附件预览
/// - 文字输入
/// - 操作工具栏（拍照、相册、模式选择）
class ExpandedChatInput extends StatefulWidget {
  final String hintText;
  final ValueChanged<String> onSubmit;
  final VoidCallback? onCameraTap;
  final VoidCallback? onGalleryTap;
  final VoidCallback? onModeTap;
  final List<ChatAttachment> attachments;
  final ValueChanged<ChatAttachment>? onAttachmentRemove;
  final bool enabled;

  const ExpandedChatInput({
    super.key,
    this.hintText = '简单描述下方案背景与目标',
    required this.onSubmit,
    this.onCameraTap,
    this.onGalleryTap,
    this.onModeTap,
    this.attachments = const [],
    this.onAttachmentRemove,
    this.enabled = true,
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
            _buildSendButton(enabled: false),
          ],
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
  Widget _buildToolbar() {
    return Row(
      children: [
        // 拍照按钮
        _buildToolButton(
          icon: Icons.camera_alt_outlined,
          onTap: widget.onCameraTap,
        ),
        const SizedBox(width: 3),
        
        // 相册按钮
        _buildToolButton(
          icon: Icons.photo_library_outlined,
          onTap: widget.onGalleryTap,
        ),
        const SizedBox(width: 3),
        
        // 模式选择按钮
        _buildModeButton(),
        
        const Spacer(),
        
        // 发送按钮
        _buildSendButton(enabled: _hasText || widget.attachments.isNotEmpty),
      ],
    );
  }

  /// 工具按钮
  Widget _buildToolButton({
    required IconData icon,
    VoidCallback? onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 32,
        height: 32,
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.04),
          borderRadius: BorderRadius.circular(112),
        ),
        child: Icon(
          icon,
          size: 18,
          color: AgentProfileTheme.titleColor,
        ),
      ),
    );
  }

  /// 模式选择按钮
  Widget _buildModeButton() {
    return GestureDetector(
      onTap: widget.onModeTap,
      child: Container(
        height: 32,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.04),
          borderRadius: BorderRadius.circular(21),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.tune,
              size: 18,
              color: AgentProfileTheme.titleColor,
            ),
            const SizedBox(width: 4),
            Text(
              '默认',
              style: TextStyle(
                color: Colors.black.withOpacity(0.9),
                fontSize: 12,
                fontWeight: FontWeight.w400,
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

