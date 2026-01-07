# AI数字员工平台 - 最终架构方案

## 🎯 架构决策

基于实际情况（内部Auth Token + 自定义Base URL），采用**混合架构**：

```
┌──────────────────────────────────────────────────┐
│                 Flutter App                       │
└──────────────────────────────────────────────────┘
           │                    │
           │                    │
    ┌──────▼─────┐       ┌─────▼──────┐
    │  Supabase  │       │  FastAPI   │
    │  数据层     │       │  AI层      │
    └────────────┘       └────────────┘
```

## 📊 职责分工

### Supabase (数据层 - 70%)

**负责**:
- ✅ 用户认证 (Supabase Auth)
- ✅ 数据存储 (PostgreSQL + RLS)
- ✅ 实时订阅 (Realtime - alerts推送)
- ✅ 文件存储 (Storage - 头像、报告等)

**Flutter直接调用**:
```dart
// 查询AI员工列表
final agents = await supabase.from('agents').select();

// 订阅AI员工
await supabase.from('user_agent_subscriptions').insert({...});

// 查询对话历史
final messages = await supabase.from('messages').select();

// 实时监听alerts
supabase.from('alerts').stream(primaryKey: ['id']).listen((data) {
  // 收到新的alert提醒
});
```

### FastAPI (AI层 - 30%)

**负责**:
- ✅ AI对话 (使用你的Auth Token)
- ✅ SSE流式响应
- ✅ 定时分析任务 (可选)

**端点**:
```
POST /api/v1/conversations/{id}/messages/stream
  - 输入: conversationId, message
  - 输出: SSE流式AI响应
  - 使用: ANTHROPIC_AUTH_TOKEN + 自定义Base URL

POST /api/v1/agent/analyze (可选，如需定时分析)
  - 输入: agentId, dateRange
  - 输出: 分析结果
```

## 🔧 配置文件

### FastAPI Backend (.env)

```bash
# Supabase (用于保存messages到数据库)
SUPABASE_URL=https://dwesyojvzbltqtgtctpt.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Database (用于直接查询conversations等)
DATABASE_URL=postgresql://postgres.dwesyojvzbltqtgtctpt:vJ3xR6wE8MJgiHXS@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Claude API - 使用你的Auth Token
ANTHROPIC_AUTH_TOKEN=sk-QTakUxAFn8sR4t29yGlkWmJr5ne9JfsQKHtKKnmy8LEskgbX
ANTHROPIC_BASE_URL=https://llm-gateway.oppoer.me
ANTHROPIC_MODEL=saas/claude-sonnet-4.5

# Security
SECRET_KEY=your-secret-key-change-this
```

### Flutter (main.dart)

```dart
// Supabase配置
const supabaseUrl = 'https://dwesyojvzbltqtgtctpt.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

// FastAPI配置
const fastApiUrl = 'http://localhost:8000';  // 或你部署的地址
```

## 📁 保留的代码

### Supabase (全部保留)
```
supabase/
├── migrations/
│   ├── 20241228000000_initial_schema.sql          ✅ 保留
│   └── 20241229000000_rls_policies_enhancement.sql ✅ 保留
└── seed.sql                                        ✅ 保留
```

### FastAPI Backend (保留核心部分)
```
ai_agent_platform/backend/
├── app/
│   ├── core/
│   │   ├── config.py             ✅ 已更新支持Auth Token
│   │   └── security.py           ✅ 保留
│   ├── models/
│   │   ├── user.py              ✅ 保留
│   │   └── conversation.py      ✅ 保留
│   ├── services/
│   │   └── claude_service.py    ✅ 已更新支持Auth Token
│   ├── api/v1/endpoints/
│   │   ├── auth.py              ❌ 删除(用Supabase Auth)
│   │   ├── agents.py            ❌ 删除(Flutter直接查Supabase)
│   │   ├── subscriptions.py     ❌ 删除(Flutter直接查Supabase)
│   │   └── conversations.py     ✅ 保留(只保留chat-stream端点)
│   └── db/
│       └── session.py           ✅ 保留(连接Supabase数据库)
├── main.py                       ✅ 保留(简化)
└── requirements.txt              ✅ 保留
```

### 删除的部分
```
supabase/functions/          ❌ 删除Edge Functions(用FastAPI代替)
ai_agent_platform/backend/app/crud/    ❌ 删除(Flutter直接CRUD)
ai_agent_platform/backend/app/schemas/ ❌ 删除(简化)
```

## 🚀 部署方式

### 开发环境
1. **Supabase**: 已经在线(免费)
2. **FastAPI**: 本地运行 `uvicorn main:app --reload`
3. **Flutter**: 连接本地FastAPI + 在线Supabase

### 生产环境（未来）
1. **Supabase**: 保持在线(可能需要升级套餐)
2. **FastAPI**: 部署到内网服务器/Docker容器
3. **Flutter**: 打包发布

## ✅ 优势总结

1. **降低成本**: Supabase免费层足够用，只需维护一个轻量FastAPI
2. **保护Token**: Auth Token只在后端使用，不暴露到客户端
3. **灵活性**: AI逻辑完全掌控，可以随时切换模型或provider
4. **简化开发**: Flutter大部分操作直接调Supabase，代码简洁
5. **实时功能**: Alerts可以通过Supabase Realtime实时推送
6. **安全性**: RLS保护数据，每个用户只能看到自己的数据

## 📝 下一步

1. ✅ 配置已完成(支持Auth Token)
2. ⏳ 在Dashboard执行seed.sql
3. ⏳ 测试FastAPI是否正常
4. ⏳ 开始Flutter开发

---

**关键点**: 这个架构既利用了Supabase的强大功能（免费数据库+RLS+实时订阅），又保留了对AI能力的完全控制（使用你的Auth Token）。是最适合当前情况的方案！
