"""
Agent Orchestrator Configuration Module

统一配置管理，包括超时设置、WebSocket配置等。
"""

from .timeouts import TimeoutConfig, get_timeout_config

__all__ = [
    "TimeoutConfig",
    "get_timeout_config",
]
