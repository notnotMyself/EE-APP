import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/briefing_repository.dart';
import '../../domain/models/briefing.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';
import '../../../../core/network/authenticated_http_client.dart';

/// Briefing Repository Provider
final briefingRepositoryProvider = Provider<BriefingRepository>((ref) {
  return BriefingRepository();
});

/// 简报列表 Provider - 带认证检查
final briefingsProvider = FutureProvider<BriefingListResponse>((ref) async {
  // 检查认证状态
  if (!AuthenticatedHttpClient.isAuthenticated()) {
    throw Exception('用户未登录');
  }

  final repository = ref.watch(briefingRepositoryProvider);
  try {
    return await repository.getBriefings();
  } catch (e) {
    // 如果是认证错误，清除所有缓存
    if (e.toString().contains('401') || e.toString().contains('未登录')) {
      ref.invalidate(authStateProvider);
    }
    rethrow;
  }
});

/// 未读简报数量 Provider - 带认证检查
final briefingUnreadCountProvider = FutureProvider<BriefingUnreadCount>((ref) async {
  // 检查认证状态
  if (!AuthenticatedHttpClient.isAuthenticated()) {
    // 返回空数据而不是抛出异常（避免阻塞 UI）
    return const BriefingUnreadCount(count: 0);
  }

  final repository = ref.watch(briefingRepositoryProvider);
  try {
    return await repository.getUnreadCount();
  } catch (e) {
    // 静默失败，返回默认值
    return const BriefingUnreadCount(count: 0);
  }
});

/// 单个简报详情 Provider
final briefingDetailProvider =
    FutureProvider.family<Briefing, String>((ref, briefingId) async {
  final repository = ref.watch(briefingRepositoryProvider);
  return repository.getBriefing(briefingId);
});

/// Briefing Controller
class BriefingController extends StateNotifier<AsyncValue<void>> {
  BriefingController(this.ref) : super(const AsyncValue.data(null));

  final Ref ref;

  /// 标记简报为已读
  Future<void> markAsRead(
    String briefingId, {
    bool refreshList = true,
    bool refreshUnread = true,
  }) async {
    try {
      final repository = ref.read(briefingRepositoryProvider);
      await repository.markAsRead(briefingId);

      // 刷新简报列表和未读数量
      if (refreshList) {
        ref.invalidate(briefingsProvider);
      }
      if (refreshUnread) {
        ref.invalidate(briefingUnreadCountProvider);
      }
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  /// 从简报开始对话
  Future<String?> startConversation(String briefingId, {String? prompt}) async {
    state = const AsyncValue.loading();
    try {
      final repository = ref.read(briefingRepositoryProvider);
      final response = await repository.startConversation(briefingId, prompt: prompt);

      state = const AsyncValue.data(null);

      // 刷新简报列表
      ref.invalidate(briefingsProvider);
      ref.invalidate(briefingUnreadCountProvider);

      return response.conversationId;
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      return null;
    }
  }

  /// 忽略简报
  Future<void> dismissBriefing(String briefingId) async {
    try {
      final repository = ref.read(briefingRepositoryProvider);
      await repository.dismissBriefing(briefingId);

      // 刷新简报列表
      ref.invalidate(briefingsProvider);
      ref.invalidate(briefingUnreadCountProvider);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  /// 刷新简报列表
  Future<void> refresh() async {
    ref.invalidate(briefingsProvider);
    ref.invalidate(briefingUnreadCountProvider);
  }
}

/// Briefing Controller Provider
final briefingControllerProvider =
    StateNotifierProvider<BriefingController, AsyncValue<void>>((ref) {
  return BriefingController(ref);
});
