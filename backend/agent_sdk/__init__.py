"""
Agent SDK Module

基于 Claude Agent SDK 的 Agent 服务封装层。
提供任务管理、消息持久化、MCP 工具集成、Session 管理等功能。
"""

from .config import AgentSDKConfig
from .exceptions import (
    AgentSDKError,
    TaskExecutionError,
    ToolExecutionError,
    ConfigurationError,
)
from .agent_sdk_service import AgentSDKService, MessageBuffer
from .task_manager import TaskManager
from .session import (
    MessageQueue,
    AgentSession,
    SessionManager,
    get_session_manager,
    init_session_manager,
)

__all__ = [
    "AgentSDKConfig",
    "AgentSDKService",
    "MessageBuffer",
    "TaskManager",
    "AgentSDKError",
    "TaskExecutionError",
    "ToolExecutionError",
    "ConfigurationError",
    # Session management
    "MessageQueue",
    "AgentSession",
    "SessionManager",
    "get_session_manager",
    "init_session_manager",
]
