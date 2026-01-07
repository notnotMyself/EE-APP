"""
简报生成流程快速测试脚本

用法：
    python test_briefing_quick.py

功能：
    1. 手动触发一次简报生成任务
    2. 查看生成结果
    3. 验证数据库记录
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_agent_platform/backend'))

from app.services.briefing_service import BriefingService
from app.db.supabase import get_supabase_admin_client
from uuid import UUID
import json


# 改进后的 task_prompt（明确输出格式）
IMPROVED_TASK_PROMPT = """
请执行每日研发效能分析并生成结构化报告：

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
- 后续系统会根据你的分析判断是否推送简报给用户
"""


async def main():
    print("=" * 60)
    print("🧪 简报生成流程测试")
    print("=" * 60)

    # 1. 获取 Agent 信息
    print("\n📌 Step 1: 获取 Agent 信息...")
    supabase = get_supabase_admin_client()

    agent_result = supabase.table('agents').select('*').eq(
        'role', 'dev_efficiency_analyst'
    ).execute()

    if not agent_result.data:
        print("❌ 未找到 dev_efficiency_analyst Agent")
        print("请先执行数据库迁移：supabase db push")
        return

    agent = agent_result.data[0]
    print(f"✅ 找到 Agent: {agent['name']} (ID: {agent['id']})")

    # 2. 检查订阅用户
    print("\n📌 Step 2: 检查订阅用户...")
    subscriptions = supabase.table('user_agent_subscriptions').select(
        'user_id'
    ).eq('agent_id', agent['id']).eq('is_active', True).execute()

    if not subscriptions.data:
        print("⚠️  没有用户订阅此 Agent")
        print("提示：即使没有订阅用户，也会执行分析，只是不会创建简报记录")
    else:
        print(f"✅ 找到 {len(subscriptions.data)} 个订阅用户")

    # 3. 执行简报生成
    print("\n📌 Step 3: 执行简报生成...")
    print("使用改进后的 task_prompt（包含明确的输出格式要求）\n")

    service = BriefingService()

    try:
        result = await service.execute_and_generate_briefing(
            db=None,  # 使用 Supabase client
            agent_id=UUID(agent['id']),
            task_prompt=IMPROVED_TASK_PROMPT,
            briefing_config={
                "enabled": True,
                "min_importance_score": 0.6,
                "max_daily_briefings": 3
            }
        )

        print("\n" + "=" * 60)
        print("✅ 执行完成！")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 4. 检查生成的简报
        if result.get('briefing_generated') and result.get('briefing_ids'):
            print("\n📌 Step 4: 查看生成的简报...")

            briefings = supabase.table('briefings').select(
                'id, briefing_type, priority, title, summary, importance_score, created_at'
            ).in_('id', result['briefing_ids']).execute()

            for i, briefing in enumerate(briefings.data, 1):
                print(f"\n简报 {i}:")
                print(f"  📝 标题: {briefing['title']}")
                print(f"  🏷️  类型: {briefing['briefing_type']}")
                print(f"  ⚠️  优先级: {briefing['priority']}")
                print(f"  📊 重要性分数: {briefing['importance_score']}")
                print(f"  📄 摘要: {briefing['summary'][:100]}...")
                print(f"  🕐 创建时间: {briefing['created_at']}")

        elif not result.get('briefing_generated'):
            print("\n📌 未生成简报")
            reason = result.get('reason', '未知原因')
            print(f"原因: {reason}")

            if "importance score" in reason.lower():
                print("\n💡 提示: AI 判断该分析结果不够重要，未达到推送阈值")
            elif "quota" in reason.lower():
                print("\n💡 提示: 今天已达到简报配额上限（3条）")
            elif "正常" in reason or "no anomaly" in reason.lower():
                print("\n💡 提示: 数据分析结果正常，符合'信息流铁律'不推送")

        # 5. 查看今日简报统计
        print("\n📌 Step 5: 今日简报统计...")
        from datetime import date
        today = date.today().isoformat()

        today_briefings = supabase.table('briefings').select(
            'id', count='exact'
        ).eq('agent_id', agent['id']).gte(
            'created_at', f"{today}T00:00:00"
        ).execute()

        count = today_briefings.count or 0
        print(f"✅ 今日已生成 {count} 条简报（配额: 3条）")

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("提示：请确保已启动 Supabase 并配置环境变量")
    print("      SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY\n")

    asyncio.run(main())
