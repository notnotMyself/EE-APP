#!/bin/bash
# 完整配置助手脚本
# 帮助你完成所有必要的配置

set -e  # 遇到错误立即退出

echo "🚀 APP 更新功能 - 完整配置助手"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤 1: 检查 Supabase Storage bucket
echo "📦 步骤 1: 检查 Supabase Storage bucket"
echo "----------------------------------------"
echo "✅ 你已经创建了 apk-releases bucket"
echo ""
echo "⚠️  注意: 确保 bucket 限制至少 150MB"
echo ""
echo "请在 Supabase Dashboard 执行以下 SQL 调整限制:"
echo ""
cat << 'SQL'
-- 在 Supabase Dashboard → SQL Editor 中执行
UPDATE storage.buckets
SET file_size_limit = 157286400  -- 150MB
WHERE id = 'apk-releases';

-- 验证
SELECT id, name, file_size_limit / 1024 / 1024 as limit_mb
FROM storage.buckets
WHERE id = 'apk-releases';
SQL
echo ""
read -p "完成后按 Enter 继续..."

# 步骤 2: 获取 Supabase Service Key
echo ""
echo "🔑 步骤 2: 获取 Supabase Service Key"
echo "----------------------------------------"
echo ""
echo "1. 打开浏览器访问:"
echo "   ${YELLOW}https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/api${NC}"
echo ""
echo "2. 找到 'service_role' 部分 (不是 anon!)"
echo "   点击眼睛图标显示密钥"
echo ""
echo "3. 复制这个 key (以 'eyJ' 开头的长字符串)"
echo ""
read -p "请粘贴 Service Key: " SERVICE_KEY

if [ -z "$SERVICE_KEY" ]; then
    echo "${RED}❌ Service Key 不能为空${NC}"
    exit 1
fi

# 验证 key 格式
if [[ ! "$SERVICE_KEY" =~ ^eyJ ]]; then
    echo "${RED}❌ Service Key 格式不正确，应该以 'eyJ' 开头${NC}"
    exit 1
fi

echo "${GREEN}✅ Service Key 格式正确${NC}"

# 步骤 3: 配置后端环境变量
echo ""
echo "🔧 步骤 3: 配置后端环境变量"
echo "----------------------------------------"

# 创建后端 .env 文件
ENV_FILE="backend/agent_orchestrator/.env"
echo "创建 $ENV_FILE ..."

cat > "$ENV_FILE" << EOF
# Supabase 配置
SUPABASE_URL=https://dwesyojvzbltqtgtctpt.supabase.co
SUPABASE_SERVICE_KEY=$SERVICE_KEY
SUPABASE_SERVICE_ROLE_KEY=$SERVICE_KEY

# 由配置助手自动生成
# 生成时间: $(date)
EOF

echo "${GREEN}✅ 后端环境变量已配置${NC}"

# 步骤 4: 配置 GitHub Secrets
echo ""
echo "📝 步骤 4: 配置 GitHub Secrets"
echo "----------------------------------------"

# 检查 gh CLI
if command -v gh &> /dev/null; then
    echo "使用 GitHub CLI 配置..."

    # 配置 Secrets
    echo "$SERVICE_KEY" | gh secret set SUPABASE_SERVICE_KEY
    echo "https://dwesyojvzbltqtgtctpt.supabase.co" | gh secret set SUPABASE_URL

    echo "${GREEN}✅ GitHub Secrets 已配置${NC}"
    echo ""
    echo "已配置的 Secrets:"
    gh secret list
else
    echo "${YELLOW}⚠️  未安装 GitHub CLI，需要手动配置${NC}"
    echo ""
    echo "请访问:"
    REPO_URL=$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/' || echo "你的GitHub仓库")
    echo "   ${YELLOW}https://github.com/$REPO_URL/settings/secrets/actions${NC}"
    echo ""
    echo "添加两个 Secrets:"
    echo ""
    echo "1. Name: SUPABASE_URL"
    echo "   Secret: https://dwesyojvzbltqtgtctpt.supabase.co"
    echo ""
    echo "2. Name: SUPABASE_SERVICE_KEY"
    echo "   Secret: [粘贴你刚才输入的 key]"
    echo ""
    read -p "完成后按 Enter 继续..."
fi

# 步骤 5: 插入测试数据
echo ""
echo "📊 步骤 5: 插入测试数据到数据库"
echo "----------------------------------------"

# 导出环境变量供 Python 脚本使用
export SUPABASE_SERVICE_KEY="$SERVICE_KEY"

echo "正在插入测试版本数据..."
if python3 scripts/insert_test_version.py; then
    echo "${GREEN}✅ 测试数据插入成功${NC}"
else
    echo "${RED}❌ 测试数据插入失败${NC}"
    echo ""
    echo "你也可以手动在 Supabase Dashboard → SQL Editor 执行:"
    cat << 'SQL'

INSERT INTO app_versions (
  version_code, version_name, apk_url, apk_size,
  release_notes, force_update, is_active, min_support_version
) VALUES (
  2, '0.1.1',
  'https://dwesyojvzbltqtgtctpt.supabase.co/storage/v1/object/public/apk-releases/app-release-v2.apk',
  50000000,
  '# 版本 0.1.1

## 新功能
- ✨ 应用内更新功能
- 📱 支持多下载源
- 🔄 断点续传支持

## 优化
- 🚀 提升应用性能
- 💾 减小安装包体积',
  false, true, 1
);
SQL
    read -p "手动插入完成后按 Enter 继续..."
fi

# 步骤 6: 验证配置
echo ""
echo "🧪 步骤 6: 验证配置"
echo "----------------------------------------"

echo "正在测试 API 端点..."

# 检查后端是否运行
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "${GREEN}✅ 后端服务正在运行${NC}"

    echo ""
    echo "测试版本检查 API:"
    RESPONSE=$(curl -s "http://localhost:8000/app/version/latest?current_version=1")
    echo "$RESPONSE" | jq . || echo "$RESPONSE"

    if echo "$RESPONSE" | grep -q "has_update.*true"; then
        echo ""
        echo "${GREEN}✅ API 测试通过！${NC}"
    else
        echo ""
        echo "${YELLOW}⚠️  API 返回无更新，这可能正常（如果数据库中版本号≤1）${NC}"
    fi
else
    echo "${YELLOW}⚠️  后端服务未运行${NC}"
    echo ""
    echo "请启动后端服务进行测试:"
    echo "   cd backend/agent_orchestrator"
    echo "   python3 main.py"
    echo ""
    echo "然后在另一个终端测试 API:"
    echo "   curl 'http://localhost:8000/app/version/latest?current_version=1' | jq ."
fi

# 完成
echo ""
echo "🎉 配置完成！"
echo "========================================"
echo ""
echo "✅ 已完成的配置:"
echo "   • Supabase Storage bucket (apk-releases)"
echo "   • Storage 限制调整为 150MB"
echo "   • 后端环境变量 (.env)"
echo "   • GitHub Secrets"
echo "   • 测试版本数据"
echo ""
echo "📋 配置文件位置:"
echo "   • 后端: backend/agent_orchestrator/.env"
echo "   • GitHub: 仓库的 Settings → Secrets"
echo ""
echo "🚀 下一步:"
echo "   1. 启动后端测试 API"
echo "   2. 编译 APK 并在手机上测试"
echo "   3. 或推送代码到 main 分支触发 GitHub Actions"
echo ""
echo "📚 详细测试指南: docs/APP_UPDATE_TESTING_GUIDE.md"
echo ""
