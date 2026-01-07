# 后端部署完成 - 下一步操作

## ✅ 已完成的工作

1. **数据库Schema** - 9张核心表已创建
2. **RLS安全策略** - Row Level Security已配置
3. **数据库函数** - Helper functions已创建
4. **Edge Functions** - 2个核心函数已部署:
   - `chat-stream` - AI对话(SSE流式)
   - `agent-analysis` - 定时分析任务

## 🔧 需要手动配置的步骤

### 1. 设置Edge Functions环境变量

前往: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/functions

添加以下Secrets:

```
CLAUDE_API_KEY=sk-ant-api03-...  (你的Claude API Key)
CRON_SECRET=随机生成一个密钥 (例如: uuidgen生成)
```

### 2. 配置定时任务 (可选，如果需要自动分析)

前往: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/sql/new

执行以下SQL:

```sql
-- 创建每小时执行的定时分析任务
SELECT cron.schedule(
  'agent-analysis-hourly',
  '0 * * * *',
  $$
  SELECT
    net.http_post(
      url:='https://dwesyojvzbltqtgtctpt.supabase.co/functions/v1/agent-analysis',
      headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MzA5MTQsImV4cCI6MjA4MjUwNjkxNH0.t4TBNkYp99HWBFu5kBOAgH13_7O5UADAMAptR16ENqc"}'::jsonb,
      body:='{}'::jsonb
    ) AS request_id;
  $$
);

-- 查看已创建的定时任务
SELECT * FROM cron.job;

-- 如果需要删除任务:
-- SELECT cron.unschedule('agent-analysis-hourly');
```

### 3. 创建测试数据 (可选)

前往SQL Editor执行:

```sql
-- 创建一个内置的"研发效能分析官" Agent
INSERT INTO agents (
  name,
  role,
  description,
  is_builtin,
  is_active,
  capabilities,
  trigger_conditions
) VALUES (
  '研发效能分析官',
  'dev_efficiency_analyst',
  '持续监控团队的研发效能数据，包括代码Review耗时、返工率、需求交付周期等关键指标。当发现异常趋势时主动提醒，帮助团队及时调整。',
  true,
  true,
  '{"can_generate_reports": true, "can_create_charts": true, "can_analyze_trends": true}'::jsonb,
  '{"review_time_threshold": 24, "rework_rate_threshold": 0.15}'::jsonb
);

-- 创建另一个内置Agent: NPS洞察官
INSERT INTO agents (
  name,
  role,
  description,
  is_builtin,
  is_active,
  capabilities,
  trigger_conditions
) VALUES (
  'NPS洞察官',
  'nps_analyst',
  '监控产品的NPS分数变化，分析用户反馈趋势。当NPS出现下降或收到负面反馈集中时，及时提醒并提供改进建议。',
  true,
  true,
  '{"can_generate_reports": true, "can_analyze_sentiment": true}'::jsonb,
  '{"nps_threshold": 40, "detractor_threshold": 0.2}'::jsonb
);
```

## 📱 下一步: Flutter前端

现在后端已经完成，可以开始Flutter开发了:

### Flutter需要的端点信息

**Supabase配置**:
```dart
const supabaseUrl = 'https://dwesyojvzbltqtgtctpt.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MzA5MTQsImV4cCI6MjA4MjUwNjkxNH0.t4TBNkYp99HWBFu5kBOAgH13_7O5UADAMAptR16ENqc';
```

**Edge Function端点**:
```
POST https://dwesyojvzbltqtgtctpt.supabase.co/functions/v1/chat-stream
POST https://dwesyojvzbltqtgtctpt.supabase.co/functions/v1/agent-analysis
```

**数据库表** (Flutter可以直接查询):
- `agents` - AI员工列表
- `user_agent_subscriptions` - 订阅管理
- `conversations` - 对话列表
- `messages` - 消息历史
- `alerts` - 提醒通知

### Flutter要实现的主要功能

1. **用户认证** - 使用Supabase Auth
2. **AI员工列表** - 直接查询agents表
3. **订阅管理** - CRUD操作user_agent_subscriptions
4. **对话界面** - 调用chat-stream Edge Function (SSE)
5. **信息流** - 查询alerts表，显示AI提醒
6. **实时更新** - 使用Supabase Realtime订阅

## 🧪 测试后端

### 测试Edge Function (需要先在Supabase Dashboard创建用户)

1. 创建用户并获取JWT token
2. 创建一个conversation
3. 测试chat-stream:

```bash
curl -X POST https://dwesyojvzbltqtgtctpt.supabase.co/functions/v1/chat-stream \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "YOUR_CONVERSATION_ID",
    "message": "你好，介绍一下你自己"
  }'
```

## 📊 监控

查看Edge Functions日志:
https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/functions

查看数据库:
https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/editor
