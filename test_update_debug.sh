#!/bin/bash

echo "========== 更新检查调试 =========="
echo ""

echo "1. 检查生产环境 API"
echo "URL: https://super-niuma-cn.allawntech.com/api/v1/app/version/latest?current_version=1"
curl -s "https://super-niuma-cn.allawntech.com/api/v1/app/version/latest?current_version=1" | jq .
echo ""

echo "2. 检查本地 API"
echo "URL: http://localhost:8000/api/v1/app/version/latest?current_version=1"
curl -s "http://localhost:8000/api/v1/app/version/latest?current_version=1" | jq .
echo ""

echo "3. 检查 pubspec.yaml 中的版本"
echo "当前版本:"
grep "^version:" ai_agent_app/pubspec.yaml
echo ""

echo "4. 检查数据库中的版本记录"
echo "使用 Supabase REST API:"
SUPABASE_URL="https://dwesyojvzbltqtgtctpt.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MzA5MTQsImV4cCI6MjA4MjUwNjkxNH0.t4TBNkYp99HWBFu5kBOAgH13_7O5UADAMAptR16ENqc"

curl -s "${SUPABASE_URL}/rest/v1/app_versions?select=version_code,version_name,is_active&order=version_code.desc" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_KEY}" | jq .

echo ""
echo "========== 调试完成 =========="
echo ""
echo "如果 API 返回 has_update=true，但 App 没有弹窗，可能原因："
echo "1. App 连接的不是生产环境 API（检查编译时环境变量）"
echo "2. App 的 buildNumber 不是 1（检查实际安装的 APK）"
echo "3. 更新检查没有在启动时触发（检查 FeedHomePage.initState）"
echo "4. 弹窗被某些条件阻止（检查 context.mounted 等条件）"
echo ""
echo "调试建议："
echo "- 在 Flutter app 中添加日志：print('Current version: \$versionCode')"
echo "- 在 AppUpdateService.checkUpdateOnStartup 中添加日志"
echo "- 使用 Flutter DevTools 查看网络请求"
