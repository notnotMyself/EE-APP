"""
WebSocket Writer Adapter

适配Agent SDK流式输出到WebSocket连接。
参考 claudecodeui 的 WebSocketWriter 模式。
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

from .websocket_manager import ConnectionManager

logger = logging.getLogger(__name__)
_LOG_WS_PAYLOAD = bool(int(__import__("os").getenv("WS_LOG_PAYLOAD", "0")))
_LOG_WS_SUMMARY = bool(int(__import__("os").getenv("WS_LOG_SUMMARY", "0")))


@dataclass
class WSMessage:
    """WebSocket消息格式"""

    type: str  # text_chunk, tool_use, tool_result, error, done, ping, pong
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type, "ts": self.timestamp}
        if self.content is not None:
            result["content"] = self.content
        if self.metadata is not None:
            result.update(self.metadata)
        return result


class MessageType:
    """消息类型常量"""

    TEXT_CHUNK = "text_chunk"  # 流式文本内容
    TOOL_USE = "tool_use"  # 工具调用开始
    TOOL_RESULT = "tool_result"  # 工具执行结果
    TOOL_PROGRESS = "tool_progress"  # 工具执行进度（新增：让用户看到长时间运行工具的进度）
    TASK_START = "task_start"  # 任务开始
    TASK_PROGRESS = "task_progress"  # 任务进度
    BRIEFING_CREATED = "briefing_created"  # 简报创建
    ERROR = "error"  # 错误
    DONE = "done"  # 完成
    PING = "ping"  # 心跳ping
    PONG = "pong"  # 心跳pong


class WebSocketWriter:
    """WebSocket写入器

    适配Agent SDK的流式输出到WebSocket连接。
    支持：
    - 文本chunk缓冲和批量发送
    - 自适应刷新间隔（首次快，后续稳定）
    - 工具调用消息
    - 错误处理
    """

    def __init__(
        self,
        websocket: WebSocket,
        connection_manager: ConnectionManager,
        conversation_id: str,
        user_id: str,
        initial_flush_interval: float = 0.01,  # 10ms首次刷新 (优化: 从50ms减少)
        steady_flush_interval: float = 0.08,  # 80ms稳定刷新 (优化: 从100ms减少)
        max_buffer_size: int = 15,  # 15字符触发刷新 (优化: 从30减少)
    ):
        self.websocket = websocket
        self.manager = connection_manager
        self.conversation_id = conversation_id
        self.user_id = user_id

        self._initial_flush_interval = initial_flush_interval
        self._steady_flush_interval = steady_flush_interval
        self._max_buffer_size = max_buffer_size

        self._buffer: List[str] = []
        self._flush_count = 0
        self._last_flush_time = time.time()
        self._flush_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

        # 累积的完整内容（用于保存到数据库）
        self._accumulated_content = ""
        
        # 是否是首次输出（用于TTFT优化）
        self._is_first_output = True

    @property
    def accumulated_content(self) -> str:
        """获取累积的完整内容"""
        return self._accumulated_content

    async def write_text_chunk(self, content: str) -> None:
        """写入文本chunk（带缓冲）
        
        TTFT优化：首次输出立即刷新，让用户尽快看到第一个字符
        """
        async with self._lock:
            self._buffer.append(content)
            self._accumulated_content += content

            # 首次输出立即刷新（TTFT优化）
            if self._is_first_output:
                self._is_first_output = False
                await self._flush_buffer()
                return

            # 计算当前应该使用的刷新间隔
            flush_interval = (
                self._initial_flush_interval
                if self._flush_count == 0
                else self._steady_flush_interval
            )

            # 检查是否应该刷新
            current_time = time.time()
            buffer_content = "".join(self._buffer)
            time_elapsed = current_time - self._last_flush_time

            should_flush = (
                time_elapsed >= flush_interval
                or len(buffer_content) >= self._max_buffer_size
            )

            if should_flush:
                await self._flush_buffer()
            elif self._flush_task is None:
                # 安排延迟刷新
                self._flush_task = asyncio.create_task(
                    self._delayed_flush(flush_interval)
                )

    async def _flush_buffer(self) -> None:
        """刷新缓冲区"""
        if self._flush_task:
            self._flush_task.cancel()
            self._flush_task = None

        if not self._buffer:
            return

        content = "".join(self._buffer)
        self._buffer.clear()

        # 发送消息
        message = WSMessage(type=MessageType.TEXT_CHUNK, content=content)
        try:
            if _LOG_WS_SUMMARY:
                logger.info(
                    "WS send text_chunk: conversation=%s user=%s len=%s",
                    self.conversation_id,
                    self.user_id,
                    len(content),
                )
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send text_chunk: conversation=%s user=%s len=%s%s",
                    self.conversation_id,
                    self.user_id,
                    len(content),
                    f" content={content!r}" if _LOG_WS_PAYLOAD else "",
                )
            # 通过 ConnectionManager 发送，便于统一处理断连/状态
            ok = await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
            if not ok:
                raise RuntimeError("WebSocket not connected")
            self._flush_count += 1
            self._last_flush_time = time.time()
        except Exception as e:
            logger.error(f"Failed to send text chunk: {e}")
            raise

    async def _delayed_flush(self, delay: float) -> None:
        """延迟刷新"""
        try:
            await asyncio.sleep(delay)
            async with self._lock:
                await self._flush_buffer()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Delayed flush error: {e}")
        finally:
            self._flush_task = None

    async def write_tool_use(
        self,
        tool_name: str,
        tool_id: str,
        tool_input: Optional[Dict[str, Any]] = None,
    ) -> None:
        """写入工具调用消息"""
        # 先刷新缓冲区中的文本
        async with self._lock:
            await self._flush_buffer()

        message = WSMessage(
            type=MessageType.TOOL_USE,
            metadata={
                "tool_name": tool_name,
                "tool_id": tool_id,
                "tool_input": tool_input,
            },
        )
        try:
            if _LOG_WS_SUMMARY:
                logger.info(
                    "WS send tool_use: conversation=%s user=%s tool_name=%s tool_id=%s",
                    self.conversation_id,
                    self.user_id,
                    tool_name,
                    tool_id,
                )
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send tool_use: conversation=%s user=%s tool_name=%s tool_id=%s",
                    self.conversation_id,
                    self.user_id,
                    tool_name,
                    tool_id,
                )
            ok = await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
            if not ok:
                raise RuntimeError("WebSocket not connected")
        except Exception as e:
            logger.error(f"Failed to send tool_use: {e}")
            raise

    async def write_tool_result(
        self,
        tool_id: str,
        result: Any,
        is_error: bool = False,
    ) -> None:
        """写入工具结果消息"""
        message = WSMessage(
            type=MessageType.TOOL_RESULT,
            metadata={
                "tool_id": tool_id,
                "result": result,
                "is_error": is_error,
            },
        )
        try:
            if _LOG_WS_SUMMARY:
                logger.info(
                    "WS send tool_result: conversation=%s user=%s tool_id=%s is_error=%s",
                    self.conversation_id,
                    self.user_id,
                    tool_id,
                    is_error,
                )
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send tool_result: conversation=%s user=%s tool_id=%s is_error=%s",
                    self.conversation_id,
                    self.user_id,
                    tool_id,
                    is_error,
                )
            ok = await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
            if not ok:
                raise RuntimeError("WebSocket not connected")
        except Exception as e:
            logger.error(f"Failed to send tool_result: {e}")
            raise

    async def write_tool_progress(
        self,
        tool_name: str,
        tool_id: str,
        progress: float,  # 0.0 - 1.0
        status: str = "executing",  # executing, writing, completed
        message_text: Optional[str] = None,
        file_path: Optional[str] = None,  # 对于 Write 工具，显示文件路径
    ) -> None:
        """写入工具执行进度消息（新增：让用户看到长时间运行工具的进度）

        参考 claudecodeui 的设计，在工具执行期间向前端推送进度更新。

        Args:
            tool_name: 工具名称（如 Write, Bash）
            tool_id: 工具调用 ID
            progress: 进度 0.0-1.0
            status: 状态描述
            message_text: 可选的消息文本
            file_path: 对于文件操作，显示文件路径
        """
        message = WSMessage(
            type=MessageType.TOOL_PROGRESS,
            content=message_text,
            metadata={
                "tool_name": tool_name,
                "tool_id": tool_id,
                "progress": progress,
                "status": status,
                "file_path": file_path,
            },
        )
        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send tool_progress: conversation=%s user=%s tool=%s progress=%.0f%%",
                    self.conversation_id,
                    self.user_id,
                    tool_name,
                    progress * 100,
                )
            ok = await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
            if not ok:
                raise RuntimeError("WebSocket not connected")
        except Exception as e:
            logger.error(f"Failed to send tool_progress: {e}")
            # 进度消息失败不应中断执行
            pass

    async def write_task_start(
        self,
        task_type: str,
        task_id: Optional[str] = None,
    ) -> None:
        """写入任务开始消息"""
        message = WSMessage(
            type=MessageType.TASK_START,
            metadata={
                "task_type": task_type,
                "task_id": task_id,
            },
        )
        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send task_start: conversation=%s user=%s task_type=%s task_id=%s",
                    self.conversation_id,
                    self.user_id,
                    task_type,
                    task_id,
                )
            ok = await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
            if not ok:
                raise RuntimeError("WebSocket not connected")
        except Exception as e:
            logger.error(f"Failed to send task_start: {e}")
            raise

    async def write_task_progress(
        self,
        progress: float,  # 0.0 - 1.0
        message_text: Optional[str] = None,
    ) -> None:
        """写入任务进度消息"""
        message = WSMessage(
            type=MessageType.TASK_PROGRESS,
            content=message_text,
            metadata={"progress": progress},
        )
        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send task_progress: conversation=%s user=%s progress=%s%s",
                    self.conversation_id,
                    self.user_id,
                    progress,
                    f" msg={message_text!r}" if (_LOG_WS_PAYLOAD and message_text) else "",
                )
            ok = await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
            if not ok:
                raise RuntimeError("WebSocket not connected")
        except Exception as e:
            logger.error(f"Failed to send task_progress: {e}")
            raise

    async def write_error(self, error_message: str) -> None:
        """写入错误消息"""
        message = WSMessage(type=MessageType.ERROR, content=error_message)
        try:
            if _LOG_WS_SUMMARY:
                logger.info(
                    "WS send error: conversation=%s user=%s len=%s",
                    self.conversation_id,
                    self.user_id,
                    len(error_message),
                )
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send error: conversation=%s user=%s len=%s%s",
                    self.conversation_id,
                    self.user_id,
                    len(error_message),
                    f" error={error_message!r}" if _LOG_WS_PAYLOAD else "",
                )
            # 错误消息尽力发送：如果连接已关闭，避免再次抛异常刷屏
            await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
        except Exception as e:
            logger.error(f"Failed to send error: {e}")
            return

    async def write_done(self, message_id: Optional[str] = None) -> None:
        """写入完成消息"""
        # 先刷新所有缓冲
        async with self._lock:
            await self._flush_buffer()

        message = WSMessage(
            type=MessageType.DONE,
            metadata={"message_id": message_id} if message_id else None,
        )
        try:
            if _LOG_WS_SUMMARY:
                logger.info(
                    "WS send done: conversation=%s user=%s message_id=%s",
                    self.conversation_id,
                    self.user_id,
                    message_id,
                )
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "WS send done: conversation=%s user=%s message_id=%s",
                    self.conversation_id,
                    self.user_id,
                    message_id,
                )
            # done 也是尽力发送：连接关闭时不应抛异常
            await self.manager.send_json(
                self.conversation_id, self.user_id, message.to_dict()
            )
        except Exception as e:
            logger.error(f"Failed to send done: {e}")
            return

    async def finalize(self) -> str:
        """最终化：刷新所有缓冲并返回累积内容"""
        async with self._lock:
            await self._flush_buffer()
        return self._accumulated_content

    async def close(self) -> None:
        """关闭写入器"""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None
