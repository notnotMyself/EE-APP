#!/usr/bin/env python3
"""
Agent SDK 集成测试

测试与 Claude Agent SDK 的实际集成。
需要在独立终端运行（不能在 Claude Code 内部运行）。

使用方法:
    cd /Users/80392083/develop/ee_app_claude/backend
    PYTHONPATH=. python3 agent_sdk/tests/test_integration.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_sdk import AgentSDKConfig, AgentSDKService
from agent_sdk.mcp_tools import create_dev_efficiency_server


async def test_simple_query():
    """测试简单查询"""
    print("=" * 60)
    print("测试 1: 简单查询")
    print("=" * 60)

    service = AgentSDKService()

    print("发送: 你好，请用一句话介绍一下你自己")
    print("-" * 40)

    content = []
    async for event in service.execute_query(
        prompt="你好，请用一句话介绍一下你自己",
        agent_role="dev_efficiency_analyst",
    ):
        if event["type"] == "text_chunk":
            print(event["content"], end="", flush=True)
            content.append(event["content"])
        elif event["type"] == "result":
            print(f"\n\n[花费: ${event.get('total_cost_usd', 0):.6f}]")

    print("-" * 40)
    print(f"✅ 响应长度: {len(''.join(content))} 字符")
    print()
    return True


async def test_with_mcp_tools():
    """测试 MCP 工具调用"""
    print("=" * 60)
    print("测试 2: MCP 工具调用")
    print("=" * 60)

    service = AgentSDKService()
    mcp_server = create_dev_efficiency_server()

    print("发送: 请获取 mobile-app 项目最近 7 天的代码审查统计数据")
    print("-" * 40)

    tool_calls = []
    async for event in service.execute_query(
        prompt="请获取 mobile-app 项目最近 7 天的代码审查统计数据",
        agent_role="dev_efficiency_analyst",
        mcp_servers={"dev_efficiency": mcp_server},
    ):
        if event["type"] == "text_chunk":
            print(event["content"], end="", flush=True)
        elif event["type"] == "tool_use":
            tool_calls.append(event["tool_name"])
            print(f"\n[调用工具: {event['tool_name']}]")
        elif event["type"] == "result":
            print(f"\n\n[花费: ${event.get('total_cost_usd', 0):.6f}]")

    print("-" * 40)
    print(f"✅ 调用了 {len(tool_calls)} 个工具: {tool_calls}")
    print()
    return len(tool_calls) > 0


async def test_efficiency_report():
    """测试效能报告生成"""
    print("=" * 60)
    print("测试 3: 效能报告生成")
    print("=" * 60)

    service = AgentSDKService()
    mcp_server = create_dev_efficiency_server()

    print("发送: 请生成今日的研发效能日报")
    print("-" * 40)

    async for event in service.execute_query(
        prompt="请生成今日的研发效能日报，使用 markdown 格式",
        agent_role="dev_efficiency_analyst",
        mcp_servers={"dev_efficiency": mcp_server},
    ):
        if event["type"] == "text_chunk":
            print(event["content"], end="", flush=True)
        elif event["type"] == "tool_use":
            print(f"\n[调用工具: {event['tool_name']}]")
        elif event["type"] == "result":
            print(f"\n\n[花费: ${event.get('total_cost_usd', 0):.6f}]")

    print("-" * 40)
    print("✅ 报告生成完成")
    print()
    return True


async def test_multi_turn_analysis():
    """测试多轮分析"""
    print("=" * 60)
    print("测试 4: 多工具组合分析")
    print("=" * 60)

    service = AgentSDKService()
    mcp_server = create_dev_efficiency_server()

    prompt = """请完成以下分析任务:
1. 先获取 backend 项目最近 14 天的代码审查数据
2. 再获取 review_time 指标最近 4 周的趋势
3. 基于以上数据给出分析和建议"""

    print(f"发送: {prompt[:50]}...")
    print("-" * 40)

    tool_calls = []
    async for event in service.execute_query(
        prompt=prompt,
        agent_role="dev_efficiency_analyst",
        mcp_servers={"dev_efficiency": mcp_server},
    ):
        if event["type"] == "text_chunk":
            print(event["content"], end="", flush=True)
        elif event["type"] == "tool_use":
            tool_calls.append(event["tool_name"])
            print(f"\n[调用工具: {event['tool_name']}]")
        elif event["type"] == "result":
            print(f"\n\n[花费: ${event.get('total_cost_usd', 0):.6f}]")

    print("-" * 40)
    print(f"✅ 调用了 {len(tool_calls)} 个工具")
    print()
    return len(tool_calls) >= 2


async def main():
    """运行集成测试"""
    print("\n" + "=" * 60)
    print("Agent SDK 集成测试")
    print("=" * 60)

    # 检查环境
    config = AgentSDKConfig()
    if not config.anthropic_auth_token:
        print("❌ 错误: ANTHROPIC_AUTH_TOKEN 未设置")
        print("请设置环境变量后重试:")
        print("  export ANTHROPIC_AUTH_TOKEN=your-token")
        return False

    print(f"API Gateway: {config.anthropic_base_url}")
    print(f"Auth Token: 已设置")
    print()

    tests = [
        ("简单查询", test_simple_query),
        ("MCP 工具调用", test_with_mcp_tools),
        ("效能报告生成", test_efficiency_report),
        ("多工具组合分析", test_multi_turn_analysis),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 失败: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 汇总
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")

    print()
    print(f"总计: {passed}/{len(results)} 通过")

    return passed == len(results)


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(1)
