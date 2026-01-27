#!/bin/bash
# 测试应用更新通知流程

echo "=== 测试更新通知流程 ==="

# 1. 检查后端是否运行
echo "1. 检查后端服务..."
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 后端服务运行中"
else
    echo "❌ 后端服务未运行，请先启动: cd backend/agent_orchestrator && python3 main.py"
    exit 1
fi

# 2. 模拟 APP 检查更新（当前版本号为 1）
echo ""
echo "2. 模拟 APP 检查更新 (current_version=1)..."
response=$(curl -s "http://localhost:8000/api/v1/app/version/latest?current_version=1&region=cn")
echo "$response" | python3 -m json.tool

# 3. 解析结果
has_update=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('has_update', False))")

echo ""
if [ "$has_update" = "True" ]; then
    echo "✅ 触发更新通知！"
    echo "最新版本信息:"
    echo "$response" | python3 -c "import sys, json; v = json.load(sys.stdin).get('latest_version', {}); print(f\"  version_code: {v.get('version_code')}\n  version_name: {v.get('version_name')}\n  apk_url: {v.get('apk_url')}\")"
else
    echo "❌ 未触发更新通知"
    echo "可能原因:"
    echo "  - Supabase 中的 version_code 不大于 1"
    echo "  - is_active 未设置为 true"
fi

echo ""
echo "=== 测试完成 ==="
