"""
TaskTemplate Service - 任务模板服务

负责：
1. 任务模板的 CRUD 操作
2. Prompt 变量插值渲染（Jinja2）
3. 从模板实例化任务
4. 配置合并（系统 → 模板 → 实例）
"""
import logging
import re
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from jinja2 import Template, TemplateSyntaxError, UndefinedError

from app.models.task_template import TaskTemplate, TaskType, ScheduleType
from app.models.briefing import ScheduledJob
from app.schemas.task_template import (
    TaskTemplateCreate,
    TaskTemplateUpdate,
    TaskInstanceCreate,
    TaskConfigUpdate,
    PromptRenderResponse,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class TaskTemplateService:
    """任务模板服务"""

    # =========================================================================
    # CRUD Operations
    # =========================================================================

    @staticmethod
    async def create_template(
        db: AsyncSession,
        template_data: TaskTemplateCreate
    ) -> TaskTemplate:
        """创建任务模板

        Args:
            db: 数据库会话
            template_data: 模板数据

        Returns:
            创建的任务模板

        Raises:
            ValueError: 如果模板 ID 已存在
        """
        # 生成模板 ID（如果未提供）
        if template_data.id is None:
            template_id = TaskTemplateService._generate_template_id(
                template_data.name,
                template_data.task_type
            )
        else:
            template_id = template_data.id

        # 检查 ID 是否已存在
        existing = await db.get(TaskTemplate, template_id)
        if existing:
            raise ValueError(f"Template with ID '{template_id}' already exists")

        # 创建模板
        db_template = TaskTemplate(
            id=template_id,
            name=template_data.name,
            description=template_data.description,
            task_type=template_data.task_type.value,
            applicable_agent_types=template_data.applicable_agent_types,
            prompt_template=template_data.prompt_template,
            default_config=template_data.default_config,
            schedule_config=template_data.schedule_config,
            is_active=template_data.is_active,
        )

        db.add(db_template)
        await db.commit()
        await db.refresh(db_template)

        logger.info(f"Created task template: {template_id}")
        return db_template

    @staticmethod
    async def get_template(
        db: AsyncSession,
        template_id: str
    ) -> Optional[TaskTemplate]:
        """获取任务模板"""
        return await db.get(TaskTemplate, template_id)

    @staticmethod
    async def get_template_or_404(
        db: AsyncSession,
        template_id: str
    ) -> TaskTemplate:
        """获取任务模板（如果不存在则抛出异常）"""
        template = await TaskTemplateService.get_template(db, template_id)
        if template is None:
            raise ValueError(f"Template '{template_id}' not found")
        return template

    @staticmethod
    async def list_templates(
        db: AsyncSession,
        task_type: Optional[TaskType] = None,
        applicable_agent_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_text: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[TaskTemplate], int]:
        """列出任务模板

        Returns:
            (模板列表, 总数)
        """
        query = select(TaskTemplate)

        # 过滤条件
        filters = []
        if task_type is not None:
            filters.append(TaskTemplate.task_type == task_type.value)
        if applicable_agent_type is not None:
            filters.append(TaskTemplate.applicable_agent_types.contains([applicable_agent_type]))
        if is_active is not None:
            filters.append(TaskTemplate.is_active == is_active)
        if search_text:
            search_pattern = f"%{search_text}%"
            filters.append(
                or_(
                    TaskTemplate.name.ilike(search_pattern),
                    TaskTemplate.description.ilike(search_pattern)
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # 计算总数
        count_query = select(func.count()).select_from(TaskTemplate)
        if filters:
            count_query = count_query.where(and_(*filters))
        total = await db.scalar(count_query)

        # 分页
        query = query.order_by(TaskTemplate.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        templates = result.scalars().all()

        return list(templates), total or 0

    @staticmethod
    async def update_template(
        db: AsyncSession,
        template_id: str,
        update_data: TaskTemplateUpdate
    ) -> TaskTemplate:
        """更新任务模板"""
        template = await TaskTemplateService.get_template_or_404(db, template_id)

        # 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(template, field):
                setattr(template, field, value)

        await db.commit()
        await db.refresh(template)

        logger.info(f"Updated task template: {template_id}")
        return template

    @staticmethod
    async def delete_template(
        db: AsyncSession,
        template_id: str
    ) -> None:
        """删除任务模板"""
        template = await TaskTemplateService.get_template_or_404(db, template_id)

        await db.delete(template)
        await db.commit()

        logger.info(f"Deleted task template: {template_id}")

    # =========================================================================
    # Prompt Rendering
    # =========================================================================

    @staticmethod
    async def render_prompt(
        db: AsyncSession,
        template_id: str,
        variables: Dict[str, Any]
    ) -> PromptRenderResponse:
        """渲染 Prompt（使用 Jinja2 变量插值）

        Args:
            db: 数据库会话
            template_id: 模板 ID
            variables: 变量字典

        Returns:
            渲染后的 Prompt

        Raises:
            ValueError: 如果模板语法错误或变量缺失
        """
        template = await TaskTemplateService.get_template_or_404(db, template_id)

        try:
            # 创建 Jinja2 模板
            jinja_template = Template(template.prompt_template)

            # 渲染
            rendered = jinja_template.render(**variables)

            # 提取使用的变量
            variables_used = TaskTemplateService._extract_variables_from_template(
                template.prompt_template
            )

            return PromptRenderResponse(
                rendered_prompt=rendered,
                variables_used=variables_used,
                template_id=template_id
            )

        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in '{template_id}': {e}")
            raise ValueError(f"Template syntax error: {e}")
        except UndefinedError as e:
            logger.error(f"Undefined variable in template '{template_id}': {e}")
            raise ValueError(f"Undefined variable: {e}")
        except Exception as e:
            logger.error(f"Error rendering template '{template_id}': {e}")
            raise ValueError(f"Error rendering template: {e}")

    @staticmethod
    def _extract_variables_from_template(template_str: str) -> List[str]:
        """从模板字符串中提取变量名

        支持 {{variable}} 和 {% for item in items %} 等语法
        """
        # 匹配 {{variable}} 和 {{obj.attr}}
        variable_pattern = r'\{\{\s*(\w+(?:\.\w+)?)\s*\}\}'
        # 匹配 {% for x in y %}
        for_pattern = r'\{%\s*for\s+\w+\s+in\s+(\w+)\s*%\}'

        variables = set()

        # 提取 {{variable}}
        for match in re.finditer(variable_pattern, template_str):
            var_name = match.group(1).split('.')[0]  # 只取第一部分
            variables.add(var_name)

        # 提取 {% for x in y %}
        for match in re.finditer(for_pattern, template_str):
            variables.add(match.group(1))

        return sorted(list(variables))

    # =========================================================================
    # Task Instantiation
    # =========================================================================

    @staticmethod
    async def instantiate_task(
        db: AsyncSession,
        instantiation_data: TaskInstanceCreate
    ) -> ScheduledJob:
        """从模板实例化任务

        Args:
            db: 数据库会话
            instantiation_data: 实例化数据

        Returns:
            创建的 ScheduledJob

        Raises:
            ValueError: 如果模板不存在或不适用于指定 Agent
        """
        # 获取模板
        template = await TaskTemplateService.get_template_or_404(
            db, instantiation_data.template_id
        )

        # 验证模板是否适用于指定 Agent
        # （这里简化处理，实际应查询 Agent 的 role）
        # if not template.is_applicable_for_agent(agent_role):
        #     raise ValueError(f"Template not applicable for agent")

        # 合并配置
        final_config = template.merge_config(instantiation_data.instance_config)

        # 渲染 Prompt
        render_response = await TaskTemplateService.render_prompt(
            db, template.id, final_config
        )

        # 提取调度配置
        schedule_type = template.schedule_config.get('type', 'cron')
        cron_expression = None
        interval_seconds = None

        if schedule_type == 'cron':
            cron_expression = template.schedule_config.get('expression')
        elif schedule_type == 'interval':
            hours = template.schedule_config.get('hours', 0)
            minutes = template.schedule_config.get('minutes', 0)
            interval_seconds = str((hours * 60 + minutes) * 60)

        # 创建 ScheduledJob
        job = ScheduledJob(
            id=uuid.uuid4(),
            template_id=template.id,
            task_type=template.task_type,
            agent_id=uuid.UUID(instantiation_data.agent_id),
            job_name=instantiation_data.job_name or template.name,
            job_type='briefing_generation',  # 默认类型
            schedule_type=schedule_type,
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
            timezone=template.schedule_config.get('timezone', 'Asia/Shanghai'),
            task_prompt=render_response.rendered_prompt,
            instance_config=final_config,
            briefing_config=final_config,  # 简报配置使用合并后的配置
            target_user_ids=instantiation_data.target_user_ids,
            is_active=True,
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)

        logger.info(
            f"Instantiated task from template '{template.id}': "
            f"job_id={job.id}, agent_id={job.agent_id}"
        )

        return job

    @staticmethod
    async def update_task_config(
        db: AsyncSession,
        job_id: uuid.UUID,
        config_update: TaskConfigUpdate
    ) -> ScheduledJob:
        """动态更新任务配置

        Args:
            db: 数据库会话
            job_id: 任务 ID
            config_update: 配置更新

        Returns:
            更新后的 ScheduledJob

        Raises:
            ValueError: 如果任务不存在或没有关联模板
        """
        # 获取任务
        job = await db.get(ScheduledJob, job_id)
        if job is None:
            raise ValueError(f"Job '{job_id}' not found")

        if job.template_id is None:
            raise ValueError(f"Job '{job_id}' is not template-based")

        # 获取模板
        template = await TaskTemplateService.get_template_or_404(db, job.template_id)

        # 合并配置：template.default_config + old instance_config + new config_update
        updated_instance_config = dict(template.default_config)
        updated_instance_config.update(job.instance_config or {})
        updated_instance_config.update(config_update.instance_config)

        # 重新渲染 Prompt
        render_response = await TaskTemplateService.render_prompt(
            db, template.id, updated_instance_config
        )

        # 更新任务
        job.instance_config = updated_instance_config
        job.task_prompt = render_response.rendered_prompt
        job.briefing_config = updated_instance_config

        await db.commit()
        await db.refresh(job)

        logger.info(f"Updated config for job '{job_id}'")

        return job

    # =========================================================================
    # Utility Methods
    # =========================================================================

    @staticmethod
    def _generate_template_id(name: str, task_type: TaskType) -> str:
        """生成模板 ID

        格式：tmpl_{task_type}_{slug}

        Example: tmpl_monitoring_daily_efficiency
        """
        # 创建 slug（只保留字母数字和下划线）
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '_', slug)
        slug = slug[:40]  # 限制长度

        # 组合 ID
        template_id = f"tmpl_{task_type.value}_{slug}"

        # 如果 ID 太长，截断并添加短 UUID
        if len(template_id) > 90:
            short_uuid = str(uuid.uuid4())[:8]
            template_id = f"tmpl_{task_type.value}_{slug[:30]}_{short_uuid}"

        return template_id

    @staticmethod
    async def get_templates_for_agent(
        db: AsyncSession,
        agent_role: str
    ) -> List[TaskTemplate]:
        """获取适用于指定 Agent 的模板列表"""
        query = select(TaskTemplate).where(
            and_(
                TaskTemplate.applicable_agent_types.contains([agent_role]),
                TaskTemplate.is_active == True
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_stats(db: AsyncSession) -> Dict[str, Any]:
        """获取任务模板统计信息"""
        # 总数
        total = await db.scalar(select(func.count()).select_from(TaskTemplate))

        # 活跃数
        active = await db.scalar(
            select(func.count()).select_from(TaskTemplate).where(TaskTemplate.is_active == True)
        )

        # 按类型统计
        by_type_query = select(
            TaskTemplate.task_type,
            func.count().label('count')
        ).group_by(TaskTemplate.task_type)
        by_type_result = await db.execute(by_type_query)
        by_type = {row[0]: row[1] for row in by_type_result}

        return {
            "total_templates": total or 0,
            "active_templates": active or 0,
            "by_type": by_type
        }


# Singleton instance
task_template_service = TaskTemplateService()
