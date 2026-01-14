import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class BottomChatBar extends StatefulWidget {
  final Function(String) onSend;

  const BottomChatBar({
    super.key,
    required this.onSend,
  });

  @override
  State<BottomChatBar> createState() => _BottomChatBarState();
}

class _BottomChatBarState extends State<BottomChatBar> {
  final TextEditingController _controller = TextEditingController();
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(() {
      setState(() {
        _hasText = _controller.text.trim().isNotEmpty;
      });
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleSend() {
    if (_hasText) {
      widget.onSend(_controller.text);
      _controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
          colors: [
            Colors.white.withOpacity(0.9),
            Colors.white.withOpacity(0.0),
          ],
        ),
      ),
      child: Row(
        children: [
           // Agents List Button
          _buildActionButton(
            context,
            icon: Icons.apps,
            onTap: () => context.go('/agents'),
            color: Colors.black54,
          ),
          const SizedBox(width: 8),

          // Input Area
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.8),
                borderRadius: BorderRadius.circular(30),
                border: Border.all(color: Colors.white),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  // Mic Button
                  IconButton(
                    icon: const Icon(Icons.mic_none),
                    onPressed: () {},
                    color: Colors.black45,
                  ),

                  // Text Field
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        hintText: 'Ask your secretary...',
                        hintStyle: TextStyle(color: Colors.black38),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(horizontal: 8),
                      ),
                      style: const TextStyle(color: Colors.black87),
                      onSubmitted: (_) => _handleSend(),
                    ),
                  ),

                  // Send Button
                  Container(
                    margin: const EdgeInsets.only(right: 4),
                    decoration: BoxDecoration(
                      color: _hasText ? Colors.blue.shade600 : Colors.grey.shade200,
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.arrow_upward, size: 20),
                      onPressed: _hasText ? _handleSend : null,
                      color: _hasText ? Colors.white : Colors.grey.shade400,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(
                        minWidth: 36,
                        minHeight: 36,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(
    BuildContext context, {
    required IconData icon,
    required VoidCallback onTap,
    required Color color,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: IconButton(
        icon: Icon(icon),
        onPressed: onTap,
        color: color,
      ),
    );
  }
}
