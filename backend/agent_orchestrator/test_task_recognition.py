#!/usr/bin/env python3
"""
Test script for task intent recognition

Tests the TaskIntentRecognizer to verify it correctly identifies task commands.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.task_intent_recognizer import TaskIntentRecognizer


async def test_task_recognition():
    """Test task intent recognition with various messages"""

    recognizer = TaskIntentRecognizer()

    # Test cases
    test_cases = [
        # Data analysis tasks (should be recognized)
        {
            "message": "帮我分析昨天的代码审查数据",
            "expected_type": "data_analysis",
            "should_match": True
        },
        {
            "message": "查看最近7天的效能指标",
            "expected_type": "data_analysis",
            "should_match": True
        },
        {
            "message": "统计本周的提交数据",
            "expected_type": "data_analysis",
            "should_match": True
        },

        # Report generation tasks (should be recognized)
        {
            "message": "生成本月的效能报告",
            "expected_type": "report_generation",
            "should_match": True
        },
        {
            "message": "导出上周的分析报告",
            "expected_type": "report_generation",
            "should_match": True
        },

        # Monitoring setup tasks (should be recognized)
        {
            "message": "每天早上9点推送效能简报",
            "expected_type": "monitoring_setup",
            "should_match": True
        },
        {
            "message": "每周一提醒我查看代码审查情况",
            "expected_type": "monitoring_setup",
            "should_match": True
        },

        # Normal chat (should NOT be recognized as tasks)
        {
            "message": "你好，今天天气怎么样？",
            "expected_type": None,
            "should_match": False
        },
        {
            "message": "这个功能怎么用？",
            "expected_type": None,
            "should_match": False
        },
        {
            "message": "谢谢你的帮助",
            "expected_type": None,
            "should_match": False
        },
    ]

    print("\n" + "=" * 80)
    print("Task Intent Recognition Test")
    print("=" * 80 + "\n")

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        message = test_case["message"]
        expected_type = test_case["expected_type"]
        should_match = test_case["should_match"]

        print(f"Test {i}: {message}")
        print("-" * 80)

        # Run recognition
        context = {"agent_id": "dev_efficiency_analyst"}
        result = await recognizer.recognize(message, conversation_context=context)

        # Check result
        if should_match:
            if result and result.task_type == expected_type:
                print(f"✅ PASS: Recognized as {result.task_type}")
                print(f"   Task prompt preview: {result.task_prompt[:100]}...")
                if result.schedule_config:
                    print(f"   Schedule config: {result.schedule_config}")
                passed += 1
            else:
                print(f"❌ FAIL: Expected {expected_type}, got {result.task_type if result else None}")
                failed += 1
        else:
            if result is None:
                print(f"✅ PASS: Correctly identified as non-task")
                passed += 1
            else:
                print(f"❌ FAIL: Should not match, but got {result.task_type}")
                failed += 1

        print()

    # Summary
    print("=" * 80)
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(test_task_recognition())
    sys.exit(0 if success else 1)
