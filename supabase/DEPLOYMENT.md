# Supabase Edge Functions 部署指南

## Edge Functions 说明

我们创建了2个Edge Functions来处理核心AI功能：

### 1. chat-stream (AI对话)
- **路径**: `/functions/v1/chat-stream`
- **功能**: 处理用户与AI员工的对话，支持SSE流式响应
- **认证**: 需要用户JWT token
- **请求示例**:
```bash
curl -X POST https://your-project.supabase.co/functions/v1/chat-stream \
  -H "Authorization: Bearer USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "uuid",
    "message": "帮我分析一下最近的代码review情况"
  }'
```

### 2. agent-analysis (定时分析)
- **路径**: `/functions/v1/agent-analysis`
- **功能**: 定时执行AI员工的数据分析，生成异常提醒
- **触发**: Supabase Cron (每小时)
- **认证**: Cron secret或anon key

## 部署步骤

### 1. 应用最新的数据库迁移
```bash
cd /Users/80392083/develop/ee_app_claude
supabase db push --linked
```

### 2. 配置环境变量
在Supabase Dashboard设置Edge Functions的环境变量：

项目设置 -> Edge Functions -> Configuration

添加以下secrets:
```
CLAUDE_API_KEY=your_claude_api_key_here
CRON_SECRET=your_random_secret_for_cron_jobs
```

### 3. 部署Edge Functions
```bash
# 部署chat-stream
supabase functions deploy chat-stream

# 部署agent-analysis
supabase functions deploy agent-analysis
```

### 4. 设置定时任务
在Supabase SQL Editor中执行：

```sql
-- 启用pg_cron扩展（如果还没启用）
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 创建每小时执行的定时任务
SELECT cron.schedule(
  'agent-analysis-hourly',
  '0 * * * *', -- 每小时的第0分钟执行
  $$
  SELECT
    net.http_post(
      url:='https://dwesyojvzbltqtgtctpt.supabase.co/functions/v1/agent-analysis',
      headers:='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_ANON_KEY"}'::jsonb,
      body:='{}'::jsonb
    ) AS request_id;
  $$
);

-- 查看已创建的定时任务
SELECT * FROM cron.job;
```

**注意**: 将上面的URL和Authorization替换成你的实际值。

### 5. 测试Edge Functions

测试chat-stream (需要先创建用户和conversation):
```bash
# 获取JWT token (登录后)
TOKEN="eyJ..."

# 调用chat-stream
curl -X POST https://dwesyojvzbltqtgtctpt.supabase.co/functions/v1/chat-stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "your-conversation-id",
    "message": "你好"
  }'
```

测试agent-analysis:
```bash
curl -X POST https://dwesyojvzbltqtgtctpt.supabase.co/functions/v1/agent-analysis \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json"
```

## 本地开发

启动本地Supabase:
```bash
supabase start
```

运行Edge Function本地调试:
```bash
supabase functions serve chat-stream --env-file ./supabase/.env.local
```

创建 `.env.local` 文件:
```
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your_local_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_local_service_role_key
CLAUDE_API_KEY=your_claude_api_key
CRON_SECRET=local_test_secret
```

## 监控和日志

在Supabase Dashboard查看:
- Edge Functions -> Logs: 查看函数执行日志
- Edge Functions -> Metrics: 查看调用次数、错误率等

## 常见问题

### Q: Edge Function超时怎么办?
A: 默认超时是150秒。如果分析任务太长，考虑：
   1. 拆分成更小的批次
   2. 使用Supabase Storage + 后台任务

### Q: Claude API配额限制?
A: 监控使用量，考虑：
   1. 减少定时任务频率
   2. 添加缓存机制
   3. 只对关键异常触发分析

### Q: 如何调试?
A: 使用 `console.log()` 输出到Edge Function日志
