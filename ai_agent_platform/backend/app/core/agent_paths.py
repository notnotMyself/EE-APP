"""
Agent Workspace 路径解析器

提供函数来定位 Agent 的工作目录和相关文件。
"""

import os
from pathlib import Path
from typing import Optional


def get_agent_workspace(agent_role: str) -> Path:
    """
    获取 Agent 的 workspace 路径

    Args:
        agent_role: Agent 角色标识（如 'dev_efficiency_analyst'）

    Returns:
        Agent workspace 的 Path 对象

    Raises:
        ValueError: 如果 workspace 不存在
    """
    # 基于项目根目录解析
    # 当前文件在: ai_agent_platform/backend/app/core/agent_paths.py
    # 需要到达: backend/agents/{agent_role}/
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent.parent
    workspace = project_root / "backend" / "agents" / agent_role

    if not workspace.exists():
        raise ValueError(
            f"Agent workspace not found: {workspace}\n"
            f"Expected path: {workspace}\n"
            f"Agent role: {agent_role}\n"
            f"Please ensure the Agent directory exists."
        )

    return workspace


def get_claude_md_path(agent_role: str) -> Path:
    """
    获取 Agent 的 CLAUDE.md 文件路径

    Args:
        agent_role: Agent 角色标识

    Returns:
        CLAUDE.md 文件的 Path 对象

    Raises:
        ValueError: 如果文件不存在
    """
    workspace = get_agent_workspace(agent_role)
    claude_md = workspace / "CLAUDE.md"

    if not claude_md.exists():
        raise ValueError(
            f"CLAUDE.md not found: {claude_md}\n"
            f"Each Agent must have a CLAUDE.md file defining its role and capabilities."
        )

    return claude_md


def get_skills_directory(agent_role: str) -> Path:
    """
    获取 Agent 的 skills 目录路径

    Args:
        agent_role: Agent 角色标识

    Returns:
        .claude/skills/ 目录的 Path 对象
    """
    workspace = get_agent_workspace(agent_role)
    skills_dir = workspace / ".claude" / "skills"

    if not skills_dir.exists():
        # 创建目录（可选）
        skills_dir.mkdir(parents=True, exist_ok=True)

    return skills_dir


def get_reports_directory(agent_role: str) -> Path:
    """
    获取 Agent 的 reports 目录路径

    Args:
        agent_role: Agent 角色标识

    Returns:
        reports/ 目录的 Path 对象
    """
    workspace = get_agent_workspace(agent_role)
    reports_dir = workspace / "reports"

    if not reports_dir.exists():
        reports_dir.mkdir(parents=True, exist_ok=True)

    return reports_dir
