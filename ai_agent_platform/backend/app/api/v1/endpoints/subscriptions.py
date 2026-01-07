"""
Subscription API endpoints.
使用 Supabase Client 替代 SQLAlchemy 直连。
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user
from app.crud.crud_subscription_supabase import subscription_supabase as crud_subscription
from app.crud.crud_agent_supabase import agent_supabase as crud_agent
from app.schemas.subscription import (
    Subscription,
    SubscriptionCreate,
    SubscriptionUpdate,
)
from app.schemas.user import CurrentUser

router = APIRouter()


@router.get("/", response_model=List[Subscription])
async def list_my_subscriptions(
    active_only: bool = True,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get current user's subscriptions.

    - **active_only**: Only return active subscriptions
    """
    subscriptions = await crud_subscription.get_user_subscriptions(
        user_id=current_user.id, active_only=active_only
    )
    return subscriptions


@router.get("/{subscription_id}", response_model=Subscription)
async def get_subscription(
    subscription_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get subscription details by ID.
    """
    subscription = await crud_subscription.get(subscription_id=subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Check ownership
    if str(subscription.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this subscription"
        )

    return subscription


@router.post("/", response_model=Subscription, status_code=status.HTTP_201_CREATED)
async def subscribe_to_agent(
    subscription_in: SubscriptionCreate,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Subscribe to an AI agent.

    If a previous subscription exists (inactive), it will be reactivated.
    """
    # Check if agent exists and is active
    agent = await crud_agent.get(agent_id=subscription_in.agent_id)
    if not agent or not agent.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not active"
        )

    # Check if active subscription already exists
    existing = await crud_subscription.get_user_subscription(
        user_id=current_user.id, agent_id=subscription_in.agent_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already subscribed to this agent"
        )

    # Try to reactivate inactive subscription
    reactivated = await crud_subscription.resubscribe(
        user_id=current_user.id, agent_id=subscription_in.agent_id
    )
    if reactivated:
        return reactivated

    # Create new subscription
    subscription = await crud_subscription.create(
        user_id=current_user.id,
        obj_in=subscription_in.model_dump()
    )
    return subscription


@router.put("/{subscription_id}", response_model=Subscription)
async def update_subscription(
    subscription_id: UUID,
    subscription_in: SubscriptionUpdate,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Update subscription settings.
    """
    subscription = await crud_subscription.get(subscription_id=subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Check ownership
    if str(subscription.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this subscription"
        )

    updated = await crud_subscription.update(
        subscription_id=subscription_id,
        obj_in=subscription_in.model_dump(exclude_unset=True)
    )
    return updated


@router.delete("/{agent_id}", response_model=Subscription)
async def unsubscribe_from_agent(
    agent_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Unsubscribe from an AI agent.

    This is a soft delete - the subscription is deactivated but not removed.
    """
    subscription = await crud_subscription.unsubscribe(
        user_id=current_user.id, agent_id=agent_id
    )
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    return subscription


@router.get("/agent/{agent_id}/subscribers-count")
async def get_agent_subscribers_count(
    agent_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get number of subscribers for an agent.
    """
    count = await crud_subscription.count_agent_subscribers(agent_id=agent_id)
    return {"agent_id": agent_id, "subscribers_count": count}
