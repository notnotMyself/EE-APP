"""
Agent SDK 异常定义
"""

from typing import Optional, Dict, Any


class AgentSDKError(Exception):
    """Agent SDK 错误基类"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class ConfigurationError(AgentSDKError):
    """配置错误"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, {"config_key": config_key} if config_key else None)
        self.config_key = config_key


class TaskExecutionError(AgentSDKError):
    """任务执行错误"""

    def __init__(
        self,
        task_id: str,
        message: str,
        phase: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {"task_id": task_id}
        if phase:
            details["phase"] = phase
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(f"Task {task_id} failed: {message}", details)
        self.task_id = task_id
        self.phase = phase
        self.original_error = original_error


class ToolExecutionError(AgentSDKError):
    """工具执行错误"""

    def __init__(
        self,
        tool_name: str,
        message: str,
        input_data: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {"tool_name": tool_name}
        if input_data:
            details["input"] = input_data
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(f"Tool {tool_name} failed: {message}", details)
        self.tool_name = tool_name
        self.input_data = input_data
        self.original_error = original_error


class AgentNotFoundError(AgentSDKError):
    """Agent 角色不存在"""

    def __init__(self, role: str):
        super().__init__(f"Agent role '{role}' not found", {"role": role})
        self.role = role


class TaskNotFoundError(AgentSDKError):
    """任务不存在"""

    def __init__(self, task_id: str):
        super().__init__(f"Task '{task_id}' not found", {"task_id": task_id})
        self.task_id = task_id


class TaskCancelledError(AgentSDKError):
    """任务被取消"""

    def __init__(self, task_id: str):
        super().__init__(f"Task '{task_id}' was cancelled", {"task_id": task_id})
        self.task_id = task_id


class TaskTimeoutError(AgentSDKError):
    """任务超时"""

    def __init__(self, task_id: str, timeout_seconds: int):
        super().__init__(
            f"Task '{task_id}' timed out after {timeout_seconds} seconds",
            {"task_id": task_id, "timeout_seconds": timeout_seconds},
        )
        self.task_id = task_id
        self.timeout_seconds = timeout_seconds
