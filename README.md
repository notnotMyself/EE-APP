# AI数字员工平台 - 项目总览

> **核心定位：企业内部的 AI 角色工作台 + 决策前哨站**
> 
> *「让 AI 帮你盯着那些你没空盯的事」*

---

## 🎯 产品愿景

这是一个以 AI 数字员工为核心的「决策认知辅助系统」：

- **不是信息流产品** - 不追求刷内容的时长
- **不是 BI 工具** - 不只是看数据
- **不是聊天机器人** - 不只是一问一答

而是：**让关键人群每天自然地被 AI 帮助做判断**

详见：[📖 产品定位与价值](docs/PRODUCT_VISION.md)

---

## 🎯 项目状态

### ✅ 后端 (已完成)
- **Supabase数据层**: 数据库Schema + RLS + Helper Functions
- **FastAPI AI层**: 支持Auth Token + SSE流式对话
- **测试数据**: 5个内置AI员工已创建

### ✅ Flutter前端 (基础框架完成)
- **项目结构**: Clean Architecture + Feature-first
- **核心配置**: Supabase + GoRouter + Riverpod
- **UI页面**: 登录、注册、首页等基础页面

---

## 📁 项目结构

```
ee_app_claude/
├── supabase/                              # Supabase配置
│   ├── migrations/                        # 数据库迁移
│   ├── seed.sql                          # 测试数据
│   └── DEPLOYMENT.md                     # 部署文档
│
├── ai_agent_platform/backend/            # FastAPI后端
│   ├── app/
│   │   ├── core/                         # 核心配置
│   │   ├── services/                     # Claude服务
│   │   ├── models/                       # 数据模型
│   │   └── api/v1/endpoints/            # API端点
│   ├── main.py                           # 应用入口
│   ├── requirements.txt                  # Python依赖
│   └── .env                              # 环境配置
│
├── flutter_config/                        # Flutter配置文件
│   ├── pubspec.yaml                      # 依赖配置
│   └── lib/                              # 源代码
│       ├── main.dart                     # 应用入口
│       ├── core/                         # 核心功能
│       └── features/                     # 功能模块
│
├── ai_agent_app/                         # Flutter项目 (运行setup_flutter.sh创建)
│
├── ARCHITECTURE.md                        # 架构文档
├── BACKEND_SETUP_COMPLETE.md             # 后端设置完成
├── FLUTTER_SETUP.md                      # Flutter设置指南
└── setup_flutter.sh                      # Flutter一键设置脚本
```

---

## 🚀 快速开始

### 1. 启动后端 (FastAPI)

```bash
cd /Users/80392083/develop/ee_app_claude/ai_agent_platform/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --port 8000

# 访问API文档
open http://localhost:8000/docs
```

### 2. 设置Flutter项目

```bash
cd /Users/80392083/develop/ee_app_claude

# 运行一键设置脚本
./setup_flutter.sh

# 进入项目
cd ai_agent_app

# 运行应用
flutter run
```

---

## 🔑 配置信息

### Supabase
- **URL**: https://dwesyojvzbltqtgtctpt.supabase.co
- **Anon Key**: (见.env文件)
- **Dashboard**: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt

### FastAPI Backend
- **本地地址**: http://localhost:8000
- **API前缀**: /api/v1
- **配置**: ai_agent_platform/backend/.env

### Claude API
- **Auth Token**: 已配置在.env中
- **Base URL**: https://llm-gateway.oppoer.me
- **Model**: saas/claude-sonnet-4.5

---

## 📊 数据库

### 核心表
- `users` - 用户
- `agents` - AI员工 (5个内置员工已创建)
- `user_agent_subscriptions` - 订阅关系
- `conversations` - 对话
- `messages` - 消息
- `alerts` - 提醒
- `tasks` - 任务
- `artifacts` - AI生成的产出
- `agent_analytics` - 分析数据

### 查看数据
https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/editor

---

## 🎨 Flutter功能清单

### ✅ 已完成
- [x] 项目基础框架
- [x] Material Design 3主题
- [x] GoRouter路由配置
- [x] Riverpod状态管理
- [x] 登录/注册UI页面
- [x] 首页布局
- [x] Supabase配置

### 🚧 进行中
- [ ] Supabase Auth集成
- [ ] AI员工列表
- [ ] 对话功能
- [ ] Alerts提醒

### 📋 待开发
- [ ] 个人中心
- [ ] 设置页面
- [ ] Push通知
- [ ] 深色模式切换

---

## 🏗️ 架构设计

### 混合架构
```
Flutter App
    │
    ├─► Supabase (数据层 - 70%)
    │   • 用户认证
    │   • 数据CRUD
    │   • 实时订阅
    │   • 文件存储
    │
    └─► FastAPI (AI层 - 30%)
        • AI对话 (Auth Token)
        • SSE流式响应
        • 定时分析 (可选)
```

### 优势
- ✅ 利用Supabase免费功能(数据库+RLS+Realtime)
- ✅ 掌控AI能力(使用内部Auth Token)
- ✅ 简化Flutter开发(直接查询Supabase)
- ✅ 降低运维成本(只维护一个轻量FastAPI)

---

## 📱 开发工作流

### 日常开发
1. **启动后端**: `cd ai_agent_platform/backend && uvicorn main:app --reload`
2. **启动Flutter**: `cd ai_agent_app && flutter run`
3. **查看数据**: Supabase Dashboard
4. **API测试**: http://localhost:8000/docs

### 代码组织
```
Flutter Feature结构:
features/
  ├── auth/              # 认证
  ├── agents/            # AI员工
  ├── conversations/     # 对话
  ├── alerts/            # 提醒
  └── profile/           # 个人中心

每个Feature包含:
  ├── data/              # 数据层
  ├── domain/            # 业务逻辑
  └── presentation/      # UI层
```

---

## 🔧 常用命令

### Flutter
```bash
# 运行应用
flutter run

# 运行在指定设备
flutter run -d chrome
flutter run -d "iPhone 14"

# 清理构建
flutter clean && flutter pub get

# 代码生成
flutter pub run build_runner build --delete-conflicting-outputs

# 分析代码
flutter analyze
```

### FastAPI
```bash
# 开发模式
uvicorn main:app --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 查看日志
tail -f logs/app.log
```

---

## 📚 文档索引

### 核心文档
- **📖 产品定位与价值**: [docs/PRODUCT_VISION.md](docs/PRODUCT_VISION.md) - 产品愿景、目标用户、价值创造
- **🛠️ Auto-Develop 策略**: [docs/AUTO_DEVELOP_STRATEGY.md](docs/AUTO_DEVELOP_STRATEGY.md) - AI 驱动开发流程

### 技术文档
- **架构设计**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **后端设置**: [BACKEND_SETUP_COMPLETE.md](BACKEND_SETUP_COMPLETE.md)
- **Flutter设置**: [FLUTTER_SETUP.md](FLUTTER_SETUP.md)
- **Supabase部署**: [supabase/DEPLOYMENT.md](supabase/DEPLOYMENT.md)

### 规范驱动开发
- **OpenSpec 规范**: [openspec/](openspec/) - 规范驱动开发框架
- **项目约定**: [openspec/project.md](openspec/project.md) - 技术栈和约定

---

## 🎯 产品演进路线

### Phase 1: 数字秘书 MVP（当前）
> **目标**：证明 AI 能稳定扮演一个可信角色

- [x] 研发效能分析官实现
- [ ] 认证功能（Supabase Auth）
- [ ] AI 员工列表
- [ ] 对话功能（SSE 流式）
- [ ] 信息流首页

**成功指标**：1 个用户连续 7 天每天都看

### Phase 2: 秘书系统化
> **目标**：多角色、结构化信息流、用户开始依赖

- [ ] NPS 洞察官
- [ ] 竞品情报官
- [ ] 舆情哨兵
- [ ] 信息流结构化
- [ ] 任务托付功能

### Phase 3: 认知基础设施
> **目标**：从「看」到「引用」，从个人到组织

- [ ] 信息流被引用到会议/汇报
- [ ] 组织级别推广
- [ ] 决策习惯被改变

---

## 🛠️ Auto-Develop 工作流

本项目采用 **规范驱动 + AI 执行** 的开发模式：

```
需求输入 → AI 生成规范 → 人审核 → AI 实现 → 人验收 → 规范沉淀
```

详见：[🛠️ Auto-Develop 策略](docs/AUTO_DEVELOP_STRATEGY.md)

---

## 💡 提示

- **Supabase Dashboard**: 随时查看数据库数据
- **API文档**: FastAPI自动生成 Swagger文档
- **热重载**: Flutter和FastAPI都支持热重载
- **日志**: 使用logger包记录关键信息

---

**项目开始日期**: 2024-12-29
**当前状态**: MVP开发中
**预计完成**: 2025-02 (Phase 1-4)
