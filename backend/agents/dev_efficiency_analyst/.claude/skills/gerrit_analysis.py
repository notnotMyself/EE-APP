#!/usr/bin/env python3
"""
Gerrit Analysis Skill
分析Gerrit代码审查数据的能力 - 从MySQL数据库获取数据
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 数据库配置
# 集群主地址: rabbit-mysql-test0.mysql.oppo.test:33066 或 10.52.61.119:33066
# 集群只读地址: 10.52.61.119:33067
DB_CONFIG = {
    "dialect": "mysql",
    "host": "10.52.61.119",  # 使用IP地址，避免DNS解析问题
    "port": 33067,  # 只读端口，用于分析查询
    "username": "ee_read",
    "password": "OdX0M4nAxRjtN_wXMyG34mYyZPXEwLOS",
    "database": "rabbit_test"
}


def get_db_connection():
    """
    获取MySQL数据库连接
    
    Returns:
        数据库连接对象
    """
    try:
        import pymysql
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["username"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG.get("database", "gerrit"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except ImportError:
        raise ImportError("pymysql is required. Install it with: pip install pymysql")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")


def fetch_gerrit_changes(
    days: int = 7,
    project: Optional[str] = None,
    author: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    从数据库获取Gerrit代码变更数据
    
    Args:
        days: 获取最近多少天的数据
        project: 可选，过滤特定项目
        author: 可选，过滤特定作者
        
    Returns:
        Gerrit changes数据列表
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 构建查询SQL (根据实际表结构调整)
            sql = """
                SELECT 
                    change_id,
                    project,
                    branch,
                    subject,
                    owner,
                    status,
                    created,
                    updated,
                    submitted,
                    insertions,
                    deletions,
                    revision_count
                FROM changes
                WHERE created >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            params = [days]
            
            if project:
                sql += " AND project = %s"
                params.append(project)
            
            if author:
                sql += " AND owner = %s"
                params.append(author)
            
            sql += " ORDER BY created DESC"
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # 转换日期格式为字符串
            for row in results:
                for key in ['created', 'updated', 'submitted']:
                    if row.get(key) and isinstance(row[key], datetime):
                        row[key] = row[key].isoformat()
            
            return results
    finally:
        connection.close()


def fetch_review_comments(change_ids: List[int]) -> Dict[int, List[Dict]]:
    """
    获取指定变更的Review评论数据
    
    Args:
        change_ids: 变更ID列表
        
    Returns:
        变更ID到评论列表的映射
    """
    if not change_ids:
        return {}
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(change_ids))
            sql = f"""
                SELECT 
                    change_id,
                    reviewer,
                    comment_text,
                    created_at,
                    line_number,
                    file_path
                FROM review_comments
                WHERE change_id IN ({placeholders})
                ORDER BY created_at
            """
            cursor.execute(sql, change_ids)
            results = cursor.fetchall()
            
            # 按change_id分组
            comments_map = {}
            for row in results:
                cid = row['change_id']
                if cid not in comments_map:
                    comments_map[cid] = []
                if isinstance(row.get('created_at'), datetime):
                    row['created_at'] = row['created_at'].isoformat()
                comments_map[cid].append(row)
            
            return comments_map
    finally:
        connection.close()


def analyze_review_metrics(changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析代码审查指标

    Args:
        changes: Gerrit changes数据列表

    Returns:
        分析结果字典
    """
    if not changes:
        return {
            "error": "No data to analyze",
            "metrics": {}
        }

    # 提取Review耗时
    review_times = []
    rework_count = 0
    total_count = len(changes)
    total_insertions = 0
    total_deletions = 0

    for change in changes:
        # 计算Review耗时（从创建到合并的时间）
        created_str = change.get('created', '')
        updated_str = change.get('updated', '')
        
        if created_str and updated_str:
            if isinstance(created_str, str):
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00').replace('+00:00', ''))
            else:
                created = created_str
            
            if isinstance(updated_str, str):
                updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00').replace('+00:00', ''))
            else:
                updated = updated_str
                
            review_time_hours = (updated - created).total_seconds() / 3600
            review_times.append(review_time_hours)

        # 检测返工（多次revision）
        revision_count = change.get('revision_count', 1)
        if revision_count > 2:
            rework_count += 1
        
        # 统计代码变更量
        total_insertions += change.get('insertions', 0) or 0
        total_deletions += change.get('deletions', 0) or 0

    # 计算统计指标
    if review_times:
        review_times.sort()
        n = len(review_times)
        median_time = review_times[n // 2]
        p95_time = review_times[int(n * 0.95)]
        avg_time = sum(review_times) / n
    else:
        median_time = p95_time = avg_time = 0
        n = 0
    
    rework_rate = rework_count / total_count if total_count > 0 else 0

    # 检测异常
    anomalies = []

    if median_time > 24:
        anomalies.append({
            "type": "high_review_time",
            "severity": "warning",
            "message": f"Review中位耗时({median_time:.1f}小时)超过24小时阈值",
            "value": median_time,
            "threshold": 24
        })

    if p95_time > 72:
        anomalies.append({
            "type": "high_p95_time",
            "severity": "critical",
            "message": f"Review P95耗时({p95_time:.1f}小时)超过72小时阈值",
            "value": p95_time,
            "threshold": 72
        })

    if rework_rate > 0.15:
        anomalies.append({
            "type": "high_rework_rate",
            "severity": "warning",
            "message": f"返工率({rework_rate*100:.1f}%)超过15%阈值",
            "value": rework_rate * 100,
            "threshold": 15
        })

    return {
        "metrics": {
            "total_changes": total_count,
            "median_review_time_hours": round(median_time, 2),
            "p95_review_time_hours": round(p95_time, 2),
            "avg_review_time_hours": round(avg_time, 2),
            "rework_rate_percent": round(rework_rate * 100, 2),
            "rework_count": rework_count,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions
        },
        "anomalies": anomalies,
        "data_source": "mysql",
        "timestamp": datetime.now().isoformat()
    }


def run_analysis(days: int = 7, project: str = None, author: str = None) -> Dict[str, Any]:
    """
    执行完整的Gerrit分析流程
    
    Args:
        days: 分析最近多少天的数据
        project: 可选，过滤特定项目
        author: 可选，过滤特定作者
        
    Returns:
        分析结果
    """
    try:
        # 从数据库获取数据
        changes = fetch_gerrit_changes(days=days, project=project, author=author)
        
        # 分析数据
        result = analyze_review_metrics(changes)
        result["query_params"] = {
            "days": days,
            "project": project,
            "author": author
        }
        
        return result
    except Exception as e:
        return {
            "error": str(e),
            "metrics": {},
            "data_source": "mysql"
        }


def main():
    """主函数：从stdin读取参数或数据，输出分析结果"""
    try:
        # 从stdin读取JSON数据
        input_data = sys.stdin.read().strip()
        
        if input_data:
            data = json.loads(input_data)
            
            # 如果提供了changes数据，直接分析
            if 'changes' in data:
                result = analyze_review_metrics(data['changes'])
            else:
                # 否则作为查询参数，从数据库获取数据
                result = run_analysis(
                    days=data.get('days', 7),
                    project=data.get('project'),
                    author=data.get('author')
                )
        else:
            # 默认分析最近7天数据
            result = run_analysis(days=7)

        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))

        return 0
    except Exception as e:
        error_result = {
            "error": str(e),
            "metrics": {},
            "data_source": "mysql"
        }
        print(json.dumps(error_result, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
