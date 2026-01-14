import 'package:supabase_flutter/supabase_flutter.dart';

/// 认证HTTP客户端工具类
/// 提供统一的认证Header获取方法
class AuthenticatedHttpClient {
  /// 获取认证Header
  /// 包含Bearer Token和Content-Type
  static Future<Map<String, String>> getAuthHeaders() async {
    final token = Supabase.instance.client.auth.currentSession?.accessToken;

    if (token == null) {
      throw Exception('用户未登录，无法获取认证Token');
    }

    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  /// 获取仅包含Token的Header（用于流式请求）
  static Future<Map<String, String>> getAuthHeadersOnly() async {
    final token = Supabase.instance.client.auth.currentSession?.accessToken;

    if (token == null) {
      throw Exception('用户未登录，无法获取认证Token');
    }

    return {
      'Authorization': 'Bearer $token',
    };
  }

  /// 检查用户是否已登录
  static bool isAuthenticated() {
    return Supabase.instance.client.auth.currentSession != null;
  }

  /// 获取当前用户ID
  static String? getCurrentUserId() {
    return Supabase.instance.client.auth.currentUser?.id;
  }
}
