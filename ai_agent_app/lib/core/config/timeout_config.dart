/// 超时配置
///
/// 统一的超时设置，与后端TimeoutConfig保持一致。
class TimeoutConfig {
  // ========== WebSocket 配置 ==========
  /// WebSocket连接超时
  static const Duration wsConnectTimeout = Duration(seconds: 10);

  /// WebSocket重连延迟（初始值）
  static const Duration wsReconnectDelay = Duration(seconds: 3);

  /// 最大重连尝试次数
  static const int wsMaxReconnectAttempts = 5;

  /// 服务端心跳间隔（客户端应预期此频率的ping）
  static const Duration serverPingInterval = Duration(seconds: 3);

  /// Ping超时（超过此时间未收到ping则认为断连）
  static const Duration pingTimeout = Duration(seconds: 10);

  // ========== 消息配置 ==========
  /// 消息发送总超时
  static const Duration messageTimeout = Duration(minutes: 10);

  /// 单个chunk接收超时
  static const Duration chunkTimeout = Duration(seconds: 30);

  // ========== HTTP配置（SSE fallback） ==========
  /// HTTP请求超时
  static const Duration httpRequestTimeout = Duration(seconds: 180);

  /// SSE流式chunk超时
  static const Duration sseChunkTimeout = Duration(seconds: 30);

  // ========== UI更新配置 ==========
  /// 流式内容批量更新间隔
  static const Duration streamingUpdateInterval = Duration(milliseconds: 50);

  /// 自动滚动延迟
  static const Duration autoScrollDelay = Duration(milliseconds: 100);

  /// 滚动防抖时间
  static const Duration scrollDebounceTime = Duration(milliseconds: 200);
}
