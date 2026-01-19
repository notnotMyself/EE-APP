"""
WebSocket Conversation API

基于WebSocket的实时对话端点，替代SSE提供更好的双向通信体验。
参考 claudecodeui 的 WebSocket 实现模式。

消息协议：
- 客户端 -> 服务端:
  {"type": "message", "content": "用户消息"}
  {"type": "pong"}

- 服务端 -> 客户端:
  {"type": "text_chunk", "content": "...", "ts": 1234567890}
  {"type": "tool_use", "tool_name": "...", "tool_id": "...", "tool_input": {...}}
  {"type": "tool_result", "tool_id": "...", "result": "...", "is_error": false}
  {"type": "done", "message_id": "..."}
  {"type": "ping", "ts": 1234567890}
  {"type": "error", "content": "..."}
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from config import get_timeout_config
from services.websocket_manager import ConnectionManager, get_connection_manager
from services.websocket_writer import MessageType, WebSocketWriter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# 全局服务引用，由main.py注入
conversation_service = None
supabase_client = None


def set_websocket_services(conv_service, supabase):
    """设置WebSocket服务依赖"""
    global conversation_service, supabase_client
    conversation_service = conv_service
    supabase_client = supabase


async def verify_token(token: str) -> Optional[str]:
    """验证JWT Token并返回用户ID

    优先使用 Supabase 验证，如果 Supabase 不可用则直接解码 JWT。
    """
    # 方式1：使用 Supabase 验证
    if supabase_client:
        try:
            user_response = supabase_client.auth.get_user(token)
            if user_response.user:
                return str(user_response.user.id)
        except Exception as e:
            logger.warning(f"Supabase token verification failed: {e}")

    # 方式2：直接解码 JWT（用于 Supabase 不可用时）
    try:
        import base64
        import json as json_module

        # JWT 格式: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            logger.warning("Invalid JWT format")
            return None

        # 解码 payload（第二部分）
        payload = parts[1]
        # 添加 padding
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding

        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json_module.loads(decoded)

        # 从 sub 字段获取用户ID
        user_id = payload_data.get('sub')
        if user_id:
            logger.info(f"JWT decoded, user_id: {user_id}")
            return user_id

        logger.warning("No 'sub' field in JWT payload")
    except Exception as e:
        logger.warning(f"JWT decode failed: {e}")

    return None


@router.websocket("/api/v1/conversations/{conversation_id}/ws")
async def conversation_websocket(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(..., description="JWT Token for authentication"),
):
    """
    WebSocket端点用于实时对话

    连接流程：
    1. 客户端连接时提供JWT Token作为查询参数
    2. 服务端验证Token并接受连接
    3. 服务端开始发送心跳ping（每3秒）
    4. 客户端发送消息，服务端流式返回响应

    消息类型：
    - message: 用户发送消息
    - pong: 客户端响应心跳
    """
    # 先接受 WebSocket 连接（必须在发送任何消息之前）
    await websocket.accept()

    # 验证Token
    user_id = await verify_token(token)
    if not user_id:
        await websocket.send_json({"type": "error", "content": "Invalid or expired token"})
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # 获取连接管理器
    manager = get_connection_manager()

    # 验证对话存在且属于用户（仅当服务可用时）
    if conversation_service and supabase_client:
        try:
            conversation = await conversation_service.get_conversation(conversation_id)
            if not conversation:
                await websocket.send_json({"type": "error", "content": "Conversation not found"})
                await websocket.close(code=4004, reason="Conversation not found")
                return
            if conversation.get("user_id") != user_id:
                await websocket.send_json({"type": "error", "content": "Access denied"})
                await websocket.close(code=4003, reason="Access denied")
                return
        except Exception as e:
            logger.warning(f"Failed to verify conversation (continuing anyway): {e}")
            # 继续连接，不阻塞（开发环境）

    # 连接WebSocket
    try:
        connection_state = await manager.connect(
            websocket=websocket,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "conversation_id": conversation_id,
            "ts": asyncio.get_event_loop().time(),
        })

        # 消息处理循环
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)

                msg_type = message.get("type")

                if msg_type == "pong":
                    # 处理心跳响应
                    manager.handle_pong(conversation_id, user_id)

                elif msg_type == "message":
                    # 处理用户消息
                    content = message.get("content", "").strip()
                    if content:
                        await handle_user_message(
                            websocket=websocket,
                            manager=manager,
                            conversation_id=conversation_id,
                            user_id=user_id,
                            content=content,
                        )

                else:
                    logger.warning(f"Unknown message type: {msg_type}")

            except json.JSONDecodeError:
                logger.warning("Received invalid JSON message")
                await websocket.send_json({
                    "type": "error",
                    "content": "Invalid JSON format",
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {conversation_id}/{user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(conversation_id, user_id)


async def handle_user_message(
    websocket: WebSocket,
    manager: ConnectionManager,
    conversation_id: str,
    user_id: str,
    content: str,
) -> None:
    """处理用户消息并流式返回响应"""
    if not conversation_service:
        await websocket.send_json({
            "type": "error",
            "content": "Service not available",
        })
        return

    # 创建WebSocket写入器
    writer = WebSocketWriter(
        websocket=websocket,
        connection_manager=manager,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    try:
        # 调用对话服务的WebSocket版本
        await conversation_service.send_message_ws(
            conversation_id=conversation_id,
            user_message=content,
            user_id=user_id,
            ws_writer=writer,
        )

        # 发送完成消息
        await writer.write_done()

    except asyncio.CancelledError:
        logger.info(f"Message handling cancelled: {conversation_id}")
        await writer.write_error("Request cancelled")
        raise
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await writer.write_error(str(e))


@router.get("/api/v1/ws/health")
async def websocket_health():
    """WebSocket服务健康检查"""
    manager = get_connection_manager()
    config = get_timeout_config()

    return {
        "status": "healthy",
        "active_connections": manager.get_connection_count(),
        "config": {
            "heartbeat_interval": config.WS_HEARTBEAT_INTERVAL,
            "ping_timeout": config.WS_PING_TIMEOUT,
            "idle_timeout": config.WS_IDLE_TIMEOUT,
        },
    }
