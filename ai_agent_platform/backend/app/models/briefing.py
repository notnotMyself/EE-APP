"""
Briefing SQLAlchemy model.
AI员工简报模型 - 存储AI员工主动推送的简报信息
"""
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class Briefing(Base):
    """AI员工简报模型"""
    __tablename__ = "briefings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 关联关系
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 简报类型: alert(警报), insight(洞察), summary(摘要), action(待办)
    briefing_type = Column(String(20), nullable=False, default='insight')

    # 优先级: P0(紧急), P1(重要), P2(普通)
    priority = Column(String(5), nullable=False, default='P2')

    # 简报内容
    title = Column(String(100), nullable=False)  # 一句话标题
    summary = Column(Text, nullable=False)  # 2-3句摘要
    impact = Column(Text, nullable=True)  # 影响说明

    # 可操作按钮配置
    actions = Column(JSONB, default=list)

    # 关联的完整报告
    report_artifact_id = Column(UUID(as_uuid=True), ForeignKey("artifacts.id", ondelete="SET NULL"), nullable=True)

    # 关联的对话 (点击简报后创建)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)

    # 原始数据/上下文
    context_data = Column(JSONB, default=dict)

    # 状态: new(新), read(已读), actioned(已处理), dismissed(已忽略)
    status = Column(String(20), nullable=False, default='new')

    # 重要性分数 (0.0-1.0)
    importance_score = Column(Numeric(3, 2), default=0.5)

    # 去重哈希（新增）
    content_hash = Column(String(64), nullable=True)  # MD5/SHA256 哈希，用于快速去重

    # 时间戳
    read_at = Column(DateTime(timezone=True), nullable=True)
    actioned_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # 元数据 (renamed to avoid SQLAlchemy reserved word)
    extra_metadata = Column("metadata", JSONB, default=dict)


class ScheduledJob(Base):
    """定时任务配置模型"""
    __tablename__ = "scheduled_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 关联的Agent
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)

    # 任务模板（新增）
    template_id = Column(String(100), ForeignKey("task_templates.id", ondelete="SET NULL"), nullable=True)
    task_type = Column(String(30), nullable=True)  # 从模板继承的任务类型

    # 任务标识
    job_name = Column(String(100), nullable=False)
    job_type = Column(String(50), nullable=False)

    # 调度配置
    schedule_type = Column(String(20), nullable=False, default='cron')
    cron_expression = Column(String(100), nullable=True)
    interval_seconds = Column(String, nullable=True)
    timezone = Column(String(50), default='Asia/Shanghai')

    # 任务提示词
    task_prompt = Column(Text, nullable=False)

    # 简报生成配置
    briefing_config = Column(JSONB, default={
        "enabled": True,
        "min_importance_score": 0.6,
        "max_daily_briefings": 3
    })

    # 实例级配置（新增）
    instance_config = Column(JSONB, default={})  # 覆盖模板默认值的配置
    last_run_context = Column(JSONB, default={})  # 上次执行上下文（用于去重、趋势对比）

    # 目标用户
    target_user_ids = Column(JSONB, nullable=True)  # UUID数组

    # 状态
    is_active = Column(Boolean, default=True, nullable=False)

    # 执行记录
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    last_result = Column(JSONB, nullable=True)
    run_count = Column(String, default='0')
    success_count = Column(String, default='0')
    failure_count = Column(String, default='0')

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
