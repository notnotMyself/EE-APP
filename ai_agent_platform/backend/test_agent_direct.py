#!/usr/bin/env python3
"""
测试脚本：直接调用 Agent SDK 执行任务，查看详细输出
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.agent_sdk_client import execute_agent_task


async def test_agent_sdk_direct():
    """直接测试 Agent SDK 执行"""

    print("=" * 80)
    print("直接测试 Agent SDK - 执行 gerrit_analysis.py")
    print("=" * 80)

    task_prompt = """
# 任务：执行研发效能分析

## 步骤

1. 使用 Bash 工具进入 .claude/skills/ 目录
2. 执行 gerrit_analysis.py 脚本，获取最近1天的数据
3. 分析输出的 JSON 数据
4. 生成结构化的分析报告

## 执行命令示例

```bash
cd .claude/skills
echo '{"days": 1}' | python3 gerrit_analysis.py
```

## 输出要求

请以 Markdown 格式输出分析报告，包括：
- 数据来源说明（真实数据 or 模拟数据）
- 关键指标分析
- 异常检测结果
- 建议（如果有）
"""

    print(f"\n📝 Task Prompt:")
    print("-" * 80)
    print(task_prompt)
    print("-" * 80)

    print("\n🚀 开始执行...\n")

    try:
        result = await execute_agent_task(
            agent_role="dev_efficiency_analyst",
            task_prompt=task_prompt,
            allowed_tools=["Bash", "Read", "Write", "Grep", "Glob"],
            timeout=120
        )

        print("\n" + "=" * 80)
        print("✅ 执行完成！")
        print("=" * 80)

        print("\n📊 完整输出:")
        print("-" * 80)
        print(result)
        print("-" * 80)

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🧪 Agent SDK 直接调用测试\n")
    asyncio.run(test_agent_sdk_direct())
    print("\n✨ 测试完成\n")
