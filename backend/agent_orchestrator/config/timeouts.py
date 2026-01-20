"""
Timeout Configuration

统一的超时配置，确保前后端超时设置一致。
"""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class TimeoutConfig:
    """统一超时配置

    所有超时值的单位是秒，除非特别说明。
    """

    # ========== WebSocket 配置 ==========
    # 心跳间隔（服务端发送ping的间隔）
    WS_HEARTBEAT_INTERVAL: int = 3  # 从10秒优化到3秒

    # 心跳超时（等待pong响应的超时时间）
    WS_PING_TIMEOUT: int = 5

    # 连接空闲超时
    WS_IDLE_TIMEOUT: int = 300  # 5分钟

    # 重连宽限期
    WS_RECONNECT_GRACE_PERIOD: int = 10

    # ========== 对话级别超时 ==========
    # 整个对话的超时时间
    CONVERSATION_TIMEOUT: int = 600  # 10分钟

    # 单个API调用超时
    API_CALL_TIMEOUT: int = 120  # 2分钟

    # 流式响应中单个chunk的超时
    STREAM_CHUNK_TIMEOUT: int = 30  # 30秒

    # ========== 工具级别超时（中优先级，暂不强制） ==========
    # 默认工具超时
    TOOL_DEFAULT_TIMEOUT: int = 60  # 1分钟

    # 长时间运行的工具超时
    TOOL_LONG_RUNNING_TIMEOUT: int = 300  # 5分钟

    # ========== SSE 配置（向后兼容） ==========
    # SSE Keep-alive 间隔
    SSE_KEEPALIVE_INTERVAL: int = 5  # 从10秒优化到5秒

    # SSE 空闲超时
    SSE_IDLE_TIMEOUT: int = 600  # 10分钟

    # ========== 消息缓冲配置 ==========
    # 首次刷新间隔（毫秒）
    BUFFER_INITIAL_FLUSH_MS: int = 30

    # 稳定刷新间隔（毫秒）
    BUFFER_STEADY_FLUSH_MS: int = 100

    # 缓冲区大小触发阈值（字符数）
    BUFFER_MAX_SIZE: int = 30


@lru_cache(maxsize=1)
def get_timeout_config() -> TimeoutConfig:
    """获取超时配置（支持环境变量覆盖）"""
    return TimeoutConfig(
        WS_HEARTBEAT_INTERVAL=int(os.getenv("WS_HEARTBEAT_INTERVAL", "3")),
        WS_PING_TIMEOUT=int(os.getenv("WS_PING_TIMEOUT", "5")),
        WS_IDLE_TIMEOUT=int(os.getenv("WS_IDLE_TIMEOUT", "300")),
        WS_RECONNECT_GRACE_PERIOD=int(os.getenv("WS_RECONNECT_GRACE_PERIOD", "10")),
        CONVERSATION_TIMEOUT=int(os.getenv("CONVERSATION_TIMEOUT", "600")),
        API_CALL_TIMEOUT=int(os.getenv("API_CALL_TIMEOUT", "120")),
        STREAM_CHUNK_TIMEOUT=int(os.getenv("STREAM_CHUNK_TIMEOUT", "30")),
        TOOL_DEFAULT_TIMEOUT=int(os.getenv("TOOL_DEFAULT_TIMEOUT", "60")),
        TOOL_LONG_RUNNING_TIMEOUT=int(os.getenv("TOOL_LONG_RUNNING_TIMEOUT", "300")),
        SSE_KEEPALIVE_INTERVAL=int(os.getenv("SSE_KEEPALIVE_INTERVAL", "5")),
        SSE_IDLE_TIMEOUT=int(os.getenv("SSE_IDLE_TIMEOUT", "600")),
        BUFFER_INITIAL_FLUSH_MS=int(os.getenv("BUFFER_INITIAL_FLUSH_MS", "30")),
        BUFFER_STEADY_FLUSH_MS=int(os.getenv("BUFFER_STEADY_FLUSH_MS", "100")),
        BUFFER_MAX_SIZE=int(os.getenv("BUFFER_MAX_SIZE", "30")),
    )
