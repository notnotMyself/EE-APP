"""
任务意图识别模块 - Task Intent Recognizer

从用户消息中识别任务指令并提取参数。
支持数据分析、报告生成、监控设置三种任务类型。
"""

import re
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class TaskIntent:
    """任务意图数据类"""

    task_type: str  # 'data_analysis' | 'monitoring_setup' | 'report_generation'
    task_prompt: str  # 提取的任务描述
    agent_role: Optional[str] = None  # 从对话上下文推断
    schedule_config: Optional[Dict[str, Any]] = None  # 仅监控任务


# 任务识别模式（规则匹配）
TASK_PATTERNS = {
    "data_analysis": [
        r"分析.*数据",
        r"查看.*指标",
        r"帮我.*统计",
        r"统计.*数据",
        r"分析.*情况",
        r"查看.*趋势",
        r"对比.*数据",
    ],
    "report_generation": [
        r"生成.*报告",
        r"导出.*报告",
        r"生成.*周报",
        r"生成.*月报",
        r"生成.*总结",
        r"给我.*报告",
    ],
    "monitoring_setup": [
        r"每(天|周|月).*推送",
        r"定时.*提醒",
        r"监控.*变化",
        r"每(天|周|月).*发送",
        r"每(天|周|月).*生成",
        r"定期.*推送",
    ],
}

# 时间范围提取模式
TIME_RANGE_PATTERNS = {
    "今天": lambda: {"start": "today", "end": "today"},
    "昨天": lambda: {"start": "yesterday", "end": "yesterday"},
    "最近(\d+)天": lambda m: {
        "start": f"-{m.group(1)}d",
        "end": "today",
    },
    "最近一周": lambda: {"start": "-7d", "end": "today"},
    "最近一月": lambda: {"start": "-30d", "end": "today"},
    "本周": lambda: {"start": "this_week_start", "end": "today"},
    "上周": lambda: {"start": "last_week_start", "end": "last_week_end"},
    "本月": lambda: {"start": "this_month_start", "end": "today"},
    "上月": lambda: {"start": "last_month_start", "end": "last_month_end"},
}


class TaskIntentRecognizer:
    """任务意图识别器

    使用规则匹配识别用户消息中的任务指令。
    Phase 3 将升级为AI分析。
    """

    def __init__(self):
        """初始化识别器"""
        self.patterns = TASK_PATTERNS
        self.time_patterns = TIME_RANGE_PATTERNS

    async def recognize(
        self, message: str, conversation_context: Optional[Dict[str, Any]] = None
    ) -> Optional[TaskIntent]:
        """识别任务意图

        Args:
            message: 用户消息
            conversation_context: 对话上下文（包含agent_id等）

        Returns:
            TaskIntent对象，如果不是任务指令则返回None
        """
        # 1. 模式匹配
        task_type = self._match_patterns(message)
        if not task_type:
            return None

        # 2. 提取参数
        params = self._extract_task_params(message, task_type, conversation_context)

        logger.info(
            f"Recognized task intent: {task_type}, "
            f"prompt: {params['task_prompt'][:50]}..."
        )

        return TaskIntent(
            task_type=task_type,
            task_prompt=params["task_prompt"],
            agent_role=params.get("agent_role"),
            schedule_config=params.get("schedule_config"),
        )

    def _match_patterns(self, message: str) -> Optional[str]:
        """规则匹配

        Args:
            message: 用户消息

        Returns:
            任务类型，如果不匹配任何模式则返回None
        """
        for task_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    logger.debug(f"Matched pattern '{pattern}' for type '{task_type}'")
                    return task_type

        return None

    def _extract_task_params(
        self,
        message: str,
        task_type: str,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """提取任务参数

        Args:
            message: 用户消息
            task_type: 任务类型
            conversation_context: 对话上下文

        Returns:
            参数字典，包含task_prompt、agent_role、schedule_config等
        """
        params: Dict[str, Any] = {}

        # 1. 提取agent_role（从对话上下文）
        if conversation_context and "agent_id" in conversation_context:
            params["agent_role"] = conversation_context["agent_id"]

        # 2. 构建任务提示词
        params["task_prompt"] = self._build_task_prompt(message, task_type)

        # 3. 如果是监控任务，提取调度配置
        if task_type == "monitoring_setup":
            params["schedule_config"] = self._extract_schedule_config(message)

        return params

    def _build_task_prompt(self, message: str, task_type: str) -> str:
        """构建任务提示词

        将用户原始消息转换为适合Agent执行的任务描述。

        Args:
            message: 用户消息
            task_type: 任务类型

        Returns:
            任务提示词
        """
        # 提取时间范围
        time_range = self._extract_time_range(message)

        # 根据任务类型构建prompt
        if task_type == "data_analysis":
            # 数据分析任务
            prompt = f"""
请分析以下数据请求：

用户请求：{message}
时间范围：{time_range if time_range else "最近7天"}

请执行数据分析，包括：
1. 从数据源获取相关数据
2. 进行统计分析
3. 识别异常和趋势
4. 生成结构化的分析结果

输出格式要求：
- 标题：简洁描述分析主题
- 摘要：3-5句话总结关键发现
- 详细分析：包含数据、图表、趋势说明
- 影响：对团队的影响说明
- 建议：可操作的改进建议
"""

        elif task_type == "report_generation":
            # 报告生成任务
            prompt = f"""
请生成以下报告：

用户请求：{message}
时间范围：{time_range if time_range else "最近7天"}

请生成完整的分析报告，包括：
1. 执行概况（总体数据统计）
2. 关键指标分析
3. 趋势变化说明
4. 问题识别
5. 改进建议

输出格式要求：
- 使用Markdown格式
- 包含数据表格和图表说明
- 结构清晰，易于理解
"""

        elif task_type == "monitoring_setup":
            # 监控设置任务
            prompt = f"""
用户请求设置定时监控：

请求内容：{message}

这是一个定时任务设置请求。
系统将为用户创建定时任务，定期执行数据分析并推送简报。

请确认以下信息：
1. 监控内容：需要分析哪些数据
2. 频率：每天/每周/每月
3. 推送时间：具体时间点

（注：实际任务创建由系统处理，此处仅用于意图确认）
"""

        else:
            # 默认使用原始消息
            prompt = message

        return prompt.strip()

    def _extract_time_range(self, message: str) -> Optional[str]:
        """提取时间范围

        Args:
            message: 用户消息

        Returns:
            时间范围描述字符串，如"昨天"、"最近7天"
        """
        for pattern, handler in self.time_patterns.items():
            match = re.search(pattern, message)
            if match:
                if callable(handler):
                    # Check if handler expects parameters by looking at argument count
                    time_config = handler(match) if handler.__code__.co_argcount > 0 else handler()
                    # 返回人类可读的描述
                    if "start" in time_config:
                        return self._format_time_range(time_config)

        return None

    def _format_time_range(self, time_config: Dict[str, str]) -> str:
        """格式化时间范围为人类可读格式

        Args:
            time_config: 时间配置，如 {"start": "-7d", "end": "today"}

        Returns:
            格式化的时间范围描述
        """
        start = time_config.get("start", "")
        end = time_config.get("end", "")

        if start == "today" and end == "today":
            return "今天"
        elif start == "yesterday" and end == "yesterday":
            return "昨天"
        elif start.startswith("-") and end == "today":
            days = start.replace("-", "").replace("d", "")
            return f"最近{days}天"
        elif start == "this_week_start":
            return "本周"
        elif start == "last_week_start":
            return "上周"
        elif start == "this_month_start":
            return "本月"
        elif start == "last_month_start":
            return "上月"
        else:
            return f"{start} 至 {end}"

    def _extract_schedule_config(self, message: str) -> Optional[Dict[str, Any]]:
        """提取调度配置（用于监控任务）

        Args:
            message: 用户消息

        Returns:
            调度配置字典，包含frequency、time等
        """
        config: Dict[str, Any] = {}

        # 提取频率
        if re.search(r"每天", message):
            config["frequency"] = "daily"
        elif re.search(r"每周", message):
            config["frequency"] = "weekly"
            # 提取星期几
            weekday_match = re.search(r"每周([一二三四五六日天])", message)
            if weekday_match:
                weekday_map = {
                    "一": 1,
                    "二": 2,
                    "三": 3,
                    "四": 4,
                    "五": 5,
                    "六": 6,
                    "日": 0,
                    "天": 0,
                }
                config["weekday"] = weekday_map.get(weekday_match.group(1), 1)
        elif re.search(r"每月", message):
            config["frequency"] = "monthly"
            # 提取日期
            day_match = re.search(r"每月(\d+)号", message)
            if day_match:
                config["day_of_month"] = int(day_match.group(1))
            else:
                config["day_of_month"] = 1  # 默认每月1号

        # 提取时间
        time_match = re.search(r"(\d{1,2})[点时:：](\d{0,2})", message)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            config["time"] = f"{hour:02d}:{minute:02d}"
        else:
            # 默认时间
            if "早上" in message or "上午" in message:
                config["time"] = "09:00"
            elif "下午" in message:
                config["time"] = "14:00"
            elif "晚上" in message:
                config["time"] = "19:00"
            else:
                config["time"] = "09:00"  # 默认早上9点

        return config if config else None
