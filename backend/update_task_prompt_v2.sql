-- =============================================================================
-- 更新 scheduled_jobs 表中的 task_prompt（V2 版本）
-- 使用更有价值的分析维度：时间效率损耗、分支健康度、人员贡献度等
-- =============================================================================

UPDATE scheduled_jobs
SET task_prompt = '请执行每日研发效能分析，使用 Skills 脚本获取真实数据并生成有价值的洞察。

## 分析任务

### 选项1：时间效率损耗分析（推荐，最有价值）
```bash
cd .claude/skills
echo ''{"action": "time_efficiency_loss", "days": 7, "departments": ["系统开发部", "应用开发一部", "应用开发二部", "互联通信开发部"]}'' | python3 gerrit_analysis.py
```

这个分析会告诉你：
- 人均活跃分支数（>10个说明工作分散）
- 一次性通过率（<50%需关注返工问题）
- Story拆分是否合理（1个Story对应>10个change_id可能是借单）
- 同分支多次提交的异常情况

### 选项2：直接生成简报（最快）
```bash
cd .claude/skills
echo ''{"action": "briefing", "days": 7}'' | python3 gerrit_analysis.py
```

这会直接返回 should_push、priority、title、summary 等字段。

### 选项3：综合概览
```bash
cd .claude/skills
echo ''{"action": "summary", "days": 7}'' | python3 gerrit_analysis.py
```

## 输出要求

请基于分析结果，输出以下格式的 Markdown 报告：

---
# 研发效能洞察

**日期**: {今天日期}
**分析周期**: 最近7天
**数据来源**: Gerrit数据库

## 🎯 核心发现

{用1-2句话说明最重要的发现，例如：}
- "一次性通过率仅33.9%，团队返工成本较高"
- "人均活跃分支25.9个，工作过于分散"
- "发现412个Story对应超过10个change_id，可能存在借单问题"

## 📊 关键指标

| 指标 | 数值 | 状态 |
|------|------|------|
| 一次性通过率 | X% | ✅正常/⚠️需关注 |
| 人均活跃分支 | X个 | ✅正常/⚠️过多 |
| 理想Story比例 | X% | ✅正常/⚠️偏低 |

## 💡 洞察与建议

{基于数据给出2-3条具体可行的建议}

1. **{问题1}**: {具体建议}
2. **{问题2}**: {具体建议}

---

**重要提示**：
1. 优先使用 `time_efficiency_loss` 或 `briefing` action，这些是最有价值的分析
2. 如果数据库连接失败，请明确说明
3. 关注异常数据，不要只报告正常情况
4. 报告要有洞察价值，不是简单罗列数字'
WHERE job_type = 'daily_analysis'
  AND job_name = 'daily_efficiency_analysis';

-- 验证更新
SELECT
    job_name,
    schedule_type,
    cron_expression,
    LENGTH(task_prompt) as prompt_length,
    LEFT(task_prompt, 200) || '...' as prompt_preview,
    is_active
FROM scheduled_jobs
WHERE job_type = 'daily_analysis';

