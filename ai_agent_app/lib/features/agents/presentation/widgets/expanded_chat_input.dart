import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../theme/agent_profile_theme.dart';
import 'app_selector_popup.dart';
import 'attachment_menu_popup.dart';

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
/// - 操作工具栏（附件、应用选择）
/// - 语音输入（麦克风按钮）
class ExpandedChatInput extends StatefulWidget {
  final String hintText;
  final ValueChanged<String> onSubmit;
  final VoidCallback? onImageTap;                // 添加图片
  final VoidCallback? onFileTap;                 // 添加文件
  final VoidCallback? onFigmaTap;                // 添加 Figma 链接
  final VoidCallback? onVoiceTap;                // 语音输入
  final List<ChatAttachment> attachments;
  final ValueChanged<ChatAttachment>? onAttachmentRemove;
  final bool enabled;
  final bool initiallyExpanded;                  // 是否默认展开
  final bool chatMode;                            // 聊天模式：保持单行，不展开
  final AppInfo? selectedApp;                    // 当前选中的应用
  final ValueChanged<AppInfo?>? onAppSelected;  // 应用选择回调

  const ExpandedChatInput({
    super.key,
    this.hintText = '简单描述设计方案背景与目标', // Figma: 输入框组件默认文案
    required this.onSubmit,
    this.onImageTap,
    this.onFileTap,
    this.onFigmaTap,
    this.onVoiceTap,
    this.attachments = const [],
    this.onAttachmentRemove,
    this.enabled = true,
    this.initiallyExpanded = false,
    this.chatMode = false,
    this.selectedApp,
    this.onAppSelected,
  });

  @override
  State<ExpandedChatInput> createState() => _ExpandedChatInputState();
}

class _ExpandedChatInputState extends State<ExpandedChatInput> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  late bool _isExpanded = widget.initiallyExpanded;
  bool _hasText = false;
  bool _isFocused = false;

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
    final focused = _focusNode.hasFocus;
    if (focused != _isFocused) {
      setState(() => _isFocused = focused);
    }
    if (focused && !_isExpanded) {
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
    // chatMode: 始终显示单行输入框，不展开
    if (widget.chatMode) {
      return _buildChatModeInput();
    }

    // 如果未展开，显示简单输入框
    if (!_isExpanded) {
      return _buildCollapsedInput();
    }

    // 展开状态显示完整输入卡片
    return _buildExpandedCard();
  }

  /// 聊天模式的单行输入框
  /// 始终保持单行，不会展开，支持直接输入和发送
  Widget _buildChatModeInput() {
    final hasText = _hasText;
    final canSend = hasText && widget.enabled;

    // Figma 设计稿：56px 高，白色 68% 背景，白色 1px 边框，pill 圆角
    return Container(
      width: double.infinity,
      height: 56,
      clipBehavior: Clip.antiAlias,
      decoration: ShapeDecoration(
        color: Colors.white.withOpacity(0.68),
        shape: RoundedRectangleBorder(
          side: const BorderSide(width: 1, color: Colors.white),
          borderRadius: BorderRadius.circular(100),
        ),
      ),
      padding: const EdgeInsets.only(left: 24, right: 10),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              decoration: InputDecoration(
                hintText: widget.hintText,
                hintStyle: TextStyle(
                  color: Colors.black.withOpacity(0.60),
                  fontSize: 16,
                  fontFamily: 'OPPO Sans 4.0',
                  fontWeight: FontWeight.w400,
                  height: 1,
                ),
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
                contentPadding: EdgeInsets.zero,
                isDense: true,
              ),
              style: const TextStyle(
                color: Colors.black,
                fontSize: 16,
                fontFamily: 'OPPO Sans 4.0',
                fontWeight: FontWeight.w400,
                height: 1,
              ),
              cursorColor: Colors.black.withOpacity(0.54),
              maxLines: 1,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _handleSubmit(),
              enabled: widget.enabled,
            ),
          ),
          const SizedBox(width: 10),
          // 发送按钮: 保持之前的样式
          _buildSendButton(enabled: canSend),
        ],
      ),
    );
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
        decoration: ShapeDecoration(
          color: AgentProfileTheme.cardBackground,
          shape: RoundedRectangleBorder(
            side: const BorderSide(width: 1, color: Colors.white),
            borderRadius: BorderRadius.circular(100),
          ),
        ),
        padding: const EdgeInsets.only(left: 24, right: 10),
        child: Row(
          children: [
            Expanded(
              child: Opacity(
                opacity: 0.54, // Figma: couiColorLabelSecondary (black 54%)
                child: Text(
                  widget.hintText,
                  style: AgentProfileTheme.inputHintStyle,
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ),
            ),
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
        child: SvgPicture.asset(
          'assets/icons/chat/send_icon.svg',
          width: 16,
          height: 16,
          colorFilter: const ColorFilter.mode(Colors.white, BlendMode.srcIn),
        ),
      ),
    );
  }

  /// 展开状态的输入卡片
  /// Figma (1922:19780): 329x152, padding 12px 16px, borderRadius 20px, column gap 2px
  Widget _buildExpandedCard() {
    final hasAttachments = widget.attachments.isNotEmpty;
    // Figma: fixed 152px height without attachments; taller when attachments present
    final cardHeight = hasAttachments ? 152.0 + 53.0 : 152.0;

    return Container(
      height: cardHeight,
      decoration: _expandedCardDecoration,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12), // Figma: padding 12px 16px
      child: Column(
        mainAxisSize: MainAxisSize.max,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 附件预览区域
          if (hasAttachments) ...[
            _buildAttachmentsPreview(),
            const SizedBox(height: 10),
          ],

          // 输入区域 - Figma: text height 86px, fills remaining space
          Expanded(
            child: _buildInputArea(),
          ),

          const SizedBox(height: 2), // Figma: column gap 2px

          // 操作工具栏
          _buildToolbar(),
        ],
      ),
    );
  }

  /// 展开卡片的装饰样式
  /// Figma 激活态(1922:19776): 和未激活态完全一样，NO blue border
  /// 质感样式/面板（亮色）: borderRadius 20px, inset shadows, backdrop blur
  ShapeDecoration get _expandedCardDecoration => ShapeDecoration(
    color: Colors.white.withOpacity(0.68),
    shape: RoundedRectangleBorder(
      side: const BorderSide(
        width: 1,
        color: Colors.white, // Figma: 无蓝色边框，激活和未激活一样
      ),
      borderRadius: BorderRadius.circular(20),
    ),
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
  /// 支持本地文件和网络URL的图片预览，兼容 Web 和移动端
  Widget _buildAttachmentItem(ChatAttachment attachment) {
    final displayUrl = attachment.displayUrl;
    final localPath = attachment.localPath;
    
    // 判断图片来源
    final hasLocalFile = localPath != null && localPath.isNotEmpty;
    final hasNetworkUrl = displayUrl != null && 
                          displayUrl.isNotEmpty && 
                          (displayUrl.startsWith('http://') || displayUrl.startsWith('https://'));
    final isBlobUrl = localPath != null && localPath.startsWith('blob:');
    
    Widget imageWidget;
    if (isBlobUrl) {
      // Web 平台的 blob URL
      imageWidget = Image.network(
        localPath,
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => _buildImagePlaceholder(),
      );
    } else if (hasLocalFile && !hasNetworkUrl) {
      // 移动端本地文件
      imageWidget = Image.file(
        File(localPath),
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => _buildImagePlaceholder(),
      );
    } else if (hasNetworkUrl) {
      // 网络URL
      imageWidget = Image.network(
        displayUrl,
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
    } else {
      imageWidget = _buildImagePlaceholder();
    }

    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          width: 43,
          height: 43,
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.04),
            borderRadius: BorderRadius.circular(4),
          ),
          clipBehavior: Clip.antiAlias,
          child: imageWidget,
        ),
        // 上传状态指示器
        if (attachment.status == AttachmentStatus.uploading)
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.3),
                borderRadius: BorderRadius.circular(4),
              ),
              child: const Center(
                child: SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation(Colors.white),
                  ),
                ),
              ),
            ),
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

  /// 图片占位符
  Widget _buildImagePlaceholder() {
    return Container(
      color: Colors.black.withOpacity(0.04),
      child: const Icon(
        Icons.image_outlined,
        color: AgentProfileTheme.labelColor,
        size: 20,
      ),
    );
  }

  /// 输入区域
  /// Figma: text area fills remaining space, hint text at top-left
  Widget _buildInputArea() {
    return TextField(
      controller: _controller,
      focusNode: _focusNode,
      enabled: widget.enabled,
      style: const TextStyle(
        color: Colors.black,
        fontSize: 16, // Figma: Body/L · Regular
        fontWeight: FontWeight.w400,
        height: 1.375, // Figma: 1.375em
      ),
      decoration: InputDecoration(
        hintText: widget.hintText,
        hintStyle: TextStyle(
          color: Colors.black.withOpacity(0.54), // Figma: 中性色/文本&图标（黑）/54 · Secondary
          fontSize: 16, // Figma: Body/L · Regular
          fontWeight: FontWeight.w400,
          height: 1.375, // Figma: 1.375em
        ),
        border: InputBorder.none,
        enabledBorder: InputBorder.none,
        focusedBorder: InputBorder.none,
        disabledBorder: InputBorder.none,
        errorBorder: InputBorder.none,
        focusedErrorBorder: InputBorder.none,
        filled: false,
        contentPadding: EdgeInsets.zero,
        isDense: true,
      ),
      maxLines: null, // Figma: text area fills available space
      expands: true,
      textAlignVertical: TextAlignVertical.top,
      textInputAction: TextInputAction.newline,
    );
  }

  /// 附件按钮的 GlobalKey
  final GlobalKey _attachmentKey = GlobalKey();

  /// 操作工具栏
  /// Figma (1922:19776 activated): @ 账号(唤起应用选择) + 附件 ... 发送
  /// Figma layout: row, space-between, left group gap 12px, right send button
  Widget _buildToolbar() {
    return Row(
      children: [
        // @ 账号按钮 → 唤起应用选择弹窗
        _buildAccountButton(),
        const SizedBox(width: 12), // Figma: left group gap 12px

        // 附件按钮
        _buildAttachmentButton(),

        const Spacer(),

        // 发送按钮
        _buildSendButton(enabled: _hasText || widget.attachments.isNotEmpty),
      ],
    );
  }

  /// 附件按钮
  /// Figma: 36x36, borderRadius 112, fill rgba(0,0,0,0.04)
  /// Note: attachment_icon.svg already includes its own 36x36 background circle
  Widget _buildAttachmentButton() {
    return GestureDetector(
      key: _attachmentKey,
      onTap: _showAttachmentMenu,
      child: SvgPicture.asset(
        'assets/icons/chat/attachment_icon.svg',
        width: 36,
        height: 36,
      ),
    );
  }

  /// 显示附件菜单弹窗
  void _showAttachmentMenu() async {
    final RenderBox button =
        _attachmentKey.currentContext!.findRenderObject() as RenderBox;
    final RenderBox overlay =
        Navigator.of(context).overlay!.context.findRenderObject() as RenderBox;

    final buttonPosition = button.localToGlobal(Offset.zero, ancestor: overlay);
    final buttonSize = button.size;

    // 计算弹窗位置（在按钮上方）
    final position = RelativeRect.fromLTRB(
      buttonPosition.dx,
      buttonPosition.dy - 140, // 弹窗高度约128 + 间距
      overlay.size.width - buttonPosition.dx - buttonSize.width,
      overlay.size.height - buttonPosition.dy,
    );

    final attachmentType = await showAttachmentMenuPopup(
      context,
      position: position,
    );

    if (attachmentType != null) {
      switch (attachmentType) {
        case AttachmentType.image:
          widget.onImageTap?.call();
          break;
        case AttachmentType.file:
          widget.onFileTap?.call();
          break;
        case AttachmentType.figma:
          widget.onFigmaTap?.call();
          break;
      }
    }
  }

  /// 应用选择弹窗 GlobalKey
  final GlobalKey _appSelectorKey = GlobalKey();

  /// @ 账号按钮 → 唤起应用选择弹窗
  /// Figma: 36x36, borderRadius 112, fill rgba(0,0,0,0.04), account icon 20x20
  Widget _buildAccountButton() {
    return GestureDetector(
      key: _appSelectorKey,
      onTap: _showAppSelector,
      child: Container(
        width: 36, // Figma: 36x36
        height: 36,
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.04), // Figma: 中性色/填充色/4 · Thin
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(112), // Figma: borderRadius 112
          ),
        ),
        child: Center(
          child: SvgPicture.asset(
            'assets/icons/chat/account_icon.svg',
            width: 20, // Figma: 20x20
            height: 20,
          ),
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

  /// 发送按钮
  /// Figma规范: 36x36, 90%黑色背景, 圆角112, 向右箭头图标
  Widget _buildSendButton({required bool enabled}) {
    final canSend = enabled && widget.enabled;

    return GestureDetector(
      onTap: canSend ? _handleSubmit : null,
      child: Container(
        width: 36, // Figma: 36x36
        height: 36,
        decoration: BoxDecoration(
          color: canSend
              ? Colors.black.withOpacity(0.9) // Figma: 中性色/文本&图标（黑）/90 · Primary
              : Colors.black.withOpacity(0.04), // Figma: 中性色/填充色/4 · Thin
          borderRadius: BorderRadius.circular(112), // Figma: borderRadius 112
        ),
        child: Center(
          child: SvgPicture.asset(
            'assets/icons/chat/send_icon.svg',
            width: 20, // Figma: 20x20
            height: 20,
            colorFilter: const ColorFilter.mode(
              Colors.white,
              BlendMode.srcIn,
            ),
          ),
        ),
      ),
    );
  }
}

