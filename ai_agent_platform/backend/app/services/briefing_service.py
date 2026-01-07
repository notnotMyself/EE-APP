"""
Briefing Service - 简报生成核心服务

负责：
1. 调用 Agent 执行分析任务
2. 让 AI 判断是否值得推送简报
3. 生成简报并存入数据库
"""
import json
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.claude_service import claude_service
from app.services.agent_sdk_client import execute_agent_task
from app.crud.crud_briefing import briefing as briefing_crud, scheduled_job as scheduled_job_crud
from app.crud.crud_agent import agent as agent_crud
from app.schemas.briefing import (
    BriefingCreate, BriefingType, BriefingPriority, BriefingAction
)
from app.db.supabase import get_supabase_admin_client

logger = logging.getLogger(__name__)


class BriefingService:
    """简报生成服务"""

    # =========================================================================
    # 简报判断 Prompt - 核心中的核心
    # =========================================================================
    BRIEFING_DECISION_PROMPT = """
你刚刚完成了数据分析任务。现在请判断是否需要向用户推送简报。

## 信息流铁律

在判断前，请牢记这三条铁律：
1. **一天最多3条** - 不要用无价值信息打扰用户
2. **宁可不发** - 如果不确定是否值得发，就不发
3. **能接上对话** - 用户看完会想问"为什么"或"怎么办"

## 判断标准

只有满足以下条件之一才推送：

| 推送 | 场景示例 |
|------|----------|
| ✅ 推送 | 发现异常：Review积压超过阈值、指标突然恶化 |
| ✅ 推送 | 重要趋势：返工率连续3周上升、效率下降超过20% |
| ✅ 推送 | 可操作机会：发现明确的改进点、建议具体行动 |
| ❌ 不推送 | 数据正常，没有异常 |
| ❌ 不推送 | 变化在正常波动范围内（±10%） |
| ❌ 不推送 | 信息用户已知或无法操作 |
| ❌ 不推送 | 纯粹的"刷存在感"汇总 |

## 分析结果

{analysis_result}

## 输出要求

请以JSON格式返回你的判断。

**如果值得推送**，返回：
```json
{{
  "should_push": true,
  "briefing": {{
    "type": "alert|insight|summary|action",
    "priority": "P0|P1|P2",
    "title": "一句话标题（动词开头，≤30字，像新闻标题）",
    "summary": "问题+影响+行动建议（≤100字）",
    "impact": "对业务的具体影响（≤50字）",
    "actions": [
      {{"label": "深入分析", "action": "start_conversation", "prompt": "请帮我分析..."}},
      {{"label": "查看详情", "action": "view_report"}}
    ],
    "importance_score": 0.0到1.0之间的数字
  }}
}}
```

**如果不值得推送**，返回：
```json
{{
  "should_push": false,
  "reason": "简要说明为什么不推送"
}}
```

## 标题写作指南

好的标题：
- "Review积压严重，5个PR等待超48小时" ✅
- "返工率连续上升，已达18%" ✅
- "platform模块效率下降30%，建议关注" ✅

差的标题：
- "本周研发效能周报" ❌（太模板化）
- "代码审查数据分析结果" ❌（没有信息量）
- "系统正常运行" ❌（不值得推送）

请直接返回JSON，不要添加其他说明。
"""

    async def execute_and_generate_briefing(
        self,
        db: AsyncSession,
        agent_id: UUID,
        task_prompt: str,
        briefing_config: Dict[str, Any],
        target_user_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """
        执行分析并生成简报

        Args:
            db: 数据库会话
            agent_id: Agent ID
            task_prompt: 任务提示词
            briefing_config: 简报配置
            target_user_ids: 目标用户ID列表（None则推送给所有订阅用户）

        Returns:
            {
                "analysis_completed": True,
                "briefing_generated": True/False,
                "briefing_count": 0,
                "reason": "...",
                "briefing_ids": [...]
            }
        """
        logger.info(f"Starting briefing generation for agent {agent_id}")

        try:
            # 1. 获取 Agent 配置 (使用 Supabase 客户端)
            supabase = get_supabase_admin_client()
            agent_result = supabase.table('agents').select('*').eq('id', str(agent_id)).execute()

            if not agent_result.data:
                return {"error": f"Agent not found: {agent_id}"}

            agent = agent_result.data[0]

            # 2. 执行 Agent 分析任务
            analysis_result = await self._execute_agent_analysis(
                agent_name=agent['name'],
                agent_role=agent['role'],
                agent_description=agent.get('description', ''),
                task_prompt=task_prompt
            )

            logger.info(f"Analysis completed, length: {len(analysis_result)}")

            # 3. 让 AI 判断是否需要生成简报
            min_importance = briefing_config.get('min_importance_score', 0.6)
            briefing_decision = await self._decide_briefing(
                analysis_result=analysis_result,
                min_importance_score=min_importance
            )

            if not briefing_decision.get('should_push'):
                logger.info(f"Briefing not needed: {briefing_decision.get('reason')}")
                return {
                    "analysis_completed": True,
                    "briefing_generated": False,
                    "briefing_count": 0,
                    "reason": briefing_decision.get('reason', 'Not important enough'),
                    "analysis_result": analysis_result[:500]  # 保留部分分析结果用于调试
                }

            # 4. 检查今日简报配额 (使用 Supabase)
            max_daily = briefing_config.get('max_daily_briefings', 3)
            today = date.today().isoformat()
            count_result = supabase.table('briefings').select('id', count='exact').eq(
                'agent_id', str(agent_id)
            ).gte('created_at', f"{today}T00:00:00").execute()
            today_count = count_result.count or 0

            if today_count >= max_daily:
                logger.warning(f"Daily quota exceeded: {today_count}/{max_daily}")
                return {
                    "analysis_completed": True,
                    "briefing_generated": False,
                    "briefing_count": 0,
                    "reason": f"Daily briefing quota exceeded ({today_count}/{max_daily})"
                }

            # 5. 获取目标用户
            users = await self._get_target_users(agent_id, target_user_ids)

            if not users:
                logger.warning("No target users found")
                return {
                    "analysis_completed": True,
                    "briefing_generated": False,
                    "briefing_count": 0,
                    "reason": "No subscribed users found"
                }

            # 6. 为每个用户创建简报 (使用 Supabase)
            briefing_data = briefing_decision['briefing']
            briefing_ids = []

            for user in users:
                briefing_id = await self._create_briefing_for_user_supabase(
                    agent_id=agent_id,
                    user_id=UUID(user['user_id']),
                    briefing_data=briefing_data,
                    context_data={
                        'analysis_result': analysis_result,
                        'task_prompt': task_prompt,
                        'generated_at': datetime.utcnow().isoformat()
                    }
                )
                briefing_ids.append(str(briefing_id))

            logger.info(f"Generated {len(briefing_ids)} briefings")

            return {
                "analysis_completed": True,
                "briefing_generated": True,
                "briefing_count": len(briefing_ids),
                "briefing_ids": briefing_ids,
                "briefing_title": briefing_data.get('title')
            }

        except Exception as e:
            logger.error(f"Error in execute_and_generate_briefing: {e}", exc_info=True)
            return {
                "analysis_completed": False,
                "briefing_generated": False,
                "error": str(e)
            }

    async def _execute_agent_analysis(
        self,
        agent_name: str,
        agent_role: str,
        agent_description: str,
        task_prompt: str
    ) -> str:
        """使用 Claude Agent SDK 执行分析任务"""
        try:
            # 使用 Agent SDK 执行任务
            result = await execute_agent_task(
                agent_role=agent_role,
                task_prompt=task_prompt,
                allowed_tools=["Bash", "Read", "Write", "Grep", "Glob"],
                timeout=300
            )

            logger.info(f"Agent {agent_role} analysis completed")
            return result

        except Exception as e:
            logger.error(f"Agent analysis failed: {e}", exc_info=True)
            # 降级到旧方法（可选）
            logger.warning("Falling back to legacy claude_service")

            system_prompt = claude_service.build_agent_system_prompt(
                agent_name=agent_name,
                agent_role=agent_role,
                agent_description=agent_description
            )

            messages = [{"role": "user", "content": task_prompt}]
            result = await claude_service.chat_completion(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=4096
            )

            return result

    async def _decide_briefing(
        self,
        analysis_result: str,
        min_importance_score: float
    ) -> Dict[str, Any]:
        """让 AI 判断是否需要生成简报"""
        prompt = self.BRIEFING_DECISION_PROMPT.format(
            analysis_result=analysis_result
        )

        messages = [{"role": "user", "content": prompt}]

        response = await claude_service.chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.3  # 降低随机性，让判断更稳定
        )

        # 解析 JSON 响应
        try:
            # 提取 JSON 部分（处理可能的 markdown 代码块）
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0]
            else:
                # 尝试找到 JSON 对象
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]

            decision = json.loads(json_str.strip())

            # 检查重要性分数
            if decision.get('should_push'):
                importance = decision.get('briefing', {}).get('importance_score', 0)
                if isinstance(importance, str):
                    importance = float(importance)
                if importance < min_importance_score:
                    return {
                        "should_push": False,
                        "reason": f"Importance score {importance} below threshold {min_importance_score}"
                    }

            return decision

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse briefing decision: {response[:500]}")
            return {
                "should_push": False,
                "reason": f"Failed to parse AI response: {str(e)}"
            }

    async def _get_target_users(
        self,
        agent_id: UUID,
        target_user_ids: Optional[List[UUID]]
    ) -> List[Dict[str, Any]]:
        """获取目标用户列表"""
        supabase = get_supabase_admin_client()

        if target_user_ids:
            # 指定用户
            result = supabase.table('user_agent_subscriptions').select(
                'user_id'
            ).in_(
                'user_id', [str(uid) for uid in target_user_ids]
            ).eq('agent_id', str(agent_id)).eq('is_active', True).execute()
        else:
            # 所有订阅用户
            result = supabase.table('user_agent_subscriptions').select(
                'user_id'
            ).eq('agent_id', str(agent_id)).eq('is_active', True).execute()

        return result.data if result.data else []

    async def _create_briefing_for_user(
        self,
        db: AsyncSession,
        agent_id: UUID,
        user_id: UUID,
        briefing_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> UUID:
        """为用户创建简报"""
        # 解析简报类型
        type_map = {
            'alert': BriefingType.ALERT,
            'insight': BriefingType.INSIGHT,
            'summary': BriefingType.SUMMARY,
            'action': BriefingType.ACTION
        }

        priority_map = {
            'P0': BriefingPriority.P0,
            'P1': BriefingPriority.P1,
            'P2': BriefingPriority.P2
        }

        # 解析 actions
        actions = []
        for action_data in briefing_data.get('actions', []):
            actions.append(BriefingAction(
                label=action_data.get('label', '查看'),
                action=action_data.get('action', 'view_report'),
                data=action_data.get('data'),
                prompt=action_data.get('prompt')
            ))

        # 获取重要性分数
        importance_score = briefing_data.get('importance_score', 0.5)
        if isinstance(importance_score, str):
            importance_score = float(importance_score)

        briefing_create = BriefingCreate(
            agent_id=agent_id,
            user_id=user_id,
            briefing_type=type_map.get(briefing_data.get('type', 'insight'), BriefingType.INSIGHT),
            priority=priority_map.get(briefing_data.get('priority', 'P2'), BriefingPriority.P2),
            title=briefing_data.get('title', '新简报'),
            summary=briefing_data.get('summary', ''),
            impact=briefing_data.get('impact'),
            actions=actions,
            context_data=context_data,
            importance_score=Decimal(str(importance_score))
        )

        created = await briefing_crud.create(db, obj_in=briefing_create)
        return created.id

    async def _create_briefing_for_user_supabase(
        self,
        agent_id: UUID,
        user_id: UUID,
        briefing_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> UUID:
        """为用户创建简报 (使用 Supabase)"""
        import uuid

        # 获取重要性分数
        importance_score = briefing_data.get('importance_score', 0.5)
        if isinstance(importance_score, str):
            importance_score = float(importance_score)

        briefing_record = {
            'id': str(uuid.uuid4()),
            'agent_id': str(agent_id),
            'user_id': str(user_id),
            'briefing_type': briefing_data.get('type', 'insight'),
            'priority': briefing_data.get('priority', 'P2'),
            'title': briefing_data.get('title', '新简报'),
            'summary': briefing_data.get('summary', ''),
            'impact': briefing_data.get('impact'),
            'actions': briefing_data.get('actions', []),
            'context_data': context_data,
            'importance_score': importance_score,
            'status': 'new'
        }

        supabase = get_supabase_admin_client()
        result = supabase.table('briefings').insert(briefing_record).execute()

        return UUID(result.data[0]['id'])


# 单例实例
briefing_service = BriefingService()
