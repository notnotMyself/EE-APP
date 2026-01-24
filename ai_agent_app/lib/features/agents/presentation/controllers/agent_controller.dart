import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/agent_repository.dart';
import '../../domain/models/agent.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';

/// Agent Repository Provider
final agentRepositoryProvider = Provider<AgentRepository>((ref) {
  return AgentRepository();
});

/// 所有活跃AI员工列表Provider（带可见性过滤 + 小知）
final activeAgentsProvider = FutureProvider<List<Agent>>((ref) async {
  final repository = ref.watch(agentRepositoryProvider);
  final agents = await repository.getActiveAgents();

  // 获取当前用户
  final currentUser = ref.watch(currentUserProvider);
  final userEmail = currentUser?.email;

  // 特殊可见性规则：EE 研发员工只对特定用户可见
  const restrictedEmail = '1091201603@qq.com';

  final filteredAgents = agents.where((agent) {
    // dev_efficiency_analyst 只对特定用户可见
    if (agent.role == 'dev_efficiency_analyst') {
      return userEmail == restrictedEmail;
    }
    return true;
  }).toList();

  // 添加虚拟的"小知"Agent（通用AI助手）
  final generalAgent = Agent(
    id: 'general-ai-agent', // 固定ID用于订阅识别
    name: '小知',
    description: '你的智能助手，可以回答各种问题',
    role: 'general',
    avatarUrl: null, // 使用前端资源
    isActive: true,
    createdAt: DateTime.now(),
  );

  // 将小知放在列表最前面
  return [generalAgent, ...filteredAgents];
});

/// 用户订阅的AI员工Provider（小知默认订阅）
final userSubscriptionsProvider =
    FutureProvider<List<UserAgentSubscription>>((ref) async {
  final currentUser = ref.watch(currentUserProvider);
  if (currentUser == null) {
    return [];
  }

  final repository = ref.watch(agentRepositoryProvider);
  final subscriptions = await repository.getUserSubscriptions(currentUser.id);

  // 自动添加"小知"的订阅（虚拟订阅，不存储到后端）
  final generalSubscription = UserAgentSubscription(
    userId: currentUser.id,
    agentId: 'general-ai-agent',
    subscribedAt: DateTime.now(),
    agent: Agent(
      id: 'general-ai-agent',
      name: '小知',
      description: '你的智能助手，可以回答各种问题',
      role: 'general',
      avatarUrl: null,
      isActive: true,
      createdAt: DateTime.now(),
    ),
  );

  return [generalSubscription, ...subscriptions];
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
    // 防止取消订阅小知
    if (agentId == 'general-ai-agent') {
      state = AsyncValue.error('小知是默认助手，无法取消订阅', StackTrace.current);
      return;
    }

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
