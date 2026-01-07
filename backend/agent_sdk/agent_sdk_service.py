"""
Agent SDK Service

基于 Claude Agent SDK 的 Agent 服务封装。
处理 Agent 任务执行、消息流式输出、工具调用等。
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    query,
)

from .config import AgentSDKConfig, get_config
from .exceptions import (
    AgentNotFoundError,
    AgentSDKError,
    TaskCancelledError,
    TaskExecutionError,
)

logger = logging.getLogger(__name__)


class MessageBuffer:
    """消息内容缓冲器，用于批量更新数据库"""

    def __init__(
        self,
        flush_callback: Callable[[str], Any],
        flush_interval: float = 0.5,
        max_buffer_size: int = 1000,
    ):
        self.flush_callback = flush_callback
        self.flush_interval = flush_interval
        self.max_buffer_size = max_buffer_size
        self.content = ""
        self.last_flush_time = time.time()
        self.last_flush_length = 0
        self._pending_flush: Optional[asyncio.Task] = None

    async def append(self, text: str) -> None:
        """追加文本到缓冲区"""
        self.content += text

        current_time = time.time()
        should_flush = (
            current_time - self.last_flush_time >= self.flush_interval
            or len(self.content) - self.last_flush_length >= self.max_buffer_size
        )

        if should_flush:
            await self._flush()
        elif self._pending_flush is None:
            # 延迟刷新
            self._pending_flush = asyncio.create_task(self._delayed_flush())

    async def _flush(self) -> None:
        """刷新缓冲区到数据库"""
        if self._pending_flush:
            self._pending_flush.cancel()
            self._pending_flush = None

        try:
            await self.flush_callback(self.content)
            self.last_flush_time = time.time()
            self.last_flush_length = len(self.content)
        except Exception as e:
            logger.error(f"Failed to flush message buffer: {e}")

    async def _delayed_flush(self) -> None:
        """延迟刷新"""
        await asyncio.sleep(self.flush_interval)
        await self._flush()
        self._pending_flush = None

    async def finalize(self) -> str:
        """最终刷新并返回完整内容"""
        await self._flush()
        return self.content


class AgentSDKService:
    """基于 Claude Agent SDK 的 Agent 服务"""

    def __init__(
        self,
        config: Optional[AgentSDKConfig] = None,
        supabase_client: Optional[Any] = None,
    ):
        self.config = config or get_config()
        self.supabase = supabase_client
        self._cancelled_tasks: set = set()

    def _load_system_prompt(self, agent_role: str) -> str:
        """加载 Agent 的系统提示词"""
        workdir = self.config.get_agent_workdir(agent_role)
        claude_md_path = workdir / "CLAUDE.md"

        role_config = self.config.get_agent_role(agent_role)
        if not role_config:
            raise AgentNotFoundError(agent_role)

        if not claude_md_path.exists():
            return f"""你是{role_config.name}。

职责：{role_config.description}

请根据用户的问题提供专业的回答和建议。"""

        try:
            with open(claude_md_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading CLAUDE.md for {agent_role}: {e}")
            return f"你是{role_config.name}。"

    def _get_agent_options(
        self,
        agent_role: str,
        mcp_servers: Optional[List[Any]] = None,
    ) -> ClaudeAgentOptions:
        """构建 Agent 配置选项"""
        role_config = self.config.get_agent_role(agent_role)
        if not role_config:
            raise AgentNotFoundError(agent_role)

        workdir = self.config.get_agent_workdir(agent_role)

        options = ClaudeAgentOptions(
            system_prompt=self._load_system_prompt(agent_role),
            cwd=str(workdir),
            allowed_tools=role_config.allowed_tools,
            model=role_config.model,
            max_turns=role_config.max_turns,
            permission_mode=self.config.permission_mode,
            env=self.config.get_env_dict(),
        )

        # 添加 MCP 服务器
        if mcp_servers:
            options.mcp_servers = mcp_servers

        return options

    async def execute_query(
        self,
        prompt: str,
        agent_role: str,
        mcp_servers: Optional[List[Any]] = None,
        on_text_chunk: Optional[Callable[[str], Any]] = None,
        on_tool_use: Optional[Callable[[str, Dict], Any]] = None,
        on_tool_result: Optional[Callable[[str, Any], Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        执行 Agent 查询（流式输出）

        Args:
            prompt: 用户提示词
            agent_role: Agent 角色
            mcp_servers: MCP 服务器列表
            on_text_chunk: 文本块回调
            on_tool_use: 工具调用回调
            on_tool_result: 工具结果回调

        Yields:
            消息事件字典
        """
        options = self._get_agent_options(agent_role, mcp_servers)

        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            if on_text_chunk:
                                await self._safe_callback(on_text_chunk, block.text)
                            yield {
                                "type": "text_chunk",
                                "content": block.text,
                            }
                        elif isinstance(block, ToolUseBlock):
                            if on_tool_use:
                                await self._safe_callback(
                                    on_tool_use, block.name, block.input
                                )
                            yield {
                                "type": "tool_use",
                                "tool_name": block.name,
                                "tool_id": block.id,
                                "input": block.input,
                            }
                        elif isinstance(block, ToolResultBlock):
                            if on_tool_result:
                                await self._safe_callback(
                                    on_tool_result, block.tool_use_id, block.content
                                )
                            yield {
                                "type": "tool_result",
                                "tool_id": block.tool_use_id,
                                "content": block.content,
                            }

                elif isinstance(message, ResultMessage):
                    yield {
                        "type": "result",
                        "total_cost_usd": message.total_cost_usd,
                        "total_input_tokens": getattr(message, "total_input_tokens", 0),
                        "total_output_tokens": getattr(message, "total_output_tokens", 0),
                    }

        except Exception as e:
            logger.error(f"Agent query failed: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e),
            }
            raise TaskExecutionError(
                task_id="direct_query",
                message=str(e),
                phase="execution",
                original_error=e,
            )

    async def execute_agent_task(
        self,
        task_id: str,
        agent_role: str,
        prompt: str,
        conversation_id: str,
        mcp_servers: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行 Agent 任务（后台运行，写入数据库）

        Args:
            task_id: 任务 ID
            agent_role: Agent 角色
            prompt: 用户提示词
            conversation_id: 对话 ID
            mcp_servers: MCP 服务器列表

        Returns:
            任务执行结果
        """
        if not self.supabase:
            raise AgentSDKError("Supabase client not configured")

        logger.info(f"Starting task {task_id} for agent {agent_role}")

        try:
            # 1. 更新任务状态为 running
            await self._update_task_status(task_id, "running")

            # 2. 创建 AI 消息记录
            message_id = await self._create_message(
                conversation_id=conversation_id,
                task_id=task_id,
                role="assistant",
                status="streaming",
            )

            # 3. 创建消息缓冲器
            async def flush_content(content: str) -> None:
                await self._update_message_content(message_id, content)

            buffer = MessageBuffer(
                flush_callback=flush_content,
                flush_interval=self.config.message_update_interval,
            )

            # 4. 流式执行
            tool_calls = []
            total_cost = 0.0

            async for event in self.execute_query(
                prompt=prompt,
                agent_role=agent_role,
                mcp_servers=mcp_servers,
            ):
                # 检查是否被取消
                if task_id in self._cancelled_tasks:
                    self._cancelled_tasks.discard(task_id)
                    raise TaskCancelledError(task_id)

                if event["type"] == "text_chunk":
                    await buffer.append(event["content"])

                elif event["type"] == "tool_use":
                    tool_calls.append({
                        "name": event["tool_name"],
                        "id": event["tool_id"],
                        "input": event["input"],
                    })

                elif event["type"] == "result":
                    total_cost = event.get("total_cost_usd", 0)

                elif event["type"] == "error":
                    raise TaskExecutionError(
                        task_id=task_id,
                        message=event["error"],
                        phase="execution",
                    )

            # 5. 最终更新
            final_content = await buffer.finalize()

            await self._update_message(
                message_id=message_id,
                content=final_content,
                status="completed",
                tool_calls=tool_calls,
            )

            await self._update_task_status(
                task_id=task_id,
                status="completed",
                metadata={"cost_usd": total_cost},
            )

            logger.info(f"Task {task_id} completed successfully")

            return {
                "task_id": task_id,
                "message_id": message_id,
                "status": "completed",
                "content_length": len(final_content),
                "tool_calls_count": len(tool_calls),
                "cost_usd": total_cost,
            }

        except TaskCancelledError:
            await self._update_task_status(task_id, "cancelled")
            logger.info(f"Task {task_id} was cancelled")
            raise

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            await self._update_task_status(task_id, "failed", error=str(e))
            raise TaskExecutionError(
                task_id=task_id,
                message=str(e),
                phase="execution",
                original_error=e,
            )

    def cancel_task(self, task_id: str) -> None:
        """标记任务为取消"""
        self._cancelled_tasks.add(task_id)

    # ==================== 数据库操作 ====================

    async def _update_task_status(
        self,
        task_id: str,
        status: str,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """更新任务状态"""
        if not self.supabase:
            return

        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }

        if status == "running":
            update_data["started_at"] = datetime.utcnow().isoformat()
        elif status in ("completed", "failed", "cancelled"):
            update_data["completed_at"] = datetime.utcnow().isoformat()

        if error:
            update_data["error"] = error

        if metadata:
            update_data["metadata"] = metadata

        await self.supabase.table("tasks").update(update_data).eq(
            "id", task_id
        ).execute()

    async def _create_message(
        self,
        conversation_id: str,
        task_id: str,
        role: str,
        status: str,
    ) -> str:
        """创建消息记录"""
        if not self.supabase:
            raise AgentSDKError("Supabase client not configured")

        result = await self.supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "task_id": task_id,
            "role": role,
            "content": "",
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        return result.data[0]["id"]

    async def _update_message_content(self, message_id: str, content: str) -> None:
        """更新消息内容"""
        if not self.supabase:
            return

        await self.supabase.table("messages").update({
            "content": content,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", message_id).execute()

    async def _update_message(
        self,
        message_id: str,
        content: str,
        status: str,
        tool_calls: Optional[List[Dict]] = None,
    ) -> None:
        """更新消息完整信息"""
        if not self.supabase:
            return

        update_data = {
            "content": content,
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }

        if tool_calls:
            update_data["tool_calls"] = tool_calls

        await self.supabase.table("messages").update(update_data).eq(
            "id", message_id
        ).execute()

    async def _safe_callback(self, callback: Callable, *args) -> None:
        """安全执行回调"""
        try:
            result = callback(*args)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.error(f"Callback error: {e}")

    # ==================== 工具方法 ====================

    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有可用的 Agent"""
        agents = []
        for role, role_config in self.config.agent_roles.items():
            workdir = self.config.get_agent_workdir(role)
            agents.append({
                "role": role,
                "name": role_config.name,
                "description": role_config.description,
                "model": role_config.model,
                "workdir": str(workdir),
                "available": workdir.exists(),
            })
        return agents
