import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/agent_repository.dart';
import '../../domain/models/agent.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';

/// Agent Repository Provider
final agentRepositoryProvider = Provider<AgentRepository>((ref) {
  return AgentRepository();
});

/// 所有活跃AI员工列表Provider
final activeAgentsProvider = FutureProvider<List<Agent>>((ref) async {
  final repository = ref.watch(agentRepositoryProvider);
  return repository.getActiveAgents();
});

/// 用户订阅的AI员工Provider
final userSubscriptionsProvider =
    FutureProvider<List<UserAgentSubscription>>((ref) async {
  final currentUser = ref.watch(currentUserProvider);
  if (currentUser == null) {
    return [];
  }

  final repository = ref.watch(agentRepositoryProvider);
  return repository.getUserSubscriptions(currentUser.id);
});

/// Agent Controller for subscription actions
class AgentController extends StateNotifier<AsyncValue<void>> {
  AgentController(this.ref) : super(const AsyncValue.data(null));

  final Ref ref;

  /// 订阅AI员工
  Future<void> subscribe(String agentId) async {
    final currentUser = ref.read(currentUserProvider);
    if (currentUser == null) {
      state = AsyncValue.error('请先登录', StackTrace.current);
      return;
    }

    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repository = ref.read(agentRepositoryProvider);
      await repository.subscribeToAgent(
        userId: currentUser.id,
        agentId: agentId,
      );

      // 刷新订阅列表
      ref.invalidate(userSubscriptionsProvider);
    });
  }

  /// 取消订阅AI员工
  Future<void> unsubscribe(String agentId) async {
    final currentUser = ref.read(currentUserProvider);
    if (currentUser == null) {
      state = AsyncValue.error('请先登录', StackTrace.current);
      return;
    }

    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repository = ref.read(agentRepositoryProvider);
      await repository.unsubscribeFromAgent(
        userId: currentUser.id,
        agentId: agentId,
      );

      // 刷新订阅列表
      ref.invalidate(userSubscriptionsProvider);
    });
  }

  /// 检查是否已订阅
  Future<bool> isSubscribed(String agentId) async {
    final currentUser = ref.read(currentUserProvider);
    if (currentUser == null) {
      return false;
    }

    final repository = ref.read(agentRepositoryProvider);
    return repository.isUserSubscribed(
      userId: currentUser.id,
      agentId: agentId,
    );
  }
}

/// Agent Controller Provider
final agentControllerProvider =
    StateNotifierProvider<AgentController, AsyncValue<void>>((ref) {
  return AgentController(ref);
});

/// 检查特定agent是否已订阅的Provider
final isAgentSubscribedProvider =
    FutureProvider.family<bool, String>((ref, agentId) async {
  final subscriptions = await ref.watch(userSubscriptionsProvider.future);
  return subscriptions.any((sub) => sub.agentId == agentId);
});

/// Agent.role → Agent.id (UUID) 映射
/// 用于根据 Agent 的 role 字段查找对应的 UUID
final agentRoleToIdProvider = FutureProvider<Map<String, String>>((ref) async {
  final agents = await ref.watch(activeAgentsProvider.future);
  return {
    for (var agent in agents)
      agent.role: agent.id,
  };
});

/// 检查用户是否订阅了指定 role 的 Agent
/// 通过 role → UUID → 订阅状态 的映射链查询
final isAgentRoleSubscribedProvider =
    FutureProvider.family<bool, String?>((ref, agentRole) async {
  if (agentRole == null) return false;

  // 1. 获取 role → UUID 映射
  final roleToIdMap = await ref.watch(agentRoleToIdProvider.future);
  final agentId = roleToIdMap[agentRole];

  if (agentId == null) return false;

  // 2. 检查是否订阅该 UUID
  return ref.watch(isAgentSubscribedProvider(agentId).future);
});
