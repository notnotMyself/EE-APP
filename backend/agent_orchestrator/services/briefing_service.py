"""
简报服务 - 简报生成、过滤和管理

优化说明:
- 优先使用 skills 返回的结构化数据(metrics, findings, key_data, full_report)
- 支持确定性UI Schema生成（基于结构化数据，无需LLM调用）
- 支持AI生成封面图片
"""

import json
import logging
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .importance_evaluator import ImportanceEvaluator

logger = logging.getLogger(__name__)


class BriefingService:
    """简报生成和管理服务"""

    def __init__(
        self,
        supabase_client: Any,
        importance_evaluator: ImportanceEvaluator = None,
        conversation_service: Any = None,
        push_notification_service: Any = None,
        ui_schema_generator: Any = None,
        cover_image_service: Any = None,
    ):
        self.supabase = supabase_client
        self.evaluator = importance_evaluator or ImportanceEvaluator()
        self.conversation_service = conversation_service
        self.push_notification_service = push_notification_service
        self.ui_schema_generator = ui_schema_generator
        self.cover_image_service = cover_image_service

    async def evaluate_importance(self, analysis_result: Dict[str, Any]) -> float:
        """评估分析结果的重要性分数"""
        return await self.evaluator.evaluate(analysis_result)

    async def get_today_briefing_count(self, agent_id: str) -> int:
        """获取今日该Agent生成的简报数量"""
        if not self.supabase:
            return 0

        today = date.today().isoformat()

        try:
            result = (
                self.supabase.table("briefings")
                .select("id", count="exact")
                .eq("agent_id", agent_id)
                .gte("created_at", f"{today}T00:00:00")
                .lt("created_at", f"{today}T23:59:59")
                .execute()
            )
            return result.count or 0
        except Exception as e:
            logger.error(f"Failed to get today's briefing count: {e}")
            return 0

    async def create_briefing(
        self,
        agent_id: str,
        user_id: str,
        analysis_result: Dict[str, Any],
        importance_score: float,
        job_id: Optional[str] = None,
        report_artifact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建简报记录"""
        # 从分析结果中提取简报信息（优先使用结构化数据）
        briefing_data = self._extract_briefing_data(analysis_result)

        # 构建简报记录
        briefing = {
            "id": str(uuid4()),
            "agent_id": agent_id,
            "user_id": user_id,
            "briefing_type": briefing_data["type"],
            "priority": briefing_data["priority"],
            "title": briefing_data["title"],
            "summary": briefing_data["summary"],
            "impact": briefing_data.get("impact"),
            "actions": briefing_data.get("actions", []),
            "report_artifact_id": report_artifact_id,
            "context_data": {
                "analysis_result": analysis_result,
                "job_id": job_id,
                # 保存结构化数据以便前端和对话使用
                "metrics": briefing_data.get("metrics", {}),
                "findings": briefing_data.get("findings", []),
                "key_data": briefing_data.get("key_data", {}),
            },
            "importance_score": importance_score,
            "status": "new",
            "created_at": datetime.utcnow().isoformat(),
        }

        # Generate UI Schema - 优先使用确定性生成（基于结构化数据）
        if self.ui_schema_generator:
            try:
                # 如果有结构化数据，使用确定性生成
                if briefing_data.get("metrics") or briefing_data.get("findings"):
                    ui_schema = self.ui_schema_generator.generate_from_structured_data({
                        "metrics": briefing_data.get("metrics", {}),
                        "findings": briefing_data.get("findings", []),
                        "key_data": briefing_data.get("key_data", {}),
                    })
                    if ui_schema:
                        briefing["ui_schema"] = ui_schema
                        briefing["ui_schema_version"] = "1.0"
                        logger.info(f"Generated deterministic UI schema for briefing {briefing['id']}")
                    else:
                        # Fallback to LLM-based generation
                        ui_schema = self.ui_schema_generator.generate_from_analysis(
                            analysis_result=analysis_result.get("response", ""),
                            data_context={"agent_id": agent_id, "priority": briefing_data["priority"]},
                            agent_role=agent_id
                        )
                        if ui_schema:
                            briefing["ui_schema"] = ui_schema
                            briefing["ui_schema_version"] = "1.0"
                else:
                    # 没有结构化数据，使用LLM生成
                    ui_schema = self.ui_schema_generator.generate_from_analysis(
                        analysis_result=analysis_result.get("response", ""),
                        data_context={"agent_id": agent_id, "priority": briefing_data["priority"]},
                        agent_role=agent_id
                    )
                    if ui_schema:
                        briefing["ui_schema"] = ui_schema
                        briefing["ui_schema_version"] = "1.0"
                    else:
                        # Fallback to markdown schema
                        briefing["ui_schema"] = self.ui_schema_generator.create_fallback_markdown_schema(
                            briefing_data["summary"]
                        )
                        briefing["ui_schema_version"] = "1.0"
            except Exception as e:
                logger.error(f"Error generating UI schema: {e}")

        # Generate cover image if service is available
        if self.cover_image_service:
            try:
                cover_result = await self.cover_image_service.generate_cover_image(
                    briefing_type=briefing_data["type"],
                    title=briefing_data["title"],
                    summary=briefing_data["summary"],
                    priority=briefing_data["priority"],
                )
                if cover_result and cover_result.get("image_data"):
                    cover_url = await self.cover_image_service.upload_to_storage(
                        image_data=cover_result["image_data"],
                        briefing_id=briefing["id"],
                        supabase_client=self.supabase,
                    )
                    if cover_url:
                        briefing["cover_image_url"] = cover_url
                        briefing["cover_image_metadata"] = cover_result.get("metadata", {})
                        logger.info(f"Generated cover image for briefing {briefing['id']}")
            except Exception as e:
                logger.warning(f"Cover image generation failed (non-critical): {e}")

        if not self.supabase:
            logger.warning("Supabase not configured, briefing not saved")
            return briefing

        try:
            result = self.supabase.table("briefings").insert(briefing).execute()
            created_briefing = result.data[0] if result.data else briefing
            logger.info(f"Created briefing {briefing['id']} for user {user_id}")

            # Send push notification if push service is configured
            priority = briefing_data["priority"]
            if self.push_notification_service and importance_score >= 0.7 and priority in ["P0", "P1"]:
                try:
                    # Get agent name from the registry or context
                    agent_name = analysis_result.get("agent_name", "AI Employee")

                    # Prepare briefing data for notification
                    notification_briefing = {
                        **created_briefing,
                        "agent_name": agent_name
                    }

                    # Send notification asynchronously (don't wait for result)
                    await self.push_notification_service.send_briefing_notification(
                        user_id=user_id,
                        briefing=notification_briefing
                    )
                except Exception as e:
                    # Log but don't fail briefing creation if notification fails
                    logger.error(f"Failed to send push notification for briefing {briefing['id']}: {e}")

            return created_briefing
        except Exception as e:
            logger.error(f"Failed to create briefing: {e}")
            raise

    def _extract_briefing_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从分析结果中提取简报数据

        优先级:
        1. 直接使用 structured_data 字段（如果存在）
        2. 尝试从 response 中解析 JSON
        3. 回退到文本提取（旧逻辑）
        """
        # 1. 优先检查 structured_data 字段
        structured = analysis_result.get("structured_data")
        if structured and isinstance(structured, dict) and structured.get("title"):
            logger.info("Using structured_data for briefing extraction")
            return self._extract_from_structured(structured)

        # 2. 尝试从 response 中解析 JSON
        response = analysis_result.get("response", "")
        parsed = self._try_parse_json_from_response(response)
        if parsed and isinstance(parsed, dict) and parsed.get("title"):
            logger.info("Parsed JSON from response for briefing extraction")
            return self._extract_from_structured(parsed)

        # 3. 回退到文本提取
        logger.info("Using text extraction for briefing (no structured data found)")
        return self._extract_from_text(response)

    def _extract_from_structured(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """从结构化数据提取简报信息"""
        findings = data.get("findings", [])
        severity = self._determine_severity_from_findings(findings)

        # 确定类型和优先级
        briefing_type = data.get("briefing_type", "insight")
        if briefing_type == "dev_efficiency":
            briefing_type = "insight"  # 标准化类型

        priority = data.get("priority", "P2")
        if not priority.startswith("P"):
            # 根据 severity 推断 priority
            if severity == "high":
                priority = "P1"
            elif severity == "critical":
                priority = "P0"
            else:
                priority = "P2"

        # 构建操作按钮
        actions = self._build_actions_from_findings(findings)

        return {
            "type": briefing_type,
            "priority": priority,
            "title": data.get("title", "分析报告"),
            "summary": data.get("summary", ""),
            "impact": data.get("impact"),
            "actions": actions,
            "metrics": data.get("metrics", {}),
            "findings": findings,
            "key_data": data.get("key_data", {}),
            "full_report": data.get("full_report"),
        }

    def _determine_severity_from_findings(self, findings: List[Dict]) -> str:
        """从发现列表中确定整体严重程度"""
        if not findings:
            return "low"

        severities = [f.get("severity", "low") for f in findings]
        if "critical" in severities:
            return "critical"
        if "high" in severities:
            return "high"
        if "medium" in severities:
            return "medium"
        return "low"

    def _build_actions_from_findings(self, findings: List[Dict]) -> List[Dict]:
        """根据发现构建操作按钮"""
        actions = [
            {"label": "查看详情", "action": "view_report", "data": {}},
            {
                "label": "继续对话",
                "action": "start_conversation",
                "data": {"prompt": "请详细解释这个问题"},
            },
            {"label": "已知悉", "action": "dismiss", "data": {}},
        ]

        # 如果有高优先级发现，可以添加特定操作
        if findings:
            first_finding = findings[0]
            finding_type = first_finding.get("type", "")
            if "借单" in finding_type:
                actions[1]["data"]["prompt"] = f"请详细分析{first_finding.get('title', '借单问题')}的原因"
            elif "返工" in finding_type:
                actions[1]["data"]["prompt"] = "如何降低返工率？有哪些具体建议？"
            elif "分散" in finding_type:
                actions[1]["data"]["prompt"] = "工作分散的问题应该如何改善？"

        return actions

    def _try_parse_json_from_response(self, response: str) -> Optional[Dict]:
        """尝试从响应文本中解析JSON"""
        if not response:
            return None

        # 尝试找到JSON代码块
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # Markdown JSON代码块
            r'```\s*([\s\S]*?)\s*```',       # 普通代码块
            r'\{[\s\S]*\}',                   # 直接的JSON对象
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                try:
                    if isinstance(match, str):
                        # 清理可能的前后空白
                        cleaned = match.strip()
                        if cleaned.startswith('{'):
                            parsed = json.loads(cleaned)
                            if isinstance(parsed, dict) and ("title" in parsed or "summary" in parsed):
                                return parsed
                except json.JSONDecodeError:
                    continue

        return None

    def _extract_from_text(self, response: str) -> Dict[str, Any]:
        """从文本响应中提取简报数据（旧逻辑，作为回退）"""
        # 检查是否有异常
        has_anomalies = "异常" in response or "超过阈值" in response
        has_critical = "严重" in response or "紧急" in response

        # 确定类型和优先级
        if has_critical:
            briefing_type = "alert"
            priority = "P0"
        elif has_anomalies:
            briefing_type = "insight"
            priority = "P1"
        else:
            briefing_type = "summary"
            priority = "P2"

        # 提取标题（从响应的第一行或生成）
        title = self._extract_title(response)

        # 提取摘要（前3句话）
        summary = self._extract_summary(response)

        # 构建操作按钮
        actions = [
            {"label": "查看详情", "action": "view_report", "data": {}},
            {
                "label": "继续对话",
                "action": "start_conversation",
                "data": {"prompt": "请详细解释这个问题"},
            },
            {"label": "已知悉", "action": "dismiss", "data": {}},
        ]

        return {
            "type": briefing_type,
            "priority": priority,
            "title": title,
            "summary": summary,
            "impact": self._extract_impact(response),
            "actions": actions,
            "metrics": {},
            "findings": [],
            "key_data": {},
        }

    def _extract_title(self, response: str) -> str:
        """提取标题"""
        lines = response.strip().split("\n")

        # 尝试找到标题行（以#开头或第一个非空行）
        for line in lines:
            line = line.strip()
            if line:
                # 移除markdown标题符号
                title = line.lstrip("#").strip()
                # 限制长度
                if len(title) > 50:
                    title = title[:47] + "..."
                return title

        return "研发效能分析结果"

    def _extract_summary(self, response: str, max_sentences: int = 3) -> str:
        """提取摘要"""
        # 简单的句子分割
        sentences = []
        temp = response

        for delimiter in ["。", "！", "？"]:
            temp = temp.replace(delimiter, delimiter + "|||")

        parts = temp.split("|||")
        for part in parts:
            part = part.strip()
            if part and len(part) > 10:  # 忽略太短的句子
                sentences.append(part)
                if len(sentences) >= max_sentences:
                    break

        return "".join(sentences) if sentences else response[:200]

    def _extract_impact(self, response: str) -> Optional[str]:
        """提取影响说明"""
        impact_keywords = ["影响", "可能导致", "风险", "后果"]
        for keyword in impact_keywords:
            if keyword in response:
                # 找到包含关键词的句子
                start = response.find(keyword)
                end = response.find("。", start)
                if end > start:
                    return response[start : end + 1]
        return None

    # ============================================
    # 查询和管理方法
    # ============================================

    async def list_briefings(
        self,
        user_id: str,
        status: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """获取用户的简报列表"""
        if not self.supabase:
            return {"briefings": [], "total": 0, "unread_count": 0}

        try:
            query = (
                self.supabase.table("briefings")
                .select("*", count="exact")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
            )

            if status:
                query = query.eq("status", status)

            if agent_id:
                query = query.eq("agent_id", agent_id)

            result = query.range(offset, offset + limit - 1).execute()

            # 获取未读数量
            unread_result = (
                self.supabase.table("briefings")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("status", "new")
                .execute()
            )

            return {
                "briefings": result.data,
                "total": result.count or 0,
                "unread_count": unread_result.count or 0,
            }
        except Exception as e:
            logger.error(f"Failed to list briefings: {e}")
            return {"briefings": [], "total": 0, "unread_count": 0}

    async def get_briefing(self, briefing_id: str) -> Optional[Dict[str, Any]]:
        """获取简报详情"""
        if not self.supabase:
            return None

        try:
            result = (
                self.supabase.table("briefings")
                .select("*")
                .eq("id", briefing_id)
                .single()
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Failed to get briefing: {e}")
            return None

    async def mark_as_read(self, briefing_id: str) -> bool:
        """标记简报为已读"""
        if not self.supabase:
            return False

        try:
            self.supabase.table("briefings").update(
                {"status": "read", "read_at": datetime.utcnow().isoformat()}
            ).eq("id", briefing_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to mark briefing as read: {e}")
            return False

    async def execute_action(
        self, briefing_id: str, action: str, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行简报操作"""
        briefing = await self.get_briefing(briefing_id)
        if not briefing:
            raise ValueError(f"Briefing not found: {briefing_id}")

        result = {"action": action, "success": True}

        if action == "view_report":
            # 返回完整报告内容
            result["report"] = briefing.get("context_data", {}).get(
                "analysis_result", {}
            )

        elif action == "start_conversation":
            # 将简报添加到对话中（而不是创建新对话）
            if self.conversation_service:
                try:
                    conversation_id = await self.conversation_service.add_briefing_to_conversation(
                        briefing_id=briefing_id,
                        user_id=briefing["user_id"],
                        agent_id=briefing["agent_id"],
                    )
                    result["conversation_id"] = conversation_id
                    logger.info(
                        f"Briefing {briefing_id} added to conversation {conversation_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to add briefing to conversation: {e}"
                    )
                    result["conversation_id"] = None
                    result["success"] = False
                    result["error"] = str(e)
            else:
                logger.warning(
                    "ConversationService not available, returning None for conversation_id"
                )
                result["conversation_id"] = None

        elif action == "dismiss":
            # 标记为已忽略
            await self._update_status(briefing_id, "dismissed")

        # 更新简报状态为已操作
        await self._update_status(briefing_id, "actioned")

        return result

    async def _update_status(self, briefing_id: str, status: str):
        """更新简报状态"""
        if not self.supabase:
            return

        update_data = {"status": status}
        if status == "actioned":
            update_data["actioned_at"] = datetime.utcnow().isoformat()

        self.supabase.table("briefings").update(update_data).eq(
            "id", briefing_id
        ).execute()

    async def delete_briefing(self, briefing_id: str) -> bool:
        """删除简报"""
        if not self.supabase:
            return False

        try:
            self.supabase.table("briefings").delete().eq("id", briefing_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete briefing: {e}")
            return False

    async def get_briefing_report(self, briefing_id: str) -> Optional[Dict[str, Any]]:
        """获取简报关联的完整报告"""
        if not self.supabase:
            return None

        try:
            # 1. 获取briefing
            briefing = await self.get_briefing(briefing_id)
            if not briefing:
                return None

            artifact_id = briefing.get("report_artifact_id")
            if not artifact_id:
                # 如果没有artifact_id，返回context_data中的响应
                context_data = briefing.get("context_data", {})
                analysis_result = context_data.get("analysis_result", {})
                return {
                    "content": analysis_result.get("response", ""),
                    "format": "markdown",
                    "title": briefing.get("title", "分析报告"),
                }

            # 2. 获取artifact
            result = (
                self.supabase.table("artifacts")
                .select("*")
                .eq("id", artifact_id)
                .single()
                .execute()
            )

            if not result.data:
                return None

            return {
                "content": result.data.get("content", ""),
                "format": result.data.get("format", "markdown"),
                "title": result.data.get("title", "分析报告"),
                "created_at": result.data.get("created_at"),
            }
        except Exception as e:
            logger.error(f"Failed to get briefing report: {e}")
            return None
