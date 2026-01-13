import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';
import '../domain/models/briefing.dart';
import '../../../core/config/app_config.dart';

class BriefingRepository {
  final _supabase = Supabase.instance.client;

  /// 获取简报列表（信息流）
  Future<BriefingListResponse> getBriefings({
    int skip = 0,
    int limit = 50,
    BriefingStatus? status,
  }) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;
      if (token == null) {
        throw Exception('用户未登录');
      }

      var url = '${AppConfig.apiUrl}/briefings?skip=$skip&limit=$limit';
      if (status != null) {
        url += '&status=${_statusToString(status)}';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return BriefingListResponse.fromJson(data);
      } else {
        throw Exception('获取简报列表失败: ${response.body}');
      }
    } catch (e) {
      throw Exception('获取简报列表失败: $e');
    }
  }

  /// 获取未读简报数量
  Future<BriefingUnreadCount> getUnreadCount() async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;
      if (token == null) {
        throw Exception('用户未登录');
      }

      final response = await http.get(
        Uri.parse('${AppConfig.apiUrl}/briefings/unread-count'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return BriefingUnreadCount.fromJson(data);
      } else {
        throw Exception('获取未读数量失败: ${response.body}');
      }
    } catch (e) {
      throw Exception('获取未读数量失败: $e');
    }
  }

  /// 获取单个简报详情
  Future<Briefing> getBriefing(String briefingId) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;
      if (token == null) {
        throw Exception('用户未登录');
      }

      final response = await http.get(
        Uri.parse('${AppConfig.apiUrl}/briefings/$briefingId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return Briefing.fromJson(data);
      } else {
        throw Exception('获取简报详情失败: ${response.body}');
      }
    } catch (e) {
      throw Exception('获取简报详情失败: $e');
    }
  }

  /// 获取简报关联的完整报告
  ///
  /// 返回格式：
  /// - content: 完整的Markdown报告内容
  /// - format: 内容格式（默认markdown）
  /// - title: 报告标题
  /// - created_at: 创建时间（如果从artifact获取）
  Future<Map<String, dynamic>?> getBriefingReport(String briefingId) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;
      if (token == null) {
        throw Exception('用户未登录');
      }

      final response = await http.get(
        Uri.parse('${AppConfig.apiUrl}/briefings/$briefingId/report'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else if (response.statusCode == 404) {
        return null;
      } else {
        throw Exception('获取报告失败: ${response.body}');
      }
    } catch (e) {
      throw Exception('获取报告失败: $e');
    }
  }

  /// 标记简报为已读
  Future<Briefing> markAsRead(String briefingId) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;
      if (token == null) {
        throw Exception('用户未登录');
      }

      final response = await http.patch(
        Uri.parse('${AppConfig.apiUrl}/briefings/$briefingId/read'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return Briefing.fromJson(data);
      } else {
        throw Exception('标记已读失败: ${response.body}');
      }
    } catch (e) {
      throw Exception('标记已读失败: $e');
    }
  }

  /// 从简报开始对话
  Future<StartConversationResponse> startConversation(
    String briefingId, {
    String? prompt,
  }) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;
      if (token == null) {
        throw Exception('用户未登录');
      }

      final body = <String, dynamic>{};
      if (prompt != null) {
        body['prompt'] = prompt;
      }

      final response = await http.post(
        Uri.parse('${AppConfig.apiUrl}/briefings/$briefingId/start-conversation'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: body.isNotEmpty ? jsonEncode(body) : null,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return StartConversationResponse.fromJson(data);
      } else {
        throw Exception('开始对话失败: ${response.body}');
      }
    } catch (e) {
      throw Exception('开始对话失败: $e');
    }
  }

  /// 忽略简报
  Future<void> dismissBriefing(String briefingId) async {
    try {
      final token = _supabase.auth.currentSession?.accessToken;
      if (token == null) {
        throw Exception('用户未登录');
      }

      final response = await http.delete(
        Uri.parse('${AppConfig.apiUrl}/briefings/$briefingId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode != 200) {
        throw Exception('忽略简报失败: ${response.body}');
      }
    } catch (e) {
      throw Exception('忽略简报失败: $e');
    }
  }

  /// 使用 Supabase 直接获取简报（备用方案，用于轮询）
  Future<List<Briefing>> getBriefingsFromSupabase({
    required String userId,
    int limit = 50,
  }) async {
    try {
      final response = await _supabase
          .from('briefings')
          .select('''
            *,
            agents:agent_id (
              name,
              avatar_url,
              role
            )
          ''')
          .eq('user_id', userId)
          .order('created_at', ascending: false)
          .limit(limit);

      return (response as List).map((json) {
        final briefingJson = Map<String, dynamic>.from(json);
        // 展开 agents 关联
        if (briefingJson['agents'] != null) {
          final agent = briefingJson['agents'] as Map<String, dynamic>;
          briefingJson['agent_name'] = agent['name'];
          briefingJson['agent_avatar_url'] = agent['avatar_url'];
          briefingJson['agent_role'] = agent['role'];
        }
        briefingJson.remove('agents');
        return Briefing.fromJson(briefingJson);
      }).toList();
    } catch (e) {
      throw Exception('获取简报失败: $e');
    }
  }

  String _statusToString(BriefingStatus status) {
    switch (status) {
      case BriefingStatus.newItem:
        return 'new';
      case BriefingStatus.read:
        return 'read';
      case BriefingStatus.actioned:
        return 'actioned';
      case BriefingStatus.dismissed:
        return 'dismissed';
    }
  }
}
