#!/usr/bin/env python3
"""
检查昨日Gerrit数据详情
"""
import pymysql
from datetime import datetime, timedelta
import json

DB_CONFIG = {
    "host": "10.52.61.119",
    "port": 33067,
    "user": "ee_read",
    "password": "OdX0M4nAxRjtN_wXMyG34mYyZPXEwLOS",
    "database": "rabbit_test",
    "charset": 'utf8mb4',
    "cursorclass": pymysql.cursors.DictCursor
}

def main():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # 获取昨日数据
            sql = """
                SELECT
                    change_id,
                    owner,
                    status,
                    repo,
                    patchset_id as revisions,
                    insertions,
                    deletions,
                    created_at,
                    updated_at,
                    TIMESTAMPDIFF(HOUR, created_at,
                        CASE WHEN status = 'MERGED' THEN updated_at ELSE NOW() END
                    ) as hours_elapsed
                FROM gerrit_change
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
                  AND created_at < CURDATE()
                ORDER BY created_at DESC
            """
            cursor.execute(sql)
            changes = cursor.fetchall()

            # 计算统计指标
            total = len(changes)
            merged = sum(1 for c in changes if c['status'] == 'MERGED')
            pending = sum(1 for c in changes if c['status'] == 'NEW')
            abandoned = sum(1 for c in changes if c['status'] == 'ABANDONED')

            # 返工率计算
            rework_changes = [c for c in changes if c['revisions'] > 1]
            rework_rate = len(rework_changes) / total * 100 if total > 0 else 0

            # Review耗时计算（仅已合并）
            merged_changes = [c for c in changes if c['status'] == 'MERGED']
            if merged_changes:
                review_times = sorted([c['hours_elapsed'] for c in merged_changes])
                median_time = review_times[len(review_times)//2] if review_times else 0
                p95_idx = int(len(review_times) * 0.95)
                p95_time = review_times[p95_idx] if review_times else 0
            else:
                median_time = None
                p95_time = None

            result = {
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": {
                    "total_changes": total,
                    "merged": merged,
                    "pending": pending,
                    "abandoned": abandoned,
                    "merge_rate": round(merged / total * 100, 2) if total > 0 else 0,
                    "rework_rate": round(rework_rate, 2)
                },
                "review_time": {
                    "median_hours": median_time,
                    "p95_hours": p95_time,
                    "merged_count": len(merged_changes)
                },
                "changes": [
                    {
                        "change_id": c['change_id'],
                        "owner": c['owner'],
                        "status": c['status'],
                        "repo": c['repo'],
                        "revisions": c['revisions'],
                        "lines": f"+{c['insertions']}/-{c['deletions']}",
                        "hours_elapsed": c['hours_elapsed'],
                        "created_at": c['created_at'].strftime("%Y-%m-%d %H:%M:%S") if c['created_at'] else None
                    }
                    for c in changes
                ]
            }

            print(json.dumps(result, indent=2, ensure_ascii=False))

    finally:
        connection.close()

if __name__ == "__main__":
    main()
