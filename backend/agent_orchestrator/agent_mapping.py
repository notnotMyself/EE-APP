"""
Agent 标识符映射配置

解决 Agent Orchestrator (role string) 和 Database (UUID) 之间的标识符不匹配问题。

使用方式：
    from agent_mapping import get_agent_uuid, get_agent_role, is_valid_uuid

    uuid = get_agent_uuid("dev_efficiency_analyst")
    role = get_agent_role(uuid)
"""

import re
from typing import Optional

# Agent Role → UUID 映射
# 基于数据库中已有的 agents 记录
AGENT_ROLE_TO_UUID = {
    # 完全匹配的映射
    "dev_efficiency_analyst": "a1e79944-69bf-4f06-8e05-8060bcebad30",

    # 不匹配的映射（Agent SDK role → Database UUID）
    "nps_insight_analyst": "f67d011f-f517-4f4d-961c-b67e3fc89985",  # DB: nps_analyst
    "competitor_tracking_analyst": "76741da9-cb73-48f5-b298-ba15a9bb5a96",  # DB: competitor_analyst

    # 其他 Agent SDK roles（使用固定 UUID，如果数据库中不存在）
    "product_requirement_analyst": "00000000-0000-0000-0000-000000000003",
    "knowledge_management_assistant": "00000000-0000-0000-0000-000000000005",
}

# UUID → Agent Role 反向映射
AGENT_UUID_TO_ROLE = {v: k for k, v in AGENT_ROLE_TO_UUID.items()}

# UUID 正则表达式
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


def is_valid_uuid(value: str) -> bool:
    """检查字符串是否是有效的 UUID

    Args:
        value: 要检查的字符串

    Returns:
        True 如果是有效 UUID，否则 False
    """
    if not value or not isinstance(value, str):
        return False
    return UUID_PATTERN.match(value) is not None


def get_agent_uuid(role_or_uuid: str) -> str:
    """获取 Agent 的 UUID

    如果输入已经是 UUID，直接返回；
    如果输入是 role，查找映射返回 UUID。

    Args:
        role_or_uuid: Agent 的 role string 或 UUID

    Returns:
        Agent 的 UUID

    Raises:
        ValueError: 如果 role 不存在映射且不是有效 UUID

    Examples:
        >>> get_agent_uuid("dev_efficiency_analyst")
        'a1e79944-69bf-4f06-8e05-8060bcebad30'

        >>> get_agent_uuid("a1e79944-69bf-4f06-8e05-8060bcebad30")
        'a1e79944-69bf-4f06-8e05-8060bcebad30'
    """
    # 如果已经是 UUID，直接返回
    if is_valid_uuid(role_or_uuid):
        return role_or_uuid

    # 否则查找映射
    uuid = AGENT_ROLE_TO_UUID.get(role_or_uuid)
    if uuid:
        return uuid

    # 未找到映射
    raise ValueError(
        f"Agent role '{role_or_uuid}' not found in mapping. "
        f"Available roles: {', '.join(AGENT_ROLE_TO_UUID.keys())}"
    )


def get_agent_role(uuid_or_role: str) -> Optional[str]:
    """获取 Agent 的 role string

    如果输入已经是 role，直接返回；
    如果输入是 UUID，查找反向映射返回 role。

    Args:
        uuid_or_role: Agent 的 UUID 或 role string

    Returns:
        Agent 的 role string，如果未找到返回 None

    Examples:
        >>> get_agent_role("a1e79944-69bf-4f06-8e05-8060bcebad30")
        'dev_efficiency_analyst'

        >>> get_agent_role("dev_efficiency_analyst")
        'dev_efficiency_analyst'
    """
    # 如果不是 UUID，假设已经是 role
    if not is_valid_uuid(uuid_or_role):
        return uuid_or_role if uuid_or_role in AGENT_ROLE_TO_UUID else None

    # 否则查找反向映射
    return AGENT_UUID_TO_ROLE.get(uuid_or_role)


def list_agent_mappings() -> dict:
    """列出所有 Agent 映射

    Returns:
        包含所有映射的字典
    """
    return {
        "role_to_uuid": AGENT_ROLE_TO_UUID.copy(),
        "uuid_to_role": AGENT_UUID_TO_ROLE.copy()
    }


# 测试代码
if __name__ == "__main__":
    print("Agent Mapping Configuration")
    print("=" * 60)

    print("\n✅ Role → UUID Mappings:")
    for role, uuid in AGENT_ROLE_TO_UUID.items():
        print(f"  {role:<35} → {uuid}")

    print("\n✅ UUID Validation Tests:")
    test_cases = [
        ("a1e79944-69bf-4f06-8e05-8060bcebad30", True),
        ("dev_efficiency_analyst", False),
        ("not-a-uuid", False),
        ("00000000-0000-0000-0000-000000000003", True),
    ]
    for value, expected in test_cases:
        result = is_valid_uuid(value)
        status = "✅" if result == expected else "❌"
        print(f"  {status} is_valid_uuid('{value[:30]}...') = {result}")

    print("\n✅ Conversion Tests:")
    print(f"  get_agent_uuid('dev_efficiency_analyst') = {get_agent_uuid('dev_efficiency_analyst')}")
    print(f"  get_agent_role('a1e79944-69bf-4f06-8e05-8060bcebad30') = {get_agent_role('a1e79944-69bf-4f06-8e05-8060bcebad30')}")

    print("\n✅ Idempotent Tests:")
    uuid = get_agent_uuid("dev_efficiency_analyst")
    print(f"  get_agent_uuid(get_agent_uuid('dev_efficiency_analyst')) = {get_agent_uuid(uuid)}")

    role = get_agent_role(uuid)
    print(f"  get_agent_role(get_agent_role(uuid)) = {get_agent_role(role)}")
