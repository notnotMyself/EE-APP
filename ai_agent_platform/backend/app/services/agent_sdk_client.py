"""
Claude Agent SDK 客户端封装

提供简化的接口来使用 Claude Agent SDK 执行任务。
"""

import logging
from pathlib import Path
from typing import List, Optional

from claude_agent_sdk import query, ClaudeAgentOptions

from app.core.agent_paths import get_agent_workspace, get_claude_md_path
from app.core.config import settings

logger = logging.getLogger(__name__)


async def execute_agent_task(
    agent_role: str,
    task_prompt: str,
    allowed_tools: Optional[List[str]] = None,
    timeout: int = 300
) -> str:
    """
    使用 Claude Agent SDK 执行 Agent 任务

    Args:
        agent_role: Agent 角色标识（如 'dev_efficiency_analyst'）
        task_prompt: 任务提示词
        allowed_tools: 允许使用的工具列表，默认为 ["Bash", "Read", "Write", "Grep", "Glob"]
        timeout: 任务超时时间（秒）

    Returns:
        任务执行结果（完整的文本输出）

    Raises:
        ValueError: 如果 workspace 或 CLAUDE.md 不存在
        Exception: Agent 执行过程中的错误
    """
    try:
        # 1. 获取 workspace 路径
        workspace = get_agent_workspace(agent_role)
        logger.info(f"Agent SDK: Using workspace: {workspace}")

        # 2. 读取 CLAUDE.md 作为 Agent 角色定义
        claude_md_path = get_claude_md_path(agent_role)
        agent_context = claude_md_path.read_text(encoding='utf-8')
        logger.info(f"Agent SDK: Loaded CLAUDE.md ({len(agent_context)} chars)")

        # 3. 构建完整的 prompt
        full_prompt = f"""
{agent_context}

---

# 当前任务

{task_prompt}

---

# 工作环境

**工作目录**: {workspace}

**可用工具**: Bash, Read, Write, Grep, Glob

**Skills 脚本位置**: `.claude/skills/` 目录

你可以使用 Bash 工具执行 skills 脚本来获取数据。例如：
```bash
cd .claude/skills
echo '{{"days": 1}}' | python gerrit_analysis.py
```

**重要提示**:
1. 优先使用 skills 脚本获取真实数据
2. 如果无法连接真实数据源（如 Gerrit 数据库），使用 `data/` 目录中的模拟数据
3. 返回结构化的分析报告（Markdown 格式）
4. 明确说明数据来源（真实数据 or 模拟数据）

开始执行任务！
"""

        # 4. 配置 Agent SDK 选项
        if allowed_tools is None:
            allowed_tools = ["Bash", "Read", "Write", "Grep", "Glob"]

        options = ClaudeAgentOptions(
            allowed_tools=allowed_tools,
            cwd=str(workspace),
            model=settings.ANTHROPIC_MODEL
        )

        logger.info(f"Agent SDK: Executing task for {agent_role}")
        logger.info(f"Agent SDK: Allowed tools: {allowed_tools}")
        logger.info(f"Agent SDK: Model: {settings.ANTHROPIC_MODEL}")

        # 5. 执行任务并收集结果
        result_chunks = []
        message_count = 0

        async for message in query(prompt=full_prompt, options=options):
            message_count += 1

            # 处理不同类型的消息
            if hasattr(message, 'content'):
                content_str = str(message.content)
                result_chunks.append(content_str)

                # 记录工具调用（如果有）
                if 'tool_use' in content_str.lower():
                    logger.debug(f"Agent SDK: Tool use detected in message {message_count}")
            else:
                result_chunks.append(str(message))

        # 6. 返回完整结果
        full_result = '\n'.join(result_chunks)
        logger.info(f"Agent SDK: Task completed ({message_count} messages, {len(full_result)} chars)")

        return full_result

    except ValueError as e:
        # workspace 或 CLAUDE.md 不存在
        logger.error(f"Agent SDK: Configuration error - {e}")
        raise

    except Exception as e:
        # Agent 执行错误
        logger.error(f"Agent SDK: Execution failed - {e}", exc_info=True)
        raise Exception(f"Agent task execution failed for {agent_role}: {e}")


async def execute_agent_task_stream(
    agent_role: str,
    task_prompt: str,
    allowed_tools: Optional[List[str]] = None,
    on_message_chunk = None
):
    """
    使用 Claude Agent SDK 执行 Agent 任务（流式输出）

    Args:
        agent_role: Agent 角色标识
        task_prompt: 任务提示词
        allowed_tools: 允许使用的工具列表
        on_message_chunk: 接收消息块的回调函数

    Yields:
        消息块

    Raises:
        ValueError: 如果 workspace 或 CLAUDE.md 不存在
        Exception: Agent 执行过程中的错误
    """
    try:
        workspace = get_agent_workspace(agent_role)
        claude_md_path = get_claude_md_path(agent_role)
        agent_context = claude_md_path.read_text(encoding='utf-8')

        full_prompt = f"""
{agent_context}

---

当前任务：
{task_prompt}

---

工作目录：{workspace}
可用工具：Bash, Read, Write, Grep, Glob

你可以执行 .claude/skills/ 中的脚本来获取数据。
"""

        if allowed_tools is None:
            allowed_tools = ["Bash", "Read", "Write", "Grep", "Glob"]

        options = ClaudeAgentOptions(
            allowed_tools=allowed_tools,
            cwd=str(workspace),
            model=settings.ANTHROPIC_MODEL
        )

        logger.info(f"Agent SDK: Starting stream execution for {agent_role}")

        async for message in query(prompt=full_prompt, options=options):
            if on_message_chunk:
                await on_message_chunk(message)

            yield message

        logger.info(f"Agent SDK: Stream execution completed for {agent_role}")

    except Exception as e:
        logger.error(f"Agent SDK: Stream execution failed - {e}", exc_info=True)
        raise
