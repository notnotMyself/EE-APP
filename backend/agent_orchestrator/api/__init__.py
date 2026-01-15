"""
API路由模块
"""

from .briefings import router as briefings_router
from .scheduled_jobs import router as scheduled_jobs_router
from .conversations import router as conversations_router
from .profile import router as profile_router
from .notifications import router as notifications_router

__all__ = [
    "briefings_router",
    "scheduled_jobs_router",
    "conversations_router",
    "profile_router",
    "notifications_router",
]
