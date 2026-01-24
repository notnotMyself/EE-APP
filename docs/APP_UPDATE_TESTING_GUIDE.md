# APP 更新功能测试指南

## 测试状态

✅ 已完成:
- [x] 数据库表创建 (`app_versions`)
- [x] 后端 API 实现 (`/app/version/latest`)
- [x] Flutter 代码实现 (models, repositories, controllers, UI)
- [x] GitHub Actions 自动上传脚本
- [x] Code generation (freezed models)
- [x] 代码静态分析通过

⏳ 待完成:
- [ ] 插入测试版本数据到数据库
- [ ] 编译测试 APK
- [ ] 端到端测试更新流程

## 前置准备

### 1. 配置 GitHub Secrets

在 GitHub 仓库中配置以下 Secrets (参考 `.github/SECRETS_SETUP.md`):

- `SUPABASE_URL`: https://dwesyojvzbltqtgtctpt.supabase.co
- `SUPABASE_SERVICE_KEY`: 从 Supabase Dashboard → Settings → API → service_role key

### 2. 插入测试版本数据

#### 方法 A: 使用 Supabase Dashboard SQL Editor

```sql
-- 1. 停用旧版本
UPDATE app_versions SET is_active = false;

-- 2. 插入测试版本 v0.1.1 (version_code=2)
INSERT INTO app_versions (
  version_code,
  version_name,
  apk_url,
  apk_size,
  apk_md5,
  release_notes,
  force_update,
  is_active,
  min_support_version
) VALUES (
  2,
  '0.1.1',
  'https://dwesyojvzbltqtgtctpt.supabase.co/storage/v1/object/public/apk-releases/app-release-v2.apk',
  50000000,
  'test_md5_hash',
  E'# 版本 0.1.1\n\n## 新功能\n- ✨ 应用内更新功能\n- 📱 支持多下载源\n- 🔄 断点续传支持\n\n## 优化\n- 🚀 提升应用性能\n- 💾 减小安装包体积',
  false,
  true,
  1
);
```

#### 方法 B: 使用 Python 脚本

```bash
# 设置环境变量
export SUPABASE_SERVICE_KEY="your_service_role_key_here"

# 运行脚本
python3 scripts/insert_test_version.py
```

### 3. 验证 API 响应

```bash
# 测试版本检查 API
curl "http://localhost:8000/app/version/latest?current_version=1&region=cn" | jq .

# 期望输出:
{
  "has_update": true,
  "latest_version": {
    "version_code": 2,
    "version_name": "0.1.1",
    "apk_url": "https://...",
    "apk_size": 50000000,
    ...
  },
  "message": "..."
}
```

## 测试步骤

### 阶段 1: 本地编译测试 (版本 0.1.0)

1. **确保当前版本号为 1**

   编辑 `ai_agent_app/android/app/build.gradle`:
   ```gradle
   defaultConfig {
       versionCode = 1
       versionName = "0.1.0"
   }
   ```

2. **编译 APK**

   ```bash
   cd ai_agent_app
   flutter clean
   flutter pub get
   dart run build_runner build --delete-conflicting-outputs
   flutter build apk --release
   ```

3. **安装到手机**

   ```bash
   adb install ai_agent_app/build/app/outputs/flutter-apk/app-release.apk
   ```

4. **验证版本号**

   打开 APP → 设置 → 关于，确认显示版本 0.1.0 (1)

### 阶段 2: 编译新版本 (版本 0.1.1)

1. **升级版本号**

   编辑 `ai_agent_app/android/app/build.gradle`:
   ```gradle
   defaultConfig {
       versionCode = 2
       versionName = "0.1.1"
   }
   ```

2. **编译新版本 APK**

   ```bash
   cd ai_agent_app
   flutter build apk --release
   ```

3. **上传到 Supabase Storage**

   ```bash
   python3 scripts/upload_apk.py ai_agent_app/build/app/outputs/flutter-apk/app-release.apk
   ```

   或手动上传到 Supabase Dashboard → Storage → apk-releases

### 阶段 3: 端到端更新测试

#### 测试场景 1: 启动时自动检查更新

1. 确保手机安装了 v0.1.0 (version_code=1)
2. 确保手机可以访问后端 (使用 adb reverse 或配置 IP)
   ```bash
   adb reverse tcp:8000 tcp:8000
   ```
3. 打开 APP
4. **预期结果**:
   - 显示更新弹窗
   - 显示版本号 "v0.1.1"
   - 显示更新内容
   - 显示文件大小

#### 测试场景 2: 下载更新

1. 在更新弹窗中点击"立即更新"
2. **预期结果**:
   - 显示下载进度条
   - 显示下载百分比
   - 显示已下载/总大小

#### 测试场景 3: 取消下载

1. 开始下载后点击"取消"
2. **预期结果**:
   - 下载停止
   - 弹窗关闭(非强制更新)或重新显示更新按钮(强制更新)

#### 测试场景 4: 安装更新

1. 下载完成后
2. **预期结果**:
   - 自动弹出系统安装界面
   - 安装完成后版本更新为 0.1.1

#### 测试场景 5: 强制更新

1. 在数据库中将 `force_update` 改为 true
   ```sql
   UPDATE app_versions SET force_update = true WHERE version_code = 2;
   ```
2. 重启 APP
3. **预期结果**:
   - 更新弹窗无法关闭
   - 不显示"稍后更新"按钮
   - 必须更新才能使用

#### 测试场景 6: 手动检查更新

1. 进入设置页面
2. 点击"检查更新"
3. **预期结果**:
   - 显示"正在检查更新..."提示
   - 如有更新则显示更新弹窗
   - 如无更新则显示"已是最新版本"

#### 测试场景 7: 多下载源切换

1. 在数据库中配置多个下载源
   ```sql
   UPDATE app_versions
   SET apk_mirror_urls = jsonb_build_array(
     jsonb_build_object('name', 'GitHub CDN', 'url', 'https://...', 'speed', 'fast'),
     jsonb_build_object('name', '备用源', 'url', 'https://...', 'speed', 'medium')
   )
   WHERE version_code = 2;
   ```
2. 模拟主源下载失败
3. **预期结果**:
   - 显示错误信息
   - 显示"选择其他下载源"按钮
   - 可以选择备用源重新下载

## 验收标准

### 功能验收

- ✅ APP 能正确检测新版本
- ✅ 下载进度实时更新
- ✅ 可以取消下载
- ✅ 下载完成后自动弹出安装界面
- ✅ 强制更新模式下无法跳过
- ✅ 无更新时正确提示
- ✅ 错误情况有友好提示

### 性能验收

- ✅ 检查更新响应时间 < 2秒
- ✅ 下载速度正常(取决于网络和存储)
- ✅ 不阻塞 UI 线程

### 安全验收

- ✅ 使用 HTTPS 下载
- ✅ MD5 校验(如果配置)
- ✅ 不暴露敏感信息

## 自动化测试(未来)

```dart
// 单元测试
test('UpdateRepository.checkUpdate returns correct response', () async {
  final repository = UpdateRepository();
  final response = await repository.checkUpdate();
  expect(response.hasUpdate, isTrue);
});

// Widget 测试
testWidgets('UpdateDialog shows correct information', (tester) async {
  // ...
});
```

## 故障排除

### 问题: API 返回 404

**原因**: 后端未启动或路由未注册

**解决**:
```bash
cd backend/agent_orchestrator
python3 main.py
```

### 问题: 下载失败

**原因**: APK URL 不正确或 Storage 权限问题

**解决**:
1. 检查 Supabase Storage → apk-releases bucket 是否为 public
2. 检查 RLS 策略是否允许匿名读取

### 问题: 安装失败

**原因**: 签名不一致

**解决**:
1. 确保使用相同的 keystore 签名
2. 或先卸载旧版本再安装

### 问题: 无法连接后端

**原因**: 手机和电脑不在同一网络

**解决**:
```bash
# 使用 adb reverse
adb reverse tcp:8000 tcp:8000

# 或配置实际 IP
# 编辑 ai_agent_app/lib/core/config/app_config.dart
```

## GitHub Actions 自动化

推送到 main 分支后:

1. GitHub Actions 自动编译 APK
2. 自动上传到 Supabase Storage
3. 自动更新数据库版本信息
4. 用户打开 APP 时自动检测更新

## 下一步优化

- [ ] 增量更新(差分包)
- [ ] 后台静默下载
- [ ] 灰度发布
- [ ] 版本回滚
- [ ] 更新统计分析
