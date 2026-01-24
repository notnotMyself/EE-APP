# 🚀 快速配置指南

## 当前状态

✅ **已完成**:
- Supabase Storage bucket `apk-releases` 已创建

⚠️ **需要配置** (50MB 限制需要调整):
- Storage 文件大小限制 (50MB → 150MB)
- Supabase Service Key
- GitHub Secrets
- 测试版本数据

---

## 🎯 一键配置（推荐）

我为你准备了一个**自动配置脚本**，它会帮你完成所有配置：

```bash
./scripts/setup_complete.sh
```

这个脚本会引导你完成：

1. ✅ 调整 Storage 限制为 150MB
2. ✅ 获取 Supabase Service Key
3. ✅ 配置后端环境变量
4. ✅ 配置 GitHub Secrets
5. ✅ 插入测试版本数据
6. ✅ 验证 API 是否正常

**预计时间**: 5 分钟

---

## 📝 手动配置（如果脚本失败）

### 1. 调整 Storage 限制

在 **Supabase Dashboard** 执行：

```sql
-- SQL Editor → New query
UPDATE storage.buckets
SET file_size_limit = 157286400  -- 150MB
WHERE id = 'apk-releases';
```

### 2. 获取 Service Key

1. 访问: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/api
2. 找到 **"service_role"** (不是 anon!)
3. 点击眼睛图标，复制 key

### 3. 配置 GitHub Secrets

访问: https://github.com/你的用户名/ee_app_claude/settings/secrets/actions

添加两个 Secrets:

```
Name: SUPABASE_URL
Secret: https://dwesyojvzbltqtgtctpt.supabase.co

Name: SUPABASE_SERVICE_KEY
Secret: [粘贴刚才复制的 key]
```

### 4. 配置后端环境变量

创建 `backend/agent_orchestrator/.env`:

```bash
SUPABASE_URL=https://dwesyojvzbltqtgtctpt.supabase.co
SUPABASE_SERVICE_KEY=你的_service_key
SUPABASE_SERVICE_ROLE_KEY=你的_service_key
```

### 5. 插入测试数据

```bash
export SUPABASE_SERVICE_KEY="你的_service_key"
python3 scripts/insert_test_version.py
```

或在 Supabase Dashboard → SQL Editor 执行：

```sql
INSERT INTO app_versions (
  version_code, version_name, apk_url, apk_size,
  release_notes, force_update, is_active
) VALUES (
  2, '0.1.1',
  'https://dwesyojvzbltqtgtctpt.supabase.co/storage/v1/object/public/apk-releases/app-release-v2.apk',
  50000000,
  '# 版本 0.1.1

## 新功能
- ✨ 应用内更新功能
- 📱 支持多下载源',
  false, true
);
```

### 6. 验证配置

```bash
# 启动后端
cd backend/agent_orchestrator
python3 main.py

# 在另一个终端测试
curl "http://localhost:8000/app/version/latest?current_version=1" | jq .
```

---

## ✅ 配置完成后

你可以：

### 方式 A: 立即测试（本地）

```bash
# 1. 编译 APK (确保 versionCode = 1)
cd ai_agent_app
flutter build apk --release

# 2. 安装到手机
adb install build/app/outputs/flutter-apk/app-release.apk

# 3. 配置网络
adb reverse tcp:8000 tcp:8000

# 4. 打开 APP 测试更新
```

### 方式 B: GitHub Actions 自动化

```bash
# 1. 升级版本号 (versionCode = 2)
# 编辑 ai_agent_app/android/app/build.gradle

# 2. 提交推送
git add .
git commit -m "feat: 版本 0.1.1 - 测试更新功能"
git push origin main

# 3. GitHub Actions 自动编译上传
# 4. 用户打开 APP 收到更新提示
```

---

## 🆘 遇到问题？

查看详细文档：
- 完整测试指南: `docs/APP_UPDATE_TESTING_GUIDE.md`
- 配置清单: `docs/SETUP_CHECKLIST.md`
- 实现总结: `docs/APP_UPDATE_IMPLEMENTATION_SUMMARY.md`

---

## 📊 当前 GitHub Actions 配置状态

✅ **Workflow 已配置**:
- `.github/workflows/build_android.yml` 已包含 Supabase 上传步骤

⚠️ **需要的 Secrets**:
- `SUPABASE_URL` (需要添加)
- `SUPABASE_SERVICE_KEY` (需要添加)

推送代码到 main 分支后，GitHub Actions 会自动：
1. 编译 APK
2. 上传到 Supabase Storage
3. 更新数据库版本记录

---

**推荐**: 使用自动配置脚本 `./scripts/setup_complete.sh` 🚀
