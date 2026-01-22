#!/usr/bin/env python3
"""
检查指定周期的Gerrit数据统计
"""
import pymysql
from datetime import datetime, timedelta
import json
import sys

DB_CONFIG = {
    "host": "10.52.61.119",
    "port": 33067,
    "user": "ee_read",
    "password": "OdX0M4nAxRjtN_wXMyG34mYyZPXEwLOS",
    "database": "rabbit_test",
    "charset": 'utf8mb4',
    "cursorclass": pymysql.cursors.DictCursor
}

def analyze_period(days):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # 获取指定周期的数据
            sql = """
                SELECT
                    change_id,
                    owner,
                    status,
                    patchset_id as revisions,
                    insertions,
                    deletions,
                    created_at,
                    updated_at,
                    TIMESTAMPDIFF(HOUR, created_at, updated_at) as hours_to_update
                FROM gerrit_change
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY created_at DESC
            """
            cursor.execute(sql, [days])
            changes = cursor.fetchall()

            # 统计指标
            total = len(changes)
            merged = [c for c in changes if c['status'] == 'MERGED']
            pending = [c for c in changes if c['status'] == 'NEW']
            abandoned = [c for c in changes if c['status'] == 'ABANDONED']

            # 返工率
            rework_changes = [c for c in changes if c['revisions'] > 1]
            rework_rate = len(rework_changes) / total * 100 if total > 0 else 0

            # Review耗时（仅已合并的）
            review_times = []
            for c in merged:
                if c['hours_to_update'] is not None and c['hours_to_update'] >= 0:
                    review_times.append(c['hours_to_update'])

            if review_times:
                review_times.sort()
                median_time = review_times[len(review_times)//2]
                p95_idx = int(len(review_times) * 0.95)
                p95_time = review_times[p95_idx] if p95_idx < len(review_times) else review_times[-1]
                avg_time = sum(review_times) / len(review_times)
            else:
                median_time = avg_time = p95_time = None

            # 代码变更量
            total_insertions = sum(c['insertions'] or 0 for c in changes)
            total_deletions = sum(c['deletions'] or 0 for c in changes)

            result = {
                "period_days": days,
                "summary": {
                    "total_changes": total,
                    "merged": len(merged),
                    "pending": len(pending),
                    "abandoned": len(abandoned),
                    "merge_rate": round(len(merged) / total * 100, 2) if total > 0 else 0,
                    "rework_rate": round(rework_rate, 2)
                },
                "review_time": {
                    "median_hours": round(median_time, 1) if median_time is not None else None,
                    "avg_hours": round(avg_time, 1) if avg_time is not None else None,
                    "p95_hours": round(p95_time, 1) if p95_time is not None else None,
                    "sample_size": len(review_times)
                },
                "code_volume": {
                    "total_insertions": total_insertions,
                    "total_deletions": total_deletions,
                    "net_change": total_insertions - total_deletions
                },
                "thresholds_check": {
                    "median_exceeds_24h": median_time > 24 if median_time is not None else None,
                    "p95_exceeds_72h": p95_time > 72 if p95_time is not None else None,
                    "rework_exceeds_15pct": rework_rate > 15
                }
            }

            print(json.dumps(result, indent=2, ensure_ascii=False))

    finally:
        connection.close()

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    analyze_period(days)
