import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/briefing.dart';
import '../../domain/models/secretary.dart';
import '../controllers/briefing_controller.dart';
import '../controllers/home_provider.dart';
import '../widgets/briefing_card_stack.dart';
import '../widgets/briefing_card.dart';
import '../widgets/view_toggle.dart';
import '../widgets/role_dial.dart';
import '../widgets/avatar_display.dart';
import 'briefing_detail_page.dart';

/// 信息流首页 - 新版 UI
class FeedHomePage extends ConsumerWidget {
  const FeedHomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final briefingsAsync = ref.watch(briefingsProvider);
    final cachedBriefings = briefingsAsync.valueOrNull?.items;
    final viewMode = ref.watch(homeViewModeProvider);
    final activeAgentData = ref.watch(activeAgentSecretaryProvider);
    final activeSecretaryIndex = ref.watch(activeSecretaryIndexProvider);
    final visibleAgentsAsync = ref.watch(visibleAgentSecretariesProvider);
    final cachedVisibleAgents = visibleAgentsAsync.valueOrNull;

    return Scaffold(
      extendBodyBehindAppBar: true,
      resizeToAvoidBottomInset: false,
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFFE0EAFC), // Light Blue Gray
              Color(0xFFCFDEF3),
            ],
          ),
        ),
        child: SafeArea(
          bottom: false,
          child: visibleAgentsAsync.when(
            data: (visibleAgents) => _buildContentFromAgents(
              context,
              ref,
              visibleAgents,
              briefingsAsync,
              cachedBriefings,
              viewMode,
              activeAgentData,
              activeSecretaryIndex,
            ),
            loading: () {
              if (cachedVisibleAgents != null) {
                return _buildContentFromAgents(
                  context,
                  ref,
                  cachedVisibleAgents,
                  briefingsAsync,
                  cachedBriefings,
                  viewMode,
                  activeAgentData,
                  activeSecretaryIndex,
                );
              }
              return const Center(child: CircularProgressIndicator());
            },
            error: (error, stack) => _buildErrorState(context, ref, error),
            skipLoadingOnRefresh: true,
            skipLoadingOnReload: true,
          ),
        ),
      ),
    );
  }

  Widget _buildContentFromAgents(
    BuildContext context,
    WidgetRef ref,
    List<Map<String, dynamic>> visibleAgents,
    AsyncValue<BriefingListResponse> briefingsAsync,
    List<Briefing>? cachedBriefings,
    ViewMode viewMode,
    Map<String, dynamic>? activeAgentData,
    int activeSecretaryIndex,
  ) {
    if (visibleAgents.isEmpty) {
      return _buildEmptyState(context);
    }

    return briefingsAsync.when(
      data: (response) => _buildContent(
        context,
        ref,
        response.items,
        viewMode,
        activeAgentData ?? visibleAgents.first,
        activeSecretaryIndex,
        visibleAgents,
      ),
      loading: () {
        if (cachedBriefings != null) {
          return _buildContent(
            context,
            ref,
            cachedBriefings,
            viewMode,
            activeAgentData ?? visibleAgents.first,
            activeSecretaryIndex,
            visibleAgents,
          );
        }
        return const Center(child: CircularProgressIndicator());
      },
      error: (error, stack) => _buildErrorState(context, ref, error),
      skipLoadingOnRefresh: true,
      skipLoadingOnReload: true,
    );
  }

  Widget _buildContent(
    BuildContext context,
    WidgetRef ref,
    List<Briefing> allBriefings,
    ViewMode viewMode,
    Map<String, dynamic> activeAgentData,
    int activeSecretaryIndex,
    List<Map<String, dynamic>> visibleAgents,
  ) {
    // 使用 activeAgentIdProvider 获取当前 Agent UUID
    final agentId = ref.watch(activeAgentIdProvider);
    final agentKey = agentId ?? 'all';
    final dismissedIds = ref.watch(dismissedBriefingIdsProvider(agentKey));

    // 提取显示数据
    final displayName = activeAgentData['name'] as String;
    final secretary = activeAgentData['secretary'] as Secretary;

    // 修复 Bug：使用 UUID 而非 secretary.id 过滤
    final briefings = agentId == null
        ? allBriefings  // general: 显示所有简报
        : allBriefings.where((b) => b.agentId == agentId).toList();

    return Stack(
      children: [
        Column(
          children: [
            // Custom Header
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 10, 20, 10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          _getGreeting(),
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.black87,
                              ),
                        ),
                        Text(
                          '$displayName has ${briefings.length} updates',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.black54,
                                fontWeight: FontWeight.w500,
                              ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Row(
                    children: [
                      // Refresh button
                      IconButton(
                        icon: const Icon(Icons.refresh, color: Colors.black54),
                        onPressed: () {
                          ref.invalidate(briefingsProvider);
                          ref.invalidate(briefingUnreadCountProvider);
                        },
                      ),
                      ViewToggle(
                        mode: viewMode,
                        onToggle: (mode) =>
                            ref.read(homeViewModeProvider.notifier).state = mode,
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Avatar and Role Dial Row (only in cards mode)
            AnimatedOpacity(
              opacity: viewMode == ViewMode.cards ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 300),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                height: viewMode == ViewMode.cards ? 140 : 0,
                child: viewMode == ViewMode.cards
                    ? Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            // Avatar (Left) - 使用 Secretary 提供视觉主题
                            AvatarDisplay(secretary: secretary),

                            const Spacer(),

                            // Role Dial (Right) - 传入动态列表
                            RoleDial(
                              visibleAgents: visibleAgents,
                              activeIndex: activeSecretaryIndex,
                              onSelect: (index) => ref
                                  .read(activeSecretaryIndexProvider.notifier)
                                  .state = index,
                            ),
                          ],
                        ),
                      )
                    : null,
              ),
            ),

            // Content Area
            Expanded(
              child: viewMode == ViewMode.cards
                  ? _buildCardsView(
                      context,
                      ref,
                      briefings,
                      agentKey,
                      dismissedIds,
                    )
                  : _buildGridView(context, ref, briefings),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCardsView(
    BuildContext context,
    WidgetRef ref,
    List<Briefing> briefings,
    String agentKey,
    Set<String> dismissedIds,
  ) {
    if (briefings.isEmpty) {
      return _buildEmptyState(context);
    }

    return Padding(
      padding: const EdgeInsets.only(top: 20),
      child: BriefingCardStack(
        // 使用 agentId 作为 key，确保切换 agent 时重置状态，但数据刷新时保持状态
        key: ValueKey('card-stack-$agentKey'),
        briefings: briefings,
        dismissedIds: dismissedIds,
        onCardDismissed: (briefing) {
          // Mark as read when dismissed
          ref.read(dismissedBriefingIdsProvider(agentKey).notifier).add(briefing.id);
          ref
              .read(briefingControllerProvider.notifier)
              .markAsRead(
                briefing.id,
                refreshList: false,
                refreshUnread: false,
              );
        },
        onCardAction: (briefing) {
          _onBriefingTap(context, ref, briefing);
        },
      ),
    );
  }

  Widget _buildGridView(
    BuildContext context,
    WidgetRef ref,
    List<Briefing> briefings,
  ) {
    if (briefings.isEmpty) {
      return _buildEmptyState(context);
    }

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(briefingsProvider);
        ref.invalidate(briefingUnreadCountProvider);
      },
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(0, 16, 0, 16),
        itemCount: briefings.length,
        itemBuilder: (context, index) {
          return BriefingCard(
            briefing: briefings[index],
            onTap: () => _onBriefingTap(context, ref, briefings[index]),
          );
        },
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.check_circle_outline,
            size: 60,
            color: Colors.black26,
          ),
          const SizedBox(height: 16),
          Text(
            'No updates yet',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.black54,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Your AI employees will notify you\nwhen something important happens',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.black38,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, WidgetRef ref, Object error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 60, color: Colors.red[300]),
          const SizedBox(height: 16),
          Text(
            'Failed to load',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Text(
            '$error',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.black54,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              ref.invalidate(briefingsProvider);
              ref.invalidate(briefingUnreadCountProvider);
            },
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  void _onBriefingTap(
    BuildContext context,
    WidgetRef ref,
    Briefing briefing,
  ) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => BriefingDetailPage(briefing: briefing),
      ),
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return 'Good Morning';
    } else if (hour < 17) {
      return 'Good Afternoon';
    } else {
      return 'Good Evening';
    }
  }
}
