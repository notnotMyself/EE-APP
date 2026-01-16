import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:dio/dio.dart';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/authenticated_http_client.dart';
import '../domain/models/conversation.dart';
import '../domain/models/conversation_summary.dart';

class ConversationRepository {
  final _supabase = Supabase.instance.client;

  /// 获取或创建对话（通过后端 API）
  ///
  /// 数据库有唯一约束限制每个用户-Agent对只能有一个对话，
  /// 所以这里改用后端的 get_or_create 逻辑。
  Future<Conversation> createConversation({
    required String userId,
    required String agentId,
  }) async {
    try {
      // 使用后端 API 获取或创建对话
      final dio = Dio();
      final authHeaders = await AuthenticatedHttpClient.getAuthHeaders();

      final response = await dio.get(
        '${AppConfig.apiUrl}/conversations/$agentId',
        options: Options(headers: authHeaders),
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        return Conversation(
          id: data['id'] as String,
          userId: data['user_id'] as String,
          agentId: data['agent_id'] as String,
          status: data['status'] as String?,
          startedAt: DateTime.parse(data['started_at'] as String),
          lastMessageAt: data['last_message_at'] != null
              ? DateTime.parse(data['last_message_at'] as String)
              : null,
        );
      } else {
        throw Exception('获取对话失败: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('获取对话失败: ${e.message}');
    } catch (e) {
      throw Exception('获取对话失败: $e');
    }
  }

  /// 获取用户的所有对话
  Future<List<Conversation>> getUserConversations(String userId) async {
    try {
      final response = await _supabase
          .from('conversations')
          .select('*')
          .eq('user_id', userId)
          .order('last_message_at', ascending: false);

      return (response as List)
          .map((json) => Conversation.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('获取对话列表失败: $e');
    }
  }

  /// 获取对话详情
  Future<Conversation> getConversation(String conversationId) async {
    try {
      final response = await _supabase
          .from('conversations')
          .select('*')
          .eq('id', conversationId)
          .single();

      return Conversation.fromJson(response as Map<String, dynamic>);
    } catch (e) {
      throw Exception('获取对话详情失败: $e');
    }
  }

  /// 获取对话中的所有消息（通过后端 API）
  Future<List<Message>> getMessages(String conversationId) async {
    try {
      final dio = Dio();
      final authHeaders = await AuthenticatedHttpClient.getAuthHeaders();

      final response = await dio.get(
        '${AppConfig.apiUrl}/conversations/$conversationId/messages',
        options: Options(headers: authHeaders),
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final messages = data['messages'] as List;
        return messages
            .map((json) => Message.fromJson(json as Map<String, dynamic>))
            .toList();
      } else {
        throw Exception('获取消息列表失败: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('获取消息列表失败: ${e.message}');
    } catch (e) {
      throw Exception('获取消息列表失败: $e');
    }
  }

  /// 保存消息到数据库
  Future<Message> saveMessage({
    required String conversationId,
    required String role,
    required String content,
  }) async {
    try {
      final response = await _supabase.from('messages').insert({
        'conversation_id': conversationId,
        'role': role,
        'content': content,
      }).select().single();

      return Message.fromJson(response as Map<String, dynamic>);
    } catch (e) {
      throw Exception('保存消息失败: $e');
    }
  }

  /// 调用 agent_orchestrator 的流式对话接口（带超时控制）
  Stream<String> sendMessageStream({
    required String conversationId,
    required String newMessage,
    Duration timeout = const Duration(seconds: 60),
  }) async* {
    try {
      // 获取认证Token
      final authHeaders = await AuthenticatedHttpClient.getAuthHeadersOnly();

      // 构建请求体
      final requestBody = {
        'content': newMessage,  // 修改为后端期望的字段名
      };

      // 发送POST请求到正确的端点，添加超时
      final request = http.Request(
        'POST',
        Uri.parse('${AppConfig.apiUrl}/conversations/$conversationId/messages'),  // 修正endpoint
      );
      request.headers.addAll(authHeaders);
      request.headers['Content-Type'] = 'application/json';
      request.body = jsonEncode(requestBody);

      final streamedResponse = await request.send().timeout(
        timeout,
        onTimeout: () {
          throw TimeoutException('消息发送超时，请检查网络连接');
        },
      );

      if (streamedResponse.statusCode != 200) {
        final body = await streamedResponse.stream.bytesToString();
        throw Exception(
            'API请求失败: ${streamedResponse.statusCode} ${streamedResponse.reasonPhrase} $body');
      }

      // 解析 SSE（ai_agent_platform 格式：只有 data: ... 行，且事件以空行分隔）
      // 添加流超时控制
      String buffer = '';
      await for (final chunk in streamedResponse.stream
          .timeout(
            timeout,
            onTimeout: (sink) {
              sink.addError(TimeoutException('消息接收超时，请检查网络连接'));
              sink.close();
            },
          )
          .transform(utf8.decoder)) {
        buffer += chunk;

        while (true) {
          final idx = buffer.indexOf('\n\n');
          if (idx == -1) break;

          final eventBlock = buffer.substring(0, idx);
          buffer = buffer.substring(idx + 2);

          final lines = eventBlock.split('\n');
          final dataLines = <String>[];
          for (final rawLine in lines) {
            final line = rawLine.trimRight();
            if (line.startsWith('data:')) {
              dataLines.add(line.substring(5).trimLeft());
            }
          }

          if (dataLines.isEmpty) continue;
          final data = dataLines.join('\n');

          if (data == '[DONE]') return;
          if (data.startsWith('[ERROR]')) {
            throw Exception('AI响应错误: $data');
          }

          yield data;
        }
      }
    } on TimeoutException catch (e) {
      throw Exception('请求超时: ${e.message}');
    } on SocketException catch (e) {
      throw Exception('网络连接失败: ${e.message}');
    } catch (e) {
      throw Exception('发送消息失败: $e');
    }
  }

  /// 带重试机制的流式对话接口
  Stream<String> sendMessageStreamWithRetry({
    required String conversationId,
    required String newMessage,
    int maxRetries = 3,
    Duration timeout = const Duration(seconds: 60),
  }) async* {
    int retryCount = 0;

    while (retryCount <= maxRetries) {
      try {
        yield* sendMessageStream(
          conversationId: conversationId,
          newMessage: newMessage,
          timeout: timeout,
        );
        return; // 成功则退出
      } on TimeoutException catch (e) {
        retryCount++;
        if (retryCount > maxRetries) {
          throw Exception('请求超时（已重试${maxRetries}次）: ${e.message}');
        }

        // 指数退避等待后重试
        final waitSeconds = pow(2, retryCount).toInt();
        yield '[网络超时，正在重试...第 $retryCount 次，等待 $waitSeconds 秒]';
        await Future.delayed(Duration(seconds: waitSeconds));
      } on SocketException catch (e) {
        retryCount++;
        if (retryCount > maxRetries) {
          throw Exception('网络连接失败（已重试${maxRetries}次）: ${e.message}');
        }

        // 指数退避等待后重试
        final waitSeconds = pow(2, retryCount).toInt();
        yield '[网络连接失败，正在重试...第 $retryCount 次，等待 $waitSeconds 秒]';
        await Future.delayed(Duration(seconds: waitSeconds));
      } catch (e) {
        // 其他错误不重试，直接抛出
        rethrow;
      }
    }
  }

  /// 获取用户的对话摘要列表（用于消息列表页）
  Future<List<ConversationSummary>> getConversationSummaries() async {
    try {
      final dio = Dio();
      final authHeaders = await AuthenticatedHttpClient.getAuthHeaders();

      // 1. 获取对话列表
      final conversationsResponse = await dio.get(
        '${AppConfig.apiUrl}/conversations',
        queryParameters: {'limit': 50},
        options: Options(headers: authHeaders),
      );

      // 2. 获取 agent 列表（用于填充 agent 信息）
      final agentsResponse = await dio.get(
        '${AppConfig.apiUrl}/agents',
        options: Options(headers: authHeaders),
      );

      // 构建 agent 映射 (uuid -> agent info)
      final agentMap = <String, Map<String, dynamic>>{};
      if (agentsResponse.statusCode == 200) {
        final agentsData = agentsResponse.data as Map<String, dynamic>;
        final agents = agentsData['agents'] as List? ?? [];
        for (final agent in agents) {
          // 后端返回的 agent 包含 role, name, description 等
          // 需要通过 role 查找对应的 uuid
          agentMap[agent['role'] as String] = agent as Map<String, dynamic>;
        }
      }

      // 3. 转换为 ConversationSummary
      final conversations = conversationsResponse.data as List? ?? [];
      final summaries = <ConversationSummary>[];

      for (final conv in conversations) {
        final agentId = conv['agent_id'] as String;
        
        // 尝试通过 agent_id (uuid) 或 role 查找 agent 信息
        Map<String, dynamic>? agentInfo;
        for (final entry in agentMap.entries) {
          // 简单匹配：检查 agent_id 是否包含 role 或者相等
          if (agentId == entry.key || agentId.contains(entry.key)) {
            agentInfo = entry.value;
            break;
          }
        }

        summaries.add(ConversationSummary(
          id: conv['id'] as String,
          agentId: agentId,
          agentName: agentInfo?['name'] as String? ?? '未知员工',
          agentRole: agentInfo?['role'] as String? ?? agentId,
          agentAvatarUrl: null, // TODO: 后端需要返回 avatar
          lastMessageContent: conv['title'] as String?, // 用 title 作为最后消息预览
          lastMessageAt: conv['last_message_at'] != null
              ? DateTime.tryParse(conv['last_message_at'] as String)
              : null,
          unreadCount: 0, // TODO: 后端需要返回未读数
          createdAt: DateTime.parse(conv['started_at'] as String),
        ));
      }

      return summaries;
    } on DioException catch (e) {
      throw Exception('获取对话摘要列表失败: ${e.message}');
    } catch (e) {
      throw Exception('获取对话摘要列表失败: $e');
    }
  }

  /// 搜索对话内容
  Future<List<Message>> searchMessages(String userId, String query) async {
    try {
      // TODO: 等 backend 实现搜索接口后再完善
      return [];
    } catch (e) {
      throw Exception('搜索对话失败: $e');
    }
  }

  /// 标记对话为已读
  Future<void> markConversationAsRead(String conversationId) async {
    try {
      // TODO: 等 backend 实现已读状态接口后再完善
    } catch (e) {
      throw Exception('标记已读失败: $e');
    }
  }
}
