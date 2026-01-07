# Flutter手动设置步骤

由于Flutter不在PATH中，请按照以下步骤手动设置：

## 步骤1: 找到Flutter安装位置

在终端运行：
```bash
# 查找Flutter
find ~ -name "flutter" -type d 2>/dev/null | grep "bin/flutter" | head -1

# 或者查看常见位置
ls -la ~/flutter/bin/flutter
ls -la ~/development/flutter/bin/flutter
```

## 步骤2: 添加Flutter到PATH (临时)

假设Flutter在 `~/flutter`，在当前终端运行：
```bash
export PATH="$HOME/flutter/bin:$PATH"

# 验证
flutter --version
```

## 步骤3: 添加到PATH (永久)

编辑 `~/.zshrc` 或 `~/.bash_profile`:
```bash
echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 步骤4: 手动设置项目

已更新pubspec.yaml修复了依赖问题。现在手动运行：

```bash
# 进入项目目录
cd /Users/80392083/develop/ee_app_claude/ai_agent_app

# 复制更新后的pubspec.yaml
cp ../flutter_config/pubspec.yaml ./pubspec.yaml

# 安装依赖
flutter pub get

# 运行项目
flutter run
```

## 修复的问题

✅ 已移除不存在的 `eventsource_client` 包
✅ 改用标准的 `http` 包处理SSE

## 如果还有问题

1. **Flutter未安装**:
   访问 https://docs.flutter.dev/get-started/install/macos 安装

2. **依赖错误**:
   ```bash
   flutter clean
   flutter pub get
   ```

3. **需要帮助**:
   运行 `flutter doctor` 检查环境

---

完成这些步骤后，运行 `flutter run` 应该能看到登录页面！
