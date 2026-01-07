-- 更新 scheduled_jobs 表中的 task_prompt
-- 使用改进后的 prompt，明确告诉 AI 应该输出什么格式

UPDATE scheduled_jobs
SET task_prompt = '请执行每日研发效能分析并生成结构化报告：

## 第一步：数据采集
使用 gerrit_analysis skill 获取昨日（过去24小时）的代码审查数据：
- 代码变更数量
- Review 耗时分布（中位数、P95）
- 返工率（revision > 1 的比例）
- 各模块/团队的效率数据

如果无法连接真实 Gerrit 数据库，请使用 data/mock_gerrit_data.json 中的模拟数据。

## 第二步：异常检测
对比以下阈值，检测异常：
- ⚠️ Review中位耗时 > 24小时
- 🔴 Review P95耗时 > 72小时
- ⚠️ 返工率 > 15%
- ⚠️ 某模块效率下降 > 30%

## 第三步：生成分析报告

请按以下 Markdown 格式输出：

---
# 研发效能每日分析

**日期**: {今天日期}
**数据范围**: 过去24小时

## 核心指标摘要
| 指标 | 数值 | 阈值 | 状态 |
|------|------|------|------|
| Review中位耗时 | X小时 | 24小时 | ✅/⚠️ |
| Review P95耗时 | X小时 | 72小时 | ✅/⚠️ |
| 返工率 | X% | 15% | ✅/⚠️ |
| 代码变更数 | X个 | - | - |

## 异常发现
{如果所有指标正常，请明确说明"✅ 各项指标正常，无异常发现"。}
{如果有异常，详细描述每个异常的现象、影响和可能原因。}

### 示例（有异常时）：
🔴 **Review积压严重**
- 现象: Review P95耗时达到 {value} 小时，超过阈值 {threshold} 小时
- 影响: 涉及 {count} 个PR，可能影响本周版本发布
- 建议: 增加 Reviewer 人手或调整 PR 优先级

## 改进建议
{仅在发现异常时提供1-3条具体可行的改进建议}
---

**重要**：
- 如果一切正常，请在"异常发现"部分明确说明"无异常"
- 后续系统会根据你的分析判断是否推送简报给用户'
WHERE job_type = 'daily_analysis'
  AND job_name = 'daily_efficiency_analysis';

-- 验证更新
SELECT
    job_name,
    schedule_type,
    cron_expression,
    LENGTH(task_prompt) as prompt_length,
    LEFT(task_prompt, 100) || '...' as prompt_preview,
    is_active
FROM scheduled_jobs
WHERE job_type = 'daily_analysis';
