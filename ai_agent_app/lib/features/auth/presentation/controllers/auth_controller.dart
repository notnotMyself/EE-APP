import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../data/legal_repository.dart';
import '../../domain/models/consent_status.dart';

/// Auth状态Provider
final authStateProvider = StreamProvider<AuthState>((ref) {
  return Supabase.instance.client.auth.onAuthStateChange;
});

/// 当前用户Provider
final currentUserProvider = Provider<User?>((ref) {
  final authState = ref.watch(authStateProvider);
  return authState.value?.session?.user;
});

/// Auth Controller
class AuthController extends StateNotifier<AsyncValue<void>> {
  AuthController(this._legalRepository) : super(const AsyncValue.data(null));

  final _supabase = Supabase.instance.client;
  final LegalRepository _legalRepository;

  /// 注册
  Future<void> signUp({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final response = await _supabase.auth.signUp(
        email: email,
        password: password,
      );

      if (response.user == null) {
        throw Exception('注册失败，请重试');
      }
    });
  }

  /// 登录
  Future<void> signIn({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await _supabase.auth.signInWithPassword(
        email: email,
        password: password,
      );
    });
  }

  /// 登出
  Future<void> signOut() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await _supabase.auth.signOut();
    });
  }

  /// 重置密码
  Future<void> resetPassword(String email) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await _supabase.auth.resetPasswordForEmail(email);
    });
  }

  /// 检查用户同意状态
  ///
  /// 返回是否需要跳转到服务条款页面
  /// 如果返回true，表示用户需要同意服务条款
  Future<bool> checkAndNavigateToTermsIfNeeded() async {
    try {
      // 检查用户是否已登录
      if (_supabase.auth.currentUser == null) {
        return false;
      }

      // 检查用户同意状态
      final consentStatus = await _legalRepository.checkConsentStatus();

      // 返回是否需要同意
      return consentStatus.needsConsent;
    } catch (e) {
      // 如果检查失败，保守起见要求用户同意
      // 在生产环境中，可以根据具体错误类型决定是否要求同意
      return true;
    }
  }

  /// 获取用户同意状态详情
  ///
  /// 返回详细的同意状态信息，包括各个文档的同意情况
  Future<ConsentStatus> getConsentStatus() async {
    return await _legalRepository.checkConsentStatus();
  }
}

/// Auth Controller Provider
final authControllerProvider =
    StateNotifierProvider<AuthController, AsyncValue<void>>((ref) {
  final legalRepository = LegalRepository();
  return AuthController(legalRepository);
});
