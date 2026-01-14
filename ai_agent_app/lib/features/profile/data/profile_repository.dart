import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/authenticated_http_client.dart';
import '../domain/models/usage_stats.dart';
import '../../agents/domain/models/agent.dart';

class ProfileRepository {
  final _supabase = Supabase.instance.client;
  final _dio = Dio();

  /// 获取使用统计
  /// user_id现在从JWT token中自动获取，无需手动传递
  Future<UsageStats> getUsageStats() async {
    try {
      final authHeaders = await AuthenticatedHttpClient.getAuthHeaders();

      final response = await _dio.get(
        '${AppConfig.apiUrl}/profile/usage-stats',  // 移除user_id参数
        options: Options(headers: authHeaders),
      );

      return UsageStats.fromJson(response.data);
    } catch (e) {
      throw Exception('获取使用统计失败: $e');
    }
  }

  /// 获取订阅的AI员工列表
  /// user_id现在从JWT token中自动获取，无需手动传递
  Future<List<Agent>> getSubscribedAgents() async {
    try {
      final authHeaders = await AuthenticatedHttpClient.getAuthHeaders();

      final response = await _dio.get(
        '${AppConfig.apiUrl}/profile/subscribed-agents',  // 移除user_id参数
        options: Options(headers: authHeaders),
      );

      return (response.data as List)
          .map((json) => Agent.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('获取订阅列表失败: $e');
    }
  }
}
