#!/usr/bin/env python3
"""
Database migration script - Execute SQL migrations directly on Supabase.
"""
import psycopg2
from psycopg2 import sql
import os

# Database connection string
# Using Supabase pooler with correct username format: postgres.project-ref
DB_CONNECTION = "postgresql://postgres.dwesyojvzbltqtgtctpt:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

def read_sql_file(filepath):
    """Read SQL file content."""
    with open(filepath, 'r') as f:
        return f.read()

def execute_migration(connection_string, sql_content):
    """Execute SQL migration."""
    print("Connecting to database...")

    conn = None
    try:
        # Disable GSSAPI to avoid negotiation issues
        conn = psycopg2.connect(connection_string, gssencmode='disable')
        conn.autocommit = True
        cursor = conn.cursor()

        print("Executing migration SQL...")
        cursor.execute(sql_content)

        print("✅ Migration completed successfully!")

        # Verify tables were created
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        return True

    except Exception as e:
        print(f"❌ Error executing migration: {e}")
        return False

    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <database_password>")
        print("\nExample:")
        print("  python run_migration.py your_db_password")
        sys.exit(1)

    password = sys.argv[1]
    connection_string = DB_CONNECTION.replace("[PASSWORD]", password)

    # Read migration file
    migration_file = "ai_agent_platform/backend/migrations/001_initial_schema.sql"

    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)

    sql_content = read_sql_file(migration_file)
    print(f"📄 Read migration file: {migration_file}")
    print(f"📝 SQL size: {len(sql_content)} characters\n")

    # Execute migration
    success = execute_migration(connection_string, sql_content)

    if success:
        print("\n🎉 Database migration completed successfully!")
        print("\nNext steps:")
        print("  1. Start the backend server: cd ai_agent_platform/backend && python3 main.py")
        print("  2. Test the API: http://localhost:8000/docs")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
