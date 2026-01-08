"""
对话API - Conversation endpoints

提供对话管理的REST API：
- GET /conversations/{agent_id} - 获取或创建与Agent的对话
- GET /conversations/{conversation_id}/messages - 获取对话消息
- POST /conversations/{conversation_id}/messages - 发送消息（流式响应）
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from agent_mapping import get_agent_uuid, is_valid_uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

# 全局conversation_service引用，由main.py注入
conversation_service = None


def set_conversation_service(service):
    """设置conversation服务实例"""
    global conversation_service
    conversation_service = service


# ============================================
# 数据模型 (Pydantic Schemas)
# ============================================


class ConversationResponse(BaseModel):
    """对话响应模型"""

    id: str
    user_id: str
    agent_id: str
    title: Optional[str] = None
    status: str
    started_at: str
    last_message_at: Optional[str] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """消息响应模型"""

    id: str
    conversation_id: str
    role: str  # 'user', 'assistant', 'system'
    content_type: str  # 'text', 'briefing_card'
    content: str  # 对于briefing_card是JSON字符串
    briefing_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """发送消息请求模型"""

    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")


class MessageListResponse(BaseModel):
    """消息列表响应"""

    messages: List[MessageResponse]
    total: int
    conversation_id: str


# ============================================
# API端点
# ============================================


@router.get("/{agent_id}", response_model=ConversationResponse)
async def get_conversation_with_agent(
    agent_id: str,
    user_id: str = Query(..., description="用户ID"),
):
    """
    获取与特定AI员工的对话（如果不存在则创建）

    **核心变化**: 通过agent_id而非conversation_id获取对话
    - 每个用户+Agent对只有一个持久化对话
    - 首次访问时自动创建对话
    - 后续访问复用同一对话

    **兼容性**: agent_id 可以是 role string (如 "dev_efficiency_analyst") 或 UUID

    Returns:
        对话信息（包含conversation_id）
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        # 🔧 新增：支持 role string，自动转换为 UUID
        try:
            agent_uuid = get_agent_uuid(agent_id)
            logger.info(f"Mapped agent '{agent_id}' to UUID: {agent_uuid}")
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # 获取或创建对话（使用 UUID）
        conversation_id = await conversation_service.get_or_create_conversation(
            user_id=user_id, agent_id=agent_uuid
        )

        # 获取对话详情
        conversation = await conversation_service.conversation_model.get_by_id(
            conversation_id
        )

        if not conversation:
            raise HTTPException(
                status_code=500, detail="Failed to create or retrieve conversation"
            )

        return ConversationResponse(**conversation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation with agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def list_messages(
    conversation_id: str,
    user_id: str = Query(..., description="用户ID（用于权限验证）"),
    limit: int = Query(50, ge=1, le=100, description="消息数量限制"),
    offset: int = Query(0, ge=0, description="偏移量（用于分页）"),
):
    """
    获取对话的所有消息（包括简报卡片）

    **消息类型**:
    - `content_type='text'`: 普通文本消息
    - `content_type='briefing_card'`: 简报卡片（content为JSON字符串）

    **消息顺序**: 按created_at升序（时间线顺序）

    Returns:
        消息列表，包含文本消息和简报卡片
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        # 验证对话存在且用户有权访问
        conversation = await conversation_service.conversation_model.get_by_id(
            conversation_id
        )

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation["user_id"] != user_id:
            raise HTTPException(
                status_code=403, detail="Access denied to this conversation"
            )

        # 获取消息列表
        messages = await conversation_service.message_model.list_by_conversation(
            conversation_id=conversation_id, limit=limit, offset=offset
        )

        # 计算总数（简化实现，实际生产环境应用分页时单独查询count）
        total = len(messages)

        return MessageListResponse(
            messages=[MessageResponse(**msg) for msg in messages],
            total=total,
            conversation_id=conversation_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing messages for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/messages")
async def send_message_stream(
    conversation_id: str,
    message_data: MessageCreate,
    user_id: str = Query(..., description="用户ID（用于权限验证）"),
):
    """
    发送消息并流式返回AI响应（Server-Sent Events）

    **工作流程**:
    1. 保存用户消息到数据库
    2. 获取对话上下文（最近20条消息，包括简报卡片）
    3. 构建AI prompt（包含简报信息）
    4. 流式调用Agent SDK
    5. 保存AI响应到数据库
    6. 更新对话时间戳

    **响应格式**: Server-Sent Events (SSE)
    - 每个chunk格式: `data: {text_chunk}\\n\\n`
    - Content-Type: text/event-stream

    Returns:
        流式AI响应
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        # 流式生成器
        async def stream_generator():
            try:
                async for chunk in conversation_service.send_message(
                    conversation_id=conversation_id,
                    user_message=message_data.content,
                    user_id=user_id,
                ):
                    # SSE格式: data: {chunk}\n\n
                    yield f"data: {chunk}\n\n"

                # 发送结束标记
                yield "data: [DONE]\n\n"

            except ValueError as e:
                # 权限或验证错误
                logger.warning(f"Validation error in send_message: {e}")
                yield f"data: [ERROR] {str(e)}\n\n"
            except Exception as e:
                # 其他错误
                logger.error(f"Error in send_message stream: {e}")
                yield f"data: [ERROR] Internal server error\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用nginx缓冲
            },
        )

    except Exception as e:
        logger.error(f"Error setting up message stream for {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[ConversationResponse])
async def list_user_conversations(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="对话数量限制"),
):
    """
    获取用户的所有对话列表

    **排序**: 按last_message_at降序（最近活跃的在前）

    Returns:
        对话列表
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        conversations = await conversation_service.list_user_conversations(
            user_id=user_id, limit=limit
        )

        return [ConversationResponse(**conv) for conv in conversations]

    except Exception as e:
        logger.error(f"Error listing conversations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
