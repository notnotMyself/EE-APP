# GitHub Secrets 配置指南

## 必需的 Secrets

为了使 APK 自动上传功能正常工作，需要在 GitHub 仓库中配置以下 Secrets:

### 1. SUPABASE_URL
- **说明**: Supabase 项目 URL
- **获取方式**:
  - 登录 Supabase Dashboard
  - 进入项目设置 (Settings) → API
  - 复制 "Project URL"
- **示例**: `https://dwesyojvzbltqtgtctpt.supabase.co`

### 2. SUPABASE_SERVICE_KEY
- **说明**: Supabase Service Role Key (具有管理员权限)
- **获取方式**:
  - 登录 Supabase Dashboard
  - 进入项目设置 (Settings) → API
  - 复制 "service_role" secret key (⚠️ 不要复制 anon public key)
- **重要**: 这个 key 拥有完整权限，务必保密

## 配置步骤

1. 进入 GitHub 仓库页面
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 分别添加上述两个 secrets

## 工作流程

配置完成后，每次推送到 main 分支或手动触发 workflow 时:

1. ✅ 自动编译 APK
2. ✅ 上传到 Supabase Storage (`apk-releases/app-release-v{version_code}.apk`)
3. ✅ 更新数据库 `app_versions` 表
4. ✅ 旧版本自动设置为非激活状态
5. ✅ 用户打开 APP 时自动检查更新

## 更改存储位置

如果将来需要更换 APK 存储位置（如切换到其他 CDN）:

1. 修改 `scripts/upload_apk.py` 中的上传逻辑
2. 或者直接在 Supabase 数据库中更新 `apk_url` 字段
3. **无需重新编译 APP** - APP 通过 API 动态获取下载地址

## 故障排除

### APK 上传失败
- 检查 Secrets 是否正确配置
- 检查 Supabase Storage bucket `apk-releases` 是否存在
- 检查 Service Role Key 是否有 Storage 写入权限

### 版本号重复
- 数据库中 `version_code` 必须唯一
- 确保每次发布前更新 `build.gradle` 中的 `versionCode`

### 用户收不到更新提示
- 检查 `app_versions` 表中 `is_active` 是否为 true
- 检查用户当前版本号是否低于 `version_code`
- 检查后端 API `/api/v1/app/version/latest` 是否正常
