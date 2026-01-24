import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/secretaries_data.dart';
import '../../../agents/presentation/controllers/agent_controller.dart';
import '../../../agents/domain/models/agent.dart';

enum ViewMode { cards, grid }

final homeViewModeProvider = StateProvider<ViewMode>((ref) => ViewMode.cards);

/// 用户订阅的 Agent 作为首页人物（带视觉主题）
/// 返回格式：List<(Secretary主题, Agent数据)>
final visibleAgentSecretariesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final subscriptions = await ref.watch(userSubscriptionsProvider.future);

  final visibleList = <Map<String, dynamic>>[];

  // 特殊处理：添加"全部"（通用）入口
  visibleList.add({
    'type': 'general',
    'secretary': secretariesData.firstWhere((s) => s.id == 'general'),
    'agent': null,
    'name': '小知',  // 通用AI的名字
    'description': '查看所有 AI 员工的简报',
  });

  // 遍历用户订阅的 Agent
  for (final subscription in subscriptions) {
    final agent = subscription.agent;
    if (agent == null) continue;

    // 根据 Agent.role 查找对应的视觉主题（Secretary）
    final secretary = secretariesData.firstWhere(
      (s) => s.mappedAgentRole == agent.role,
      orElse: () => secretariesData.first, // 默认使用第一个主题
    );

    visibleList.add({
      'type': 'agent',
      'secretary': secretary,
      'agent': agent,
      'name': agent.name,  // 使用 Agent 的真实名称
      'description': agent.description,
    });
  }

  return visibleList;
});

/// 当前激活的索引
final activeSecretaryIndexProvider = StateProvider<int>((ref) => 0);

/// 当前激活的人物数据
final activeAgentSecretaryProvider = Provider<Map<String, dynamic>?>((ref) {
  final visibleListAsync = ref.watch(visibleAgentSecretariesProvider);

  return visibleListAsync.when(
    data: (visibleList) {
      if (visibleList.isEmpty) return null;

      final index = ref.watch(activeSecretaryIndexProvider);

      // 索引越界保护
      if (index >= visibleList.length) {
        Future.microtask(() {
          ref.read(activeSecretaryIndexProvider.notifier).state = 0;
        });
        return visibleList.first;
      }

      return visibleList[index];
    },
    loading: () => null,
    error: (_, __) => null,
  );
});

/// 获取当前选中人物对应的 Agent UUID（用于简报过滤）
final activeAgentIdProvider = Provider<String?>((ref) {
  final activeData = ref.watch(activeAgentSecretaryProvider);

  if (activeData == null) return null;

  final type = activeData['type'] as String;
  if (type == 'general') {
    return null; // null 表示显示所有简报
  }

  final agent = activeData['agent'] as Agent?;
  return agent?.id;
});

/// 首页卡片已滑走的简报 ID（按选中角色隔离）
class DismissedBriefingIds extends StateNotifier<Set<String>> {
  DismissedBriefingIds() : super(const {});

  void add(String briefingId) {
    if (state.contains(briefingId)) return;
    state = {...state, briefingId};
  }

  void reset() {
    state = const {};
  }
}

final dismissedBriefingIdsProvider =
    StateNotifierProvider.family<DismissedBriefingIds, Set<String>, String>(
  (ref, key) => DismissedBriefingIds(),
);
