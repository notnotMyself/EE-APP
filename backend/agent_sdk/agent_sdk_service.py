"""
Agent SDK Service

基于 Claude Agent SDK 的 Agent 服务封装。
处理 Agent 任务执行、消息流式输出、工具调用等。

多模态支持：
- 对于纯文本请求，使用 Claude Agent SDK（支持工具调用）
- 对于带图片的多模态请求，使用 Anthropic API 直接调用（流式输出）
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Union

from anthropic import AsyncAnthropic
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
from claude_agent_sdk.types import StreamEvent  # 细粒度流式输出事件

from .config import AgentSDKConfig, get_config
from .exceptions import (
    AgentNotFoundError,
    AgentSDKError,
    TaskCancelledError,
    TaskExecutionError,
)

logger = logging.getLogger(__name__)


class MessageBuffer:
    """消息内容缓冲器，用于批量更新数据库

    优化：支持首次快速刷新，减少 TTFT（Time to First Token）
    """

    def __init__(
        self,
        flush_callback: Callable[[str], Any],
        initial_flush_interval: float = 0.01,  # 首次 10ms 快速刷新 (TTFT优化)
        steady_flush_interval: float = 0.08,   # 后续 80ms 稳定刷新
        max_buffer_size: int = 15,             # 15 字符触发刷新 (更快响应)
    ):
        self.flush_callback = flush_callback
        self.initial_flush_interval = initial_flush_interval
        self.steady_flush_interval = steady_flush_interval
        self.max_buffer_size = max_buffer_size
        self.content = ""
        self.last_flush_time = time.time()
        self.last_flush_length = 0
        self.flush_count = 0
        self._pending_flush: Optional[asyncio.Task] = None

    async def append(self, text: str) -> None:
        """追加文本到缓冲区（优化：首次快速响应）"""
        self.content += text

        # 第一次刷新使用快速间隔，后续使用稳定间隔
        flush_interval = (
            self.initial_flush_interval
            if self.flush_count == 0
            else self.steady_flush_interval
        )

        current_time = time.time()
        should_flush = (
            current_time - self.last_flush_time >= flush_interval
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
            self.flush_count += 1  # Track flush count for adaptive intervals
        except Exception as e:
            logger.error(f"Failed to flush message buffer: {e}")

    async def _delayed_flush(self) -> None:
        """延迟刷新"""
        # Use appropriate interval based on flush count
        flush_interval = (
            self.initial_flush_interval
            if self.flush_count == 0
            else self.steady_flush_interval
        )
        await asyncio.sleep(flush_interval)
        await self._flush()
        self._pending_flush = None

    async def finalize(self) -> str:
        """最终刷新并返回完整内容"""
        await self._flush()
        return self.content


class AgentSDKService:
    """基于 Claude Agent SDK 的 Agent 服务
    
    多模态支持：
    - 纯文本请求：使用 Claude Agent SDK（支持工具调用）
    - 带图片请求：使用 Anthropic API 直接调用（流式输出）
    """

    def __init__(
        self,
        config: Optional[AgentSDKConfig] = None,
        supabase_client: Optional[Any] = None,
    ):
        self.config = config or get_config()
        self.supabase = supabase_client
        self._cancelled_tasks: set = set()
        
        # 预热优化：System prompt 缓存（减少文件 I/O）
        self._system_prompt_cache: Dict[str, str] = {}
        
        # 预热优化：Agent options 缓存
        self._agent_options_cache: Dict[str, ClaudeAgentOptions] = {}
        
        # 初始化 Anthropic 客户端（用于多模态请求）
        self._anthropic_client: Optional[AsyncAnthropic] = None
        api_key = self.config.anthropic_auth_token or os.getenv("ANTHROPIC_AUTH_TOKEN")
        base_url = self.config.anthropic_base_url or os.getenv("ANTHROPIC_BASE_URL")
        
        if api_key:
            self._anthropic_client = AsyncAnthropic(
                api_key=api_key,
                base_url=base_url,
            )
            logger.info(f"Anthropic client initialized for multimodal support (base_url={base_url})")

    def _load_system_prompt(self, agent_role: str) -> str:
        """加载 Agent 的系统提示词（带缓存优化）
        
        预热优化：首次加载后缓存，避免重复文件 I/O
        """
        # 检查缓存
        if agent_role in self._system_prompt_cache:
            return self._system_prompt_cache[agent_role]
        
        workdir = self.config.get_agent_workdir(agent_role)
        claude_md_path = workdir / "CLAUDE.md"

        role_config = self.config.get_agent_role(agent_role)
        if not role_config:
            raise AgentNotFoundError(agent_role)

        if not claude_md_path.exists():
            prompt = f"""你是{role_config.name}。

职责：{role_config.description}

请根据用户的问题提供专业的回答和建议。"""
            self._system_prompt_cache[agent_role] = prompt
            return prompt

        try:
            with open(claude_md_path, "r", encoding="utf-8") as f:
                prompt = f.read()
                self._system_prompt_cache[agent_role] = prompt
                logger.info(f"System prompt cached for agent: {agent_role}")
                return prompt
        except Exception as e:
            logger.error(f"Error loading CLAUDE.md for {agent_role}: {e}")
            prompt = f"你是{role_config.name}。"
            self._system_prompt_cache[agent_role] = prompt
            return prompt

    def _get_agent_options(
        self,
        agent_role: str,
        mcp_servers: Optional[List[Any]] = None,
    ) -> ClaudeAgentOptions:
        """构建 Agent 配置选项（带缓存优化）
        
        注意：MCP servers 不缓存，因为可能变化
        """
        # 检查缓存（仅当没有 mcp_servers 时使用缓存）
        if not mcp_servers and agent_role in self._agent_options_cache:
            return self._agent_options_cache[agent_role]
        
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
            # 启用细粒度流式输出：返回 StreamEvent 包含 content_block_delta
            include_partial_messages=True,
        )

        # 添加 MCP 服务器
        if mcp_servers:
            options.mcp_servers = mcp_servers
        else:
            # 缓存（仅当没有 mcp_servers 时）
            self._agent_options_cache[agent_role] = options

        return options

    def warmup_agent(self, agent_role: str) -> None:
        """预热 Agent 配置（减少首次请求延迟）
        
        在 WebSocket 连接时调用，预加载：
        1. System prompt（从文件）
        2. Agent options
        
        Args:
            agent_role: Agent 角色标识
        """
        try:
            # 预加载配置（会触发缓存）
            self._get_agent_options(agent_role)
            logger.info(f"Agent warmed up: {agent_role}")
        except Exception as e:
            logger.warning(f"Failed to warmup agent {agent_role}: {e}")

    async def _execute_multimodal_query(
        self,
        prompt: str,
        agent_role: str,
        image_blocks: List[Dict[str, Any]],
        on_text_chunk: Optional[Callable[[str], Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        执行多模态查询（带图片）
        
        根据 Claude Agent SDK 文档，有两种方式支持多模态：
        1. ClaudeSDKClient 流式输入模式 - 支持图片（推荐）
        2. query() 单消息模式 - 不支持图片
        
        这里优先尝试使用 ClaudeSDKClient，如果失败则回退到 Anthropic API。
        
        Args:
            prompt: 用户提示词
            agent_role: Agent 角色
            image_blocks: 图片内容块列表
            on_text_chunk: 文本块回调
            
        Yields:
            消息事件字典
        """
        # 优先尝试使用 ClaudeSDKClient 流式输入模式
        logger.info("[Multimodal] Attempting ClaudeSDKClient approach...")
        try:
            event_count = 0
            async for event in self._execute_multimodal_via_sdk_client(
                prompt, agent_role, image_blocks, on_text_chunk
            ):
                event_count += 1
                logger.info(f"[Multimodal] SDK Client yielded event #{event_count}: {event.get('type')}")
                yield event
            logger.info(f"[Multimodal] SDK Client completed, total events: {event_count}")
            return
        except Exception as e:
            logger.warning(f"[Multimodal] ClaudeSDKClient failed, falling back to Anthropic API: {e}", exc_info=True)
        
        # 回退到 Anthropic API 直接调用
        async for event in self._execute_multimodal_via_anthropic(
            prompt, agent_role, image_blocks, on_text_chunk
        ):
            yield event

    async def _execute_multimodal_via_sdk_client(
        self,
        prompt: str,
        agent_role: str,
        image_blocks: List[Dict[str, Any]],
        on_text_chunk: Optional[Callable[[str], Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        使用 ClaudeSDKClient 流式输入模式执行多模态查询
        
        根据文档 https://platform.claude.com/docs/zh-CN/agent-sdk/streaming-vs-single-mode
        流式输入模式支持图片上传，使用异步生成器发送消息。
        """
        from claude_agent_sdk import ClaudeSDKClient
        
        logger.info(f"[SDK Client] Starting multimodal query with {len(image_blocks)} images")
        
        options = self._get_agent_options(agent_role)
        logger.info(f"[SDK Client] Options prepared for agent_role={agent_role}")
        
        # 构建多模态消息内容
        message_content = image_blocks + [{"type": "text", "text": prompt}]
        logger.info(f"[SDK Client] Message content prepared: {len(message_content)} blocks")
        
        async def message_generator():
            """异步消息生成器 - 流式输入模式"""
            logger.info("[SDK Client] Message generator yielding user message")
            yield {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": message_content,
                }
            }
            logger.info("[SDK Client] Message generator completed")
        
        logger.info(f"[SDK Client] Creating ClaudeSDKClient...")
        
        try:
            async with ClaudeSDKClient(options) as client:
                logger.info("[SDK Client] Client context entered, calling query...")
                await client.query(message_generator())
                logger.info("[SDK Client] Query submitted, receiving response...")
                
                async for message in client.receive_response():
                    logger.info(f"[SDK Client] Received message type: {type(message).__name__}")
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                logger.info(f"[SDK Client] TextBlock received: {len(block.text)} chars")
                                if on_text_chunk:
                                    await self._safe_callback(on_text_chunk, block.text)
                                yield {
                                    "type": "text_chunk",
                                    "content": block.text,
                                }
                            elif isinstance(block, ToolUseBlock):
                                logger.info(f"[SDK Client] ToolUseBlock: {block.name}")
                                yield {
                                    "type": "tool_use",
                                    "tool_name": block.name,
                                    "tool_id": block.id,
                                    "input": block.input,
                                }
                    elif isinstance(message, ResultMessage):
                        logger.info(f"[SDK Client] ResultMessage received")
                        yield {
                            "type": "result",
                            "total_cost_usd": message.total_cost_usd,
                            "duration_ms": message.duration_ms,
                            "num_turns": message.num_turns,
                        }
                        
                logger.info("[SDK Client] Response stream completed")
        except Exception as e:
            logger.error(f"[SDK Client] Error in ClaudeSDKClient: {e}", exc_info=True)
            raise

    async def _execute_multimodal_via_anthropic(
        self,
        prompt: str,
        agent_role: str,
        image_blocks: List[Dict[str, Any]],
        on_text_chunk: Optional[Callable[[str], Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        使用 Anthropic API 直接调用执行多模态查询（回退方案）
        """
        if not self._anthropic_client:
            logger.error("Anthropic client not initialized for multimodal query")
            yield {
                "type": "error",
                "error": "多模态功能未配置，请检查 ANTHROPIC_AUTH_TOKEN",
            }
            return
        
        role_config = self.config.get_agent_role(agent_role)
        if not role_config:
            raise AgentNotFoundError(agent_role)
        
        system_prompt = self._load_system_prompt(agent_role)
        message_content = image_blocks + [{"type": "text", "text": prompt}]
        
        logger.info(f"Executing multimodal query via Anthropic API with {len(image_blocks)} images")
        
        try:
            async with self._anthropic_client.messages.stream(
                model=role_config.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": message_content}],
            ) as stream:
                async for text in stream.text_stream:
                    if text:
                        if on_text_chunk:
                            await self._safe_callback(on_text_chunk, text)
                        yield {
                            "type": "text_delta",
                            "content": text,
                        }
                
                final_message = await stream.get_final_message()
                if final_message:
                    yield {
                        "type": "result",
                        "input_tokens": final_message.usage.input_tokens if final_message.usage else 0,
                        "output_tokens": final_message.usage.output_tokens if final_message.usage else 0,
                    }
                    
        except Exception as e:
            logger.error(f"Anthropic API multimodal query failed: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": f"多模态查询失败: {str(e)}",
            }

    async def execute_query(
        self,
        prompt: str,
        agent_role: str,
        mcp_servers: Optional[List[Any]] = None,
        image_blocks: Optional[List[Dict[str, Any]]] = None,
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
            image_blocks: 图片内容块列表（用于多模态分析）
                         格式: [{"type": "image", "source": {"type": "base64", "media_type": "...", "data": "..."}}]
            on_text_chunk: 文本块回调
            on_tool_use: 工具调用回调
            on_tool_result: 工具结果回调

        Yields:
            消息事件字典
        """
        # 多模态请求：使用 Anthropic API 直接调用（Agent SDK 不支持列表格式的 prompt）
        if image_blocks:
            logger.info(f"Executing multimodal query with {len(image_blocks)} images using Anthropic API")
            async for event in self._execute_multimodal_query(
                prompt=prompt,
                agent_role=agent_role,
                image_blocks=image_blocks,
                on_text_chunk=on_text_chunk,
            ):
                yield event
            return

        # 纯文本请求：使用 Agent SDK（支持工具调用）
        options = self._get_agent_options(agent_role, mcp_servers)

        try:
            async for message in query(prompt=prompt, options=options):
                # 处理 StreamEvent：细粒度流式输出（token 级别）
                if isinstance(message, StreamEvent):
                    event = message.event
                    event_type = event.get("type", "")
                    
                    # content_block_delta 包含 text_delta（文本增量）
                    if event_type == "content_block_delta":
                        delta = event.get("delta", {})
                        delta_type = delta.get("type", "")
                        
                        if delta_type == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                if on_text_chunk:
                                    await self._safe_callback(on_text_chunk, text)
                                yield {
                                    "type": "text_delta",  # 使用 text_delta 区分于完整 TextBlock
                                    "content": text,
                                }
                        elif delta_type == "thinking_delta":
                            # 思考过程增量（如果启用了 extended thinking）
                            thinking = delta.get("thinking", "")
                            if thinking:
                                yield {
                                    "type": "thinking_delta",
                                    "content": thinking,
                                }
                        elif delta_type == "input_json_delta":
                            # 工具调用输入的增量
                            partial_json = delta.get("partial_json", "")
                            if partial_json:
                                yield {
                                    "type": "tool_input_delta",
                                    "content": partial_json,
                                }
                    
                    # content_block_start: 内容块开始
                    elif event_type == "content_block_start":
                        content_block = event.get("content_block", {})
                        block_type = content_block.get("type", "")
                        if block_type == "tool_use":
                            # 工具调用开始
                            yield {
                                "type": "tool_use_start",
                                "tool_name": content_block.get("name", ""),
                                "tool_id": content_block.get("id", ""),
                            }
                        elif block_type == "thinking":
                            yield {
                                "type": "thinking_start",
                            }
                    
                    # content_block_stop: 内容块结束
                    elif event_type == "content_block_stop":
                        yield {
                            "type": "content_block_stop",
                            "index": event.get("index", 0),
                        }
                    
                    # message_start / message_delta / message_stop 可以忽略或做元数据处理
                    elif event_type in ("message_start", "message_delta", "message_stop"):
                        # 可选：传递消息级别的元数据
                        pass

                # 处理 AssistantMessage：完整的消息块（作为补充/备用）
                elif isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # 如果已经通过 StreamEvent 发送了 text_delta，这里可能是重复的
                            # 但为了兼容性，仍然处理完整的 TextBlock
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
