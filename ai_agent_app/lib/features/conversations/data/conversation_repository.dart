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

  // 优化：超时配置常量（与后端对齐）
  static const Duration _requestTimeout = Duration(seconds: 180);  // 3分钟总超时
  static const Duration _streamChunkTimeout = Duration(seconds: 30); // 单个chunk超时

  /// 获取后端API基础URL
  String get baseUrl => AppConfig.apiUrl;

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
  ///
  /// 优化：使用与后端对齐的超时配置
  Stream<String> sendMessageStream({
    required String conversationId,
    required String newMessage,
    Duration? timeout,
  }) async* {
    final effectiveTimeout = timeout ?? _requestTimeout;

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
        effectiveTimeout,
        onTimeout: () {
          throw TimeoutException('消息发送超时（${effectiveTimeout.inSeconds}秒），请检查网络连接');
        },
      );

      if (streamedResponse.statusCode != 200) {
        final body = await streamedResponse.stream.bytesToString();
        throw Exception(
            'API请求失败: ${streamedResponse.statusCode} ${streamedResponse.reasonPhrase} $body');
      }

      // 解析 SSE - 按行处理，更简单更可靠
      String buffer = '';
      await for (final chunk in streamedResponse.stream
          .timeout(
            _streamChunkTimeout,
            onTimeout: (sink) {
              sink.addError(TimeoutException('数据接收超时，请检查网络连接'));
              sink.close();
            },
          )
          .transform(utf8.decoder)) {
        buffer += chunk;

        // 按行处理
        while (buffer.contains('\n')) {
          final idx = buffer.indexOf('\n');
          final line = buffer.substring(0, idx).trim();
          buffer = buffer.substring(idx + 1);

          // 跳过空行
          if (line.isEmpty) continue;

          // 解析 data: 行
          if (line.startsWith('data:')) {
            final data = line.substring(5).trim();

            // 跳过空数据
            if (data.isEmpty) continue;

            // 检查结束标记
            if (data == '[DONE]') return;

            // 检查错误
            if (data.startsWith('[ERROR]')) {
              throw Exception('AI响应错误: $data');
            }

            // 尝试解析为 JSON（任务相关事件）
            if (data.startsWith('{')) {
              try {
                final json = jsonDecode(data) as Map<String, dynamic>;
                // 如果是错误类型，抛出异常
                if (json['type'] == 'error') {
                  throw Exception(json['error'] ?? '未知错误');
                }
                // 其他 JSON 事件暂时忽略（任务进度等）
                continue;
              } catch (e) {
                // 不是有效 JSON，当作普通文本处理
              }
            }

            // 普通文本 chunk
            yield data;
          }
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
    Duration? timeout,
  }) async* {
    final effectiveTimeout = timeout ?? _requestTimeout;
    int retryCount = 0;

    while (retryCount <= maxRetries) {
      try {
        yield* sendMessageStream(
          conversationId: conversationId,
          newMessage: newMessage,
          timeout: effectiveTimeout,
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

      // 获取对话列表（后端现在直接返回 agent_name 和 agent_role）
      final response = await dio.get(
        '${AppConfig.apiUrl}/conversations',
        queryParameters: {'limit': 50},
        options: Options(headers: authHeaders),
      );

      final conversations = response.data as List? ?? [];
      final summaries = <ConversationSummary>[];

      for (final conv in conversations) {
        summaries.add(ConversationSummary(
          id: conv['id'] as String,
          agentId: conv['agent_id'] as String,
          agentName: conv['agent_name'] as String? ?? '未知员工',
          agentRole: conv['agent_role'] as String? ?? conv['agent_id'] as String,
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
