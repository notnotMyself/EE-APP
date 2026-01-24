# 生产环境配置指南

## 目录

- [概述](#概述)
- [后端配置](#后端配置)
- [前端配置](#前端配置)
- [构建和部署](#构建和部署)
- [配置检查清单](#配置检查清单)
- [常见问题](#常见问题)

---

## 概述

本文档说明如何配置AI数字员工平台的生产环境。生产环境配置与开发环境的主要区别：

1. **安全性**: 使用真实的API密钥和证书，隐藏技术细节
2. **性能**: 启用生产优化（代码压缩、缓存等）
3. **可用性**: 配置监控、日志和备份
4. **合规性**: HTTPS、CORS、数据保护

**重要**:
- ⚠️ 生产环境密钥绝对不要提交到Git
- ⚠️ 所有敏感信息使用环境变量或密钥管理服务
- ⚠️ 定期备份数据库和配置

---

## 后端配置

### 1. 环境变量配置

#### 1.1 创建生产环境文件

```bash
cd backend/agent_orchestrator

# 复制示例文件
cp .env.example .env.production

# 编辑配置文件
vim .env.production
```

#### 1.2 必需配置项

**基础配置**:
```bash
# 环境标识（重要！）
ENV=production

# 日志级别（生产环境使用 INFO）
LOG_LEVEL=INFO
APP_VERBOSE_LIB_LOGS=0
```

**Supabase 配置**:
```bash
# 项目 URL
SUPABASE_URL=https://dwesyojvzbltqtgtctpt.supabase.co

# Service Role Key（从 Supabase Dashboard 获取）
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 获取方式:
# 1. 登录 https://supabase.com/dashboard
# 2. 选择项目: dwesyojvzbltqtgtctpt
# 3. Settings > API > Service Role Key
```

**Claude API 配置**:
```bash
# 方案1: 使用官方 API
ANTHROPIC_API_KEY=sk-ant-api03-xxx...

# 方案2: 使用自定义网关
ANTHROPIC_AUTH_TOKEN=sk-QTakUxAFn8sRxxxxx
ANTHROPIC_BASE_URL=https://llm-gateway.oppoer.me
```

**JPush 配置**（可选，需要先申请）:
```bash
# 极光推送凭证
JPUSH_APP_KEY=你的AppKey
JPUSH_MASTER_SECRET=你的MasterSecret
JPUSH_APNS_PRODUCTION=true

# 申请地址: https://www.jiguang.cn/
# 申请后在控制台获取 App Key 和 Master Secret
```

**CORS 配置**（重要！）:
```bash
# 生产环境只允许信任的域名
CORS_ORIGINS=https://app.eeplatform.com,https://www.eeplatform.com

# ⚠️ 不要在生产环境使用 * 通配符！
```

#### 1.3 可选配置项

**Gemini API**（封面图生成）:
```bash
GEMINI_API_KEY=AIzaSy...

# 获取地址: https://aistudio.google.com/app/apikey
```

**数据库直连**（如不使用Supabase SDK）:
```bash
DATABASE_URL=postgresql://postgres:password@db.dwesyojvzbltqtgtctpt.supabase.co:5432/postgres
```

### 2. 启动生产服务

```bash
cd backend/agent_orchestrator

# 确保已安装依赖
pip install -r requirements.txt

# 加载生产环境变量并启动
export $(cat .env.production | xargs) && python3 main.py

# 或使用 systemd 服务（推荐）
# 见下文"部署到服务器"章节
```

### 3. 健康检查

启动后验证服务正常：

```bash
# 健康检查
curl http://localhost:8000/health

# 应该返回:
# {
#   "status": "healthy",
#   "database": "connected",
#   "scheduler": {"status": "running"},
#   "agents_loaded": 4
# }

# 检查法律文档API
curl http://localhost:8000/api/v1/legal/documents/privacy_policy
```

### 4. 部署到服务器

#### 4.1 使用 systemd（推荐）

创建服务文件 `/etc/systemd/system/ee-backend.service`:

```ini
[Unit]
Description=AI Employee Platform Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ee-platform/backend/agent_orchestrator
EnvironmentFile=/opt/ee-platform/backend/agent_orchestrator/.env.production
ExecStart=/usr/bin/python3 /opt/ee-platform/backend/agent_orchestrator/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ee-backend
sudo systemctl start ee-backend
sudo systemctl status ee-backend
```

#### 4.2 使用 Docker（可选）

创建 `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/agent_orchestrator /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python3", "main.py"]
```

构建和运行:
```bash
docker build -t ee-backend .
docker run -d --env-file .env.production -p 8000:8000 ee-backend
```

---

## 前端配置

### 1. AppConfig 生产 URL

修改 `ai_agent_app/lib/core/config/app_config.dart`:

```dart
class AppConfig {
  static String get apiBaseUrl {
    const env = String.fromEnvironment('ENV', defaultValue: 'dev');
    switch (env) {
      case 'prod':
        // ⚠️ 替换为实际的生产API地址
        return 'https://api.eeplatform.com';
      case 'dev':
      default:
        return 'http://localhost:8000/api/v1';
    }
  }

  // Supabase 配置
  static const String supabaseUrl = 'https://dwesyojvzbltqtgtctpt.supabase.co';
  static const String supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

  // ⚠️ 从 Supabase Dashboard > Settings > API > anon public key 获取
}
```

### 2. JPush 配置（可选）

如果使用极光推送，需要配置AppKey。

修改推送服务配置文件（位置取决于实现）:
```dart
class PushConfig {
  static const String jpushAppKey = 'your-jpush-app-key';
}
```

---

## 构建和部署

### 1. 构建命令

#### Android APK

```bash
cd ai_agent_app

# 开发版本（连接 localhost:8000）
flutter build apk --dart-define=ENV=dev

# 生产版本（连接生产API）
flutter build apk --dart-define=ENV=prod --release

# 输出位置:
# build/app/outputs/flutter-apk/app-release.apk
```

#### iOS IPA

```bash
cd ai_agent_app

# 开发版本
flutter build ios --dart-define=ENV=dev

# 生产版本
flutter build ios --dart-define=ENV=prod --release

# 需要在 Xcode 中签名和导出 IPA
```

### 2. 版本号管理

修改 `pubspec.yaml`:
```yaml
version: 1.0.0+100  # version_name+version_code

# version_name: 1.0.0 (语义化版本，用户可见)
# version_code: 100 (构建号，递增整数，用于比较)
```

**发布新版本流程**:
1. 更新 `pubspec.yaml` 中的版本号
2. 构建生产版本
3. 发布到应用商店
4. 在数据库 `app_versions` 表中插入新版本记录（用于版本更新检查）

### 3. 应用商店元数据

准备以下资料用于应用商店提交:

**必需资料**:
- 应用名称: AI数字员工平台
- 应用描述: （见下文示例）
- 应用图标: 1024x1024 PNG（无透明度）
- 应用截图: 至少3张（不同屏幕尺寸）
- 隐私政策URL: https://your-domain.com/privacy
- 应用分类: 生产力工具 / 商务

**应用描述示例**:
```
AI数字员工平台 - 您的智能工作助手

让AI员工帮您处理日常工作，提升效率：

✨ 核心功能
• AI对话助手 - 24/7在线解答问题
• 任务管理 - 智能提醒和执行
• 数据分析 - 自动生成简报
• 多员工协作 - 研发、产品、运营全覆盖

🚀 为什么选择我们
• 专业AI模型 - 基于Claude最新技术
• 安全可靠 - 企业级数据保护
• 简单易用 - 无需培训即可上手

立即下载，开启智能办公新时代！
```

---

## 配置检查清单

### 后端配置

- [ ] `.env.production` 文件已创建
- [ ] 所有必需环境变量已填写真实值
- [ ] `ENV=production` 已设置
- [ ] `LOG_LEVEL=INFO` 已设置
- [ ] Supabase Service Key 已配置
- [ ] Claude API 密钥已配置
- [ ] CORS 配置了生产域名（不是 `*`）
- [ ] 健康检查端点返回正常
- [ ] 法律文档API可访问
- [ ] 数据库迁移已执行

### 前端配置

- [ ] `AppConfig.apiBaseUrl` 生产环境返回正确URL
- [ ] Supabase URL 和 Anon Key 已配置
- [ ] 版本号已更新（pubspec.yaml）
- [ ] 生产版本可正常构建
- [ ] 应用图标和启动页已配置
- [ ] 应用商店元数据已准备

### 数据库

- [ ] 所有迁移文件已执行
- [ ] RLS 策略已启用
- [ ] 法律文档（隐私政策、用户协议）已插入
- [ ] 数据库已备份
- [ ] 数据库连接限制已配置

### 安全性

- [ ] HTTPS 证书已配置
- [ ] API 密钥定期轮换计划已制定
- [ ] 敏感日志已关闭（不记录密码、Token）
- [ ] 错误信息不暴露技术细节
- [ ] 数据库访问IP已限制

### 监控和日志

- [ ] 应用日志已配置（文件或服务）
- [ ] 错误追踪已配置（可选：Sentry）
- [ ] 性能监控已配置（可选：APM）
- [ ] 健康检查定时任务已设置

---

## 常见问题

### Q1: 如何获取 Supabase Service Role Key？

**A**:
1. 登录 https://supabase.com/dashboard
2. 选择项目 `dwesyojvzbltqtgtctpt`
3. Settings > API > Service Role Key
4. 复制 Key 到 `.env.production`

### Q2: JPush 必须配置吗？

**A**: 不是必须的。如果暂时不需要推送通知功能，可以不配置JPush。后端代码会检测到凭证未配置并自动禁用推送功能。后续需要时再申请和配置即可。

### Q3: 如何申请 JPush 凭证？

**A**:
1. 访问 https://www.jiguang.cn/
2. 注册账号
3. 创建应用
4. 在控制台获取 App Key 和 Master Secret
5. 配置到 `.env.production`

### Q4: 生产环境如何连接本地数据库测试？

**A**: 不建议生产环境连接本地数据库。应该：
1. 使用 Supabase 的远程数据库
2. 或者部署独立的 PostgreSQL 生产实例
3. 确保数据库有公网访问或VPN

### Q5: 如何处理数据库迁移？

**A**:
```bash
# 连接到生产数据库
supabase link --project-ref dwesyojvzbltqtgtctpt --password "your-db-password"

# 执行迁移（先备份！）
supabase db push

# 验证迁移
supabase db diff
```

### Q6: 后端服务崩溃如何处理？

**A**:
1. 查看日志: `sudo journalctl -u ee-backend -f`
2. 检查健康端点: `curl http://localhost:8000/health`
3. 重启服务: `sudo systemctl restart ee-backend`
4. 检查环境变量是否正确加载

### Q7: 前端无法连接后端怎么办？

**A**: 检查以下项：
1. 后端服务是否运行（健康检查）
2. CORS 配置是否包含前端域名
3. 前端 `AppConfig.apiBaseUrl` 是否正确
4. 网络防火墙是否允许连接
5. HTTPS 证书是否有效

### Q8: 如何回滚配置？

**A**:
```bash
# 后端: 切换回之前的 .env 文件
cp .env.production.backup .env.production
sudo systemctl restart ee-backend

# 前端: 重新构建之前的版本
git checkout <previous-commit>
flutter build apk --dart-define=ENV=prod --release
```

### Q9: 生产环境性能慢怎么办？

**A**: 检查以下项：
1. 数据库查询是否有索引
2. API 响应时间监控
3. 日志级别是否过于详细（应为INFO）
4. 是否启用了缓存
5. Claude API 响应时间

### Q10: 如何确保配置安全？

**A**:
1. ✅ 所有密钥使用环境变量，不硬编码
2. ✅ .env.production 在 .gitignore 中
3. ✅ 定期轮换密钥（建议每90天）
4. ✅ 使用密钥管理服务（如 AWS Secrets Manager）
5. ✅ 最小权限原则（只授予必要权限）
6. ✅ 审计日志（记录谁访问了敏感配置）

---

## 联系支持

如有问题，请联系:
- 技术支持邮箱: support@eeplatform.com
- 文档反馈: 在 Git 仓库提交 Issue
