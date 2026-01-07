#!/usr/bin/env python3
"""
Gerrit Code Review Data Analysis
分析代码审查效率指标
"""

import json
from datetime import datetime, timedelta
from statistics import median, mean
import sys

def parse_datetime(dt_string):
    """解析ISO格式时间"""
    return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))

def calculate_review_time(change):
    """计算单个change的审查时间（小时）"""
    created = parse_datetime(change['created'])
    updated = parse_datetime(change['updated'])
    return (updated - created).total_seconds() / 3600

def calculate_rework_rate(change):
    """计算返工率（revision数量 > 1表示有返工）"""
    return len(change.get('revisions', {})) > 1

def analyze_gerrit_data(data):
    """分析Gerrit数据"""
    changes = data.get('changes', [])
    
    if not changes:
        return {
            'error': '没有找到可分析的变更记录'
        }
    
    # 计算审查时间
    review_times = []
    for change in changes:
        review_time = calculate_review_time(change)
        review_times.append(review_time)
    
    # 计算返工率
    rework_count = sum(1 for change in changes if calculate_rework_rate(change))
    rework_rate = (rework_count / len(changes)) * 100
    
    # 计算P95
    sorted_times = sorted(review_times)
    p95_index = int(len(sorted_times) * 0.95)
    p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
    
    # 项目维度分析
    project_stats = {}
    for change in changes:
        project = change['project']
        if project not in project_stats:
            project_stats[project] = {
                'count': 0,
                'review_times': [],
                'rework_count': 0
            }
        project_stats[project]['count'] += 1
        project_stats[project]['review_times'].append(calculate_review_time(change))
        if calculate_rework_rate(change):
            project_stats[project]['rework_count'] += 1
    
    # 整理项目统计
    project_summary = {}
    for project, stats in project_stats.items():
        project_summary[project] = {
            'change_count': stats['count'],
            'avg_review_time_hours': round(mean(stats['review_times']), 2),
            'median_review_time_hours': round(median(stats['review_times']), 2),
            'rework_rate_percent': round((stats['rework_count'] / stats['count']) * 100, 2)
        }
    
    return {
        'summary': {
            'total_changes': len(changes),
            'avg_review_time_hours': round(mean(review_times), 2),
            'median_review_time_hours': round(median(review_times), 2),
            'p95_review_time_hours': round(p95_time, 2),
            'rework_rate_percent': round(rework_rate, 2),
            'merged_count': sum(1 for c in changes if c['status'] == 'MERGED')
        },
        'project_breakdown': project_summary,
        'details': [
            {
                'id': change['id'],
                'project': change['project'],
                'subject': change['subject'],
                'review_time_hours': round(calculate_review_time(change), 2),
                'revision_count': len(change.get('revisions', {})),
                'status': change['status']
            }
            for change in changes
        ]
    }

def detect_anomalies(analysis_result):
    """检测异常指标"""
    anomalies = []
    summary = analysis_result['summary']
    
    # 阈值配置
    MEDIAN_THRESHOLD = 24  # 中位数 > 24小时
    P95_THRESHOLD = 72     # P95 > 72小时
    REWORK_THRESHOLD = 15  # 返工率 > 15%
    
    if summary['median_review_time_hours'] > MEDIAN_THRESHOLD:
        anomalies.append({
            'type': 'REVIEW_TIME_HIGH',
            'severity': 'WARNING',
            'metric': 'Review中位耗时',
            'current_value': f"{summary['median_review_time_hours']}小时",
            'threshold': f"< {MEDIAN_THRESHOLD}小时",
            'message': f"Review中位耗时({summary['median_review_time_hours']}小时)超过阈值({MEDIAN_THRESHOLD}小时)"
        })
    
    if summary['p95_review_time_hours'] > P95_THRESHOLD:
        anomalies.append({
            'type': 'P95_TIME_HIGH',
            'severity': 'WARNING',
            'metric': 'Review P95耗时',
            'current_value': f"{summary['p95_review_time_hours']}小时",
            'threshold': f"< {P95_THRESHOLD}小时",
            'message': f"Review P95耗时({summary['p95_review_time_hours']}小时)超过阈值({P95_THRESHOLD}小时)"
        })
    
    if summary['rework_rate_percent'] > REWORK_THRESHOLD:
        anomalies.append({
            'type': 'REWORK_RATE_HIGH',
            'severity': 'WARNING',
            'metric': '返工率',
            'current_value': f"{summary['rework_rate_percent']}%",
            'threshold': f"< {REWORK_THRESHOLD}%",
            'message': f"返工率({summary['rework_rate_percent']}%)超过阈值({REWORK_THRESHOLD}%)"
        })
    
    return anomalies

def main():
    # 读取数据
    try:
        with open('data/mock_gerrit_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ 错误: 找不到数据文件 data/mock_gerrit_data.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 错误: JSON解析失败 - {e}")
        sys.exit(1)
    
    # 分析数据
    analysis_result = analyze_gerrit_data(data)
    
    if 'error' in analysis_result:
        print(f"❌ 分析失败: {analysis_result['error']}")
        sys.exit(1)
    
    # 检测异常
    anomalies = detect_anomalies(analysis_result)
    
    # 输出结果
    result = {
        'analysis': analysis_result,
        'anomalies': anomalies
    }
    
    # 保存结果
    with open('analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("✅ 分析完成，结果已保存到 analysis_result.json")
    
    # 输出简要报告
    print("\n" + "="*60)
    print("📊 代码审查效率分析报告")
    print("="*60)
    
    summary = analysis_result['summary']
    print(f"\n📈 关键指标:")
    print(f"  • 总变更数: {summary['total_changes']} 个")
    print(f"  • 已合并: {summary['merged_count']} 个")
    print(f"  • Review平均耗时: {summary['avg_review_time_hours']} 小时")
    print(f"  • Review中位耗时: {summary['median_review_time_hours']} 小时")
    print(f"  • Review P95耗时: {summary['p95_review_time_hours']} 小时")
    print(f"  • 返工率: {summary['rework_rate_percent']}%")
    
    print(f"\n📦 项目维度:")
    for project, stats in analysis_result['project_breakdown'].items():
        print(f"  • {project}:")
        print(f"    - 变更数: {stats['change_count']}")
        print(f"    - 中位耗时: {stats['median_review_time_hours']} 小时")
        print(f"    - 返工率: {stats['rework_rate_percent']}%")
    
    if anomalies:
        print(f"\n🚨 发现 {len(anomalies)} 个异常:")
        for anomaly in anomalies:
            print(f"  • [{anomaly['severity']}] {anomaly['message']}")
    else:
        print("\n✅ 未发现异常，各项指标正常")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
