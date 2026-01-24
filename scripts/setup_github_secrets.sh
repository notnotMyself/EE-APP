#!/bin/bash
# GitHub Secrets 配置助手

echo "🔐 GitHub Secrets 配置助手"
echo "================================"
echo ""

# 检查 gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ 未安装 GitHub CLI (gh)"
    echo ""
    echo "请按照以下步骤手动配置："
    echo ""
    echo "1️⃣  获取 Supabase Service Key："
    echo "   访问: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/api"
    echo "   找到 'service_role' 部分"
    echo "   点击眼睛图标显示密钥"
    echo "   复制这个 key (以 'eyJ' 开头的长字符串)"
    echo ""
    echo "2️⃣  配置 GitHub Secrets："
    echo "   访问: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/settings/secrets/actions"
    echo "   点击 'New repository secret'"
    echo ""
    echo "   添加第一个 Secret:"
    echo "   Name:   SUPABASE_URL"
    echo "   Secret: https://dwesyojvzbltqtgtctpt.supabase.co"
    echo ""
    echo "   添加第二个 Secret:"
    echo "   Name:   SUPABASE_SERVICE_KEY"
    echo "   Secret: [粘贴你在步骤1复制的 key]"
    echo ""
    exit 1
fi

# 使用 gh CLI 配置
echo "✅ 检测到 GitHub CLI"
echo ""
echo "请提供以下信息："
echo ""

# 获取 Service Key
echo "📋 第一步：获取 Supabase Service Key"
echo "访问: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/api"
echo "找到 'service_role' 部分，复制那个 key"
echo ""
read -p "请粘贴 Service Key: " SERVICE_KEY

if [ -z "$SERVICE_KEY" ]; then
    echo "❌ Service Key 不能为空"
    exit 1
fi

# 配置 SUPABASE_URL
echo ""
echo "🔧 配置 SUPABASE_URL..."
echo "https://dwesyojvzbltqtgtctpt.supabase.co" | gh secret set SUPABASE_URL

# 配置 SUPABASE_SERVICE_KEY
echo "🔧 配置 SUPABASE_SERVICE_KEY..."
echo "$SERVICE_KEY" | gh secret set SUPABASE_SERVICE_KEY

echo ""
echo "✅ GitHub Secrets 配置完成！"
echo ""
echo "📋 已配置的 Secrets:"
gh secret list

echo ""
echo "🎉 现在可以推送代码触发 GitHub Actions 了！"
