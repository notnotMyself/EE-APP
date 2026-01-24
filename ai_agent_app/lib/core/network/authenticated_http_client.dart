import 'package:supabase_flutter/supabase_flutter.dart';

/// 认证HTTP客户端工具类
/// 提供统一的认证Header获取方法
class AuthenticatedHttpClient {
  /// 获取认证Header
  /// 包含Bearer Token和Content-Type
  static Future<Map<String, String>> getAuthHeaders() async {
    try {
      // 尝试刷新 session（如果需要）
      final session = await Supabase.instance.client.auth.refreshSession();
      final token = session.session?.accessToken;

      if (token == null) {
        // 如果刷新失败，清除本地 session
        await _clearInvalidSession();
        throw Exception('用户未登录，无法获取认证Token');
      }

      return {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };
    } catch (e) {
      // 捕获 refresh token 错误
      if (e.toString().contains('refresh_token_not_found') ||
          e.toString().contains('Invalid Refresh Token')) {
        await _clearInvalidSession();
        throw Exception('登录已过期，请重新登录');
      }

      // 其他错误也尝试获取当前 token
      final token = Supabase.instance.client.auth.currentSession?.accessToken;
      if (token == null) {
        await _clearInvalidSession();
        throw Exception('用户未登录，无法获取认证Token');
      }

      return {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };
    }
  }

  /// 获取仅包含Token的Header（用于流式请求）
  static Future<Map<String, String>> getAuthHeadersOnly() async {
    try {
      final session = await Supabase.instance.client.auth.refreshSession();
      final token = session.session?.accessToken;

      if (token == null) {
        await _clearInvalidSession();
        throw Exception('用户未登录，无法获取认证Token');
      }

      return {
        'Authorization': 'Bearer $token',
      };
    } catch (e) {
      if (e.toString().contains('refresh_token_not_found') ||
          e.toString().contains('Invalid Refresh Token')) {
        await _clearInvalidSession();
        throw Exception('登录已过期，请重新登录');
      }

      final token = Supabase.instance.client.auth.currentSession?.accessToken;
      if (token == null) {
        await _clearInvalidSession();
        throw Exception('用户未登录，无法获取认证Token');
      }

      return {
        'Authorization': 'Bearer $token',
      };
    }
  }

  /// 检查用户是否已登录
  static bool isAuthenticated() {
    return Supabase.instance.client.auth.currentSession != null;
  }

  /// 获取当前用户ID
  static String? getCurrentUserId() {
    return Supabase.instance.client.auth.currentUser?.id;
  }

  /// 清除无效的 Session
  static Future<void> _clearInvalidSession() async {
    try {
      // 使用 local scope 只清除本地 session，不通知服务器
      await Supabase.instance.client.auth.signOut(scope: SignOutScope.local);
    } catch (e) {
      // 忽略登出错误
      print('Clear session error: $e');
    }
  }
}
