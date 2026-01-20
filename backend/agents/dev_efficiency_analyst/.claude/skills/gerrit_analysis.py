#!/usr/bin/env python3
"""
Gerrit Analysis Skill - 增强版
分析Gerrit代码审查数据的能力 - 从MySQL数据库获取数据

支持的分析维度：
1. 高产人员特征（归因分析）
2. 工作负荷（个人和团队）
3. 分支管理和健康度
4. 个人和团队贡献度
5. ALM关联分析
6. 代码审查效率指标
"""

import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional


def _to_number(val):
    """将数据库返回值转换为Python数字类型"""
    if val is None:
        return 0
    if isinstance(val, Decimal):
        return float(val)
    return val

# 数据库配置
DB_CONFIG = {
    "dialect": "mysql",
    "host": "10.52.61.119",
    "port": 33067,
    "username": "ee_read",
    "password": "OdX0M4nAxRjtN_wXMyG34mYyZPXEwLOS",
    "database": "rabbit_test"
}


def get_db_connection():
    """获取MySQL数据库连接"""
    try:
        import pymysql
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["username"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except ImportError:
        raise ImportError("pymysql is required. Install it with: pip install pymysql")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")


# ============================================================
# 1. 高产人员特征（归因分析）
# ============================================================
def analyze_top_contributors(days: int = 30, limit: int = 20) -> Dict[str, Any]:
    """
    分析高产人员特征，识别高效能人员的共同特点
    
    分析维度：
    - 变更数量和代码行数
    - 活跃时段分布
    - 班车率（按时提交率）
    - 涉及仓库广度
    - 合并成功率
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 查询高产人员统计
            sql = """
                SELECT 
                    gc.owner,
                    gc.owner_wkno,
                    u.depart_name_path,
                    COUNT(*) as change_count,
                    SUM(gc.insertions + gc.deletions) as total_lines,
                    SUM(gc.insertions) as total_insertions,
                    SUM(gc.deletions) as total_deletions,
                    COUNT(DISTINCT gc.repo) as repo_count,
                    COUNT(DISTINCT gc.issue_id) as alm_count,
                    SUM(CASE WHEN gc.status = 'MERGED' THEN 1 ELSE 0 END) as merged_count,
                    SUM(CASE WHEN gc.status = 'ABANDONED' THEN 1 ELSE 0 END) as abandoned_count,
                    SUM(CASE WHEN gc.is_shuttle_bus = 1 THEN 1 ELSE 0 END) as shuttle_bus_count,
                    AVG(gc.patchset_id) as avg_patchset,
                    AVG(gc.changed_file_count) as avg_files_per_change
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY gc.owner, gc.owner_wkno, u.depart_name_path
                HAVING change_count >= 5
                ORDER BY change_count DESC
                LIMIT %s
            """
            cursor.execute(sql, [days, limit])
            results = cursor.fetchall()
            
            contributors = []
            for row in results:
                total = _to_number(row['change_count'])
                merged = _to_number(row['merged_count']) or 0
                shuttle = _to_number(row['shuttle_bus_count']) or 0
                
                contributors.append({
                    "name": row['owner'],
                    "wkno": row['owner_wkno'],
                    "department": row['depart_name_path'],
                    "change_count": int(total),
                    "total_lines": int(_to_number(row['total_lines']) or 0),
                    "insertions": int(_to_number(row['total_insertions']) or 0),
                    "deletions": int(_to_number(row['total_deletions']) or 0),
                    "repo_count": int(_to_number(row['repo_count'])),
                    "alm_count": int(_to_number(row['alm_count'])),
                    "merge_rate": round(merged / total * 100, 1) if total > 0 else 0,
                    "shuttle_bus_rate": round(shuttle / total * 100, 1) if total > 0 else 0,
                    "avg_patchset": round(_to_number(row['avg_patchset']) or 1, 1),
                    "avg_files_per_change": round(_to_number(row['avg_files_per_change']) or 0, 1),
                    "efficiency_score": _calculate_efficiency_score(row)
                })
            
            # 分析高产人员共同特征
            if len(contributors) >= 5:
                top5 = contributors[:5]
                characteristics = {
                    "avg_merge_rate": round(sum(c['merge_rate'] for c in top5) / 5, 1),
                    "avg_shuttle_bus_rate": round(sum(c['shuttle_bus_rate'] for c in top5) / 5, 1),
                    "avg_patchset": round(sum(c['avg_patchset'] for c in top5) / 5, 1),
                    "avg_repo_breadth": round(sum(c['repo_count'] for c in top5) / 5, 1),
                    "insight": _generate_contributor_insight(top5)
                }
            else:
                characteristics = {}
            
            return {
                "action": "top_contributors",
                "period_days": days,
                "contributors": contributors,
                "top5_characteristics": characteristics,
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


def _calculate_efficiency_score(row: Dict) -> float:
    """计算效率综合评分"""
    total = _to_number(row['change_count'])
    if total == 0:
        return 0
    
    merged = _to_number(row['merged_count']) or 0
    shuttle = _to_number(row['shuttle_bus_count']) or 0
    avg_patchset = _to_number(row['avg_patchset']) or 1
    
    # 评分因素：合并率 + 班车率 - 返工惩罚
    merge_score = (merged / total) * 40
    shuttle_score = (shuttle / total) * 30
    rework_penalty = max(0, (avg_patchset - 1) * 5)  # 每多一次patchset扣5分
    
    return round(merge_score + shuttle_score + 30 - rework_penalty, 1)


def _generate_contributor_insight(top5: List[Dict]) -> str:
    """生成高产人员特征洞察"""
    avg_merge = sum(c['merge_rate'] for c in top5) / 5
    avg_shuttle = sum(c['shuttle_bus_rate'] for c in top5) / 5
    avg_patchset = sum(c['avg_patchset'] for c in top5) / 5
    
    insights = []
    if avg_merge > 90:
        insights.append("高合并成功率(>90%)")
    if avg_shuttle > 60:
        insights.append("高班车率(>60%)")
    if avg_patchset < 1.5:
        insights.append("低返工率(平均<1.5次修订)")
    
    return "，".join(insights) if insights else "无明显共同特征"


# ============================================================
# 2. 工作负荷分析（个人和团队）
# ============================================================
def analyze_workload(
    days: int = 30, 
    scope: str = "individual",  # "individual" or "team"
    owner_wkno: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    分析工作负荷
    
    个人维度：变更数、代码行数、涉及仓库、涉及ALM
    团队维度：按部门聚合统计
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if scope == "team":
                return _analyze_team_workload(cursor, days, department, limit)
            else:
                return _analyze_individual_workload(cursor, days, owner_wkno, limit)
    finally:
        connection.close()


def _analyze_individual_workload(cursor, days: int, owner_wkno: Optional[str], limit: int) -> Dict:
    """分析个人工作负荷"""
    sql = """
        SELECT 
            gc.owner,
            gc.owner_wkno,
            u.depart_name_path,
            COUNT(*) as change_count,
            SUM(gc.insertions + gc.deletions) as total_lines,
            COUNT(DISTINCT gc.repo) as repo_count,
            COUNT(DISTINCT gc.issue_id) as alm_count,
            COUNT(DISTINCT DATE(gc.created_at)) as active_days,
            MIN(gc.created_at) as first_change,
            MAX(gc.created_at) as last_change
        FROM gerrit_change gc
        LEFT JOIN user u ON gc.owner_wkno = u.wkno
        WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    """
    params = [days]
    
    if owner_wkno:
        sql += " AND gc.owner_wkno = %s"
        params.append(owner_wkno)
    
    sql += """
        GROUP BY gc.owner, gc.owner_wkno, u.depart_name_path
        ORDER BY change_count DESC
        LIMIT %s
    """
    params.append(limit)
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    
    workloads = []
    for row in results:
        active_days = _to_number(row['active_days']) or 1
        change_count = _to_number(row['change_count'])
        total_lines = _to_number(row['total_lines']) or 0
        workloads.append({
            "name": row['owner'],
            "wkno": row['owner_wkno'],
            "department": row['depart_name_path'],
            "change_count": int(change_count),
            "total_lines": int(total_lines),
            "repo_count": int(_to_number(row['repo_count'])),
            "alm_count": int(_to_number(row['alm_count'])),
            "active_days": int(active_days),
            "changes_per_day": round(change_count / active_days, 1),
            "lines_per_day": round(total_lines / active_days, 0),
            "first_change": str(row['first_change']) if row['first_change'] else None,
            "last_change": str(row['last_change']) if row['last_change'] else None
        })
    
    return {
        "action": "workload",
        "scope": "individual",
        "period_days": days,
        "workloads": workloads,
        "timestamp": datetime.now().isoformat()
    }


def _analyze_team_workload(cursor, days: int, department: Optional[str], limit: int) -> Dict:
    """分析团队工作负荷"""
    sql = """
        SELECT 
            u.depart_name_path,
            COUNT(*) as change_count,
            SUM(gc.insertions + gc.deletions) as total_lines,
            COUNT(DISTINCT gc.owner_wkno) as member_count,
            COUNT(DISTINCT gc.repo) as repo_count,
            COUNT(DISTINCT gc.issue_id) as alm_count,
            SUM(CASE WHEN gc.status = 'MERGED' THEN 1 ELSE 0 END) as merged_count
        FROM gerrit_change gc
        JOIN user u ON gc.owner_wkno = u.wkno
        WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    """
    params = [days]
    
    if department:
        sql += " AND u.depart_name_path LIKE %s"
        params.append(f"%{department}%")
    
    sql += """
        GROUP BY u.depart_name_path
        HAVING member_count >= 2
        ORDER BY change_count DESC
        LIMIT %s
    """
    params.append(limit)
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    
    teams = []
    for row in results:
        total = _to_number(row['change_count'])
        merged = _to_number(row['merged_count']) or 0
        members = _to_number(row['member_count'])
        total_lines = _to_number(row['total_lines']) or 0
        
        teams.append({
            "department": row['depart_name_path'],
            "member_count": int(members),
            "change_count": int(total),
            "total_lines": int(total_lines),
            "repo_count": int(_to_number(row['repo_count'])),
            "alm_count": int(_to_number(row['alm_count'])),
            "merge_rate": round(merged / total * 100, 1) if total > 0 else 0,
            "changes_per_member": round(total / members, 1) if members > 0 else 0,
            "lines_per_member": round(total_lines / members, 0) if members > 0 else 0
        })
    
    return {
        "action": "workload",
        "scope": "team",
        "period_days": days,
        "teams": teams,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# 3. 分支管理和健康度
# ============================================================
def analyze_branch_health(days: int = 30, repo: Optional[str] = None) -> Dict[str, Any]:
    """
    分析分支健康度
    
    分析维度：
    - 分支活跃度
    - 合并待办情况
    - 跨分支变更统计
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 1. 分支活跃度统计
            sql = """
                SELECT 
                    branch,
                    COUNT(*) as change_count,
                    COUNT(DISTINCT owner_wkno) as contributor_count,
                    SUM(CASE WHEN status = 'MERGED' THEN 1 ELSE 0 END) as merged_count,
                    SUM(CASE WHEN status = 'NEW' THEN 1 ELSE 0 END) as pending_count,
                    MAX(created_at) as last_activity
                FROM gerrit_change
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            params = [days]
            
            if repo:
                sql += " AND repo = %s"
                params.append(repo)
            
            sql += """
                GROUP BY branch
                ORDER BY change_count DESC
                LIMIT 20
            """
            
            cursor.execute(sql, params)
            branch_stats = cursor.fetchall()
            
            branches = []
            for row in branch_stats:
                total = _to_number(row['change_count'])
                merged = _to_number(row['merged_count']) or 0
                pending = _to_number(row['pending_count']) or 0
                
                branches.append({
                    "branch": row['branch'],
                    "change_count": int(total),
                    "contributor_count": int(_to_number(row['contributor_count'])),
                    "merged_count": int(merged),
                    "pending_count": int(pending),
                    "merge_rate": round(merged / total * 100, 1) if total > 0 else 0,
                    "last_activity": str(row['last_activity']) if row['last_activity'] else None,
                    "health_status": _assess_branch_health(merged, pending, total)
                })
            
            # 2. Release分支合并待办
            cursor.execute("""
                SELECT 
                    release_branch,
                    COUNT(*) as total_count,
                    SUM(CASE WHEN need_merge = 1 THEN 1 ELSE 0 END) as need_merge_count,
                    SUM(CASE WHEN is_finished = 1 THEN 1 ELSE 0 END) as finished_count
                FROM release_check_by_change
                WHERE updated_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY release_branch
                ORDER BY need_merge_count DESC
                LIMIT 10
            """, [days])
            
            release_backlogs = []
            for row in cursor.fetchall():
                need = _to_number(row['need_merge_count']) or 0
                finished = _to_number(row['finished_count']) or 0
                release_backlogs.append({
                    "branch": row['release_branch'],
                    "total": int(_to_number(row['total_count'])),
                    "need_merge": int(need),
                    "finished": int(finished),
                    "completion_rate": round(finished / need * 100, 1) if need > 0 else 100
                })
            
            # 3. 锁定分支统计
            cursor.execute("SELECT COUNT(*) as cnt FROM lock_repo_branch")
            locked_count = int(_to_number(cursor.fetchone()['cnt']))
            
            cursor.execute("SELECT COUNT(*) as cnt FROM repo_branch")
            total_branch_count = int(_to_number(cursor.fetchone()['cnt']))
            
            return {
                "action": "branch_health",
                "period_days": days,
                "branches": branches,
                "release_backlogs": release_backlogs,
                "branch_overview": {
                    "total_branches": total_branch_count,
                    "locked_branches": locked_count,
                    "lock_rate": round(locked_count / total_branch_count * 100, 2) if total_branch_count > 0 else 0
                },
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


def _assess_branch_health(merged: int, pending: int, total: int) -> str:
    """评估分支健康状态"""
    if total == 0:
        return "inactive"
    merge_rate = merged / total
    pending_rate = pending / total
    
    if pending_rate > 0.3:
        return "warning"  # 大量待合并
    elif merge_rate > 0.8:
        return "healthy"
    elif merge_rate > 0.5:
        return "normal"
    else:
        return "concern"


# ============================================================
# 4. 个人和团队贡献度
# ============================================================
def analyze_contribution(
    days: int = 30,
    scope: str = "individual",
    limit: int = 20
) -> Dict[str, Any]:
    """
    分析贡献度
    
    维度：代码贡献量、变更质量（patchset次数）、合入成功率
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if scope == "team":
                sql = """
                    SELECT 
                        u.depart_name_path as entity,
                        COUNT(*) as change_count,
                        SUM(gc.insertions) as insertions,
                        SUM(gc.deletions) as deletions,
                        SUM(gc.changed_file_count) as files_changed,
                        AVG(gc.patchset_id) as avg_patchset,
                        SUM(CASE WHEN gc.status = 'MERGED' THEN 1 ELSE 0 END) as merged,
                        COUNT(DISTINCT gc.owner_wkno) as contributors
                    FROM gerrit_change gc
                    JOIN user u ON gc.owner_wkno = u.wkno
                    WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY u.depart_name_path
                    HAVING contributors >= 2
                    ORDER BY insertions + deletions DESC
                    LIMIT %s
                """
            else:
                sql = """
                    SELECT 
                        gc.owner as entity,
                        gc.owner_wkno as wkno,
                        COUNT(*) as change_count,
                        SUM(gc.insertions) as insertions,
                        SUM(gc.deletions) as deletions,
                        SUM(gc.changed_file_count) as files_changed,
                        AVG(gc.patchset_id) as avg_patchset,
                        SUM(CASE WHEN gc.status = 'MERGED' THEN 1 ELSE 0 END) as merged
                    FROM gerrit_change gc
                    WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY gc.owner, gc.owner_wkno
                    HAVING change_count >= 3
                    ORDER BY insertions + deletions DESC
                    LIMIT %s
                """
            
            cursor.execute(sql, [days, limit])
            results = cursor.fetchall()
            
            contributions = []
            for row in results:
                total = _to_number(row['change_count'])
                merged = _to_number(row['merged']) or 0
                insertions = _to_number(row['insertions']) or 0
                deletions = _to_number(row['deletions']) or 0
                
                contribution = {
                    "entity": row['entity'],
                    "change_count": int(total),
                    "insertions": int(insertions),
                    "deletions": int(deletions),
                    "total_lines": int(insertions + deletions),
                    "net_lines": int(insertions - deletions),
                    "files_changed": int(_to_number(row['files_changed']) or 0),
                    "avg_patchset": round(_to_number(row['avg_patchset']) or 1, 1),
                    "merge_rate": round(merged / total * 100, 1) if total > 0 else 0,
                    "quality_score": _calculate_quality_score(row)
                }
                
                if scope == "individual" and row.get('wkno'):
                    contribution["wkno"] = row['wkno']
                if scope == "team" and row.get('contributors'):
                    contribution["contributors"] = int(_to_number(row['contributors']))
                
                contributions.append(contribution)
            
            return {
                "action": "contribution",
                "scope": scope,
                "period_days": days,
                "contributions": contributions,
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


def _calculate_quality_score(row: Dict) -> float:
    """计算代码质量评分"""
    total = _to_number(row['change_count'])
    if total == 0:
        return 0
    
    merged = _to_number(row['merged']) or 0
    avg_patchset = _to_number(row['avg_patchset']) or 1
    
    # 合并率权重50，低返工权重50
    merge_score = (merged / total) * 50
    rework_score = max(0, 50 - (avg_patchset - 1) * 15)  # patchset越多扣分越多
    
    return round(merge_score + rework_score, 1)


# ============================================================
# 5. ALM关联分析
# ============================================================
def analyze_alm_association(
    days: int = 30,
    analysis_type: str = "collaboration",  # collaboration, branches, types
    issue_id: Optional[int] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    ALM关联分析
    
    分析类型：
    - collaboration: 同一ALM多人协作分析
    - branches: 单ALM涉及分支数分析
    - types: 缺陷vs需求类型分布
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if analysis_type == "collaboration":
                return _analyze_alm_collaboration(cursor, days, issue_id, limit)
            elif analysis_type == "branches":
                return _analyze_alm_branches(cursor, days, issue_id, limit)
            elif analysis_type == "types":
                return _analyze_alm_types(cursor, days, limit)
            else:
                return {"error": f"Unknown analysis_type: {analysis_type}"}
    finally:
        connection.close()


def _analyze_alm_collaboration(cursor, days: int, issue_id: Optional[int], limit: int) -> Dict:
    """分析同一ALM多人协作情况"""
    sql = """
        SELECT 
            issue_id,
            COUNT(DISTINCT owner_wkno) as owner_count,
            COUNT(*) as change_count,
            GROUP_CONCAT(DISTINCT owner SEPARATOR ', ') as owners,
            COUNT(DISTINCT branch) as branch_count,
            MIN(created_at) as start_time,
            MAX(change_updated_at) as end_time
        FROM gerrit_change
        WHERE issue_id IS NOT NULL AND issue_id > 0
          AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    """
    params = [days]
    
    if issue_id:
        sql += " AND issue_id = %s"
        params.append(issue_id)
    
    sql += """
        GROUP BY issue_id
        HAVING owner_count > 1
        ORDER BY owner_count DESC
        LIMIT %s
    """
    params.append(limit)
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    
    collaborations = []
    for row in results:
        start = row['start_time']
        end = row['end_time']
        duration_days = (end - start).days if start and end else 0
        
        collaborations.append({
            "issue_id": int(_to_number(row['issue_id'])),
            "owner_count": int(_to_number(row['owner_count'])),
            "change_count": int(_to_number(row['change_count'])),
            "owners": row['owners'][:200] if row['owners'] else "",
            "branch_count": int(_to_number(row['branch_count'])),
            "duration_days": duration_days,
            "start_time": str(start) if start else None,
            "end_time": str(end) if end else None
        })
    
    return {
        "action": "alm_analysis",
        "analysis_type": "collaboration",
        "period_days": days,
        "collaborations": collaborations,
        "insight": f"共有 {len(collaborations)} 个ALM存在多人协作",
        "timestamp": datetime.now().isoformat()
    }


def _analyze_alm_branches(cursor, days: int, issue_id: Optional[int], limit: int) -> Dict:
    """分析单ALM涉及分支数"""
    sql = """
        SELECT 
            issue_id,
            COUNT(DISTINCT branch) as branch_count,
            COUNT(*) as change_count,
            GROUP_CONCAT(DISTINCT branch SEPARATOR ', ') as branches,
            MIN(created_at) as start_time,
            MAX(change_updated_at) as end_time
        FROM gerrit_change
        WHERE issue_id IS NOT NULL AND issue_id > 0
          AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
    """
    params = [days]
    
    if issue_id:
        sql += " AND issue_id = %s"
        params.append(issue_id)
    
    sql += """
        GROUP BY issue_id
        HAVING branch_count > 3
        ORDER BY branch_count DESC
        LIMIT %s
    """
    params.append(limit)
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    
    alm_branches = []
    for row in results:
        start = row['start_time']
        end = row['end_time']
        duration_days = (end - start).days if start and end else 0
        branch_count = int(_to_number(row['branch_count']))
        
        alm_branches.append({
            "issue_id": int(_to_number(row['issue_id'])),
            "branch_count": branch_count,
            "change_count": int(_to_number(row['change_count'])),
            "branches": row['branches'][:300] if row['branches'] else "",
            "duration_days": duration_days,
            "health_risk": "high" if branch_count > 10 else "medium" if branch_count > 5 else "low"
        })
    
    # 风险评估
    high_risk = sum(1 for a in alm_branches if a['health_risk'] == 'high')
    
    return {
        "action": "alm_analysis",
        "analysis_type": "branches",
        "period_days": days,
        "alm_branches": alm_branches,
        "risk_summary": {
            "high_risk_count": high_risk,
            "insight": f"{high_risk} 个ALM涉及超过10个分支，可能存在分支管理风险"
        },
        "timestamp": datetime.now().isoformat()
    }


def _analyze_alm_types(cursor, days: int, limit: int) -> Dict:
    """分析缺陷vs需求类型分布"""
    # 从 almid_commit_exemption 获取工作项类型
    cursor.execute("""
        SELECT 
            work_item_type,
            COUNT(*) as count,
            COUNT(DISTINCT alm_id) as alm_count,
            COUNT(DISTINCT gerrit_owner_id) as owner_count
        FROM almid_commit_exemption
        WHERE gerrit_patchset_createtime >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY work_item_type
        ORDER BY count DESC
        LIMIT %s
    """, [days, limit])
    
    type_stats = []
    total = 0
    defect_count = 0
    requirement_count = 0
    
    for row in cursor.fetchall():
        type_name = row['work_item_type'] or '未知'
        count = int(_to_number(row['count']))
        total += count
        
        # 分类：缺陷 vs 需求
        if '缺陷' in type_name or 'Bug' in type_name:
            defect_count += count
        elif '需求' in type_name or '故事' in type_name or 'Feature' in type_name:
            requirement_count += count
        
        type_stats.append({
            "type": type_name,
            "count": count,
            "alm_count": int(_to_number(row['alm_count'])),
            "owner_count": int(_to_number(row['owner_count']))
        })
    
    return {
        "action": "alm_analysis",
        "analysis_type": "types",
        "period_days": days,
        "type_distribution": type_stats,
        "summary": {
            "total_changes": total,
            "defect_changes": defect_count,
            "requirement_changes": requirement_count,
            "defect_ratio": round(defect_count / total * 100, 1) if total > 0 else 0,
            "insight": _generate_type_insight(defect_count, requirement_count, total)
        },
        "timestamp": datetime.now().isoformat()
    }


def _generate_type_insight(defect: int, requirement: int, total: int) -> str:
    """生成类型分布洞察"""
    if total == 0:
        return "无数据"
    
    defect_ratio = defect / total
    if defect_ratio > 0.7:
        return "缺陷修复占比过高(>70%)，建议关注代码质量"
    elif defect_ratio > 0.5:
        return "缺陷与需求开发基本持平"
    else:
        return "需求开发为主，缺陷修复占比正常"


# ============================================================
# 重点部门过滤配置
# ============================================================
TARGET_DEPARTMENTS = [
    "系统开发部",
    "应用开发一部",
    "应用开发二部",
    "互联通信开发部"
]


def _build_department_filter(cursor, departments: List[str] = None) -> str:
    """构建部门过滤SQL条件
    
    注意：使用%%转义百分号，避免与pymysql参数化冲突
    """
    if not departments:
        departments = TARGET_DEPARTMENTS
    
    # 使用%%转义，避免被pymysql当作格式化字符
    conditions = " OR ".join([f"u.depart_name_path LIKE '%%{dept}%%'" for dept in departments])
    return f"({conditions})"


# ============================================================
# 7. 分支收敛度分析（增强版）
# ============================================================
def analyze_branch_convergence(
    days: int = 365,
    departments: List[str] = None
) -> Dict[str, Any]:
    """
    分析分支收敛度
    
    分析维度：
    - 分支类型分布（release/master/feature/bugfix等）
    - 分支数量趋势
    - 僵尸分支识别
    - 分支管理建议
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 1. 分支类型分布统计
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN branch LIKE '%release%' OR branch LIKE '%Release%' THEN 'release'
                        WHEN branch = 'master' OR branch = 'main' THEN 'master'
                        WHEN branch LIKE 'feature/%' OR branch LIKE 'feat/%' THEN 'feature'
                        WHEN branch LIKE 'bugfix/%' OR branch LIKE 'hotfix/%' THEN 'bugfix'
                        WHEN branch LIKE 'dev%' THEN 'develop'
                        ELSE 'other'
                    END as branch_type,
                    COUNT(DISTINCT branch) as branch_count,
                    COUNT(*) as change_count,
                    COUNT(DISTINCT owner_wkno) as contributor_count,
                    SUM(CASE WHEN status = 'MERGED' THEN 1 ELSE 0 END) as merged_count,
                    SUM(CASE WHEN status = 'NEW' THEN 1 ELSE 0 END) as pending_count
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY branch_type
                ORDER BY branch_count DESC
            """, [days])
            
            branch_types = []
            total_branches = 0
            for row in cursor.fetchall():
                branch_count = int(_to_number(row['branch_count']))
                change_count = int(_to_number(row['change_count']))
                total_branches += branch_count
                
                branch_types.append({
                    "type": row['branch_type'],
                    "branch_count": branch_count,
                    "change_count": change_count,
                    "contributor_count": int(_to_number(row['contributor_count'])),
                    "merge_rate": round(_to_number(row['merged_count']) / change_count * 100, 1) if change_count > 0 else 0,
                    "pending_rate": round(_to_number(row['pending_count']) / change_count * 100, 1) if change_count > 0 else 0
                })
            
            # 2. 识别僵尸分支（长时间无活动）
            cursor.execute("""
                SELECT 
                    branch,
                    MAX(created_at) as last_activity,
                    COUNT(*) as total_changes,
                    SUM(CASE WHEN status = 'NEW' THEN 1 ELSE 0 END) as pending_count
                FROM gerrit_change
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY branch
                HAVING last_activity < DATE_SUB(NOW(), INTERVAL 90 DAY)
                   AND pending_count > 0
                ORDER BY pending_count DESC
                LIMIT 20
            """, [days])
            
            zombie_branches = []
            for row in cursor.fetchall():
                zombie_branches.append({
                    "branch": row['branch'],
                    "last_activity": str(row['last_activity']),
                    "total_changes": int(_to_number(row['total_changes'])),
                    "pending_count": int(_to_number(row['pending_count']))
                })
            
            # 3. 分支数量趋势（按月）
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(created_at, '%%Y-%%m') as month,
                    COUNT(DISTINCT branch) as active_branches,
                    COUNT(*) as changes
                FROM gerrit_change
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY month
                ORDER BY month
            """, [days])
            
            monthly_trend = []
            for row in cursor.fetchall():
                monthly_trend.append({
                    "month": row['month'],
                    "active_branches": int(_to_number(row['active_branches'])),
                    "changes": int(_to_number(row['changes']))
                })
            
            # 生成建议
            recommendations = []
            release_count = next((t['branch_count'] for t in branch_types if t['type'] == 'release'), 0)
            feature_count = next((t['branch_count'] for t in branch_types if t['type'] == 'feature'), 0)
            
            if release_count > 50:
                recommendations.append(f"Release分支数量过多({release_count}个)，建议定期清理已完成版本的分支")
            if feature_count > 100:
                recommendations.append(f"Feature分支数量过多({feature_count}个)，建议合并后及时删除")
            if len(zombie_branches) > 10:
                recommendations.append(f"存在{len(zombie_branches)}个僵尸分支（90天无活动但有待处理变更），建议清理")
            
            return {
                "action": "branch_convergence",
                "period_days": days,
                "summary": {
                    "total_active_branches": total_branches,
                    "branch_types": len(branch_types),
                    "zombie_branch_count": len(zombie_branches)
                },
                "branch_type_distribution": branch_types,
                "zombie_branches": zombie_branches,
                "monthly_trend": monthly_trend,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


# ============================================================
# 8. Change ID 收敛分析
# ============================================================
def analyze_change_convergence(
    days: int = 365,
    departments: List[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    分析Change ID收敛度 - 一个change_id是否对应多笔提交
    
    分析维度：
    - 单change的commit数量分布
    - 高commit数change的特征
    - 部门维度对比
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            dept_filter = _build_department_filter(cursor, departments)
            
            # 1. Change ID 收敛度统计 - 按patchset_id聚合
            cursor.execute(f"""
                SELECT 
                    gc.change_id,
                    gc.repo,
                    gc.branch,
                    gc.owner,
                    MAX(gc.patchset_id) as max_patchset,
                    COUNT(*) as record_count,
                    MIN(gc.created_at) as first_submit,
                    MAX(gc.change_updated_at) as last_update,
                    gc.status,
                    u.depart_name_path
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY gc.change_id, gc.repo, gc.branch, gc.owner, gc.status, u.depart_name_path
                HAVING max_patchset > 3
                ORDER BY max_patchset DESC
                LIMIT %s
            """, [days, limit])
            
            high_patchset_changes = []
            for row in cursor.fetchall():
                first = row['first_submit']
                last = row['last_update']
                duration_days = (last - first).days if first and last else 0
                
                high_patchset_changes.append({
                    "change_id": row['change_id'],
                    "repo": row['repo'],
                    "branch": row['branch'],
                    "owner": row['owner'],
                    "max_patchset": int(_to_number(row['max_patchset'])),
                    "duration_days": duration_days,
                    "status": row['status'],
                    "department": row['depart_name_path']
                })
            
            # 2. Patchset 分布统计
            cursor.execute(f"""
                SELECT 
                    CASE 
                        WHEN patchset_id = 1 THEN '1次提交'
                        WHEN patchset_id = 2 THEN '2次提交'
                        WHEN patchset_id = 3 THEN '3次提交'
                        WHEN patchset_id BETWEEN 4 AND 5 THEN '4-5次提交'
                        WHEN patchset_id BETWEEN 6 AND 10 THEN '6-10次提交'
                        ELSE '10次以上'
                    END as patchset_range,
                    COUNT(*) as change_count,
                    COUNT(DISTINCT owner_wkno) as contributor_count
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY patchset_range
                ORDER BY 
                    CASE patchset_range
                        WHEN '1次提交' THEN 1
                        WHEN '2次提交' THEN 2
                        WHEN '3次提交' THEN 3
                        WHEN '4-5次提交' THEN 4
                        WHEN '6-10次提交' THEN 5
                        ELSE 6
                    END
            """, [days])
            
            patchset_distribution = []
            total_changes = 0
            for row in cursor.fetchall():
                count = int(_to_number(row['change_count']))
                total_changes += count
                patchset_distribution.append({
                    "range": row['patchset_range'],
                    "count": count,
                    "contributors": int(_to_number(row['contributor_count']))
                })
            
            # 计算占比
            for item in patchset_distribution:
                item['percentage'] = round(item['count'] / total_changes * 100, 1) if total_changes > 0 else 0
            
            # 3. 部门维度对比
            cursor.execute(f"""
                SELECT 
                    SUBSTRING_INDEX(SUBSTRING_INDEX(u.depart_name_path, '/', 6), '/', -1) as department,
                    COUNT(*) as change_count,
                    AVG(gc.patchset_id) as avg_patchset,
                    SUM(CASE WHEN gc.patchset_id > 3 THEN 1 ELSE 0 END) as high_patchset_count
                FROM gerrit_change gc
                JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY department
                HAVING change_count >= 10
                ORDER BY avg_patchset DESC
            """, [days])
            
            department_comparison = []
            for row in cursor.fetchall():
                total = int(_to_number(row['change_count']))
                high = int(_to_number(row['high_patchset_count']))
                department_comparison.append({
                    "department": row['department'],
                    "change_count": total,
                    "avg_patchset": round(_to_number(row['avg_patchset']), 2),
                    "high_patchset_rate": round(high / total * 100, 1) if total > 0 else 0
                })
            
            # 生成洞察
            one_shot_rate = next((d['percentage'] for d in patchset_distribution if d['range'] == '1次提交'), 0)
            high_rework_rate = sum(d['percentage'] for d in patchset_distribution if '5' in d['range'] or '10' in d['range'] or '以上' in d['range'])
            
            insights = []
            if one_shot_rate < 50:
                insights.append(f"一次性通过率较低({one_shot_rate}%)，说明代码质量或评审流程有优化空间")
            if high_rework_rate > 10:
                insights.append(f"高返工率({high_rework_rate}%)的变更较多，建议分析具体原因")
            
            return {
                "action": "change_convergence",
                "period_days": days,
                "summary": {
                    "total_changes": total_changes,
                    "one_shot_rate": one_shot_rate,
                    "high_rework_rate": high_rework_rate
                },
                "patchset_distribution": patchset_distribution,
                "high_patchset_changes": high_patchset_changes[:20],
                "department_comparison": department_comparison,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


# ============================================================
# 9. 人员留存与熟练度分析
# ============================================================
def analyze_contributor_retention(
    year_current: int = 2025,
    year_previous: int = 2024,
    departments: List[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    分析人员留存情况 - 24年高产人员25年是否还在
    
    分析维度：
    - 年度活跃人员对比
    - 高产人员留存率
    - 新人占比与成长曲线
    - 熟练度分析（随时间效率变化）
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            dept_filter = _build_department_filter(cursor, departments)
            
            # 1. 上一年度高产人员（按提交量排名）
            cursor.execute(f"""
                SELECT 
                    gc.owner,
                    gc.owner_wkno,
                    u.depart_name_path,
                    COUNT(*) as change_count,
                    SUM(gc.insertions + gc.deletions) as total_lines,
                    AVG(gc.patchset_id) as avg_patchset,
                    SUM(CASE WHEN gc.status = 'MERGED' THEN 1 ELSE 0 END) as merged_count
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE YEAR(gc.created_at) = %s
                  AND {dept_filter}
                GROUP BY gc.owner, gc.owner_wkno, u.depart_name_path
                HAVING change_count >= 10
                ORDER BY change_count DESC
                LIMIT %s
            """, [year_previous, limit])
            
            previous_year_contributors = {}
            for row in cursor.fetchall():
                total = int(_to_number(row['change_count']))
                merged = int(_to_number(row['merged_count']))
                previous_year_contributors[row['owner_wkno']] = {
                    "name": row['owner'],
                    "wkno": row['owner_wkno'],
                    "department": row['depart_name_path'],
                    "change_count": total,
                    "total_lines": int(_to_number(row['total_lines']) or 0),
                    "avg_patchset": round(_to_number(row['avg_patchset']), 1),
                    "merge_rate": round(merged / total * 100, 1) if total > 0 else 0
                }
            
            # 2. 当前年度活跃人员
            cursor.execute(f"""
                SELECT 
                    gc.owner,
                    gc.owner_wkno,
                    u.depart_name_path,
                    COUNT(*) as change_count,
                    SUM(gc.insertions + gc.deletions) as total_lines,
                    AVG(gc.patchset_id) as avg_patchset,
                    SUM(CASE WHEN gc.status = 'MERGED' THEN 1 ELSE 0 END) as merged_count
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE YEAR(gc.created_at) = %s
                  AND {dept_filter}
                GROUP BY gc.owner, gc.owner_wkno, u.depart_name_path
                HAVING change_count >= 1
                ORDER BY change_count DESC
            """, [year_current])
            
            current_year_contributors = {}
            for row in cursor.fetchall():
                total = int(_to_number(row['change_count']))
                merged = int(_to_number(row['merged_count']))
                current_year_contributors[row['owner_wkno']] = {
                    "name": row['owner'],
                    "wkno": row['owner_wkno'],
                    "department": row['depart_name_path'],
                    "change_count": total,
                    "total_lines": int(_to_number(row['total_lines']) or 0),
                    "avg_patchset": round(_to_number(row['avg_patchset']), 1),
                    "merge_rate": round(merged / total * 100, 1) if total > 0 else 0
                }
            
            # 3. 计算留存与流失
            prev_wknos = set(previous_year_contributors.keys())
            curr_wknos = set(current_year_contributors.keys())
            
            retained_wknos = prev_wknos & curr_wknos  # 留存
            churned_wknos = prev_wknos - curr_wknos   # 流失
            new_wknos = curr_wknos - prev_wknos      # 新人
            
            retained_contributors = []
            churned_contributors = []
            new_contributors = []
            
            for wkno in retained_wknos:
                prev = previous_year_contributors[wkno]
                curr = current_year_contributors[wkno]
                retained_contributors.append({
                    "name": prev['name'],
                    "wkno": wkno,
                    "department": prev['department'],
                    f"{year_previous}_changes": prev['change_count'],
                    f"{year_current}_changes": curr['change_count'],
                    "change_delta": curr['change_count'] - prev['change_count'],
                    "efficiency_trend": "improved" if curr['avg_patchset'] < prev['avg_patchset'] else "declined"
                })
            
            for wkno in churned_wknos:
                prev = previous_year_contributors[wkno]
                churned_contributors.append({
                    "name": prev['name'],
                    "wkno": wkno,
                    "department": prev['department'],
                    f"{year_previous}_changes": prev['change_count'],
                    "total_lines_lost": prev['total_lines']
                })
            
            for wkno in list(new_wknos)[:30]:
                curr = current_year_contributors[wkno]
                new_contributors.append({
                    "name": curr['name'],
                    "wkno": wkno,
                    "department": curr['department'],
                    f"{year_current}_changes": curr['change_count'],
                    "avg_patchset": curr['avg_patchset']
                })
            
            # 4. 计算统计指标
            retention_rate = round(len(retained_wknos) / len(prev_wknos) * 100, 1) if prev_wknos else 0
            churn_rate = round(len(churned_wknos) / len(prev_wknos) * 100, 1) if prev_wknos else 0
            new_rate = round(len(new_wknos) / len(curr_wknos) * 100, 1) if curr_wknos else 0
            
            # 计算流失带来的产能损失
            total_lines_lost = sum(c.get('total_lines_lost', 0) for c in churned_contributors)
            
            # 排序
            retained_contributors.sort(key=lambda x: x.get(f'{year_previous}_changes', 0), reverse=True)
            churned_contributors.sort(key=lambda x: x.get(f'{year_previous}_changes', 0), reverse=True)
            new_contributors.sort(key=lambda x: x.get(f'{year_current}_changes', 0), reverse=True)
            
            return {
                "action": "contributor_retention",
                "years": {"previous": year_previous, "current": year_current},
                "summary": {
                    "previous_year_contributors": len(prev_wknos),
                    "current_year_contributors": len(curr_wknos),
                    "retained_count": len(retained_wknos),
                    "churned_count": len(churned_wknos),
                    "new_count": len(new_wknos),
                    "retention_rate": retention_rate,
                    "churn_rate": churn_rate,
                    "new_rate": new_rate,
                    "total_lines_lost": total_lines_lost
                },
                "retained_contributors": retained_contributors[:20],
                "churned_contributors": churned_contributors[:20],
                "new_contributors": new_contributors[:20],
                "insights": _generate_retention_insights(retention_rate, churn_rate, new_rate, churned_contributors),
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


def _generate_retention_insights(retention: float, churn: float, new: float, churned: List) -> List[str]:
    """生成留存分析洞察"""
    insights = []
    
    if retention < 70:
        insights.append(f"人员留存率较低({retention}%)，高产人员流失可能影响团队产能")
    elif retention > 90:
        insights.append(f"人员留存率较高({retention}%)，团队稳定性良好")
    
    if churn > 20:
        top_churned = sum(1 for c in churned if c.get(f'{2024}_changes', 0) > 50)
        if top_churned > 3:
            insights.append(f"有{top_churned}名高产人员流失，建议关注人才保留")
    
    if new > 40:
        insights.append(f"新人占比较高({new}%)，可能存在新人培训和熟练度提升的挑战")
    
    return insights


# ============================================================
# 10. Story/ALM 跨度分析（增强版）
# ============================================================
def analyze_story_duration(
    days: int = 365,
    departments: List[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    分析Story/ALM的时间跨度
    
    分析维度：
    - Story周期分布
    - 长周期Story特征（>30天）
    - 跨分支Story识别
    - 部门维度对比
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            dept_filter = _build_department_filter(cursor, departments)
            
            # 1. Story周期统计
            cursor.execute(f"""
                SELECT 
                    gc.issue_id,
                    MIN(gc.created_at) as start_time,
                    MAX(gc.change_updated_at) as end_time,
                    COUNT(*) as change_count,
                    COUNT(DISTINCT gc.owner_wkno) as contributor_count,
                    COUNT(DISTINCT gc.branch) as branch_count,
                    COUNT(DISTINCT gc.repo) as repo_count,
                    GROUP_CONCAT(DISTINCT gc.owner SEPARATOR ', ') as contributors,
                    SUM(gc.insertions + gc.deletions) as total_lines
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.issue_id IS NOT NULL AND gc.issue_id > 0
                  AND gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY gc.issue_id
                HAVING change_count >= 2
                ORDER BY DATEDIFF(MAX(gc.change_updated_at), MIN(gc.created_at)) DESC
                LIMIT %s
            """, [days, limit])
            
            long_duration_stories = []
            all_durations = []
            
            for row in cursor.fetchall():
                start = row['start_time']
                end = row['end_time']
                duration_days = (end - start).days if start and end else 0
                all_durations.append(duration_days)
                
                if duration_days > 30:  # 长周期Story
                    long_duration_stories.append({
                        "issue_id": int(_to_number(row['issue_id'])),
                        "duration_days": duration_days,
                        "change_count": int(_to_number(row['change_count'])),
                        "contributor_count": int(_to_number(row['contributor_count'])),
                        "branch_count": int(_to_number(row['branch_count'])),
                        "repo_count": int(_to_number(row['repo_count'])),
                        "contributors": row['contributors'][:100] if row['contributors'] else "",
                        "total_lines": int(_to_number(row['total_lines']) or 0),
                        "start_time": str(start) if start else None,
                        "end_time": str(end) if end else None,
                        "risk_level": "high" if duration_days > 60 else "medium"
                    })
            
            # 2. 周期分布统计
            cursor.execute(f"""
                SELECT 
                    CASE 
                        WHEN DATEDIFF(MAX(change_updated_at), MIN(created_at)) <= 1 THEN '1天内'
                        WHEN DATEDIFF(MAX(change_updated_at), MIN(created_at)) <= 7 THEN '1-7天'
                        WHEN DATEDIFF(MAX(change_updated_at), MIN(created_at)) <= 14 THEN '8-14天'
                        WHEN DATEDIFF(MAX(change_updated_at), MIN(created_at)) <= 30 THEN '15-30天'
                        WHEN DATEDIFF(MAX(change_updated_at), MIN(created_at)) <= 60 THEN '31-60天'
                        ELSE '60天以上'
                    END as duration_range,
                    COUNT(DISTINCT issue_id) as story_count
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.issue_id IS NOT NULL AND gc.issue_id > 0
                  AND gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY issue_id
                HAVING COUNT(*) >= 1
            """, [days])
            
            # 聚合周期分布
            duration_buckets = {'1天内': 0, '1-7天': 0, '8-14天': 0, '15-30天': 0, '31-60天': 0, '60天以上': 0}
            for row in cursor.fetchall():
                bucket = row['duration_range']
                if bucket in duration_buckets:
                    duration_buckets[bucket] += 1
            
            total_stories = sum(duration_buckets.values())
            duration_distribution = []
            for bucket, count in duration_buckets.items():
                duration_distribution.append({
                    "range": bucket,
                    "count": count,
                    "percentage": round(count / total_stories * 100, 1) if total_stories > 0 else 0
                })
            
            # 3. 跨分支Story分析
            cursor.execute(f"""
                SELECT 
                    gc.issue_id,
                    COUNT(DISTINCT gc.branch) as branch_count,
                    COUNT(*) as change_count,
                    GROUP_CONCAT(DISTINCT gc.branch SEPARATOR ', ') as branches,
                    DATEDIFF(MAX(gc.change_updated_at), MIN(gc.created_at)) as duration_days
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.issue_id IS NOT NULL AND gc.issue_id > 0
                  AND gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY gc.issue_id
                HAVING branch_count > 3
                ORDER BY branch_count DESC
                LIMIT 20
            """, [days])
            
            cross_branch_stories = []
            for row in cursor.fetchall():
                cross_branch_stories.append({
                    "issue_id": int(_to_number(row['issue_id'])),
                    "branch_count": int(_to_number(row['branch_count'])),
                    "change_count": int(_to_number(row['change_count'])),
                    "branches": row['branches'][:200] if row['branches'] else "",
                    "duration_days": int(_to_number(row['duration_days']))
                })
            
            # 4. 计算统计指标
            avg_duration = sum(all_durations) / len(all_durations) if all_durations else 0
            long_story_count = sum(1 for d in all_durations if d > 30)
            long_story_rate = round(long_story_count / len(all_durations) * 100, 1) if all_durations else 0
            
            # 生成洞察
            insights = []
            if long_story_rate > 20:
                insights.append(f"长周期Story(>30天)占比{long_story_rate}%，建议拆分大Story提高交付效率")
            if len(cross_branch_stories) > 10:
                insights.append(f"存在{len(cross_branch_stories)}个跨多分支的Story，可能存在分支管理复杂度")
            if avg_duration > 20:
                insights.append(f"Story平均周期{avg_duration:.1f}天，偏长，建议优化交付节奏")
            
            return {
                "action": "story_duration",
                "period_days": days,
                "summary": {
                    "total_stories": total_stories,
                    "avg_duration_days": round(avg_duration, 1),
                    "long_story_count": long_story_count,
                    "long_story_rate": long_story_rate,
                    "cross_branch_story_count": len(cross_branch_stories)
                },
                "duration_distribution": duration_distribution,
                "long_duration_stories": long_duration_stories[:20],
                "cross_branch_stories": cross_branch_stories,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


# ============================================================
# 11. 时间效率损耗分析（核心）
# ============================================================
def analyze_time_efficiency_loss(
    days: int = 365,
    departments: List[str] = None
) -> Dict[str, Any]:
    """
    从人的时间效率角度分析各维度的损耗
    
    业务模型：
    - ALM层级：Epic → Feature → Story(alm_id/issue_id)
    - Gerrit层级：change_id(逻辑变更) → 多条记录(不同分支)
    
    分析维度：
    1. 分支分散度：人均活跃分支数
    2. Story拆分合理性：alm_id → change_id 的映射（1:N是否合理）
    3. Change分支分布：change_id → 记录数（cherry-pick/多仓库/异常）
    4. 返工率：patchset分布
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            dept_filter = _build_department_filter(cursor, departments)
            
            # ====== 1. 分支分散度分析 ======
            cursor.execute(f"""
                SELECT 
                    gc.owner_wkno,
                    gc.owner,
                    COUNT(DISTINCT gc.branch) as branch_count,
                    COUNT(*) as change_count,
                    COUNT(DISTINCT gc.repo) as repo_count
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY gc.owner_wkno, gc.owner
                HAVING change_count >= 5
                ORDER BY branch_count DESC
                LIMIT 50
            """, [days])
            
            branch_per_person = []
            total_branches_all = 0
            total_people = 0
            high_branch_people = 0
            
            for row in cursor.fetchall():
                branch_count = int(_to_number(row['branch_count']))
                total_branches_all += branch_count
                total_people += 1
                if branch_count > 5:
                    high_branch_people += 1
                
                branch_per_person.append({
                    "name": row['owner'],
                    "wkno": row['owner_wkno'],
                    "branch_count": branch_count,
                    "change_count": int(_to_number(row['change_count'])),
                    "repo_count": int(_to_number(row['repo_count']))
                })
            
            avg_branches_per_person = round(total_branches_all / total_people, 1) if total_people > 0 else 0
            
            # ====== 2. Story拆分合理性：alm_id → change_id ======
            # 一个Story(alm_id)对应多少个不同的change_id
            cursor.execute(f"""
                SELECT 
                    gc.issue_id,
                    COUNT(DISTINCT gc.change_id) as change_id_count,
                    COUNT(DISTINCT gc.owner_wkno) as contributor_count,
                    GROUP_CONCAT(DISTINCT gc.owner SEPARATOR ', ') as contributors,
                    MIN(gc.created_at) as start_time,
                    MAX(gc.change_updated_at) as end_time
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.issue_id IS NOT NULL AND gc.issue_id > 0
                  AND gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY gc.issue_id
                ORDER BY change_id_count DESC
                LIMIT 50
            """, [days])
            
            story_analysis = []
            for row in cursor.fetchall():
                start = row['start_time']
                end = row['end_time']
                duration = (end - start).days if start and end else 0
                change_id_count = int(_to_number(row['change_id_count']))
                contributor_count = int(_to_number(row['contributor_count']))
                
                # 推断可能的问题
                possible_issue = None
                if change_id_count > 10:
                    if contributor_count > 3:
                        possible_issue = "借单(多人挂同一alm_id)"
                    else:
                        possible_issue = "Story拆分过细或需求不清晰"
                elif change_id_count > 5:
                    possible_issue = "可能存在边做边补"
                
                story_analysis.append({
                    "issue_id": int(_to_number(row['issue_id'])),
                    "change_id_count": change_id_count,
                    "contributor_count": contributor_count,
                    "contributors": row['contributors'][:100] if row['contributors'] else "",
                    "duration_days": duration,
                    "possible_issue": possible_issue
                })
            
            # Story拆分分布统计
            cursor.execute(f"""
                SELECT 
                    bucket,
                    COUNT(*) as story_count
                FROM (
                    SELECT 
                        gc.issue_id,
                        CASE 
                            WHEN COUNT(DISTINCT gc.change_id) = 1 THEN '1个change_id(理想)'
                            WHEN COUNT(DISTINCT gc.change_id) BETWEEN 2 AND 3 THEN '2-3个change_id(正常)'
                            WHEN COUNT(DISTINCT gc.change_id) BETWEEN 4 AND 10 THEN '4-10个change_id(偏多)'
                            ELSE '10个以上change_id(异常)'
                        END as bucket
                    FROM gerrit_change gc
                    LEFT JOIN user u ON gc.owner_wkno = u.wkno
                    WHERE gc.issue_id IS NOT NULL AND gc.issue_id > 0
                      AND gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                      AND {dept_filter}
                    GROUP BY gc.issue_id
                ) t
                GROUP BY bucket
            """, [days])
            
            story_distribution = {}
            for row in cursor.fetchall():
                story_distribution[row['bucket']] = int(_to_number(row['story_count']))
            
            # ====== 3. Change分支分布：change_id → 记录数 ======
            cursor.execute(f"""
                SELECT 
                    CASE 
                        WHEN cnt = branch_cnt AND repo_cnt = 1 THEN 'cherry-pick(单仓库)'
                        WHEN cnt = branch_cnt AND repo_cnt > 1 THEN 'cherry-pick(多仓库)'
                        WHEN cnt > branch_cnt THEN '同分支多次记录(异常)'
                        ELSE '其他'
                    END as reason,
                    COUNT(*) as change_id_count,
                    SUM(cnt) as total_records
                FROM (
                    SELECT 
                        change_id, 
                        COUNT(*) as cnt, 
                        COUNT(DISTINCT branch) as branch_cnt, 
                        COUNT(DISTINCT repo) as repo_cnt
                    FROM gerrit_change gc
                    LEFT JOIN user u ON gc.owner_wkno = u.wkno
                    WHERE change_id IS NOT NULL AND change_id != ''
                      AND gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                      AND {dept_filter}
                    GROUP BY change_id
                    HAVING cnt > 1
                ) t
                GROUP BY reason
            """, [days])
            
            change_branch_distribution = {}
            for row in cursor.fetchall():
                change_branch_distribution[row['reason']] = {
                    "change_id_count": int(_to_number(row['change_id_count'])),
                    "total_records": int(_to_number(row['total_records']))
                }
            
            # 同分支多次记录的详细分析
            cursor.execute(f"""
                SELECT 
                    gc.change_id,
                    gc.branch,
                    gc.repo,
                    COUNT(*) as record_count,
                    COUNT(DISTINCT gc.issue_id) as issue_count,
                    SUM(CASE WHEN gc.status = 'ABANDONED' THEN 1 ELSE 0 END) as abandoned_count,
                    SUM(CASE WHEN gc.status = 'MERGED' THEN 1 ELSE 0 END) as merged_count
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.change_id IS NOT NULL AND gc.change_id != ''
                  AND gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
                GROUP BY gc.change_id, gc.branch, gc.repo
                HAVING record_count > 1
                ORDER BY record_count DESC
                LIMIT 20
            """, [days])
            
            abnormal_changes = []
            for row in cursor.fetchall():
                record_count = int(_to_number(row['record_count']))
                abandoned = int(_to_number(row['abandoned_count']))
                merged = int(_to_number(row['merged_count']))
                issue_count = int(_to_number(row['issue_count']))
                
                # 推断原因
                if abandoned > merged:
                    reason = "反复提交-放弃(可能门禁失败)"
                elif issue_count > 1:
                    reason = "借单(同一change_id关联多个issue_id)"
                elif merged > 1:
                    reason = "合并后又重新提交"
                else:
                    reason = "待分析"
                
                abnormal_changes.append({
                    "change_id": row['change_id'][:20] + "...",
                    "branch": row['branch'],
                    "repo": row['repo'],
                    "record_count": record_count,
                    "abandoned_count": abandoned,
                    "merged_count": merged,
                    "issue_count": issue_count,
                    "possible_reason": reason
                })
            
            # ====== 4. 返工率分析 ======
            cursor.execute(f"""
                SELECT 
                    SUM(CASE WHEN patchset_id = 1 THEN 1 ELSE 0 END) as one_shot,
                    SUM(CASE WHEN patchset_id = 2 THEN 1 ELSE 0 END) as two_times,
                    SUM(CASE WHEN patchset_id = 3 THEN 1 ELSE 0 END) as three_times,
                    SUM(CASE WHEN patchset_id > 3 THEN 1 ELSE 0 END) as more_than_three,
                    SUM(patchset_id - 1) as total_rework_count,
                    COUNT(*) as total_changes,
                    AVG(patchset_id) as avg_patchset
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
            """, [days])
            
            rework_stats = cursor.fetchone()
            total_changes = int(_to_number(rework_stats['total_changes']))
            total_rework = int(_to_number(rework_stats['total_rework_count']) or 0)
            one_shot = int(_to_number(rework_stats['one_shot']) or 0)
            
            rework_analysis = {
                "total_changes": total_changes,
                "one_shot_count": one_shot,
                "one_shot_rate": round(one_shot / total_changes * 100, 1) if total_changes > 0 else 0,
                "total_rework_count": total_rework,
                "avg_patchset": round(_to_number(rework_stats['avg_patchset']), 2),
                "distribution": {
                    "1次通过": int(_to_number(rework_stats['one_shot']) or 0),
                    "2次通过": int(_to_number(rework_stats['two_times']) or 0),
                    "3次通过": int(_to_number(rework_stats['three_times']) or 0),
                    "3次以上": int(_to_number(rework_stats['more_than_three']) or 0)
                }
            }
            
            # ====== 5. 汇总统计 ======
            cursor.execute(f"""
                SELECT 
                    COUNT(DISTINCT gc.owner_wkno) as total_contributors,
                    COUNT(*) as total_records,
                    COUNT(DISTINCT gc.change_id) as total_change_ids,
                    COUNT(DISTINCT gc.issue_id) as total_stories
                FROM gerrit_change gc
                LEFT JOIN user u ON gc.owner_wkno = u.wkno
                WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND {dept_filter}
            """, [days])
            
            summary_stats = cursor.fetchone()
            
            # 计算关键比率
            total_stories = sum(story_distribution.values())
            ideal_story_rate = round(story_distribution.get('1个change_id(理想)', 0) / total_stories * 100, 1) if total_stories > 0 else 0
            
            # ====== 生成洞察 ======
            insights = []
            
            if avg_branches_per_person > 10:
                insights.append({
                    "category": "分支分散度",
                    "severity": "high",
                    "finding": f"人均活跃分支{avg_branches_per_person}个，工作非常分散"
                })
            
            if ideal_story_rate < 50:
                insights.append({
                    "category": "Story拆分",
                    "severity": "high",
                    "finding": f"只有{ideal_story_rate}%的Story是1个change_id解决的，可能存在借单或拆分不合理"
                })
            
            abnormal_change_count = change_branch_distribution.get('同分支多次记录(异常)', {}).get('change_id_count', 0)
            if abnormal_change_count > 100:
                insights.append({
                    "category": "异常提交",
                    "severity": "medium",
                    "finding": f"有{abnormal_change_count}个change_id在同一分支有多次记录，可能是反复提交或借单"
                })
            
            if rework_analysis['one_shot_rate'] < 50:
                insights.append({
                    "category": "返工率",
                    "severity": "high",
                    "finding": f"一次性通过率仅{rework_analysis['one_shot_rate']}%，总返工{total_rework}次"
                })
            
            return {
                "action": "time_efficiency_loss",
                "period_days": days,
                "summary": {
                    "total_contributors": int(_to_number(summary_stats['total_contributors'])),
                    "total_records": int(_to_number(summary_stats['total_records'])),
                    "total_change_ids": int(_to_number(summary_stats['total_change_ids'])),
                    "total_stories": int(_to_number(summary_stats['total_stories'])),
                    "avg_branches_per_person": avg_branches_per_person,
                    "one_shot_rate": rework_analysis['one_shot_rate'],
                    "ideal_story_rate": ideal_story_rate
                },
                "branch_distribution": {
                    "avg_branches_per_person": avg_branches_per_person,
                    "high_branch_people_count": high_branch_people,
                    "high_branch_people_rate": round(high_branch_people / total_people * 100, 1) if total_people > 0 else 0,
                    "top_scattered_people": branch_per_person[:10]
                },
                "story_convergence": {
                    "distribution": story_distribution,
                    "high_change_stories": [s for s in story_analysis if s['change_id_count'] > 5][:10]
                },
                "change_branch_analysis": {
                    "reason_distribution": change_branch_distribution,
                    "abnormal_changes": abnormal_changes[:10]
                },
                "rework_analysis": rework_analysis,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


# ============================================================
# 12. 年度效率综合报告
# ============================================================
def generate_annual_efficiency_report(
    year: int = 2024,
    departments: List[str] = None
) -> Dict[str, Any]:
    """
    生成年度效率综合报告
    
    整合所有分析维度，生成针对指定部门的年度效率报告
    """
    if departments is None:
        departments = TARGET_DEPARTMENTS
    
    # 计算年度天数
    from datetime import date
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    days = (end_date - start_date).days + 1
    
    # 收集各维度分析结果
    try:
        branch_analysis = analyze_branch_convergence(days=days, departments=departments)
        change_analysis = analyze_change_convergence(days=days, departments=departments)
        retention_analysis = analyze_contributor_retention(
            year_current=year,
            year_previous=year-1,
            departments=departments
        )
        story_analysis = analyze_story_duration(days=days, departments=departments)
        
        # 汇总关键指标
        return {
            "action": "annual_efficiency_report",
            "year": year,
            "target_departments": departments,
            "executive_summary": {
                "branch_health": {
                    "total_branches": branch_analysis['summary']['total_active_branches'],
                    "zombie_branches": branch_analysis['summary']['zombie_branch_count'],
                    "status": "warning" if branch_analysis['summary']['zombie_branch_count'] > 10 else "healthy"
                },
                "change_efficiency": {
                    "one_shot_rate": change_analysis['summary']['one_shot_rate'],
                    "high_rework_rate": change_analysis['summary']['high_rework_rate'],
                    "status": "warning" if change_analysis['summary']['one_shot_rate'] < 50 else "healthy"
                },
                "team_stability": {
                    "retention_rate": retention_analysis['summary']['retention_rate'],
                    "churn_rate": retention_analysis['summary']['churn_rate'],
                    "new_rate": retention_analysis['summary']['new_rate'],
                    "status": "warning" if retention_analysis['summary']['retention_rate'] < 70 else "healthy"
                },
                "delivery_efficiency": {
                    "avg_story_duration": story_analysis['summary']['avg_duration_days'],
                    "long_story_rate": story_analysis['summary']['long_story_rate'],
                    "status": "warning" if story_analysis['summary']['long_story_rate'] > 20 else "healthy"
                }
            },
            "detailed_analysis": {
                "branch_convergence": branch_analysis,
                "change_convergence": change_analysis,
                "contributor_retention": retention_analysis,
                "story_duration": story_analysis
            },
            "recommendations": _generate_annual_recommendations(
                branch_analysis, change_analysis, retention_analysis, story_analysis
            ),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "action": "annual_efficiency_report",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def _generate_annual_recommendations(branch, change, retention, story) -> List[Dict]:
    """生成年度改进建议"""
    recommendations = []
    
    # 分支管理建议
    if branch['summary']['zombie_branch_count'] > 10:
        recommendations.append({
            "category": "分支管理",
            "priority": "high",
            "issue": f"存在{branch['summary']['zombie_branch_count']}个僵尸分支",
            "suggestion": "定期清理90天无活动的分支，建立分支生命周期管理机制"
        })
    
    # 代码质量建议
    if change['summary']['one_shot_rate'] < 50:
        recommendations.append({
            "category": "代码质量",
            "priority": "high",
            "issue": f"一次性通过率仅{change['summary']['one_shot_rate']}%",
            "suggestion": "加强代码自测和Code Review前的自检，减少返工"
        })
    
    if change['summary']['high_rework_rate'] > 10:
        recommendations.append({
            "category": "代码质量",
            "priority": "medium",
            "issue": f"高返工率({change['summary']['high_rework_rate']}%)的变更较多",
            "suggestion": "分析返工原因，是需求不清晰还是技术实现问题"
        })
    
    # 人员稳定性建议
    if retention['summary']['retention_rate'] < 70:
        recommendations.append({
            "category": "团队稳定",
            "priority": "high",
            "issue": f"人员留存率{retention['summary']['retention_rate']}%，偏低",
            "suggestion": "关注高产人员的满意度和职业发展，降低关键人才流失"
        })
    
    if retention['summary']['new_rate'] > 40:
        recommendations.append({
            "category": "团队稳定",
            "priority": "medium",
            "issue": f"新人占比{retention['summary']['new_rate']}%，较高",
            "suggestion": "加强新人培训和导师制度，加速新人成长"
        })
    
    # 交付效率建议
    if story['summary']['long_story_rate'] > 20:
        recommendations.append({
            "category": "交付效率",
            "priority": "high",
            "issue": f"长周期Story占比{story['summary']['long_story_rate']}%",
            "suggestion": "拆分大Story为可独立交付的小Story，提高交付频率"
        })
    
    if story['summary']['cross_branch_story_count'] > 10:
        recommendations.append({
            "category": "交付效率",
            "priority": "medium",
            "issue": f"存在{story['summary']['cross_branch_story_count']}个跨多分支Story",
            "suggestion": "减少Story的分支跨度，简化代码合并复杂度"
        })
    
    return recommendations


# ============================================================
# 6. 代码审查效率指标 (原有功能增强)
# ============================================================
def analyze_review_metrics(days: int = 7, project: Optional[str] = None) -> Dict[str, Any]:
    """
    分析代码审查效率指标
    
    指标：
    - 变更总数和合并率
    - 代码行数统计
    - 返工率（patchset > 2）
    - 异常检测
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    COUNT(*) as total_changes,
                    SUM(CASE WHEN status = 'MERGED' THEN 1 ELSE 0 END) as merged_count,
                    SUM(CASE WHEN status = 'ABANDONED' THEN 1 ELSE 0 END) as abandoned_count,
                    SUM(CASE WHEN status = 'NEW' THEN 1 ELSE 0 END) as pending_count,
                    SUM(insertions) as total_insertions,
                    SUM(deletions) as total_deletions,
                    SUM(CASE WHEN patchset_id > 2 THEN 1 ELSE 0 END) as rework_count,
                    AVG(patchset_id) as avg_patchset,
                    COUNT(DISTINCT owner_wkno) as contributor_count,
                    COUNT(DISTINCT repo) as repo_count
                FROM gerrit_change
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            params = [days]
            
            if project:
                sql += " AND repo LIKE %s"
                params.append(f"%{project}%")
            
            cursor.execute(sql, params)
            stats = cursor.fetchone()
            
            total = _to_number(stats['total_changes']) or 0
            merged = _to_number(stats['merged_count']) or 0
            rework = _to_number(stats['rework_count']) or 0
            
            # 异常检测
            anomalies = []
            rework_rate = rework / total * 100 if total > 0 else 0
            merge_rate = merged / total * 100 if total > 0 else 0
            
            if rework_rate > 15:
                anomalies.append({
                    "type": "high_rework_rate",
                    "severity": "warning",
                    "message": f"返工率({rework_rate:.1f}%)超过15%阈值",
                    "value": rework_rate,
                    "threshold": 15
                })
            
            if merge_rate < 70 and total > 10:
                anomalies.append({
                    "type": "low_merge_rate",
                    "severity": "warning",
                    "message": f"合并率({merge_rate:.1f}%)低于70%",
                    "value": merge_rate,
                    "threshold": 70
                })
            
            return {
                "action": "review_metrics",
                "period_days": days,
                "metrics": {
                    "total_changes": int(total),
                    "merged_count": int(merged),
                    "abandoned_count": int(_to_number(stats['abandoned_count']) or 0),
                    "pending_count": int(_to_number(stats['pending_count']) or 0),
                    "merge_rate_percent": round(merge_rate, 2),
                    "rework_rate_percent": round(rework_rate, 2),
                    "avg_patchset": round(_to_number(stats['avg_patchset']) or 1, 2),
                    "total_insertions": int(_to_number(stats['total_insertions']) or 0),
                    "total_deletions": int(_to_number(stats['total_deletions']) or 0),
                    "contributor_count": int(_to_number(stats['contributor_count']) or 0),
                    "repo_count": int(_to_number(stats['repo_count']) or 0)
                },
                "anomalies": anomalies,
                "data_source": "mysql",
                "timestamp": datetime.now().isoformat()
            }
    finally:
        connection.close()


# ============================================================
# 主入口函数
# ============================================================
def run_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行分析的主入口
    
    支持的action:
    - top_contributors: 高产人员分析
    - workload: 工作负荷分析
    - branch_health: 分支健康度
    - contribution: 贡献度分析
    - alm_analysis: ALM关联分析
    - review_metrics: 审查效率指标
    - summary: 综合概览
    
    新增action (年度效率分析):
    - branch_convergence: 分支收敛度分析
    - change_convergence: Change ID收敛分析
    - contributor_retention: 人员留存分析
    - story_duration: Story跨度分析
    - annual_report: 年度效率综合报告
    """
    action = params.get('action', 'summary')
    days = params.get('days', 30)
    departments = params.get('departments')  # 部门过滤
    
    try:
        if action == 'top_contributors':
            return analyze_top_contributors(
                days=days,
                limit=params.get('limit', 20)
            )
        
        elif action == 'workload':
            return analyze_workload(
                days=days,
                scope=params.get('scope', 'individual'),
                owner_wkno=params.get('owner_wkno'),
                department=params.get('department'),
                limit=params.get('limit', 20)
            )
        
        elif action == 'branch_health':
            return analyze_branch_health(
                days=days,
                repo=params.get('repo')
            )
        
        elif action == 'contribution':
            return analyze_contribution(
                days=days,
                scope=params.get('scope', 'individual'),
                limit=params.get('limit', 20)
            )
        
        elif action == 'alm_analysis':
            return analyze_alm_association(
                days=days,
                analysis_type=params.get('analysis_type', 'collaboration'),
                issue_id=params.get('issue_id'),
                limit=params.get('limit', 20)
            )
        
        elif action == 'review_metrics':
            return analyze_review_metrics(
                days=days,
                project=params.get('project')
            )
        
        elif action == 'summary':
            # 综合概览：汇总多个维度
            return _generate_summary(days)
        
        # ========== 新增年度效率分析 ==========
        elif action == 'branch_convergence':
            return analyze_branch_convergence(
                days=days,
                departments=departments
            )
        
        elif action == 'change_convergence':
            return analyze_change_convergence(
                days=days,
                departments=departments,
                limit=params.get('limit', 50)
            )
        
        elif action == 'contributor_retention':
            return analyze_contributor_retention(
                year_current=params.get('year_current', 2025),
                year_previous=params.get('year_previous', 2024),
                departments=departments,
                limit=params.get('limit', 100)
            )
        
        elif action == 'story_duration':
            return analyze_story_duration(
                days=days,
                departments=departments,
                limit=params.get('limit', 50)
            )
        
        elif action == 'annual_report':
            return generate_annual_efficiency_report(
                year=params.get('year', 2024),
                departments=departments
            )
        
        elif action == 'time_efficiency_loss':
            return analyze_time_efficiency_loss(
                days=days,
                departments=departments
            )
        
        elif action == 'briefing':
            return generate_briefing(
                days=days,
                departments=departments
            )
        
        elif action == 'ui_schema':
            return generate_ui_schema(
                days=days,
                departments=departments
            )
        
        else:
            return {"error": f"Unknown action: {action}"}
            
    except Exception as e:
        return {
            "error": str(e),
            "action": action,
            "data_source": "mysql"
        }


def _generate_summary(days: int) -> Dict[str, Any]:
    """生成综合概览"""
    metrics = analyze_review_metrics(days=days)
    contributors = analyze_top_contributors(days=days, limit=5)
    branch = analyze_branch_health(days=days)
    
    return {
        "action": "summary",
        "period_days": days,
        "overview": {
            "total_changes": metrics['metrics']['total_changes'],
            "merge_rate": metrics['metrics']['merge_rate_percent'],
            "rework_rate": metrics['metrics']['rework_rate_percent'],
            "contributors": metrics['metrics']['contributor_count'],
            "repos": metrics['metrics']['repo_count']
        },
        "top_contributors": [
            {"name": c['name'], "changes": c['change_count'], "efficiency": c['efficiency_score']}
            for c in contributors['contributors'][:5]
        ],
        "branch_health": {
            "total_branches": branch['branch_overview']['total_branches'],
            "lock_rate": branch['branch_overview']['lock_rate']
        },
        "anomalies": metrics['anomalies'],
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# 13. 简报生成（用于信息流推送）- 重构版
# ============================================================
def generate_briefing(
    days: int = 7,
    departments: List[str] = None
) -> Dict[str, Any]:
    """
    生成Gerrit代码审查效率简报 - 用于信息流推送
    
    简报设计原则（来自CLAUDE.md）:
    1. 标题动词开头，说清核心发现（包含具体人/事/数据）
    2. 摘要包含三要素：问题 + 影响 + 行动（有具体可操作性）
    3. 只在真正有价值时才推送
    4. 用户看完会想问"为什么"或"怎么办"
    
    Returns:
        简报数据，包含:
        - should_push: 是否值得推送
        - title/summary: 包含具体洞察的标题和摘要
        - full_report: 完整的Markdown分析报告
    """
    try:
        # 获取效率分析数据
        data = analyze_time_efficiency_loss(days=days, departments=departments)
        
        if data.get("error"):
            return {"error": data["error"], "briefing_type": "code_review", "should_push": False}
        
        # 提取各维度数据
        summary_data = data.get("summary", {})
        rework = data.get("rework_analysis", {})
        story_conv = data.get("story_convergence", {})
        branch_dist = data.get("branch_distribution", {})
        change_branch = data.get("change_branch_analysis", {})
        insights = data.get("insights", [])
        
        # 关键指标
        one_shot_rate = summary_data.get("one_shot_rate", 0)
        avg_branches = summary_data.get("avg_branches_per_person", 0)
        total_rework = rework.get("total_rework_count", 0)
        ideal_story_rate = summary_data.get("ideal_story_rate", 0)
        total_records = summary_data.get("total_records", 0)
        total_contributors = summary_data.get("total_contributors", 0)
        
        # ========================================
        # 1. 提取具体洞察（人、事、问题）
        # ========================================
        
        # 疑似借单的Story（最严重的问题）
        suspicious_stories = story_conv.get("high_change_stories", [])[:5]
        
        # 工作最分散的人员
        scattered_people = branch_dist.get("top_scattered_people", [])[:5]
        
        # 异常的change（同分支多次提交）
        abnormal_changes = change_branch.get("abnormal_changes", [])[:3]
        
        # ========================================
        # 2. 确定核心发现和优先级
        # ========================================
        
        findings = []  # 具体发现列表
        should_push = False
        priority = "P2"
        severity = "low"
        
        # 发现1: 借单问题（最严重）
        if suspicious_stories:
            worst_story = suspicious_stories[0]
            issue_id = worst_story.get("issue_id", "未知")
            change_count = worst_story.get("change_id_count", 0)
            contributor_count = worst_story.get("contributor_count", 0)
            possible_issue = worst_story.get("possible_issue", "异常")
            
            if change_count > 50 or contributor_count > 5:
                should_push = True
                priority = "P1"
                severity = "high"
                findings.append({
                    "type": "借单风险",
                    "title": f"Story #{issue_id} 疑似借单",
                    "detail": f"{contributor_count}人参与，{change_count}个change",
                    "reason": possible_issue,
                    "severity": "high"
                })
        
        # 发现2: 工作分散问题
        if scattered_people and avg_branches > 15:
            worst_person = scattered_people[0]
            person_name = worst_person.get("name", "未知")
            branch_count = worst_person.get("branch_count", 0)
            repo_count = worst_person.get("repo_count", 0)
            
            should_push = True
            if severity != "high":
                priority = "P1" if avg_branches > 25 else "P2"
                severity = "high" if avg_branches > 25 else "medium"
            
            findings.append({
                "type": "工作分散",
                "title": f"{person_name}同时维护{branch_count}个分支",
                "detail": f"涉及{repo_count}个仓库，建议排查工作分配",
                "severity": severity
            })
        
        # 发现3: 返工率问题
        if one_shot_rate < 40:
            should_push = True
            if severity == "low":
                priority = "P1"
                severity = "high"
            
            rework_dist = rework.get("distribution", {})
            high_rework_count = rework_dist.get("3次以上", 0)
            
            findings.append({
                "type": "返工率高",
                "title": f"一次性通过率仅{one_shot_rate}%",
                "detail": f"{high_rework_count}个change需要3次以上修改才能合并",
                "severity": "high"
            })
        elif one_shot_rate < 50:
            should_push = True
            findings.append({
                "type": "返工率偏高",
                "title": f"一次性通过率{one_shot_rate}%，低于50%基准",
                "detail": f"总返工{total_rework}次，平均每个change需要{rework.get('avg_patchset', 1):.1f}次修改",
                "severity": "medium"
            })
        
        # ========================================
        # 3. 生成标题（具体、有冲击力）
        # ========================================
        
        if not findings:
            title = f"研发效能正常：{days}天内{total_contributors}人完成{total_records}次提交"
            should_push = False
        elif findings[0]["type"] == "借单风险":
            f = findings[0]
            title = f"发现{len(suspicious_stories)}个疑似借单Story，{f['title']}"
        elif findings[0]["type"] == "工作分散":
            f = findings[0]
            title = f"工作分散告警：{f['title']}，共{len(scattered_people)}人需关注"
        elif findings[0]["type"] in ["返工率高", "返工率偏高"]:
            f = findings[0]
            title = f"返工率告警：{f['title']}，总返工{total_rework}次"
        else:
            title = f"研发效能异常：发现{len(findings)}个问题需关注"
        
        # ========================================
        # 4. 生成摘要（问题 + 影响 + 具体行动）
        # ========================================
        
        summary_lines = []
        
        if findings:
            # 核心发现
            top_finding = findings[0]
            summary_lines.append(f"**核心发现**：{top_finding['title']}")
            summary_lines.append(f"- {top_finding['detail']}")
            
            # 其他发现
            if len(findings) > 1:
                summary_lines.append("")
                summary_lines.append(f"**其他问题**（共{len(findings)}项）：")
                for f in findings[1:3]:
                    summary_lines.append(f"- {f['type']}：{f['title']}")
            
            # 影响范围
            summary_lines.append("")
            summary_lines.append(f"**影响范围**：{days}天内，{total_contributors}名开发者，{total_records}次提交")
            
            # 具体行动建议
            summary_lines.append("")
            summary_lines.append("**建议行动**：")
            if any(f["type"] == "借单风险" for f in findings):
                summary_lines.append(f"1. 排查Story #{suspicious_stories[0].get('issue_id')}，确认是否存在借单")
            if any(f["type"] == "工作分散" for f in findings):
                summary_lines.append(f"2. 与{scattered_people[0].get('name')}沟通，优化分支管理策略")
            if any(f["type"] in ["返工率高", "返工率偏高"] for f in findings):
                summary_lines.append("3. 建立代码提交前自检机制，减少返工")
        else:
            summary_lines.append(f"近{days}天研发效能指标正常，暂无需要关注的异常。")
            summary_lines.append(f"- 一次性通过率：{one_shot_rate}%")
            summary_lines.append(f"- 人均分支数：{avg_branches}")
            summary_lines.append(f"- 参与开发者：{total_contributors}人")
        
        summary_text = "\n".join(summary_lines)
        
        # ========================================
        # 5. 生成完整Markdown报告
        # ========================================
        
        full_report = _generate_full_markdown_report(
            days=days,
            summary_data=summary_data,
            rework=rework,
            story_conv=story_conv,
            branch_dist=branch_dist,
            change_branch=change_branch,
            findings=findings,
            suspicious_stories=suspicious_stories,
            scattered_people=scattered_people,
            abnormal_changes=abnormal_changes
        )
        
        # ========================================
        # 6. 构建返回数据
        # ========================================
        
        metrics = {
            "total_changes": total_records,
            "one_shot_rate": one_shot_rate,
            "total_rework": total_rework,
            "avg_branches_per_person": avg_branches,
            "ideal_story_rate": ideal_story_rate,
            "contributors": total_contributors
        }
        
        return {
            "briefing_type": "dev_efficiency",
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
            "should_push": should_push,
            "priority": priority,
            "severity": severity,
            "title": title,
            "summary": summary_text,
            "impact": f"影响{total_contributors}名开发者，{len(findings)}个效率问题",
            "metrics": metrics,
            "findings": findings,
            "key_data": {
                "suspicious_stories": suspicious_stories[:3],
                "scattered_people": scattered_people[:3],
                "abnormal_changes": abnormal_changes[:3]
            },
            "full_report": full_report,
            "details_available": True
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "briefing_type": "dev_efficiency",
            "should_push": False
        }


def _generate_full_markdown_report(
    days: int,
    summary_data: Dict,
    rework: Dict,
    story_conv: Dict,
    branch_dist: Dict,
    change_branch: Dict,
    findings: List[Dict],
    suspicious_stories: List[Dict],
    scattered_people: List[Dict],
    abnormal_changes: List[Dict]
) -> str:
    """
    生成完整的Markdown分析报告
    """
    lines = []
    
    # 标题
    lines.append(f"# 研发效能分析报告")
    lines.append(f"")
    lines.append(f"**分析周期**：最近 {days} 天")
    lines.append(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    # 执行摘要
    lines.append("## 📊 执行摘要")
    lines.append("")
    lines.append("| 指标 | 数值 | 状态 |")
    lines.append("|------|------|------|")
    
    one_shot_rate = summary_data.get("one_shot_rate", 0)
    avg_branches = summary_data.get("avg_branches_per_person", 0)
    ideal_story_rate = summary_data.get("ideal_story_rate", 0)
    
    status_one_shot = "🔴 需关注" if one_shot_rate < 40 else ("🟡 偏低" if one_shot_rate < 50 else "🟢 正常")
    status_branches = "🔴 严重" if avg_branches > 25 else ("🟡 偏高" if avg_branches > 15 else "🟢 正常")
    status_story = "🔴 需排查" if ideal_story_rate < 50 else "🟢 正常"
    
    lines.append(f"| 总提交数 | {summary_data.get('total_records', 0)} | - |")
    lines.append(f"| 参与开发者 | {summary_data.get('total_contributors', 0)}人 | - |")
    lines.append(f"| 一次性通过率 | {one_shot_rate}% | {status_one_shot} |")
    lines.append(f"| 人均活跃分支 | {avg_branches}个 | {status_branches} |")
    lines.append(f"| 理想Story比例 | {ideal_story_rate}% | {status_story} |")
    lines.append(f"| 总返工次数 | {rework.get('total_rework_count', 0)}次 | - |")
    lines.append("")
    
    # 核心发现
    if findings:
        lines.append("## 🎯 核心发现")
        lines.append("")
        for i, f in enumerate(findings, 1):
            severity_icon = "🔴" if f.get("severity") == "high" else "🟡"
            lines.append(f"### {i}. {severity_icon} {f['title']}")
            lines.append(f"")
            lines.append(f"- **类型**：{f['type']}")
            lines.append(f"- **详情**：{f['detail']}")
            if f.get("reason"):
                lines.append(f"- **可能原因**：{f['reason']}")
            lines.append("")
    
    # 借单风险分析
    if suspicious_stories:
        lines.append("## ⚠️ 借单风险分析")
        lines.append("")
        lines.append("以下Story存在异常，可能是借单或拆分不合理：")
        lines.append("")
        lines.append("| Story ID | Change数 | 参与人数 | 持续天数 | 可能原因 | 参与者 |")
        lines.append("|----------|----------|----------|----------|----------|--------|")
        
        for s in suspicious_stories:
            contributors = s.get("contributors", "")
            if len(contributors) > 30:
                contributors = contributors[:27] + "..."
            lines.append(f"| #{s.get('issue_id', '-')} | {s.get('change_id_count', 0)} | {s.get('contributor_count', 0)} | {s.get('duration_days', 0)}天 | {s.get('possible_issue', '-')} | {contributors} |")
        lines.append("")
        
        lines.append("**建议行动**：")
        lines.append(f"1. 优先排查 Story #{suspicious_stories[0].get('issue_id')}（{suspicious_stories[0].get('change_id_count')}个change）")
        lines.append("2. 与相关开发者确认是否存在借单行为")
        lines.append("3. 如确认借单，协助规范化Story拆分")
        lines.append("")
    
    # 工作分散分析
    if scattered_people:
        lines.append("## 📌 工作分散分析")
        lines.append("")
        lines.append("以下人员同时维护多个分支，工作较分散：")
        lines.append("")
        lines.append("| 姓名 | 工号 | 分支数 | 仓库数 | 提交数 |")
        lines.append("|------|------|--------|--------|--------|")
        
        for p in scattered_people:
            lines.append(f"| {p.get('name', '-')} | {p.get('wkno', '-')} | {p.get('branch_count', 0)} | {p.get('repo_count', 0)} | {p.get('change_count', 0)} |")
        lines.append("")
        
        lines.append("**建议行动**：")
        lines.append(f"1. 与 {scattered_people[0].get('name')} 沟通，了解多分支的业务原因")
        lines.append("2. 评估是否可以收敛分支数量")
        lines.append("3. 建立分支清理机制，及时删除已合并分支")
        lines.append("")
    
    # 返工率分析
    if rework:
        lines.append("## 🔄 返工率分析")
        lines.append("")
        
        dist = rework.get("distribution", {})
        lines.append("**Patchset分布**：")
        lines.append("")
        lines.append("| 修改次数 | 数量 | 占比 |")
        lines.append("|----------|------|------|")
        
        total = sum(dist.values()) if dist else 1
        for key in ["1次通过", "2次通过", "3次通过", "3次以上"]:
            count = dist.get(key, 0)
            pct = count / total * 100 if total > 0 else 0
            lines.append(f"| {key} | {count} | {pct:.1f}% |")
        lines.append("")
        
        lines.append(f"**平均修改次数**：{rework.get('avg_patchset', 0):.2f}次/change")
        lines.append("")
        
        if one_shot_rate < 50:
            lines.append("**建议行动**：")
            lines.append("1. 建立代码提交前的自检清单")
            lines.append("2. 加强单元测试覆盖")
            lines.append("3. 在代码评审中关注常见问题模式")
            lines.append("")
    
    # 异常Change分析
    if abnormal_changes:
        lines.append("## 🔍 异常Change分析")
        lines.append("")
        lines.append("以下Change存在同分支多次提交的情况：")
        lines.append("")
        
        for c in abnormal_changes:
            change_id = c.get("change_id", "")
            if len(change_id) > 20:
                change_id = change_id[:17] + "..."
            lines.append(f"- **{change_id}**")
            lines.append(f"  - 分支：{c.get('branch', '-')}")
            lines.append(f"  - 仓库：{c.get('repo', '-')}")
            lines.append(f"  - 记录数：{c.get('record_count', 0)}（放弃{c.get('abandoned_count', 0)}，合并{c.get('merged_count', 0)}）")
            if c.get("possible_reason"):
                lines.append(f"  - 可能原因：{c.get('possible_reason')}")
            lines.append("")
    
    # 总结与建议
    lines.append("## 📝 总结与建议")
    lines.append("")
    
    if findings:
        lines.append(f"本次分析发现 **{len(findings)}** 个需要关注的问题：")
        lines.append("")
        for i, f in enumerate(findings, 1):
            lines.append(f"{i}. {f['type']}：{f['title']}")
        lines.append("")
        lines.append("**优先级建议**：")
        if any(f["type"] == "借单风险" for f in findings):
            lines.append("- 🔴 **高**：排查借单问题，这可能影响需求追溯和工作量统计")
        if any(f["type"] == "工作分散" for f in findings):
            lines.append("- 🟡 **中**：关注工作分散问题，避免开发者精力过度分散")
        if any(f["type"] in ["返工率高", "返工率偏高"] for f in findings):
            lines.append("- 🟡 **中**：改善返工率，提升开发效率")
    else:
        lines.append("本次分析未发现明显异常，研发效能指标正常。")
        lines.append("")
        lines.append("**持续关注**：")
        lines.append("- 保持一次性通过率在50%以上")
        lines.append("- 控制人均分支数在15个以内")
        lines.append("- 定期清理已完成的分支")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*报告由研发效能分析官自动生成*")
    
    return "\n".join(lines)


# ============================================================
# 14. A2UI Schema 生成（用于动态UI渲染）
# ============================================================
def generate_ui_schema(
    days: int = 7,
    departments: List[str] = None
) -> Dict[str, Any]:
    """
    生成A2UI格式的UI Schema - 用于App动态渲染
    
    支持的组件类型：
    - metric_cards: 指标卡片
    - bar_chart: 柱状图
    - alert_list: 告警列表
    - table: 表格
    - markdown: Markdown文本
    
    Returns:
        A2UI格式的UI Schema
    """
    try:
        # 获取效率分析数据
        data = analyze_time_efficiency_loss(days=days, departments=departments)
        
        if data.get("error"):
            return {"error": data["error"]}
        
        summary = data.get("summary", {})
        insights = data.get("insights", [])
        rework = data.get("rework_analysis", {})
        story_conv = data.get("story_convergence", {})
        branch_dist = data.get("branch_distribution", {})
        
        sections = []
        
        # 1. 指标卡片
        one_shot_rate = summary.get("one_shot_rate", 0)
        sections.append({
            "type": "metric_cards",
            "title": "关键指标",
            "cards": [
                {
                    "label": "总提交数",
                    "value": str(summary.get("total_records", 0)),
                    "trend": "flat"
                },
                {
                    "label": "一次性通过率",
                    "value": f"{one_shot_rate}%",
                    "trend": "down" if one_shot_rate < 50 else "up",
                    "change": "需关注" if one_shot_rate < 50 else "正常"
                },
                {
                    "label": "人均分支数",
                    "value": str(summary.get("avg_branches_per_person", 0)),
                    "trend": "down" if summary.get("avg_branches_per_person", 0) > 10 else "flat"
                },
                {
                    "label": "活跃开发者",
                    "value": str(summary.get("total_contributors", 0)),
                    "trend": "flat"
                }
            ]
        })
        
        # 2. 告警列表（如果有）
        if insights:
            alerts = []
            for insight in insights:
                alerts.append({
                    "severity": insight.get("severity", "medium"),
                    "message": insight.get("finding", "")
                })
            
            sections.append({
                "type": "alert_list",
                "title": "效率洞察",
                "alerts": alerts
            })
        
        # 3. 返工分布柱状图
        rework_dist = rework.get("distribution", {})
        if rework_dist:
            sections.append({
                "type": "bar_chart",
                "title": "Patchset分布",
                "xAxis": list(rework_dist.keys()),
                "series": [{
                    "name": "提交数",
                    "data": list(rework_dist.values())
                }]
            })
        
        # 4. Story拆分分布
        story_dist = story_conv.get("distribution", {})
        if story_dist:
            sections.append({
                "type": "bar_chart",
                "title": "Story拆分情况",
                "xAxis": list(story_dist.keys()),
                "series": [{
                    "name": "Story数",
                    "data": list(story_dist.values())
                }]
            })
        
        # 5. 分支分散度Top10表格
        top_people = branch_dist.get("top_scattered_people", [])[:5]
        if top_people:
            sections.append({
                "type": "table",
                "title": "分支分散度Top5",
                "headers": ["姓名", "分支数", "提交数", "仓库数"],
                "rows": [
                    [p["name"], str(p["branch_count"]), str(p["change_count"]), str(p["repo_count"])]
                    for p in top_people
                ]
            })
        
        return {
            "type": "briefing",
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
            "content": {
                "sections": sections
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "type": "briefing",
            "version": "1.0"
        }


def main():
    """主函数：从stdin读取参数，执行分析"""
    try:
        input_data = sys.stdin.read().strip()
        
        if input_data:
            params = json.loads(input_data)
        else:
            params = {"action": "summary", "days": 7}
        
        result = run_analysis(params)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "data_source": "mysql"
        }
        print(json.dumps(error_result, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
