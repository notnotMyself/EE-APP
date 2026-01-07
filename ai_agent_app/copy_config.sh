#!/bin/bash
# 手动复制配置文件的快速脚本

echo "📦 复制Flutter配置文件..."
cd /Users/80392083/develop/ee_app_claude/ai_agent_app

# 复制pubspec.yaml
echo "   复制 pubspec.yaml..."
cp ../flutter_config/pubspec.yaml ./pubspec.yaml

# 复制lib目录
echo "   复制 lib/ 目录..."
rm -rf lib
cp -r ../flutter_config/lib ./lib

echo "✅ 配置文件复制完成！"
echo ""
echo "下一步："
echo "1. 运行: flutter pub get"
echo "2. 运行: flutter run"
