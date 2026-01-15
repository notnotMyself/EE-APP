#!/usr/bin/env python3
"""
添加 design_validator 和 ee_developer 到 AI 员工市场
"""
import os
from supabase import create_client, Client

url = "https://dwesyojvzbltqtgtctpt.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjkzMDkxNCwiZXhwIjoyMDgyNTA2OTE0fQ.jZb1AmsokaJIVksT8it4khZzArI73xQpwq83otsboIA"

supabase: Client = create_client(url, service_key)

print("添加 EE 和 Chris 到 AI 员工市场...")
print("=" * 80)

# 要添加的 Agents
agents_to_add = [
    {
        'role': 'design_validator',
        'name': 'Chris设计评审员',
        'description': '产品设计稿验证和设计历史经验沉淀。使用 Claude Opus 视觉分析能力，提供交互可用性验证、视觉一致性检查和多方案对比分析。\n\n我会关注：\n• 设计是否符合可用性原则（Jakob Nielsen 5维度）\n• 视觉风格是否与品牌规范一致\n• 历史设计决策和成功案例\n• 设计评审报告和改进建议\n\n当你需要设计评审时，我会：\n✓ 分析设计稿的可用性问题\n✓ 检查与设计系统的一致性\n✓ 提供可操作的改进建议\n✓ 沉淀设计决策到知识库',
        'model': 'saas/claude-opus-4.5',
        'workdir': '/Users/80392083/develop/ee_app_claude/backend/agents/design_validator',
        'allowed_tools': ['Read', 'Write', 'Grep', 'Glob'],
        'visibility': 'public'
    },
    {
        'role': 'ee_developer',
        'name': 'EE研发员工',
        'description': '代码修改、测试、提交的自动化执行。使用 Git 分支隔离策略，确保代码安全和质量。\n\n我可以帮你：\n• 自动化代码修改（遵循最佳实践）\n• 运行测试确保质量\n• 创建 feature 分支并提交 PR\n• 进行基础代码审查\n\n当你需要代码修改时，我会：\n✓ 在 feature 分支上安全操作（永不直接修改 main）\n✓ 修改后自动运行测试\n✓ 生成规范的 commit message\n✓ 创建 Pull Request 供审核\n\n安全保证：\n🔒 分支隔离：所有修改在 feature 分支\n🔒 测试先行：修改后必须测试通过\n🔒 敏感文件保护：拒绝访问 .env、*.key 等',
        'model': 'saas/claude-opus-4.5',
        'workdir': '/Users/80392083/develop/ee_app_claude/backend/agents/ee_developer',
        'allowed_tools': ['Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob'],
        'visibility': 'public'
    }
]

# 添加或更新 Agents
for agent_data in agents_to_add:
    try:
        # 检查是否已存在
        existing = supabase.table('agents').select('*').eq('role', agent_data['role']).execute()

        if existing.data:
            # 更新现有记录
            result = supabase.table('agents').update(agent_data).eq('role', agent_data['role']).execute()
            print(f"✅ 已更新: {agent_data['name']} ({agent_data['role']})")
        else:
            # 插入新记录
            result = supabase.table('agents').insert(agent_data).execute()
            print(f"✅ 已添加: {agent_data['name']} ({agent_data['role']})")

    except Exception as e:
        print(f"❌ 处理 {agent_data['role']} 时出错: {e}")

# 查看最终结果
print("\n" + "=" * 80)
print("AI 员工市场当前的 Agents：\n")

all_agents = supabase.table('agents').select('role, name, visibility, model').eq('visibility', 'public').order('created_at').execute()

for i, agent in enumerate(all_agents.data, 1):
    print(f"{i}. {agent['name']} ({agent['role']})")
    print(f"   模型: {agent['model']}")
    print(f"   状态: {'✅ 市场展示' if agent['visibility'] == 'public' else '🔒 隐藏'}")
    print()

print("=" * 80)
print(f"✅ 完成！共 {len(all_agents.data)} 个 Agents 在市场展示")
