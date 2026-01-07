"""
CRUD operations for Briefing and ScheduledJob models.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.briefing import Briefing, ScheduledJob
from app.models.agent import Agent
from app.schemas.briefing import (
    BriefingCreate, BriefingUpdate, BriefingStatus,
    ScheduledJobCreate, ScheduledJobUpdate
)


class CRUDBriefing:
    """CRUD operations for briefings."""

    async def get(self, db: AsyncSession, briefing_id: UUID) -> Optional[Briefing]:
        """Get briefing by ID."""
        result = await db.execute(
            select(Briefing).where(Briefing.id == briefing_id)
        )
        return result.scalar_one_or_none()

    async def get_with_agent(
        self,
        db: AsyncSession,
        briefing_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get briefing with agent info."""
        result = await db.execute(
            select(Briefing, Agent.name, Agent.avatar_url, Agent.role)
            .join(Agent, Briefing.agent_id == Agent.id)
            .where(Briefing.id == briefing_id)
        )
        row = result.first()
        if not row:
            return None

        briefing, agent_name, agent_avatar_url, agent_role = row
        return {
            **briefing.__dict__,
            "agent_name": agent_name,
            "agent_avatar_url": agent_avatar_url,
            "agent_role": agent_role
        }

    async def get_user_briefings(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        status: Optional[BriefingStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's briefings with agent info."""
        query = (
            select(Briefing, Agent.name, Agent.avatar_url, Agent.role)
            .join(Agent, Briefing.agent_id == Agent.id)
            .where(Briefing.user_id == user_id)
        )

        if status:
            query = query.where(Briefing.status == status.value)

        query = query.order_by(Briefing.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        rows = result.all()

        briefings = []
        for briefing, agent_name, agent_avatar_url, agent_role in rows:
            briefings.append({
                **{k: v for k, v in briefing.__dict__.items() if not k.startswith('_')},
                "agent_name": agent_name,
                "agent_avatar_url": agent_avatar_url,
                "agent_role": agent_role
            })

        return briefings

    async def count_user_briefings(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        status: Optional[BriefingStatus] = None
    ) -> int:
        """Count user's briefings."""
        query = select(func.count(Briefing.id)).where(Briefing.user_id == user_id)

        if status:
            query = query.where(Briefing.status == status.value)

        result = await db.execute(query)
        return result.scalar() or 0

    async def get_unread_count(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Dict[str, int]:
        """Get unread briefing count by priority."""
        # 总未读数
        total_result = await db.execute(
            select(func.count(Briefing.id))
            .where(and_(
                Briefing.user_id == user_id,
                Briefing.status == BriefingStatus.NEW.value
            ))
        )
        total = total_result.scalar() or 0

        # 按优先级统计
        priority_result = await db.execute(
            select(Briefing.priority, func.count(Briefing.id))
            .where(and_(
                Briefing.user_id == user_id,
                Briefing.status == BriefingStatus.NEW.value
            ))
            .group_by(Briefing.priority)
        )
        by_priority = {row[0]: row[1] for row in priority_result.all()}

        return {
            "count": total,
            "by_priority": by_priority
        }

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: BriefingCreate
    ) -> Briefing:
        """Create a new briefing."""
        db_obj = Briefing(
            agent_id=obj_in.agent_id,
            user_id=obj_in.user_id,
            briefing_type=obj_in.briefing_type.value,
            priority=obj_in.priority.value,
            title=obj_in.title,
            summary=obj_in.summary,
            impact=obj_in.impact,
            actions=[a.model_dump() for a in obj_in.actions],
            report_artifact_id=obj_in.report_artifact_id,
            context_data=obj_in.context_data,
            importance_score=obj_in.importance_score,
            expires_at=obj_in.expires_at,
            metadata=obj_in.metadata,
            status=BriefingStatus.NEW.value
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def mark_as_read(
        self,
        db: AsyncSession,
        briefing_id: UUID
    ) -> Optional[Briefing]:
        """Mark briefing as read."""
        briefing = await self.get(db, briefing_id)
        if briefing and briefing.status == BriefingStatus.NEW.value:
            briefing.status = BriefingStatus.READ.value
            briefing.read_at = datetime.utcnow()
            db.add(briefing)
            await db.commit()
            await db.refresh(briefing)
        return briefing

    async def mark_as_actioned(
        self,
        db: AsyncSession,
        briefing_id: UUID,
        conversation_id: Optional[UUID] = None
    ) -> Optional[Briefing]:
        """Mark briefing as actioned."""
        briefing = await self.get(db, briefing_id)
        if briefing:
            briefing.status = BriefingStatus.ACTIONED.value
            briefing.actioned_at = datetime.utcnow()
            if conversation_id:
                briefing.conversation_id = conversation_id
            db.add(briefing)
            await db.commit()
            await db.refresh(briefing)
        return briefing

    async def dismiss(
        self,
        db: AsyncSession,
        briefing_id: UUID
    ) -> Optional[Briefing]:
        """Dismiss a briefing."""
        briefing = await self.get(db, briefing_id)
        if briefing:
            briefing.status = BriefingStatus.DISMISSED.value
            db.add(briefing)
            await db.commit()
            await db.refresh(briefing)
        return briefing

    async def count_agent_daily_briefings(
        self,
        db: AsyncSession,
        agent_id: UUID,
        target_date: date = None
    ) -> int:
        """Count briefings generated by agent today."""
        if target_date is None:
            target_date = date.today()

        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        result = await db.execute(
            select(func.count(Briefing.id))
            .where(and_(
                Briefing.agent_id == agent_id,
                Briefing.created_at >= start_of_day,
                Briefing.created_at <= end_of_day
            ))
        )
        return result.scalar() or 0


class CRUDScheduledJob:
    """CRUD operations for scheduled jobs."""

    async def get(self, db: AsyncSession, job_id: UUID) -> Optional[ScheduledJob]:
        """Get scheduled job by ID."""
        result = await db.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        agent_id: UUID,
        job_name: str
    ) -> Optional[ScheduledJob]:
        """Get scheduled job by agent and name."""
        result = await db.execute(
            select(ScheduledJob).where(and_(
                ScheduledJob.agent_id == agent_id,
                ScheduledJob.job_name == job_name
            ))
        )
        return result.scalar_one_or_none()

    async def get_active_jobs(self, db: AsyncSession) -> List[ScheduledJob]:
        """Get all active scheduled jobs."""
        result = await db.execute(
            select(ScheduledJob)
            .where(ScheduledJob.is_active == True)
            .order_by(ScheduledJob.next_run_at)
        )
        return result.scalars().all()

    async def get_agent_jobs(
        self,
        db: AsyncSession,
        agent_id: UUID
    ) -> List[ScheduledJob]:
        """Get all jobs for an agent."""
        result = await db.execute(
            select(ScheduledJob)
            .where(ScheduledJob.agent_id == agent_id)
            .order_by(ScheduledJob.created_at.desc())
        )
        return result.scalars().all()

    async def get_all_with_agent(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all jobs with agent info."""
        result = await db.execute(
            select(ScheduledJob, Agent.name, Agent.role)
            .join(Agent, ScheduledJob.agent_id == Agent.id)
            .order_by(ScheduledJob.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = result.all()

        jobs = []
        for job, agent_name, agent_role in rows:
            jobs.append({
                **{k: v for k, v in job.__dict__.items() if not k.startswith('_')},
                "agent_name": agent_name,
                "agent_role": agent_role
            })

        return jobs

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: ScheduledJobCreate
    ) -> ScheduledJob:
        """Create a new scheduled job."""
        db_obj = ScheduledJob(
            agent_id=obj_in.agent_id,
            job_name=obj_in.job_name,
            job_type=obj_in.job_type,
            schedule_type=obj_in.schedule_type.value,
            cron_expression=obj_in.cron_expression,
            interval_seconds=obj_in.interval_seconds,
            timezone=obj_in.timezone,
            task_prompt=obj_in.task_prompt,
            briefing_config=obj_in.briefing_config.model_dump(),
            target_user_ids=obj_in.target_user_ids,
            is_active=True
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ScheduledJob,
        obj_in: ScheduledJobUpdate
    ) -> ScheduledJob:
        """Update a scheduled job."""
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'briefing_config' in update_data and update_data['briefing_config']:
            update_data['briefing_config'] = update_data['briefing_config'].model_dump()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_run_status(
        self,
        db: AsyncSession,
        job_id: UUID,
        *,
        success: bool,
        result: Dict[str, Any],
        next_run_at: Optional[datetime] = None
    ) -> Optional[ScheduledJob]:
        """Update job after execution."""
        job = await self.get(db, job_id)
        if job:
            job.last_run_at = datetime.utcnow()
            job.last_result = result
            job.run_count = int(job.run_count or 0) + 1

            if success:
                job.success_count = int(job.success_count or 0) + 1
            else:
                job.failure_count = int(job.failure_count or 0) + 1

            if next_run_at:
                job.next_run_at = next_run_at

            db.add(job)
            await db.commit()
            await db.refresh(job)

        return job

    async def deactivate(
        self,
        db: AsyncSession,
        job_id: UUID
    ) -> Optional[ScheduledJob]:
        """Deactivate a scheduled job."""
        job = await self.get(db, job_id)
        if job:
            job.is_active = False
            db.add(job)
            await db.commit()
            await db.refresh(job)
        return job


# Singleton instances
briefing = CRUDBriefing()
scheduled_job = CRUDScheduledJob()
