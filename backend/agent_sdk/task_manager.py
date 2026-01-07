"""
Task Manager

管理 Agent 任务的创建、调度和状态跟踪。
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .agent_sdk_service import AgentSDKService
from .config import AgentSDKConfig, get_config
from .exceptions import (
    AgentNotFoundError,
    TaskNotFoundError,
    TaskExecutionError,
)

logger = logging.getLogger(__name__)


class TaskManager:
    """任务管理器"""

    def __init__(
        self,
        agent_service: Optional[AgentSDKService] = None,
        supabase_client: Optional[Any] = None,
        config: Optional[AgentSDKConfig] = None,
    ):
        self.config = config or get_config()
        self.supabase = supabase_client
        self.agent_service = agent_service or AgentSDKService(
            config=self.config,
            supabase_client=supabase_client,
        )

        # 跟踪正在运行的任务
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def create_task(
        self,
        conversation_id: str,
        agent_role: str,
        user_message: str,
        mcp_servers: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        创建任务并异步执行

        Args:
            conversation_id: 对话 ID
            agent_role: Agent 角色
            user_message: 用户消息
            mcp_servers: MCP 服务器列表

        Returns:
            任务信息
        """
        # 验证 Agent 角色
        role_config = self.config.get_agent_role(agent_role)
        if not role_config:
            raise AgentNotFoundError(agent_role)

        # 1. 保存用户消息
        await self._save_user_message(conversation_id, user_message)

        # 2. 创建任务记录
        task_id = str(uuid.uuid4())
        task_data = {
            "id": task_id,
            "conversation_id": conversation_id,
            "agent_role": agent_role,
            "prompt": user_message,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

        if self.supabase:
            result = await self.supabase.table("tasks").insert(task_data).execute()
            task_id = result.data[0]["id"]
            task_data = result.data[0]

        logger.info(f"Created task {task_id} for agent {agent_role}")

        # 3. 异步执行任务（不阻塞）
        async_task = asyncio.create_task(
            self._execute_task_wrapper(
                task_id=task_id,
                agent_role=agent_role,
                prompt=user_message,
                conversation_id=conversation_id,
                mcp_servers=mcp_servers,
            )
        )

        self._running_tasks[task_id] = async_task

        # 清理完成的任务
        async_task.add_done_callback(
            lambda t: self._running_tasks.pop(task_id, None)
        )

        return {
            "task_id": task_id,
            "conversation_id": conversation_id,
            "agent_role": agent_role,
            "status": "pending",
            "created_at": task_data.get("created_at"),
        }

    async def _execute_task_wrapper(
        self,
        task_id: str,
        agent_role: str,
        prompt: str,
        conversation_id: str,
        mcp_servers: Optional[List[Any]] = None,
    ) -> None:
        """任务执行包装器（处理异常）"""
        try:
            await self.agent_service.execute_agent_task(
                task_id=task_id,
                agent_role=agent_role,
                prompt=prompt,
                conversation_id=conversation_id,
                mcp_servers=mcp_servers,
            )
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            # 异常已在 execute_agent_task 中处理，这里只记录日志

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """获取任务信息"""
        if not self.supabase:
            raise TaskNotFoundError(task_id)

        result = await self.supabase.table("tasks").select("*").eq(
            "id", task_id
        ).single().execute()

        if not result.data:
            raise TaskNotFoundError(task_id)

        return result.data

    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """取消任务"""
        # 标记为取消
        self.agent_service.cancel_task(task_id)

        # 取消 asyncio 任务
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()

        # 更新数据库
        if self.supabase:
            await self.supabase.table("tasks").update({
                "status": "cancelled",
                "completed_at": datetime.utcnow().isoformat(),
            }).eq("id", task_id).execute()

        logger.info(f"Task {task_id} cancelled")

        return {
            "task_id": task_id,
            "status": "cancelled",
            "cancelled_at": datetime.utcnow().isoformat(),
        }

    async def list_tasks(
        self,
        conversation_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """列出任务"""
        if not self.supabase:
            return []

        query = self.supabase.table("tasks").select("*")

        if conversation_id:
            query = query.eq("conversation_id", conversation_id)

        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True).limit(limit)

        result = await query.execute()
        return result.data

    async def get_running_task(
        self,
        conversation_id: str,
    ) -> Optional[Dict[str, Any]]:
        """获取对话中正在运行的任务"""
        if not self.supabase:
            return None

        result = await self.supabase.table("tasks").select("*").eq(
            "conversation_id", conversation_id
        ).eq("status", "running").single().execute()

        return result.data if result.data else None

    def is_task_running(self, task_id: str) -> bool:
        """检查任务是否正在运行"""
        return task_id in self._running_tasks

    def get_running_task_count(self) -> int:
        """获取正在运行的任务数量"""
        return len(self._running_tasks)

    # ==================== 消息操作 ====================

    async def _save_user_message(
        self,
        conversation_id: str,
        content: str,
    ) -> str:
        """保存用户消息"""
        if not self.supabase:
            return str(uuid.uuid4())

        result = await self.supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "user",
            "content": content,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        return result.data[0]["id"]

    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        before: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取对话消息"""
        if not self.supabase:
            return {"messages": [], "has_more": False}

        query = self.supabase.table("messages").select("*").eq(
            "conversation_id", conversation_id
        ).order("created_at", desc=True).limit(limit)

        if before:
            # 获取 before 消息的时间戳
            before_msg = await self.supabase.table("messages").select(
                "created_at"
            ).eq("id", before).single().execute()

            if before_msg.data:
                query = query.lt("created_at", before_msg.data["created_at"])

        result = await query.execute()
        messages = list(reversed(result.data))

        return {
            "messages": messages,
            "has_more": len(result.data) == limit,
            "next_cursor": messages[0]["id"] if messages else None,
        }

    async def get_message_by_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """根据任务 ID 获取消息"""
        if not self.supabase:
            return None

        result = await self.supabase.table("messages").select("*").eq(
            "task_id", task_id
        ).eq("role", "assistant").single().execute()

        return result.data if result.data else None
