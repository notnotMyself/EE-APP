#!/usr/bin/env python3
"""
清理不需要的 Agents 并确保正确的 Agents 配置
"""
import os
from supabase import create_client, Client

url = "https://dwesyojvzbltqtgtctpt.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjkzMDkxNCwiZXhwIjoyMDgyNTA2OTE0fQ.jZb1AmsokaJIVksT8it4khZzArI73xQpwq83otsboIA"

supabase: Client = create_client(url, service_key)

print("开始清理 AI 员工市场...")
print("=" * 80)

# 需要删除的 Agent roles
agents_to_delete = [
    'nps_analyst',          # NPS洞察官
    'competitor_analyst',   # 竞品情报官
    'sentiment_monitor',    # 舆情哨兵
    'operations_assistant'  # AI营运助理
]

# 需要添加的 Agent（如果不存在）
agents_to_keep = [
    {
        'role': 'ai_news_crawler',
        'name': 'AI资讯追踪官',
        'description': '每日追踪AI行业重要资讯，包括产业动态、技术发布、融资消息等。帮助你第一时间掌握AI领域的关键信息。',
        'visibility': 'public'
    },
    {
        'role': 'dev_efficiency_analyst',
        'name': '研发效能分析官',
        'description': '持续监控团队的研发效能数据，包括代码Review耗时、返工率、需求交付周期等关键指标。当发现异常趋势时主动提醒。',
        'visibility': 'public'
    }
]

# 不在市场展示的 Agent（设置为 private 或删除）
agents_to_hide = [
    'design_validator',  # Chris设计评审员 - 工具类，不在市场展示
    'ee_developer'       # EE研发员工 - 系统级，不在市场展示
]

# 1. 删除不需要的 Agents
print("\n步骤 1: 删除不需要的 Agents")
print("-" * 80)
for role in agents_to_delete:
    try:
        # 先删除相关的订阅记录
        supabase.table('user_agent_subscriptions').delete().eq('agent_id',
            supabase.table('agents').select('id').eq('role', role).execute().data[0]['id']
        ).execute()

        # 删除 Agent
        result = supabase.table('agents').delete().eq('role', role).execute()
        print(f"  ✅ 已删除: {role}")
    except Exception as e:
        print(f"  ⚠️  删除 {role} 时出错: {e}")

# 2. 确保需要的 Agents 存在且配置正确
print("\n步骤 2: 确保需要的 Agents 配置正确")
print("-" * 80)
for agent_data in agents_to_keep:
    try:
        # 检查是否存在
        existing = supabase.table('agents').select('*').eq('role', agent_data['role']).execute()

        if existing.data:
            # 更新现有 Agent
            result = supabase.table('agents').update({
                'name': agent_data['name'],
                'description': agent_data['description'],
                'visibility': agent_data['visibility']
            }).eq('role', agent_data['role']).execute()
            print(f"  ✅ 已更新: {agent_data['name']} ({agent_data['role']})")
        else:
            print(f"  ℹ️  {agent_data['role']} 不在数据库中（从文件系统加载）")
    except Exception as e:
        print(f"  ⚠️  处理 {agent_data['role']} 时出错: {e}")

# 3. 隐藏不需要在市场展示的 Agents
print("\n步骤 3: 隐藏工具类/系统级 Agents")
print("-" * 80)
for role in agents_to_hide:
    try:
        existing = supabase.table('agents').select('*').eq('role', role).execute()
        if existing.data:
            # 设置为 private
            result = supabase.table('agents').update({
                'visibility': 'private'
            }).eq('role', role).execute()
            print(f"  ✅ 已隐藏: {role} (设置为 private)")
        else:
            print(f"  ℹ️  {role} 不在数据库中（从文件系统加载）")
    except Exception as e:
        print(f"  ⚠️  处理 {role} 时出错: {e}")

# 4. 查看最终结果
print("\n步骤 4: 查看清理后的结果")
print("-" * 80)
all_agents = supabase.table('agents').select('role, name, visibility').order('created_at').execute()
print("\n数据库中的 Agents:")
for agent in all_agents.data:
    status = "✅ 市场展示" if agent['visibility'] == 'public' else "🔒 隐藏"
    print(f"  {status} - {agent['name']} ({agent['role']})")

print("\n" + "=" * 80)
print("✅ 清理完成！")
print("\n注意：")
print("  - design_validator 和 ee_developer 如果不在数据库中，")
print("    它们只会从后端 API 返回，不会在前端市场展示")
print("  - 前端市场只展示数据库中 visibility='public' 的 Agents")
