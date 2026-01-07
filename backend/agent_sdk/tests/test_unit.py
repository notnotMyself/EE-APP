#!/usr/bin/env python3
"""
Agent SDK 模块单元测试（不需要 API 调用）

验证配置、初始化、MCP 工具等功能。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_sdk import AgentSDKConfig, AgentSDKService, TaskManager
from agent_sdk.exceptions import AgentNotFoundError, TaskExecutionError
from agent_sdk.mcp_tools import create_dev_efficiency_server


def test_config():
    """测试配置"""
    print("=" * 50)
    print("测试: 配置管理")
    print("=" * 50)

    config = AgentSDKConfig()

    assert config.anthropic_base_url == "https://llm-gateway.oppoer.me"
    assert config.default_model == "sonnet"
    assert config.permission_mode == "acceptEdits"
    assert config.max_turns == 20

    # 测试 Agent 角色
    role = config.get_agent_role("dev_efficiency_analyst")
    assert role is not None
    assert role.name == "研发效能分析官"
    assert "Read" in role.allowed_tools

    # 测试不存在的角色
    assert config.get_agent_role("nonexistent") is None

    print("✅ 配置管理测试通过")
    print()


def test_service_list_agents():
    """测试列出 Agents"""
    print("=" * 50)
    print("测试: 列出可用 Agents")
    print("=" * 50)

    service = AgentSDKService()
    agents = service.list_agents()

    assert len(agents) == 5
    print(f"共有 {len(agents)} 个 Agent:")

    for agent in agents:
        status = "✅" if agent["available"] else "❌"
        print(f"  {status} {agent['name']} ({agent['role']})")

    print()
    print("✅ Agent 列表测试通过")
    print()


def test_system_prompt_loading():
    """测试系统提示词加载"""
    print("=" * 50)
    print("测试: 系统提示词加载")
    print("=" * 50)

    service = AgentSDKService()

    # 测试存在的 Agent（有 CLAUDE.md）
    prompt = service._load_system_prompt("dev_efficiency_analyst")
    assert "研发效能分析官" in prompt
    assert "核心职责" in prompt
    print(f"✅ dev_efficiency_analyst 提示词加载成功 ({len(prompt)} 字符)")

    # 测试不存在的 Agent
    try:
        service._load_system_prompt("nonexistent")
        assert False, "应该抛出 AgentNotFoundError"
    except AgentNotFoundError as e:
        print(f"✅ 正确抛出 AgentNotFoundError: {e.role}")

    print()


def test_mcp_server_creation():
    """测试 MCP 服务器创建"""
    print("=" * 50)
    print("测试: MCP 服务器创建")
    print("=" * 50)

    server = create_dev_efficiency_server()

    assert server is not None
    assert server["type"] == "sdk"
    assert server["name"] == "dev_efficiency"
    assert "instance" in server

    print(f"✅ MCP 服务器创建成功")
    print(f"   类型: {server['type']}")
    print(f"   名称: {server['name']}")
    print()


def test_mcp_tools_mock_data():
    """测试 MCP 工具模拟数据"""
    print("=" * 50)
    print("测试: MCP 工具模拟数据")
    print("=" * 50)

    from agent_sdk.mcp_tools.dev_efficiency import (
        _generate_mock_gerrit_data,
        _generate_mock_trend_data,
        _generate_mock_report,
    )

    # Gerrit 数据
    gerrit_data = _generate_mock_gerrit_data("test-project", 7, "merged")
    assert gerrit_data["project"] == "test-project"
    assert gerrit_data["total_reviews"] == 150
    assert "top_reviewers" in gerrit_data
    print(f"✅ Gerrit 模拟数据: {gerrit_data['total_reviews']} 条审查")

    # 趋势数据
    trend_data = _generate_mock_trend_data("review_time", 4)
    assert trend_data["metric"] == "review_time"
    assert len(trend_data["trend"]) == 4
    print(f"✅ 趋势模拟数据: {len(trend_data['trend'])} 周数据")

    # 报告
    report_md = _generate_mock_report("daily", "markdown")
    assert "研发效能日报" in report_md
    assert "关键指标" in report_md
    print(f"✅ Markdown 报告: {len(report_md)} 字符")

    report_json = _generate_mock_report("weekly", "json")
    import json
    data = json.loads(report_json)
    assert "title" in data
    print(f"✅ JSON 报告: {len(data)} 个字段")
    print()


def test_exceptions():
    """测试异常类"""
    print("=" * 50)
    print("测试: 异常类")
    print("=" * 50)

    # AgentNotFoundError
    e1 = AgentNotFoundError("test_role")
    assert e1.role == "test_role"
    assert "test_role" in str(e1)
    print(f"✅ AgentNotFoundError: {e1}")

    # TaskExecutionError
    e2 = TaskExecutionError(
        task_id="task_123",
        message="测试错误",
        phase="execution",
    )
    assert e2.task_id == "task_123"
    assert e2.phase == "execution"
    print(f"✅ TaskExecutionError: {e2}")

    # to_dict
    d = e2.to_dict()
    assert d["error"] == "TaskExecutionError"
    assert d["details"]["task_id"] == "task_123"
    print(f"✅ to_dict(): {d}")
    print()


def test_task_manager_init():
    """测试 TaskManager 初始化"""
    print("=" * 50)
    print("测试: TaskManager 初始化")
    print("=" * 50)

    # 无 Supabase 客户端
    manager = TaskManager()

    assert manager.agent_service is not None
    assert manager.supabase is None
    assert manager.get_running_task_count() == 0

    print("✅ TaskManager 初始化成功（无 Supabase）")
    print(f"   正在运行的任务数: {manager.get_running_task_count()}")
    print()


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Agent SDK 模块单元测试")
    print("=" * 60 + "\n")

    tests = [
        test_config,
        test_service_list_agents,
        test_system_prompt_loading,
        test_mcp_server_creation,
        test_mcp_tools_mock_data,
        test_exceptions,
        test_task_manager_init,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            print()

    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
