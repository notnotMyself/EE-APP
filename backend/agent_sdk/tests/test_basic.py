#!/usr/bin/env python3
"""
Agent SDK 基础功能验证

验证新实现的 Agent SDK 服务能正常工作。
"""

import asyncio
import os
import sys

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_sdk import AgentSDKConfig, AgentSDKService
from agent_sdk.mcp_tools import create_dev_efficiency_server


async def test_config():
    """测试配置管理"""
    print("=" * 50)
    print("测试 1: 配置管理")
    print("=" * 50)

    config = AgentSDKConfig()

    print(f"API Gateway: {config.anthropic_base_url}")
    print(f"Auth Token: {'已设置' if config.anthropic_auth_token else '未设置'}")
    print(f"Agents Base Dir: {config.agents_base_dir}")
    print(f"Default Model: {config.default_model}")
    print(f"Permission Mode: {config.permission_mode}")
    print()

    # 列出 Agent 角色
    print("已注册的 Agent 角色:")
    for role, role_config in config.agent_roles.items():
        print(f"  - {role}: {role_config.name}")
        print(f"    模型: {role_config.model}")
        print(f"    工具: {role_config.allowed_tools}")
    print()

    return True


async def test_service_init():
    """测试服务初始化"""
    print("=" * 50)
    print("测试 2: AgentSDKService 初始化")
    print("=" * 50)

    config = AgentSDKConfig()
    service = AgentSDKService(config=config)

    # 列出可用 Agent
    agents = service.list_agents()
    print(f"可用 Agent 数量: {len(agents)}")
    for agent in agents:
        status = "可用" if agent["available"] else "不可用"
        print(f"  - {agent['name']} ({agent['role']}): {status}")
    print()

    return True


async def test_mcp_server():
    """测试 MCP 服务器创建"""
    print("=" * 50)
    print("测试 3: MCP 服务器创建")
    print("=" * 50)

    try:
        server = create_dev_efficiency_server()
        print(f"MCP 服务器创建成功: {server}")
        print("  - gerrit_query")
        print("  - efficiency_trend")
        print("  - generate_report")
        print()
        return True
    except Exception as e:
        print(f"MCP 服务器创建失败: {e}")
        return False


async def test_agent_query():
    """测试 Agent 查询（需要真实 API）"""
    print("=" * 50)
    print("测试 4: Agent 查询")
    print("=" * 50)

    config = AgentSDKConfig()

    if not config.anthropic_auth_token:
        print("跳过: ANTHROPIC_AUTH_TOKEN 未设置")
        print()
        return True

    service = AgentSDKService(config=config)

    # 创建 MCP 服务器
    mcp_server = create_dev_efficiency_server()

    print("执行查询: 请简单介绍一下你自己")
    print()

    try:
        content_parts = []
        async for event in service.execute_query(
            prompt="你好，请用一句话介绍一下你自己",
            agent_role="dev_efficiency_analyst",
            mcp_servers={"dev_efficiency": mcp_server},
        ):
            if event["type"] == "text_chunk":
                content_parts.append(event["content"])
                print(event["content"], end="", flush=True)
            elif event["type"] == "tool_use":
                print(f"\n[工具调用] {event['tool_name']}")
            elif event["type"] == "result":
                print(f"\n[完成] 花费: ${event.get('total_cost_usd', 0):.6f}")

        print()
        return True

    except Exception as e:
        print(f"\n查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_tool_query():
    """测试 MCP 工具调用"""
    print("=" * 50)
    print("测试 5: MCP 工具调用")
    print("=" * 50)

    config = AgentSDKConfig()

    if not config.anthropic_auth_token:
        print("跳过: ANTHROPIC_AUTH_TOKEN 未设置")
        print()
        return True

    service = AgentSDKService(config=config)
    mcp_server = create_dev_efficiency_server()

    print("执行查询: 获取代码审查数据")
    print()

    try:
        async for event in service.execute_query(
            prompt="请获取 mobile-app 项目最近 7 天的代码审查统计数据",
            agent_role="dev_efficiency_analyst",
            mcp_servers={"dev_efficiency": mcp_server},
        ):
            if event["type"] == "text_chunk":
                print(event["content"], end="", flush=True)
            elif event["type"] == "tool_use":
                print(f"\n[工具调用] {event['tool_name']}: {event.get('input', {})}")
            elif event["type"] == "tool_result":
                print(f"[工具结果] 返回数据长度: {len(str(event.get('content', '')))}")
            elif event["type"] == "result":
                print(f"\n[完成] 花费: ${event.get('total_cost_usd', 0):.6f}")

        print()
        return True

    except Exception as e:
        print(f"\n查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Agent SDK 基础功能验证")
    print("=" * 60 + "\n")

    results = []

    # 基础测试
    results.append(("配置管理", await test_config()))
    results.append(("服务初始化", await test_service_init()))
    results.append(("MCP 服务器", await test_mcp_server()))

    # API 测试（可选）
    results.append(("Agent 查询", await test_agent_query()))
    results.append(("MCP 工具调用", await test_mcp_tool_query()))

    # 总结
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "通过" if passed else "失败"
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败，请检查配置")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
