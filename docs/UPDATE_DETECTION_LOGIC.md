# 📱 APP 升级检测逻辑详解

## 🔍 核心判断逻辑

### 简单来说

**判断依据**: `数据库最新版本号 > APP当前版本号`

```
如果 latest_version_code > current_version_code
→ 有更新，显示更新弹窗

否则
→ 无更新，不显示（或提示"已是最新版本"）
```

---

## 📊 完整检测流程

### 1. 前端触发检查

#### 触发时机 A: 应用启动时（自动检查）

```dart
// 在 main.dart 或首页 initState() 中
Future.delayed(Duration(seconds: 2), () {
  AppUpdateService.checkUpdateOnStartup(
    context,
    ref,
    silent: true  // 静默检查，无更新时不提示
  );
});
```

**特点**:
- 延迟 2 秒检查（避免影响启动速度）
- `silent: true` 表示无更新时不提示用户
- 有更新时自动弹窗

#### 触发时机 B: 手动检查（设置页面）

```dart
// 用户点击"检查更新"按钮
AppUpdateService.checkUpdateManually(context, ref);
```

**特点**:
- `silent: false` 会显示"正在检查更新..."
- 无更新时也会提示"已是最新版本"

---

### 2. 获取当前版本号

```dart
// Flutter 端
Future<int> getCurrentVersionCode() async {
  final packageInfo = await PackageInfo.fromPlatform();
  return int.tryParse(packageInfo.buildNumber) ?? 1;
}
```

**来源**: 从 `android/app/build.gradle` 读取

```gradle
defaultConfig {
    versionCode = 1  // ← 这个值
    versionName = "0.1.0"
}
```

---

### 3. 调用后端 API

```
GET /app/version/latest?current_version=1&region=cn
```

**请求参数**:
- `current_version`: 当前 APP 的版本号 (如 1)
- `region`: 地区代码 (cn/us/global)，用于选择下载源

---

### 4. 后端判断逻辑

```python
# backend/agent_orchestrator/api/app_version.py

# 1. 查询数据库：最新的激活版本
response = supabase.table("app_versions")
    .select("*")
    .eq("is_active", True)       # 只查激活的版本
    .order("version_code", desc=True)  # 按版本号倒序
    .limit(1)                     # 只取最新的一条
    .execute()

latest_version_code = response.data[0]["version_code"]

# 2. 版本比较
has_update = latest_version_code > current_version

# 3. 返回结果
if has_update:
    return {
        "has_update": True,
        "latest_version": {...},  # 包含 APK URL、大小、更新说明等
        "message": "发现新版本 0.1.1"
    }
else:
    return {
        "has_update": False,
        "latest_version": None,
        "message": "已是最新版本"
    }
```

---

### 5. 前端处理响应

```dart
// UpdateController
await controller.checkUpdate();

final state = ref.read(updateControllerProvider);

if (state.checkStatus == UpdateCheckStatus.hasUpdate) {
  final version = state.updateResponse?.latestVersion;

  // 显示更新对话框
  await showUpdateDialog(
    context,
    force: version.forceUpdate,  // 是否强制更新
  );
}
```

---

## 🎯 关键判断规则

### 规则 1: 版本号必须递增

```
当前版本: 1 → 有更新: 版本 2, 3, 4...
当前版本: 2 → 有更新: 版本 3, 4, 5...
当前版本: 5 → 没有更新（数据库最新也是 5）
```

### 规则 2: 只检查激活的版本

数据库中可能有多个版本记录，但**只有 `is_active = true` 的版本**会被检测到。

```sql
-- 示例数据
version_code | version_name | is_active
-------------|--------------|----------
1            | 0.1.0        | false     ← 旧版本，停用
2            | 0.1.1        | true      ← 当前激活，会被检测
3            | 0.1.2-beta   | false     ← 测试版，不对外
```

### 规则 3: 取最大的版本号

如果有多个激活版本（不推荐），会取 `version_code` 最大的那个。

---

## 🔢 版本号设计建议

### Android 版本号体系

```gradle
defaultConfig {
    versionCode = 1      // 版本号（整数，递增）
    versionName = "0.1.0"  // 版本名称（给用户看）
}
```

**推荐规则**:

| versionCode | versionName | 说明 |
|-------------|-------------|------|
| 1 | 0.1.0 | 初始版本 |
| 2 | 0.1.1 | Bug 修复 |
| 3 | 0.2.0 | 小版本更新 |
| 10 | 1.0.0 | 正式版 |
| 11 | 1.0.1 | 正式版 Patch |
| 20 | 2.0.0 | 大版本更新 |

**关键**:
- `versionCode` 用于程序判断，必须递增
- `versionName` 给用户看，可以语义化

---

## 💡 检测逻辑示例

### 场景 1: 用户首次打开 APP

```
1. APP 启动，延迟 2 秒
2. 读取本地 versionCode = 1
3. 调用 API: /app/version/latest?current_version=1
4. 后端查询数据库，最新版本 = 2
5. 判断: 2 > 1 → 有更新
6. 返回: has_update = true
7. 前端显示更新弹窗
```

### 场景 2: 用户已是最新版本

```
1. APP 启动，延迟 2 秒
2. 读取本地 versionCode = 2
3. 调用 API: /app/version/latest?current_version=2
4. 后端查询数据库，最新版本 = 2
5. 判断: 2 = 2 → 无更新
6. 返回: has_update = false
7. 前端不显示弹窗（silent 模式）
```

### 场景 3: 手动检查更新（无更新）

```
1. 用户点击"检查更新"
2. 读取本地 versionCode = 2
3. 调用 API: /app/version/latest?current_version=2
4. 后端判断: 2 = 2 → 无更新
5. 返回: has_update = false, message = "已是最新版本"
6. 前端显示 SnackBar: "已是最新版本"
```

### 场景 4: 跨版本更新

```
1. 用户安装了很久没更新的 APP (versionCode = 1)
2. 数据库中已经有版本 2, 3, 4
3. 调用 API: /app/version/latest?current_version=1
4. 后端返回最新版本 4（不是 2 或 3）
5. 用户直接从版本 1 更新到版本 4（跳过 2 和 3）
```

---

## 🛡️ 强制更新逻辑

### 数据库配置

```sql
UPDATE app_versions
SET force_update = true
WHERE version_code = 2;
```

### 前端行为

```dart
await showUpdateDialog(
  context,
  force: version.forceUpdate,  // true
);
```

**效果**:
- ✅ 弹窗无法关闭（无 X 按钮）
- ✅ 没有"稍后更新"按钮
- ✅ 用户必须更新才能继续使用

**使用场景**:
- 重大安全漏洞修复
- API 不兼容，必须升级
- 强制合规要求

---

## 📈 最低支持版本

### 数据库配置

```sql
INSERT INTO app_versions (
  version_code,
  min_support_version,  -- 最低支持版本
  ...
) VALUES (
  5,
  3,  -- 版本 5 最低支持从版本 3 升级
  ...
);
```

### 检测逻辑（可扩展）

```python
# 目前未实现，可以增强为：
if current_version < latest.min_support_version:
    return {
        "has_update": True,
        "force_update": True,  # 强制更新
        "message": "您的版本过低，必须更新"
    }
```

---

## 🔄 更新检查频率

### 当前实现

- **启动检查**: 每次 APP 启动时检查一次
- **手动检查**: 用户主动触发

### 可扩展方案

```dart
// 每天检查一次
SharedPreferences prefs = await SharedPreferences.getInstance();
int lastCheckTime = prefs.getInt('last_update_check') ?? 0;
int currentTime = DateTime.now().millisecondsSinceEpoch;

if (currentTime - lastCheckTime > 24 * 60 * 60 * 1000) {
  // 超过 24 小时，检查更新
  await checkUpdateOnStartup(...);
  prefs.setInt('last_update_check', currentTime);
}
```

---

## 🎨 自定义检测逻辑

### 按地区推送不同版本

```python
# 后端可以根据 region 参数返回不同版本
if region == "cn":
    # 中国大陆版本
    response = supabase.table("app_versions")
        .eq("region", "cn")
        ...
elif region == "us":
    # 国际版本
    response = supabase.table("app_versions")
        .eq("region", "global")
        ...
```

### 灰度发布（未实现）

```python
# 可以增加字段：release_percentage (发布比例 0-100)
# 根据用户 ID 计算哈希，决定是否显示更新

user_hash = hash(user_id) % 100
if user_hash < latest.release_percentage:
    # 该用户在灰度范围内，显示更新
    return {...}
```

---

## 📝 总结

### 核心逻辑

```
检测条件: 数据库最新激活版本号 > APP 当前版本号
判断方式: 纯数字比较
触发时机: 启动时自动 + 手动触发
```

### 关键字段

- `version_code`: 版本号（整数，用于比较）
- `is_active`: 是否激活（只检测激活的版本）
- `force_update`: 是否强制更新
- `min_support_version`: 最低支持版本（可扩展）

### 优势

✅ **逻辑简单**: 只比较数字，不会出错
✅ **完全后台控制**: 随时可以发布/停用版本
✅ **支持跨版本**: 直接升级到最新版
✅ **灵活扩展**: 可以加灰度、地区等逻辑

---

**文档位置**: `docs/UPDATE_DETECTION_LOGIC.md`
