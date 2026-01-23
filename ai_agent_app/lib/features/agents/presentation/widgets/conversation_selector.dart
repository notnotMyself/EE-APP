import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timeago/timeago.dart' as timeago;

import '../../../conversations/domain/models/conversation.dart';

/// 会话选择器组件
///
/// 显示用户与特定Agent的所有会话列表，支持：
/// - 查看会话列表（标题、时间）
/// - 创建新会话
/// - 切换会话
/// - 重命名会话
class ConversationSelector extends ConsumerStatefulWidget {
  final String agentId;
  final String? currentConversationId;
  final List<Conversation> conversations;
  final VoidCallback onNewConversation;
  final Function(String conversationId) onSelectConversation;
  final Function(String conversationId, String newTitle) onRenameConversation;

  const ConversationSelector({
    super.key,
    required this.agentId,
    this.currentConversationId,
    required this.conversations,
    required this.onNewConversation,
    required this.onSelectConversation,
    required this.onRenameConversation,
  });

  /// 显示会话选择器
  static void show(
    BuildContext context, {
    required String agentId,
    String? currentConversationId,
    required List<Conversation> conversations,
    required VoidCallback onNewConversation,
    required Function(String conversationId) onSelectConversation,
    required Function(String conversationId, String newTitle)
        onRenameConversation,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ConversationSelector(
        agentId: agentId,
        currentConversationId: currentConversationId,
        conversations: conversations,
        onNewConversation: onNewConversation,
        onSelectConversation: onSelectConversation,
        onRenameConversation: onRenameConversation,
      ),
    );
  }

  @override
  ConsumerState<ConversationSelector> createState() =>
      _ConversationSelectorState();
}

class _ConversationSelectorState extends ConsumerState<ConversationSelector> {
  /// 显示重命名对话框
  void _showRenameDialog(Conversation conversation) {
    final controller = TextEditingController(text: conversation.title ?? '');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('重命名会话'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: InputDecoration(
            hintText: '输入新标题...',
            hintStyle: TextStyle(color: Colors.black.withOpacity(0.4)),
            filled: true,
            fillColor: Colors.black.withOpacity(0.04),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
          ),
          maxLength: 50,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              final newTitle = controller.text.trim();
              if (newTitle.isNotEmpty) {
                Navigator.pop(context);
                widget.onRenameConversation(conversation.id, newTitle);
              }
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;

    return Container(
      constraints: BoxConstraints(
        maxHeight: screenHeight * 0.7,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 顶部拖动条
          Container(
            margin: const EdgeInsets.symmetric(vertical: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.2),
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // 标题栏
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: Row(
              children: [
                const Text(
                  '会话列表',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                    widget.onNewConversation();
                  },
                  icon: const Icon(Icons.add, size: 20),
                  label: const Text('新建'),
                  style: TextButton.styleFrom(
                    foregroundColor: const Color(0xFF2C69FF),
                  ),
                ),
              ],
            ),
          ),

          const Divider(height: 1),

          // 会话列表
          Flexible(
            child: widget.conversations.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    shrinkWrap: true,
                    itemCount: widget.conversations.length,
                    itemBuilder: (context, index) {
                      final conversation = widget.conversations[index];
                      final isSelected =
                          conversation.id == widget.currentConversationId;

                      return _buildConversationItem(
                        conversation,
                        isSelected: isSelected,
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  /// 构建空状态
  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.chat_bubble_outline,
              size: 64,
              color: Colors.black.withOpacity(0.2),
            ),
            const SizedBox(height: 16),
            Text(
              '暂无会话',
              style: TextStyle(
                fontSize: 16,
                color: Colors.black.withOpacity(0.4),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '点击"新建"创建第一个会话',
              style: TextStyle(
                fontSize: 14,
                color: Colors.black.withOpacity(0.3),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建会话列表项
  Widget _buildConversationItem(
    Conversation conversation, {
    required bool isSelected,
  }) {
    // 格式化时间
    String formattedTime = '';
    if (conversation.lastMessageAt != null) {
      formattedTime = timeago.format(
        conversation.lastMessageAt!,
        locale: 'zh',
      );
    } else if (conversation.startedAt != null) {
      formattedTime = timeago.format(
        conversation.startedAt,
        locale: 'zh',
      );
    }

    return InkWell(
      onTap: isSelected
          ? null
          : () {
              Navigator.pop(context);
              widget.onSelectConversation(conversation.id);
            },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF2C69FF).withOpacity(0.1) : null,
          border: Border(
            bottom: BorderSide(
              color: Colors.black.withOpacity(0.05),
              width: 1,
            ),
          ),
        ),
        child: Row(
          children: [
            // 左侧选中指示器
            if (isSelected)
              Container(
                width: 4,
                height: 40,
                margin: const EdgeInsets.only(right: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFF2C69FF),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),

            // 会话信息
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    conversation.title ?? '未命名会话',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                      color: isSelected
                          ? const Color(0xFF2C69FF)
                          : Colors.black.withOpacity(0.8),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    formattedTime,
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.black.withOpacity(0.4),
                    ),
                  ),
                ],
              ),
            ),

            // 重命名按钮
            IconButton(
              onPressed: () => _showRenameDialog(conversation),
              icon: Icon(
                Icons.edit_outlined,
                size: 20,
                color: Colors.black.withOpacity(0.4),
              ),
              tooltip: '重命名',
            ),
          ],
        ),
      ),
    );
  }
}
