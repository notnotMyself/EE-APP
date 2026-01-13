import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/briefing_repository.dart';
import '../../domain/models/briefing.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';

/// Briefing Repository Provider
final briefingRepositoryProvider = Provider<BriefingRepository>((ref) {
  return BriefingRepository();
});

/// 简报列表 Provider
final briefingsProvider = FutureProvider<BriefingListResponse>((ref) async {
  final repository = ref.watch(briefingRepositoryProvider);
  return repository.getBriefings();
});

/// 未读简报数量 Provider
final briefingUnreadCountProvider = FutureProvider<BriefingUnreadCount>((ref) async {
  final repository = ref.watch(briefingRepositoryProvider);
  return repository.getUnreadCount();
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
  Future<void> markAsRead(String briefingId) async {
    try {
      final repository = ref.read(briefingRepositoryProvider);
      await repository.markAsRead(briefingId);

      // 刷新简报列表和未读数量
      ref.invalidate(briefingsProvider);
      ref.invalidate(briefingUnreadCountProvider);
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
