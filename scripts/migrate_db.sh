#!/bin/bash
# 数据库迁移执行脚本
# 用途：执行所有待处理的 Supabase 数据库迁移

set -e  # 遇到错误立即退出

echo "🗄️  Supabase Database Migration Script"
echo "======================================"

# 检查 supabase CLI 是否安装
if ! command -v supabase &> /dev/null; then
    echo "❌ Error: supabase CLI not found"
    echo "   Install: https://supabase.com/docs/guides/cli"
    exit 1
fi

# 项目配置
PROJECT_REF="dwesyojvzbltqtgtctpt"
DB_PASSWORD="ee-for-everything1"

echo ""
echo "📋 Step 1: Linking to Supabase project..."
echo "   Project: $PROJECT_REF"

# 链接项目（如果尚未链接）
if [ ! -f ".supabase/config.toml" ]; then
    echo "   Linking project..."
    supabase link --project-ref "$PROJECT_REF" --password "$DB_PASSWORD"
else
    echo "   ✅ Project already linked"
fi

echo ""
echo "📋 Step 2: Checking migration files..."
MIGRATION_COUNT=$(ls -1 supabase/migrations/*.sql 2>/dev/null | wc -l)
echo "   Found $MIGRATION_COUNT migration file(s)"

if [ "$MIGRATION_COUNT" -eq 0 ]; then
    echo "   ℹ️  No migration files found"
    exit 0
fi

# 列出最近的迁移
echo ""
echo "📋 Recent migrations:"
ls -lt supabase/migrations/*.sql | head -5 | awk '{print "   -", $9}'

echo ""
echo "📋 Step 3: Pushing migrations to database..."

# 执行迁移
if supabase db push; then
    echo ""
    echo "✅ Database migrations completed successfully!"
    echo ""
    echo "📊 Next steps:"
    echo "   - Verify tables in Supabase Dashboard"
    echo "   - Check RLS policies are enabled"
    echo "   - Test API endpoints"
else
    echo ""
    echo "❌ Migration failed!"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   1. Check database connection"
    echo "   2. Verify migration SQL syntax"
    echo "   3. Check for conflicts with existing schema"
    echo "   4. Review error messages above"
    exit 1
fi

echo ""
echo "======================================"
echo "✅ Migration script completed"
