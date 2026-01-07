#!/usr/bin/env python3
"""
POC 1: 基础查询验证
验证 claude-agent-sdk 的 query() 函数基础功能
"""

import anyio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)


async def test_basic_query():
    """测试基础查询"""
    print("=" * 50)
    print("测试 1: 基础查询")
    print("=" * 50)

    async for message in query(prompt="你好，请用一句话介绍你自己"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            if message.total_cost_usd:
                print(f"\n费用: ${message.total_cost_usd:.6f}")
    print()


async def test_with_system_prompt():
    """测试带 system prompt 的查询"""
    print("=" * 50)
    print("测试 2: 带 System Prompt")
    print("=" * 50)

    options = ClaudeAgentOptions(
        system_prompt="你是一个研发效能分析官，专门分析代码审查数据。请用简洁专业的语言回答。",
        max_turns=1,
    )

    async for message in query(
        prompt="请介绍你的职责",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
    print()


async def test_with_cwd():
    """测试工作目录设置"""
    print("=" * 50)
    print("测试 3: 工作目录设置 (cwd)")
    print("=" * 50)

    options = ClaudeAgentOptions(
        cwd="/Users/80392083/develop/ee_app_claude/backend/agents/dev_efficiency_analyst",
        max_turns=2,
        allowed_tools=["Read"],
    )

    async for message in query(
        prompt="请读取当前目录下的 CLAUDE.md 文件，告诉我你的职责是什么",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
    print()


async def main():
    """运行所有测试"""
    print("\n🚀 Claude Agent SDK POC - 基础查询验证\n")

    try:
        await test_basic_query()
        await test_with_system_prompt()
        await test_with_cwd()
        print("✅ 所有基础测试完成")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    anyio.run(main)
