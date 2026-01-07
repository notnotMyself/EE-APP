#!/usr/bin/env python3
"""
POC 3: MCP 自定义工具验证
验证通过 @tool 装饰器和 create_sdk_mcp_server 创建自定义工具
"""

import anyio
from typing import Any
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


# 定义自定义工具：模拟 Gerrit 代码审查数据查询
@tool("get_review_stats", "获取代码审查统计数据", {"project": str, "days": int})
async def get_review_stats(args: dict[str, Any]) -> dict[str, Any]:
    """获取指定项目的代码审查统计"""
    project = args.get("project", "default")
    days = args.get("days", 7)

    # 模拟数据
    mock_data = {
        "project": project,
        "period": f"最近 {days} 天",
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
        ]
    }

    import json
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(mock_data, ensure_ascii=False, indent=2)
        }]
    }


@tool("get_efficiency_trend", "获取效能趋势数据", {"metric": str, "weeks": int})
async def get_efficiency_trend(args: dict[str, Any]) -> dict[str, Any]:
    """获取效能指标的周趋势"""
    metric = args.get("metric", "review_time")
    weeks = args.get("weeks", 4)

    # 模拟趋势数据
    trend_data = {
        "metric": metric,
        "unit": "小时" if "time" in metric else "百分比",
        "trend": [
            {"week": "W1", "value": 20.5},
            {"week": "W2", "value": 18.2},
            {"week": "W3", "value": 22.1},
            {"week": "W4", "value": 18.5},
        ][:weeks],
        "analysis": "整体呈下降趋势，效率有所提升。W3 有异常峰值，建议关注。"
    }

    import json
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(trend_data, ensure_ascii=False, indent=2)
        }]
    }


def display_message(msg):
    """显示消息"""
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"[Claude] {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"[Tool Use] {block.name}")
                print(f"  Input: {block.input}")
    elif isinstance(msg, ResultMessage):
        if msg.total_cost_usd:
            print(f"\n[Cost] ${msg.total_cost_usd:.6f}")


async def test_single_mcp_tool():
    """测试单个 MCP 工具"""
    print("=" * 50)
    print("测试 1: 单个 MCP 工具 (get_review_stats)")
    print("=" * 50)

    # 创建 MCP 服务器
    server = create_sdk_mcp_server(
        name="dev_efficiency",
        version="1.0.0",
        tools=[get_review_stats]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"stats": server},
        allowed_tools=["mcp__stats__get_review_stats"],
        max_turns=3,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("请获取 mobile-app 项目最近 14 天的代码审查统计数据")
        async for msg in client.receive_response():
            display_message(msg)
    print()


async def test_multiple_mcp_tools():
    """测试多个 MCP 工具"""
    print("=" * 50)
    print("测试 2: 多个 MCP 工具")
    print("=" * 50)

    # 创建包含多个工具的 MCP 服务器
    server = create_sdk_mcp_server(
        name="dev_efficiency",
        version="1.0.0",
        tools=[get_review_stats, get_efficiency_trend]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"stats": server},
        allowed_tools=[
            "mcp__stats__get_review_stats",
            "mcp__stats__get_efficiency_trend"
        ],
        max_turns=5,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "请先获取 backend 项目最近 7 天的审查统计，然后获取 review_time 指标最近 4 周的趋势，最后给出分析报告"
        )
        async for msg in client.receive_response():
            display_message(msg)
    print()


async def test_mcp_with_builtin_tools():
    """测试 MCP 工具与内置工具混合使用"""
    print("=" * 50)
    print("测试 3: MCP 工具 + 内置工具混合")
    print("=" * 50)

    server = create_sdk_mcp_server(
        name="dev_efficiency",
        version="1.0.0",
        tools=[get_review_stats]
    )

    options = ClaudeAgentOptions(
        cwd="/Users/80392083/develop/ee_app_claude/backend/poc",
        mcp_servers={"stats": server},
        allowed_tools=[
            "mcp__stats__get_review_stats",
            "Write",
        ],
        permission_mode="acceptEdits",
        max_turns=5,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "请获取 frontend 项目最近 7 天的代码审查数据，然后将结果保存到 review_report.md 文件中"
        )
        async for msg in client.receive_response():
            display_message(msg)
    print()


async def main():
    """运行所有 MCP 工具测试"""
    print("\n🚀 Claude Agent SDK POC - MCP 自定义工具验证\n")

    try:
        await test_single_mcp_tool()
        await test_multiple_mcp_tools()
        await test_mcp_with_builtin_tools()
        print("✅ 所有 MCP 工具测试完成")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    anyio.run(main)
