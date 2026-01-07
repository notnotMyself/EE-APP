"""
插入测试简报数据到数据库

用于测试信息流功能
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.supabase import get_supabase_admin_client
import uuid
from datetime import datetime


def insert_test_briefings():
    """插入多条测试简报"""
    supabase = get_supabase_admin_client()

    # 1. 获取第一个 Agent（研发效能分析官）
    agents = supabase.table('agents').select('id, name, role').limit(1).execute()
    if not agents.data:
        print("❌ 没有找到 Agent，请先创建 Agent")
        return

    agent = agents.data[0]
    print(f"✅ 找到 Agent: {agent['name']} ({agent['role']})")

    # 2. 获取第一个用户
    users = supabase.table('users').select('id, email').limit(1).execute()
    if not users.data:
        print("❌ 没有找到用户，请先注册用户")
        return

    user = users.data[0]
    print(f"✅ 找到用户: {user.get('email', 'unknown')}")

    # 3. 准备测试简报数据
    test_briefings = [
        {
            'id': str(uuid.uuid4()),
            'agent_id': agent['id'],
            'user_id': user['id'],
            'briefing_type': 'alert',
            'priority': 'P1',
            'title': 'Review积压严重，5个PR等待超48小时',
            'summary': '发现当前有5个代码审查请求等待超过48小时，影响开发效率。建议立即处理积压，或安排专人负责代码审查。',
            'impact': '开发流程受阻，可能延迟版本发布',
            'actions': [
                {"label": "查看详情", "action": "view_report"},
                {"label": "深入分析", "action": "start_conversation", "prompt": "请帮我详细分析这些积压的PR，包括阻塞原因和改进建议"}
            ],
            'importance_score': 0.85,
            'status': 'new',
            'context_data': {
                'analysis_result': '通过分析最近7天的代码审查数据，发现有5个PR等待时间超过48小时...',
                'generated_at': datetime.utcnow().isoformat()
            }
        },
        {
            'id': str(uuid.uuid4()),
            'agent_id': agent['id'],
            'user_id': user['id'],
            'briefing_type': 'insight',
            'priority': 'P2',
            'title': '返工率连续上升，已达18%',
            'summary': '过去3周返工率持续上升，从12%增长到18%。主要集中在后端模块，建议加强代码审查质量和单元测试覆盖率。',
            'impact': '研发效率下降，每次迭代需要更多时间修复问题',
            'actions': [
                {"label": "查看趋势", "action": "view_report"},
                {"label": "分析原因", "action": "start_conversation", "prompt": "请分析返工率上升的根本原因"}
            ],
            'importance_score': 0.75,
            'status': 'new',
            'context_data': {
                'analysis_result': '返工率定义为需要重新提交的代码审查占总审查数的比例...',
                'generated_at': datetime.utcnow().isoformat()
            }
        },
        {
            'id': str(uuid.uuid4()),
            'agent_id': agent['id'],
            'user_id': user['id'],
            'briefing_type': 'action',
            'priority': 'P2',
            'title': 'platform模块效率下降30%，建议关注',
            'summary': 'platform模块的代码审查周期从平均16小时增加到24小时，影响因素包括代码复杂度上升和审查人员不足。建议增加审查人员或拆分大型PR。',
            'impact': '核心模块开发速度放缓',
            'actions': [
                {"label": "查看详情", "action": "view_report"},
                {"label": "制定方案", "action": "start_conversation", "prompt": "请帮我制定改进platform模块效率的具体方案"}
            ],
            'importance_score': 0.70,
            'status': 'new',
            'context_data': {
                'analysis_result': '对比过去30天数据，platform模块效率显著下降...',
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    ]

    # 4. 插入简报
    print(f"\n正在插入 {len(test_briefings)} 条测试简报...")

    try:
        result = supabase.table('briefings').insert(test_briefings).execute()
        print(f"✅ 成功插入 {len(result.data)} 条简报！")

        # 显示插入的简报
        print("\n📋 已创建的简报：")
        for i, briefing in enumerate(result.data, 1):
            print(f"\n{i}. [{briefing['priority']}] {briefing['title']}")
            print(f"   类型: {briefing['briefing_type']}")
            print(f"   重要性: {briefing['importance_score']}")

        print(f"\n✨ 现在刷新前端 Feed 页面，即可看到这些简报！")

    except Exception as e:
        print(f"❌ 插入失败: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 测试简报数据插入脚本")
    print("=" * 60)
    insert_test_briefings()
    print("=" * 60)
