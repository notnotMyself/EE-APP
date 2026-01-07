#!/usr/bin/env python3
"""
Report Generation Skill
生成标准化报告的能力
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any


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


def main():
    """主函数：从stdin读取分析结果，生成报告"""
    try:
        # 从stdin读取JSON数据
        input_data = sys.stdin.read()
        data = json.loads(input_data)

        # 生成报告
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
