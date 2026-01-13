import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

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
  AuthController() : super(const AsyncValue.data(null));

  final _supabase = Supabase.instance.client;

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
}

/// Auth Controller Provider
final authControllerProvider =
    StateNotifierProvider<AuthController, AsyncValue<void>>((ref) {
  return AuthController();
});
