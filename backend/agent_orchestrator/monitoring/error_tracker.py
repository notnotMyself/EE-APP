"""
Error Tracker - 错误追踪和监控

提供系统级错误追踪、告警阈值和错误统计功能。
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import threading

logger = logging.getLogger(__name__)


@dataclass
class ErrorRecord:
    """单条错误记录"""
    error_type: str
    message: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


class ErrorTracker:
    """错误追踪器 - 监控系统异常

    Features:
    - 按类型统计错误
    - 保留最近错误用于调试
    - 自动告警阈值
    - 线程安全
    """

    # 告警阈值配置
    ALERT_THRESHOLD = 10  # 每种错误达到此数量时告警
    MAX_ERRORS_PER_TYPE = 100  # 每种错误最多保留条数
    RETENTION_HOURS = 24  # 错误记录保留时间

    def __init__(self):
        self._errors: Dict[str, List[ErrorRecord]] = defaultdict(list)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
        self._last_cleanup: datetime = datetime.utcnow()

    def track_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录错误

        Args:
            error_type: 错误类型（如 "database_error", "api_timeout"）
            error_message: 错误信息
            context: 上下文信息（可选）
        """
        with self._lock:
            self._error_counts[error_type] += 1

            record = ErrorRecord(
                error_type=error_type,
                message=error_message,
                timestamp=datetime.utcnow(),
                context=context or {},
            )
            self._errors[error_type].append(record)

            # 限制内存：每种错误最多保留 MAX_ERRORS_PER_TYPE 条
            if len(self._errors[error_type]) > self.MAX_ERRORS_PER_TYPE:
                self._errors[error_type] = self._errors[error_type][-self.MAX_ERRORS_PER_TYPE:]

            # 告警阈值检查
            if self._error_counts[error_type] % self.ALERT_THRESHOLD == 0:
                logger.warning(
                    f"[ALERT] Error '{error_type}' occurred {self._error_counts[error_type]} times"
                )

            # 定期清理过期记录
            self._maybe_cleanup()

    def _maybe_cleanup(self) -> None:
        """清理过期错误记录"""
        now = datetime.utcnow()
        if now - self._last_cleanup < timedelta(hours=1):
            return

        self._last_cleanup = now
        cutoff = now - timedelta(hours=self.RETENTION_HOURS)

        for error_type in list(self._errors.keys()):
            self._errors[error_type] = [
                e for e in self._errors[error_type]
                if e.timestamp > cutoff
            ]

    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要

        Returns:
            包含总错误数、错误类型数、Top错误的字典
        """
        with self._lock:
            return {
                "total_errors": sum(self._error_counts.values()),
                "error_types": len(self._error_counts),
                "top_errors": sorted(
                    self._error_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5],
                "recent_errors": self._get_recent_errors(10),
            }

    def _get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的错误记录"""
        all_errors: List[ErrorRecord] = []
        for errors in self._errors.values():
            all_errors.extend(errors)

        # 按时间倒序
        all_errors.sort(key=lambda x: x.timestamp, reverse=True)

        return [
            {
                "type": e.error_type,
                "message": e.message,
                "timestamp": e.timestamp.isoformat(),
                "context": e.context,
            }
            for e in all_errors[:limit]
        ]

    def get_errors_by_type(self, error_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取特定类型的错误

        Args:
            error_type: 错误类型
            limit: 返回数量限制

        Returns:
            错误记录列表
        """
        with self._lock:
            errors = self._errors.get(error_type, [])
            return [
                {
                    "message": e.message,
                    "timestamp": e.timestamp.isoformat(),
                    "context": e.context,
                }
                for e in errors[-limit:]
            ]

    def reset(self) -> None:
        """重置所有统计（用于测试）"""
        with self._lock:
            self._errors.clear()
            self._error_counts.clear()

    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态（用于健康检查）

        Returns:
            健康状态字典，包含状态和详情
        """
        summary = self.get_error_summary()

        # 根据错误数量判断健康状态
        total_errors = summary["total_errors"]
        if total_errors == 0:
            status = "healthy"
        elif total_errors < 50:
            status = "ok"
        elif total_errors < 200:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "total_errors": total_errors,
            "error_types": summary["error_types"],
            "top_errors": summary["top_errors"],
        }


# 全局 error_tracker 实例
error_tracker = ErrorTracker()


def track_error(error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """便捷函数：记录错误到全局追踪器"""
    error_tracker.track_error(error_type, error_message, context)


def get_error_summary() -> Dict[str, Any]:
    """便捷函数：获取全局错误摘要"""
    return error_tracker.get_error_summary()
