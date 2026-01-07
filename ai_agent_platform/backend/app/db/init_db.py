"""Initialize database - Run migrations and seed data."""
import asyncio
from supabase import create_client, Client
from app.core.config import settings


async def run_migration(supabase: Client, migration_file: str):
    """Run a SQL migration file."""
    print(f"Running migration: {migration_file}")

    with open(migration_file, 'r') as f:
        sql = f.read()

    # Note: Supabase client doesn't support raw SQL execution
    # You'll need to run migrations manually via Supabase Dashboard or use psycopg2
    print(f"Migration SQL prepared. Please run it via Supabase Dashboard.")
    print("Go to: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/sql/new")
    return sql


async def seed_builtin_agents(supabase: Client):
    """Seed built-in AI agents."""
    print("Seeding built-in AI agents...")

    # Research & Development Efficiency Agent
    dev_efficiency_agent = {
        "name": "研发效能分析官",
        "description": "持续监控研发过程数据，发现异常和趋势，提供深度分析和建议",
        "role": "dev_efficiency_analyst",
        "avatar_url": None,
        "data_sources": {
            "gerrit": {
                "enabled": True,
                "metrics": ["review_time", "commit_frequency", "rework_rate"]
            },
            "jira": {
                "enabled": True,
                "metrics": ["sprint_velocity", "issue_cycle_time", "defect_rate"]
            }
        },
        "trigger_conditions": {
            "review_time_threshold_hours": 48,
            "rework_rate_threshold_percent": 20,
            "load_threshold_percentile": 90,
            "trend_window_days": 14
        },
        "capabilities": {
            "can_generate_reports": True,
            "can_create_charts": True,
            "can_analyze_trends": True,
            "can_detect_anomalies": True
        },
        "is_active": True,
        "is_builtin": True,
        "metadata": {
            "category": "engineering",
            "tags": ["dev", "efficiency", "analytics"],
            "version": "1.0"
        }
    }

    # Insert agent
    response = supabase.table('agents').insert(dev_efficiency_agent).execute()
    print(f"Created agent: {response.data}")

    return response.data


async def init_db():
    """Initialize database."""
    print("Initializing database...")

    # Create Supabase client
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )

    # Run migrations
    print("\n=== Running Migrations ===")
    migration_sql = await run_migration(
        supabase,
        "migrations/001_initial_schema.sql"
    )

    print("\n=== Please run the following SQL in Supabase Dashboard ===")
    print(migration_sql[:500] + "...")
    print("\n=== After running migrations, run this script again to seed data ===")

    # Seed data (comment out until migrations are run)
    # print("\n=== Seeding Data ===")
    # await seed_builtin_agents(supabase)

    print("\n=== Database initialization complete ===")


if __name__ == "__main__":
    asyncio.run(init_db())
