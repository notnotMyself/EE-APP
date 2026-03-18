"""
对话API - Conversation endpoints

提供对话管理的REST API：
- GET /conversations/{agent_id} - 获取或创建与Agent的对话
- GET /conversations/{conversation_id}/messages - 获取对话消息
- POST /conversations/{conversation_id}/messages - 发送消息（流式响应）
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from .deps import get_current_user_id

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
    agent_name: Optional[str] = None  # Agent 名称
    agent_role: Optional[str] = None  # Agent role（用于匹配 agent_registry）
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


class ConversationCreate(BaseModel):
    """创建会话请求模型"""

    agent_id: str = Field(..., description="Agent ID (UUID 或 role string)")
    title: Optional[str] = Field(None, max_length=255, description="会话标题")


class ConversationTitleUpdate(BaseModel):
    """更新会话标题请求模型"""

    title: str = Field(..., min_length=1, max_length=255, description="新标题")


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
    user_id: str = Depends(get_current_user_id),
):
    """
    获取与特定AI员工的对话（如果不存在则创建）

    需要认证：需要在Header中提供有效的Bearer Token
    user_id将从JWT token中自动提取

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
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100, description="消息数量限制"),
    offset: int = Query(0, ge=0, description="偏移量（用于分页）"),
):
    """
    获取对话的所有消息（包括简报卡片）

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该对话是否属于当前用户

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
    user_id: str = Depends(get_current_user_id),
):
    """
    发送消息并流式返回AI响应（Server-Sent Events）

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该对话是否属于当前用户

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


@router.get("", response_model=List[ConversationResponse])
async def list_user_conversations(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=100, description="对话数量限制"),
):
    """
    获取当前用户的所有对话列表

    需要认证：需要在Header中提供有效的Bearer Token
    user_id将从JWT token中自动提取

    **排序**: 按last_message_at降序（最近活跃的在前）

    Returns:
        对话列表（包含 agent_name 和 agent_role）
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        conversations = await conversation_service.list_user_conversations(
            user_id=user_id, limit=limit
        )

        # 获取所有 agent_id 并查询 agent 信息
        agent_ids = list({conv["agent_id"] for conv in conversations})
        agent_map = {}
        
        if agent_ids and conversation_service.supabase:
            try:
                result = conversation_service.supabase.table("agents").select(
                    "id, name, role"
                ).in_("id", agent_ids).execute()
                
                if result.data:
                    for agent in result.data:
                        agent_map[agent["id"]] = {
                            "name": agent.get("name"),
                            "role": agent.get("role"),
                        }
            except Exception as e:
                logger.warning(f"Failed to fetch agent info: {e}")

        # 构建带有 agent 信息的响应
        result = []
        for conv in conversations:
            agent_info = agent_map.get(conv["agent_id"], {})
            result.append(ConversationResponse(
                id=conv["id"],
                user_id=conv["user_id"],
                agent_id=conv["agent_id"],
                agent_name=agent_info.get("name"),
                agent_role=agent_info.get("role"),
                title=conv.get("title"),
                status=conv["status"],
                started_at=conv["started_at"],
                last_message_at=conv.get("last_message_at"),
            ))

        return result

    except Exception as e:
        logger.error(f"Error listing conversations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_in: ConversationCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    创建新会话（多会话模式）

    需要认证：需要在Header中提供有效的Bearer Token

    **多会话模式**: 允许用户与同一Agent创建多个会话
    - 每次调用都会创建新的会话
    - 不再检查 UNIQUE(user_id, agent_id) 约束
    - 可指定自定义标题，否则自动生成

    Returns:
        新创建的会话信息
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        # 支持 role string，自动转换为 UUID
        try:
            agent_uuid = get_agent_uuid(conversation_in.agent_id)
            logger.info(
                f"Creating conversation with agent '{conversation_in.agent_id}' (UUID: {agent_uuid})"
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # 验证Agent存在且激活
        if conversation_service.supabase:
            try:
                agent_result = (
                    conversation_service.supabase.table("agents")
                    .select("id, name, is_active")
                    .eq("id", agent_uuid)
                    .execute()
                )

                if not agent_result.data:
                    raise HTTPException(status_code=404, detail="Agent not found")

                agent = agent_result.data[0]
                if not agent.get("is_active", True):
                    raise HTTPException(status_code=400, detail="Agent is not active")
            except HTTPException:
                raise
            except Exception as e:
                logger.warning(f"Failed to validate agent: {e}")

        # 生成默认标题
        title = conversation_in.title or f"New Conversation"

        # 创建新会话（不再使用 get_or_create）
        conversation_id = (
            await conversation_service.conversation_model.create_conversation(
                user_id=user_id, agent_id=agent_uuid, title=title
            )
        )

        # 获取创建的会话详情
        conversation = await conversation_service.conversation_model.get_by_id(
            conversation_id
        )

        if not conversation:
            raise HTTPException(
                status_code=500, detail="Failed to create conversation"
            )

        return ConversationResponse(**conversation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/conversations", response_model=List[ConversationResponse])
async def list_agent_conversations(
    agent_id: str,
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=100, description="对话数量限制"),
    status: Optional[str] = Query("active", description="对话状态过滤"),
):
    """
    获取用户与特定Agent的所有会话列表（多会话模式）

    需要认证：需要在Header中提供有效的Bearer Token

    **排序**: 按last_message_at降序（最近活跃的在前）
    **过滤**: 支持按状态过滤（active/archived/closed）

    Returns:
        与特定Agent的所有会话列表
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        # 支持 role string，自动转换为 UUID
        try:
            agent_uuid = get_agent_uuid(agent_id)
            logger.info(
                f"Listing conversations for agent '{agent_id}' (UUID: {agent_uuid})"
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # 查询该用户与该Agent的所有会话
        conversations = await conversation_service.list_agent_conversations(
            user_id=user_id, agent_id=agent_uuid, limit=limit, status=status
        )

        # 获取Agent信息
        agent_info = {}
        if conversation_service.supabase:
            try:
                agent_result = (
                    conversation_service.supabase.table("agents")
                    .select("id, name, role")
                    .eq("id", agent_uuid)
                    .execute()
                )

                if agent_result.data:
                    agent = agent_result.data[0]
                    agent_info = {
                        "name": agent.get("name"),
                        "role": agent.get("role"),
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch agent info: {e}")

        # 构建响应
        result = []
        for conv in conversations:
            result.append(
                ConversationResponse(
                    id=conv["id"],
                    user_id=conv["user_id"],
                    agent_id=conv["agent_id"],
                    agent_name=agent_info.get("name"),
                    agent_role=agent_info.get("role"),
                    title=conv.get("title"),
                    status=conv["status"],
                    started_at=conv["started_at"],
                    last_message_at=conv.get("last_message_at"),
                )
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error listing agent conversations for user {user_id}, agent {agent_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a conversation and all its messages.

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该对话是否属于当前用户

    Returns:
        204 No Content on success
    """
    if not conversation_service:
        raise HTTPException(
            status_code=500, detail="Conversation service not initialized"
        )

    try:
        # Verify conversation exists and belongs to user
        conversation = await conversation_service.conversation_model.get_by_id(
            conversation_id
        )

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation["user_id"] != user_id:
            raise HTTPException(
                status_code=403, detail="Access denied to this conversation"
            )

        # Delete messages first (foreign key constraint)
        await conversation_service.message_model.delete_by_conversation(conversation_id)

        # Delete conversation
        await conversation_service.conversation_model.delete(conversation_id)

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{conversation_id}/title", response_model=ConversationResponse)
async def update_conversation_title(
    conversation_id: str,
    title_update: ConversationTitleUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """
    更新会话标题

    需要认证：需要在Header中提供有效的Bearer Token
    会验证该对话是否属于当前用户

    用户可自定义会话标题以便区分不同会话

    Returns:
        更新后的会话信息
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

        # 更新标题
        updated = await conversation_service.conversation_model.update_title(
            conversation_id=conversation_id, title=title_update.title
        )

        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update title")

        return ConversationResponse(**updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation title {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

