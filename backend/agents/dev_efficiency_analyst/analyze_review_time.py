#!/usr/bin/env python3
"""
详细的Review耗时分析 - 关注待处理时长
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

def analyze_review_time(days):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # 查询最近days天的数据
            sql = """
                SELECT
                    change_id,
                    owner,
                    status,
                    repo,
                    patchset_id as revisions,
                    created_at,
                    updated_at,
                    TIMESTAMPDIFF(HOUR, created_at, updated_at) as hours_to_merge,
                    TIMESTAMPDIFF(HOUR, created_at, NOW()) as hours_pending
                FROM gerrit_change
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY created_at DESC
            """
            cursor.execute(sql, [days])
            changes = cursor.fetchall()

            # 按状态分组
            merged = []
            pending = []
            abandoned = []

            for c in changes:
                if c['status'] == 'MERGED':
                    merged.append(c)
                elif c['status'] == 'NEW':
                    pending.append(c)
                elif c['status'] == 'ABANDONED':
                    abandoned.append(c)

            # 已合并的Review耗时
            merged_times = [c['hours_to_merge'] for c in merged if c['hours_to_merge'] is not None]
            merged_times.sort()

            # 待处理的已等待时长
            pending_times = [c['hours_pending'] for c in pending if c['hours_pending'] is not None]
            pending_times.sort()

            def calc_percentiles(times):
                if not times:
                    return None, None, None, None
                n = len(times)
                return (
                    round(times[n//2], 1),  # P50
                    round(sum(times)/n, 1),  # avg
                    round(times[int(n*0.95)] if int(n*0.95) < n else times[-1], 1),  # P95
                    round(times[-1], 1)  # max
                )

            merged_p50, merged_avg, merged_p95, merged_max = calc_percentiles(merged_times)
            pending_p50, pending_avg, pending_p95, pending_max = calc_percentiles(pending_times)

            # 识别超时的PR
            pending_over_24h = [c for c in pending if c['hours_pending'] > 24]
            pending_over_72h = [c for c in pending if c['hours_pending'] > 72]
            merged_over_24h = [c for c in merged if c['hours_to_merge'] > 24]

            result = {
                "period_days": days,
                "merged_review_time": {
                    "count": len(merged),
                    "median_hours": merged_p50,
                    "avg_hours": merged_avg,
                    "p95_hours": merged_p95,
                    "max_hours": merged_max,
                    "over_24h_count": len(merged_over_24h)
                },
                "pending_wait_time": {
                    "count": len(pending),
                    "median_hours": pending_p50,
                    "avg_hours": pending_avg,
                    "p95_hours": pending_p95,
                    "max_hours": pending_max,
                    "over_24h_count": len(pending_over_24h),
                    "over_72h_count": len(pending_over_72h)
                },
                "anomalies": [],
                "top_pending_changes": [
                    {
                        "change_id": c['change_id'][:20],
                        "owner": c['owner'],
                        "repo": c['repo'],
                        "hours_waiting": c['hours_pending'],
                        "created_at": c['created_at'].strftime("%Y-%m-%d %H:%M") if c['created_at'] else None
                    }
                    for c in sorted(pending, key=lambda x: x['hours_pending'], reverse=True)[:10]
                ]
            }

            # 异常检测
            if pending_p50 and pending_p50 > 24:
                result["anomalies"].append({
                    "type": "high_pending_median",
                    "severity": "warning",
                    "message": f"待处理PR中位等待时长({pending_p50}小时)超过24小时阈值",
                    "value": pending_p50,
                    "threshold": 24
                })

            if pending_p95 and pending_p95 > 72:
                result["anomalies"].append({
                    "type": "high_pending_p95",
                    "severity": "critical",
                    "message": f"待处理PR的P95等待时长({pending_p95}小时)超过72小时阈值",
                    "value": pending_p95,
                    "threshold": 72
                })

            if len(pending_over_72h) > 5:
                result["anomalies"].append({
                    "type": "many_stale_prs",
                    "severity": "warning",
                    "message": f"有{len(pending_over_72h)}个PR已等待超过72小时，可能造成交付阻塞",
                    "value": len(pending_over_72h),
                    "threshold": 5
                })

            print(json.dumps(result, indent=2, ensure_ascii=False))

    finally:
        connection.close()

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    analyze_review_time(days)
