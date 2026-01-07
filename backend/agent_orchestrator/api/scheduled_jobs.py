"""
定时任务管理API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/scheduled-jobs", tags=["scheduled_jobs"])

# 全局引用，由main.py注入
scheduler_service = None
supabase_client = None


def set_scheduler_service(service):
    """设置调度器服务实例"""
    global scheduler_service
    scheduler_service = service


def set_supabase_client(client):
    """设置Supabase客户端"""
    global supabase_client
    supabase_client = client


# ============================================
# 数据模型
# ============================================


class ScheduledJobResponse(BaseModel):
    id: str
    agent_id: str
    job_name: str
    job_type: str
    schedule_type: str
    cron_expression: Optional[str]
    interval_seconds: Optional[int]
    is_active: bool
    last_run_at: Optional[str]
    next_run_at: Optional[str]
    run_count: int
    success_count: int
    failure_count: int

    class Config:
        from_attributes = True


class CreateJobRequest(BaseModel):
    agent_id: str
    job_name: str
    job_type: str = "daily_analysis"
    schedule_type: str = "cron"
    cron_expression: Optional[str] = "0 9 * * *"
    interval_seconds: Optional[int] = None
    task_prompt: str
    briefing_config: dict = {
        "enabled": True,
        "min_importance_score": 0.6,
        "max_daily_briefings": 3,
    }


class RunJobResponse(BaseModel):
    job_id: str
    status: str
    briefings_created: int
    start_time: str
    end_time: str
    error: Optional[str] = None


# ============================================
# API端点
# ============================================


@router.get("", response_model=List[dict])
async def list_scheduled_jobs(
    agent_id: Optional[str] = Query(None, description="过滤Agent ID"),
    is_active: Optional[bool] = Query(None, description="过滤是否激活"),
):
    """列出所有定时任务"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        query = supabase_client.table("scheduled_jobs").select("*")

        if agent_id:
            query = query.eq("agent_id", agent_id)

        if is_active is not None:
            query = query.eq("is_active", is_active)

        result = query.execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}")
async def get_scheduled_job(job_id: str):
    """获取定时任务详情"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        result = (
            supabase_client.table("scheduled_jobs")
            .select("*")
            .eq("id", job_id)
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Job not found")
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict)
async def create_scheduled_job(request: CreateJobRequest):
    """创建定时任务"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        job_data = {
            "agent_id": request.agent_id,
            "job_name": request.job_name,
            "job_type": request.job_type,
            "schedule_type": request.schedule_type,
            "cron_expression": request.cron_expression,
            "interval_seconds": request.interval_seconds,
            "task_prompt": request.task_prompt,
            "briefing_config": request.briefing_config,
            "is_active": True,
        }

        result = supabase_client.table("scheduled_jobs").insert(job_data).execute()
        return result.data[0] if result.data else job_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/run")
async def run_job_now(job_id: str):
    """立即执行一次定时任务（用于测试）"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")

    try:
        result = await scheduler_service.run_job_now(job_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{job_id}/toggle")
async def toggle_job(job_id: str, is_active: bool = Query(...)):
    """启用/禁用定时任务"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        result = (
            supabase_client.table("scheduled_jobs")
            .update({"is_active": is_active})
            .eq("id", job_id)
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"status": "success", "job_id": job_id, "is_active": is_active}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """删除定时任务"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        supabase_client.table("scheduled_jobs").delete().eq("id", job_id).execute()
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/running/status")
async def get_scheduler_status():
    """获取调度器状态"""
    if not scheduler_service:
        return {"status": "not_initialized", "jobs": []}

    jobs = scheduler_service.get_jobs()
    return {"status": "running", "jobs": jobs}
