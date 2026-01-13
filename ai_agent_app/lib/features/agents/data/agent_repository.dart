import 'package:supabase_flutter/supabase_flutter.dart';
import '../domain/models/agent.dart';

class AgentRepository {
  final _supabase = Supabase.instance.client;

  /// 获取所有活跃的AI员工
  Future<List<Agent>> getActiveAgents() async {
    try {
      final response = await _supabase
          .from('agents')
          .select()
          .eq('is_active', true)
          .order('created_at', ascending: false);

      return (response as List)
          .map((json) => Agent.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('获取AI员工列表失败: $e');
    }
  }

  /// 获取用户订阅的AI员工
  Future<List<UserAgentSubscription>> getUserSubscriptions(
      String userId) async {
    try {
      final response = await _supabase
          .from('user_agent_subscriptions')
          .select('*, agent:agents(*)')
          .eq('user_id', userId)
          .order('subscribed_at', ascending: false);

      // Supabase .select() 直接返回 List<Map<String, dynamic>>
      return (response as List)
          .map((json) =>
              UserAgentSubscription.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('获取订阅列表失败: $e');
    }
  }

  /// 订阅AI员工
  Future<void> subscribeToAgent({
    required String userId,
    required String agentId,
    Map<String, dynamic>? config,
  }) async {
    try {
      await _supabase.from('user_agent_subscriptions').insert({
        'user_id': userId,
        'agent_id': agentId,
        'config': config,
        'subscribed_at': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      throw Exception('订阅AI员工失败: $e');
    }
  }

  /// 取消订阅AI员工
  Future<void> unsubscribeFromAgent({
    required String userId,
    required String agentId,
  }) async {
    try {
      await _supabase
          .from('user_agent_subscriptions')
          .delete()
          .eq('user_id', userId)
          .eq('agent_id', agentId);
    } catch (e) {
      throw Exception('取消订阅失败: $e');
    }
  }

  /// 检查用户是否已订阅某个AI员工
  Future<bool> isUserSubscribed({
    required String userId,
    required String agentId,
  }) async {
    try {
      final response = await _supabase
          .from('user_agent_subscriptions')
          .select()
          .eq('user_id', userId)
          .eq('agent_id', agentId)
          .maybeSingle();

      return response != null;
    } catch (e) {
      return false;
    }
  }
}
