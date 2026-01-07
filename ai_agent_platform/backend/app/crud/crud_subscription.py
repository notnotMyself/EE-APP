"""
CRUD operations for Subscription model.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime

from app.models.subscription import UserAgentSubscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class CRUDSubscription:
    """CRUD operations for user-agent subscriptions."""

    async def get(self, db: AsyncSession, subscription_id: UUID) -> Optional[UserAgentSubscription]:
        """Get subscription by ID."""
        result = await db.execute(
            select(UserAgentSubscription).where(UserAgentSubscription.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def get_user_subscription(
        self,
        db: AsyncSession,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[UserAgentSubscription]:
        """Get active subscription for a user-agent pair."""
        result = await db.execute(
            select(UserAgentSubscription).where(
                and_(
                    UserAgentSubscription.user_id == user_id,
                    UserAgentSubscription.agent_id == agent_id,
                    UserAgentSubscription.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_subscriptions(
        self,
        db: AsyncSession,
        user_id: UUID,
        active_only: bool = True
    ) -> List[UserAgentSubscription]:
        """Get all subscriptions for a user."""
        query = select(UserAgentSubscription).where(
            UserAgentSubscription.user_id == user_id
        )

        if active_only:
            query = query.where(UserAgentSubscription.is_active == True)

        query = query.order_by(UserAgentSubscription.subscribed_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    async def get_agent_subscribers(
        self,
        db: AsyncSession,
        agent_id: UUID
    ) -> List[UserAgentSubscription]:
        """Get all active subscribers for an agent."""
        result = await db.execute(
            select(UserAgentSubscription).where(
                and_(
                    UserAgentSubscription.agent_id == agent_id,
                    UserAgentSubscription.is_active == True
                )
            )
        )
        return result.scalars().all()

    async def count_agent_subscribers(
        self,
        db: AsyncSession,
        agent_id: UUID
    ) -> int:
        """Count active subscribers for an agent."""
        result = await db.execute(
            select(func.count(UserAgentSubscription.id)).where(
                and_(
                    UserAgentSubscription.agent_id == agent_id,
                    UserAgentSubscription.is_active == True
                )
            )
        )
        return result.scalar()

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        obj_in: SubscriptionCreate
    ) -> UserAgentSubscription:
        """Create a new subscription."""
        db_obj = UserAgentSubscription(
            user_id=user_id,
            agent_id=obj_in.agent_id,
            config=obj_in.config,
            notify_on_alert=obj_in.notify_on_alert,
            notify_via_push=obj_in.notify_via_push,
            notify_via_email=obj_in.notify_via_email,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: UserAgentSubscription,
        obj_in: SubscriptionUpdate
    ) -> UserAgentSubscription:
        """Update a subscription."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def unsubscribe(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[UserAgentSubscription]:
        """Unsubscribe user from agent (soft delete)."""
        subscription = await self.get_user_subscription(db, user_id, agent_id)
        if subscription:
            subscription.is_active = False
            subscription.unsubscribed_at = datetime.utcnow()
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
        return subscription

    async def resubscribe(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[UserAgentSubscription]:
        """Reactivate an inactive subscription."""
        # Find inactive subscription
        result = await db.execute(
            select(UserAgentSubscription).where(
                and_(
                    UserAgentSubscription.user_id == user_id,
                    UserAgentSubscription.agent_id == agent_id,
                    UserAgentSubscription.is_active == False
                )
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.is_active = True
            subscription.subscribed_at = datetime.utcnow()
            subscription.unsubscribed_at = None
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)

        return subscription


# Create singleton instance
subscription = CRUDSubscription()
