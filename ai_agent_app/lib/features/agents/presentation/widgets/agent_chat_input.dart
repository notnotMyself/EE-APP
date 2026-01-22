import 'package:flutter/material.dart';
import '../theme/agent_profile_theme.dart';

/// AI员工对话输入框组件
/// 
/// 基于 Figma 设计稿实现的胶囊形输入框
class AgentChatInput extends StatefulWidget {
  final String hintText;
  final ValueChanged<String> onSubmit;
  final bool enabled;

  const AgentChatInput({
    super.key,
    this.hintText = '简单描述下方案背景与目标',
    required this.onSubmit,
    this.enabled = true,
  });

  @override
  State<AgentChatInput> createState() => _AgentChatInputState();
}

class _AgentChatInputState extends State<AgentChatInput> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_onTextChanged);
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

  void _handleSubmit() {
    final text = _controller.text.trim();
    if (text.isNotEmpty) {
      widget.onSubmit(text);
      _controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: AgentProfileTheme.inputHeight,
      decoration: AgentProfileTheme.cardDecoration,
      padding: const EdgeInsets.only(
        left: 24,
        right: 10,
      ),
      child: Row(
        children: [
          // 输入框
          Expanded(
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              enabled: widget.enabled,
              style: AgentProfileTheme.inputHintStyle,
              decoration: InputDecoration(
                hintText: widget.hintText,
                hintStyle: AgentProfileTheme.inputHintStyle.copyWith(
                  color: Colors.black.withOpacity(0.6),
                ),
                border: InputBorder.none,
                contentPadding: EdgeInsets.zero,
                isDense: true,
              ),
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _handleSubmit(),
            ),
          ),
          // 发送按钮
          _buildSendButton(),
        ],
      ),
    );
  }

  Widget _buildSendButton() {
    return GestureDetector(
      onTap: _hasText ? _handleSubmit : null,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: _hasText 
              ? AgentProfileTheme.accentBlue 
              : Colors.transparent,
          shape: BoxShape.circle,
        ),
        child: Icon(
          Icons.arrow_upward_rounded,
          size: 20,
          color: _hasText 
              ? Colors.white 
              : AgentProfileTheme.labelColor,
        ),
      ),
    );
  }
}

