# 🛠️ APP 更新功能 - 配置操作指南

**重要**: 按照下面的顺序逐步完成配置

---

## ✅ 第一步：Supabase Storage 配置

### 方法 A：使用 Dashboard (推荐)

1. **打开 Supabase Dashboard**
   - 访问: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt
   - 登录你的账号

2. **创建 Storage Bucket**
   - 左侧菜单 → Storage
   - 点击 "New bucket"
   - Bucket name: `apk-releases`
   - ✅ 勾选 "Public bucket" (重要！否则无法下载)
   - 点击 "Create bucket"

3. **验证配置**
   - 进入 `apk-releases` bucket
   - 应该能看到一个空的文件列表
   - 右上角显示 "Public" 标识

### 方法 B：使用 SQL

1. 打开: Settings → Database → SQL Editor
2. 点击 "New query"
3. 复制粘贴以下 SQL:

```sql
-- 创建 Storage bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('apk-releases', 'apk-releases', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- 允许所有人读取（下载 APK）
CREATE POLICY IF NOT EXISTS "Public Read Access" ON storage.objects
FOR SELECT
USING (bucket_id = 'apk-releases');

-- 允许 service_role 上传
CREATE POLICY IF NOT EXISTS "Service Role Upload" ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'apk-releases' AND auth.role() = 'service_role');

-- 允许 service_role 删除
CREATE POLICY IF NOT EXISTS "Service Role Delete" ON storage.objects
FOR DELETE
USING (bucket_id = 'apk-releases' AND auth.role() = 'service_role');
```

4. 点击 "Run" 执行

---

## ✅ 第二步：获取 Supabase Service Key

1. **打开 API Settings**
   - Dashboard → Settings → API

2. **复制 Service Role Key**
   - 找到 "service_role" 部分
   - 点击眼睛图标显示密钥
   - 点击复制按钮
   - ⚠️ **重要**: 这是 `service_role` key，不是 `anon` key！

3. **记录信息**（后面配置时需要）
   ```
   SUPABASE_URL: https://dwesyojvzbltqtgtctpt.supabase.co
   SUPABASE_SERVICE_KEY: eyJhbG... (你复制的 key)
   ```

---

## ✅ 第三步：配置 GitHub Secrets

1. **打开 GitHub 仓库设置**
   - 访问: https://github.com/你的用户名/ee_app_claude
   - 点击 Settings (仓库设置)

2. **进入 Secrets 配置**
   - 左侧菜单 → Secrets and variables → Actions
   - 点击 "New repository secret"

3. **添加 SUPABASE_URL**
   - Name: `SUPABASE_URL`
   - Secret: `https://dwesyojvzbltqtgtctpt.supabase.co`
   - 点击 "Add secret"

4. **添加 SUPABASE_SERVICE_KEY**
   - 再次点击 "New repository secret"
   - Name: `SUPABASE_SERVICE_KEY`
   - Secret: 粘贴你在第二步复制的 service_role key
   - 点击 "Add secret"

5. **验证**
   - 应该能看到两个 secrets:
     - `SUPABASE_URL`
     - `SUPABASE_SERVICE_KEY`

---

## ✅ 第四步：插入测试版本数据

现在数据库已经有 `app_versions` 表了，但是是空的。我们需要插入一条测试数据。

### 方法 A：使用 Python 脚本 (推荐)

```bash
# 1. 设置环境变量（使用你在第二步复制的 key）
export SUPABASE_SERVICE_KEY="eyJhbG..."

# 2. 运行脚本
python3 scripts/insert_test_version.py
```

**预期输出**:
```
🔌 连接到 Supabase...
📝 停用旧版本...
📦 插入测试版本 v0.1.1 (code: 2)...

✅ 测试版本插入成功!
   版本: 0.1.1 (2)
   ID: xxxx-xxxx-xxxx
   下载地址: https://...

下一步:
1. 确保 APK 已上传到 Supabase Storage
2. 测试 API: curl 'http://localhost:8000/app/version/latest?current_version=1'
3. 在手机上测试更新流程
```

### 方法 B：使用 Supabase Dashboard SQL

1. Dashboard → SQL Editor → New query
2. 粘贴以下 SQL:

```sql
-- 停用旧版本
UPDATE app_versions SET is_active = false;

-- 插入测试版本
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

3. 点击 "Run"

---

## ✅ 第五步：验证后端 API

```bash
# 启动后端（如果还没启动）
cd backend/agent_orchestrator
python3 main.py

# 在另一个终端测试 API
curl "http://localhost:8000/app/version/latest?current_version=1&region=cn" | jq .
```

**预期输出**:
```json
{
  "has_update": true,
  "latest_version": {
    "version_code": 2,
    "version_name": "0.1.1",
    "apk_url": "https://dwesyojvzbltqtgtctpt.supabase.co/storage/v1/object/public/apk-releases/app-release-v2.apk",
    "apk_size": 50000000,
    "release_notes": "# 版本 0.1.1\n\n## 新功能...",
    "force_update": false,
    "download_sources": []
  },
  "message": "发现新版本 v0.1.1"
}
```

如果返回 `"has_update": false`，说明：
- 数据库中没有版本数据，或
- `version_code` ≤ `current_version`

---

## ✅ 第六步：配置本地环境变量（可选，用于本地测试上传脚本）

如果你想在本地测试上传脚本:

```bash
# 在项目根目录创建 .env 文件
cat > .env << EOF
SUPABASE_URL=https://dwesyojvzbltqtgtctpt.supabase.co
SUPABASE_SERVICE_KEY=你的_service_role_key
EOF

# 加载环境变量
source .env

# 测试上传脚本（需要先有 APK 文件）
python3 scripts/upload_apk.py ai_agent_app/build/app/outputs/flutter-apk/app-release.apk
```

---

## 📋 配置检查清单

完成上述步骤后，用这个清单验证:

- [ ] Supabase Storage bucket `apk-releases` 已创建并设为 public
- [ ] 已获取 Supabase Service Role Key
- [ ] GitHub Secrets 已配置:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_SERVICE_KEY`
- [ ] 测试版本数据已插入数据库
- [ ] 后端 API 测试通过（返回 `has_update: true`）
- [ ] (可选) 本地环境变量已配置

---

## 🎯 完成后的下一步

配置完成后，你可以：

### 立即测试 (不需要 GitHub Actions)

1. **编译当前版本 APK (v0.1.0)**
   ```bash
   # 确保 build.gradle 中 versionCode = 1
   cd ai_agent_app
   flutter build apk --release
   ```

2. **安装到手机**
   ```bash
   adb install build/app/outputs/flutter-apk/app-release.apk
   ```

3. **配置网络访问**
   ```bash
   # 方法 A: 使用 adb reverse (推荐)
   adb reverse tcp:8000 tcp:8000

   # 方法 B: 或修改 app_config.dart 使用电脑 IP
   # apiUrl: 'http://你的电脑IP:8000'
   ```

4. **打开 APP 测试**
   - 启动 APP
   - 应该自动弹出更新提示
   - 点击"立即更新"
   - 观察下载进度
   - 注意：由于 APK 文件还不存在，会下载失败（这是正常的）

### 完整流程测试 (需要 GitHub Actions)

1. **升级版本号**
   ```bash
   # 编辑 ai_agent_app/android/app/build.gradle
   versionCode = 2
   versionName = "0.1.1"
   ```

2. **提交并推送**
   ```bash
   git add .
   git commit -m "feat: 版本 0.1.1 - 测试更新功能"
   git push origin main
   ```

3. **GitHub Actions 自动执行**
   - 编译 APK
   - 上传到 Supabase Storage
   - 更新数据库

4. **在手机上测试**
   - 打开 APP (安装的是 v0.1.0)
   - 应该提示更新到 v0.1.1
   - 下载并安装
   - 验证版本已更新

---

## ⚠️ 常见问题

### Q: Storage bucket 创建失败？
A: 检查是否有足够的权限。如果是免费版，检查配额是否已满。

### Q: API 返回 401 错误？
A: Service Role Key 不正确。重新从 Dashboard 复制。

### Q: 下载 APK 失败？
A:
1. 检查 bucket 是否设为 public
2. 检查 APK 文件是否存在
3. 检查 URL 是否正确

### Q: GitHub Actions 上传失败？
A: 检查 GitHub Secrets 是否配置正确。

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 `docs/APP_UPDATE_TESTING_GUIDE.md` 的故障排除章节
2. 检查后端日志
3. 检查 Supabase Dashboard 的日志

---

**预计完成时间**: 10-15 分钟

**当前状态**: ⏸️ 等待配置

**下一个里程碑**: 配置完成后进行端到端测试
