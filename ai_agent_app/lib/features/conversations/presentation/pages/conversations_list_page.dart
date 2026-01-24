import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../data/conversation_repository.dart';
import '../../domain/models/conversation_summary.dart';
import '../pages/conversation_page.dart';
import '../../../agents/domain/models/agent.dart';
import '../../../agents/presentation/theme/agent_profile_theme.dart';

/// Provider for conversation summaries
final conversationSummariesProvider =
    FutureProvider<List<ConversationSummary>>((ref) async {
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

class _ConversationsListPageState extends ConsumerState<ConversationsListPage> {
  bool _isSearching = false;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final conversationsAsync = ref.watch(conversationSummariesProvider);

    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      body: CustomScrollView(
        slivers: [
          // 自定义 AppBar
          SliverAppBar(
            backgroundColor: AgentProfileTheme.backgroundColor,
            elevation: 0,
            floating: true,
            pinned: true,
            expandedHeight: _isSearching ? 80 : 130,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                padding: const EdgeInsets.fromLTRB(20, 56, 20, 12),
                child: _isSearching
                    ? _buildSearchBar()
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Text(
                            '消息',
                            style: GoogleFonts.poppins(
                              fontSize: 26,
                              fontWeight: FontWeight.w700,
                              color: AgentProfileTheme.titleColor,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '与AI员工的对话记录',
                            style: GoogleFonts.poppins(
                              fontSize: 13,
                              color: AgentProfileTheme.labelColor,
                            ),
                          ),
                        ],
                      ),
              ),
            ),
            // 移除了搜索按钮
          ),

          // 内容区域
          conversationsAsync.when(
            data: (conversations) {
              // 按 agentId 分组，每个 AI 员工只保留最新的一条会话
              final latestByAgent = <String, ConversationSummary>{};
              for (final c in conversations) {
                final existing = latestByAgent[c.agentId];
                if (existing == null ||
                    (c.lastMessageAt != null &&
                        (existing.lastMessageAt == null ||
                            c.lastMessageAt!.isAfter(existing.lastMessageAt!)))) {
                  latestByAgent[c.agentId] = c;
                }
              }
              
              // 转换为列表并按时间排序（最新的在前）
              var uniqueConversations = latestByAgent.values.toList()
                ..sort((a, b) {
                  if (a.lastMessageAt == null && b.lastMessageAt == null) return 0;
                  if (a.lastMessageAt == null) return 1;
                  if (b.lastMessageAt == null) return -1;
                  return b.lastMessageAt!.compareTo(a.lastMessageAt!);
                });

              // Filter by search query
              final filtered = _searchQuery.isEmpty
                  ? uniqueConversations
                  : uniqueConversations
                      .where((c) =>
                          c.agentName
                              .toLowerCase()
                              .contains(_searchQuery.toLowerCase()) ||
                          (c.lastMessageContent
                                  ?.toLowerCase()
                                  .contains(_searchQuery.toLowerCase()) ??
                              false))
                      .toList();

              if (filtered.isEmpty) {
                return SliverFillRemaining(
                  child: _buildEmptyState(),
                );
              }

              return SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final conversation = filtered[index];
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _ConversationCard(
                          conversation: conversation,
                          onTap: () => _navigateToConversation(conversation),
                        ),
                      );
                    },
                    childCount: filtered.length,
                  ),
                ),
              );
            },
            loading: () => const SliverFillRemaining(
              child: Center(
                child: CircularProgressIndicator(
                  color: AgentProfileTheme.accentBlue,
                ),
              ),
            ),
            error: (error, stack) => SliverFillRemaining(
              child: _buildErrorState(error),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Container(
        height: 52,
        decoration: BoxDecoration(
          color: AgentProfileTheme.cardBackground,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white, width: 1),
        ),
        child: TextField(
          controller: _searchController,
          autofocus: true,
          style: GoogleFonts.poppins(
            fontSize: 15,
            color: AgentProfileTheme.titleColor,
          ),
          decoration: InputDecoration(
            hintText: '搜索对话内容...',
            hintStyle: GoogleFonts.poppins(
              fontSize: 15,
              color: AgentProfileTheme.labelColor.withOpacity(0.6),
            ),
            prefixIcon: const Icon(
              Icons.search_rounded,
              color: AgentProfileTheme.labelColor,
            ),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 16,
            ),
          ),
          onChanged: (query) {
            setState(() {
              _searchQuery = query;
            });
          },
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: AgentProfileTheme.cardBackground,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 2),
              ),
              child: const Icon(
                Icons.chat_bubble_outline_rounded,
                size: 48,
                color: AgentProfileTheme.labelColor,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              _searchQuery.isEmpty ? '暂无对话' : '未找到相关对话',
              style: GoogleFonts.poppins(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AgentProfileTheme.titleColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _searchQuery.isEmpty
                  ? '与AI员工开始对话后，会在这里显示'
                  : '试试其他关键词',
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: AgentProfileTheme.labelColor,
              ),
              textAlign: TextAlign.center,
            ),
            if (_searchQuery.isEmpty) ...[
              const SizedBox(height: 32),
              _buildActionButton(
                onPressed: () => context.go('/agents'),
                icon: Icons.smart_toy_outlined,
                label: '浏览AI员工',
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: const Color(0xFFEF4444).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.error_outline_rounded,
                size: 40,
                color: Color(0xFFEF4444),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              '加载失败',
              style: GoogleFonts.poppins(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AgentProfileTheme.titleColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '$error',
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: AgentProfileTheme.labelColor,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            _buildActionButton(
              onPressed: () => ref.invalidate(conversationSummariesProvider),
              icon: Icons.refresh_rounded,
              label: '重试',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton({
    required VoidCallback onPressed,
    required IconData icon,
    required String label,
  }) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AgentProfileTheme.accentBlue,
            AgentProfileTheme.accentBlue.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AgentProfileTheme.accentBlue.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, size: 20),
        label: Text(
          label,
          style: GoogleFonts.poppins(fontWeight: FontWeight.w500),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          foregroundColor: Colors.white,
          shadowColor: Colors.transparent,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }

  void _navigateToConversation(ConversationSummary conversation) {
    final agent = Agent(
      id: conversation.agentId,
      name: conversation.agentName,
      description: '',
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
  }
}

class _ConversationCard extends StatelessWidget {
  const _ConversationCard({
    required this.conversation,
    required this.onTap,
  });

  final ConversationSummary conversation;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AgentProfileTheme.cardBackground,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white, width: 1),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.03),
              blurRadius: 12,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            // Avatar
            _buildAvatar(),
            const SizedBox(width: 14),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          conversation.agentName,
                          style: GoogleFonts.poppins(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: AgentProfileTheme.titleColor,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _formatTime(conversation.lastMessageAt),
                        style: GoogleFonts.poppins(
                          fontSize: 12,
                          color: AgentProfileTheme.labelColor,
                        ),
                      ),
                    ],
                  ),
                  // 移除了显示技术名称（agentRole）的部分
                  if (conversation.lastMessageContent != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      conversation.lastMessageContent!,
                      style: GoogleFonts.poppins(
                        fontSize: 14,
                        color: AgentProfileTheme.labelColor,
                        height: 1.4,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ],
              ),
            ),

            // Arrow
            const SizedBox(width: 8),
            Icon(
              Icons.chevron_right_rounded,
              color: AgentProfileTheme.labelColor.withOpacity(0.5),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    // 根据 Agent role 映射到对应的头像
    String? roleAvatar;
    switch (conversation.agentRole) {
      case 'design_validator':
        roleAvatar = AgentProfileTheme.chrisChenAvatar;
        break;
      case 'ai_news_crawler':
        roleAvatar = 'assets/images/secretary-girl-avatar.png'; // 码码
        break;
      case 'dev_efficiency_analyst':
        roleAvatar = 'assets/images/secretary-woman-avatar.png'; // 商商
        break;
    }

    return Container(
      width: 52,
      height: 52,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AgentProfileTheme.avatarPlaceholder,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: roleAvatar != null
          ? Image.asset(
              roleAvatar,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => _buildAvatarFallback(),
            )
          : conversation.agentAvatarUrl != null
              ? Image.network(
                  conversation.agentAvatarUrl!,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _buildAvatarFallback(),
                )
              : _buildAvatarFallback(),
    );
  }

  Widget _buildAvatarFallback() {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AgentProfileTheme.accentBlue.withOpacity(0.8),
            AgentProfileTheme.accentBlue,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Center(
        child: Text(
          conversation.agentName.isNotEmpty
              ? conversation.agentName[0].toUpperCase()
              : '?',
          style: GoogleFonts.poppins(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
      ),
    );
  }

  String _formatTime(DateTime? dateTime) {
    if (dateTime == null) return '';

    final now = DateTime.now();
    final diff = now.difference(dateTime);

    if (diff.inMinutes < 1) {
      return '刚刚';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}分钟前';
    } else if (diff.inDays < 1) {
      return '${diff.inHours}小时前';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}天前';
    } else {
      return DateFormat('MM-dd').format(dateTime);
    }
  }
}
