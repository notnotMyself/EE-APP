#!/usr/bin/env python3
"""
POC 2: 工具调用验证
验证内置工具 Read, Write, Bash 的功能
"""

import anyio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    UserMessage,
)


def display_message(msg):
    """显示消息内容"""
    if isinstance(msg, UserMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"[User] {block.text}")
            elif isinstance(block, ToolResultBlock):
                content = block.content[:200] if block.content else "None"
                print(f"[ToolResult] {content}...")
    elif isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"[Claude] {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"[Tool Use] {block.name}")
                if block.input:
                    print(f"  Input: {block.input}")
    elif isinstance(msg, ResultMessage):
        if msg.total_cost_usd:
            print(f"\n[Cost] ${msg.total_cost_usd:.6f}")


async def test_read_tool():
    """测试 Read 工具"""
    print("=" * 50)
    print("测试 1: Read 工具")
    print("=" * 50)

    options = ClaudeAgentOptions(
        cwd="/Users/80392083/develop/ee_app_claude/backend/agents/dev_efficiency_analyst",
        allowed_tools=["Read"],
        permission_mode="acceptEdits",  # 自动接受编辑操作
        max_turns=3,
    )

    async for message in query(
        prompt="请读取 CLAUDE.md 文件的前 50 行，并总结这个 Agent 的主要职责",
        options=options
    ):
        display_message(message)
    print()


async def test_bash_tool():
    """测试 Bash 工具"""
    print("=" * 50)
    print("测试 2: Bash 工具")
    print("=" * 50)

    options = ClaudeAgentOptions(
        cwd="/Users/80392083/develop/ee_app_claude/backend/poc",
        allowed_tools=["Bash"],
        permission_mode="acceptEdits",
        max_turns=3,
    )

    async for message in query(
        prompt="请执行 ls -la 命令查看当前目录的文件列表",
        options=options
    ):
        display_message(message)
    print()


async def test_write_tool():
    """测试 Write 工具"""
    print("=" * 50)
    print("测试 3: Write 工具")
    print("=" * 50)

    options = ClaudeAgentOptions(
        cwd="/Users/80392083/develop/ee_app_claude/backend/poc",
        allowed_tools=["Write", "Read"],
        permission_mode="acceptEdits",
        max_turns=3,
    )

    async for message in query(
        prompt="请创建一个名为 test_output.txt 的文件，内容为 'Hello from Claude Agent SDK POC!'，然后读取并确认内容",
        options=options
    ):
        display_message(message)
    print()


async def test_combined_tools():
    """测试组合工具调用"""
    print("=" * 50)
    print("测试 4: 组合工具调用")
    print("=" * 50)

    options = ClaudeAgentOptions(
        cwd="/Users/80392083/develop/ee_app_claude/backend/agents/dev_efficiency_analyst",
        allowed_tools=["Read", "Bash", "Grep"],
        permission_mode="acceptEdits",
        max_turns=5,
    )

    async for message in query(
        prompt="请先用 ls 查看当前目录结构，然后读取 CLAUDE.md 文件，搜索其中包含 '职责' 的行",
        options=options
    ):
        display_message(message)
    print()


async def main():
    """运行所有工具测试"""
    print("\n🚀 Claude Agent SDK POC - 工具调用验证\n")

    try:
        await test_read_tool()
        await test_bash_tool()
        await test_write_tool()
        await test_combined_tools()
        print("✅ 所有工具测试完成")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    anyio.run(main)
