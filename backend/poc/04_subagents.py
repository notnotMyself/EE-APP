#!/usr/bin/env python3
"""
POC 4: Sub-agent 验证
验证 AgentDefinition 和多 Agent 协作功能
"""

import anyio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


def display_message(msg):
    """显示消息"""
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"[Claude] {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"[Tool Use] {block.name}")
                if block.input:
                    # 只显示关键输入
                    input_str = str(block.input)
                    if len(input_str) > 200:
                        input_str = input_str[:200] + "..."
                    print(f"  Input: {input_str}")
    elif isinstance(msg, ResultMessage):
        if msg.total_cost_usd:
            print(f"\n[Cost] ${msg.total_cost_usd:.6f}")


async def test_single_agent_definition():
    """测试单个 Agent 定义"""
    print("=" * 50)
    print("测试 1: 单个 AgentDefinition")
    print("=" * 50)

    options = ClaudeAgentOptions(
        agents={
            "code-analyzer": AgentDefinition(
                description="分析代码结构和模式的专家",
                prompt="你是一个代码分析专家。分析代码时要关注：1.架构模式 2.依赖关系 3.潜在问题。用简洁的语言总结。",
                tools=["Read", "Grep", "Glob"],
                model="sonnet",
            ),
        },
        cwd="/Users/80392083/develop/ee_app_claude/backend/poc",
        max_turns=5,
    )

    async for message in query(
        prompt="请使用 code-analyzer agent 分析当前目录下的 Python 文件结构",
        options=options
    ):
        display_message(message)
    print()


async def test_multiple_agents():
    """测试多个 Agent 定义"""
    print("=" * 50)
    print("测试 2: 多个 AgentDefinition")
    print("=" * 50)

    options = ClaudeAgentOptions(
        agents={
            "data-analyzer": AgentDefinition(
                description="分析数据并提取洞察",
                prompt="你是数据分析师。从数据中提取关键洞察，用数字说话。",
                tools=["Read", "Bash"],
                model="haiku",
            ),
            "report-writer": AgentDefinition(
                description="撰写专业报告",
                prompt="你是技术报告撰写专家。将分析结果整理成结构化的专业报告。",
                tools=["Write"],
                model="sonnet",
            ),
        },
        cwd="/Users/80392083/develop/ee_app_claude/backend/poc",
        permission_mode="acceptEdits",
        max_turns=8,
    )

    async for message in query(
        prompt="""请完成以下任务：
1. 先用 data-analyzer agent 分析 review_report.md 文件中的数据
2. 再用 report-writer agent 将分析结果写入 analysis_summary.md 文件""",
        options=options
    ):
        display_message(message)
    print()


async def test_agent_with_specific_tools():
    """测试 Agent 的工具隔离"""
    print("=" * 50)
    print("测试 3: Agent 工具隔离验证")
    print("=" * 50)

    options = ClaudeAgentOptions(
        agents={
            "reader-only": AgentDefinition(
                description="只读分析专家，只能读取不能写入",
                prompt="你只能读取和分析文件，不能修改任何内容。",
                tools=["Read", "Grep"],  # 只有读取权限
                model="haiku",
            ),
            "writer": AgentDefinition(
                description="写入专家",
                prompt="你负责将内容写入文件。",
                tools=["Write"],  # 只有写入权限
                model="haiku",
            ),
        },
        cwd="/Users/80392083/develop/ee_app_claude/backend/poc",
        permission_mode="acceptEdits",
        max_turns=5,
    )

    async for message in query(
        prompt="使用 reader-only agent 读取 test_output.txt 的内容",
        options=options
    ):
        display_message(message)
    print()


async def main():
    """运行所有 Sub-agent 测试"""
    print("\n🚀 Claude Agent SDK POC - Sub-agent 验证\n")

    try:
        await test_single_agent_definition()
        await test_multiple_agents()
        await test_agent_with_specific_tools()
        print("✅ 所有 Sub-agent 测试完成")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    anyio.run(main)
