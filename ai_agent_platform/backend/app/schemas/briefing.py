"""
Briefing Pydantic schemas for request/response validation.
AI员工简报相关的请求/响应模型
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class BriefingType(str, Enum):
    """简报类型枚举"""
    ALERT = "alert"       # 异常警报
    INSIGHT = "insight"   # 趋势洞察
    SUMMARY = "summary"   # 周期摘要
    ACTION = "action"     # 待办建议


class BriefingPriority(str, Enum):
    """优先级枚举"""
    P0 = "P0"  # 紧急
    P1 = "P1"  # 重要
    P2 = "P2"  # 普通


class BriefingStatus(str, Enum):
    """简报状态枚举"""
    NEW = "new"           # 新简报（未读）
    READ = "read"         # 已读
    ACTIONED = "actioned" # 已处理
    DISMISSED = "dismissed"  # 已忽略


class BriefingAction(BaseModel):
    """简报操作按钮"""
    label: str = Field(..., description="按钮显示文本")
    action: str = Field(..., description="操作类型: view_report, start_conversation, dismiss, custom")
    data: Optional[Dict[str, Any]] = Field(default=None, description="操作附加数据")
    prompt: Optional[str] = Field(default=None, description="预填的对话提示（用于start_conversation）")


# =============================================================================
# Briefing Schemas
# =============================================================================

class BriefingBase(BaseModel):
    """简报基础字段"""
    briefing_type: BriefingType = Field(default=BriefingType.INSIGHT)
    priority: BriefingPriority = Field(default=BriefingPriority.P2)
    title: str = Field(..., min_length=1, max_length=100, description="一句话标题")
    summary: str = Field(..., min_length=1, description="2-3句摘要")
    impact: Optional[str] = Field(default=None, description="影响说明")
    actions: List[BriefingAction] = Field(default_factory=list, description="操作按钮列表")


class BriefingCreate(BriefingBase):
    """创建简报的请求模型"""
    agent_id: UUID
    user_id: UUID
    report_artifact_id: Optional[UUID] = None
    context_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    importance_score: Optional[Decimal] = Field(default=Decimal("0.5"), ge=0, le=1)
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BriefingUpdate(BaseModel):
    """更新简报的请求模型"""
    status: Optional[BriefingStatus] = None
    conversation_id: Optional[UUID] = None


class Briefing(BriefingBase):
    """完整简报模型（数据库返回）"""
    id: UUID
    agent_id: UUID
    user_id: UUID
    report_artifact_id: Optional[UUID]
    conversation_id: Optional[UUID]
    context_data: Dict[str, Any]
    status: BriefingStatus
    importance_score: float  # 使用 float 确保 JSON 序列化为数字而非字符串
    read_at: Optional[datetime]
    actioned_at: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class BriefingWithAgent(Briefing):
    """带Agent信息的简报（用于列表展示）"""
    agent_name: Optional[str] = None
    agent_avatar_url: Optional[str] = None
    agent_role: Optional[str] = None


class BriefingListResponse(BaseModel):
    """简报列表响应"""
    items: List[BriefingWithAgent]
    total: int
    unread_count: int


class BriefingUnreadCount(BaseModel):
    """未读简报数量"""
    count: int
    by_priority: Dict[str, int] = Field(default_factory=dict)


class StartConversationRequest(BaseModel):
    """从简报开始对话的请求"""
    prompt: Optional[str] = Field(default=None, description="预填的问题（可选）")


class StartConversationResponse(BaseModel):
    """开始对话的响应"""
    conversation_id: UUID
    briefing_id: UUID


# =============================================================================
# ScheduledJob Schemas
# =============================================================================

class ScheduleType(str, Enum):
    """调度类型"""
    CRON = "cron"
    INTERVAL = "interval"


class BriefingConfig(BaseModel):
    """简报生成配置"""
    enabled: bool = True
    min_importance_score: float = Field(default=0.6, ge=0, le=1)
    max_daily_briefings: int = Field(default=3, ge=1, le=10)


class ScheduledJobBase(BaseModel):
    """定时任务基础字段"""
    job_name: str = Field(..., min_length=1, max_length=100)
    job_type: str = Field(..., min_length=1, max_length=50)
    schedule_type: ScheduleType = Field(default=ScheduleType.CRON)
    cron_expression: Optional[str] = Field(default=None, description="Cron表达式，如 '0 9 * * *'")
    interval_seconds: Optional[int] = Field(default=None, ge=60, description="间隔秒数")
    timezone: str = Field(default="Asia/Shanghai")
    task_prompt: str = Field(..., min_length=1, description="任务提示词")
    briefing_config: BriefingConfig = Field(default_factory=BriefingConfig)
    target_user_ids: Optional[List[UUID]] = None


class ScheduledJobCreate(ScheduledJobBase):
    """创建定时任务的请求"""
    agent_id: UUID


class ScheduledJobUpdate(BaseModel):
    """更新定时任务的请求"""
    job_name: Optional[str] = None
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    task_prompt: Optional[str] = None
    briefing_config: Optional[BriefingConfig] = None
    target_user_ids: Optional[List[UUID]] = None
    is_active: Optional[bool] = None


class ScheduledJob(ScheduledJobBase):
    """完整定时任务模型"""
    id: UUID
    agent_id: UUID
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    last_result: Optional[Dict[str, Any]]
    run_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduledJobWithAgent(ScheduledJob):
    """带Agent信息的定时任务"""
    agent_name: Optional[str] = None
    agent_role: Optional[str] = None


class TriggerJobRequest(BaseModel):
    """手动触发任务的请求"""
    dry_run: bool = Field(default=False, description="是否为试运行（不实际生成简报）")


class TriggerJobResponse(BaseModel):
    """触发任务的响应"""
    job_id: UUID
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None
