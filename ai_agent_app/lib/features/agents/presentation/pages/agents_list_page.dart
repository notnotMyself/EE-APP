import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../controllers/agent_controller.dart';
import '../../domain/models/agent.dart';
import '../theme/agent_profile_theme.dart';
import 'agent_profile_page.dart';

class AgentsListPage extends ConsumerWidget {
  const AgentsListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final agentsAsync = ref.watch(activeAgentsProvider);

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
            expandedHeight: 130,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                padding: const EdgeInsets.fromLTRB(20, 56, 20, 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    Text(
                      'AI员工市场',
                      style: GoogleFonts.poppins(
                        fontSize: 26,
                        fontWeight: FontWeight.w700,
                        color: AgentProfileTheme.titleColor,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '订阅你需要的AI助手',
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
          agentsAsync.when(
            data: (agents) {
              if (agents.isEmpty) {
                return SliverFillRemaining(
                  child: _buildEmptyState(),
                );
              }

              return SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final agent = agents[index];
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: _AgentCard(agent: agent),
                      );
                    },
                    childCount: agents.length,
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
              child: _buildErrorState(context, ref, error),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
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
            child: Icon(
              Icons.psychology_outlined,
              size: 48,
              color: AgentProfileTheme.labelColor,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            '暂无可用的AI员工',
            style: GoogleFonts.poppins(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AgentProfileTheme.titleColor,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '敬请期待更多AI助手上线',
            style: GoogleFonts.poppins(
              fontSize: 14,
              color: AgentProfileTheme.labelColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, WidgetRef ref, Object error) {
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
              onPressed: () => ref.invalidate(activeAgentsProvider),
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
        label: Text(label),
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
}

class _AgentCard extends ConsumerWidget {
  const _AgentCard({required this.agent});

  final Agent agent;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isSubscribedAsync = ref.watch(isAgentSubscribedProvider(agent.id));

    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => AgentProfilePage(agent: agent),
          ),
        );
      },
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AgentProfileTheme.cardBackground,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: Colors.white, width: 1),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 16,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Row
            Row(
              children: [
                // Avatar
                _buildAvatar(),
                const SizedBox(width: 16),

                // Name and Role
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        agent.name,
                        style: GoogleFonts.poppins(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: AgentProfileTheme.titleColor,
                        ),
                      ),
                    ],
                  ),
                ),

                // Subscribe Button
                isSubscribedAsync.when(
                  data: (isSubscribed) => _buildSubscribeButton(
                    context,
                    ref,
                    isSubscribed,
                  ),
                  loading: () => const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: AgentProfileTheme.accentBlue,
                    ),
                  ),
                  error: (_, __) => const Icon(
                    Icons.error_outline,
                    color: Color(0xFFEF4444),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Description
            Text(
              agent.description,
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: AgentProfileTheme.labelColor,
                height: 1.5,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),

            const SizedBox(height: 16),

            // Action Button
            Container(
              width: double.infinity,
              height: 48,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AgentProfileTheme.accentBlue,
                    AgentProfileTheme.accentBlue.withOpacity(0.85),
                  ],
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (context) => AgentProfilePage(agent: agent),
                    ),
                  );
                },
                icon: const Icon(Icons.chat_bubble_outline_rounded, size: 18),
                label: Text(
                  '开始对话',
                  style: GoogleFonts.poppins(
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  foregroundColor: Colors.white,
                  shadowColor: Colors.transparent,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    // 根据 Agent role 映射到对应的头像
    String? roleAvatar;
    bool useTextFallback = false;
    String? fallbackText;

    switch (agent.role) {
      case 'design_validator':
        roleAvatar = AgentProfileTheme.chrisChenAvatar;
        break;
      case 'ai_news_crawler':
        roleAvatar = 'assets/images/secretary-girl-avatar.png'; // 码码
        break;
      case 'dev_efficiency_analyst':
        // 研发效能分析官使用商商头像
        roleAvatar = 'assets/images/secretary-woman-avatar.png';
        break;
      case 'ee_developer':
        // EE研发员工使用"EE"文字头像
        useTextFallback = true;
        fallbackText = 'EE';
        break;
      case 'general':
        // 小知使用小智头像
        roleAvatar = 'assets/images/secretary-boy-avatar.png';
        break;
    }

    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AgentProfileTheme.avatarPlaceholder,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: useTextFallback
          ? _buildAvatarFallback(customText: fallbackText)
          : roleAvatar != null
              ? Image.asset(
                  roleAvatar,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _buildAvatarFallback(),
                )
              : agent.avatarUrl != null
                  ? Image.network(
                      agent.avatarUrl!,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => _buildAvatarFallback(),
                    )
                  : _buildAvatarFallback(),
    );
  }

  Widget _buildAvatarFallback({String? customText}) {
    final displayText = customText ??
        (agent.name.isNotEmpty ? agent.name[0].toUpperCase() : '?');

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
          displayText,
          style: GoogleFonts.poppins(
            fontSize: 22,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
      ),
    );
  }

  Widget _buildSubscribeButton(
    BuildContext context,
    WidgetRef ref,
    bool isSubscribed,
  ) {
    return GestureDetector(
      onTap: () async {
        if (isSubscribed) {
          await ref.read(agentControllerProvider.notifier).unsubscribe(agent.id);
        } else {
          await ref.read(agentControllerProvider.notifier).subscribe(agent.id);
        }

        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                isSubscribed ? '已取消订阅' : '订阅成功',
                style: GoogleFonts.poppins(),
              ),
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              duration: const Duration(seconds: 2),
            ),
          );
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isSubscribed
              ? AgentProfileTheme.accentBlue.withOpacity(0.1)
              : AgentProfileTheme.accentBlue,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          isSubscribed ? '已订阅' : '订阅',
          style: GoogleFonts.poppins(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: isSubscribed
                ? AgentProfileTheme.accentBlue
                : Colors.white,
          ),
        ),
      ),
    );
  }
}
