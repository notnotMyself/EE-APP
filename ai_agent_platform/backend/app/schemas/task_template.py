"""
TaskTemplate Pydantic schemas for request/response validation.
任务模板相关的请求/响应模型
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class TaskType(str, Enum):
    """任务类型枚举"""
    MONITORING = "monitoring"  # 监控型任务：盯住指标，超过阈值报警
    TREND_ANALYSIS = "trend_analysis"  # 趋势分析型：分析一段时间的数据，发现趋势变化
    REALTIME_INSIGHT = "realtime_insight"  # 实时洞察型：持续扫描新数据，发现新机会/风险
    CUSTOM_ANALYSIS = "custom_analysis"  # 定制分析型：用户发起的一次性深度分析


class ScheduleType(str, Enum):
    """调度类型枚举"""
    CRON = "cron"  # 固定时间执行（如每天9am）
    INTERVAL = "interval"  # 固定间隔执行（如每6小时）
    MANUAL = "manual"  # 手动触发


# =============================================================================
# TaskTemplate Schemas
# =============================================================================

class TaskTemplateBase(BaseModel):
    """任务模板基础字段"""
    name: str = Field(..., min_length=1, max_length=200, description="模板名称")
    description: Optional[str] = Field(default=None, description="详细描述")
    task_type: TaskType = Field(..., description="任务类型")
    applicable_agent_types: List[str] = Field(..., min_items=1, description="适用的 Agent 角色列表")
    prompt_template: str = Field(..., min_length=1, description="Prompt 模板（支持 Jinja2 变量插值）")
    default_config: Dict[str, Any] = Field(default_factory=dict, description="默认配置")
    schedule_config: Dict[str, Any] = Field(default_factory=dict, description="调度配置")

    @validator('schedule_config')
    def validate_schedule_config(cls, v):
        """验证 schedule_config 必须包含 type 字段"""
        if not v.get('type'):
            raise ValueError("schedule_config must contain 'type' field")

        schedule_type = v['type']
        if schedule_type not in ['cron', 'interval', 'manual']:
            raise ValueError(f"Invalid schedule type: {schedule_type}")

        # 验证 Cron 配置
        if schedule_type == 'cron':
            if not v.get('expression'):
                raise ValueError("Cron schedule must have 'expression' field")

        # 验证 Interval 配置
        elif schedule_type == 'interval':
            hours = v.get('hours', 0)
            minutes = v.get('minutes', 0)
            if hours <= 0 and minutes <= 0:
                raise ValueError("Interval schedule must have positive 'hours' or 'minutes'")

        return v


class TaskTemplateCreate(TaskTemplateBase):
    """创建任务模板的请求模型"""
    id: Optional[str] = Field(default=None, description="模板ID（可选，如果不提供则自动生成）")
    is_active: bool = Field(default=True, description="是否启用")

    @validator('id')
    def validate_id(cls, v):
        """验证 ID 格式"""
        if v is not None:
            if not v.startswith('tmpl_'):
                raise ValueError("Template ID must start with 'tmpl_'")
            if len(v) > 100:
                raise ValueError("Template ID must not exceed 100 characters")
        return v


class TaskTemplateUpdate(BaseModel):
    """更新任务模板的请求模型"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    applicable_agent_types: Optional[List[str]] = None
    prompt_template: Optional[str] = None
    default_config: Optional[Dict[str, Any]] = None
    schedule_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @validator('schedule_config')
    def validate_schedule_config(cls, v):
        """验证 schedule_config（如果提供）"""
        if v is not None:
            # 重用 TaskTemplateBase 的验证逻辑
            return TaskTemplateBase.__fields__['schedule_config'].validators[0](v)
        return v


class TaskTemplate(TaskTemplateBase):
    """完整任务模板模型（数据库返回）"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TaskTemplateList(BaseModel):
    """任务模板列表响应"""
    items: List[TaskTemplate]
    total: int
    page: int = 1
    page_size: int = 20


# =============================================================================
# TaskTemplate Instantiation (从模板创建任务实例)
# =============================================================================

class TaskInstanceCreate(BaseModel):
    """从模板创建任务实例的请求模型"""
    template_id: str = Field(..., description="任务模板 ID")
    agent_id: str = Field(..., description="关联的 Agent UUID")
    job_name: Optional[str] = Field(default=None, description="任务名称（可选，默认使用模板名称）")
    instance_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="实例级配置（覆盖模板默认值）")
    target_user_ids: Optional[List[str]] = Field(default=None, description="目标用户 UUID 列表")

    @validator('template_id')
    def validate_template_id(cls, v):
        """验证模板 ID 格式"""
        if not v.startswith('tmpl_'):
            raise ValueError("template_id must start with 'tmpl_'")
        return v


class TaskConfigUpdate(BaseModel):
    """动态更新任务配置的请求模型"""
    instance_config: Dict[str, Any] = Field(..., description="要更新的实例配置")


# =============================================================================
# Prompt Rendering (Prompt 渲染)
# =============================================================================

class PromptRenderRequest(BaseModel):
    """渲染 Prompt 的请求模型"""
    template_id: str = Field(..., description="任务模板 ID")
    variables: Dict[str, Any] = Field(default_factory=dict, description="变量字典")


class PromptRenderResponse(BaseModel):
    """渲染 Prompt 的响应模型"""
    rendered_prompt: str = Field(..., description="渲染后的 Prompt")
    variables_used: List[str] = Field(default_factory=list, description="使用的变量列表")
    template_id: str = Field(..., description="模板 ID")


# =============================================================================
# Utility Schemas
# =============================================================================

class TaskTemplateSearchQuery(BaseModel):
    """任务模板搜索查询"""
    task_type: Optional[TaskType] = None
    applicable_agent_type: Optional[str] = None
    is_active: Optional[bool] = None
    search_text: Optional[str] = Field(default=None, description="在 name 和 description 中搜索")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TaskTypeStats(BaseModel):
    """任务类型统计"""
    task_type: TaskType
    count: int
    active_count: int


class TaskTemplateStats(BaseModel):
    """任务模板统计响应"""
    total_templates: int
    active_templates: int
    by_type: List[TaskTypeStats]
    by_schedule_type: Dict[str, int]
