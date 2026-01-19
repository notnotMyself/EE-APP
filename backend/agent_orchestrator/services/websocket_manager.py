"""
WebSocket Connection Manager

管理WebSocket连接，包括心跳检测、重连支持和消息广播。
参考 claudecodeui 的 WebSocket 实现模式。
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

from config import get_timeout_config

logger = logging.getLogger(__name__)


@dataclass
class ConnectionState:
    """单个连接的状态"""

    websocket: WebSocket
    user_id: str
    conversation_id: str
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    last_pong: float = field(default_factory=time.time)
    heartbeat_task: Optional[asyncio.Task] = None
    is_alive: bool = True


class ConnectionManager:
    """WebSocket 连接管理器

    功能：
    - 管理多个对话的WebSocket连接
    - 心跳检测（3秒间隔）
    - 自动断开空闲连接（5分钟）
    - 支持广播消息
    """

    def __init__(self):
        self._config = get_timeout_config()

        # conversation_id -> {user_id -> ConnectionState}
        self._connections: Dict[str, Dict[str, ConnectionState]] = {}

        # 等待中的pong响应
        self._pending_pongs: Dict[str, asyncio.Event] = {}

    @property
    def heartbeat_interval(self) -> int:
        return self._config.WS_HEARTBEAT_INTERVAL

    @property
    def ping_timeout(self) -> int:
        return self._config.WS_PING_TIMEOUT

    @property
    def idle_timeout(self) -> int:
        return self._config.WS_IDLE_TIMEOUT

    async def connect(
        self,
        websocket: WebSocket,
        conversation_id: str,
        user_id: str,
    ) -> ConnectionState:
        """注册新的WebSocket连接（websocket.accept() 应该在调用此方法前完成）"""
        # 创建连接状态
        state = ConnectionState(
            websocket=websocket,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        # 注册连接
        if conversation_id not in self._connections:
            self._connections[conversation_id] = {}

        # 如果用户已有连接，先关闭旧连接
        if user_id in self._connections[conversation_id]:
            old_state = self._connections[conversation_id][user_id]
            await self._close_connection(old_state, reason="replaced")

        self._connections[conversation_id][user_id] = state

        # 启动心跳任务
        state.heartbeat_task = asyncio.create_task(
            self._heartbeat_loop(state),
            name=f"heartbeat-{conversation_id}-{user_id}",
        )

        logger.info(
            f"WebSocket connected: conversation={conversation_id}, user={user_id}"
        )

        return state

    async def disconnect(self, conversation_id: str, user_id: str) -> None:
        """断开连接并清理资源"""
        if conversation_id not in self._connections:
            return

        if user_id not in self._connections[conversation_id]:
            return

        state = self._connections[conversation_id][user_id]
        await self._close_connection(state, reason="client_disconnect")

        # 清理连接记录
        del self._connections[conversation_id][user_id]
        if not self._connections[conversation_id]:
            del self._connections[conversation_id]

        logger.info(
            f"WebSocket disconnected: conversation={conversation_id}, user={user_id}"
        )

    async def _close_connection(self, state: ConnectionState, reason: str) -> None:
        """关闭单个连接"""
        state.is_alive = False

        # 取消心跳任务
        if state.heartbeat_task:
            state.heartbeat_task.cancel()
            try:
                await state.heartbeat_task
            except asyncio.CancelledError:
                pass

        # 关闭WebSocket
        try:
            await state.websocket.close(code=1000, reason=reason)
        except Exception as e:
            logger.debug(f"Error closing websocket: {e}")

    async def send_json(
        self,
        conversation_id: str,
        user_id: str,
        data: Dict[str, Any],
    ) -> bool:
        """发送JSON消息到指定客户端"""
        if conversation_id not in self._connections:
            return False

        if user_id not in self._connections[conversation_id]:
            return False

        state = self._connections[conversation_id][user_id]
        if not state.is_alive:
            return False

        try:
            await state.websocket.send_json(data)
            state.last_activity = time.time()
            return True
        except Exception as e:
            logger.warning(f"Failed to send message: {e}")
            await self.disconnect(conversation_id, user_id)
            return False

    async def send_text(
        self,
        conversation_id: str,
        user_id: str,
        text: str,
    ) -> bool:
        """发送纯文本消息到指定客户端"""
        if conversation_id not in self._connections:
            return False

        if user_id not in self._connections[conversation_id]:
            return False

        state = self._connections[conversation_id][user_id]
        if not state.is_alive:
            return False

        try:
            await state.websocket.send_text(text)
            state.last_activity = time.time()
            return True
        except Exception as e:
            logger.warning(f"Failed to send text: {e}")
            await self.disconnect(conversation_id, user_id)
            return False

    async def broadcast(
        self,
        conversation_id: str,
        data: Dict[str, Any],
        exclude_user: Optional[str] = None,
    ) -> int:
        """广播消息给对话中的所有连接"""
        if conversation_id not in self._connections:
            return 0

        sent_count = 0
        for user_id, state in list(self._connections[conversation_id].items()):
            if exclude_user and user_id == exclude_user:
                continue

            if await self.send_json(conversation_id, user_id, data):
                sent_count += 1

        return sent_count

    def handle_pong(self, conversation_id: str, user_id: str) -> None:
        """处理客户端的pong响应"""
        if conversation_id not in self._connections:
            return

        if user_id not in self._connections[conversation_id]:
            return

        state = self._connections[conversation_id][user_id]
        state.last_pong = time.time()

        # 通知等待中的ping
        pong_key = f"{conversation_id}:{user_id}"
        if pong_key in self._pending_pongs:
            self._pending_pongs[pong_key].set()

    async def _heartbeat_loop(self, state: ConnectionState) -> None:
        """心跳循环：每3秒发送ping，等待5秒内的pong响应"""
        try:
            while state.is_alive:
                await asyncio.sleep(self.heartbeat_interval)

                if not state.is_alive:
                    break

                # 检查空闲超时
                idle_time = time.time() - state.last_activity
                if idle_time > self.idle_timeout:
                    logger.info(
                        f"Connection idle timeout: "
                        f"conversation={state.conversation_id}, "
                        f"user={state.user_id}"
                    )
                    await self.disconnect(state.conversation_id, state.user_id)
                    break

                # 发送ping
                try:
                    await state.websocket.send_json(
                        {"type": "ping", "ts": time.time()}
                    )
                except Exception as e:
                    logger.warning(f"Failed to send ping: {e}")
                    await self.disconnect(state.conversation_id, state.user_id)
                    break

                # 等待pong（使用事件机制）
                pong_key = f"{state.conversation_id}:{state.user_id}"
                pong_event = asyncio.Event()
                self._pending_pongs[pong_key] = pong_event

                try:
                    await asyncio.wait_for(
                        pong_event.wait(),
                        timeout=self.ping_timeout,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Ping timeout: conversation={state.conversation_id}, "
                        f"user={state.user_id}"
                    )
                    await self.disconnect(state.conversation_id, state.user_id)
                    break
                finally:
                    self._pending_pongs.pop(pong_key, None)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}")

    def get_connection_count(self, conversation_id: Optional[str] = None) -> int:
        """获取连接数量"""
        if conversation_id:
            return len(self._connections.get(conversation_id, {}))
        return sum(len(users) for users in self._connections.values())

    def is_connected(self, conversation_id: str, user_id: str) -> bool:
        """检查用户是否已连接"""
        if conversation_id not in self._connections:
            return False
        if user_id not in self._connections[conversation_id]:
            return False
        return self._connections[conversation_id][user_id].is_alive


# 全局连接管理器实例
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """获取全局连接管理器"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager
