"""API v1 package."""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, agents, subscriptions, conversations, briefings

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(briefings.router, prefix="/briefings", tags=["briefings"])
