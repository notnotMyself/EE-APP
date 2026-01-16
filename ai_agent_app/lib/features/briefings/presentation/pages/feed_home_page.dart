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
import '../widgets/bottom_chat_bar.dart';
import '../../data/secretaries_data.dart';
import 'briefing_detail_page.dart';

/// 信息流首页 - 新版 UI
class FeedHomePage extends ConsumerWidget {
  const FeedHomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final briefingsAsync = ref.watch(briefingsProvider);
    final viewMode = ref.watch(homeViewModeProvider);
    final activeSecretary = ref.watch(activeSecretaryProvider);
    final activeSecretaryIndex = ref.watch(activeSecretaryIndexProvider);

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
          child: briefingsAsync.when(
            data: (response) => _buildContent(
              context,
              ref,
              response.items,
              viewMode,
              activeSecretary,
              activeSecretaryIndex,
            ),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stack) => _buildErrorState(context, ref, error),
          ),
        ),
      ),
    );
  }

  Widget _buildContent(
    BuildContext context,
    WidgetRef ref,
    List<Briefing> allBriefings,
    ViewMode viewMode,
    Secretary activeSecretary,
    int activeSecretaryIndex,
  ) {
    // Filter briefings based on active secretary
    final briefings = activeSecretary.id == 'general'
        ? allBriefings
        : allBriefings.where((b) => b.agentId == activeSecretary.id).toList();

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
                          '${activeSecretary.name} has ${briefings.length} updates',
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
                            // Avatar (Left)
                            AvatarDisplay(secretary: activeSecretary),

                            const Spacer(),

                            // Role Dial (Right)
                            RoleDial(
                              secretaries: secretariesData,
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
                  ? _buildCardsView(context, ref, briefings)
                  : _buildGridView(context, ref, briefings),
            ),
          ],
        ),

        // Bottom Chat Bar - positioned above bottom navigation bar
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: BottomChatBar(
            onSend: (message) {
              _onChatSend(context, ref, message, activeSecretary);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildCardsView(
    BuildContext context,
    WidgetRef ref,
    List<Briefing> briefings,
  ) {
    if (briefings.isEmpty) {
      return _buildEmptyState(context);
    }

    return Padding(
      padding: const EdgeInsets.only(top: 20),
      child: BriefingCardStack(
        briefings: briefings,
        onCardDismissed: (briefing) {
          // Mark as read when dismissed
          ref.read(briefingControllerProvider.notifier).markAsRead(briefing.id);
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
        padding: const EdgeInsets.fromLTRB(0, 16, 0, 100),
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

  void _onChatSend(
    BuildContext context,
    WidgetRef ref,
    String message,
    Secretary secretary,
  ) {
    // Navigate to conversations page with a new conversation
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('${secretary.name} is processing: "$message"'),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.only(bottom: 100, left: 20, right: 20),
      ),
    );
    // TODO: Create new conversation and navigate to chat
    // context.go('/conversations/new?agent=${secretary.id}&message=$message');
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
