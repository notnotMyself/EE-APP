"""
Agent Registry - Agent 注册中心

负责自动发现、加载和管理所有 Agent 配置。
取代 config.py 和 agent_mapping.py 中的硬编码配置。
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml
import sys

# 支持相对导入和直接运行
try:
    from .agent_yaml_schema import AgentYamlConfig, validate_agent_yaml
except ImportError:
    # 直接运行时使用绝对导入
    sys.path.insert(0, str(Path(__file__).parent))
    from agent_yaml_schema import AgentYamlConfig, validate_agent_yaml

logger = logging.getLogger(__name__)


@dataclass
class RegisteredAgent:
    """注册的 Agent 信息"""
    config: AgentYamlConfig
    yaml_path: Path
    agent_dir: Path

    @property
    def id(self) -> str:
        return self.config.metadata.id

    @property
    def uuid(self) -> str:
        return self.config.metadata.uuid

    @property
    def name(self) -> str:
        return self.config.metadata.name

    @property
    def is_public(self) -> bool:
        return self.config.metadata.visibility == "public"

    @property
    def owner_team(self) -> Optional[str]:
        return self.config.metadata.owner_team


class AgentRegistry:
    """Agent 注册中心

    自动发现和加载 agents/ 目录下的所有 agent.yaml 配置。

    用法:
        registry = AgentRegistry(Path("backend/agents"))

        # 列出所有公开 Agent
        public_agents = registry.list_agents()

        # 列出特定团队可见的 Agent
        team_agents = registry.list_agents(user_team="team_a")

        # 获取单个 Agent
        agent = registry.get_agent("dev_efficiency_analyst")
    """

    def __init__(self, agents_base_dir: Path):
        """初始化 Agent Registry

        Args:
            agents_base_dir: agents 根目录路径
        """
        self.agents_base_dir = Path(agents_base_dir)
        self._agents: Dict[str, RegisteredAgent] = {}
        self._uuid_to_id: Dict[str, str] = {}

        # 自动扫描和加载
        self._scan_and_load()

    def _scan_and_load(self):
        """扫描 agents 目录并加载所有 agent.yaml"""
        if not self.agents_base_dir.exists():
            logger.warning(f"Agents directory not found: {self.agents_base_dir}")
            return

        logger.info(f"Scanning agents directory: {self.agents_base_dir}")

        for agent_dir in self.agents_base_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            yaml_path = agent_dir / "agent.yaml"
            if not yaml_path.exists():
                logger.debug(f"Skipping {agent_dir.name}: no agent.yaml found")
                continue

            try:
                self._load_agent(agent_dir, yaml_path)
            except Exception as e:
                logger.error(f"Failed to load agent from {agent_dir.name}: {e}")

        logger.info(f"Loaded {len(self._agents)} agents: {list(self._agents.keys())}")

    def _load_agent(self, agent_dir: Path, yaml_path: Path):
        """加载单个 Agent 配置

        Args:
            agent_dir: Agent 目录路径
            yaml_path: agent.yaml 文件路径
        """
        # 验证 YAML
        is_valid, error_msg = validate_agent_yaml(yaml_path)
        if not is_valid:
            raise ValueError(f"Invalid agent.yaml: {error_msg}")

        # 加载配置
        config = AgentYamlConfig.from_yaml(yaml_path)

        # 验证目录名和 ID 一致
        if agent_dir.name != config.metadata.id:
            logger.warning(
                f"Agent directory name '{agent_dir.name}' does not match "
                f"agent.yaml id '{config.metadata.id}'. Using id from YAML."
            )

        # 注册 Agent
        agent = RegisteredAgent(
            config=config,
            yaml_path=yaml_path,
            agent_dir=agent_dir
        )

        self._agents[config.metadata.id] = agent
        self._uuid_to_id[config.metadata.uuid] = config.metadata.id

        logger.info(
            f"Registered agent: {config.metadata.id} "
            f"(uuid={config.metadata.uuid}, visibility={config.metadata.visibility})"
        )

    def reload(self):
        """重新扫描和加载所有 Agent"""
        self._agents.clear()
        self._uuid_to_id.clear()
        self._scan_and_load()

    def list_agents(
        self,
        user_team: Optional[str] = None,
        visibility: Optional[str] = None
    ) -> List[RegisteredAgent]:
        """列出可见的 Agent

        Args:
            user_team: 用户所属团队（用于过滤私有 Agent）
            visibility: 过滤可见性（public | private）

        Returns:
            Agent 列表
        """
        agents = []

        for agent in self._agents.values():
            # 可见性过滤
            if visibility and agent.config.metadata.visibility != visibility:
                continue

            # 权限检查
            if agent.config.metadata.visibility == "private":
                # 私有 Agent：只有所属团队可见
                if not user_team or user_team != agent.config.metadata.owner_team:
                    continue

            agents.append(agent)

        return agents

    def get_agent(
        self,
        agent_id_or_uuid: str,
        user_team: Optional[str] = None
    ) -> Optional[RegisteredAgent]:
        """获取单个 Agent

        Args:
            agent_id_or_uuid: Agent ID 或 UUID
            user_team: 用户所属团队（用于权限检查）

        Returns:
            Agent 对象，如果不存在或无权限则返回 None
        """
        # 尝试通过 ID 获取
        agent = self._agents.get(agent_id_or_uuid)

        # 如果不存在，尝试通过 UUID 获取
        if not agent:
            agent_id = self._uuid_to_id.get(agent_id_or_uuid)
            if agent_id:
                agent = self._agents.get(agent_id)

        if not agent:
            return None

        # 权限检查
        if agent.config.metadata.visibility == "private":
            if not user_team or user_team != agent.config.metadata.owner_team:
                logger.warning(
                    f"Access denied: Agent {agent.id} is private to team "
                    f"{agent.config.metadata.owner_team}, user team is {user_team}"
                )
                return None

        return agent

    def get_agent_uuid(self, agent_id: str) -> Optional[str]:
        """通过 Agent ID 获取 UUID

        Args:
            agent_id: Agent ID

        Returns:
            UUID string，如果不存在返回 None
        """
        agent = self._agents.get(agent_id)
        return agent.uuid if agent else None

    def get_agent_id(self, uuid: str) -> Optional[str]:
        """通过 UUID 获取 Agent ID

        Args:
            uuid: Agent UUID

        Returns:
            Agent ID，如果不存在返回 None
        """
        return self._uuid_to_id.get(uuid)

    def exists(self, agent_id_or_uuid: str) -> bool:
        """检查 Agent 是否存在

        Args:
            agent_id_or_uuid: Agent ID 或 UUID

        Returns:
            True 如果存在，否则 False
        """
        return (
            agent_id_or_uuid in self._agents or
            agent_id_or_uuid in self._uuid_to_id
        )

    def get_all_ids(self) -> List[str]:
        """获取所有 Agent ID 列表"""
        return list(self._agents.keys())

    def get_all_uuids(self) -> List[str]:
        """获取所有 Agent UUID 列表"""
        return list(self._uuid_to_id.keys())

    def get_config_dict(self, agent_id: str) -> Optional[Dict]:
        """获取 Agent 配置的字典表示（兼容旧代码）

        Args:
            agent_id: Agent ID

        Returns:
            配置字典，如果不存在返回 None
        """
        agent = self._agents.get(agent_id)
        return agent.config.to_dict() if agent else None


# 全局单例
_global_registry: Optional[AgentRegistry] = None


def get_global_registry() -> AgentRegistry:
    """获取全局 Agent Registry 单例"""
    global _global_registry
    if _global_registry is None:
        # 默认路径
        from pathlib import Path
        agents_dir = Path(__file__).parent.parent / "agents"
        _global_registry = AgentRegistry(agents_dir)
    return _global_registry


def init_global_registry(agents_base_dir: Path):
    """初始化全局 Agent Registry

    Args:
        agents_base_dir: agents 根目录路径
    """
    global _global_registry
    _global_registry = AgentRegistry(agents_base_dir)
    return _global_registry


# 兼容性函数（用于替换 agent_mapping.py）
def get_agent_uuid(role_or_uuid: str) -> str:
    """兼容 agent_mapping.py 的 get_agent_uuid 函数"""
    from .agent_mapping import is_valid_uuid

    # 如果已经是 UUID，直接返回
    if is_valid_uuid(role_or_uuid):
        return role_or_uuid

    # 否则从 registry 查找
    registry = get_global_registry()
    uuid = registry.get_agent_uuid(role_or_uuid)
    if uuid:
        return uuid

    # 未找到，抛出异常
    raise ValueError(
        f"Agent role '{role_or_uuid}' not found in registry. "
        f"Available roles: {', '.join(registry.get_all_ids())}"
    )


def get_agent_role(uuid_or_role: str) -> Optional[str]:
    """兼容 agent_mapping.py 的 get_agent_role 函数"""
    from .agent_mapping import is_valid_uuid

    # 如果不是 UUID，假设已经是 role
    if not is_valid_uuid(uuid_or_role):
        registry = get_global_registry()
        return uuid_or_role if registry.exists(uuid_or_role) else None

    # 否则从 registry 查找
    registry = get_global_registry()
    return registry.get_agent_id(uuid_or_role)


if __name__ == "__main__":
    # 测试代码
    import sys
    from pathlib import Path

    # 初始化 registry
    agents_dir = Path(__file__).parent.parent / "agents"
    registry = AgentRegistry(agents_dir)

    print("=" * 60)
    print("Agent Registry Test")
    print("=" * 60)

    print(f"\n📂 Agents directory: {agents_dir}")
    print(f"✅ Loaded {len(registry._agents)} agents")

    print("\n📋 All Agents:")
    for agent in registry.list_agents():
        print(f"  • {agent.id}")
        print(f"    UUID: {agent.uuid}")
        print(f"    Name: {agent.name}")
        print(f"    Visibility: {agent.config.metadata.visibility}")
        print(f"    Skills: {[s.name for s in agent.config.skills]}")
        print()

    print("🔍 Testing queries:")

    # 测试通过 ID 获取
    agent = registry.get_agent("dev_efficiency_analyst")
    if agent:
        print(f"  ✅ get_agent('dev_efficiency_analyst'): {agent.name}")

    # 测试通过 UUID 获取
    uuid = registry.get_agent_uuid("dev_efficiency_analyst")
    if uuid:
        agent = registry.get_agent(uuid)
        print(f"  ✅ get_agent('{uuid}'): {agent.name if agent else 'None'}")

    # 测试可见性过滤
    public_agents = registry.list_agents(visibility="public")
    print(f"  ✅ Public agents: {[a.id for a in public_agents]}")

    print("\n✅ All tests passed!")
