"""
Briefing Service - 简报生成核心服务

负责：
1. 调用 Agent 执行分析任务
2. 从 Agent 原始输出中提取分析报告（过滤思考过程）
3. 让 AI 判断是否值得推送简报
4. 生成简报并存入数据库
"""
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.claude_service import claude_service
from app.services.agent_sdk_client import execute_agent_task
from app.services.cover_image_service import cover_image_service
from app.crud.crud_briefing import briefing as briefing_crud, scheduled_job as scheduled_job_crud
from app.crud.crud_agent import agent as agent_crud
from app.schemas.briefing import (
    BriefingCreate, BriefingType, BriefingPriority, BriefingAction
)
from app.db.supabase import get_supabase_admin_client
from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# 分析报告提取器 - 从 Agent 原始输出中提取有效内容
# =============================================================================

class AnalysisReportExtractor:
    """
    从 Agent SDK 的原始输出中提取分析报告
    
    Agent 输出通常包含：
    1. 思考过程（"我将执行...", "让我先...", "看起来..."）
    2. 工具调用记录（[tool_use], bash 命令输出等）
    3. 最终的分析报告（Markdown 格式）
    
    我们只需要第3部分。
    """
    
    # 思考过程的典型开头模式
    THINKING_PATTERNS = [
        r'^我将',
        r'^让我',
        r'^首先',
        r'^接下来',
        r'^现在',
        r'^好的',
        r'^看起来',
        r'^需要先',
        r'^我需要',
        r'^我来',
        r'^我会',
        r'^我要',
        r'^正在',
        r'^开始',
        r'^执行',
        r'^分析',
        r'^获取',
        r'^查询',
        r'^连接',
        r'^尝试',
        r'^检查',
    ]
    
    # 工具调用相关的模式
    TOOL_PATTERNS = [
        r'\[tool_use\]',
        r'\[tool_result\]',
        r'TextBlock\(',
        r'ToolUseBlock\(',
        r'ToolResultBlock\(',
        r'ContentBlock\(',
        r'bash\s*\(',
        r'echo\s+[\'"]?\{',
        r'python\s+\w+\.py',
        r'cd\s+\.claude',
        r'pip\s+install',
    ]
    
    # 有效报告的标志
    REPORT_MARKERS = [
        r'^#+\s+.+',           # Markdown 标题
        r'^\|.+\|.+\|',        # Markdown 表格
        r'^-\s+\*\*.+\*\*',    # 带粗体的列表项
        r'^##\s*📊',           # 带 emoji 的标题
        r'^##\s*🔍',
        r'^##\s*💡',
        r'^##\s*⚠️',
        r'^##\s*🚨',
        r'^##\s*核心指标',
        r'^##\s*异常发现',
        r'^##\s*改进建议',
        r'^##\s*分析结果',
        r'研发效能',
        r'Review.*耗时',
        r'返工率',
        r'代码变更',
    ]
    
    @classmethod
    def extract(cls, raw_output: str) -> Tuple[str, Dict[str, Any]]:
        """
        从原始输出中提取分析报告
        
        Args:
            raw_output: Agent SDK 的原始输出
            
        Returns:
            Tuple[str, Dict]: (提取后的报告, 提取元数据)
        """
        if not raw_output or not raw_output.strip():
            return "", {"status": "empty_input"}
        
        metadata = {
            "original_length": len(raw_output),
            "extraction_method": None,
            "filtered_lines": 0,
            "kept_lines": 0,
        }
        
        # 方法1: 尝试找到 Markdown 报告块
        report = cls._extract_markdown_report(raw_output)
        if report and len(report) > 200:
            metadata["extraction_method"] = "markdown_block"
            metadata["extracted_length"] = len(report)
            return report, metadata
        
        # 方法2: 按行过滤，移除思考过程和工具调用
        report, line_stats = cls._filter_by_lines(raw_output)
        metadata.update(line_stats)
        
        if report and len(report) > 100:
            metadata["extraction_method"] = "line_filter"
            metadata["extracted_length"] = len(report)
            return report, metadata
        
        # 方法3: 如果上述方法都失败，返回清理后的原文
        cleaned = cls._basic_cleanup(raw_output)
        metadata["extraction_method"] = "basic_cleanup"
        metadata["extracted_length"] = len(cleaned)
        
        return cleaned, metadata
    
    @classmethod
    def _extract_markdown_report(cls, text: str) -> Optional[str]:
        """
        尝试提取完整的 Markdown 报告块
        
        查找以 # 开头的报告标题，一直到文末或下一个明显的分隔
        """
        lines = text.split('\n')
        report_start = -1
        report_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 查找报告开始标志
            if report_start < 0:
                # 匹配 # 研发效能, # 分析报告, # 每日分析 等
                if re.match(r'^#+\s*(研发效能|分析报告|效能分析|每日分析|日报|周报)', stripped):
                    report_start = i
                    report_lines.append(line)
                # 或者匹配 --- 分隔符后的 # 标题
                elif stripped == '---' and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if re.match(r'^#+\s+', next_line):
                        report_start = i
                        report_lines.append(line)
            else:
                # 已经在报告中，检查是否结束
                # 遇到工具调用或思考过程则停止
                is_tool_line = any(re.search(p, stripped, re.IGNORECASE) for p in cls.TOOL_PATTERNS)
                is_thinking = any(re.match(p, stripped) for p in cls.THINKING_PATTERNS[:10])
                
                if is_tool_line or (is_thinking and len(report_lines) > 5):
                    break
                
                report_lines.append(line)
        
        if report_lines:
            return '\n'.join(report_lines).strip()
        
        return None
    
    @classmethod
    def _filter_by_lines(cls, text: str) -> Tuple[str, Dict[str, int]]:
        """
        按行过滤，移除思考过程和工具调用
        """
        lines = text.split('\n')
        kept_lines = []
        filtered_count = 0
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # 跟踪代码块状态
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                # 保留 Markdown 代码块（但不是工具输出的代码块）
                if not any(re.search(p, stripped) for p in cls.TOOL_PATTERNS):
                    kept_lines.append(line)
                continue
            
            # 在代码块内，检查是否是工具输出
            if in_code_block:
                # 跳过明显的工具输出
                if any(re.search(p, stripped, re.IGNORECASE) for p in cls.TOOL_PATTERNS):
                    filtered_count += 1
                    continue
                kept_lines.append(line)
                continue
            
            # 空行保留（用于格式）
            if not stripped:
                kept_lines.append(line)
                continue
            
            # 检查是否是思考过程
            is_thinking = any(re.match(p, stripped) for p in cls.THINKING_PATTERNS)
            
            # 检查是否是工具相关
            is_tool = any(re.search(p, stripped, re.IGNORECASE) for p in cls.TOOL_PATTERNS)
            
            # 检查是否是有效报告内容
            is_report = any(re.search(p, stripped, re.IGNORECASE) for p in cls.REPORT_MARKERS)
            
            # 决定是否保留
            if is_tool:
                filtered_count += 1
            elif is_thinking and not is_report:
                # 如果是思考过程但包含报告关键词，还是保留
                filtered_count += 1
            else:
                kept_lines.append(line)
        
        # 清理连续的空行
        result = '\n'.join(kept_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip(), {
            "filtered_lines": filtered_count,
            "kept_lines": len(kept_lines)
        }
    
    @classmethod
    def _basic_cleanup(cls, text: str) -> str:
        """
        基本清理：移除明显的噪音
        """
        # 移除 TextBlock, ToolUseBlock 等 SDK 输出格式
        text = re.sub(r'TextBlock\(text=[\'"]', '', text)
        text = re.sub(r'ToolUseBlock\([^)]+\)', '', text)
        text = re.sub(r'ToolResultBlock\([^)]+\)', '', text)
        text = re.sub(r'ContentBlock\([^)]+\)', '', text)
        text = re.sub(r'[\'"],?\s*type=[\'"]text[\'"]', '', text)
        text = re.sub(r'\)\s*$', '', text, flags=re.MULTILINE)
        
        # 清理连续空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()


class BriefingService:
    """简报生成服务"""

    # =========================================================================
    # 简报判断 Prompt - 核心中的核心（V2 优化版）
    # =========================================================================
    BRIEFING_DECISION_PROMPT = """
你是一个研发效能分析专家。请根据以下分析结果，判断是否值得向用户推送简报。

## 信息流铁律

1. **一天最多3条** - 不要用无价值信息打扰用户
2. **宁可不发** - 如果不确定是否值得发，就不发
3. **能接上对话** - 用户看完会想问"为什么"或"怎么办"

## 判断标准

| 推送 | 场景示例 |
|------|----------|
| ✅ 推送 | 一次性通过率<50%，返工成本高 |
| ✅ 推送 | 人均活跃分支>15个，工作过于分散 |
| ✅ 推送 | 发现借单异常（1个Story对应>10个change_id） |
| ✅ 推送 | 同分支多次提交异常（反复提交-放弃） |
| ✅ 推送 | 效率趋势恶化超过20% |
| ❌ 不推送 | 各项指标正常，无异常发现 |
| ❌ 不推送 | 数据库连接失败，无有效数据 |
| ❌ 不推送 | 纯粹的数字罗列，没有洞察 |

## 分析结果

{analysis_result}

## 输出要求

请以JSON格式返回，**必须严格按照以下格式**：

**如果值得推送**：
```json
{{
  "should_push": true,
  "briefing": {{
    "type": "insight",
    "priority": "P1",
    "title": "一次性通过率仅33.9%，团队返工成本较高",
    "summary": "最近7天分析显示，代码一次性通过率仅33.9%，总返工次数达45126次。人均活跃分支25.9个，工作分散度较高。建议：1）加强代码自测，提高一次性通过率；2）减少分支切换，聚焦核心任务。",
    "impact": "返工导致约30%的开发时间浪费",
    "actions": [
      {{"label": "为什么会这样？", "action": "start_conversation", "prompt": "请详细分析返工率高的原因，哪些模块或人员返工最多？"}},
      {{"label": "给我详细分析", "action": "start_conversation", "prompt": "请给我完整的时间效率损耗分析报告"}},
      {{"label": "如何改进？", "action": "start_conversation", "prompt": "针对当前的效率问题，请给出具体的改进建议和优先级"}}
    ],
    "importance_score": 0.85
  }}
}}
```

**如果不值得推送**：
```json
{{
  "should_push": false,
  "reason": "各项指标正常，无需推送"
}}
```

## 标题写作指南（非常重要！）

**好的标题**（说清核心发现，有数字支撑）：
- "一次性通过率仅33.9%，团队返工成本较高" ✅
- "人均活跃分支25.9个，工作过于分散" ✅
- "发现412个疑似借单Story，需要关注" ✅
- "系统开发部返工率下降15%，效率提升" ✅

**差的标题**（绝对不要这样写）：
- "本周研发效能周报" ❌
- "我将执行每日研发效能分析" ❌
- "代码审查数据分析结果" ❌
- "未知" ❌

## Summary 写作指南（非常重要！）

Summary 必须包含三要素：**发现 + 影响 + 建议**

**好的 Summary 示例**：
"最近7天分析显示，代码一次性通过率仅33.9%，总返工次数达45126次。人均活跃分支25.9个，工作分散度较高。建议：1）加强代码自测，提高一次性通过率；2）减少分支切换，聚焦核心任务。"

**差的 Summary**（绝对不要这样写）：
- "我将执行每日研发效能分析，按照流程获取数据并分析关键指标" ❌
- "看来需要先了解数据库中实际存在的表结构" ❌

请直接返回JSON，不要添加任何其他说明文字。
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
            raw_analysis_result = await self._execute_agent_analysis(
                agent_name=agent['name'],
                agent_role=agent['role'],
                agent_description=agent.get('description', ''),
                task_prompt=task_prompt
            )

            logger.info(f"Raw analysis completed, length: {len(raw_analysis_result)}")

            # 2.5 【关键步骤】从原始输出中提取分析报告
            # Agent SDK 返回的内容包含思考过程、工具调用等噪音
            # 这里提取出真正的分析报告
            analysis_result, extraction_meta = AnalysisReportExtractor.extract(raw_analysis_result)
            
            logger.info(
                f"Report extracted: method={extraction_meta.get('extraction_method')}, "
                f"original={extraction_meta.get('original_length')}, "
                f"extracted={extraction_meta.get('extracted_length')}"
            )
            
            # 如果提取后的内容太短，可能提取失败
            if len(analysis_result) < 50:
                logger.warning(f"Extracted report too short ({len(analysis_result)} chars), using raw output")
                analysis_result = raw_analysis_result[:4000]  # 限制长度

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
                    "analysis_result": analysis_result[:500],  # 提取后的分析报告（用于调试）
                    "extraction_meta": extraction_meta
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
                        'analysis_result': analysis_result,  # 提取后的报告
                        'raw_output_preview': raw_analysis_result[:1000] if len(raw_analysis_result) > 1000 else raw_analysis_result,  # 原始输出预览
                        'extraction_meta': extraction_meta,
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
        import uuid as uuid_module

        # 获取重要性分数
        importance_score = briefing_data.get('importance_score', 0.5)
        if isinstance(importance_score, str):
            importance_score = float(importance_score)

        # ✨ 生成 AI 封面图（如果启用）
        cover_image_url = None
        enable_cover = getattr(settings, 'ENABLE_AI_COVER_GENERATION', False)
        
        if enable_cover:
            try:
                cover_image_url = await cover_image_service.generate_cover_image(
                    briefing_type=briefing_data.get('type', 'insight'),
                    title=briefing_data.get('title', ''),
                    summary=briefing_data.get('summary', ''),
                    priority=briefing_data.get('priority', 'P2')
                )
                if cover_image_url:
                    logger.info(f"Generated cover image: {cover_image_url[:50]}...")
            except Exception as e:
                logger.warning(f"Failed to generate cover image, using fallback: {e}")
                # 降级到前端渐变背景

        briefing_record = {
            'id': str(uuid_module.uuid4()),
            'agent_id': str(agent_id),
            'user_id': str(user_id),
            'briefing_type': briefing_data.get('type', 'insight'),
            'priority': briefing_data.get('priority', 'P2'),
            'title': briefing_data.get('title', '新简报'),
            'summary': briefing_data.get('summary', ''),
            'impact': briefing_data.get('impact'),
            'actions': briefing_data.get('actions', []),
            'context_data': {
                **context_data,
                'cover_image_url': cover_image_url  # ✨ 封面图 URL
            },
            'importance_score': importance_score,
            'status': 'new'
        }

        supabase = get_supabase_admin_client()
        result = supabase.table('briefings').insert(briefing_record).execute()

        return UUID(result.data[0]['id'])


# 单例实例
briefing_service = BriefingService()
