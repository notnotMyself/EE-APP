#!/usr/bin/env python3
"""
定时任务详细状态检查
"""

import os
import sys
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_agent_platform/backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'ai_agent_platform/backend/.env'))

from supabase import create_client

def get_supabase_client():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    return create_client(url, key)

def check_scheduler_details(supabase):
    print("\n" + "="*70)
    print("📊 定时任务详细状态分析")
    print("="*70)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取所有定时任务
    result = supabase.table("scheduled_jobs").select("*").execute()
    jobs = result.data
    
    for job in jobs:
        print("\n" + "="*70)
        print(f"📋 任务: {job.get('job_name')}")
        print("="*70)
        
        print(f"\n【基本信息】")
        print(f"  ID: {job.get('id')}")
        print(f"  Agent ID: {job.get('agent_id')}")
        print(f"  任务类型: {job.get('job_type')}")
        print(f"  调度类型: {job.get('schedule_type')}")
        print(f"  Cron表达式: {job.get('cron_expression')}")
        print(f"  时区: {job.get('timezone')}")
        print(f"  是否活跃: {'✅ 是' if job.get('is_active') else '❌ 否'}")
        
        print(f"\n【任务提示词】")
        prompt = job.get('task_prompt', '')
        if prompt:
            # 截取显示
            if len(prompt) > 500:
                print(f"  {prompt[:500]}...")
            else:
                print(f"  {prompt}")
        
        print(f"\n【简报配置】")
        config = job.get('briefing_config', {})
        if config:
            print(f"  启用简报: {'✅ 是' if config.get('enabled') else '❌ 否'}")
            print(f"  最小重要性分数: {config.get('min_importance_score', 'N/A')}")
            print(f"  每日最大简报数: {config.get('max_daily_briefings', 'N/A')}")
            print(f"  简报类型: {config.get('briefing_type', 'N/A')}")
            print(f"  默认优先级: {config.get('default_priority', 'N/A')}")
            print(f"  最大重试次数: {config.get('max_retries', 'N/A')}")
            print(f"  重试延迟(分钟): {config.get('retry_delay_minutes', 'N/A')}")
        
        print(f"\n【运行统计】")
        print(f"  总运行次数: {job.get('run_count', 0)}")
        print(f"  成功次数: {job.get('success_count', 0)}")
        print(f"  失败次数: {job.get('failure_count', 0)}")
        print(f"  上次运行: {job.get('last_run_at', '从未运行')}")
        print(f"  下次运行: {job.get('next_run_at', '未设置')}")
        
        print(f"\n【最后执行结果】")
        last_result = job.get('last_result')
        if last_result:
            print(f"  状态: {last_result.get('status', 'N/A')}")
            if last_result.get('error'):
                print(f"  错误: {last_result.get('error')}")
            if last_result.get('result'):
                result_data = last_result.get('result', {})
                print(f"  生成简报数: {result_data.get('briefings_created', 0)}")
        else:
            print("  无执行记录")
        
        print(f"\n【时间戳】")
        print(f"  创建时间: {job.get('created_at')}")
        print(f"  更新时间: {job.get('updated_at')}")
    
    # 检查简报生成历史
    print("\n" + "="*70)
    print("📬 简报生成历史分析")
    print("="*70)
    
    # 按日期统计简报
    result = supabase.table("briefings").select("created_at, briefing_type, priority, status, importance_score").order("created_at", desc=True).execute()
    briefings = result.data
    
    if briefings:
        # 按日期分组
        by_date = {}
        for b in briefings:
            date = b['created_at'][:10] if b.get('created_at') else 'Unknown'
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(b)
        
        print(f"\n按日期统计:")
        for date, items in sorted(by_date.items(), reverse=True):
            print(f"\n  📅 {date}: {len(items)} 条简报")
            for item in items:
                print(f"     - [{item.get('priority')}] {item.get('briefing_type')} (重要性: {item.get('importance_score')}, 状态: {item.get('status')})")
    else:
        print("  暂无简报数据")
    
    # 检查是否有完整报告
    print("\n" + "="*70)
    print("📄 完整报告检查")
    print("="*70)
    
    result = supabase.table("artifacts").select("*").eq("type", "report").order("created_at", desc=True).limit(5).execute()
    reports = result.data
    
    if reports:
        print(f"\n找到 {len(reports)} 个报告:")
        for r in reports:
            print(f"\n  📑 {r.get('title', 'N/A')}")
            print(f"     ID: {r.get('id')}")
            print(f"     创建时间: {r.get('created_at')}")
            content = r.get('content', '')
            print(f"     内容长度: {len(content)} 字符")
            if content:
                # 显示前200字符
                preview = content[:200].replace('\n', ' ')
                print(f"     内容预览: {preview}...")
    else:
        print("  ⚠️ 暂无完整报告")
        print("  说明: 简报系统可能未生成完整报告，或报告未存储到 artifacts 表")
    
    # 检查简报是否关联了报告
    print("\n" + "="*70)
    print("🔗 简报-报告关联检查")
    print("="*70)
    
    result = supabase.table("briefings").select("id, title, report_artifact_id").execute()
    briefings = result.data
    
    with_report = [b for b in briefings if b.get('report_artifact_id')]
    without_report = [b for b in briefings if not b.get('report_artifact_id')]
    
    print(f"\n  有关联报告的简报: {len(with_report)}")
    print(f"  无关联报告的简报: {len(without_report)}")
    
    if with_report:
        print(f"\n  有报告的简报:")
        for b in with_report[:5]:
            print(f"    - {b.get('title', 'N/A')[:40]} -> {b.get('report_artifact_id')}")
    
    print("\n" + "="*70)
    print("✅ 详细检查完成")
    print("="*70)

def main():
    supabase = get_supabase_client()
    check_scheduler_details(supabase)

if __name__ == "__main__":
    main()


