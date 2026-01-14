#!/usr/bin/env python3
"""
POC测试脚本 - 验证Agent SDK架构
"""

import json
import asyncio
from pathlib import Path


def test_agent_structure():
    """测试1: 验证AI员工工作目录结构"""
    print("=" * 60)
    print("测试1: 验证AI员工工作目录结构")
    print("=" * 60)

    agents_dir = Path(__file__).parent.parent / "agents"
    dev_agent_dir = agents_dir / "dev_efficiency_analyst"

    checks = {
        "工作目录存在": dev_agent_dir.exists(),
        "CLAUDE.md存在": (dev_agent_dir / "CLAUDE.md").exists(),
        "settings.json存在": (dev_agent_dir / ".claude" / "settings.json").exists(),
        "gerrit_analysis.py存在": (dev_agent_dir / ".claude" / "skills" / "gerrit_analysis.py").exists(),
        "report_generation.py存在": (dev_agent_dir / ".claude" / "skills" / "report_generation.py").exists(),
        "data目录存在": (dev_agent_dir / "data").exists(),
        "reports目录存在": (dev_agent_dir / "reports").exists(),
    }

    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")

    all_passed = all(checks.values())
    print(f"\n{'✅ 所有检查通过' if all_passed else '❌ 部分检查失败'}\n")
    return all_passed


def test_skill_execution():
    """测试2: 验证Skills可以执行"""
    print("=" * 60)
    print("测试2: 验证Gerrit分析Skill")
    print("=" * 60)

    import subprocess
    import sys

    agents_dir = Path(__file__).parent.parent / "agents"
    skill_path = agents_dir / "dev_efficiency_analyst" / ".claude" / "skills" / "gerrit_analysis.py"

    # 构造测试数据
    test_data = {
        "changes": [
            {
                "id": "1",
                "created": "2024-01-01T10:00:00Z",
                "updated": "2024-01-01T20:00:00Z",
                "revisions": {"rev1": {}, "rev2": {}}
            },
            {
                "id": "2",
                "created": "2024-01-02T10:00:00Z",
                "updated": "2024-01-03T14:00:00Z",
                "revisions": {"rev1": {}, "rev2": {}, "rev3": {}}
            }
        ]
    }

    try:
        # 执行skill
        result = subprocess.run(
            [sys.executable, str(skill_path)],
            input=json.dumps(test_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            print("✅ Skill执行成功")
            print(f"\n分析结果:")
            print(f"  - 总提交数: {output['metrics']['total_changes']}")
            print(f"  - Review中位耗时: {output['metrics']['median_review_time_hours']:.1f} 小时")
            print(f"  - 返工率: {output['metrics']['rework_rate_percent']:.1f}%")

            if output['anomalies']:
                print(f"\n⚠️  发现 {len(output['anomalies'])} 个异常:")
                for anomaly in output['anomalies']:
                    print(f"  - {anomaly['message']}")
            else:
                print("\n✅ 无异常")

            return True
        else:
            print(f"❌ Skill执行失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False


def test_agent_manager():
    """测试3: 验证Agent SDK Service（已迁移）"""
    print("\n" + "=" * 60)
    print("测试3: 验证Agent SDK Service")
    print("=" * 60)

    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from agent_sdk import AgentSDKService, AgentSDKConfig

        # 初始化Agent SDK Service
        config = AgentSDKConfig()
        agent_service = AgentSDKService(config=config)

        # 测试列出所有AI员工
        agents = agent_service.list_agents()
        print(f"✅ 成功加载 {len(agents)} 个AI员工:")
        for agent in agents:
            print(f"  - {agent['name']} ({agent['role']})")

        # 测试获取特定员工配置
        dev_config = config.get_agent_role("dev_efficiency_analyst")
        if dev_config:
            print(f"\n✅ 成功获取研发效能分析官配置:")
            print(f"  - 名称: {dev_config.name}")
            print(f"  - 模型: {dev_config.model}")
        else:
            print("❌ 获取配置失败")
            return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_chat():
    """测试4: 验证Agent对话（模拟）"""
    print("\n" + "=" * 60)
    print("测试4: 模拟Agent对话流程")
    print("=" * 60)

    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from agent_sdk import AgentSDKService, AgentSDKConfig

        # 注意：这个测试会实际调用Claude API（如果配置了的话）
        # 为了安全起见，我们只测试配置是否正确，不实际调用

        import os
        auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")

        if not auth_token:
            print("⚠️  ANTHROPIC_AUTH_TOKEN未设置，跳过实际对话测试")
            print("   提示：设置环境变量后可以测试实际对话:")
            print('   export ANTHROPIC_AUTH_TOKEN="your-token"')
            return True

        print("✅ 环境变量配置正确")
        print(f"  - ANTHROPIC_AUTH_TOKEN: {auth_token[:20]}...")
        print(f"  - ANTHROPIC_BASE_URL: {os.getenv('ANTHROPIC_BASE_URL', '(默认)')}")

        # 初始化Agent SDK Service
        config = AgentSDKConfig()
        agent_service = AgentSDKService(config=config)

        # 测试Agent SDK配置
        print("✅ Agent SDK Service初始化成功")
        print(f"  - 默认模型: {config.default_model}")

        agents = agent_service.list_agents()
        print(f"  - 可用员工数: {len(agents)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n🚀 开始POC测试...\n")

    results = []

    # 测试1: 目录结构
    results.append(("目录结构", test_agent_structure()))

    # 测试2: Skills执行
    results.append(("Skills执行", test_skill_execution()))

    # 测试3: Agent Manager
    results.append(("Agent Manager", test_agent_manager()))

    # 测试4: 对话流程（异步）
    results.append(("对话流程", asyncio.run(test_agent_chat())))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！POC验证成功！")
        print("\n下一步:")
        print("1. 启动FastAPI服务: python main.py")
        print("2. 访问 http://localhost:8000/docs 查看API文档")
        print("3. 使用WebSocket测试与AI员工对话")
    else:
        print("⚠️  部分测试失败，请检查配置")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
