# 简报生成测试方案

## 一、问题分析

### 当前配置状态
- ✅ scheduled_jobs 表已设计（含 task_prompt 字段）
- ✅ briefing_service 已实现（AI二次判断机制）
- ⚠️ **task_prompt 缺少明确的输出格式要求**

### 问题：AI 员工不知道返回什么格式

**当前 task_prompt**（第224-234行）：
```
请执行每日研发效能分析：
1. 从Gerrit数据库获取昨日代码审查数据
2. 分析关键指标：Review耗时、返工率、代码变更量
3. 检测异常值（对比阈值）
4. 如果发现异常，准备推送简报

重点关注：
- Review中位耗时是否超过24小时
- P95耗时是否超过72小时
- 返工率是否超过15%
- 是否有模块或人员效率明显异常
```

**缺失**：没有告诉 AI 应该返回什么格式的数据！

---

## 二、改进后的 task_prompt

### 方案A：结构化分析报告（推荐）

```
请执行每日研发效能分析并生成结构化报告：

## 第一步：数据采集
使用 gerrit_analysis skill 获取昨日（过去24小时）的代码审查数据：
- 代码变更数量
- Review 耗时分布（中位数、P95）
- 返工率（revision > 1 的比例）
- 各模块/团队的效率数据

## 第二步：异常检测
对比以下阈值，检测异常：
- ⚠️ Review中位耗时 > 24小时
- 🔴 Review P95耗时 > 72小时
- ⚠️ 返工率 > 15%
- ⚠️ 某模块效率下降 > 30%

## 第三步：生成分析报告

请按以下 Markdown 格式输出：

---
# 研发效能每日分析报告

**日期**: {date}
**数据范围**: 过去24小时

## 核心指标摘要
| 指标 | 数值 | 阈值 | 状态 |
|------|------|------|------|
| Review中位耗时 | X小时 | 24小时 | ✅/⚠️ |
| Review P95耗时 | X小时 | 72小时 | ✅/⚠️ |
| 返工率 | X% | 15% | ✅/⚠️ |
| 代码变更数 | X个 | - | - |

## 异常发现（如有）
### 🔴 Review积压严重
- **现象**: Review P95耗时达到 {value} 小时，超过阈值 {threshold} 小时
- **影响范围**: 涉及 {count} 个PR，主要在 {modules} 模块
- **可能原因**: Reviewer人手不足 / 节假日影响 / 复杂变更较多

### ⚠️ 返工率上升
- **现象**: 返工率达到 {value}%，超过阈值 {threshold}%
- **影响范围**: 主要集中在 {author/module}
- **可能原因**: 需求不清晰 / 代码质量问题 / Review标准变化

## 详细数据
（可选）提供按模块/人员维度的详细统计

## 改进建议
- 如发现异常，提供1-3条具体可行的改进建议
- 如一切正常，说明"各项指标正常，无异常"
---

**重要**：如果各项指标都在正常范围内（没有超过阈值），请在报告开头明确说明"✅ 本次分析未发现异常"。
```

### 方案B：JSON结构化输出（备选）

```
请执行每日研发效能分析，并以 JSON 格式输出：

{
  "date": "2026-01-06",
  "data_range": "过去24小时",
  "summary": {
    "review_median_hours": 18.5,
    "review_p95_hours": 48.0,
    "rework_rate": 12.3,
    "total_changes": 45
  },
  "anomalies": [
    {
      "type": "REVIEW_TIME_HIGH",
      "severity": "WARNING",
      "metric": "review_p95_hours",
      "value": 48.0,
      "threshold": 72.0,
      "message": "P95耗时接近阈值，需关注"
    }
  ],
  "has_anomaly": true,
  "recommendations": [
    "建议增加 Reviewer 人手，避免积压"
  ]
}
```

---

## 三、测试步骤

### Step 1: 准备测试环境

#### 1.1 确认数据库已初始化
```bash
# 检查 scheduled_jobs 表是否存在
psql $DATABASE_URL -c "SELECT * FROM scheduled_jobs LIMIT 1;"

# 如果不存在，执行迁移
cd supabase
supabase db push
```

#### 1.2 确认 Agent 记录存在
```bash
psql $DATABASE_URL -c "SELECT id, name, role FROM agents WHERE role = 'dev_efficiency_analyst';"
```

#### 1.3 准备测试用户订阅
```bash
# 确保至少有一个用户订阅了研发效能分析官
psql $DATABASE_URL -c "
INSERT INTO user_agent_subscriptions (user_id, agent_id, is_active)
SELECT
    (SELECT id FROM auth.users LIMIT 1),
    (SELECT id FROM agents WHERE role = 'dev_efficiency_analyst'),
    TRUE
ON CONFLICT DO NOTHING;
"
```

---

### Step 2: 更新 task_prompt（重要！）

#### 方式1：通过数据库直接更新
```bash
psql $DATABASE_URL <<EOF
UPDATE scheduled_jobs
SET task_prompt = '请执行每日研发效能分析并生成结构化报告：

## 第一步：数据采集
使用 gerrit_analysis skill 获取昨日（过去24小时）的代码审查数据。

## 第二步：异常检测
对比以下阈值：
- ⚠️ Review中位耗时 > 24小时
- 🔴 Review P95耗时 > 72小时
- ⚠️ 返工率 > 15%

## 第三步：生成分析报告
请按以下格式输出：

# 研发效能每日分析

**日期**: {今天日期}
**数据范围**: 过去24小时

## 核心指标
- Review中位耗时: X小时 (阈值24h) ✅/⚠️
- Review P95耗时: X小时 (阈值72h) ✅/⚠️
- 返工率: X% (阈值15%) ✅/⚠️

## 异常发现
{如果有异常，详细描述；如果没有，说明"✅ 各项指标正常"}

## 改进建议
{仅在发现异常时提供具体建议}

**重要**：如果一切正常，请明确说明"未发现异常，无需推送简报"。'
WHERE job_type = 'daily_analysis';
EOF
```

#### 方式2：通过API更新（推荐）
```bash
# 获取 job_id
JOB_ID=$(curl -s http://localhost:8000/api/v1/scheduled-jobs \
  -H "Authorization: Bearer $TOKEN" | jq -r '.items[0].id')

# 更新 task_prompt
curl -X PATCH http://localhost:8000/api/v1/scheduled-jobs/$JOB_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_prompt": "（上述改进后的prompt）"
  }'
```

---

### Step 3: 手动触发测试

#### 3.1 方式1：通过 API 手动触发（推荐）
```bash
# 启动后端服务
cd ai_agent_platform/backend
python main.py

# 获取 scheduled_jobs 列表
curl http://localhost:8000/api/v1/scheduled-jobs \
  -H "Authorization: Bearer YOUR_TOKEN" | jq

# 手动触发任务（dry_run=false 表示真实执行）
curl -X POST http://localhost:8000/api/v1/scheduled-jobs/{job_id}/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

#### 3.2 方式2：通过 Python 脚本测试
创建 `test_briefing_flow.py`：
```python
import asyncio
from app.services.briefing_service import BriefingService
from app.db.supabase import get_supabase_admin_client
from uuid import UUID

async def test_briefing_generation():
    # 1. 获取 Agent 信息
    supabase = get_supabase_admin_client()
    agent = supabase.table('agents').select('*').eq(
        'role', 'dev_efficiency_analyst'
    ).execute().data[0]

    # 2. 准备 task_prompt（使用改进后的版本）
    task_prompt = """
    请执行每日研发效能分析并生成结构化报告：
    （完整的改进后prompt）
    """

    # 3. 执行简报生成
    service = BriefingService()
    result = await service.execute_and_generate_briefing(
        db=None,  # 使用 Supabase client
        agent_id=UUID(agent['id']),
        task_prompt=task_prompt,
        briefing_config={
            "enabled": True,
            "min_importance_score": 0.6,
            "max_daily_briefings": 3
        }
    )

    print("执行结果:")
    print(result)

    # 4. 检查数据库中的简报记录
    if result.get('briefing_generated'):
        briefings = supabase.table('briefings').select('*').in_(
            'id', result['briefing_ids']
        ).execute()
        print("\n生成的简报:")
        for b in briefings.data:
            print(f"  - {b['title']}")
            print(f"    优先级: {b['priority']}, 类型: {b['briefing_type']}")
            print(f"    重要性: {b['importance_score']}")

if __name__ == '__main__':
    asyncio.run(test_briefing_generation())
```

运行测试：
```bash
cd ai_agent_platform/backend
python test_briefing_flow.py
```

---

### Step 4: 验证完整流程

#### 4.1 后端验证

**检查日志输出**：
```bash
# 查看后端日志，应该看到：
✅ Scheduler service started
✅ Executing scheduled job: daily_efficiency_analysis
✅ Agent analysis completed
✅ AI decision: should_push=true, importance_score=0.85
✅ Generated 2 briefings for subscribed users
```

**检查数据库记录**：
```bash
# 查看简报记录
psql $DATABASE_URL -c "
SELECT
    id,
    briefing_type,
    priority,
    title,
    importance_score,
    created_at
FROM briefings
ORDER BY created_at DESC
LIMIT 5;
"

# 查看任务执行记录
psql $DATABASE_URL -c "
SELECT
    job_name,
    last_run_at,
    next_run_at,
    run_count,
    success_count,
    failure_count,
    last_result->>'briefing_count' as briefing_count
FROM scheduled_jobs
WHERE job_type = 'daily_analysis';
"
```

#### 4.2 前端验证

**启动 Flutter 应用**：
```bash
cd ai_agent_app
flutter run -d chrome
```

**测试步骤**：
1. 登录应用
2. 进入信息流页面（/feed）
3. 下拉刷新
4. 验证：
   - ✅ 简报卡片显示
   - ✅ 优先级颜色正确（P0红色/P1橙色/P2蓝色）
   - ✅ 未读标记显示
   - ✅ 点击卡片跳转到详情页
   - ✅ 点击"深入分析"启动对话
   - ✅ 对话携带简报上下文

---

### Step 5: 测试各种场景

#### 场景1：正常数据（不应推送）
```python
# 修改 Gerrit 数据或 mock 数据，确保所有指标正常
# 期望：AI 判断 should_push = false
# 结果：数据库中没有新简报
```

#### 场景2：轻微异常（P2 普通）
```python
# Review 中位耗时稍超阈值（26小时，阈值24小时）
# 期望：should_push = true, priority = "P2", importance_score ≈ 0.65
# 结果：生成简报，蓝色边框
```

#### 场景3：严重异常（P0 紧急）
```python
# Review P95耗时严重超标（120小时，阈值72小时）
# 期望：should_push = true, priority = "P0", importance_score ≈ 0.9
# 结果：生成简报，红色边框，标题突出
```

#### 场景4：超过每日配额
```python
# 同一天触发4次任务，期望第4次被拒绝
# 期望：第4次返回 reason = "Daily briefing quota exceeded"
# 结果：数据库中该Agent当天最多3条简报
```

---

## 四、常见问题排查

### 问题1：Gerrit 数据库连接失败
```bash
# 测试连接
cd backend/agents/dev_efficiency_analyst
python -c "
from gerrit_analysis import get_db_connection
try:
    conn = get_db_connection()
    print('✅ 连接成功')
    conn.close()
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

**解决方案**：
- 检查网络（10.52.61.119:33067 是否可达）
- 使用 mock 数据测试（data/mock_gerrit_data.json）

### 问题2：AI 判断逻辑不准
```bash
# 查看 AI 的判断日志
tail -f logs/briefing_service.log | grep "AI decision"
```

**调优方向**：
- 调整 `min_importance_score` 阈值（默认0.6）
- 改进 BRIEFING_DECISION_PROMPT 的措辞
- 提供更多示例（few-shot learning）

### 问题3：简报未在前端显示
```bash
# 检查 RLS 策略
psql $DATABASE_URL -c "
SELECT * FROM briefings
WHERE user_id = '{your_user_id}'
ORDER BY created_at DESC;
"
```

**解决方案**：
- 确认用户已订阅 Agent
- 检查 RLS 策略是否正确
- 前端手动刷新

---

## 五、自动化测试脚本

### 端到端测试脚本
```bash
#!/bin/bash
# test_e2e_briefing.sh

set -e

echo "🧪 开始端到端简报生成测试"

# 1. 启动后端
echo "📡 启动后端服务..."
cd ai_agent_platform/backend
python main.py &
BACKEND_PID=$!
sleep 5

# 2. 获取 Token
echo "🔑 获取认证 Token..."
TOKEN=$(curl -s http://localhost:8000/api/v1/auth/login \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# 3. 手动触发任务
echo "▶️  触发定时任务..."
JOB_ID=$(curl -s http://localhost:8000/api/v1/scheduled-jobs \
  -H "Authorization: Bearer $TOKEN" | jq -r '.items[0].id')

RESULT=$(curl -s -X POST \
  http://localhost:8000/api/v1/scheduled-jobs/$JOB_ID/run \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"dry_run":false}')

echo "✅ 任务执行结果:"
echo $RESULT | jq

# 4. 检查简报
echo "📋 检查生成的简报..."
sleep 3
BRIEFINGS=$(curl -s http://localhost:8000/api/v1/briefings \
  -H "Authorization: Bearer $TOKEN")

BRIEFING_COUNT=$(echo $BRIEFINGS | jq '.items | length')
echo "✅ 共生成 $BRIEFING_COUNT 条简报"

if [ $BRIEFING_COUNT -gt 0 ]; then
    echo "✅ 测试通过！"
    echo $BRIEFINGS | jq '.items[] | {title, priority, importance_score}'
else
    echo "⚠️  未生成简报（可能数据正常或配额已满）"
fi

# 5. 清理
kill $BACKEND_PID
echo "🎉 测试完成"
```

---

## 六、监控和调优

### 监控指标
```sql
-- 简报生成统计
SELECT
    date_trunc('day', created_at) as date,
    briefing_type,
    priority,
    COUNT(*) as count,
    AVG(importance_score) as avg_score
FROM briefings
GROUP BY 1, 2, 3
ORDER BY 1 DESC;

-- 任务执行统计
SELECT
    job_name,
    run_count,
    success_count,
    failure_count,
    (success_count::float / NULLIF(run_count, 0)) as success_rate
FROM scheduled_jobs;
```

### 调优建议
1. **importance_score 阈值**：根据实际推送质量调整（0.5-0.7）
2. **max_daily_briefings**：根据用户反馈调整（2-5条）
3. **task_prompt**：持续优化，提供更明确的指引
4. **Cron 表达式**：根据用户活跃时间调整（早9点 vs 晚8点）

---

## 总结

**测试流程**：
1. ✅ 改进 task_prompt（明确输出格式）
2. ✅ 手动触发测试（API 或 Python 脚本）
3. ✅ 验证后端日志和数据库记录
4. ✅ 验证前端显示和交互
5. ✅ 测试多种场景（正常、异常、配额）

**关键点**：
- task_prompt 必须告诉 AI 输出什么格式
- 使用结构化 Markdown 或 JSON 输出
- 明确"无异常时不推送"的逻辑
- 测试完整链路（定时→分析→判断→推送→显示）
