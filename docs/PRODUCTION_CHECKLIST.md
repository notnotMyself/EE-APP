# 生产环境上线检查清单

## 概述

本清单用于确保应用上线前所有必要的配置和验证都已完成。

**文档参考**:
- 详细配置指南: `docs/PRODUCTION_CONFIG.md`
- 测试报告: `docs/PRE_LAUNCH_TEST_REPORT.md`
- UI测试指南: `docs/MANUAL_UI_TEST_GUIDE.md`

---

## 一、代码就绪检查

### Git状态

- [x] 所有P0功能已在 `feature/pre-launch-preparation` 分支完成
- [x] 代码已提交并有详细的commit信息（10个commits）
- [ ] 代码已经过Code Review
- [ ] 分支已合并到 `main`（或准备合并）
- [ ] Git tags已打上版本标签（例如：v1.0.0）

### 代码质量

- [x] 后端全局异常处理已实现
- [x] 前端全局错误处理已实现
- [x] 所有API端点已测试验证
- [ ] UI功能已手动测试（参考 `MANUAL_UI_TEST_GUIDE.md`）
- [ ] 无严重bug（P0级别）
- [ ] 性能测试通过（启动<3秒，响应<2秒）

---

## 二、后端配置检查

### 环境变量配置

**配置文件**: `/Users/80392083/develop/ee_app_claude/backend/agent_orchestrator/.env.production`

- [ ] 文件已创建（从 `.env.example` 复制）
- [ ] `ENV=production` ✓
- [ ] `LOG_LEVEL=INFO` ✓
- [ ] `APP_VERBOSE_LIB_LOGS=0` ✓
- [ ] `SUPABASE_URL` 已填写 ✓
- [ ] `SUPABASE_SERVICE_KEY` 已填写真实密钥 ⚠️
- [ ] `ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN` 已填写 ⚠️
- [ ] `CORS_ORIGINS` 已配置生产域名（**不是** `*`） ⚠️
- [ ] `JPUSH_APP_KEY` 已填写（可选，推送功能需要）
- [ ] `JPUSH_MASTER_SECRET` 已填写（可选）
- [ ] `JPUSH_APNS_PRODUCTION=true`（iOS推送生产环境）
- [ ] `GEMINI_API_KEY` 已填写（可选，封面图生成）

**获取密钥方式**:
- Supabase Service Key: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/api
- Anthropic API Key: https://console.anthropic.com/
- JPush: https://www.jiguang.cn/ (需申请)
- Gemini: https://aistudio.google.com/app/apikey

### 服务部署

**方式1: systemd (推荐)**
- [ ] 创建服务文件 `/etc/systemd/system/ee-backend.service`
- [ ] 服务配置正确（WorkingDirectory、EnvironmentFile、ExecStart）
- [ ] 服务已启动：`sudo systemctl start ee-backend`
- [ ] 服务已启用自动启动：`sudo systemctl enable ee-backend`
- [ ] 服务运行正常：`sudo systemctl status ee-backend`

**方式2: Docker (可选)**
- [ ] Dockerfile已创建
- [ ] Docker镜像已构建
- [ ] 容器已启动并运行正常

### 后端健康检查

```bash
# 验证后端服务运行正常
curl https://your-production-api.com/health | jq .

# 应该返回:
# {
#   "status": "healthy",
#   "database": "connected",
#   "scheduler": {"status": "running"},
#   "agents_loaded": 4
# }
```

- [ ] `/health` 端点返回 `"status": "healthy"`
- [ ] `"database": "connected"`
- [ ] `"agents_loaded": 4` (或实际Agent数量)
- [ ] `/api/v1/legal/documents/privacy_policy` 可访问
- [ ] `/api/v1/legal/documents/terms_of_service` 可访问

---

## 三、数据库配置检查

### Supabase生产环境

**项目信息**:
- Project Ref: `dwesyojvzbltqtgtctpt`
- Dashboard: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt

### 数据库迁移

```bash
# 连接到生产数据库
supabase link --project-ref dwesyojvzbltqtgtctpt --password "your-db-password"

# 执行迁移（❗️ 先备份数据库）
supabase db push
```

- [ ] 生产数据库已备份
- [ ] 迁移文件 `20260123000002_add_terms_and_policies.sql` 已执行
- [ ] `legal_documents` 表已创建
- [ ] `user_consents` 表已创建
- [ ] 隐私政策 v1.0 数据已插入
- [ ] 用户协议 v1.0 数据已插入
- [ ] RLS策略已启用

### 验证数据库

```sql
-- 验证表存在
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('legal_documents', 'user_consents');

-- 验证法律文档数据
SELECT document_type, version, title, is_active
FROM legal_documents;

-- 应该返回2行：privacy_policy和terms_of_service
```

- [ ] SQL查询验证通过
- [ ] 数据库连接限制已配置（防止DDoS）
- [ ] 数据库访问IP白名单已配置（可选）

---

## 四、前端配置检查

### AppConfig生产URL

**文件**: `ai_agent_app/lib/core/config/app_config.dart`

```dart
case 'prod':
  return 'https://api.eeplatform.com';  // ⚠️ 替换为实际URL
```

- [ ] 生产API URL已填写（**不是TODO**）
- [ ] URL格式正确（https://开头，无尾部斜杠）
- [ ] 域名已注册并指向生产服务器
- [ ] SSL证书已配置（HTTPS可访问）

### Supabase配置

```dart
static const String supabaseUrl = 'https://dwesyojvzbltqtgtctpt.supabase.co';
static const String supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
```

- [ ] Supabase URL正确
- [ ] Supabase Anon Key正确（从Dashboard获取）

### 应用版本号

**文件**: `ai_agent_app/pubspec.yaml`

```yaml
version: 1.0.0+100  # version_name+version_code
```

- [ ] 版本号已更新为上线版本（例如：1.0.0+100）
- [ ] version_name语义化（1.0.0）
- [ ] version_code递增（100）

---

## 五、应用构建检查

### Android

```bash
cd ai_agent_app
flutter build apk --dart-define=ENV=prod --release
```

- [ ] 构建命令成功执行
- [ ] APK文件已生成：`build/app/outputs/flutter-apk/app-release.apk`
- [ ] APK大小合理（< 50MB）
- [ ] 已签名（使用正式keystore，非debug）
- [ ] 安装到真机测试正常

### iOS

```bash
cd ai_agent_app
flutter build ios --dart-define=ENV=prod --release
```

- [ ] 构建命令成功执行
- [ ] 在Xcode中签名成功
- [ ] 已导出IPA文件
- [ ] 安装到真机测试正常

### 构建验证

- [ ] 启动时间 < 3秒
- [ ] 首次登录显示隐私协议
- [ ] 注册功能正常（包含username字段）
- [ ] 登录后可正常对话
- [ ] 错误提示为中文且友好
- [ ] 无崩溃和ANR

---

## 六、安全和隐私检查

### 密钥安全

- [ ] `.env.production` 文件**未提交**到Git
- [ ] `.env.production` 在 `.gitignore` 中
- [ ] 生产密钥与开发密钥不同
- [ ] 密钥轮换计划已制定（建议每90天）

### HTTPS和CORS

- [ ] 后端服务使用HTTPS（生产环境必须）
- [ ] SSL证书有效且未过期
- [ ] CORS配置了具体域名（不是 `*`）
- [ ] CORS测试：从前端域名访问后端API成功

### 隐私合规

- [ ] 隐私政策文本已由法务审核（可选但建议）
- [ ] 用户协议文本已由法务审核（可选但建议）
- [ ] 首次登录强制显示协议
- [ ] 用户同意记录到数据库（audit trail）

### 错误信息

- [ ] 生产环境不暴露技术细节（堆栈跟踪、SQL错误）
- [ ] 错误日志不记录敏感信息（密码、Token）
- [ ] 全局异常处理器正常工作

---

## 七、测试验收检查

### 后端API测试

- [x] 健康检查端点正常
- [x] Agent列表API正常
- [x] 法律文档API正常（privacy_policy、terms_of_service）
- [x] 全局异常处理器测试通过
- [ ] 对话创建和消息发送API正常
- [ ] WebSocket连接正常

### Flutter UI测试

**参考**: `docs/MANUAL_UI_TEST_GUIDE.md`

- [ ] 注册功能（9个测试用例）
- [ ] 登录功能（3个测试用例）
- [ ] 隐私协议（5个测试用例）
- [ ] 错误处理（3个测试用例）
- [ ] Agent对话（4个测试用例）
- [ ] UI体验（5个测试用例）
- [ ] 至少15张功能截图已保存

### 性能测试

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 应用启动时间 | < 3秒 | | ⬜ |
| 登录响应时间 | < 2秒 | | ⬜ |
| 页面切换流畅度 | 60fps | | ⬜ |
| 消息发送响应 | < 200ms | | ⬜ |
| 内存使用 | < 150MB | | ⬜ |

### 端到端流程测试

- [ ] 新用户注册 → 登录 → 同意协议 → 进入主页 → 创建对话 → 发送消息
- [ ] 老用户登录 → 直接进入主页 → 继续对话
- [ ] 网络断开 → 显示友好错误 → 网络恢复 → 自动重连
- [ ] Token过期 → 自动跳转登录 → 重新登录后恢复

---

## 八、监控和日志检查

### 应用日志

- [ ] 后端日志级别设为INFO（生产环境）
- [ ] 日志文件路径已配置
- [ ] 日志轮转已配置（防止磁盘占满）
- [ ] 关键操作有日志记录（登录、注册、创建对话）

### 错误监控（可选）

- [ ] Sentry已集成（可选）
- [ ] 错误上报测试正常
- [ ] 报警规则已配置

### 健康监控

- [ ] 设置定时任务监控 `/health` 端点
- [ ] 数据库连接失败时发送告警
- [ ] 服务崩溃时自动重启（systemd Restart=always）

---

## 九、应用商店准备

### 元数据

- [ ] 应用名称: AI数字员工平台
- [ ] 应用描述（中文）已准备
- [ ] 应用图标 (1024x1024 PNG) 已准备
- [ ] 应用截图（至少3张，不同功能）已准备
- [ ] 隐私政策URL已提供
- [ ] 应用分类已选择（生产力工具/商务）

### 应用商店账号

**Google Play**:
- [ ] 开发者账号已注册
- [ ] 应用已创建
- [ ] 发布轨道已选择（Alpha/Beta/Production）

**Apple App Store**:
- [ ] 开发者账号已注册
- [ ] App ID已创建
- [ ] Provisioning Profile已配置
- [ ] 证书已上传

### 审核准备

- [ ] 测试账号已提供（审核人员使用）
- [ ] 应用功能说明已准备
- [ ] 符合应用商店审核指南

---

## 十、上线流程

### 灰度发布（推荐）

- [ ] 制定灰度发布计划（例如：5% → 20% → 50% → 100%）
- [ ] 设置灰度发布比例
- [ ] 监控灰度用户的崩溃率和错误日志
- [ ] 收集灰度用户反馈

### 正式发布

- [ ] 数据库迁移在正式发布前执行
- [ ] 后端服务在正式发布前部署完成
- [ ] DNS切换到生产服务器（如需要）
- [ ] 应用商店提交审核
- [ ] 应用审核通过
- [ ] 正式发布到应用商店

### 发布后监控（上线后24小时内）

- [ ] 监控服务器CPU和内存使用
- [ ] 监控API响应时间
- [ ] 监控错误率和崩溃率
- [ ] 检查用户反馈（应用商店评论）
- [ ] 准备快速修复方案（hotfix）

---

## 十一、回滚准备

### 回滚计划

- [ ] 上一版本APK/IPA已保存
- [ ] 数据库备份已保存
- [ ] 回滚脚本已准备

### 回滚条件

如果出现以下情况，立即回滚：
- 崩溃率 > 5%
- 登录成功率 < 90%
- 关键功能不可用（对话、注册、登录）
- 数据丢失或数据损坏

### 回滚步骤

```bash
# 1. 后端回滚
sudo systemctl stop ee-backend
cp /opt/ee-platform/backend/.env.production.backup /opt/ee-platform/backend/.env.production
sudo systemctl start ee-backend

# 2. 数据库回滚（如果需要）
# 从备份恢复数据库

# 3. 前端回滚
# 应用商店发布上一版本，或提供旧版本APK下载链接
```

---

## 十二、必须完成项总结

### P0级别（必须完成，否则不能上线）

**后端**:
- [ ] `.env.production` 文件已创建，所有必需变量已填写真实值
- [ ] CORS配置了生产域名（不是 `*`）
- [ ] 生产服务器已部署，健康检查通过
- [ ] 数据库迁移已执行

**前端**:
- [ ] `AppConfig.apiBaseUrl` 生产环境已配置（不是TODO）
- [ ] 生产版本APK/IPA已构建并测试正常
- [ ] UI功能已手动测试（至少完成注册、登录、协议功能）

**测试**:
- [ ] 端到端测试通过（注册 → 登录 → 协议 → 对话）
- [ ] 无P0级别bug
- [ ] 性能测试通过

**文档**:
- [x] 生产配置文档已创建
- [x] 测试报告已创建
- [x] UI测试指南已创建

### P1级别（强烈建议，可上线后快速补上）

- [ ] JPush推送配置（需要先申请凭证）
- [ ] 版本更新检查功能
- [ ] Sentry错误监控
- [ ] 应用商店元数据完善

---

## 最终确认

**上线负责人**: _____________

**检查日期**: 2026-01-22

**上线日期**: _____________

**确认签名**: _____________

---

**备注**:
- 本清单基于 `feature/pre-launch-preparation` 分支的工作
- 详细配置步骤请参考 `docs/PRODUCTION_CONFIG.md`
- UI测试详细步骤请参考 `docs/MANUAL_UI_TEST_GUIDE.md`
- 测试结果请参考 `docs/PRE_LAUNCH_TEST_REPORT.md`
