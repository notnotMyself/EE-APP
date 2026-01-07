"""
研发效能分析工具

提供 Gerrit 查询、效能趋势分析、报告生成等 MCP 工具。
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool

logger = logging.getLogger(__name__)


# ==================== 工具定义 ====================


@tool(
    "gerrit_query",
    "查询 Gerrit 代码审查数据。返回指定项目在指定时间范围内的代码审查统计。",
    {
        "project": str,
        "days": int,
        "status": str,  # "open" | "merged" | "abandoned"
    },
)
async def gerrit_query_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """查询 Gerrit 代码审查数据"""
    project = args.get("project", "all")
    days = args.get("days", 7)
    status = args.get("status", "merged")

    logger.info(f"Querying Gerrit: project={project}, days={days}, status={status}")

    try:
        # 尝试调用真实的 Gerrit API
        data = await _fetch_gerrit_data(project, days, status)
    except Exception as e:
        logger.warning(f"Failed to fetch real Gerrit data: {e}, using mock data")
        # 使用模拟数据
        data = _generate_mock_gerrit_data(project, days, status)

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(data, ensure_ascii=False, indent=2),
            }
        ]
    }


@tool(
    "efficiency_trend",
    "获取效能趋势数据。支持的指标：review_time（审查耗时）、rework_rate（返工率）、throughput（吞吐量）",
    {
        "metric": str,  # "review_time" | "rework_rate" | "throughput"
        "weeks": int,
    },
)
async def efficiency_trend_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """获取效能指标趋势"""
    metric = args.get("metric", "review_time")
    weeks = args.get("weeks", 4)

    logger.info(f"Getting efficiency trend: metric={metric}, weeks={weeks}")

    try:
        data = await _calculate_efficiency_trend(metric, weeks)
    except Exception as e:
        logger.warning(f"Failed to calculate real trend: {e}, using mock data")
        data = _generate_mock_trend_data(metric, weeks)

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(data, ensure_ascii=False, indent=2),
            }
        ]
    }


@tool(
    "generate_report",
    "生成效能分析报告。支持的报告类型：daily（日报）、weekly（周报）、monthly（月报）",
    {
        "report_type": str,  # "daily" | "weekly" | "monthly"
        "format": str,  # "markdown" | "json"
    },
)
async def generate_report_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """生成效能分析报告"""
    report_type = args.get("report_type", "daily")
    output_format = args.get("format", "markdown")

    logger.info(f"Generating report: type={report_type}, format={output_format}")

    try:
        report = await _build_efficiency_report(report_type, output_format)
    except Exception as e:
        logger.warning(f"Failed to build real report: {e}, using mock report")
        report = _generate_mock_report(report_type, output_format)

    return {
        "content": [
            {
                "type": "text",
                "text": report if isinstance(report, str) else json.dumps(report, ensure_ascii=False, indent=2),
            }
        ]
    }


# ==================== 数据获取 ====================


async def _fetch_gerrit_data(
    project: str,
    days: int,
    status: str,
) -> Dict[str, Any]:
    """从 Gerrit API 获取真实数据"""
    import os

    gerrit_url = os.getenv("GERRIT_API_URL")
    if not gerrit_url:
        raise ValueError("GERRIT_API_URL not configured")

    # 构建查询
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    query = f"status:{status}"
    if project != "all":
        query += f" project:{project}"
    query += f" after:{since_date}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{gerrit_url}/changes/",
            params={"q": query, "o": ["DETAILED_ACCOUNTS", "CURRENT_REVISION"]},
        )
        response.raise_for_status()

        # Gerrit API 返回 )]}' 前缀
        text = response.text
        if text.startswith(")]}'"):
            text = text[4:]

        changes = json.loads(text)

    # 处理数据
    return _process_gerrit_changes(changes, project, days, status)


def _process_gerrit_changes(
    changes: List[Dict],
    project: str,
    days: int,
    status: str,
) -> Dict[str, Any]:
    """处理 Gerrit 变更数据"""
    if not changes:
        return {
            "project": project,
            "period": f"最近 {days} 天",
            "status": status,
            "total_reviews": 0,
            "message": "没有找到符合条件的代码审查记录",
        }

    # 计算统计数据
    review_times = []
    reviewers_count = {}

    for change in changes:
        # 计算 review 时间
        if "created" in change and "updated" in change:
            created = datetime.fromisoformat(change["created"].replace("Z", "+00:00"))
            updated = datetime.fromisoformat(change["updated"].replace("Z", "+00:00"))
            hours = (updated - created).total_seconds() / 3600
            review_times.append(hours)

        # 统计 reviewer
        if "reviewers" in change:
            for reviewer in change.get("reviewers", {}).get("REVIEWER", []):
                name = reviewer.get("name", "Unknown")
                reviewers_count[name] = reviewers_count.get(name, 0) + 1

    # 计算指标
    sorted_times = sorted(review_times)
    n = len(sorted_times)

    return {
        "project": project,
        "period": f"最近 {days} 天",
        "status": status,
        "total_reviews": len(changes),
        "avg_review_time_hours": round(sum(review_times) / n, 1) if n > 0 else 0,
        "median_review_time_hours": round(sorted_times[n // 2], 1) if n > 0 else 0,
        "p95_review_time_hours": round(sorted_times[int(n * 0.95)] if n > 0 else 0, 1),
        "top_reviewers": sorted(
            [{"name": k, "reviews": v} for k, v in reviewers_count.items()],
            key=lambda x: x["reviews"],
            reverse=True,
        )[:5],
    }


def _generate_mock_gerrit_data(
    project: str,
    days: int,
    status: str,
) -> Dict[str, Any]:
    """生成模拟的 Gerrit 数据"""
    return {
        "project": project,
        "period": f"最近 {days} 天",
        "status": status,
        "total_reviews": 150,
        "avg_review_time_hours": 18.5,
        "median_review_time_hours": 12.3,
        "p95_review_time_hours": 48.2,
        "rework_rate": "12%",
        "pass_rate": "85%",
        "top_reviewers": [
            {"name": "张三", "reviews": 45},
            {"name": "李四", "reviews": 38},
            {"name": "王五", "reviews": 32},
        ],
        "bottlenecks": [
            "模块 A 的 Review 平均耗时 36 小时，超出阈值",
            "周一的 Review 堆积较多",
        ],
        "_note": "这是模拟数据，请配置 GERRIT_API_URL 获取真实数据",
    }


async def _calculate_efficiency_trend(
    metric: str,
    weeks: int,
) -> Dict[str, Any]:
    """计算效能趋势（真实数据）"""
    # TODO: 实现真实的数据计算
    raise NotImplementedError("Real trend calculation not implemented")


def _generate_mock_trend_data(
    metric: str,
    weeks: int,
) -> Dict[str, Any]:
    """生成模拟的趋势数据"""
    metric_config = {
        "review_time": {"unit": "小时", "values": [20.5, 18.2, 22.1, 18.5, 17.8, 19.2]},
        "rework_rate": {"unit": "%", "values": [15, 12, 14, 11, 10, 12]},
        "throughput": {"unit": "个", "values": [120, 135, 128, 145, 150, 142]},
    }

    config = metric_config.get(metric, metric_config["review_time"])
    trend = [
        {"week": f"W{i + 1}", "value": config["values"][i]}
        for i in range(min(weeks, len(config["values"])))
    ]

    # 分析趋势
    values = [t["value"] for t in trend]
    if len(values) >= 2:
        if values[-1] < values[0]:
            analysis = "整体呈下降趋势，效率有所提升。"
        elif values[-1] > values[0]:
            analysis = "整体呈上升趋势，需要关注。"
        else:
            analysis = "整体保持稳定。"

        # 检测异常
        avg = sum(values) / len(values)
        for i, v in enumerate(values):
            if v > avg * 1.2:
                analysis += f" W{i + 1} 存在异常峰值，建议关注。"
    else:
        analysis = "数据不足，无法分析趋势。"

    return {
        "metric": metric,
        "metric_name": {
            "review_time": "代码审查耗时",
            "rework_rate": "返工率",
            "throughput": "吞吐量",
        }.get(metric, metric),
        "unit": config["unit"],
        "trend": trend,
        "analysis": analysis,
        "_note": "这是模拟数据",
    }


async def _build_efficiency_report(
    report_type: str,
    output_format: str,
) -> str:
    """构建效能报告（真实数据）"""
    # TODO: 实现真实的报告生成
    raise NotImplementedError("Real report generation not implemented")


def _generate_mock_report(
    report_type: str,
    output_format: str,
) -> str:
    """生成模拟报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    report_type_name = {"daily": "日报", "weekly": "周报", "monthly": "月报"}.get(report_type, "报告")

    report_data = {
        "title": f"研发效能{report_type_name} - {today}",
        "key_metrics": {
            "review_median_hours": 12.3,
            "review_median_change": "-8%",
            "rework_rate": "11%",
            "rework_rate_change": "-2%",
            "delivery_cycle_days": 5.2,
            "delivery_cycle_change": "-10%",
        },
        "anomalies": [
            "模块 payment-service 的 Review 中位耗时达到 28 小时，超出阈值",
            "用户 zhangsan 待处理 Review 堆积 15 个",
        ],
        "recommendations": [
            "建议为 payment-service 模块增加 Reviewer 资源",
            "建议 zhangsan 优先处理堆积的 Review",
            "可以考虑引入自动化代码检查减少人工 Review 负担",
        ],
        "generated_at": datetime.now().isoformat(),
    }

    if output_format == "json":
        return json.dumps(report_data, ensure_ascii=False, indent=2)

    # Markdown 格式
    return f"""# {report_data['title']}

## 关键指标

| 指标 | 当前值 | 环比变化 |
|------|--------|----------|
| Review 中位耗时 | {report_data['key_metrics']['review_median_hours']} 小时 | {report_data['key_metrics']['review_median_change']} |
| 返工率 | {report_data['key_metrics']['rework_rate']} | {report_data['key_metrics']['rework_rate_change']} |
| 需求交付周期 | {report_data['key_metrics']['delivery_cycle_days']} 天 | {report_data['key_metrics']['delivery_cycle_change']} |

## 异常发现

{chr(10).join(f"- {a}" for a in report_data['anomalies'])}

## 改进建议

{chr(10).join(f"- {r}" for r in report_data['recommendations'])}

---
*报告生成时间: {report_data['generated_at']}*
*注意: 这是模拟数据，请配置相关 API 获取真实数据*
"""


# ==================== 服务器创建 ====================


def create_dev_efficiency_server():
    """创建研发效能分析 MCP 服务器"""
    return create_sdk_mcp_server(
        name="dev_efficiency",
        version="1.0.0",
        tools=[
            gerrit_query_tool,
            efficiency_trend_tool,
            generate_report_tool,
        ],
    )
