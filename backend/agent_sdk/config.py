"""
Agent SDK 配置管理
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _load_claude_settings() -> Dict[str, str]:
    """从 ~/.claude/settings.json 加载环境变量配置"""
    settings_path = Path.home() / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                return settings.get("env", {})
        except (json.JSONDecodeError, IOError):
            pass
    return {}


# 预加载 Claude settings
_CLAUDE_SETTINGS = _load_claude_settings()


@dataclass
class AgentRoleConfig:
    """单个 Agent 角色配置"""
    name: str
    description: str
    model: str = "saas/claude-sonnet-4.5"  # 使用完整模型名称
    allowed_tools: List[str] = field(default_factory=lambda: ["Read", "Write", "Bash", "Grep", "Glob"])
    max_turns: int = 20


@dataclass
class AgentSDKConfig:
    """Agent SDK 全局配置"""

    # API Gateway - 优先级: 环境变量 > Claude settings > 默认值
    anthropic_base_url: str = field(
        default_factory=lambda: os.getenv(
            "ANTHROPIC_BASE_URL",
            _CLAUDE_SETTINGS.get("ANTHROPIC_BASE_URL", "https://llm-gateway.oppoer.me")
        )
    )

    # API Key - 优先级: 环境变量 > Claude settings
    anthropic_auth_token: Optional[str] = field(
        default_factory=lambda: os.getenv(
            "ANTHROPIC_AUTH_TOKEN",
            _CLAUDE_SETTINGS.get("ANTHROPIC_AUTH_TOKEN")
        )
    )

    # Agent 工作目录
    agents_base_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "agents"
    )

    # 默认模型（使用完整模型名称，兼容企业 Gateway）
    default_model: str = field(
        default_factory=lambda: _CLAUDE_SETTINGS.get(
            "ANTHROPIC_MODEL",
            "saas/claude-sonnet-4.5"
        )
    )

    # 消息更新频率（秒）
    message_update_interval: float = 0.5

    # 最大轮数
    max_turns: int = 20

    # 权限模式: acceptEdits / bypassPermissions
    permission_mode: str = "acceptEdits"

    # 任务超时时间（秒）
    task_timeout: int = 300  # 5 分钟

    # Agent 角色配置
    agent_roles: Dict[str, AgentRoleConfig] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        # 确保路径是 Path 对象
        if isinstance(self.agents_base_dir, str):
            self.agents_base_dir = Path(self.agents_base_dir)

        # 注册默认 Agent 角色
        if not self.agent_roles:
            self.agent_roles = self._default_agent_roles()

    def _default_agent_roles(self) -> Dict[str, AgentRoleConfig]:
        """默认 Agent 角色配置"""
        # 从 Claude settings 获取模型别名映射
        sonnet_model = _CLAUDE_SETTINGS.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "saas/claude-sonnet-4.5")
        haiku_model = _CLAUDE_SETTINGS.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "saas/claude-haiku-4.5")
        
        return {
            "dev_efficiency_analyst": AgentRoleConfig(
                name="研发效能分析官",
                description="持续监控团队研发效率，分析代码审查数据，检测异常趋势",
                model=sonnet_model,
                allowed_tools=["Read", "Write", "Bash", "Grep", "Glob", "WebFetch"],
                max_turns=20,
            ),
            "nps_insight_analyst": AgentRoleConfig(
                name="NPS洞察官",
                description="分析用户满意度数据，提取用户痛点，识别改进机会",
                model=sonnet_model,
                allowed_tools=["Read", "Write", "Bash", "Grep"],
                max_turns=15,
            ),
            "product_requirement_analyst": AgentRoleConfig(
                name="产品需求提炼官",
                description="帮助提炼和分析产品需求，确保需求清晰可执行",
                model=sonnet_model,
                allowed_tools=["Read", "Write", "Bash"],
                max_turns=15,
            ),
            "competitor_tracking_analyst": AgentRoleConfig(
                name="竞品追踪分析官",
                description="追踪竞品动态，分析市场趋势，提供竞争洞察",
                model=sonnet_model,
                allowed_tools=["Read", "Write", "WebFetch"],
                max_turns=20,
            ),
            "knowledge_management_assistant": AgentRoleConfig(
                name="企业知识管理官",
                description="组织和管理企业知识，帮助团队高效获取信息",
                model=haiku_model,
                allowed_tools=["Read", "Grep", "Glob"],
                max_turns=10,
            ),
        }

    def get_agent_role(self, role: str) -> Optional[AgentRoleConfig]:
        """获取 Agent 角色配置"""
        return self.agent_roles.get(role)

    def get_agent_workdir(self, role: str) -> Path:
        """获取 Agent 工作目录"""
        return self.agents_base_dir / role

    def get_env_dict(self) -> Dict[str, str]:
        """
        获取传递给 SDK 的环境变量字典
        
        注意：Claude Agent SDK 不会自动读取 ~/.claude/settings.json 中的环境变量，
        需要通过 ClaudeAgentOptions.env 显式传递。
        """
        # 首先从 Claude settings 获取所有环境变量
        env = dict(_CLAUDE_SETTINGS)
        
        # 然后用当前配置覆盖（优先级更高）
        if self.anthropic_base_url:
            env["ANTHROPIC_BASE_URL"] = self.anthropic_base_url
        if self.anthropic_auth_token:
            env["ANTHROPIC_AUTH_TOKEN"] = self.anthropic_auth_token
        
        return env

    def validate(self) -> bool:
        """验证配置有效性"""
        if not self.anthropic_auth_token:
            raise ValueError("ANTHROPIC_AUTH_TOKEN is required")
        if not self.agents_base_dir.exists():
            raise ValueError(f"Agents base directory not found: {self.agents_base_dir}")
        return True


# 全局配置实例
_config: Optional[AgentSDKConfig] = None


def get_config() -> AgentSDKConfig:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = AgentSDKConfig()
    return _config


def set_config(config: AgentSDKConfig) -> None:
    """设置全局配置实例"""
    global _config
    _config = config
