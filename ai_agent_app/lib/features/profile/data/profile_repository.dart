import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../core/config/app_config.dart';
import '../domain/models/usage_stats.dart';
import '../../agents/domain/models/agent.dart';

class ProfileRepository {
  final _supabase = Supabase.instance.client;
  final _dio = Dio();

  /// 获取使用统计
  Future<UsageStats> getUsageStats(String userId) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;

      final response = await _dio.get(
        '${AppConfig.apiUrl}/profile/usage-stats',
        queryParameters: {'user_id': userId},
        options: Options(headers: {'Authorization': 'Bearer $token'}),
      );

      return UsageStats.fromJson(response.data);
    } catch (e) {
      throw Exception('获取使用统计失败: $e');
    }
  }

  /// 获取订阅的AI员工列表
  Future<List<Agent>> getSubscribedAgents(String userId) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;

      final response = await _dio.get(
        '${AppConfig.apiUrl}/profile/subscribed-agents',
        queryParameters: {'user_id': userId},
        options: Options(headers: {'Authorization': 'Bearer $token'}),
      );

      return (response.data as List)
          .map((json) => Agent.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('获取订阅列表失败: $e');
    }
  }
}
