# Database Migration Script

This script will execute the database migrations directly on your Supabase instance.

## Prerequisites

You need your Supabase database password. To get it:

1. Go to [Supabase Dashboard - Database Settings](https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/database)
2. Copy your database password (or reset if needed)

## Run Migration

```bash
# Install dependencies (if not already installed)
pip3 install psycopg2-binary

# Run migration
python3 run_migration.py YOUR_DATABASE_PASSWORD
```

Replace `YOUR_DATABASE_PASSWORD` with your actual Supabase database password.

## What This Script Does

1. Connects to your Supabase PostgreSQL database
2. Executes the SQL from `backend/migrations/001_initial_schema.sql`
3. Creates all 9 tables:
   - users
   - agents
   - user_agent_subscriptions
   - alerts
   - conversations
   - messages
   - tasks
   - artifacts
   - agent_analytics
4. Sets up Row Level Security (RLS) policies
5. Creates indexes and triggers

## Verify Migration

After running, the script will show you all created tables.

You can also verify in Supabase Dashboard:
- Go to [Table Editor](https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/editor)
- You should see all 9 tables

## Troubleshooting

**"Connection refused" or "Timeout"**
- Check your internet connection
- Verify the Supabase project is active
- Make sure you're using the correct password

**"Permission denied"**
- Make sure you're using the database password, not the API keys
- Try resetting your database password in Supabase Dashboard

**"Table already exists"**
- The migration has already been run
- You can skip this step and proceed to start the backend server
