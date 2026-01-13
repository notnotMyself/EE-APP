import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../controllers/briefing_controller.dart';
import '../widgets/briefing_card.dart';
import '../../domain/models/briefing.dart';
import 'briefing_detail_page.dart';

/// 信息流页面 - 显示AI员工的简报
class BriefingsFeedPage extends ConsumerWidget {
  const BriefingsFeedPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final briefingsAsync = ref.watch(briefingsProvider);
    final unreadCountAsync = ref.watch(briefingUnreadCountProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('信息流'),
        actions: [
          // 未读数量 Badge
          unreadCountAsync.when(
            data: (unreadCount) {
              if (unreadCount.count > 0) {
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: Badge(
                    label: Text('${unreadCount.count}'),
                    child: IconButton(
                      icon: const Icon(Icons.notifications_outlined),
                      onPressed: () {},
                    ),
                  ),
                );
              }
              return const SizedBox.shrink();
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(briefingsProvider);
              ref.invalidate(briefingUnreadCountProvider);
            },
          ),
        ],
      ),
      body: briefingsAsync.when(
        data: (response) {
          if (response.items.isEmpty) {
            return _buildEmptyState(context);
          }

          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(briefingsProvider);
              ref.invalidate(briefingUnreadCountProvider);
            },
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: response.items.length,
              itemBuilder: (context, index) {
                final briefing = response.items[index];
                return BriefingCard(
                  briefing: briefing,
                  onTap: () => _onBriefingTap(context, ref, briefing),
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => _buildErrorState(context, ref, error),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.inbox_rounded,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            '暂无简报',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.grey[600],
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'AI员工会在发现重要信息时主动通知你',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[500],
                ),
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
    // 跳转到全屏详情页
    // 标记已读的逻辑在详情页中处理
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => BriefingDetailPage(briefing: briefing),
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
          Text('加载失败: $error'),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              ref.invalidate(briefingsProvider);
              ref.invalidate(briefingUnreadCountProvider);
            },
            child: const Text('重试'),
          ),
        ],
      ),
    );
  }
}
