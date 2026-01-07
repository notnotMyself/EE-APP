"""
TaskTemplate SQLAlchemy model.
任务模板模型 - 定义可复用的任务配置
"""
from sqlalchemy import Boolean, Column, String, DateTime, Text, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base_class import Base


class TaskType(str, PyEnum):
    """任务类型枚举"""
    MONITORING = "monitoring"  # 监控型任务：盯住指标，超过阈值报警
    TREND_ANALYSIS = "trend_analysis"  # 趋势分析型：分析一段时间的数据，发现趋势变化
    REALTIME_INSIGHT = "realtime_insight"  # 实时洞察型：持续扫描新数据，发现新机会/风险
    CUSTOM_ANALYSIS = "custom_analysis"  # 定制分析型：用户发起的一次性深度分析


class ScheduleType(str, PyEnum):
    """调度类型枚举"""
    CRON = "cron"  # 固定时间执行（如每天9am）
    INTERVAL = "interval"  # 固定间隔执行（如每6小时）
    MANUAL = "manual"  # 手动触发


class TaskTemplate(Base):
    """任务模板模型

    定义可复用的任务配置模板，支持：
    - 变量插值（Jinja2 语法）
    - 三层配置（系统级 → 模板级 → 实例级）
    - 多种任务类型
    - 灵活的调度策略
    """
    __tablename__ = "task_templates"

    # 主键：使用可读的字符串 ID，如 'tmpl_daily_monitoring'
    id = Column(String(100), primary_key=True)

    # 基本信息
    name = Column(String(200), nullable=False)  # 模板名称
    description = Column(Text, nullable=True)  # 详细描述
    task_type = Column(String(30), nullable=False)  # 任务类型

    # 适用范围
    applicable_agent_types = Column(ARRAY(String), nullable=False)  # 适用的 Agent 角色列表

    # Prompt 模板（支持 Jinja2 变量插值）
    prompt_template = Column(Text, nullable=False)

    # 配置
    default_config = Column(JSONB, nullable=False, default={})  # 默认配置
    schedule_config = Column(JSONB, nullable=False, default={})  # 调度配置

    # 状态
    is_active = Column(Boolean, nullable=False, default=True)

    # 创建者（可选，如果需要权限控制）
    # created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 约束
    __table_args__ = (
        CheckConstraint(
            task_type.in_(['monitoring', 'trend_analysis', 'realtime_insight', 'custom_analysis']),
            name='valid_task_type'
        ),
    )

    def __repr__(self):
        return f"<TaskTemplate(id={self.id}, name={self.name}, type={self.task_type})>"

    @property
    def schedule_type(self) -> ScheduleType:
        """获取调度类型"""
        schedule_type_str = self.schedule_config.get('type', 'cron')
        return ScheduleType(schedule_type_str)

    @property
    def is_cron_scheduled(self) -> bool:
        """是否为 Cron 调度"""
        return self.schedule_type == ScheduleType.CRON

    @property
    def is_interval_scheduled(self) -> bool:
        """是否为 Interval 调度"""
        return self.schedule_type == ScheduleType.INTERVAL

    def is_applicable_for_agent(self, agent_role: str) -> bool:
        """判断模板是否适用于指定 Agent"""
        return agent_role in self.applicable_agent_types

    def get_cron_expression(self) -> str | None:
        """获取 Cron 表达式"""
        if self.is_cron_scheduled:
            return self.schedule_config.get('expression')
        return None

    def get_interval_minutes(self) -> int | None:
        """获取 Interval 间隔（分钟）"""
        if self.is_interval_scheduled:
            hours = self.schedule_config.get('hours', 0)
            minutes = self.schedule_config.get('minutes', 0)
            return hours * 60 + minutes
        return None

    def merge_config(self, instance_config: dict = None) -> dict:
        """合并配置：default_config + instance_config

        Args:
            instance_config: 实例级配置（可选）

        Returns:
            合并后的配置字典
        """
        merged = dict(self.default_config)
        if instance_config:
            merged.update(instance_config)
        return merged
