#!/usr/bin/env python3
"""
POC 5: 自定义 API Gateway 验证
验证 llm-gateway.oppoer.me 的兼容性
"""

import anyio
import os
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)


def display_message(msg):
    """显示消息"""
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"[Claude] {block.text}")
    elif isinstance(msg, ResultMessage):
        if msg.total_cost_usd:
            print(f"\n[Cost] ${msg.total_cost_usd:.6f}")


async def test_with_env_var():
    """测试通过环境变量配置 API Gateway"""
    print("=" * 50)
    print("测试 1: 通过 env 参数配置 API Gateway")
    print("=" * 50)

    # 配置内部 API Gateway
    custom_env = {
        "ANTHROPIC_BASE_URL": "https://llm-gateway.oppoer.me",
        # 如果需要自定义 API Key，也可以在这里设置
        # "ANTHROPIC_API_KEY": "your-custom-key"
    }

    options = ClaudeAgentOptions(
        env=custom_env,
        max_turns=1,
    )

    print(f"配置的 API Gateway: {custom_env.get('ANTHROPIC_BASE_URL')}")
    print()

    try:
        async for message in query(
            prompt="你好，请简单介绍一下你自己（一句话）",
            options=options
        ):
            display_message(message)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    print()
    return True


async def test_with_extra_args():
    """测试通过 extra_args 配置"""
    print("=" * 50)
    print("测试 2: 通过 extra_args 传递 CLI 参数")
    print("=" * 50)

    # 尝试通过 extra_args 传递参数
    options = ClaudeAgentOptions(
        extra_args={
            "--api-key-name": None,  # 使用默认
        },
        max_turns=1,
    )

    try:
        async for message in query(
            prompt="请说 'Hello from extra_args test!'",
            options=options
        ):
            display_message(message)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    print()
    return True


async def test_current_env():
    """测试当前环境变量是否生效"""
    print("=" * 50)
    print("测试 3: 检查当前环境变量")
    print("=" * 50)

    # 显示当前相关环境变量
    print("当前环境变量:")
    print(f"  ANTHROPIC_BASE_URL: {os.environ.get('ANTHROPIC_BASE_URL', '未设置')}")
    print(f"  ANTHROPIC_API_KEY: {'已设置' if os.environ.get('ANTHROPIC_API_KEY') else '未设置'}")
    print(f"  ANTHROPIC_AUTH_TOKEN: {'已设置' if os.environ.get('ANTHROPIC_AUTH_TOKEN') else '未设置'}")
    print()

    # 使用默认配置（不传自定义 env）
    options = ClaudeAgentOptions(
        max_turns=1,
    )

    try:
        async for message in query(
            prompt="请说 'Environment test passed!'",
            options=options
        ):
            display_message(message)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    print()
    return True


async def main():
    """运行所有自定义 Gateway 测试"""
    print("\n🚀 Claude Agent SDK POC - 自定义 API Gateway 验证\n")

    results = []

    # 测试 1: env 参数
    results.append(("env 参数配置", await test_with_env_var()))

    # 测试 2: extra_args
    results.append(("extra_args 配置", await test_with_extra_args()))

    # 测试 3: 当前环境变量
    results.append(("当前环境变量", await test_current_env()))

    # 总结
    print("=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name}: {status}")

    all_passed = all(r[1] for r in results)
    print()
    if all_passed:
        print("✅ 所有自定义 Gateway 测试完成")
    else:
        print("⚠️ 部分测试未通过，请检查配置")


if __name__ == "__main__":
    anyio.run(main)
