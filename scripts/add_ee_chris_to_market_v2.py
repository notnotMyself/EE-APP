#!/usr/bin/env python3
"""
添加 design_validator 和 ee_developer 到 AI 员工市场
（根据实际表结构）
"""
from supabase import create_client, Client
import json

url = "https://dwesyojvzbltqtgtctpt.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjkzMDkxNCwiZXhwIjoyMDgyNTA2OTE0fQ.jZb1AmsokaJIVksT8it4khZzArI73xQpwq83otsboIA"

supabase: Client = create_client(url, service_key)

print("添加 EE 和 Chris 到 AI 员工市场...")
print("=" * 80)

# 要添加的 Agents（根据实际表结构）
agents_to_add = [
    {
        'role': 'design_validator',
        'name': 'Chris设计评审员',
        'description': '''产品设计稿验证和设计历史经验沉淀。使用 Claude Opus 视觉分析能力，提供交互可用性验证、视觉一致性检查和多方案对比分析。

我会关注：
• 设计是否符合可用性原则（Jakob Nielsen 5维度）
• 视觉风格是否与品牌规范一致
• 历史设计决策和成功案例
• 设计评审报告和改进建议

当你需要设计评审时，我会：
✓ 分析设计稿的可用性问题
✓ 检查与设计系统的一致性
✓ 提供可操作的改进建议
✓ 沉淀设计决策到知识库''',
        'avatar_url': None,
        'capabilities': ['视觉分析', '交互验证', '一致性检查', '方案对比', '知识库管理'],
        'data_sources': ['设计稿图片', 'Markdown 知识库'],
        'trigger_conditions': ['用户上传设计稿', '请求设计评审', '需要方案对比'],
        'is_active': True,
        'is_builtin': True,
        'visibility': 'public',
        'metadata': {
            'model': 'saas/claude-opus-4.5',
            'multimodal': True,
            'workdir': '/Users/80392083/develop/ee_app_claude/backend/agents/design_validator',
            'allowed_tools': ['Read', 'Write', 'Grep', 'Glob'],
            'skills': ['vision_analysis', 'interaction_check', 'visual_consistency', 'compare_designs', 'search_cases'],
            'max_turns': 30
        }
    },
    {
        'role': 'ee_developer',
        'name': 'EE研发员工',
        'description': '''代码修改、测试、提交的自动化执行。使用 Git 分支隔离策略，确保代码安全和质量。

我可以帮你：
• 自动化代码修改（遵循最佳实践）
• 运行测试确保质量
• 创建 feature 分支并提交 PR
• 进行基础代码审查

当你需要代码修改时，我会：
✓ 在 feature 分支上安全操作（永不直接修改 main）
✓ 修改后自动运行测试
✓ 生成规范的 commit message
✓ 创建 Pull Request 供审核

安全保证：
🔒 分支隔离：所有修改在 feature 分支
🔒 测试先行：修改后必须测试通过
🔒 敏感文件保护：拒绝访问 .env、*.key 等''',
        'avatar_url': None,
        'capabilities': ['代码修改', '自动化测试', 'Git 管理', '代码审查', 'PR 创建'],
        'data_sources': ['代码仓库', '测试结果'],
        'trigger_conditions': ['用户请求代码修改', '需要创建 PR', '需要运行测试'],
        'is_active': True,
        'is_builtin': True,
        'visibility': 'public',
        'metadata': {
            'model': 'saas/claude-opus-4.5',
            'workdir': '/Users/80392083/develop/ee_app_claude/backend/agents/ee_developer',
            'allowed_tools': ['Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob'],
            'skills': ['git_operations', 'code_review', 'test_runner'],
            'max_turns': 50,
            'security': {
                'file_access_control': True,
                'git_audit_logging': True,
                'important_file_confirmation': True
            }
        }
    }
]

# 添加或更新 Agents
for agent_data in agents_to_add:
    try:
        # 检查是否已存在
        existing = supabase.table('agents').select('id').eq('role', agent_data['role']).execute()

        if existing.data:
            # 更新现有记录
            result = supabase.table('agents').update(agent_data).eq('role', agent_data['role']).execute()
            print(f"✅ 已更新: {agent_data['name']} ({agent_data['role']})")
        else:
            # 插入新记录
            result = supabase.table('agents').insert(agent_data).execute()
            print(f"✅ 已添加: {agent_data['name']} ({agent_data['role']})")
            print(f"   ID: {result.data[0]['id']}")

    except Exception as e:
        print(f"❌ 处理 {agent_data['role']} 时出错: {e}")

# 查看最终结果
print("\n" + "=" * 80)
print("AI 员工市场当前的 Agents：\n")

all_agents = supabase.table('agents').select('id, role, name, visibility, is_active').eq('visibility', 'public').order('created_at').execute()

for i, agent in enumerate(all_agents.data, 1):
    status = "✅ 活跃" if agent['is_active'] else "⏸️  暂停"
    print(f"{i}. {agent['name']} ({agent['role']})")
    print(f"   ID: {agent['id']}")
    print(f"   状态: {status}")
    print()

print("=" * 80)
print(f"✅ 完成！共 {len(all_agents.data)} 个 Agents 在市场展示")
