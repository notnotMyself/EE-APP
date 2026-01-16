import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/conversation_repository.dart';
import '../../domain/models/conversation_summary.dart';
import '../widgets/conversation_card.dart';
import '../pages/conversation_page.dart';
import '../../../agents/domain/models/agent.dart';

/// Provider for conversation summaries
final conversationSummariesProvider = FutureProvider<List<ConversationSummary>>((ref) async {
  final repository = ConversationRepository();
  return repository.getConversationSummaries();
});

/// Conversations list page - shows all conversations with AI employees
class ConversationsListPage extends ConsumerStatefulWidget {
  const ConversationsListPage({super.key});

  @override
  ConsumerState<ConversationsListPage> createState() =>
      _ConversationsListPageState();
}

class _ConversationsListPageState
    extends ConsumerState<ConversationsListPage> {
  bool _isSearching = false;
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final conversationsAsync = ref.watch(conversationSummariesProvider);

    return Scaffold(
      appBar: AppBar(
        title: _isSearching
            ? TextField(
                controller: _searchController,
                autofocus: true,
                decoration: const InputDecoration(
                  hintText: '搜索对话内容...',
                  border: InputBorder.none,
                ),
                style: const TextStyle(fontSize: 16),
                onChanged: (query) {
                  // TODO: Implement search functionality
                },
              )
            : const Text('消息'),
        actions: [
          IconButton(
            icon: Icon(_isSearching ? Icons.close : Icons.search),
            onPressed: () {
              setState(() {
                _isSearching = !_isSearching;
                if (!_isSearching) {
                  _searchController.clear();
                }
              });
            },
          ),
        ],
      ),
      body: conversationsAsync.when(
        data: (conversations) {
          if (conversations.isEmpty) {
            return _buildEmptyState();
          }
          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(conversationSummariesProvider);
            },
            child: ListView.builder(
              itemCount: conversations.length,
              itemBuilder: (context, index) {
                final conversation = conversations[index];
                return ConversationCard(
                  conversation: conversation,
                  onTap: () {
                    // 创建简化版 Agent 对象并导航到对话页
                    final agent = Agent(
                      id: conversation.agentId,
                      name: conversation.agentName,
                      description: '', // 简化版没有描述
                      role: conversation.agentRole,
                      avatarUrl: conversation.agentAvatarUrl,
                    );
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (context) => ConversationPage(
                          agent: agent,
                          conversationId: conversation.id,
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 48, color: Colors.red.shade300),
              const SizedBox(height: 16),
              Text('加载失败: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(conversationSummariesProvider),
                child: const Text('重试'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            '暂无对话',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '与AI员工开始对话后，会在这里显示',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => context.go('/agents'),
            icon: const Icon(Icons.smart_toy),
            label: const Text('浏览AI员工'),
          ),
        ],
      ),
    );
  }
}
