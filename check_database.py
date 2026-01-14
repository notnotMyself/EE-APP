#!/usr/bin/env python3
"""
数据库状态检查脚本
检查 Supabase 数据库中的报告、简报和定时任务状态
"""

import os
import sys
from datetime import datetime, timedelta

# 添加 backend 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_agent_platform/backend'))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'ai_agent_platform/backend/.env'))

from supabase import create_client

def get_supabase_client():
    """获取 Supabase 客户端"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ 错误: 缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量")
        sys.exit(1)
    
    return create_client(url, key)

def check_tables(supabase):
    """检查各表数据"""
    print("\n" + "="*60)
    print("📊 数据库状态检查报告")
    print("="*60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查 agents 表
    print("\n" + "-"*40)
    print("🤖 AI Agents (agents 表)")
    print("-"*40)
    try:
        result = supabase.table("agents").select("*").execute()
        agents = result.data
        print(f"总数: {len(agents)}")
        for agent in agents:
            print(f"  - {agent.get('name', 'N/A')} ({agent.get('role', 'N/A')})")
            print(f"    ID: {agent.get('id')}")
            print(f"    状态: {'✅ 活跃' if agent.get('is_active') else '❌ 未激活'}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 2. 检查 scheduled_jobs 表
    print("\n" + "-"*40)
    print("⏰ 定时任务 (scheduled_jobs 表)")
    print("-"*40)
    try:
        result = supabase.table("scheduled_jobs").select("*").execute()
        jobs = result.data
        print(f"总数: {len(jobs)}")
        for job in jobs:
            status_icon = "✅" if job.get('is_active') else "❌"
            print(f"\n  📋 {job.get('job_name', 'N/A')}")
            print(f"     ID: {job.get('id')}")
            print(f"     状态: {status_icon} {'活跃' if job.get('is_active') else '未激活'}")
            print(f"     调度: {job.get('cron_expression', 'N/A')} ({job.get('timezone', 'N/A')})")
            print(f"     上次运行: {job.get('last_run_at', '从未运行')}")
            print(f"     下次运行: {job.get('next_run_at', 'N/A')}")
            print(f"     运行统计: 总计 {job.get('run_count', 0)} 次, 成功 {job.get('success_count', 0)} 次, 失败 {job.get('failure_count', 0)} 次")
            
            # 显示最后结果
            last_result = job.get('last_result')
            if last_result:
                print(f"     最后结果: {last_result.get('status', 'N/A')}")
                if last_result.get('error'):
                    print(f"     错误信息: {last_result.get('error')[:100]}...")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 3. 检查 briefings 表
    print("\n" + "-"*40)
    print("📬 简报 (briefings 表)")
    print("-"*40)
    try:
        result = supabase.table("briefings").select("*, agents(name, role)").order("created_at", desc=True).limit(20).execute()
        briefings = result.data
        
        # 统计
        total_result = supabase.table("briefings").select("id", count="exact").execute()
        total_count = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
        
        new_result = supabase.table("briefings").select("id", count="exact").eq("status", "new").execute()
        new_count = new_result.count if hasattr(new_result, 'count') else len(new_result.data)
        
        print(f"总数: {total_count}")
        print(f"未读: {new_count}")
        
        if briefings:
            print(f"\n最近 {len(briefings)} 条简报:")
            for b in briefings[:10]:
                agent_info = b.get('agents', {})
                agent_name = agent_info.get('name', 'Unknown') if agent_info else 'Unknown'
                print(f"\n  📌 [{b.get('priority', 'P2')}] {b.get('title', 'N/A')[:50]}")
                print(f"     来自: {agent_name}")
                print(f"     类型: {b.get('briefing_type', 'N/A')}")
                print(f"     状态: {b.get('status', 'N/A')}")
                print(f"     创建: {b.get('created_at', 'N/A')}")
                print(f"     重要性: {b.get('importance_score', 'N/A')}")
                if b.get('report_artifact_id'):
                    print(f"     关联报告: ✅ {b.get('report_artifact_id')}")
        else:
            print("  ⚠️ 暂无简报数据")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 4. 检查 artifacts 表 (报告)
    print("\n" + "-"*40)
    print("📄 报告/产出 (artifacts 表)")
    print("-"*40)
    try:
        result = supabase.table("artifacts").select("*").order("created_at", desc=True).limit(10).execute()
        artifacts = result.data
        
        total_result = supabase.table("artifacts").select("id", count="exact").execute()
        total_count = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
        
        print(f"总数: {total_count}")
        
        if artifacts:
            print(f"\n最近 {len(artifacts)} 个报告:")
            for a in artifacts:
                print(f"\n  📑 {a.get('title', 'N/A')[:50]}")
                print(f"     ID: {a.get('id')}")
                print(f"     类型: {a.get('type', 'N/A')}")
                print(f"     格式: {a.get('format', 'N/A')}")
                print(f"     创建: {a.get('created_at', 'N/A')}")
                content = a.get('content', '')
                print(f"     内容长度: {len(content) if content else 0} 字符")
        else:
            print("  ⚠️ 暂无报告数据")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 5. 检查 users 表
    print("\n" + "-"*40)
    print("👤 用户 (users 表)")
    print("-"*40)
    try:
        result = supabase.table("users").select("id, email, created_at").execute()
        users = result.data
        print(f"总数: {len(users)}")
        for u in users[:5]:
            print(f"  - {u.get('email', 'N/A')} (ID: {u.get('id')[:8]}...)")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 6. 检查 conversations 表
    print("\n" + "-"*40)
    print("💬 对话 (conversations 表)")
    print("-"*40)
    try:
        result = supabase.table("conversations").select("id, title, created_at, updated_at").order("updated_at", desc=True).limit(5).execute()
        conversations = result.data
        
        total_result = supabase.table("conversations").select("id", count="exact").execute()
        total_count = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
        
        print(f"总数: {total_count}")
        if conversations:
            print(f"\n最近 {len(conversations)} 个对话:")
            for c in conversations:
                print(f"  - {c.get('title', 'N/A')[:40]} ({c.get('updated_at', 'N/A')})")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 7. 检查 user_agents 订阅关系
    print("\n" + "-"*40)
    print("🔗 用户-Agent 订阅 (user_agents 表)")
    print("-"*40)
    try:
        result = supabase.table("user_agents").select("*, agents(name)").eq("is_subscribed", True).execute()
        subscriptions = result.data
        print(f"活跃订阅数: {len(subscriptions)}")
        for s in subscriptions[:5]:
            agent_info = s.get('agents', {})
            agent_name = agent_info.get('name', 'Unknown') if agent_info else 'Unknown'
            print(f"  - 用户 {s.get('user_id', 'N/A')[:8]}... 订阅了 {agent_name}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    print("\n" + "="*60)
    print("✅ 检查完成")
    print("="*60)

def main():
    supabase = get_supabase_client()
    check_tables(supabase)

if __name__ == "__main__":
    main()


