# 研发效能分析官 - 技能清单

本文档定义了 研发效能分析官 的所有可用技能及其接口规范。

---

## 技能概览

| 技能 ID | 名称 | 说明 | 优先级 |
|---------|------|------|--------|
| `gerrit_analysis` | Gerrit代码审查分析 | 分析代码审查效率指标和异常 | 核心 |
| `build_analysis` | 门禁构建分析 | 分析构建耗时、瓶颈和趋势 | 核心 |
| `report_generation` | 报告生成 | 生成标准化 Markdown 报告 | 辅助 |

---

## 1. gerrit_analysis - Gerrit代码审查分析

### 概述

从 MySQL 数据库获取 Gerrit 代码审查数据，计算 Review 耗时、返工率等指标，检测异常。

### 脚本位置

```
.claude/skills/gerrit_analysis.py
```

### 调用方式

```bash
echo '<JSON参数>' | python3 .claude/skills/gerrit_analysis.py
```

### 输入格式 (stdin JSON)

**方式一：查询参数（从数据库获取数据）**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `days` | int | ❌ | `7` | 分析最近 N 天的数据 |
| `project` | string | ❌ | - | 过滤特定项目 |
| `author` | string | ❌ | - | 过滤特定作者 |

**方式二：直接传入数据**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `changes` | array | ✅ | Gerrit changes 数据数组 |

### 输出格式 (stdout JSON)

```json
{
    "metrics": {
        "total_changes": 150,
        "median_review_time_hours": 12.5,
        "p95_review_time_hours": 48.0,
        "avg_review_time_hours": 18.3,
        "rework_rate_percent": 8.5,
        "rework_count": 13,
        "total_insertions": 5000,
        "total_deletions": 2000
    },
    "anomalies": [
        {
            "type": "high_review_time",
            "severity": "warning",
            "message": "Review中位耗时(30.5小时)超过24小时阈值",
            "value": 30.5,
            "threshold": 24
        }
    ],
    "data_source": "mysql",
    "timestamp": "2026-01-13T10:00:00",
    "query_params": {
        "days": 7,
        "project": null,
        "author": null
    }
}
```

### 异常类型

| 类型 | 严重级别 | 阈值 | 说明 |
|------|----------|------|------|
| `high_review_time` | warning | 24h | Review 中位耗时过长 |
| `high_p95_time` | critical | 72h | Review P95 耗时过长 |
| `high_rework_rate` | warning | 15% | 返工率过高 |

### 使用示例

```bash
# 分析最近 7 天数据
echo '{"days": 7}' | python3 .claude/skills/gerrit_analysis.py

# 分析特定项目
echo '{"days": 14, "project": "platform/frameworks/base"}' | python3 .claude/skills/gerrit_analysis.py

# 直接传入数据分析
echo '{"changes": [...]}' | python3 .claude/skills/gerrit_analysis.py

# 无参数，使用默认配置
python3 .claude/skills/gerrit_analysis.py
```

---

## 2. build_analysis - 门禁构建分析

### 概述

从 MySQL 数据库获取门禁构建数据，进行多维度分析：
- **问题导向分析**：找出落后平台、恶化趋势、瓶颈组件
- **基础指标分析**：构建耗时分位数、各阶段占比

### 脚本位置

```
.claude/skills/build_analysis.py
```

### 调用方式

```bash
echo '<JSON参数>' | python3 .claude/skills/build_analysis.py
```

### 输入格式 (stdin JSON)

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `action` | string | ❌ | `problems` | 分析类型（见下表） |
| `days` | int | ❌ | `7` | 分析天数 |
| `baseline_name` | string | ❌ | - | 过滤特定平台（如 SM8750） |
| `top_n` | int | ❌ | `10` | 返回前 N 个结果 |

### Action 类型

#### 问题导向分析（推荐）

| Action | 说明 |
|--------|------|
| `problems` | 问题导向分析报告（**默认，推荐**） |
| `briefing` | 生成简报（用于信息流推送） |
| `lagging` | P95 落后平台分析 |
| `components` | 组件瓶颈分析 |
| `trends` | 趋势变化分析（恶化/改善） |
| `users` | 人员维度分析 |

#### 基础指标分析

| Action | 说明 |
|--------|------|
| `summary` | 完整摘要报告 |
| `metrics` | 基础指标 |
| `trend` | 趋势分析（按天/周） |
| `anomalies` | 异常检测 |
| `by_platform` | 按平台分组 |
| `percentiles` | 分位数分析 |

### 输出格式示例

**问题分析报告 (action=problems)**

```json
{
    "report_type": "problem_analysis",
    "generated_at": "2026-01-13T10:00:00",
    "analysis_period_days": 7,
    "severity": "medium",
    "summary": {
        "total_problems": 5,
        "lagging_platforms": 3,
        "worsening_platforms": 2,
        "improving_platforms": 1,
        "overall_p95_minutes": 85.5
    },
    "problems": [
        "SM8750_16 (高通骁龙8 Elite) 的P95耗时高于整体水平 25.3%，需要重点关注",
        "高通平台有 3 个型号落后，可能是该厂商的构建流程需要优化"
    ],
    "suggestions": [
        "排查落后平台的构建日志，分析耗时主要集中在哪个阶段",
        "对比健康平台和落后平台的构建配置差异"
    ],
    "details": {
        "lagging_analysis": {...},
        "component_analysis": {...},
        "trend_analysis": {...},
        "user_analysis": {...}
    }
}
```

**简报输出 (action=briefing)**

```json
{
    "briefing_type": "build_efficiency",
    "should_push": true,
    "priority": "P1",
    "severity": "high",
    "title": "SM8750_16构建耗时恶化23%",
    "summary": "SM8750平台P95超出整体25%...",
    "metrics": {...},
    "key_problems": [...],
    "key_suggestions": [...]
}
```

### 使用示例

```bash
# 问题导向分析（推荐）
echo '{"action": "problems", "days": 7}' | python3 .claude/skills/build_analysis.py

# 生成简报
echo '{"action": "briefing", "days": 7}' | python3 .claude/skills/build_analysis.py

# 分析 P95 落后平台
echo '{"action": "lagging", "days": 14}' | python3 .claude/skills/build_analysis.py

# 趋势变化分析
echo '{"action": "trends", "days": 7}' | python3 .claude/skills/build_analysis.py

# 特定平台分析
echo '{"action": "metrics", "days": 7, "baseline_name": "SM8750"}' | python3 .claude/skills/build_analysis.py
```

### 平台命名规范

| 前缀 | 厂商 | 示例 |
|------|------|------|
| `SM` | 高通 (Qualcomm) | SM8750, SM8650 |
| `MT` | 联发科 (MediaTek) | MT6991, MT6897 |

---

## 3. report_generation - 报告生成

### 概述

将分析结果转换为标准化的 Markdown 格式报告，支持多种报告类型。

### 脚本位置

```
.claude/skills/report_generation.py
```

### 调用方式

```bash
echo '<分析结果JSON>' | python3 .claude/skills/report_generation.py
```

### 输入格式 (stdin JSON)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `report_type` | string | ❌ | 报告类型（见下表） |
| `gerrit_data` | object | ❌ | Gerrit 分析数据 |
| `build_data` | object | ❌ | 构建分析数据 |
| `metrics` | object | ❌ | 向后兼容：Gerrit 指标 |
| `anomalies` | array | ❌ | 向后兼容：异常列表 |

### 报告类型

| Type | 说明 | 所需数据 |
|------|------|----------|
| `gerrit` | Gerrit 代码审查报告（默认） | `metrics`, `anomalies` |
| `build` | 门禁构建基础报告 | `build_data` |
| `build_problems` | 问题导向构建报告（**推荐**） | `build_data` |
| `combined` | 综合研发效能报告 | `gerrit_data`, `build_data` |

### 输出格式

直接输出 Markdown 格式报告到 stdout。

### 使用示例

```bash
# 生成 Gerrit 报告
echo '{"metrics": {...}, "anomalies": [...]}' | python3 .claude/skills/report_generation.py

# 生成构建问题报告（推荐）
echo '{"report_type": "build_problems", "build_data": {...}}' | python3 .claude/skills/report_generation.py

# 生成综合报告
echo '{"report_type": "combined", "gerrit_data": {...}, "build_data": {...}}' | python3 .claude/skills/report_generation.py
```

### 组合使用示例

```bash
# 分析构建问题 -> 生成报告
echo '{"action": "problems", "days": 7}' | python3 .claude/skills/build_analysis.py | \
  jq '{report_type: "build_problems", build_data: .}' | \
  python3 .claude/skills/report_generation.py > reports/daily_build_report.md
```

---

## 数据库配置

### Gerrit 数据库

```python
DB_CONFIG = {
    "host": "10.52.61.119",
    "port": 33067,  # 只读端口
    "database": "rabbit_test"
}
```

### 构建数据库

```python
BUILD_DB_CONFIG = {
    "host": "rn-test-mysql.mysql.oppo.test",
    "port": 33066,
    "database": "rn_test"
}
```

---

## 技能扩展指南

### 添加新技能

1. 在 `.claude/skills/` 目录下创建新的 Python 脚本
2. 遵循标准接口规范：stdin JSON 输入，stdout JSON 输出
3. 更新本文档，添加新技能的接口说明
4. 更新 `CLAUDE.md` 中的能力描述

### 接口规范

所有技能脚本应遵循：

```python
#!/usr/bin/env python3
"""
Skill Name
技能描述
"""

import json
import sys

def main():
    # 从 stdin 读取 JSON 参数
    input_data = sys.stdin.read().strip()
    params = json.loads(input_data) if input_data else {}
    
    # 执行技能逻辑
    result = run_skill(params)
    
    # 输出 JSON 结果到 stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

### 推荐的技能组合

| 场景 | 技能组合 |
|------|----------|
| 日常监控 | `build_analysis(briefing)` → 推送简报 |
| 深度分析 | `build_analysis(problems)` → `report_generation(build_problems)` |
| 综合报告 | `gerrit_analysis` + `build_analysis` → `report_generation(combined)` |

