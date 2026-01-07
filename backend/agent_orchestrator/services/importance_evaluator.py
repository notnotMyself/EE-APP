"""
重要性评估器 - 评估分析结果的重要性分数
"""

import re
from typing import Any, Dict


class ImportanceEvaluator:
    """简报重要性评估器"""

    # 关键词权重配置
    CRITICAL_KEYWORDS = {
        "严重": 0.3,
        "紧急": 0.3,
        "P95": 0.2,
        "阻塞": 0.25,
        "堆积": 0.2,
        "critical": 0.3,
        "urgent": 0.3,
    }

    WARNING_KEYWORDS = {
        "异常": 0.15,
        "超过阈值": 0.15,
        "上升": 0.1,
        "下降": 0.1,
        "返工率": 0.1,
        "warning": 0.15,
        "exceeds": 0.15,
    }

    NORMAL_KEYWORDS = {
        "正常": -0.2,
        "稳定": -0.15,
        "良好": -0.15,
        "healthy": -0.2,
        "stable": -0.15,
    }

    async def evaluate(self, analysis_result: Dict[str, Any]) -> float:
        """
        评估分析结果的重要性分数

        返回值范围: 0.0 - 1.0
        - 0.0-0.4: 低价值（不推送）
        - 0.4-0.6: 一般价值（可选推送）
        - 0.6-0.8: 较高价值（推荐推送）
        - 0.8-1.0: 高价值（必须推送）
        """
        base_score = 0.5
        response = analysis_result.get("response", "")

        # 1. 关键词匹配
        keyword_score = self._evaluate_keywords(response)

        # 2. 数值异常检测
        numeric_score = self._evaluate_numeric_anomalies(response)

        # 3. 结构化数据检测（如果有）
        structured_score = self._evaluate_structured_data(analysis_result)

        # 综合得分
        final_score = base_score + keyword_score + numeric_score + structured_score

        # 限制在0-1范围内
        return max(0.0, min(1.0, final_score))

    def _evaluate_keywords(self, text: str) -> float:
        """基于关键词评估"""
        score = 0.0

        for keyword, weight in self.CRITICAL_KEYWORDS.items():
            if keyword in text:
                score += weight

        for keyword, weight in self.WARNING_KEYWORDS.items():
            if keyword in text:
                score += weight

        for keyword, weight in self.NORMAL_KEYWORDS.items():
            if keyword in text:
                score += weight

        return score

    def _evaluate_numeric_anomalies(self, text: str) -> float:
        """基于数值异常评估"""
        score = 0.0

        # 检测百分比异常（如 >15%, >30%）
        percent_pattern = r"(\d+(?:\.\d+)?)\s*%"
        percentages = re.findall(percent_pattern, text)

        for pct in percentages:
            value = float(pct)
            if value > 50:
                score += 0.2
            elif value > 30:
                score += 0.1
            elif value > 15:
                score += 0.05

        # 检测时间异常（如 >24小时, >72小时）
        hour_pattern = r"(\d+(?:\.\d+)?)\s*小时"
        hours = re.findall(hour_pattern, text)

        for h in hours:
            value = float(h)
            if value > 72:
                score += 0.2
            elif value > 24:
                score += 0.1

        return score

    def _evaluate_structured_data(self, analysis_result: Dict[str, Any]) -> float:
        """基于结构化数据评估"""
        # 如果Agent返回了结构化的异常数据
        anomalies = analysis_result.get("anomalies", [])

        if not anomalies:
            return 0.0

        score = 0.0
        for anomaly in anomalies:
            severity = anomaly.get("severity", "info")
            if severity == "critical":
                score += 0.25
            elif severity == "warning":
                score += 0.15
            else:
                score += 0.05

        return min(score, 0.4)  # 最多贡献0.4分
