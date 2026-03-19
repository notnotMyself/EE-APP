"""
Agent 标识符映射

支持 role string 和 UUID 之间的转换。
优先使用数据库查询，hardcoded 映射仅作为 fallback。
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Hardcoded fallback mapping (for agents not yet in DB)
AGENT_ROLE_TO_UUID = {
    "dev_efficiency_analyst": "a1e79944-69bf-4f06-8e05-8060bcebad30",
    "design_validator": "7e2f3c4d-5a6b-4e8f-9a0b-8c7d6e5f4a3b",
    "nps_insight_analyst": "f67d011f-f517-4f4d-961c-b67e3fc89985",
    "competitor_tracking_analyst": "76741da9-cb73-48f5-b298-ba15a9bb5a96",
    "product_requirement_analyst": "00000000-0000-0000-0000-000000000003",
    "knowledge_management_assistant": "00000000-0000-0000-0000-000000000005",
}

AGENT_UUID_TO_ROLE = {v: k for k, v in AGENT_ROLE_TO_UUID.items()}

UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

# Optional supabase client, set by main.py at startup
_supabase_client = None


def set_supabase_client(client):
    """Inject supabase client so get_agent_uuid can query the DB."""
    global _supabase_client
    _supabase_client = client


def is_valid_uuid(value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    return UUID_PATTERN.match(value) is not None


def _lookup_uuid_from_db(role: str) -> Optional[str]:
    """Query agents table by role to find UUID."""
    if not _supabase_client:
        return None
    try:
        result = (
            _supabase_client.table("agents")
            .select("id")
            .eq("role", role)
            .limit(1)
            .execute()
        )
        if result.data and len(result.data) > 0:
            uuid = result.data[0]["id"]
            # Cache it for future lookups
            AGENT_ROLE_TO_UUID[role] = uuid
            AGENT_UUID_TO_ROLE[uuid] = role
            logger.info(f"Resolved agent role '{role}' to UUID '{uuid}' from DB")
            return uuid
    except Exception as e:
        logger.warning(f"DB lookup for agent role '{role}' failed: {e}")
    return None


def get_agent_uuid(role_or_uuid: str) -> str:
    """Get agent UUID from role string or passthrough UUID.

    Resolution order:
    1. If already a UUID, return as-is
    2. Check hardcoded mapping
    3. Query agents table by role
    4. Raise ValueError
    """
    if is_valid_uuid(role_or_uuid):
        return role_or_uuid

    # Hardcoded mapping
    uuid = AGENT_ROLE_TO_UUID.get(role_or_uuid)
    if uuid:
        return uuid

    # DB lookup
    uuid = _lookup_uuid_from_db(role_or_uuid)
    if uuid:
        return uuid

    raise ValueError(
        f"Agent role '{role_or_uuid}' not found in mapping or database. "
        f"Available roles: {', '.join(AGENT_ROLE_TO_UUID.keys())}"
    )


def get_agent_role(uuid_or_role: str) -> Optional[str]:
    if not is_valid_uuid(uuid_or_role):
        return uuid_or_role if uuid_or_role in AGENT_ROLE_TO_UUID else None
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
