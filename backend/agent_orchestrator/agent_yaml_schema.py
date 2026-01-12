"""
Agent YAML Schema 定义

定义 agent.yaml 的数据结构和验证规则。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from pathlib import Path
import yaml


@dataclass
class AgentMetadata:
    """Agent 元数据"""
    id: str  # Agent 唯一标识符（role string）
    uuid: str  # Agent UUID（数据库主键）
    name: str  # 显示名称
    description: str  # 功能描述
    model: str = "saas/claude-sonnet-4.5"  # 默认模型
    visibility: Literal["public", "private"] = "public"  # 可见性
    owner_team: Optional[str] = None  # 私有 Agent 所属团队

    def __post_init__(self):
        """验证规则"""
        if self.visibility == "private" and not self.owner_team:
            raise ValueError(f"Private agent '{self.id}' must specify owner_team")
        if self.visibility == "public" and self.owner_team:
            raise ValueError(f"Public agent '{self.id}' cannot specify owner_team")


@dataclass
class AgentSkill:
    """Agent 技能定义"""
    name: str  # Skill 名称
    entry: str  # Skill 入口脚本路径（相对于 agent 目录）
    description: Optional[str] = None  # Skill 描述
    timeout: int = 300  # 执行超时时间（秒）


@dataclass
class AgentSchedule:
    """Agent 定时任务"""
    cron: str  # Cron 表达式
    task: str  # 任务描述（会传给 Claude）
    enabled: bool = True  # 是否启用


@dataclass
class AgentSecret:
    """Agent 密钥配置"""
    name: str  # 环境变量名
    source: Literal["env", "supabase_secrets"]  # 密钥来源
    key: Optional[str] = None  # supabase_secrets 时的 key 名称


@dataclass
class AgentYamlConfig:
    """Agent YAML 完整配置"""
    metadata: AgentMetadata
    skills: List[AgentSkill] = field(default_factory=list)
    schedule: List[AgentSchedule] = field(default_factory=list)
    secrets: List[AgentSecret] = field(default_factory=list)
    allowed_tools: List[str] = field(default_factory=lambda: [
        "Read", "Write", "Bash", "Grep", "Glob", "WebFetch"
    ])
    max_turns: int = 20

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "AgentYamlConfig":
        """从 YAML 文件加载配置"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(
            metadata=AgentMetadata(**data['metadata']),
            skills=[AgentSkill(**skill) for skill in data.get('skills', [])],
            schedule=[AgentSchedule(**sched) for sched in data.get('schedule', [])],
            secrets=[AgentSecret(**secret) for secret in data.get('secrets', [])],
            allowed_tools=data.get('allowed_tools', cls.__dataclass_fields__['allowed_tools'].default_factory()),
            max_turns=data.get('max_turns', 20)
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'metadata': {
                'id': self.metadata.id,
                'uuid': self.metadata.uuid,
                'name': self.metadata.name,
                'description': self.metadata.description,
                'model': self.metadata.model,
                'visibility': self.metadata.visibility,
                'owner_team': self.metadata.owner_team,
            },
            'skills': [
                {
                    'name': skill.name,
                    'entry': skill.entry,
                    'description': skill.description,
                    'timeout': skill.timeout
                }
                for skill in self.skills
            ],
            'schedule': [
                {
                    'cron': sched.cron,
                    'task': sched.task,
                    'enabled': sched.enabled
                }
                for sched in self.schedule
            ],
            'secrets': [
                {
                    'name': secret.name,
                    'source': secret.source,
                    'key': secret.key
                }
                for secret in self.secrets
            ],
            'allowed_tools': self.allowed_tools,
            'max_turns': self.max_turns
        }


def validate_agent_yaml(yaml_path: Path) -> tuple[bool, Optional[str]]:
    """验证 agent.yaml 文件

    Returns:
        (是否有效, 错误信息)
    """
    try:
        config = AgentYamlConfig.from_yaml(yaml_path)

        # 验证 skills 入口文件存在
        agent_dir = yaml_path.parent
        for skill in config.skills:
            skill_path = agent_dir / skill.entry
            if not skill_path.exists():
                return False, f"Skill entry not found: {skill.entry}"

        return True, None
    except Exception as e:
        return False, str(e)


# Schema 文档（用于生成示例和文档）
AGENT_YAML_SCHEMA_DOC = """
# Agent YAML Schema

## 完整示例

```yaml
metadata:
  id: dev_efficiency_analyst
  uuid: a1e79944-69bf-4f06-8e05-8060bcebad30
  name: 研发效能分析官
  description: 持续监控团队研发效率，分析代码审查数据，检测异常趋势
  model: saas/claude-sonnet-4.5
  visibility: public  # public | private
  owner_team: null    # 仅 private 时需要

skills:
  - name: build_analysis
    entry: .claude/skills/build_analysis.py
    description: 分析 CI/CD 构建数据
    timeout: 300

  - name: gerrit_review
    entry: .claude/skills/gerrit_review.py
    description: 分析 Gerrit 代码审查数据
    timeout: 180

schedule:
  - cron: "0 9 * * 1-5"
    task: 生成每日效能简报
    enabled: true

  - cron: "0 18 * * 5"
    task: 生成周报
    enabled: false

secrets:
  - name: GERRIT_DB_PASSWORD
    source: env  # 从环境变量获取

  - name: NEWS_API_KEY
    source: supabase_secrets
    key: news_api_key  # Supabase 密钥表的 key

allowed_tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebFetch

max_turns: 20
```

## 私有 Agent 示例

```yaml
metadata:
  id: team_a_custom_agent
  uuid: 00000000-0000-0000-0000-000000000099
  name: 团队A定制Agent
  description: 团队A的特定业务分析
  visibility: private
  owner_team: team_a

skills:
  - name: custom_analysis
    entry: .claude/skills/custom.py

schedule: []
secrets: []
allowed_tools: [Read, Write]
max_turns: 15
```

## 字段说明

### metadata (必填)
- `id`: Agent 唯一标识符（role string），需与目录名一致
- `uuid`: Agent UUID（数据库主键）
- `name`: 显示名称
- `description`: 功能描述
- `model`: 使用的 Claude 模型（默认：saas/claude-sonnet-4.5）
- `visibility`: 可见性（public | private，默认：public）
- `owner_team`: 私有 Agent 所属团队（仅 visibility=private 时必填）

### skills (可选)
- `name`: Skill 名称
- `entry`: Skill 入口脚本路径（相对于 agent 目录）
- `description`: Skill 描述
- `timeout`: 执行超时时间（秒，默认：300）

### schedule (可选)
- `cron`: Cron 表达式（支持标准 5 字段格式）
- `task`: 任务描述（会作为 prompt 传给 Claude）
- `enabled`: 是否启用（默认：true）

### secrets (可选)
- `name`: 环境变量名
- `source`: 密钥来源（env | supabase_secrets）
- `key`: supabase_secrets 时的 key 名称

### allowed_tools (可选)
默认：["Read", "Write", "Bash", "Grep", "Glob", "WebFetch"]

### max_turns (可选)
默认：20
"""


if __name__ == "__main__":
    # 测试加载示例 YAML
    import sys
    import tempfile

    example_yaml = """
metadata:
  id: test_agent
  uuid: 00000000-0000-0000-0000-000000000001
  name: 测试Agent
  description: 用于测试
  visibility: public

skills:
  - name: test_skill
    entry: .claude/skills/test.py

schedule:
  - cron: "0 9 * * *"
    task: 每日任务

allowed_tools:
  - Read
  - Write

max_turns: 15
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(example_yaml)
        temp_path = Path(f.name)

    try:
        config = AgentYamlConfig.from_yaml(temp_path)
        print("✅ YAML 加载成功:")
        print(f"  ID: {config.metadata.id}")
        print(f"  Name: {config.metadata.name}")
        print(f"  Skills: {[s.name for s in config.skills]}")
        print(f"  Schedule: {len(config.schedule)} tasks")
    except Exception as e:
        print(f"❌ YAML 加载失败: {e}")
        sys.exit(1)
    finally:
        temp_path.unlink()
