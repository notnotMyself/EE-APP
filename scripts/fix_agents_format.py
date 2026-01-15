#!/usr/bin/env python3
"""
修正 design_validator 和 ee_developer 的数据格式
（改为字典格式以匹配现有 Agents）
"""
from supabase import create_client, Client

url = "https://dwesyojvzbltqtgtctpt.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjkzMDkxNCwiZXhwIjoyMDgyNTA2OTE0fQ.jZb1AmsokaJIVksT8it4khZzArI73xQpwq83otsboIA"

supabase: Client = create_client(url, service_key)

print("修正 EE 和 Chris 的数据格式...")
print("=" * 80)

# 修正后的数据（使用字典格式）
agents_updates = [
    {
        'role': 'design_validator',
        'capabilities': {
            'can_analyze_vision': True,
            'can_check_interaction': True,
            'can_check_consistency': True,
            'can_compare_designs': True,
            'can_manage_knowledge': True
        },
        'data_sources': {
            'design_images': {
                'type': 'multimodal',
                'formats': ['png', 'jpeg', 'webp']
            },
            'knowledge_base': {
                'type': 'markdown',
                'location': 'knowledge_base/'
            }
        },
        'trigger_conditions': {
            'on_design_upload': True,
            'on_review_request': True,
            'on_comparison_request': True
        }
    },
    {
        'role': 'ee_developer',
        'capabilities': {
            'can_modify_code': True,
            'can_run_tests': True,
            'can_manage_git': True,
            'can_review_code': True,
            'can_create_pr': True
        },
        'data_sources': {
            'code_repository': {
                'type': 'git',
                'branch_strategy': 'feature_branch'
            },
            'test_results': {
                'type': 'test_output',
                'frameworks': ['pytest', 'flutter_test']
            }
        },
        'trigger_conditions': {
            'on_code_modification_request': True,
            'on_pr_creation_request': True,
            'on_test_run_request': True
        }
    }
]

# 更新 Agents
for update_data in agents_updates:
    role = update_data['role']
    try:
        result = supabase.table('agents').update({
            'capabilities': update_data['capabilities'],
            'data_sources': update_data['data_sources'],
            'trigger_conditions': update_data['trigger_conditions']
        }).eq('role', role).execute()

        print(f"✅ 已修正: {role}")
    except Exception as e:
        print(f"❌ 修正 {role} 时出错: {e}")

print("\n" + "=" * 80)
print("✅ 修正完成！现在所有 Agents 的数据格式一致")
