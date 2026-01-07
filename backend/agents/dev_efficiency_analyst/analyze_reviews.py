#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
import statistics

def parse_datetime(dt_str):
    """解析ISO格式时间"""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

def calculate_review_time(created, updated):
    """计算审查耗时（小时）"""
    created_dt = parse_datetime(created)
    updated_dt = parse_datetime(updated)
    return (updated_dt - created_dt).total_seconds() / 3600

def analyze_gerrit_data(file_path):
    """分析Gerrit代码审查数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    changes = data['changes']
    
    print("=" * 60)
    print("📊 代码审查效率分析报告")
    print("=" * 60)
    print()
    
    # 1. 计算Review耗时
    review_times = []
    rework_counts = []
    
    print("## 详细变更信息\n")
    for change in changes:
        created = change['created']
        updated = change['updated']
        review_time = calculate_review_time(created, updated)
        review_times.append(review_time)
        
        # 计算返工次数（revision数量 - 1）
        revision_count = len(change['revisions'])
        rework_count = revision_count - 1
        rework_counts.append(rework_count)
        
        print(f"### {change['id']} - {change['subject']}")
        print(f"  - 项目: {change['project']}")
        print(f"  - 分支: {change['branch']}")
        print(f"  - 创建时间: {created}")
        print(f"  - 合并时间: {updated}")
        print(f"  - Review耗时: {review_time:.1f} 小时")
        print(f"  - Revision数量: {revision_count}")
        print(f"  - 返工次数: {rework_count}")
        print()
    
    # 2. 统计分析
    print("=" * 60)
    print("## 📈 关键指标")
    print("=" * 60)
    print()
    
    # Review耗时统计
    avg_review_time = statistics.mean(review_times)
    median_review_time = statistics.median(review_times)
    max_review_time = max(review_times)
    min_review_time = min(review_times)
    
    print(f"### Review耗时统计")
    print(f"  - 平均耗时: {avg_review_time:.1f} 小时")
    print(f"  - 中位数耗时: {median_review_time:.1f} 小时")
    print(f"  - 最长耗时: {max_review_time:.1f} 小时")
    print(f"  - 最短耗时: {min_review_time:.1f} 小时")
    print()
    
    # 返工率统计
    total_changes = len(changes)
    changes_with_rework = sum(1 for r in rework_counts if r > 0)
    rework_rate = (changes_with_rework / total_changes) * 100
    avg_rework_count = statistics.mean(rework_counts)
    
    print(f"### 返工情况统计")
    print(f"  - 需要返工的变更: {changes_with_rework}/{total_changes}")
    print(f"  - 返工率: {rework_rate:.1f}%")
    print(f"  - 平均返工次数: {avg_rework_count:.2f}")
    print()
    
    # 项目分布
    project_stats = {}
    for change in changes:
        project = change['project']
        if project not in project_stats:
            project_stats[project] = {'count': 0, 'review_times': []}
        project_stats[project]['count'] += 1
        review_time = calculate_review_time(change['created'], change['updated'])
        project_stats[project]['review_times'].append(review_time)
    
    print(f"### 项目分布")
    for project, stats in project_stats.items():
        avg_time = statistics.mean(stats['review_times'])
        print(f"  - {project}: {stats['count']} 个变更，平均耗时 {avg_time:.1f} 小时")
    print()
    
    # 3. 问题检测
    print("=" * 60)
    print("## 🚨 问题检测")
    print("=" * 60)
    print()
    
    issues_found = []
    
    # 检查Review耗时
    MEDIAN_THRESHOLD = 24  # 24小时
    if median_review_time > MEDIAN_THRESHOLD:
        issues_found.append({
            'level': '严重',
            'type': 'Review耗时过长',
            'current': f'{median_review_time:.1f}小时',
            'threshold': f'{MEDIAN_THRESHOLD}小时',
            'impact': '可能延误迭代交付，影响团队吞吐量'
        })
    
    # 检查返工率
    REWORK_RATE_THRESHOLD = 15  # 15%
    if rework_rate > REWORK_RATE_THRESHOLD:
        issues_found.append({
            'level': '警告',
            'type': '返工率偏高',
            'current': f'{rework_rate:.1f}%',
            'threshold': f'{REWORK_RATE_THRESHOLD}%',
            'impact': '代码质量需要改进，或Review标准不一致'
        })
    
    # 检查超长耗时
    LONG_REVIEW_THRESHOLD = 72  # 72小时 (3天)
    long_reviews = [t for t in review_times if t > LONG_REVIEW_THRESHOLD]
    if long_reviews:
        issues_found.append({
            'level': '警告',
            'type': '存在超长Review',
            'current': f'{len(long_reviews)}个变更超过{LONG_REVIEW_THRESHOLD}小时',
            'threshold': f'{LONG_REVIEW_THRESHOLD}小时',
            'impact': '可能存在Review阻塞或被遗忘的情况'
        })
    
    if issues_found:
        for idx, issue in enumerate(issues_found, 1):
            print(f"### 问题 {idx}: {issue['type']}")
            print(f"  - 严重程度: {issue['level']}")
            print(f"  - 当前值: {issue['current']}")
            print(f"  - 阈值: {issue['threshold']}")
            print(f"  - 影响: {issue['impact']}")
            print()
    else:
        print("✅ 未发现明显问题，所有指标在正常范围内。")
        print()
    
    # 4. 改进建议
    print("=" * 60)
    print("## 💡 改进建议")
    print("=" * 60)
    print()
    
    if median_review_time > MEDIAN_THRESHOLD:
        print("1. **加快Review响应速度**")
        print("   - 设置Review SLA目标（建议24小时内首次响应）")
        print("   - 使用轮值制度确保及时Review")
        print("   - 对超时Review自动提醒")
        print()
    
    if rework_rate > REWORK_RATE_THRESHOLD:
        print("2. **降低返工率**")
        print("   - 提交前强化自测和代码检查")
        print("   - 统一代码规范和Review标准")
        print("   - 对高频返工问题做团队分享")
        print()
    
    if long_reviews:
        print("3. **避免Review阻塞**")
        print("   - 拆分大型变更为小批次提交")
        print("   - 主动跟进长时间未响应的Review")
        print("   - 考虑增加Reviewer资源")
        print()
    
    print("4. **持续监控**")
    print("   - 建立每日效率看板")
    print("   - 定期（周/月）回顾趋势")
    print("   - 与团队共享关键指标")
    print()
    
    return {
        'review_times': review_times,
        'median_review_time': median_review_time,
        'avg_review_time': avg_review_time,
        'rework_rate': rework_rate,
        'issues_found': issues_found
    }

if __name__ == '__main__':
    analyze_gerrit_data('data/mock_gerrit_data.json')
