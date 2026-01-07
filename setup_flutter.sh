#!/bin/bash
# Flutter项目快速设置脚本

set -e  # 遇到错误立即退出

# 检测并设置Flutter路径
if ! command -v flutter &> /dev/null; then
    # Flutter不在PATH中，尝试常见安装位置
    FLUTTER_PATHS=(
        "$HOME/flutter/bin"
        "$HOME/development/flutter/bin"
        "/usr/local/flutter/bin"
    )
    
    FLUTTER_FOUND=false
    for path in "${FLUTTER_PATHS[@]}"; do
        if [ -f "$path/flutter" ]; then
            export PATH="$path:$PATH"
            FLUTTER_FOUND=true
            echo "✅ 找到Flutter: $path"
            break
        fi
    done
    
    if [ "$FLUTTER_FOUND" = false ]; then
        echo "❌ 错误: 未找到Flutter命令"
        echo ""
        echo "请执行以下操作之一:"
        echo "1. 安装Flutter: https://docs.flutter.dev/get-started/install"
        echo "2. 或将Flutter添加到PATH:"
        echo "   export PATH=\"\$HOME/flutter/bin:\$PATH\""
        echo "   并添加到 ~/.zshrc 或 ~/.bash_profile"
        exit 1
    fi
fi

echo "🚀 开始设置Flutter项目..."
echo ""

# 切换到项目目录
cd /Users/80392083/develop/ee_app_claude

# 步骤1: 创建Flutter项目
echo "📱 步骤1: 创建Flutter项目..."
if [ -d "ai_agent_app" ]; then
    echo "⚠️  ai_agent_app目录已存在，跳过创建"
else
    flutter create ai_agent_app --org com.oppo.ee --platforms ios,android
fi
echo "✅ Flutter项目创建完成"
echo ""

# 步骤2: 替换配置文件
echo "📦 步骤2: 替换配置文件..."
cd ai_agent_app

# 备份原始文件
if [ -f "pubspec.yaml.bak" ]; then
    echo "   备份已存在，跳过"
else
    cp pubspec.yaml pubspec.yaml.bak
    cp -r lib lib.bak
fi

# 替换配置
cp ../flutter_config/pubspec.yaml ./pubspec.yaml
rm -rf lib
cp -r ../flutter_config/lib ./lib

echo "✅ 配置文件替换完成"
echo ""

# 步骤3: 安装依赖
echo "📥 步骤3: 安装Flutter依赖..."
flutter pub get
echo "✅ 依赖安装完成"
echo ""

# 完成
echo "🎉 Flutter项目设置完成！"
echo ""
echo "📂 项目路径: /Users/80392083/develop/ee_app_claude/ai_agent_app"
echo ""
echo "▶️  运行项目:"
echo "   cd /Users/80392083/develop/ee_app_claude/ai_agent_app"
echo "   flutter run"
echo ""
echo "📖 详细文档: /Users/80392083/develop/ee_app_claude/FLUTTER_SETUP.md"
