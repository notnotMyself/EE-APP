#!/usr/bin/env python3
"""
Report Generation Skill
生成标准化报告的能力

支持报告类型：
1. 代码审查效率报告（Gerrit数据）
2. 门禁构建效率报告（Build数据）
3. 综合研发效能报告
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional


def generate_efficiency_report(metrics: Dict[str, Any], anomalies: list) -> str:
    """
    生成研发效能报告（Markdown格式）

    Args:
        metrics: 指标数据
        anomalies: 异常列表

    Returns:
        Markdown格式的报告内容
    """
    today = datetime.now().strftime("%Y-%m-%d")

    report = f"""# 研发效能日报 - {today}

## 📊 关键指标

| 指标 | 数值 | 说明 |
|-----|------|------|
| 总提交数 | {metrics.get('total_changes', 0)} | 昨日合并的代码变更数量 |
| Review中位耗时 | {metrics.get('median_review_time_hours', 0):.1f} 小时 | 50%的Review在此时间内完成 |
| Review P95耗时 | {metrics.get('p95_review_time_hours', 0):.1f} 小时 | 95%的Review在此时间内完成 |
| 平均Review耗时 | {metrics.get('avg_review_time_hours', 0):.1f} 小时 | 所有Review的平均耗时 |
| 返工率 | {metrics.get('rework_rate_percent', 0):.1f}% | 需要多次修改的提交占比 |
| 返工次数 | {metrics.get('rework_count', 0)} | 实际发生返工的提交数量 |

"""

    # 异常发现部分
    if anomalies:
        report += "\n## 🔍 异常发现\n\n"
        for idx, anomaly in enumerate(anomalies, 1):
            severity_emoji = "🚨" if anomaly['severity'] == 'critical' else "⚠️"
            report += f"{severity_emoji} **异常 {idx}**: {anomaly['message']}\n"
            report += f"   - 当前值: {anomaly['value']:.1f}\n"
            report += f"   - 阈值: {anomaly['threshold']}\n\n"

        # 影响分析
        report += "\n### 📉 影响分析\n\n"
        if any(a['type'] in ['high_review_time', 'high_p95_time'] for a in anomalies):
            report += "- Review耗时过长可能导致本周迭代延期\n"
            report += "- 影响开发者工作节奏和士气\n"

        if any(a['type'] == 'high_rework_rate' for a in anomalies):
            report += "- 高返工率表明代码质量或需求理解存在问题\n"
            report += "- 增加了团队的无效劳动时间\n"

        # 改进建议
        report += "\n## 💡 改进建议\n\n"
        suggestions = []

        if any(a['type'] in ['high_review_time', 'high_p95_time'] for a in anomalies):
            suggestions.extend([
                "1. **加快Review响应**: 设置Review提醒，确保2小时内首次响应",
                "2. **并行Review**: 添加多个Reviewer，减少等待时间",
                "3. **拆分大PR**: 将大型变更拆分为小的可独立Review的部分"
            ])

        if any(a['type'] == 'high_rework_rate' for a in anomalies):
            suggestions.extend([
                "4. **提升代码质量**: 加强本地测试和自检",
                "5. **需求澄清**: 开发前与产品确认需求细节",
                "6. **代码规范培训**: 组织团队代码规范培训"
            ])

        report += "\n".join(suggestions[:5])  # 最多5条建议

    else:
        report += "\n## ✅ 运行状态\n\n"
        report += "所有指标正常，团队研发效率保持良好状态。\n"

    # 数据来源
    report += f"\n\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    report += "*数据来源: Gerrit API*\n"

    return report


def generate_build_report(data: Dict[str, Any]) -> str:
    """
    生成门禁构建效率报告（Markdown格式）

    Args:
        data: 构建分析数据，包含 metrics, platform_percentiles, trend, anomalies 等

    Returns:
        Markdown格式的报告内容
    """
    today = datetime.now().strftime("%Y-%m-%d")
    days = data.get("analysis_period_days", 7)
    
    report = f"""# 门禁构建效率报告 - {today}

> 分析周期: 最近 **{days}** 天

"""
    
    # 基础指标
    metrics = data.get("metrics", {})
    if metrics:
        total_builds = metrics.get("total_builds", 0)
        duration = metrics.get("total_duration_minutes", {})
        
        report += """## 📊 基础指标

| 指标 | 数值 | 说明 |
|-----|------|------|
"""
        report += f"| 分析构建数 | **{total_builds:,}** 次 | 分析周期内的构建任务数量 |\n"
        report += f"| 平均耗时 | **{duration.get('avg', 0):.1f}** 分钟 | 所有构建的平均端到端耗时 |\n"
        report += f"| P50耗时 | **{duration.get('p50', 0):.1f}** 分钟 | 50%的构建在此时间内完成 |\n"
        report += f"| P95耗时 | **{duration.get('p95', 0):.1f}** 分钟 | 95%的构建在此时间内完成 |\n"
        report += f"| P99耗时 | **{duration.get('p99', 0):.1f}** 分钟 | 99%的构建在此时间内完成 |\n"
        report += f"| 最长耗时 | **{duration.get('max', 0):.1f}** 分钟 | 最慢构建的耗时 |\n"
        report += "\n"
        
        # 各阶段耗时
        stage_ratio = metrics.get("stage_ratio_percent", {})
        if stage_ratio:
            report += """### ⏱️ 各阶段耗时占比

| 阶段 | 占比 | 说明 |
|-----|------|------|
"""
            report += f"| 构建(build) | **{stage_ratio.get('build', 0):.1f}%** | 实际编译耗时 |\n"
            report += f"| 下载(download) | **{stage_ratio.get('download', 0):.1f}%** | 代码下载耗时 |\n"
            report += f"| 拷贝(copy) | **{stage_ratio.get('copy', 0):.1f}%** | 文件拷贝耗时 |\n"
            report += f"| OFP处理 | **{stage_ratio.get('ofp', 0):.1f}%** | OFP处理耗时 |\n"
            report += "\n"
    
    # 趋势分析
    trend = data.get("trend", {})
    if trend:
        overall_trend = trend.get("overall_trend", "unknown")
        trend_map = {
            "worsening": "📈 **恶化中** - 构建耗时在增加",
            "improving": "📉 **改善中** - 构建耗时在减少",
            "stable": "➡️ **保持稳定** - 构建耗时变化不大",
            "insufficient_data": "⚠️ **数据不足** - 无法判断趋势"
        }
        
        report += f"""## 📈 趋势分析

**整体趋势**: {trend_map.get(overall_trend, '未知')}

"""
        
        # 趋势数据表
        trend_data = trend.get("data", [])
        if trend_data and len(trend_data) > 0:
            report += "| 日期 | 构建数 | 平均耗时(分钟) | 环比变化 |\n"
            report += "|------|--------|---------------|----------|\n"
            for t in trend_data[-7:]:  # 最近7个周期
                change = t.get("change_percent")
                change_str = f"{change:+.1f}%" if change is not None else "-"
                change_icon = ""
                if change is not None:
                    if change > 10:
                        change_icon = "🔴"
                    elif change < -10:
                        change_icon = "🟢"
                report += f"| {t.get('period', '')} | {t.get('build_count', 0):,} | {t.get('avg_pipeline_minutes', 0):.1f} | {change_icon} {change_str} |\n"
            report += "\n"
    
    # 异常告警
    anomalies_data = data.get("anomalies", {})
    anomalies_list = anomalies_data.get("anomalies", [])
    if anomalies_list:
        report += "## ⚠️ 异常告警\n\n"
        for anomaly in anomalies_list:
            severity = anomaly.get("severity", "warning")
            severity_icon = "🔴" if severity == "critical" else "🟡"
            report += f"{severity_icon} **{anomaly.get('type', 'unknown')}**: {anomaly.get('message', '')}\n\n"
            
            details = anomaly.get("details", [])
            if details and isinstance(details, list):
                if anomaly.get("type") == "slow_builds":
                    report += "| 任务号 | 平台 | 耗时(分钟) |\n"
                    report += "|--------|------|------------|\n"
                    for d in details[:5]:
                        report += f"| {d.get('task_num', '')} | {d.get('platform', '')} | {d.get('duration_minutes', 0):.0f} |\n"
                elif anomaly.get("type") == "worsening_platforms":
                    report += "| 平台 | 当前平均(分钟) | 之前平均(分钟) | 变化 |\n"
                    report += "|------|---------------|---------------|------|\n"
                    for d in details:
                        report += f"| {d.get('platform', '')} | {d.get('recent_avg_minutes', 0):.0f} | {d.get('prev_avg_minutes', 0):.0f} | +{d.get('change_percent', 0):.0f}% |\n"
                report += "\n"
    
    # 平台分析
    platform_data = data.get("platform_percentiles", {})
    platforms = platform_data.get("platforms", [])
    if platforms:
        report += """## 🏆 平台构建耗时排行

> 按P95耗时排序，越高表示越需要关注

| 排名 | 平台 | P50(分钟) | P95(分钟) | P99(分钟) | 构建数 |
|------|------|-----------|-----------|-----------|--------|
"""
        sorted_platforms = sorted(platforms, key=lambda x: float(x.get("p95", 0) or 0), reverse=True)
        for i, p in enumerate(sorted_platforms[:10], 1):
            p95_val = float(p.get("p95", 0) or 0)
            p50_val = float(p.get("p50", 0) or 0)
            p99_val = float(p.get("p99", 0) or 0)
            count_val = int(p.get("count", 0) or 0)
            attention = "⚠️" if p95_val > 120 else ""
            report += f"| {i} {attention} | {p.get('platform', '')} | {p50_val:.0f} | {p95_val:.0f} | {p99_val:.0f} | {count_val:,} |\n"
        report += "\n"
    
    # 改进建议
    report += """## 💡 改进建议

"""
    suggestions = []
    
    # 根据异常生成建议
    if anomalies_list:
        for anomaly in anomalies_list:
            if anomaly.get("type") == "slow_builds":
                suggestions.append("1. **关注慢构建**: 排查超过P95的构建任务，检查是否存在异常")
            elif anomaly.get("type") == "worsening_platforms":
                suggestions.append("2. **平台优化**: 重点关注耗时恶化的平台，分析根因")
    
    # 根据趋势生成建议
    if trend.get("overall_trend") == "worsening":
        suggestions.append("3. **趋势警示**: 构建耗时整体在恶化，建议排查基础设施或代码变化")
    
    # 根据阶段占比生成建议
    stage_ratio = metrics.get("stage_ratio_percent", {})
    if stage_ratio:
        if stage_ratio.get("download", 0) > 30:
            suggestions.append("4. **优化下载**: 下载阶段占比过高，考虑增加缓存或优化网络")
        if stage_ratio.get("build", 0) > 70:
            suggestions.append("5. **编译优化**: 编译阶段占比最大，可考虑增量编译或并行编译优化")
    
    if not suggestions:
        suggestions.append("✅ 当前构建效率正常，继续保持")
    
    report += "\n".join(suggestions)
    
    # 数据来源
    report += f"\n\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    report += "*数据来源: 门禁构建数据库 (rn_test.personal_build)*\n"

    return report


def generate_combined_report(
    gerrit_data: Optional[Dict[str, Any]] = None,
    build_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成综合研发效能报告
    
    Args:
        gerrit_data: Gerrit分析数据
        build_data: 构建分析数据
        
    Returns:
        Markdown格式的综合报告
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# 研发效能综合报告 - {today}

"""
    
    # 代码审查部分
    if gerrit_data:
        report += "## 🔍 代码审查效率\n\n"
        metrics = gerrit_data.get("metrics", {})
        report += f"- 总提交数: **{metrics.get('total_changes', 0)}**\n"
        report += f"- Review中位耗时: **{metrics.get('median_review_time_hours', 0):.1f}** 小时\n"
        report += f"- Review P95耗时: **{metrics.get('p95_review_time_hours', 0):.1f}** 小时\n"
        report += f"- 返工率: **{metrics.get('rework_rate_percent', 0):.1f}%**\n\n"
    
    # 构建效率部分
    if build_data:
        report += "## 🏗️ 门禁构建效率\n\n"
        metrics = build_data.get("metrics", {})
        duration = metrics.get("total_duration_minutes", {})
        report += f"- 分析构建数: **{metrics.get('total_builds', 0):,}** 次\n"
        report += f"- 构建P50耗时: **{duration.get('p50', 0):.1f}** 分钟\n"
        report += f"- 构建P95耗时: **{duration.get('p95', 0):.1f}** 分钟\n"
        
        trend = build_data.get("trend", {})
        trend_map = {"worsening": "恶化中", "improving": "改善中", "stable": "稳定"}
        if trend.get("overall_trend"):
            report += f"- 趋势: **{trend_map.get(trend['overall_trend'], '未知')}**\n"
        report += "\n"
    
    # 综合异常
    all_anomalies = []
    if gerrit_data and gerrit_data.get("anomalies"):
        all_anomalies.extend([("代码审查", a) for a in gerrit_data["anomalies"]])
    if build_data:
        build_anomalies = build_data.get("anomalies", {}).get("anomalies", [])
        all_anomalies.extend([("门禁构建", a) for a in build_anomalies])
    
    if all_anomalies:
        report += "## ⚠️ 综合告警\n\n"
        for source, anomaly in all_anomalies:
            severity_icon = "🔴" if anomaly.get("severity") == "critical" else "🟡"
            report += f"{severity_icon} **[{source}]** {anomaly.get('message', '')}\n"
        report += "\n"
    else:
        report += "## ✅ 状态正常\n\n所有指标正常，团队研发效率保持良好状态。\n\n"
    
    report += f"\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return report


def generate_problem_report(data: Dict[str, Any]) -> str:
    """
    生成问题导向的构建分析报告（Markdown格式）
    
    重点呈现问题和解决思路，而非简单罗列指标
    
    Args:
        data: 问题分析数据（来自 build_analysis.py 的 problems action）
        
    Returns:
        Markdown格式的问题导向报告
    """
    today = datetime.now().strftime("%Y-%m-%d")
    days = data.get("analysis_period_days", 7)
    severity = data.get("severity", "low")
    
    severity_map = {
        "high": "🔴 严重",
        "medium": "🟡 中等",
        "low": "🟢 良好"
    }
    
    report = f"""# 门禁构建问题分析报告 - {today}

> 分析周期: 最近 **{days}** 天 | 问题等级: {severity_map.get(severity, '未知')}

"""
    
    # 核心问题概览
    summary = data.get("summary", {})
    report += f"""## 📋 问题概览

| 指标 | 数值 | 说明 |
|-----|------|------|
| 发现问题数 | **{summary.get('total_problems', 0)}** | 需要关注的问题总数 |
| 落后平台 | **{summary.get('lagging_platforms', 0)}** 个 | P95高于整体水平 |
| 恶化平台 | **{summary.get('worsening_platforms', 0)}** 个 | 耗时趋势在增加 |
| 改善平台 | **{summary.get('improving_platforms', 0)}** 个 | 耗时趋势在减少 |
| 整体P95 | **{summary.get('overall_p95_minutes', 0)}** 分钟 | 全局基准线 |

"""
    
    # 问题列表
    problems = data.get("problems", [])
    if problems:
        report += "## 🚨 发现的问题\n\n"
        for i, problem in enumerate(problems, 1):
            report += f"{i}. {problem}\n"
        report += "\n"
    else:
        report += "## ✅ 状态良好\n\n当前未发现显著问题，继续保持。\n\n"
    
    # 详细分析 - P95落后平台
    details = data.get("details", {})
    lagging = details.get("lagging_analysis", {})
    lagging_platforms = lagging.get("lagging_platforms", [])
    
    if lagging_platforms:
        report += f"""## 🐢 P95落后的平台

> 整体P95: **{lagging.get('overall_p95_minutes', 0)}** 分钟，以下平台高于此基准

| 排名 | 平台 | 构建数 | P50 | P95 | 差距 | 厂商 |
|-----|------|--------|-----|-----|------|------|
"""
        for i, p in enumerate(lagging_platforms[:10], 1):
            icon = "🔴" if float(p.get("gap_percent", 0)) > 15 else "🟡"
            report += f"| {i} {icon} | {p.get('display_name', p.get('platform', ''))} | {p.get('build_count', 0)} | {p.get('p50_minutes', 0)} | {p.get('p95_minutes', 0)} | +{p.get('gap_percent', 0)}% | {p.get('vendor', '')} |\n"
        report += "\n"
        
        # 厂商分析
        vendor_stats = {}
        for p in lagging_platforms:
            v = p.get("vendor", "其他")
            if v not in vendor_stats:
                vendor_stats[v] = 0
            vendor_stats[v] += 1
        
        if vendor_stats:
            report += "**按厂商统计落后平台数:**\n"
            for v, count in sorted(vendor_stats.items(), key=lambda x: x[1], reverse=True):
                report += f"- {v}: {count} 个\n"
            report += "\n"
    
    # 健康平台作为参考
    healthy = lagging.get("healthy_platforms", [])
    if healthy:
        report += "**健康平台参考（可学习）:**\n"
        for p in healthy[:3]:
            report += f"- ✅ {p.get('display_name', p.get('platform', ''))}: P95={p.get('p95_minutes', 0)}分钟\n"
        report += "\n"
    
    # 趋势变化
    trends = details.get("trend_analysis", {})
    worsening = trends.get("worsening_platforms", [])
    improving = trends.get("improving_platforms", [])
    
    if worsening or improving:
        report += f"""## 📈 趋势变化

> 对比周期: {trends.get('comparison_period', '最近3天 vs 之前3天')}

"""
        if worsening:
            report += "### 恶化中的平台\n\n"
            report += "| 平台 | 当前平均 | 之前平均 | 变化 |\n"
            report += "|------|---------|---------|------|\n"
            for p in worsening[:5]:
                report += f"| 📈 {p.get('display_name', p.get('platform', ''))} | {p.get('recent_avg_minutes', 0)}分钟 | {p.get('prev_avg_minutes', 0)}分钟 | +{p.get('change_percent', 0)}% |\n"
            report += "\n"
        
        if improving:
            report += "### 改善中的平台\n\n"
            report += "| 平台 | 当前平均 | 之前平均 | 变化 |\n"
            report += "|------|---------|---------|------|\n"
            for p in improving[:5]:
                report += f"| 📉 {p.get('display_name', p.get('platform', ''))} | {p.get('recent_avg_minutes', 0)}分钟 | {p.get('prev_avg_minutes', 0)}分钟 | {p.get('change_percent', 0)}% |\n"
            report += "\n"
    
    # 组件瓶颈分析
    components = details.get("component_analysis", {})
    comp_list = components.get("components", [])
    
    if comp_list:
        report += """## 🧩 组件瓶颈分析

"""
        # 组件洞察
        insights = components.get("insights", [])
        for insight in insights:
            report += f"- {insight}\n"
        
        report += "\n**P95最慢的组件:**\n\n"
        report += "| 组件 | 构建数 | P50 | P95 | 复杂度 |\n"
        report += "|------|--------|-----|-----|--------|\n"
        for c in comp_list[:7]:
            complexity = "高" if c.get("is_complex") else "低"
            report += f"| {c.get('component', '')} | {c.get('build_count', 0)} | {c.get('p50_minutes', 0)}分钟 | {c.get('p95_minutes', 0)}分钟 | {complexity} |\n"
        report += "\n"
    
    # 人员分析（简略）
    users = details.get("user_analysis", {})
    if users.get("total_users", 0) > 0:
        report += f"""## 👤 人员维度分析

- 分析用户数: **{users.get('total_users', 0)}** 人
- 平均构建耗时: **{users.get('avg_build_time_minutes', 0)}** 分钟
- 需关注用户数: **{users.get('users_need_attention', 0)}** 人（平均耗时高于整体30%）

"""
        user_insights = users.get("insights", [])
        for insight in user_insights:
            report += f"- {insight}\n"
        report += "\n"
    
    # 建议
    suggestions = data.get("suggestions", [])
    if suggestions:
        report += "## 💡 改进建议\n\n"
        for i, s in enumerate(suggestions[:8], 1):
            report += f"{i}. {s}\n"
        report += "\n"
    
    report += f"""---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源: 门禁构建数据库 (rn_test.personal_build)*
*报告类型: 问题导向分析*
"""
    
    return report


def main():
    """
    主函数：从stdin读取分析结果，生成报告
    
    输入JSON格式：
    {
        "report_type": "gerrit" | "build" | "build_problems" | "combined",
        "gerrit_data": {...},  # 可选，用于gerrit或combined报告
        "build_data": {...},   # 可选，用于build或combined报告
        "metrics": {...},      # 向后兼容：gerrit报告的metrics
        "anomalies": [...]     # 向后兼容：gerrit报告的anomalies
    }
    """
    try:
        # 从stdin读取JSON数据
        input_data = sys.stdin.read()
        data = json.loads(input_data)
        
        report_type = data.get("report_type", "gerrit")
        
        if report_type == "build":
            # 构建分析报告（基础指标）
            build_data = data.get("build_data", data)
            report = generate_build_report(build_data)
        elif report_type == "build_problems" or report_type == "problem_analysis":
            # 问题导向的构建分析报告（推荐）
            build_data = data.get("build_data", data)
            report = generate_problem_report(build_data)
        elif report_type == "combined":
            # 综合报告
            report = generate_combined_report(
                gerrit_data=data.get("gerrit_data"),
                build_data=data.get("build_data")
            )
        else:
            # 默认：Gerrit代码审查报告（向后兼容）
            report = generate_efficiency_report(
                metrics=data.get('metrics', {}),
                anomalies=data.get('anomalies', [])
            )

        # 输出报告
        print(report)

        return 0
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
