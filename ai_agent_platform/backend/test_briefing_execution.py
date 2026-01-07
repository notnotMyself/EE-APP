#!/usr/bin/env python3
"""
测试脚本：手动触发定时任务，执行 Agent 分析并生成简报
"""
import asyncio
import sys
from uuid import UUID
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.briefing_service import briefing_service
from app.db.supabase import get_supabase_admin_client


async def test_briefing_execution():
    """测试完整的简报生成流程"""

    print("=" * 80)
    print("开始测试 Agent SDK 集成 - 简报生成流程")
    print("=" * 80)

    # 配置
    job_id = UUID("da925872-9498-4beb-8913-2c44d13d11ef")
    agent_id = UUID("a1e79944-69bf-4f06-8e05-8060bcebad30")

    task_prompt = """请执行每日研发效能分析：
1. 从Gerrit数据库获取昨日代码审查数据
2. 分析关键指标：Review耗时、返工率、代码变更量
3. 检测异常值（对比阈值）
4. 如果发现异常，准备推送简报

重点关注：
- Review中位耗时是否超过24小时
- P95耗时是否超过72小时
- 返工率是否超过15%
- 是否有模块或人员效率明显异常"""

    briefing_config = {
        "enabled": True,
        "min_importance_score": 0.6,
        "max_daily_briefings": 3
    }

    print(f"\n📋 Job ID: {job_id}")
    print(f"🤖 Agent ID: {agent_id}")
    print(f"📝 Task Prompt: {task_prompt[:100]}...")
    print(f"⚙️  Config: {briefing_config}")

    print("\n" + "=" * 80)
    print("🚀 开始执行...")
    print("=" * 80 + "\n")

    try:
        # 执行任务
        result = await briefing_service.execute_and_generate_briefing(
            db=None,  # 使用 Supabase 客户端，不需要 db session
            agent_id=agent_id,
            task_prompt=task_prompt,
            briefing_config=briefing_config,
            target_user_ids=None  # 推送给所有订阅用户
        )

        print("\n" + "=" * 80)
        print("✅ 执行完成！")
        print("=" * 80)

        # 打印结果
        print("\n📊 执行结果:")
        print("-" * 80)
        print(f"分析是否完成: {result.get('analysis_completed')}")
        print(f"简报是否生成: {result.get('briefing_generated')}")
        print(f"生成简报数量: {result.get('briefing_count', 0)}")

        if result.get('error'):
            print(f"\n❌ 错误: {result['error']}")
            return

        if not result.get('briefing_generated'):
            print(f"\nℹ️ 未生成简报原因: {result.get('reason')}")

            # 如果有分析结果，打印部分内容
            if 'analysis_result' in result:
                print("\n📝 分析结果预览:")
                print("-" * 80)
                print(result['analysis_result'][:500])
                print("\n...")
        else:
            print(f"\n✅ 简报生成成功!")
            print(f"📝 简报标题: {result.get('briefing_title')}")
            print(f"🆔 简报 IDs: {result.get('briefing_ids')}")

            # 查询生成的简报详情
            print("\n" + "=" * 80)
            print("查询简报详情...")
            print("=" * 80 + "\n")

            supabase = get_supabase_admin_client()
            for briefing_id in result.get('briefing_ids', []):
                briefing_result = supabase.table('briefings').select('*').eq('id', briefing_id).execute()
                if briefing_result.data:
                    briefing = briefing_result.data[0]
                    print(f"📋 简报 #{briefing_id[:8]}...")
                    print(f"   类型: {briefing.get('briefing_type')}")
                    print(f"   优先级: {briefing.get('priority')}")
                    print(f"   标题: {briefing.get('title')}")
                    print(f"   摘要: {briefing.get('summary')[:150]}...")
                    print(f"   影响: {briefing.get('impact')}")
                    print(f"   重要性分数: {briefing.get('importance_score')}")
                    print(f"   Actions: {len(briefing.get('actions', []))}")
                    print()

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🧪 Agent SDK 集成测试 - 简报生成")
    print()
    asyncio.run(test_briefing_execution())
    print("\n✨ 测试完成\n")
