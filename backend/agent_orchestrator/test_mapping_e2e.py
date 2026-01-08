#!/usr/bin/env python3
"""
端到端测试脚本 - 验证 Agent 映射层和对话任务执行

测试流程：
1. 测试 agent 映射功能
2. 创建对话（使用 role string）
3. 发送任务指令
4. 验证任务识别和执行
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from agent_mapping import get_agent_uuid, get_agent_role, is_valid_uuid
from services.task_intent_recognizer import TaskIntentRecognizer


async def test_mapping():
    """测试 Agent 映射功能"""
    print("\n" + "=" * 80)
    print("Test 1: Agent Mapping")
    print("=" * 80 + "\n")

    test_cases = [
        ("dev_efficiency_analyst", "a1e79944-69bf-4f06-8e05-8060bcebad30"),
        ("nps_insight_analyst", "f67d011f-f517-4f4d-961c-b67e3fc89985"),
    ]

    passed = 0
    for role, expected_uuid in test_cases:
        try:
            uuid = get_agent_uuid(role)
            if uuid == expected_uuid:
                print(f"✅ {role} → {uuid}")
                passed += 1
            else:
                print(f"❌ {role} → {uuid} (expected {expected_uuid})")
        except Exception as e:
            print(f"❌ {role} → Error: {e}")

    # 反向测试
    print()
    for role, uuid in test_cases:
        try:
            result_role = get_agent_role(uuid)
            if result_role == role:
                print(f"✅ {uuid} → {result_role}")
                passed += 1
            else:
                print(f"❌ {uuid} → {result_role} (expected {role})")
        except Exception as e:
            print(f"❌ {uuid} → Error: {e}")

    # 幂等性测试
    print()
    uuid = get_agent_uuid("dev_efficiency_analyst")
    uuid2 = get_agent_uuid(uuid)
    if uuid == uuid2:
        print(f"✅ Idempotent: get_agent_uuid(uuid) = {uuid2}")
        passed += 1
    else:
        print(f"❌ Not idempotent: {uuid} != {uuid2}")

    print(f"\n📊 Mapping tests: {passed}/{len(test_cases)*2 + 1} passed\n")
    return passed == len(test_cases)*2 + 1


async def test_task_recognition():
    """测试任务识别（与映射结合）"""
    print("=" * 80)
    print("Test 2: Task Recognition with Agent Context")
    print("=" * 80 + "\n")

    recognizer = TaskIntentRecognizer()

    # 使用 UUID 作为 agent_id（模拟数据库中的情况）
    agent_uuid = get_agent_uuid("dev_efficiency_analyst")

    test_message = "帮我分析昨天的代码审查数据"

    context = {"agent_id": agent_uuid}
    result = await recognizer.recognize(test_message, conversation_context=context)

    if result and result.task_type == "data_analysis":
        print(f"✅ Task recognized with UUID context")
        print(f"   Agent UUID: {agent_uuid}")
        print(f"   Task type: {result.task_type}")
        print(f"   Task prompt preview: {result.task_prompt[:80]}...")
        return True
    else:
        print(f"❌ Task recognition failed with UUID context")
        return False


async def test_conversation_service_simulation():
    """模拟 ConversationService 的 UUID→Role 转换"""
    print("\n" + "=" * 80)
    print("Test 3: ConversationService UUID→Role Conversion Simulation")
    print("=" * 80 + "\n")

    # 模拟从数据库获取的 conversation
    conversation = {
        "id": "test-conversation-id",
        "agent_id": "a1e79944-69bf-4f06-8e05-8060bcebad30",  # UUID from DB
        "user_id": "test-user-id"
    }

    # 模拟 _get_agent_role 方法
    def _get_agent_role(agent_id: str) -> str:
        role = get_agent_role(agent_id)
        if role:
            return role
        return agent_id

    agent_role = _get_agent_role(conversation["agent_id"])

    if agent_role == "dev_efficiency_analyst":
        print(f"✅ UUID→Role conversion successful")
        print(f"   Input UUID: {conversation['agent_id']}")
        print(f"   Output Role: {agent_role}")
        return True
    else:
        print(f"❌ UUID→Role conversion failed")
        print(f"   Input UUID: {conversation['agent_id']}")
        print(f"   Output Role: {agent_role}")
        return False


async def main():
    """运行所有测试"""
    print("\n🧪 End-to-End Mapping Layer Test Suite")
    print("=" * 80)

    results = []

    # Test 1: Mapping
    results.append(await test_mapping())

    # Test 2: Task Recognition with UUID
    results.append(await test_task_recognition())

    # Test 3: ConversationService simulation
    results.append(await test_conversation_service_simulation())

    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"\nTotal: {passed}/{total} test suites passed\n")

    if passed == total:
        print("✅ All tests passed! Mapping layer is working correctly.")
        print("\n🎯 Next steps:")
        print("   1. Test with real API calls (requires authentication)")
        print("   2. Test full conversation flow")
        print("   3. Test task execution and briefing generation")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
