# 应用更新检查调试指南

## 问题描述

安装新的 APK 后，没有出现更新弹窗。

## 已验证的信息

✅ **后端 API 正常工作**
- 本地: `http://localhost:8000/api/v1/app/version/latest`
- 生产: `https://super-niuma-cn.allawntech.com/api/v1/app/version/latest`
- 都能正确返回版本信息

✅ **数据库版本配置正确**
- version_code: 2
- version_name: 0.1.1
- is_active: true

✅ **pubspec.yaml 版本**
- version: 0.1.0+1
- buildNumber: 1

✅ **更新检查代码已添加到 FeedHomePage.initState**
- 在 `WidgetsBinding.instance.addPostFrameCallback` 中调用
- silent: true（静默检查，无更新时不提示）

## 可能的原因

### 1. 实际安装的 APK 版本号不是 1

你安装的 APK 可能是从之前的构建生成的，其 buildNumber 实际上是 2 或更高。

**检查方法**：
- 查看 GitHub Actions 构建日志中的版本号
- 或者使用 `adb shell dumpsys package ai.agent.app | grep versionCode`

### 2. 环境变量问题

App 默认连接生产环境，但如果编译时传入了不同的环境变量，可能连接到其他端点。

**检查方法**：
- 查看 GitHub Actions workflow 中的编译命令
- 是否有 `--dart-define=ENV=xxx`

### 3. 更新检查被阻止

可能的阻止条件：
- `context.mounted` 返回 false
- 检查更新时发生异常
- API 请求超时或失败

## 调试步骤

### 第一步：重新构建并安装 App

等待 GitHub Actions 完成新的构建（已包含调试日志），然后下载并安装：

```bash
# 下载最新的 APK
# https://github.com/notnotMyself/EE-APP/actions

# 安装
adb install -r app-release.apk
```

### 第二步：查看日志

安装后启动 App，使用 `adb logcat` 查看日志：

```bash
# 过滤更新相关日志
adb logcat | grep UpdateCheck
adb logcat | grep UpdateRepository
adb logcat | grep AppConfig
```

你应该看到类似这样的日志：

```
🔍 [AppConfig] Environment: prod
🔍 [UpdateCheck] Current version: 0.1.0 (code: 1)
🔍 [UpdateCheck] Checking for updates...
🔍 [UpdateRepository] Current version code: 1
🔍 [UpdateRepository] API URL: https://super-niuma-cn.allawntech.com/api/v1/app/version/latest
🔍 [UpdateRepository] API Response: {has_update: true, ...}
🔍 [UpdateRepository] Has update: true
🔍 [UpdateCheck] Check status: UpdateCheckStatus.hasUpdate
🔍 [UpdateCheck] Has update! Latest: 0.1.1 (code: 2)
🔍 [UpdateCheck] Showing update dialog (force: false)
```

### 第三步：根据日志诊断问题

#### 情况 1：Current version code 不是 1

**日志显示**：
```
🔍 [UpdateCheck] Current version: 0.1.1 (code: 2)
```

**原因**：安装的 APK 版本号已经是 2，所以没有更新

**解决**：需要更新数据库中的版本号到 3：

```sql
INSERT INTO app_versions (
  version_code, version_name, apk_url, apk_size,
  release_notes, force_update, is_active, published_at
) VALUES (
  3, '0.1.2',
  'https://github.com/notnotMyself/EE-APP/releases/download/v0.1.2/app-release.apk',
  50000000,
  '# 版本 0.1.2\n\n- 测试更新功能',
  false, true, NOW()
);
```

#### 情况 2：API 请求失败

**日志显示**：
```
❌ [UpdateRepository] Check update failed: ...
❌ [UpdateCheck] Exception: ...
```

**原因**：网络问题或 API 不可达

**解决**：
- 检查设备网络连接
- 检查生产环境后端是否正常运行
- 使用浏览器访问 API 确认可达性

#### 情况 3：Context not mounted

**日志显示**：
```
⚠️ [UpdateCheck] Cannot show dialog: version=true, mounted=false
```

**原因**：更新检查完成时页面已经销毁

**解决**：调整检查时机或增加延迟

#### 情况 4：环境不是 prod

**日志显示**：
```
🔍 [AppConfig] Environment: dev
```

**原因**：编译时使用了错误的环境变量

**解决**：检查 GitHub Actions workflow，确保生产构建没有设置 ENV 变量

## 快速测试脚本

运行测试脚本验证后端：

```bash
./test_update_debug.sh
```

## 手动触发更新检查

如果自动检查失败，可以在 App 中添加手动触发按钮（例如在设置页面）：

```dart
ElevatedButton(
  onPressed: () {
    AppUpdateService.checkUpdateManually(context, ref);
  },
  child: Text('检查更新'),
)
```

## 临时解决方案：强制更新

如果需要强制所有用户更新，可以在数据库中设置：

```sql
UPDATE app_versions
SET force_update = true
WHERE version_code = 2;
```

或者设置最低支持版本：

```sql
UPDATE app_versions
SET min_support_version = 2
WHERE version_code = 2;
```

这样 version_code < 2 的用户会被强制更新。

## 相关文件

- 更新检查服务: `ai_agent_app/lib/features/app_update/services/app_update_service.dart`
- 更新仓库: `ai_agent_app/lib/features/app_update/data/repositories/update_repository.dart`
- 环境配置: `ai_agent_app/lib/core/config/app_config.dart`
- 后端 API: `backend/agent_orchestrator/api/app_version.py`
- 数据库迁移: `supabase/migrations/20260124000000_create_app_versions.sql`

## 下一步

1. 等待新的 APK 构建完成
2. 安装新 APK
3. 使用 `adb logcat` 查看日志
4. 根据日志内容确定问题原因
5. 如有需要，提供日志反馈
