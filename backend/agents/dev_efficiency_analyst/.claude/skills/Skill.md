# 研发效能分析官 - 技能清单

本文档定义了 研发效能分析官 的所有可用技能及其接口规范。

---

## 技能概览

| 技能 ID | 名称 | 说明 | 优先级 |
|---------|------|------|--------|
| `gerrit_analysis` | Gerrit代码审查分析 | 多维度分析代码变更数据：高产人员、工作负荷、分支健康、贡献度、ALM关联 | 核心 |
| `build_analysis` | 门禁构建分析 | 分析构建耗时、瓶颈和趋势 | 核心 |
| `report_generation` | 报告生成 | 生成标准化 Markdown 报告 | 辅助 |

---

## 1. gerrit_analysis - Gerrit代码审查分析（增强版）

### 概述

从 MySQL 数据库获取 Gerrit 代码审查数据，支持多维度分析：

- **高产人员特征（归因分析）**：识别高效能人员的共同特点
- **工作负荷分析**：个人和团队维度的工作量统计
- **分支管理和健康度**：分支活跃度、合并待办、锁定状态
- **个人和团队贡献度**：代码贡献量、变更质量评估
- **ALM关联分析**：多人协作、跨分支变更、缺陷vs需求分布
- **代码审查效率指标**：合并率、返工率、异常检测

### 脚本位置

```
.claude/skills/gerrit_analysis.py
```

### 调用方式

```bash
echo '<JSON参数>' | python3 .claude/skills/gerrit_analysis.py
```

### 输入格式 (stdin JSON)

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `action` | string | ❌ | `summary` | 分析类型（见下表） |
| `days` | int | ❌ | `30` | 分析最近 N 天的数据 |
| `limit` | int | ❌ | `20` | 返回结果数量限制 |
| `scope` | string | ❌ | `individual` | 范围：`individual` 或 `team` |
| `owner_wkno` | string | ❌ | - | 过滤特定人员工号 |
| `department` | string | ❌ | - | 过滤特定部门 |
| `repo` | string | ❌ | - | 过滤特定仓库 |
| `issue_id` | int | ❌ | - | 过滤特定 ALM ID |
| `analysis_type` | string | ❌ | `collaboration` | ALM分析类型 |

### Action 类型

#### 综合分析

| Action | 说明 |
|--------|------|
| `summary` | 综合概览报告（**默认，推荐**） |
| `review_metrics` | 代码审查效率指标 |

#### 人员分析

| Action | 说明 |
|--------|------|
| `top_contributors` | 高产人员特征分析（归因分析） |
| `workload` | 工作负荷分析（支持 `scope=individual/team`） |
| `contribution` | 贡献度分析（支持 `scope=individual/team`） |

#### 分支与ALM分析

| Action | 说明 |
|--------|------|
| `branch_health` | 分支管理和健康度分析 |
| `alm_analysis` | ALM关联分析（支持多种 `analysis_type`） |

### ALM 分析类型 (analysis_type)

| Type | 说明 |
|------|------|
| `collaboration` | 同一ALM多人协作分析 |
| `branches` | 单ALM涉及分支数分析 |
| `types` | 缺陷vs需求类型分布 |

#### 年度效率分析（新增）

| Action | 说明 | 参数 |
|--------|------|------|
| `time_efficiency_loss` | **时间效率损耗分析（推荐）** | `days`, `departments` |
| `briefing` | **简报生成（用于信息流推送）** | `days`, `departments` |
| `ui_schema` | **A2UI Schema生成（用于动态UI渲染）** | `days`, `departments` |
| `branch_convergence` | 分支收敛度分析 | `days`, `departments` |
| `change_convergence` | Change ID收敛分析（返工率） | `days`, `departments`, `limit` |
| `contributor_retention` | 人员留存与熟练度分析 | `year_current`, `year_previous`, `departments` |
| `story_duration` | Story/ALM跨度分析 | `days`, `departments`, `limit` |
| `annual_report` | 年度效率综合报告 | `year`, `departments` |

### 业务模型说明

```
ALM层级                          Gerrit层级
┌─────────┐
│  Epic   │
└────┬────┘
     ↓
┌─────────┐
│ Feature │
└────┬────┘
     ↓
┌─────────┐     1:N      ┌───────────┐     1:N      ┌───────────────┐
│  Story  │ ──────────→  │ change_id │ ──────────→  │  记录(分支)   │
│(alm_id) │  开发拆分task │ (逻辑变更) │   跨分支提交  │               │
└─────────┘              └───────────┘              └───────────────┘
```

**`time_efficiency_loss` 是从人的时间效率角度的综合分析，包含：**

| 维度 | 分析内容 | 异常表现 |
|------|---------|---------|
| 分支分散度 | 人均活跃分支数 | >10个说明工作分散 |
| Story拆分 | alm_id → change_id 映射 | 1个Story对应>10个change_id可能是借单或拆分不合理 |
| Change分支分布 | change_id → 记录数 | 同分支多次记录是异常（反复提交/借单） |
| 返工率 | patchset分布 | 一次性通过率<50%需关注 |

**异常原因识别：**

| 现象 | 可能原因 |
|------|---------|
| 1个alm_id对应多个change_id | 借单、Story定义不清晰、边做边补 |
| 1个change_id对应多个记录(同分支) | 反复提交-放弃、借单、合并后重提 |
| 1个change_id对应多个记录(跨分支) | cherry-pick到多个release分支（正常） |

### 部门过滤 (departments)

支持按部门过滤分析数据，默认包含四个重点部门：
- 系统开发部
- 应用开发一部
- 应用开发二部
- 互联通信开发部

---

### 输出格式示例

#### 综合概览 (action=summary)

```json
{
    "action": "summary",
    "period_days": 30,
    "overview": {
        "total_changes": 205,
        "merge_rate": 78.5,
        "rework_rate": 5.85,
        "contributors": 35,
        "repos": 42
    },
    "top_contributors": [
        {"name": "张三", "changes": 74, "efficiency": 85.5}
    ],
    "branch_health": {
        "total_branches": 866179,
        "lock_rate": 4.73
    },
    "anomalies": [],
    "timestamp": "2026-01-20T10:00:00"
}
```

#### 高产人员分析 (action=top_contributors)

```json
{
    "action": "top_contributors",
    "period_days": 30,
    "contributors": [
        {
            "name": "张三",
            "wkno": "80123456",
            "department": "/OPPO公司/软件工程系统/...",
            "change_count": 74,
            "total_lines": 16235,
            "insertions": 15709,
            "deletions": 526,
            "repo_count": 7,
            "alm_count": 31,
            "merge_rate": 92.7,
            "shuttle_bus_rate": 65.0,
            "avg_patchset": 1.1,
            "avg_files_per_change": 1.1,
            "efficiency_score": 85.5
        }
    ],
    "top5_characteristics": {
        "avg_merge_rate": 90.5,
        "avg_shuttle_bus_rate": 60.0,
        "avg_patchset": 1.2,
        "avg_repo_breadth": 4.8,
        "insight": "高合并成功率(>90%)，低返工率(平均<1.5次修订)"
    },
    "timestamp": "2026-01-20T10:00:00"
}
```

#### 工作负荷分析 (action=workload)

**个人维度 (scope=individual)**
```json
{
    "action": "workload",
    "scope": "individual",
    "period_days": 30,
    "workloads": [
        {
            "name": "张三",
            "wkno": "80123456",
            "department": "/OPPO公司/...",
            "change_count": 47,
            "total_lines": 10833,
            "repo_count": 3,
            "alm_count": 23,
            "active_days": 20,
            "changes_per_day": 2.4,
            "lines_per_day": 542
        }
    ]
}
```

**团队维度 (scope=team)**
```json
{
    "action": "workload",
    "scope": "team",
    "period_days": 30,
    "teams": [
        {
            "department": "/OPPO公司/软件工程系统/...",
            "member_count": 7,
            "change_count": 49,
            "total_lines": 9933,
            "repo_count": 9,
            "alm_count": 7,
            "merge_rate": 67.3,
            "changes_per_member": 7.0,
            "lines_per_member": 1419
        }
    ]
}
```

#### 分支健康度 (action=branch_health)

```json
{
    "action": "branch_health",
    "period_days": 30,
    "branches": [
        {
            "branch": "master",
            "change_count": 57,
            "contributor_count": 12,
            "merged_count": 26,
            "pending_count": 29,
            "merge_rate": 45.6,
            "last_activity": "2026-01-19 17:07:45",
            "health_status": "warning"
        }
    ],
    "release_backlogs": [
        {
            "branch": "u/ossi/release-14.0.0",
            "total": 6,
            "need_merge": 1,
            "finished": 0,
            "completion_rate": 0.0
        }
    ],
    "branch_overview": {
        "total_branches": 866179,
        "locked_branches": 40952,
        "lock_rate": 4.73
    }
}
```

#### ALM多人协作分析 (action=alm_analysis, analysis_type=collaboration)

```json
{
    "action": "alm_analysis",
    "analysis_type": "collaboration",
    "period_days": 90,
    "collaborations": [
        {
            "issue_id": 6260576,
            "owner_count": 6,
            "change_count": 76,
            "owners": "张三, 李四, 王五...",
            "branch_count": 20,
            "duration_days": 81,
            "start_time": "2025-10-30 10:46:17",
            "end_time": "2026-01-19 11:53:24"
        }
    ],
    "insight": "共有 5 个ALM存在多人协作"
}
```

#### ALM分支分析 (action=alm_analysis, analysis_type=branches)

```json
{
    "action": "alm_analysis",
    "analysis_type": "branches",
    "period_days": 90,
    "alm_branches": [
        {
            "issue_id": 5675693,
            "branch_count": 15,
            "change_count": 50,
            "branches": "master, release-1.0, ...",
            "duration_days": 54,
            "health_risk": "high"
        }
    ],
    "risk_summary": {
        "high_risk_count": 3,
        "insight": "3 个ALM涉及超过10个分支，可能存在分支管理风险"
    }
}
```

#### ALM类型分布 (action=alm_analysis, analysis_type=types)

```json
{
    "action": "alm_analysis",
    "analysis_type": "types",
    "period_days": 90,
    "type_distribution": [
        {"type": "软件测试缺陷", "count": 6364, "alm_count": 5000, "owner_count": 200},
        {"type": "技术故事", "count": 937, "alm_count": 800, "owner_count": 150}
    ],
    "summary": {
        "total_changes": 10000,
        "defect_changes": 7500,
        "requirement_changes": 2500,
        "defect_ratio": 75.0,
        "insight": "缺陷修复占比过高(>70%)，建议关注代码质量"
    }
}
```

#### 时间效率损耗分析 (action=time_efficiency_loss) 【推荐】

```json
{
    "action": "time_efficiency_loss",
    "period_days": 365,
    "summary": {
        "total_contributors": 883,
        "total_records": 28903,
        "total_change_ids": 25000,
        "total_stories": 7384,
        "avg_branches_per_person": 25.9,
        "one_shot_rate": 33.9,
        "ideal_story_rate": 63.3
    },
    "branch_distribution": {
        "avg_branches_per_person": 25.9,
        "high_branch_people_count": 50,
        "high_branch_people_rate": 100.0,
        "top_scattered_people": [
            {"name": "张三", "wkno": "80123456", "branch_count": 40, "change_count": 78, "repo_count": 14}
        ]
    },
    "story_convergence": {
        "distribution": {
            "1个change_id(理想)": 4672,
            "2-3个change_id(正常)": 1500,
            "4-10个change_id(偏多)": 800,
            "10个以上change_id(异常)": 412
        },
        "high_change_stories": [
            {"issue_id": 8901033, "change_id_count": 126, "contributor_count": 10, "possible_issue": "借单(多人挂同一alm_id)"}
        ]
    },
    "change_branch_analysis": {
        "reason_distribution": {
            "cherry-pick(单仓库)": {"change_id_count": 271791, "total_records": 500000},
            "cherry-pick(多仓库)": {"change_id_count": 1863, "total_records": 20000},
            "同分支多次记录(异常)": {"change_id_count": 5879, "total_records": 15000}
        },
        "abnormal_changes": [
            {
                "change_id": "I9eda6d58...",
                "branch": "master",
                "repo": "oplus/app/xxx",
                "record_count": 9,
                "abandoned_count": 8,
                "merged_count": 1,
                "issue_count": 2,
                "possible_reason": "反复提交-放弃(可能门禁失败)"
            }
        ]
    },
    "rework_analysis": {
        "total_changes": 28903,
        "one_shot_count": 9790,
        "one_shot_rate": 33.9,
        "total_rework_count": 45126,
        "avg_patchset": 2.56,
        "distribution": {
            "1次通过": 9790,
            "2次通过": 10651,
            "3次通过": 3642,
            "3次以上": 4820
        }
    },
    "insights": [
        {"category": "分支分散度", "severity": "high", "finding": "人均活跃分支25.9个，工作非常分散"},
        {"category": "返工率", "severity": "high", "finding": "一次性通过率仅33.9%，总返工45126次"}
    ]
}
```

#### 分支收敛度分析 (action=branch_convergence)

```json
{
    "action": "branch_convergence",
    "period_days": 365,
    "summary": {
        "total_active_branches": 1500,
        "branch_types": 6,
        "zombie_branch_count": 25
    },
    "branch_type_distribution": [
        {"type": "release", "branch_count": 120, "change_count": 5000, "merge_rate": 85.5},
        {"type": "master", "branch_count": 50, "change_count": 3000, "merge_rate": 90.2},
        {"type": "feature", "branch_count": 800, "change_count": 15000, "merge_rate": 75.3}
    ],
    "zombie_branches": [
        {"branch": "feature/old-xxx", "last_activity": "2024-06-15", "pending_count": 3}
    ],
    "recommendations": [
        "Feature分支数量过多(800个)，建议合并后及时删除"
    ]
}
```

#### Change ID收敛分析 (action=change_convergence)

```json
{
    "action": "change_convergence",
    "period_days": 365,
    "summary": {
        "total_changes": 50000,
        "one_shot_rate": 45.5,
        "high_rework_rate": 15.2
    },
    "patchset_distribution": [
        {"range": "1次提交", "count": 22750, "percentage": 45.5},
        {"range": "2次提交", "count": 12500, "percentage": 25.0},
        {"range": "3次提交", "count": 7500, "percentage": 15.0}
    ],
    "department_comparison": [
        {"department": "系统开发部", "avg_patchset": 2.1, "high_patchset_rate": 12.5}
    ],
    "insights": [
        "一次性通过率较低(45.5%)，说明代码质量或评审流程有优化空间"
    ]
}
```

#### 人员留存分析 (action=contributor_retention)

```json
{
    "action": "contributor_retention",
    "years": {"previous": 2024, "current": 2025},
    "summary": {
        "previous_year_contributors": 150,
        "current_year_contributors": 160,
        "retained_count": 120,
        "churned_count": 30,
        "new_count": 40,
        "retention_rate": 80.0,
        "churn_rate": 20.0,
        "new_rate": 25.0,
        "total_lines_lost": 500000
    },
    "retained_contributors": [
        {"name": "张三", "2024_changes": 200, "2025_changes": 180, "efficiency_trend": "improved"}
    ],
    "churned_contributors": [
        {"name": "李四", "2024_changes": 150, "total_lines_lost": 50000}
    ],
    "insights": [
        "人员留存率较高(80.0%)，团队稳定性良好"
    ]
}
```

#### Story跨度分析 (action=story_duration)

```json
{
    "action": "story_duration",
    "period_days": 365,
    "summary": {
        "total_stories": 3000,
        "avg_duration_days": 15.5,
        "long_story_count": 450,
        "long_story_rate": 15.0,
        "cross_branch_story_count": 25
    },
    "duration_distribution": [
        {"range": "1-7天", "count": 1500, "percentage": 50.0},
        {"range": "8-14天", "count": 750, "percentage": 25.0}
    ],
    "long_duration_stories": [
        {"issue_id": 12345, "duration_days": 65, "contributor_count": 5, "risk_level": "high"}
    ],
    "insights": [
        "长周期Story(>30天)占比15%，建议拆分大Story提高交付效率"
    ]
}
```

#### 年度效率综合报告 (action=annual_report)

```json
{
    "action": "annual_efficiency_report",
    "year": 2024,
    "target_departments": ["系统开发部", "应用开发一部", "应用开发二部", "互联通信开发部"],
    "executive_summary": {
        "branch_health": {"total_branches": 1500, "zombie_branches": 25, "status": "healthy"},
        "change_efficiency": {"one_shot_rate": 55.0, "high_rework_rate": 12.0, "status": "healthy"},
        "team_stability": {"retention_rate": 80.0, "churn_rate": 20.0, "status": "healthy"},
        "delivery_efficiency": {"avg_story_duration": 15.5, "long_story_rate": 15.0, "status": "healthy"}
    },
    "recommendations": [
        {"category": "代码质量", "priority": "medium", "issue": "一次性通过率仅55%", "suggestion": "加强代码自测"}
    ]
}
```

---

### 使用示例

```bash
# 综合概览（推荐）
echo '{"action": "summary", "days": 30}' | python3 .claude/skills/gerrit_analysis.py

# 高产人员分析
echo '{"action": "top_contributors", "days": 30, "limit": 10}' | python3 .claude/skills/gerrit_analysis.py

# 个人工作负荷
echo '{"action": "workload", "scope": "individual", "days": 30}' | python3 .claude/skills/gerrit_analysis.py

# 团队工作负荷
echo '{"action": "workload", "scope": "team", "days": 30}' | python3 .claude/skills/gerrit_analysis.py

# 分支健康度
echo '{"action": "branch_health", "days": 30}' | python3 .claude/skills/gerrit_analysis.py

# ALM多人协作分析
echo '{"action": "alm_analysis", "analysis_type": "collaboration", "days": 90}' | python3 .claude/skills/gerrit_analysis.py

# ALM分支分析
echo '{"action": "alm_analysis", "analysis_type": "branches", "days": 90}' | python3 .claude/skills/gerrit_analysis.py

# ALM类型分布
echo '{"action": "alm_analysis", "analysis_type": "types", "days": 90}' | python3 .claude/skills/gerrit_analysis.py

# 代码审查效率指标
echo '{"action": "review_metrics", "days": 7}' | python3 .claude/skills/gerrit_analysis.py

# ============ 时间效率损耗分析（新增，推荐） ============

# 时间效率损耗综合分析（最推荐，从人的时间角度）
echo '{"action": "time_efficiency_loss", "days": 365, "departments": ["系统开发部", "应用开发一部", "应用开发二部", "互联通信开发部"]}' | python3 .claude/skills/gerrit_analysis.py

# ============ 简报与UI Schema（新增） ============

# 生成简报（用于信息流推送）
echo '{"action": "briefing", "days": 7}' | python3 .claude/skills/gerrit_analysis.py

# 生成A2UI Schema（用于App动态渲染）
echo '{"action": "ui_schema", "days": 7}' | python3 .claude/skills/gerrit_analysis.py

# ============ 细分维度分析 ============

# 分支收敛度分析
echo '{"action": "branch_convergence", "days": 365}' | python3 .claude/skills/gerrit_analysis.py

# Change ID收敛分析（返工率）
echo '{"action": "change_convergence", "days": 365, "departments": ["系统开发部", "应用开发一部"]}' | python3 .claude/skills/gerrit_analysis.py

# 人员留存分析（24年 vs 25年）
echo '{"action": "contributor_retention", "year_current": 2025, "year_previous": 2024}' | python3 .claude/skills/gerrit_analysis.py

# Story跨度分析
echo '{"action": "story_duration", "days": 365}' | python3 .claude/skills/gerrit_analysis.py

# 年度效率综合报告
echo '{"action": "annual_report", "year": 2024, "departments": ["系统开发部", "应用开发一部", "应用开发二部", "互联通信开发部"]}' | python3 .claude/skills/gerrit_analysis.py
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

**主要数据表：**

| 表名 | 数据量 | 说明 |
|------|--------|------|
| `gerrit_change` | 128万+ | 代码变更记录 |
| `user` | - | 用户信息（含部门路径） |
| `user_count_2024` | - | 年度用户统计 |
| `almid_commit_exemption` | 1.4万+ | ALM工作项关联 |
| `release_check_by_change` | 5.4万+ | Release分支合并状态 |
| `repo_branch` | 86万+ | 分支信息 |
| `lock_repo_branch` | 4万+ | 锁定分支 |

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
| 日常监控 | `gerrit_analysis(summary)` + `build_analysis(briefing)` → 推送简报 |
| 人员分析 | `gerrit_analysis(top_contributors)` + `gerrit_analysis(workload)` |
| 分支管理 | `gerrit_analysis(branch_health)` + `gerrit_analysis(alm_analysis:branches)` |
| ALM追踪 | `gerrit_analysis(alm_analysis:collaboration)` + `gerrit_analysis(alm_analysis:types)` |
| 深度分析 | `build_analysis(problems)` → `report_generation(build_problems)` |
| 综合报告 | `gerrit_analysis(summary)` + `build_analysis(problems)` → `report_generation(combined)` |

---

## 分析维度速查表

### Gerrit 分析维度

| 维度 | Action | 关键指标 |
|------|--------|----------|
| 高产人员特征 | `top_contributors` | efficiency_score, merge_rate, shuttle_bus_rate |
| 个人工作负荷 | `workload` (scope=individual) | changes_per_day, lines_per_day |
| 团队工作负荷 | `workload` (scope=team) | changes_per_member, lines_per_member |
| 分支健康度 | `branch_health` | health_status, pending_count, lock_rate |
| 个人贡献度 | `contribution` (scope=individual) | total_lines, quality_score |
| 团队贡献度 | `contribution` (scope=team) | total_lines, contributors |
| ALM多人协作 | `alm_analysis` (type=collaboration) | owner_count, duration_days |
| ALM分支分析 | `alm_analysis` (type=branches) | branch_count, health_risk |
| ALM类型分布 | `alm_analysis` (type=types) | defect_ratio, insight |
| 审查效率 | `review_metrics` | merge_rate, rework_rate |

### 时间效率损耗分析维度（核心，推荐）

| 维度 | Action | 关键指标 | 分析问题 |
|------|--------|----------|----------|
| **时间效率损耗** | `time_efficiency_loss` | 见下表 | 开发人员时间花在哪里？效率损耗在哪？ |

**`time_efficiency_loss` 四大分析维度：**

| 维度 | 分析内容 | 关键指标 | 异常判断 |
|------|---------|---------|---------|
| **1. 分支分散度** | 人均活跃分支数 | `avg_branches_per_person` | >10个说明工作分散 |
| **2. Story拆分** | alm_id → change_id 映射 | `ideal_story_rate` | <50%说明借单或拆分不合理 |
| **3. Change分支分布** | change_id → 记录数原因分析 | `reason_distribution` | 同分支多次记录是异常 |
| **4. 返工率** | patchset分布 | `one_shot_rate` | <50%需关注 |

**异常原因对照表：**

| 现象 | 数据表现 | 可能原因 |
|------|---------|---------|
| 1个alm_id对应>10个change_id | `high_change_stories` | ① 借单 ② Story定义不清晰 ③ 边做边补 |
| 1个change_id同分支多次记录 | `abnormal_changes` | ① 反复提交-放弃 ② 借单(不同issue_id) ③ 合并后重提 |
| 1个change_id跨多分支 | `cherry-pick(单/多仓库)` | 正常：cherry-pick到多个release分支 |

### 细分维度分析（补充）

| 维度 | Action | 关键指标 | 分析问题 |
|------|--------|----------|----------|
| 分支收敛度 | `branch_convergence` | branch_type_distribution, zombie_branches | 分支数量是否需要收敛？release/master/feature分支比例是否合理？ |
| Change ID收敛 | `change_convergence` | one_shot_rate, high_rework_rate, patchset_distribution | 一个changeid对应多笔提交？返工率是否过高？ |
| 人员留存 | `contributor_retention` | retention_rate, churn_rate, efficiency_trend | 24年高产人员25年还在吗？熟练度是否提升？ |
| Story跨度 | `story_duration` | avg_duration_days, long_story_rate, cross_branch_stories | Story周期是否过长？是否跨多分支？ |
| 年度综合报告 | `annual_report` | executive_summary, recommendations | 整体效率如何？哪些方面需要改进？ |

### 重点部门

年度效率分析默认关注以下四个部门：
- **系统开发部**
- **应用开发一部**
- **应用开发二部**
- **互联通信开发部**

可通过 `departments` 参数自定义过滤。

