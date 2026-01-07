"""
Conversation API endpoints with Claude integration.
使用 Supabase Client 替代 SQLAlchemy 直连。
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_active_user
from app.crud.crud_conversation_supabase import (
    conversation_supabase as crud_conversation,
    message_supabase as crud_message
)
from app.crud.crud_agent_supabase import agent_supabase as crud_agent
from app.schemas.conversation import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    ConversationWithMessages,
    Message,
    ChatRequest,
    ChatResponse,
    MessageCreate,
)
from app.schemas.user import CurrentUser
from app.services.claude_service import claude_service

router = APIRouter()

def _to_sse_event(data: str) -> str:
    """
    Format text as a single SSE event.
    SSE requires each line to be prefixed with 'data: ' and events separated by a blank line.
    """
    if data is None:
        data = ""
    data = str(data).replace("\r\n", "\n").replace("\r", "\n")
    lines = data.split("\n")
    return "".join(f"data: {line}\n" for line in lines) + "\n"


@router.get("/", response_model=List[Conversation])
async def list_my_conversations(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get current user's conversations.

    - **skip**: Number of items to skip (pagination)
    - **limit**: Maximum number of items to return
    - **status**: Filter by status (active, archived, closed)
    """
    conversations = await crud_conversation.get_user_conversations(
        user_id=current_user.id, skip=skip, limit=limit, status=status
    )
    return conversations


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get conversation with messages.
    """
    conversation = await crud_conversation.get(conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check ownership
    if str(conversation.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    # Get messages
    messages = await crud_message.get_conversation_messages(conversation_id=conversation_id)

    return ConversationWithMessages(
        **conversation,
        messages=messages
    )


@router.post("/", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_in: ConversationCreate,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Create a new conversation with an AI agent.
    """
    # Verify agent exists and is active
    agent = await crud_agent.get(agent_id=conversation_in.agent_id)
    if not agent or not agent.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not active"
        )

    conversation = await crud_conversation.create(
        user_id=current_user.id,
        obj_in=conversation_in.model_dump()
    )
    return conversation


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: UUID,
    conversation_in: ConversationUpdate,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Update conversation metadata.
    """
    conversation = await crud_conversation.get(conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check ownership
    if str(conversation.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this conversation"
        )

    updated = await crud_conversation.update(
        conversation_id=conversation_id,
        obj_in=conversation_in.model_dump(exclude_unset=True)
    )
    return updated


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: UUID,
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Send a message in a conversation and get AI response (non-streaming).

    For streaming responses, use POST /{conversation_id}/messages/stream
    """
    # Get conversation
    conversation = await crud_conversation.get(conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check ownership
    if str(conversation.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    # Get agent
    agent = await crud_agent.get(agent_id=UUID(conversation["agent_id"]))
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Save user message
    user_message = await crud_message.create(
        conversation_id=conversation_id,
        obj_in={"role": "user", "content": chat_request.message}
    )

    # Get conversation history
    recent_messages = await crud_message.get_recent_messages(conversation_id, limit=20)
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in recent_messages[:-1]  # Exclude the message we just added
    ]

    # Build messages for Claude
    messages = claude_service.build_conversation_messages(
        conversation_history, chat_request.message
    )

    # Build system prompt
    system_prompt = claude_service.build_agent_system_prompt(
        agent_name=agent.get("name"),
        agent_role=agent.get("role"),
        agent_description=agent.get("description", ""),
        context=conversation.get("context")
    )

    # Get Claude response
    response_content = await claude_service.chat_completion(
        messages=messages,
        system_prompt=system_prompt
    )

    # Save assistant message
    assistant_message = await crud_message.create(
        conversation_id=conversation_id,
        obj_in={"role": "assistant", "content": response_content}
    )

    # Update conversation last_message_at
    await crud_conversation.update_last_message_time(conversation_id)

    return ChatResponse(
        message_id=UUID(assistant_message["id"]),
        content=response_content,
        conversation_id=conversation_id
    )


@router.post("/{conversation_id}/messages/stream")
async def send_message_stream(
    conversation_id: UUID,
    chat_request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Send a message and stream AI response using Server-Sent Events (SSE).

    Returns: text/event-stream
    """
    # Get conversation
    conversation = await crud_conversation.get(conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check ownership
    if str(conversation.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    # Get agent
    agent = await crud_agent.get(agent_id=UUID(conversation["agent_id"]))
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Save user message
    await crud_message.create(
        conversation_id=conversation_id,
        obj_in={"role": "user", "content": chat_request.message}
    )

    # Get conversation history
    recent_messages = await crud_message.get_recent_messages(conversation_id, limit=20)
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in recent_messages[:-1]
    ]

    # Build messages for Claude
    messages = claude_service.build_conversation_messages(
        conversation_history, chat_request.message
    )

    # Build system prompt
    system_prompt = claude_service.build_agent_system_prompt(
        agent_name=agent.get("name"),
        agent_role=agent.get("role"),
        agent_description=agent.get("description", ""),
        context=conversation.get("context")
    )

    # Stream response
    async def generate():
        full_response = ""
        try:
            async for chunk in claude_service.chat_completion_stream(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=1024,
                temperature=0.3,
            ):
                full_response += chunk
                # Format as SSE
                yield _to_sse_event(chunk)

            # After streaming completes, save the full response
            await crud_message.create(
                conversation_id=conversation_id,
                obj_in={"role": "assistant", "content": full_response}
            )

            # Update conversation timestamp
            await crud_conversation.update_last_message_time(conversation_id)

            # Send completion signal
            yield _to_sse_event("[DONE]")

        except Exception as e:
            # Make gateway errors actionable for frontend
            msg = str(e)
            if "500" in msg and "llm-gateway" in msg:
                msg = "LLM gateway returned 500. Please retry. If it persists, check ANTHROPIC_AUTH_TOKEN / gateway status."
            yield _to_sse_event(f"[ERROR] {msg}")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get all messages in a conversation.
    """
    # Get conversation and check ownership
    conversation = await crud_conversation.get(conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if str(conversation.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )

    messages = await crud_message.get_conversation_messages(conversation_id=conversation_id)
    return messages


@router.post("/{conversation_id}/close", response_model=Conversation)
async def close_conversation(
    conversation_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Close a conversation.
    """
    conversation = await crud_conversation.get(conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if str(conversation.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this conversation"
        )

    closed = await crud_conversation.close(conversation_id)
    return closed
