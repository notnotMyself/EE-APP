#!/usr/bin/env python3
"""
快速检查 Supabase agents 表中的记录
"""

import os
import sys
from pathlib import Path

# 添加父目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv
    env_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent.parent / "ai_agent_platform/backend/.env",
        Path(__file__).parent.parent.parent / "ai_agent_app/backend/.env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded .env from {env_path}")
            break
except ImportError:
    pass

from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Supabase not configured")
    sys.exit(1)

print(f"✅ Connecting to Supabase: {supabase_url}")

supabase = create_client(supabase_url, supabase_key)

# 查询 agents 表
try:
    result = supabase.table("agents").select("id, role, name, is_builtin, is_active").execute()

    print(f"\n📊 Found {len(result.data)} agents in database:\n")
    print(f"{'ID':<40} {'Role':<30} {'Name':<20} {'Built-in':<10} {'Active':<10}")
    print("=" * 120)

    for agent in result.data:
        print(f"{agent['id']:<40} {agent.get('role', 'N/A'):<30} {agent.get('name', 'N/A'):<20} {agent.get('is_builtin', False)!s:<10} {agent.get('is_active', False)!s:<10}")

    # 生成映射配置
    print("\n\n🔧 Suggested mapping configuration:\n")
    print("AGENT_ROLE_TO_UUID = {")
    for agent in result.data:
        if agent.get('role'):
            print(f'    "{agent["role"]}": "{agent["id"]}",')
    print("}")

except Exception as e:
    print(f"❌ Error querying agents: {e}")
    print("\n💡 Agents table might not exist or have different schema")
    sys.exit(1)
