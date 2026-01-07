"""
正确的 Agent 执行实现（使用 Claude Agent SDK）

这个实现替代了 briefing_service._execute_agent_analysis()
让 AI 真正能够访问 workspace 和 skills
"""

from claude_agent_sdk import query, ClaudeAgentOptions
from pathlib import Path
import asyncio
import os


async def execute_agent_analysis_with_sdk(
    agent_workspace_path: str,
    task_prompt: str,
    agent_role: str = "dev_efficiency_analyst"
) -> str:
    """
    使用 Claude Agent SDK 执行 Agent 分析任务

    关键改进：
    1. ✅ 设置 cwd 到 Agent workspace（AI 可以访问 skills）
    2. ✅ 启用 Bash 工具（AI 可以执行 skill 脚本）
    3. ✅ 启用 Read/Write 工具（AI 可以读写文件）
    4. ✅ AI 自己决定如何完成任务（调用 skills、分析数据）
    """

    # 构建完整的 workspace 路径
    workspace = Path(agent_workspace_path).resolve()

    # 读取 Agent 的 CLAUDE.md 配置
    claude_md_path = workspace / "CLAUDE.md"
    agent_context = ""
    if claude_md_path.exists():
        agent_context = claude_md_path.read_text(encoding='utf-8')

    # 构建完整的 prompt（包含 Agent 角色定义）
    full_prompt = f"""
# 你的角色定义

{agent_context}

---

# 当前任务

{task_prompt}

---

# 可用工具和资源

你可以使用以下工具来完成任务：

1. **Bash 工具**：执行命令行命令
   - 示例：执行 skill 脚本
   ```bash
   cd .claude/skills
   echo '{{"days": 7}}' | python gerrit_analysis.py
   ```

2. **Read 工具**：读取文件内容
   - 读取已有的数据文件
   - 读取 skill 输出的结果

3. **Write 工具**：写入文件
   - 保存分析结果
   - 生成报告文件

4. **Grep/Glob 工具**：搜索文件
   - 查找相关代码或配置

## 你的工作目录

当前工作目录：{workspace}

目录结构：
```
.
├── CLAUDE.md              # 你的角色定义（已读取）
├── .claude/
│   ├── settings.json      # 配置文件
│   └── skills/            # 可执行的技能脚本
│       ├── gerrit_analysis.py      # Gerrit 数据分析
│       └── report_generation.py    # 报告生成
├── data/                  # 数据缓存目录
│   └── mock_gerrit_data.json       # 模拟数据（如果无法连接真实DB）
└── reports/               # 生成的报告目录
```

## 执行建议

1. 首先，使用 Bash 执行 gerrit_analysis skill 获取数据：
   ```bash
   cd .claude/skills && echo '{{"days": 1}}' | python gerrit_analysis.py
   ```

2. 分析返回的数据，检测异常

3. 如果发现异常，按照 CLAUDE.md 中的格式生成分析报告

4. 返回结构化的 Markdown 报告

**开始执行！**
"""

    # 配置 Agent SDK 选项
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Grep", "Glob"],
        cwd=str(workspace),  # ← 关键：设置工作目录！
        model="saas/claude-sonnet-4.5"
    )

    # 执行任务
    result_chunks = []
    async for message in query(prompt=full_prompt, options=options):
        # 收集所有输出
        if hasattr(message, 'content'):
            result_chunks.append(str(message.content))
        else:
            result_chunks.append(str(message))

    # 返回完整结果
    full_result = '\n'.join(result_chunks)
    return full_result


# ============================================================================
# 示例用法
# ============================================================================

async def main():
    """测试 Agent 执行"""

    workspace = "/Users/80392083/develop/ee_app_claude/backend/agents/dev_efficiency_analyst"

    task_prompt = """
请执行每日研发效能分析：

1. 使用 gerrit_analysis skill 获取昨日（过去24小时）的代码审查数据
2. 分析关键指标：Review耗时、返工率、代码变更量
3. 检测异常值（对比阈值）
4. 生成结构化的分析报告

如果无法连接真实 Gerrit 数据库（10.52.61.119:33067），
请使用 data/mock_gerrit_data.json 中的模拟数据。
"""

    print("=" * 60)
    print("🤖 使用 Claude Agent SDK 执行分析任务")
    print("=" * 60)
    print(f"Workspace: {workspace}")
    print(f"Task: {task_prompt[:100]}...")
    print("\n执行中...\n")

    result = await execute_agent_analysis_with_sdk(
        agent_workspace_path=workspace,
        task_prompt=task_prompt
    )

    print("=" * 60)
    print("✅ 执行完成！")
    print("=" * 60)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())
