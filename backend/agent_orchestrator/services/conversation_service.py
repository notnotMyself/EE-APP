"""
Conversation Service - 对话服务

核心职责：
1. 管理持久化对话（每用户-Agent对一个对话）
2. 将简报添加为对话中的卡片消息
3. 处理用户消息并流式返回AI响应
4. 构建包含简报卡片的对话上下文

优化（v2）：
- Agent role 缓存减少数据库查询
- 并行化 IO 操作减少 TTFT
- 增强超时控制（使用全局配置）
"""

import asyncio
import base64
import logging
import json
import re
import httpx
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
from datetime import datetime

from models import ConversationModel, MessageModel
from services.task_intent_recognizer import TaskIntentRecognizer
from agent_registry import get_global_registry
from config import get_timeout_config

logger = logging.getLogger(__name__)

# 模式前缀正则匹配 [MODE:xxx]
MODE_PATTERN = re.compile(r'^\[MODE:(\w+)\]\s*(.*)$', re.DOTALL)

# 评审模式映射到描述
REVIEW_MODE_PROMPTS = {
    'interaction_check': """
【评审模式: 交互可用性验证 (模式 A)】

请使用「模式 A: 交互可用性验证」进行评审，重点关注：
1. 功能入口 - 用户认知模型匹配度
2. 操作路径 - 心智模型与断点检测
3. 交互一致性 - 平台规范符合度（iOS HIG / Material Design）
4. 状态反馈 - 操作确认充分度
5. 认知负荷 - 复杂度控制

请按风险等级（🔴高/🟡中/🟢低）列出发现的问题，并给出具体改进建议。
""",
    'visual_consistency': """
【评审模式: 视觉一致性与清晰度验证 (模式 B)】

请使用「模式 B: 视觉一致性与清晰度验证」进行评审，重点关注：
1. 颜色使用 - 品牌色板、对比度（WCAG AA >= 4.5:1）
2. 字体字号 - Type Scale、最小字号 >= 12pt
3. 间距布局 - 8pt Grid、对齐规范
4. 视觉层级 - 主次信息、关键操作突出
5. 组件一致性 - 设计系统复用

请按风险等级（🔴高/🟡中/🟢低）列出发现的问题，并给出具体改进建议。
""",
    'compare_designs': """
【评审模式: 方案对比与专业评估 (模式 C)】

请使用「模式 C: 方案对比与专业评估」进行评审，从以下维度对比各方案：
1. 认知难度 - 理解设计意图的认知成本
2. 操作效率 - 完成任务的步骤数和复杂度
3. 决策负荷 - 需要做出的选择和判断
4. 符合预期 - 心智模型和平台规范匹配度
5. 心理负担 - 可能产生的焦虑或困惑

请给出各方案的优劣分析和最终推荐。
""",
}


class ConversationService:
    """对话服务 - 支持共享对话模式（优化版）"""

    # 上下文消息数量限制
    MAX_CONTEXT_MESSAGES = 20

    def __init__(
        self,
        supabase_client: Any,
        agent_service: Any,
        briefing_service: Optional[Any] = None,
    ):
        """初始化对话服务

        Args:
            supabase_client: Supabase客户端实例
            agent_service: AgentSDKService实例（用于调用Claude Agent SDK）
            briefing_service: BriefingService实例（可选，用于获取简报详情）
        """
        self.conversation_model = ConversationModel(supabase_client)
        self.message_model = MessageModel(supabase_client)
        self.agent_service = agent_service
        self.briefing_service = briefing_service
        self.supabase = supabase_client

        # 加载全局超时配置
        self._timeout_config = get_timeout_config()

        # 任务相关组件（Phase 1新增）
        self.task_recognizer = TaskIntentRecognizer()
        self.task_executor = None  # 从main.py延迟注入，避免循环依赖

        # 优化：Agent role 缓存（减少数据库查询）
        self._agent_role_cache: Dict[str, str] = {}

    def _extract_mode_and_message(self, user_message: str) -> Tuple[Optional[str], str]:
        """从消息中提取模式标识和原始消息

        消息格式: [MODE:interaction_check] 用户消息

        Args:
            user_message: 用户原始消息

        Returns:
            (mode_id, clean_message): 模式ID和清理后的消息
        """
        match = MODE_PATTERN.match(user_message)
        if match:
            mode_id = match.group(1)
            clean_message = match.group(2).strip()
            logger.info(f"Extracted review mode: {mode_id}")
            return mode_id, clean_message
        return None, user_message

    def _get_mode_prompt(self, mode_id: str) -> str:
        """获取模式对应的评审指令

        Args:
            mode_id: 模式ID (如 interaction_check)

        Returns:
            评审指令 prompt
        """
        return REVIEW_MODE_PROMPTS.get(mode_id, "")

    async def _download_and_encode_images(
        self, attachments: List[Dict]
    ) -> List[Dict[str, Any]]:
        """下载附件图片并转换为 base64

        Args:
            attachments: 附件列表 [{id, url, mime_type}]

        Returns:
            图片内容块列表，可直接用于 Claude 多模态
        """
        image_blocks = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for attachment in attachments:
                url = attachment.get("url")
                mime_type = attachment.get("mime_type", "image/jpeg")

                if not url:
                    continue

                # 只处理图片类型
                if not mime_type.startswith("image/"):
                    logger.info(f"Skipping non-image attachment: {mime_type}")
                    continue

                try:
                    response = await client.get(url)
                    response.raise_for_status()

                    image_data = base64.standard_b64encode(response.content).decode("utf-8")

                    image_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        }
                    })

                    logger.info(f"Downloaded and encoded image: {url[:50]}...")
                except Exception as e:
                    logger.warning(f"Failed to download image {url}: {e}")

        return image_blocks

    @property
    def conversation_timeout(self) -> int:
        """对话超时时间（秒）- 使用全局配置"""
        return self._timeout_config.CONVERSATION_TIMEOUT

    @property
    def api_call_timeout(self) -> int:
        """单次API调用超时时间（秒）- 使用全局配置"""
        return self._timeout_config.API_CALL_TIMEOUT

    @property
    def long_running_task_timeout(self) -> int:
        """长时间运行任务超时（秒）- 用于生成报告等耗时操作"""
        return self._timeout_config.TOOL_LONG_RUNNING_TIMEOUT

    def set_briefing_service(self, briefing_service: Any) -> None:
        """设置BriefingService（解决循环依赖）

        Args:
            briefing_service: BriefingService实例
        """
        self.briefing_service = briefing_service

    def set_task_executor(self, task_executor: Any) -> None:
        """设置TaskExecutionService（解决循环依赖）

        Args:
            task_executor: TaskExecutionService实例
        """
        self.task_executor = task_executor

    def _get_agent_role(self, agent_id: str) -> str:
        """获取 Agent 的 role string（带缓存优化）

        优化：三级缓存策略
        1. 实例级缓存（内存）
        2. AgentRegistry（内存）
        3. 数据库查询（缓存结果）

        Args:
            agent_id: Agent 的 UUID 或 role string

        Returns:
            Agent 的 role string

        Raises:
            ValueError: 如果 agent 不存在
        """
        # 1. 检查实例缓存
        if agent_id in self._agent_role_cache:
            return self._agent_role_cache[agent_id]

        # 使用 agent_registry 的动态映射
        registry = get_global_registry()

        # 2. 尝试通过 UUID 获取 role
        role = registry.get_agent_id(agent_id)
        if role:
            self._agent_role_cache[agent_id] = role
            return role

        # 如果 agent_id 已经是 role，检查是否存在
        if registry.exists(agent_id):
            self._agent_role_cache[agent_id] = agent_id
            return agent_id

        # 3. Fallback: 从数据库查询 agent 的 role（并缓存结果）
        try:
            result = (
                self.supabase.table("agents")
                .select("role")
                .eq("id", agent_id)
                .execute()
            )
            if result.data and len(result.data) > 0:
                db_role = result.data[0].get("role")
                if db_role and registry.exists(db_role):
                    logger.info(
                        f"Found agent role '{db_role}' from database for UUID '{agent_id}'"
                    )
                    self._agent_role_cache[agent_id] = db_role
                    return db_role
        except Exception as e:
            logger.warning(f"Failed to query agent from database: {e}")

        # 未找到 agent
        logger.error(
            f"Agent '{agent_id}' not found in registry or database. "
            f"Available agents: {registry.get_all_ids()}"
        )
        raise ValueError(f"Agent '{agent_id}' not found")

    async def get_or_create_conversation(
        self, user_id: str, agent_id: str
    ) -> str:
        """获取或创建对话（核心方法）

        实现"一个用户-Agent对一个对话"模式。

        Args:
            user_id: 用户UUID
            agent_id: Agent UUID

        Returns:
            对话UUID (conversation_id)

        Raises:
            Exception: 数据库操作失败时
        """
        conversation = await self.conversation_model.get_or_create(
            user_id, agent_id
        )
        return conversation["id"]

    async def add_briefing_to_conversation(
        self, briefing_id: str, user_id: str, agent_id: str
    ) -> str:
        """将简报添加到对话中（核心新增功能）

        工作流程：
        1. 获取或创建对话
        2. 获取简报详情
        3. 在对话中插入简报卡片消息
        4. 更新对话时间戳

        Args:
            briefing_id: 简报UUID
            user_id: 用户UUID
            agent_id: Agent UUID

        Returns:
            对话UUID (conversation_id)

        Raises:
            ValueError: 简报不存在或数据无效时
            Exception: 数据库操作失败时
        """
        try:
            # 1. 获取或创建对话
            conversation_id = await self.get_or_create_conversation(
                user_id, agent_id
            )

            # 2. 获取简报详情
            if self.briefing_service:
                briefing = await self.briefing_service.get_briefing(briefing_id)
            else:
                # Fallback: 直接从数据库查询
                result = (
                    self.supabase.table("briefings")
                    .select("*")
                    .eq("id", briefing_id)
                    .execute()
                )
                if not result.data or len(result.data) == 0:
                    raise ValueError(f"Briefing not found: {briefing_id}")
                briefing = result.data[0]

            if not briefing:
                raise ValueError(f"Briefing not found: {briefing_id}")

            # 3. 在对话中插入简报卡片
            await self.message_model.create_briefing_card(
                conversation_id=conversation_id,
                briefing_id=briefing_id,
                briefing_data={
                    "title": briefing["title"],
                    "summary": briefing["summary"],
                    "priority": briefing["priority"],
                    "briefing_type": briefing.get("briefing_type", "insight"),
                    "impact": briefing.get("impact", ""),
                    "created_at": briefing.get(
                        "created_at", datetime.utcnow().isoformat()
                    ),
                },
            )

            # 4. 更新对话时间戳
            await self.conversation_model.update_last_message_time(conversation_id)

            logger.info(
                f"Added briefing {briefing_id} to conversation {conversation_id} "
                f"(user={user_id}, agent={agent_id})"
            )

            return conversation_id

        except Exception as e:
            logger.error(
                f"Error adding briefing {briefing_id} to conversation: {e}"
            )
            raise

    async def send_message(
        self, conversation_id: str, user_message: str, user_id: str
    ) -> AsyncGenerator[str, None]:
        """发送消息并流式返回AI回复（增强支持任务执行）

        优化：
        - 增加分层超时控制
        - 友好的错误提示

        工作流程：
        1. 保存用户消息
        2. 任务意图识别
        3a. 如果是任务：执行任务→生成简报→AI总结
        3b. 如果不是任务：获取上下文→AI回复
        4. 保存AI回复
        5. 更新对话时间戳

        Args:
            conversation_id: 对话UUID
            user_message: 用户消息内容
            user_id: 用户UUID（用于权限检查）

        Yields:
            AI响应的文本块（流式）或任务事件（JSON）

        Raises:
            ValueError: 对话不存在或用户无权访问时
            Exception: AI调用失败或数据库操作失败时
        """
        try:
            # 根据是否为任务选择不同超时时间
            # 先快速验证对话存在
            conversation = await self.conversation_model.get_by_id(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation not found: {conversation_id}")

            if conversation["user_id"] != user_id:
                raise ValueError(
                    f"User {user_id} does not have access to conversation {conversation_id}"
                )

            # 任务意图识别（决定超时时间）
            task_intent = None
            if self.task_recognizer:
                task_intent = await self.task_recognizer.recognize(
                    user_message, conversation_context={"agent_id": conversation["agent_id"]}
                )

            # 根据任务类型选择超时时间：任务执行用长超时，普通对话用标准超时
            timeout_seconds = (
                self.long_running_task_timeout * 2  # 任务执行：10分钟（可生成长报告）
                if task_intent and self.task_executor
                else self.conversation_timeout  # 普通对话：使用配置的超时
            )

            # 增强超时控制
            async with asyncio.timeout(timeout_seconds):
                # 1. 保存用户消息
                await self.message_model.create_text_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=user_message,
                )

                # 2. 根据是否为任务选择执行流程
                if task_intent and self.task_executor:
                    # 2a. 执行任务并流式输出
                    logger.info(f"Task recognized: {task_intent.task_type}, timeout={timeout_seconds}s")
                    async for event in self._execute_task_and_generate_briefing(
                        conversation=conversation,
                        task_intent=task_intent,
                        user_id=user_id,
                    ):
                        yield event
                else:
                    # 2b. 原有对话流程
                    async for chunk in self._normal_chat_flow(
                        conversation=conversation, user_message=user_message
                    ):
                        yield chunk

        except asyncio.TimeoutError:
            logger.error(f"Conversation timeout after {timeout_seconds}s")
            yield json.dumps({
                "type": "error",
                "error": f"对话处理超时（{timeout_seconds}秒），请稍后重试"
            })
        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            # 返回错误给用户
            yield json.dumps({
                "type": "error",
                "error": "消息处理失败，请稍后重试"
            })

    async def _execute_task_and_generate_briefing(
        self, conversation: Dict, task_intent: Any, user_id: str
    ) -> AsyncGenerator[str, None]:
        """执行任务并生成简报（Phase 1 新增方法）

        Args:
            conversation: 对话记录
            task_intent: 任务意图对象
            user_id: 用户ID

        Yields:
            任务执行事件（JSON格式）和AI总结
        """
        # 🔧 获取 Agent Role (从 UUID 转换)
        agent_role = self._get_agent_role(conversation["agent_id"])

        # 1. 任务开始事件
        yield json.dumps({
            "type": "task_start",
            "task_type": task_intent.task_type,
            "status": "executing"
        })

        # 2. 执行任务
        try:
            result = await self.task_executor.execute_ad_hoc_task(
                agent_role=agent_role,  # 使用 role string
                task_prompt=task_intent.task_prompt,
                user_id=user_id,
                conversation_id=conversation["id"],
            )

            # 3. 简报创建事件
            if result.get("briefing"):
                yield json.dumps({
                    "type": "briefing_created",
                    "briefing_id": result["briefing"]["id"],
                    "title": result["briefing"]["title"],
                    "priority": result["briefing"].get("priority", "P2")
                })
                briefing_title = result["briefing"]["title"]
            else:
                # 没有生成简报（重要性不足）
                yield json.dumps({
                    "type": "task_complete",
                    "briefing_created": False,
                    "reason": "importance_too_low"
                })
                briefing_title = None

            # 4. AI总结回复
            if briefing_title:
                summary_prompt = f"""
任务已完成。简报标题：{briefing_title}

请给用户一个友好的总结（1-2句话），告诉他们分析结果已经生成。
"""
            else:
                summary_prompt = """
任务已完成，分析结果显示一切正常，暂无需要特别关注的问题。

请给用户一个友好的回复（1-2句话）。
"""

            assistant_content = ""
            async for event in self.agent_service.execute_query(
                prompt=summary_prompt,
                agent_role=agent_role,  # 使用 role string
            ):
                event_type = event.get("type")
                # 支持细粒度流式输出 (text_delta) 和完整块 (text_chunk)
                if event_type in ("text_chunk", "text_delta"):
                    chunk = event.get("content", "")
                    assistant_content += chunk
                    yield json.dumps({
                        "type": "text_chunk",
                        "content": chunk
                    })

            # 5. 保存AI回复
            await self.message_model.create_text_message(
                conversation_id=conversation["id"],
                role="assistant",
                content=assistant_content,
            )

            # 6. 更新对话时间戳
            await self.conversation_model.update_last_message_time(conversation["id"])

        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            yield json.dumps({
                "type": "task_error",
                "error": "任务执行失败，请稍后重试"
            })

    async def _normal_chat_flow(
        self, conversation: Dict, user_message: str
    ) -> AsyncGenerator[str, None]:
        """原有对话流程（Phase 1 提取为独立方法）

        优化：并行化 IO 操作减少 TTFT

        Args:
            conversation: 对话记录
            user_message: 用户消息

        Yields:
            AI响应的文本块
        """
        # 优化：并行执行多个 IO 操作
        # 1. Agent role 查询（已缓存）
        # 2. 历史消息查询
        agent_role_task = asyncio.create_task(
            asyncio.to_thread(self._get_agent_role, conversation["agent_id"])
        )
        messages_task = asyncio.create_task(
            self.message_model.get_recent_messages(
                conversation["id"], count=self.MAX_CONTEXT_MESSAGES
            )
        )

        # 等待所有任务完成
        agent_role, messages = await asyncio.gather(agent_role_task, messages_task)

        # 3. 构建包含简报的上下文提示词（CPU 密集型，保持同步）
        context_prompt = self._build_context_with_briefings(
            conversation, messages
        )

        # 组合用户消息
        full_prompt = (
            f"{context_prompt}\n\n"
            f"用户最新消息: {user_message}\n\n"
            f"请根据对话历史和简报信息回答用户的问题。"
        )

        # 4. 流式生成回复（使用Agent SDK Service）
        assistant_content = ""

        # Agent SDK Service 使用 execute_query 方法
        async for event in self.agent_service.execute_query(
            prompt=full_prompt,
            agent_role=agent_role,  # 使用 role string
        ):
            event_type = event.get("type")
            # 支持细粒度流式输出 (text_delta) 和完整块 (text_chunk)
            if event_type in ("text_chunk", "text_delta"):
                chunk = event.get("content", "")
                assistant_content += chunk
                yield chunk

        # 5. 保存AI回复
        await self.message_model.create_text_message(
            conversation_id=conversation["id"],
            role="assistant",
            content=assistant_content,
        )

        # 6. 更新对话时间戳
        await self.conversation_model.update_last_message_time(conversation["id"])

        logger.info(
            f"Completed message exchange in conversation {conversation['id']}, "
            f"assistant response length: {len(assistant_content)}"
        )

    def _build_context_with_briefings(
        self, conversation: Dict[str, Any], messages: List[Dict[str, Any]]
    ) -> str:
        """构建包含简报的上下文（核心改进）

        将简报卡片和文本消息组合成结构化提示词，供AI理解对话背景。

        Args:
            conversation: 对话记录
            messages: 消息列表（按时间顺序）

        Returns:
            格式化的上下文提示词
        """
        prompt = "你是一个AI助手，正在与用户进行长期对话。\n\n"
        prompt += "**对话历史**（包含简报和讨论）：\n\n"

        for msg in messages:
            if msg["content_type"] == "briefing_card":
                # 简报卡片展示为结构化信息
                try:
                    briefing = json.loads(msg["content"])
                    prompt += f"[简报 {briefing.get('created_at', 'N/A')}]\n"
                    prompt += f"标题：{briefing.get('title', 'N/A')}\n"
                    prompt += f"摘要：{briefing.get('summary', 'N/A')}\n"
                    prompt += f"优先级：{briefing.get('priority', 'N/A')}\n"
                    if briefing.get("impact"):
                        prompt += f"影响：{briefing['impact']}\n"
                    prompt += "\n"
                except json.JSONDecodeError:
                    # 如果JSON解析失败，跳过这条简报
                    logger.warning(
                        f"Failed to parse briefing_card content: {msg['content']}"
                    )
                    continue

            elif msg["content_type"] == "text":
                # 普通对话
                role_label = {"user": "用户", "assistant": "助手", "system": "系统"}.get(
                    msg["role"], msg["role"]
                )
                prompt += f"{role_label}: {msg['content']}\n\n"

        return prompt

    async def get_conversation_by_agent(
        self, user_id: str, agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """根据user_id和agent_id获取对话

        Args:
            user_id: 用户UUID
            agent_id: Agent UUID

        Returns:
            对话记录，如果不存在返回None
        """
        try:
            result = (
                self.supabase.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .eq("agent_id", agent_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(
                f"Error getting conversation for user={user_id}, agent={agent_id}: {e}"
            )
            return None

    async def list_user_conversations(
        self, user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取用户的所有对话

        Args:
            user_id: 用户UUID
            limit: 返回数量限制

        Returns:
            对话列表
        """
        return await self.conversation_model.list_by_user(user_id, limit)

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取单个对话

        Args:
            conversation_id: 对话UUID

        Returns:
            对话记录，如果不存在返回None
        """
        return await self.conversation_model.get_by_id(conversation_id)

    async def send_message_ws(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        ws_writer: Any,  # WebSocketWriter
        attachments: Optional[List[Dict]] = None,
    ) -> None:
        """通过WebSocket发送消息并流式返回AI回复

        这是send_message的WebSocket版本，直接写入WebSocketWriter而不是yield。

        Args:
            conversation_id: 对话UUID
            user_message: 用户消息内容
            user_id: 用户UUID
            ws_writer: WebSocketWriter实例
            attachments: 附件列表 [{id, url, mime_type}]

        Raises:
            ValueError: 对话不存在或用户无权访问时
            Exception: AI调用失败或数据库操作失败时
        """
        # 用于 finally 中访问
        timeout_seconds = self.conversation_timeout
        try:
            # 先快速验证对话存在
            conversation = await self.conversation_model.get_by_id(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation not found: {conversation_id}")

            if conversation["user_id"] != user_id:
                raise ValueError(
                    f"User {user_id} does not have access to conversation {conversation_id}"
                )

            # 任务意图识别（决定超时时间）
            task_intent = None
            if self.task_recognizer:
                task_intent = await self.task_recognizer.recognize(
                    user_message,
                    conversation_context={"agent_id": conversation["agent_id"]},
                )

            # 根据任务类型选择超时时间
            timeout_seconds = (
                self.long_running_task_timeout * 2  # 任务执行：10分钟
                if task_intent and self.task_executor
                else self.conversation_timeout  # 普通对话：使用配置的超时
            )

            async with asyncio.timeout(timeout_seconds):
                # 1. 保存用户消息（包含附件元数据）
                await self.message_model.create_text_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=user_message,
                    attachments=attachments,
                )

                # 2. 根据是否为任务选择执行流程
                if task_intent and self.task_executor:
                    # 2a. 执行任务
                    logger.info(f"Task recognized: {task_intent.task_type}, timeout={timeout_seconds}s")
                    await self._execute_task_ws(
                        conversation=conversation,
                        task_intent=task_intent,
                        user_id=user_id,
                        ws_writer=ws_writer,
                    )
                else:
                    # 2b. 原有对话流程
                    await self._normal_chat_flow_ws(
                        conversation=conversation,
                        user_message=user_message,
                        ws_writer=ws_writer,
                        attachments=attachments,
                    )

        except asyncio.TimeoutError:
            logger.error(f"Conversation timeout after {timeout_seconds}s")
            # 超时时尝试刷新已缓冲的内容
            try:
                await ws_writer.finalize()
            except Exception:
                pass
            await ws_writer.write_error(
                f"对话处理超时（{timeout_seconds}秒），请稍后重试"
            )
        except Exception as e:
            logger.error(f"Error in send_message_ws: {e}", exc_info=True)
            await ws_writer.write_error("消息处理失败，请稍后重试")

    async def _execute_task_ws(
        self,
        conversation: Dict,
        task_intent: Any,
        user_id: str,
        ws_writer: Any,
    ) -> None:
        """执行任务（WebSocket版本）"""
        agent_role = self._get_agent_role(conversation["agent_id"])

        # 1. 任务开始事件
        await ws_writer.write_task_start(
            task_type=task_intent.task_type,
            task_id=None,
        )

        try:
            result = await self.task_executor.execute_ad_hoc_task(
                agent_role=agent_role,
                task_prompt=task_intent.task_prompt,
                user_id=user_id,
                conversation_id=conversation["id"],
            )

            # 2. 简报创建事件
            if result.get("briefing"):
                briefing = result["briefing"]
                # 通过metadata发送briefing_created事件
                await ws_writer.websocket.send_json({
                    "type": "briefing_created",
                    "briefing_id": briefing["id"],
                    "title": briefing["title"],
                    "priority": briefing.get("priority", "P2"),
                    "ts": asyncio.get_event_loop().time(),
                })
                briefing_title = briefing["title"]
            else:
                await ws_writer.websocket.send_json({
                    "type": "task_complete",
                    "briefing_created": False,
                    "reason": "importance_too_low",
                    "ts": asyncio.get_event_loop().time(),
                })
                briefing_title = None

            # 3. AI总结回复
            if briefing_title:
                summary_prompt = f"""
任务已完成。简报标题：{briefing_title}

请给用户一个友好的总结（1-2句话），告诉他们分析结果已经生成。
"""
            else:
                summary_prompt = """
任务已完成，分析结果显示一切正常，暂无需要特别关注的问题。

请给用户一个友好的回复（1-2句话）。
"""

            async for event in self.agent_service.execute_query(
                prompt=summary_prompt,
                agent_role=agent_role,
            ):
                event_type = event.get("type")
                # 支持细粒度流式输出 (text_delta) 和完整块 (text_chunk)
                if event_type in ("text_chunk", "text_delta"):
                    await ws_writer.write_text_chunk(event.get("content", ""))

            # 4. 保存AI回复
            await self.message_model.create_text_message(
                conversation_id=conversation["id"],
                role="assistant",
                content=ws_writer.accumulated_content,
            )

            # 5. 更新对话时间戳
            await self.conversation_model.update_last_message_time(conversation["id"])

        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            await ws_writer.write_error("任务执行失败，请稍后重试")

    async def _normal_chat_flow_ws(
        self,
        conversation: Dict,
        user_message: str,
        ws_writer: Any,
        attachments: Optional[List[Dict]] = None,
    ) -> None:
        """原有对话流程（WebSocket版本）"""
        # 提取模式标识和清理消息
        mode_id, clean_message = self._extract_mode_and_message(user_message)

        # 并行执行多个IO操作
        agent_role_task = asyncio.create_task(
            asyncio.to_thread(self._get_agent_role, conversation["agent_id"])
        )
        messages_task = asyncio.create_task(
            self.message_model.get_recent_messages(
                conversation["id"], count=self.MAX_CONTEXT_MESSAGES
            )
        )

        agent_role, messages = await asyncio.gather(agent_role_task, messages_task)

        # 处理附件图片（如果有）
        image_blocks = []
        if attachments:
            image_blocks = await self._download_and_encode_images(attachments)
            if image_blocks:
                logger.info(f"Downloaded and encoded {len(image_blocks)} images for multimodal analysis")

        # 构建上下文
        context_prompt = self._build_context_with_briefings(conversation, messages)

        # 如果有评审模式，添加对应的评审指令
        mode_prompt = self._get_mode_prompt(mode_id) if mode_id else ""

        if mode_prompt:
            # 有评审模式时，使用专业评审 prompt
            full_prompt = (
                f"{context_prompt}\n\n"
                f"{mode_prompt}\n\n"
                f"用户消息: {clean_message}\n\n"
                f"请按照指定的评审模式进行分析。如果用户上传了图片，请仔细分析图片内容。"
            )
        else:
            # 普通对话
            full_prompt = (
                f"{context_prompt}\n\n"
                f"用户最新消息: {clean_message}\n\n"
                f"请根据对话历史和简报信息回答用户的问题。"
            )

        # 流式生成回复
        # 工具执行进度心跳任务
        tool_progress_task: Optional[asyncio.Task] = None
        current_tool_info: dict = {}

        async def _send_tool_progress_heartbeat():
            """发送工具执行进度心跳（模拟进度，让用户知道系统在工作）"""
            try:
                progress = 0.1
                while True:
                    await asyncio.sleep(3)  # 每3秒发送一次心跳
                    progress = min(progress + 0.05, 0.9)  # 进度最多到90%
                    await ws_writer.write_tool_progress(
                        tool_name=current_tool_info.get("tool_name", ""),
                        tool_id=current_tool_info.get("tool_id", ""),
                        progress=progress,
                        status="executing",
                        message_text=current_tool_info.get("status_message"),
                        file_path=current_tool_info.get("file_path"),
                    )
            except asyncio.CancelledError:
                pass  # 正常取消

        async for event in self.agent_service.execute_query(
            prompt=full_prompt,
            agent_role=agent_role,
            image_blocks=image_blocks if image_blocks else None,
        ):
            event_type = event.get("type")
            # 支持细粒度流式输出 (text_delta) 和完整块 (text_chunk)
            if event_type in ("text_chunk", "text_delta"):
                await ws_writer.write_text_chunk(event.get("content", ""))
            elif event_type == "tool_use":
                # 取消之前的进度任务（如果有）
                if tool_progress_task:
                    tool_progress_task.cancel()
                    try:
                        await tool_progress_task
                    except asyncio.CancelledError:
                        pass

                tool_name = event.get("tool_name", "")
                tool_id = event.get("tool_id", "")
                tool_input = event.get("input", {})

                # 提取状态信息
                file_path = None
                status_message = "正在执行..."
                if tool_name == "Write":
                    file_path = tool_input.get("file_path") if tool_input else None
                    if file_path:
                        status_message = f"正在生成: {file_path.split('/')[-1]}"
                elif tool_name == "Bash":
                    command = tool_input.get("command", "") if tool_input else ""
                    if "skill" in command:
                        status_message = "正在执行数据分析..."

                current_tool_info = {
                    "tool_name": tool_name,
                    "tool_id": tool_id,
                    "file_path": file_path,
                    "status_message": status_message,
                }

                await ws_writer.write_tool_use(
                    tool_name=tool_name,
                    tool_id=tool_id,
                    tool_input=tool_input,
                )

                # 启动进度心跳任务
                tool_progress_task = asyncio.create_task(_send_tool_progress_heartbeat())

            elif event_type == "tool_result":
                # 取消进度心跳任务
                if tool_progress_task:
                    tool_progress_task.cancel()
                    try:
                        await tool_progress_task
                    except asyncio.CancelledError:
                        pass
                    tool_progress_task = None

                await ws_writer.write_tool_result(
                    tool_id=event.get("tool_id", ""),
                    result=event.get("result"),
                    is_error=event.get("is_error", False),
                )

        # 确保清理进度任务
        if tool_progress_task:
            tool_progress_task.cancel()
            try:
                await tool_progress_task
            except asyncio.CancelledError:
                pass

        # 保存AI回复
        await self.message_model.create_text_message(
            conversation_id=conversation["id"],
            role="assistant",
            content=ws_writer.accumulated_content,
        )

        # 更新对话时间戳
        await self.conversation_model.update_last_message_time(conversation["id"])

        logger.info(
            f"Completed WS message exchange in conversation {conversation['id']}, "
            f"assistant response length: {len(ws_writer.accumulated_content)}"
        )

