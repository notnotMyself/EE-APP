import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:logger/logger.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../core/config/timeout_config.dart';

/// WebSocket消息类型
enum WSMessageType {
  textChunk,
  toolUse,
  toolResult,
  toolProgress, // 新增：工具执行进度
  taskStart,
  taskProgress,
  briefingCreated,
  taskComplete,
  error,
  done,
  ping,
  pong,
  connected,
  unknown,
}

/// WebSocket消息
class WSMessage {
  final WSMessageType type;
  final String? content;
  final Map<String, dynamic>? metadata;
  final double timestamp;

  WSMessage({
    required this.type,
    this.content,
    this.metadata,
    required this.timestamp,
  });

  factory WSMessage.fromJson(Map<String, dynamic> json) {
    final typeStr = json['type'] as String? ?? 'unknown';
    final type = _parseMessageType(typeStr);

    return WSMessage(
      type: type,
      content: json['content'] as String?,
      metadata: json,
      timestamp: (json['ts'] as num?)?.toDouble() ?? 0,
    );
  }

  static WSMessageType _parseMessageType(String type) {
    switch (type) {
      case 'text_chunk':
        return WSMessageType.textChunk;
      case 'tool_use':
        return WSMessageType.toolUse;
      case 'tool_result':
        return WSMessageType.toolResult;
      case 'tool_progress':
        return WSMessageType.toolProgress;
      case 'task_start':
        return WSMessageType.taskStart;
      case 'task_progress':
        return WSMessageType.taskProgress;
      case 'briefing_created':
        return WSMessageType.briefingCreated;
      case 'task_complete':
        return WSMessageType.taskComplete;
      case 'error':
        return WSMessageType.error;
      case 'done':
        return WSMessageType.done;
      case 'ping':
        return WSMessageType.ping;
      case 'pong':
        return WSMessageType.pong;
      case 'connected':
        return WSMessageType.connected;
      default:
        return WSMessageType.unknown;
    }
  }
}

/// WebSocket连接状态
enum ConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
}

/// 对话WebSocket客户端
///
/// 提供与后端WebSocket端点的实时通信，支持：
/// - 自动重连（指数退避）
/// - 心跳检测
/// - 流式消息处理
class ConversationWebSocketClient {
  final String baseUrl;
  final String conversationId;
  final Future<String?> Function() getToken;

  // 回调
  final void Function(WSMessage)? onMessage;
  final void Function()? onConnected;
  final void Function()? onDisconnected;
  final void Function(String)? onError;

  // 内部状态
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _reconnectTimer;
  Timer? _pingCheckTimer;
  DateTime? _lastPingTime;

  int _reconnectAttempts = 0;
  ConnectionState _connectionState = ConnectionState.disconnected;

  final _logger = Logger();

  ConversationWebSocketClient({
    required this.baseUrl,
    required this.conversationId,
    required this.getToken,
    this.onMessage,
    this.onConnected,
    this.onDisconnected,
    this.onError,
  });

  /// 当前连接状态
  ConnectionState get connectionState => _connectionState;

  /// 是否已连接
  bool get isConnected => _connectionState == ConnectionState.connected;

  /// 连接WebSocket
  Future<void> connect() async {
    if (_connectionState == ConnectionState.connecting ||
        _connectionState == ConnectionState.connected) {
      return;
    }

    _connectionState = ConnectionState.connecting;

    try {
      final token = await getToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      // 构建WebSocket URL
      final wsScheme = baseUrl.startsWith('https') ? 'wss' : 'ws';
      final host = Uri.parse(baseUrl).host;
      final port = Uri.parse(baseUrl).port;
      final portStr = (port != 80 && port != 443) ? ':$port' : '';

      final wsUrl = Uri.parse(
        '$wsScheme://$host$portStr/api/v1/conversations/$conversationId/ws?token=$token',
      );

      _logger.i('Connecting to WebSocket: ${wsUrl.replace(queryParameters: {'token': '***'})}');

      _channel = WebSocketChannel.connect(wsUrl);

      // 等待连接建立
      await _channel!.ready.timeout(
        TimeoutConfig.wsConnectTimeout,
        onTimeout: () {
          throw TimeoutException('WebSocket connection timeout');
        },
      );

      _setupListeners();
      _startPingCheck();

      _connectionState = ConnectionState.connected;
      _reconnectAttempts = 0;

      _logger.i('WebSocket connected');
      onConnected?.call();
    } catch (e) {
      _logger.e('WebSocket connection failed: ${e.toString()}');
      _connectionState = ConnectionState.disconnected;
      onError?.call('连接失败: ${e.toString()}');
      _scheduleReconnect();
    }
  }

  void _setupListeners() {
    _subscription = _channel?.stream.listen(
      _handleData,
      onError: _handleError,
      onDone: _handleDone,
    );
  }

  void _handleData(dynamic data) {
    try {
      // 处理空数据
      if (data == null) {
        _logger.w('Received null data from WebSocket');
        return;
      }

      final json = jsonDecode(data as String) as Map<String, dynamic>;
      final message = WSMessage.fromJson(json);

      // 更新ping时间
      if (message.type == WSMessageType.ping) {
        _lastPingTime = DateTime.now();
        _sendPong();
        return;
      }

      onMessage?.call(message);
    } catch (e, stackTrace) {
      // 安全地记录错误，避免 null 值导致 logger 崩溃
      final errorMsg = e?.toString() ?? 'Unknown error';
      final stackMsg = stackTrace?.toString() ?? 'No stack trace';

      try {
        _logger.w('Failed to parse WebSocket message: $errorMsg');
        // 在调试模式下打印堆栈
        if (const bool.fromEnvironment('dart.vm.product') == false) {
          _logger.d('Stack trace: $stackMsg');
        }
      } catch (logError) {
        // 如果 logger 也失败了，使用 print 作为后备
        print('Failed to log WebSocket error: $errorMsg');
      }
    }
  }

  void _handleError(dynamic error) {
    // 安全地记录错误
    final errorMsg = error?.toString() ?? "Unknown error";
    try {
      _logger.e('WebSocket error: $errorMsg');
    } catch (logError) {
      print('Failed to log WebSocket error: $errorMsg');
    }
    onError?.call('WebSocket错误: $errorMsg');
    _disconnect(scheduleReconnect: true);
  }

  void _handleDone() {
    _logger.i('WebSocket stream closed');
    _disconnect(scheduleReconnect: true);
  }

  void _startPingCheck() {
    _pingCheckTimer?.cancel();
    _lastPingTime = DateTime.now();

    _pingCheckTimer = Timer.periodic(
      TimeoutConfig.serverPingInterval,
      (_) {
        if (_lastPingTime != null &&
            DateTime.now().difference(_lastPingTime!) > TimeoutConfig.pingTimeout) {
          _logger.w('Ping timeout, reconnecting...');
          _disconnect(scheduleReconnect: true);
        }
      },
    );
  }

  void _sendPong() {
    _send({'type': 'pong'});
  }

  /// 发送消息
  void sendMessage(String content) {
    _send({
      'type': 'message',
      'content': content,
    });
  }

  /// 发送带附件的消息
  void sendMessageWithAttachments(String content, List<Map<String, dynamic>>? attachments) {
    final message = <String, dynamic>{
      'type': 'message',
      'content': content,
    };
    if (attachments != null && attachments.isNotEmpty) {
      message['attachments'] = attachments;
    }
    _send(message);
  }

  void _send(Map<String, dynamic> data) {
    if (_channel == null || _connectionState != ConnectionState.connected) {
      _logger.w('Cannot send message: not connected');
      return;
    }

    try {
      _channel!.sink.add(jsonEncode(data));
    } catch (e) {
      final errorMsg = e?.toString() ?? 'Unknown error';
      try {
        _logger.e('Failed to send message: $errorMsg');
      } catch (logError) {
        print('Failed to log send error: $errorMsg');
      }
    }
  }

  void _scheduleReconnect() {
    if (_reconnectAttempts >= TimeoutConfig.wsMaxReconnectAttempts) {
      _logger.e('Max reconnection attempts reached');
      onError?.call('连接失败，已达最大重试次数');
      return;
    }

    _connectionState = ConnectionState.reconnecting;
    _reconnectAttempts++;

    // 指数退避，最大30秒
    final delay = Duration(
      seconds: min(pow(2, _reconnectAttempts).toInt(), 30),
    );

    _logger.i('Scheduling reconnect in ${delay.inSeconds}s (attempt $_reconnectAttempts)');

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(delay, () {
      connect();
    });
  }

  void _disconnect({bool scheduleReconnect = false}) {
    _pingCheckTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    _channel = null;

    final wasConnected = _connectionState == ConnectionState.connected;
    _connectionState = ConnectionState.disconnected;

    if (wasConnected) {
      onDisconnected?.call();
    }

    if (scheduleReconnect) {
      _scheduleReconnect();
    }
  }

  /// 断开连接
  void disconnect() {
    _reconnectTimer?.cancel();
    _disconnect(scheduleReconnect: false);
  }

  /// 释放资源
  void dispose() {
    disconnect();
  }
}
