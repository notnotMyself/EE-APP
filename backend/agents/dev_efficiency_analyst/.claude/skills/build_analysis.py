#!/usr/bin/env python3
"""
Build Analysis Skill
门禁构建数据分析能力 - 从MySQL数据库获取构建数据并分析

设计理念：问题导向，不只摆指标，而是呈现问题和解决思路

功能：
1. 问题发现：哪些平台/组件/流程落后，落后多少，趋势如何
2. P95落后分析：找出低于整体P95的平台，量化差距
3. 人员维度：从个人角度看构建优化点
4. 组件分析：不同编译组件的耗时占比和瓶颈
5. 趋势洞察：哪些在恶化，哪些在改善，提供解决思路

注意：此技能仅执行只读查询，不会修改任何数据
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 数据库配置 - 门禁构建数据库（只读）
BUILD_DB_CONFIG = {
    "dialect": "mysql",
    "host": "rn-test-mysql.mysql.oppo.test",
    "port": 33066,
    "username": "rn_ddl",
    "password": "LXK0Cva89SWDj47x9QbRWJfgETp7JiRP",
    "database": "rn_test"
}

# 芯片平台中文名称映射（SM=高通Snapdragon, MT=联发科MediaTek）
PLATFORM_VENDOR_MAP = {
    "SM": "高通",
    "MT": "联发科",
}

# 常见芯片型号的中文说明
CHIP_INFO = {
    # 高通旗舰
    "SM8750": "高通骁龙8 Elite (旗舰)",
    "SM8850": "高通骁龙8 Elite+ (旗舰)",
    "SM8650": "高通骁龙8 Gen3 (旗舰)",
    "SM8550": "高通骁龙8 Gen2 (旗舰)",
    "SM8450": "高通骁龙8 Gen1 (旗舰)",
    # 高通中端
    "SM7750": "高通骁龙7+ Gen3 (中高端)",
    "SM7675": "高通骁龙7s Gen3 (中端)",
    "SM7550": "高通骁龙7 Gen3 (中端)",
    "SM7475": "高通骁龙7+ Gen2 (中端)",
    "SM7435": "高通骁龙7s Gen2 (中端)",
    "SM7325": "高通骁龙778G (中端)",
    # 高通入门
    "SM6650": "高通骁龙6 Gen3 (入门)",
    "SM6450": "高通骁龙6 Gen1 (入门)",
    "SM6375": "高通骁龙695 (入门)",
    "SM6225": "高通骁龙680 (入门)",
    # 联发科旗舰
    "MT6991": "联发科天玑9400 (旗舰)",
    "MT6993": "联发科天玑9300+ (旗舰)",
    "MT6989": "联发科天玑9300 (旗舰)",
    "MT6985": "联发科天玑9200+ (旗舰)",
    # 联发科中端
    "MT6899": "联发科天玑8400 (中高端)",
    "MT6897": "联发科天玑8300 (中高端)",
    "MT6896": "联发科天玑8200 (中端)",
    "MT6895": "联发科天玑8100 (中端)",
    "MT6878": "联发科天玑7300 (中端)",
    "MT6877": "联发科天玑1080 (中端)",
    # 联发科入门
    "MT6835": "联发科天玑6300 (入门)",
    "MT6789": "联发科Helio G99 (入门)",
    "MT6769": "联发科Helio G85 (入门)",
}


def get_platform_display_name(baseline_name: str) -> str:
    """
    获取平台的显示名称（中文）
    
    Args:
        baseline_name: 平台代号，如 SM8750_16
        
    Returns:
        中文显示名称
    """
    if not baseline_name:
        return "未知平台"
    
    # 提取芯片型号（去掉Android版本后缀）
    parts = baseline_name.split("_")
    chip = parts[0] if parts else baseline_name
    
    # 查找中文名称
    if chip in CHIP_INFO:
        return f"{baseline_name} ({CHIP_INFO[chip]})"
    
    # 识别厂商
    for prefix, vendor in PLATFORM_VENDOR_MAP.items():
        if chip.startswith(prefix):
            return f"{baseline_name} ({vendor})"
    
    return baseline_name


def get_vendor_name(baseline_name: str) -> str:
    """获取芯片厂商名称"""
    if not baseline_name:
        return "未知"
    for prefix, vendor in PLATFORM_VENDOR_MAP.items():
        if baseline_name.startswith(prefix):
            return vendor
    return "其他"


def get_db_connection():
    """
    获取MySQL数据库连接（只读）
    
    Returns:
        数据库连接对象
    """
    try:
        import pymysql
        connection = pymysql.connect(
            host=BUILD_DB_CONFIG["host"],
            port=BUILD_DB_CONFIG["port"],
            user=BUILD_DB_CONFIG["username"],
            password=BUILD_DB_CONFIG["password"],
            database=BUILD_DB_CONFIG["database"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            read_timeout=30,
            write_timeout=30
        )
        return connection
    except ImportError:
        raise ImportError("pymysql is required. Install it with: pip install pymysql")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")


def calculate_percentiles(values: List[float], percentiles: List[int] = [50, 75, 90, 95, 99]) -> Dict[str, float]:
    """
    计算分位数
    
    Args:
        values: 数值列表
        percentiles: 要计算的分位数列表
        
    Returns:
        分位数字典，如 {"p50": 100, "p95": 200}
    """
    if not values:
        return {f"p{p}": 0 for p in percentiles}
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    result = {}
    
    for p in percentiles:
        index = int(n * p / 100)
        index = min(index, n - 1)
        result[f"p{p}"] = round(sorted_values[index], 2)
    
    result["avg"] = round(sum(values) / n, 2)
    result["min"] = round(min(values), 2)
    result["max"] = round(max(values), 2)
    result["count"] = n
    
    return result


def fetch_build_data(
    days: int = 7,
    baseline_name: Optional[str] = None,
    android_version: Optional[str] = None,
    compile_component: Optional[str] = None,
    created_by: Optional[str] = None,
    limit: int = 10000
) -> List[Dict[str, Any]]:
    """
    从数据库获取构建数据（只读查询）
    
    Args:
        days: 获取最近多少天的数据
        baseline_name: 可选，过滤特定平台（如 SM8750, MT6991）
        android_version: 可选，过滤特定Android版本
        compile_component: 可选，过滤特定编译组件
        created_by: 可选，过滤特定创建人
        limit: 最大返回记录数
        
    Returns:
        构建数据列表
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 构建只读查询SQL
            sql = """
                SELECT 
                    task_num,
                    created_name,
                    baseline_name,
                    android_version,
                    compile_component,
                    CAST(build_time AS SIGNED) as build_time_sec,
                    CAST(download_time AS SIGNED) as download_time_sec,
                    CAST(copy_time AS SIGNED) as copy_time_sec,
                    CAST(ofp_time AS SIGNED) as ofp_time_sec,
                    CAST(pipeline_time AS SIGNED) as pipeline_time_sec,
                    task_create_time,
                    build_trigger_time,
                    build_start_time,
                    build_end_time,
                    created_by
                FROM personal_build
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND build_end_time IS NOT NULL
                AND build_start_time IS NOT NULL
            """
            params = [days]
            
            if baseline_name:
                sql += " AND baseline_name = %s"
                params.append(baseline_name)
            
            if android_version:
                sql += " AND android_version LIKE %s"
                params.append(f"%{android_version}%")
            
            if compile_component:
                sql += " AND compile_component LIKE %s"
                params.append(f"%{compile_component}%")
            
            if created_by:
                sql += " AND created_by = %s"
                params.append(created_by)
            
            sql += " ORDER BY build_end_time DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # 转换日期格式
            for row in results:
                for key in ['task_create_time', 'build_trigger_time', 'build_start_time', 'build_end_time']:
                    if row.get(key) and isinstance(row[key], datetime):
                        row[key] = row[key].isoformat()
            
            return results
    finally:
        connection.close()


def analyze_build_metrics(builds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析构建指标
    
    Args:
        builds: 构建数据列表
        
    Returns:
        分析结果字典
    """
    if not builds:
        return {
            "error": "No data to analyze",
            "metrics": {}
        }
    
    # 提取各阶段耗时
    build_times = []
    download_times = []
    copy_times = []
    ofp_times = []
    pipeline_times = []
    total_durations = []
    
    for build in builds:
        # 各阶段耗时（秒转分钟）
        if build.get('build_time_sec'):
            build_times.append(build['build_time_sec'] / 60)
        if build.get('download_time_sec'):
            download_times.append(build['download_time_sec'] / 60)
        if build.get('copy_time_sec'):
            copy_times.append(build['copy_time_sec'] / 60)
        if build.get('ofp_time_sec'):
            ofp_times.append(build['ofp_time_sec'] / 60)
        if build.get('pipeline_time_sec'):
            pipeline_times.append(build['pipeline_time_sec'] / 60)
        
        # 计算端到端耗时
        start = build.get('build_start_time')
        end = build.get('build_end_time')
        if start and end:
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
            duration_min = (end - start).total_seconds() / 60
            if duration_min > 0:
                total_durations.append(duration_min)
    
    # 计算分位数
    metrics = {
        "total_builds": len(builds),
        "total_duration_minutes": calculate_percentiles(total_durations),
        "build_time_minutes": calculate_percentiles(build_times),
        "download_time_minutes": calculate_percentiles(download_times),
        "copy_time_minutes": calculate_percentiles(copy_times),
        "ofp_time_minutes": calculate_percentiles(ofp_times),
        "pipeline_time_minutes": calculate_percentiles(pipeline_times)
    }
    
    # 计算各阶段平均占比
    if pipeline_times:
        avg_pipeline = sum(pipeline_times) / len(pipeline_times)
        avg_build = sum(build_times) / len(build_times) if build_times else 0
        avg_download = sum(download_times) / len(download_times) if download_times else 0
        avg_copy = sum(copy_times) / len(copy_times) if copy_times else 0
        avg_ofp = sum(ofp_times) / len(ofp_times) if ofp_times else 0
        
        if avg_pipeline > 0:
            metrics["stage_ratio_percent"] = {
                "build": round(avg_build / avg_pipeline * 100, 1),
                "download": round(avg_download / avg_pipeline * 100, 1),
                "copy": round(avg_copy / avg_pipeline * 100, 1),
                "ofp": round(avg_ofp / avg_pipeline * 100, 1)
            }
    
    return metrics


def analyze_by_dimension(
    days: int = 7,
    dimension: str = "baseline_name",
    top_n: int = 10
) -> Dict[str, Any]:
    """
    按维度分组分析构建耗时
    
    Args:
        days: 分析最近多少天的数据
        dimension: 分组维度 (baseline_name, android_version, compile_component)
        top_n: 返回前N个结果
        
    Returns:
        分组分析结果
    """
    valid_dimensions = ["baseline_name", "android_version", "compile_component", "created_by"]
    if dimension not in valid_dimensions:
        return {"error": f"Invalid dimension. Must be one of: {valid_dimensions}"}
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = f"""
                SELECT 
                    {dimension} as dimension_value,
                    COUNT(*) as build_count,
                    AVG(CAST(pipeline_time AS SIGNED)) / 60 as avg_pipeline_min,
                    AVG(CAST(build_time AS SIGNED)) / 60 as avg_build_min
                FROM personal_build
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND build_end_time IS NOT NULL
                AND {dimension} IS NOT NULL
                AND {dimension} != ''
                GROUP BY {dimension}
                ORDER BY avg_pipeline_min DESC
                LIMIT %s
            """
            cursor.execute(sql, [days, top_n])
            results = cursor.fetchall()
            
            return {
                "dimension": dimension,
                "days": days,
                "results": [
                    {
                        "name": row["dimension_value"],
                        "build_count": row["build_count"],
                        "avg_pipeline_minutes": round(float(row["avg_pipeline_min"] or 0), 1),
                        "avg_build_minutes": round(float(row["avg_build_min"] or 0), 1)
                    }
                    for row in results
                ]
            }
    finally:
        connection.close()


def analyze_percentile_by_platform(
    days: int = 7,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    按平台分析构建耗时分位数（P50/P95/P99）
    
    Args:
        days: 分析最近多少天的数据
        top_n: 返回前N个平台
        
    Returns:
        各平台的分位数分析结果
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 先获取构建量最多的平台
            sql = """
                SELECT baseline_name, COUNT(*) as cnt
                FROM personal_build
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND baseline_name IS NOT NULL AND baseline_name != ''
                GROUP BY baseline_name
                ORDER BY cnt DESC
                LIMIT %s
            """
            cursor.execute(sql, [days, top_n])
            platforms = [row["baseline_name"] for row in cursor.fetchall()]
            
            results = []
            for platform in platforms:
                sql = """
                    SELECT CAST(pipeline_time AS SIGNED) / 60 as duration_min
                    FROM personal_build
                    WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND baseline_name = %s
                    AND pipeline_time IS NOT NULL AND pipeline_time != ''
                    ORDER BY CAST(pipeline_time AS SIGNED)
                """
                cursor.execute(sql, [days, platform])
                durations = [row["duration_min"] for row in cursor.fetchall() if row["duration_min"]]
                
                if durations:
                    percentiles = calculate_percentiles(durations)
                    results.append({
                        "platform": platform,
                        **percentiles
                    })
            
            return {
                "days": days,
                "platforms": results
            }
    finally:
        connection.close()


def analyze_trend(
    days: int = 30,
    granularity: str = "day",
    baseline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    分析构建耗时趋势
    
    Args:
        days: 分析最近多少天的数据
        granularity: 粒度 (day, week)
        baseline_name: 可选，过滤特定平台
        
    Returns:
        趋势分析结果
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if granularity == "week":
                date_format = "%Y-%u"
                date_label = "YEARWEEK(build_end_time)"
            else:
                date_format = "%Y-%m-%d"
                date_label = "DATE(build_end_time)"
            
            sql = f"""
                SELECT 
                    {date_label} as period,
                    COUNT(*) as build_count,
                    AVG(CAST(pipeline_time AS SIGNED)) / 60 as avg_pipeline_min,
                    AVG(CAST(build_time AS SIGNED)) / 60 as avg_build_min
                FROM personal_build
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND build_end_time IS NOT NULL
            """
            params = [days]
            
            if baseline_name:
                sql += " AND baseline_name = %s"
                params.append(baseline_name)
            
            sql += f" GROUP BY {date_label} ORDER BY period"
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            trend_data = []
            prev_avg = None
            for row in results:
                current_avg = float(row["avg_pipeline_min"] or 0)
                change_percent = None
                if prev_avg and prev_avg > 0:
                    change_percent = round((current_avg - prev_avg) / prev_avg * 100, 1)
                
                trend_data.append({
                    "period": str(row["period"]),
                    "build_count": row["build_count"],
                    "avg_pipeline_minutes": round(current_avg, 1),
                    "avg_build_minutes": round(float(row["avg_build_min"] or 0), 1),
                    "change_percent": change_percent
                })
                prev_avg = current_avg
            
            # 判断整体趋势
            if len(trend_data) >= 2:
                first_half = trend_data[:len(trend_data)//2]
                second_half = trend_data[len(trend_data)//2:]
                first_avg = sum(t["avg_pipeline_minutes"] for t in first_half) / len(first_half)
                second_avg = sum(t["avg_pipeline_minutes"] for t in second_half) / len(second_half)
                
                if second_avg > first_avg * 1.1:
                    overall_trend = "worsening"
                elif second_avg < first_avg * 0.9:
                    overall_trend = "improving"
                else:
                    overall_trend = "stable"
            else:
                overall_trend = "insufficient_data"
            
            return {
                "days": days,
                "granularity": granularity,
                "baseline_name": baseline_name,
                "overall_trend": overall_trend,
                "data": trend_data
            }
    finally:
        connection.close()


def detect_anomalies(
    days: int = 7,
    p95_threshold_minutes: float = None
) -> Dict[str, Any]:
    """
    检测异常构建
    
    Args:
        days: 分析最近多少天的数据
        p95_threshold_minutes: P95阈值（分钟），超过此值的构建被标记为异常
        
    Returns:
        异常检测结果
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 先计算P95阈值
            if p95_threshold_minutes is None:
                sql = """
                    SELECT CAST(pipeline_time AS SIGNED) / 60 as duration_min
                    FROM personal_build
                    WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND pipeline_time IS NOT NULL AND pipeline_time != ''
                    ORDER BY CAST(pipeline_time AS SIGNED)
                """
                cursor.execute(sql, [days])
                durations = [row["duration_min"] for row in cursor.fetchall() if row["duration_min"]]
                
                if durations:
                    n = len(durations)
                    p95_threshold_minutes = durations[int(n * 0.95)]
                else:
                    p95_threshold_minutes = 120  # 默认2小时
            
            # 查找超过P95的构建
            sql = """
                SELECT 
                    task_num,
                    baseline_name,
                    android_version,
                    compile_component,
                    CAST(pipeline_time AS SIGNED) / 60 as pipeline_minutes,
                    CAST(build_time AS SIGNED) / 60 as build_minutes,
                    build_end_time,
                    created_by
                FROM personal_build
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND CAST(pipeline_time AS SIGNED) / 60 > %s
                ORDER BY CAST(pipeline_time AS SIGNED) DESC
                LIMIT 20
            """
            cursor.execute(sql, [days, p95_threshold_minutes])
            slow_builds = cursor.fetchall()
            
            # 检测恶化的平台
            sql = """
                SELECT 
                    baseline_name,
                    AVG(CASE WHEN build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY) 
                        THEN CAST(pipeline_time AS SIGNED) / 60 END) as recent_avg,
                    AVG(CASE WHEN build_end_time < DATE_SUB(NOW(), INTERVAL %s DAY) 
                             AND build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                        THEN CAST(pipeline_time AS SIGNED) / 60 END) as prev_avg
                FROM personal_build
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND baseline_name IS NOT NULL AND baseline_name != ''
                GROUP BY baseline_name
                HAVING recent_avg IS NOT NULL AND prev_avg IS NOT NULL
            """
            half_days = days // 2
            cursor.execute(sql, [half_days, half_days, days, days])
            platform_changes = cursor.fetchall()
            
            worsening_platforms = []
            for p in platform_changes:
                recent = float(p["recent_avg"] or 0)
                prev = float(p["prev_avg"] or 0)
                if prev > 0 and recent > prev * 1.2:  # 恶化超过20%
                    worsening_platforms.append({
                        "platform": p["baseline_name"],
                        "recent_avg_minutes": round(recent, 1),
                        "prev_avg_minutes": round(prev, 1),
                        "change_percent": round((recent - prev) / prev * 100, 1)
                    })
            
            anomalies = []
            
            if slow_builds:
                anomalies.append({
                    "type": "slow_builds",
                    "severity": "warning",
                    "message": f"发现 {len(slow_builds)} 个构建超过 P95 阈值（{p95_threshold_minutes:.0f}分钟）",
                    "details": [
                        {
                            "task_num": b["task_num"],
                            "platform": b["baseline_name"],
                            "duration_minutes": round(float(b["pipeline_minutes"] or 0), 1)
                        }
                        for b in slow_builds[:5]  # 只返回前5个
                    ]
                })
            
            if worsening_platforms:
                anomalies.append({
                    "type": "worsening_platforms",
                    "severity": "critical",
                    "message": f"发现 {len(worsening_platforms)} 个平台构建耗时恶化超过20%",
                    "details": worsening_platforms
                })
            
            return {
                "days": days,
                "p95_threshold_minutes": round(p95_threshold_minutes, 1),
                "anomalies": anomalies,
                "slow_builds_count": len(slow_builds),
                "worsening_platforms_count": len(worsening_platforms)
            }
    finally:
        connection.close()


# ============ 问题导向分析函数 ============


def analyze_lagging_platforms(days: int = 7, min_builds: int = 50) -> Dict[str, Any]:
    """
    分析P95落后的平台 - 找出哪些平台低于整体水平
    
    问题导向：不只看指标，而是找出问题所在
    
    Args:
        days: 分析天数
        min_builds: 最小构建数（避免样本太小）
        
    Returns:
        落后平台分析结果，包含问题描述和解决建议
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 计算整体P50和P95
            cursor.execute('''
                SELECT CAST(pipeline_time AS SIGNED)/60 as duration_min
                FROM personal_build 
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND pipeline_time IS NOT NULL AND pipeline_time != ''
                ORDER BY CAST(pipeline_time AS SIGNED)
            ''', [days])
            all_durations = [row["duration_min"] for row in cursor.fetchall() if row["duration_min"]]
            
            if not all_durations:
                return {"error": "No data available"}
            
            n = len(all_durations)
            overall_p50 = all_durations[n // 2]
            overall_p95 = all_durations[int(n * 0.95)]
            
            # 获取各平台数据
            cursor.execute('''
                SELECT baseline_name, COUNT(*) as cnt
                FROM personal_build 
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND baseline_name IS NOT NULL AND baseline_name != ''
                GROUP BY baseline_name
                HAVING cnt >= %s
                ORDER BY cnt DESC
            ''', [days, min_builds])
            platforms = [(row["baseline_name"], row["cnt"]) for row in cursor.fetchall()]
            
            lagging_platforms = []
            healthy_platforms = []
            
            for platform, cnt in platforms:
                cursor.execute('''
                    SELECT CAST(pipeline_time AS SIGNED)/60 as duration_min
                    FROM personal_build 
                    WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND baseline_name = %s
                    AND pipeline_time IS NOT NULL AND pipeline_time != ''
                    ORDER BY CAST(pipeline_time AS SIGNED)
                ''', [days, platform])
                durations = [row["duration_min"] for row in cursor.fetchall() if row["duration_min"]]
                
                if durations:
                    pn = len(durations)
                    p50 = durations[pn // 2]
                    p95 = durations[int(pn * 0.95)]
                    
                    platform_info = {
                        "platform": platform,
                        "display_name": get_platform_display_name(platform),
                        "vendor": get_vendor_name(platform),
                        "build_count": cnt,
                        "p50_minutes": round(p50, 1),
                        "p95_minutes": round(p95, 1),
                    }
                    
                    if p95 > overall_p95:
                        gap_percent = round((p95 - overall_p95) / overall_p95 * 100, 1)
                        platform_info["gap_percent"] = gap_percent
                        platform_info["gap_minutes"] = round(p95 - overall_p95, 1)
                        platform_info["status"] = "lagging"
                        lagging_platforms.append(platform_info)
                    else:
                        platform_info["status"] = "healthy"
                        healthy_platforms.append(platform_info)
            
            # 按差距排序
            lagging_platforms.sort(key=lambda x: x.get("gap_percent", 0), reverse=True)
            
            # 生成问题描述和建议
            problems = []
            suggestions = []
            
            if lagging_platforms:
                worst = lagging_platforms[0]
                problems.append(f"{worst['display_name']} 的P95耗时高于整体水平 {worst['gap_percent']}%，需要重点关注")
                
                # 统计厂商情况
                vendor_lag = {}
                for p in lagging_platforms:
                    v = p["vendor"]
                    if v not in vendor_lag:
                        vendor_lag[v] = 0
                    vendor_lag[v] += 1
                
                for v, count in vendor_lag.items():
                    if count > 2:
                        problems.append(f"{v}平台有 {count} 个型号落后，可能是该厂商的构建流程需要优化")
                
                suggestions.append("排查落后平台的构建日志，分析耗时主要集中在哪个阶段")
                suggestions.append("对比健康平台和落后平台的构建配置差异")
                suggestions.append("考虑为落后平台分配更多构建资源或优化编译参数")
            
            return {
                "days": days,
                "overall_p50_minutes": round(overall_p50, 1),
                "overall_p95_minutes": round(overall_p95, 1),
                "total_platforms": len(platforms),
                "lagging_count": len(lagging_platforms),
                "healthy_count": len(healthy_platforms),
                "lagging_platforms": lagging_platforms[:15],  # 最多返回15个
                "healthy_platforms": healthy_platforms[:5],   # 最多返回5个健康的作为对比
                "problems": problems,
                "suggestions": suggestions
            }
    finally:
        connection.close()


def analyze_component_bottlenecks(days: int = 7) -> Dict[str, Any]:
    """
    分析组件构建瓶颈 - 哪些编译组件最慢
    
    Args:
        days: 分析天数
        
    Returns:
        组件瓶颈分析结果
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT compile_component, COUNT(*) as cnt
                FROM personal_build 
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND compile_component IS NOT NULL AND compile_component != ''
                GROUP BY compile_component
                ORDER BY cnt DESC
                LIMIT 20
            ''', [days])
            components = [(row["compile_component"], row["cnt"]) for row in cursor.fetchall()]
            
            results = []
            for comp, cnt in components:
                cursor.execute('''
                    SELECT CAST(pipeline_time AS SIGNED)/60 as duration_min
                    FROM personal_build 
                    WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND compile_component = %s
                    AND pipeline_time IS NOT NULL AND pipeline_time != ''
                    ORDER BY CAST(pipeline_time AS SIGNED)
                ''', [days, comp])
                durations = [row["duration_min"] for row in cursor.fetchall() if row["duration_min"]]
                
                if durations:
                    n = len(durations)
                    p50 = float(durations[n // 2])
                    p95 = float(durations[int(n * 0.95)])
                    
                    # 分析组件复杂度（包含多少个子组件）
                    sub_components = comp.split(";") if ";" in comp else [comp]
                    
                    results.append({
                        "component": comp,
                        "sub_component_count": len(sub_components),
                        "build_count": cnt,
                        "p50_minutes": round(p50, 1),
                        "p95_minutes": round(p95, 1),
                        "is_complex": len(sub_components) >= 3
                    })
            
            # 按P95排序
            results.sort(key=lambda x: x["p95_minutes"], reverse=True)
            
            # 生成洞察
            insights = []
            if results:
                slowest = results[0]
                insights.append(f"最慢组件: {slowest['component']}，P95耗时 {slowest['p95_minutes']} 分钟")
                
                # 复杂组件分析
                complex_comps = [r for r in results if r["is_complex"]]
                if complex_comps:
                    avg_complex = sum(r["p95_minutes"] for r in complex_comps) / len(complex_comps)
                    simple_comps = [r for r in results if not r["is_complex"]]
                    if simple_comps:
                        avg_simple = sum(r["p95_minutes"] for r in simple_comps) / len(simple_comps)
                        if avg_complex > avg_simple * 1.5:
                            insights.append(f"多组件构建平均耗时 {avg_complex:.0f} 分钟，是单组件的 {avg_complex/avg_simple:.1f} 倍")
            
            return {
                "days": days,
                "total_components": len(results),
                "components": results,
                "insights": insights,
                "suggestions": [
                    "考虑将复杂的多组件构建拆分为独立构建任务",
                    "对P95最高的组件进行编译优化分析",
                    "评估是否可以使用增量编译减少重复工作"
                ]
            }
    finally:
        connection.close()


def analyze_user_builds(days: int = 7, min_builds: int = 10) -> Dict[str, Any]:
    """
    分析人员维度的构建情况 - 从个人角度看优化点
    
    Args:
        days: 分析天数
        min_builds: 最小构建数
        
    Returns:
        人员构建分析结果
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 按人员统计
            cursor.execute('''
                SELECT 
                    created_by,
                    COUNT(*) as cnt, 
                    AVG(CAST(pipeline_time AS SIGNED))/60 as avg_min,
                    SUM(CAST(pipeline_time AS SIGNED))/60 as total_min
                FROM personal_build 
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND created_by IS NOT NULL AND created_by != ''
                GROUP BY created_by
                HAVING cnt >= %s
                ORDER BY avg_min DESC
            ''', [days, min_builds])
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    "user_id": row["created_by"],
                    "build_count": row["cnt"],
                    "avg_minutes": round(float(row["avg_min"] or 0), 1),
                    "total_hours": round(float(row["total_min"] or 0) / 60, 1)
                })
            
            # 统计
            if users:
                avg_all = sum(u["avg_minutes"] for u in users) / len(users)
                slow_users = [u for u in users if u["avg_minutes"] > avg_all * 1.3]  # 慢30%以上
                
                # 按总耗时排序找出构建时间消耗最多的
                users_by_total = sorted(users, key=lambda x: x["total_hours"], reverse=True)
                
                insights = []
                if slow_users:
                    insights.append(f"有 {len(slow_users)} 位用户的平均构建耗时高于整体30%以上")
                
                if users_by_total:
                    top_user = users_by_total[0]
                    insights.append(f"构建时间消耗最多: {top_user['user_id']}，共 {top_user['total_hours']} 小时")
                
                return {
                    "days": days,
                    "total_users": len(users),
                    "avg_build_time_minutes": round(avg_all, 1),
                    "slowest_users": users[:10],  # 平均最慢的10人
                    "most_active_users": users_by_total[:10],  # 构建最多的10人
                    "users_need_attention": len(slow_users),
                    "insights": insights,
                    "suggestions": [
                        "建议构建耗时较高的用户检查提交的代码变更范围是否过大",
                        "考虑是否可以使用更高效的编译组件组合",
                        "评估是否需要为高频构建用户分配优先资源"
                    ]
                }
            
            return {
                "days": days,
                "total_users": 0,
                "insights": ["数据不足，无法进行人员分析"],
                "suggestions": []
            }
    finally:
        connection.close()


def analyze_trend_changes(days: int = 7) -> Dict[str, Any]:
    """
    分析趋势变化 - 哪些平台在恶化，哪些在改善
    
    Args:
        days: 分析天数
        
    Returns:
        趋势变化分析结果
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            half = days // 2
            
            cursor.execute('''
                SELECT 
                    baseline_name,
                    AVG(CASE WHEN build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY) 
                        THEN CAST(pipeline_time AS SIGNED)/60 END) as recent_avg,
                    AVG(CASE WHEN build_end_time < DATE_SUB(NOW(), INTERVAL %s DAY) 
                        THEN CAST(pipeline_time AS SIGNED)/60 END) as prev_avg,
                    COUNT(CASE WHEN build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY) THEN 1 END) as recent_cnt,
                    COUNT(CASE WHEN build_end_time < DATE_SUB(NOW(), INTERVAL %s DAY) THEN 1 END) as prev_cnt
                FROM personal_build 
                WHERE build_end_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND baseline_name IS NOT NULL AND baseline_name != ''
                GROUP BY baseline_name
                HAVING recent_cnt >= 30 AND prev_cnt >= 30
            ''', [half, half, half, half, days])
            
            worsening = []
            improving = []
            stable = []
            
            for row in cursor.fetchall():
                platform = row["baseline_name"]
                recent = float(row["recent_avg"] or 0)
                prev = float(row["prev_avg"] or 0)
                
                if prev > 0:
                    change = (recent - prev) / prev * 100
                    info = {
                        "platform": platform,
                        "display_name": get_platform_display_name(platform),
                        "recent_avg_minutes": round(recent, 1),
                        "prev_avg_minutes": round(prev, 1),
                        "change_percent": round(change, 1),
                        "recent_count": row["recent_cnt"],
                        "prev_count": row["prev_cnt"]
                    }
                    
                    if change > 10:
                        info["status"] = "worsening"
                        worsening.append(info)
                    elif change < -10:
                        info["status"] = "improving"
                        improving.append(info)
                    else:
                        info["status"] = "stable"
                        stable.append(info)
            
            worsening.sort(key=lambda x: x["change_percent"], reverse=True)
            improving.sort(key=lambda x: x["change_percent"])
            
            # 生成洞察
            problems = []
            good_news = []
            
            if worsening:
                worst = worsening[0]
                problems.append(f"⚠️ {worst['display_name']} 耗时恶化最严重，增加了 {worst['change_percent']}%")
            
            if improving:
                best = improving[0]
                good_news.append(f"✅ {best['display_name']} 优化效果最明显，减少了 {abs(best['change_percent'])}%")
            
            return {
                "days": days,
                "comparison_period": f"最近{half}天 vs 之前{half}天",
                "worsening_count": len(worsening),
                "improving_count": len(improving),
                "stable_count": len(stable),
                "worsening_platforms": worsening[:10],
                "improving_platforms": improving[:10],
                "problems": problems,
                "good_news": good_news,
                "suggestions": [
                    "对恶化平台进行根因分析，检查是否有代码变更或配置调整",
                    "学习改善平台的优化经验，推广到其他平台",
                    "设置趋势监控告警，及时发现恶化趋势"
                ] if worsening else ["当前所有平台趋势稳定，继续保持"]
            }
    finally:
        connection.close()


def generate_problem_report(days: int = 7) -> Dict[str, Any]:
    """
    生成问题导向的分析报告 - 重点呈现问题和解决思路
    
    Args:
        days: 分析天数
        
    Returns:
        问题导向的完整分析报告
    """
    try:
        # 收集各维度分析
        lagging = analyze_lagging_platforms(days=days)
        components = analyze_component_bottlenecks(days=days)
        trends = analyze_trend_changes(days=days)
        users = analyze_user_builds(days=days)
        
        # 汇总所有问题
        all_problems = []
        all_suggestions = []
        
        # 从各分析中提取问题
        if lagging.get("problems"):
            all_problems.extend(lagging["problems"])
        if lagging.get("suggestions"):
            all_suggestions.extend(lagging["suggestions"])
            
        if trends.get("problems"):
            all_problems.extend(trends["problems"])
        if trends.get("suggestions"):
            all_suggestions.extend(trends["suggestions"])
            
        if components.get("insights"):
            all_problems.extend([f"📊 {i}" for i in components["insights"]])
        if components.get("suggestions"):
            all_suggestions.extend(components["suggestions"])
            
        if users.get("insights"):
            all_problems.extend([f"👤 {i}" for i in users["insights"]])
        if users.get("suggestions"):
            all_suggestions.extend(users["suggestions"])
        
        # 去重建议
        all_suggestions = list(dict.fromkeys(all_suggestions))
        
        # 计算问题严重程度
        severity = "low"
        if lagging.get("lagging_count", 0) > 5 or trends.get("worsening_count", 0) > 3:
            severity = "high"
        elif lagging.get("lagging_count", 0) > 2 or trends.get("worsening_count", 0) > 1:
            severity = "medium"
        
        return {
            "report_type": "problem_analysis",
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
            "severity": severity,
            "summary": {
                "total_problems": len(all_problems),
                "lagging_platforms": lagging.get("lagging_count", 0),
                "worsening_platforms": trends.get("worsening_count", 0),
                "improving_platforms": trends.get("improving_count", 0),
                "overall_p95_minutes": lagging.get("overall_p95_minutes", 0)
            },
            "problems": all_problems,
            "suggestions": all_suggestions[:10],  # 最多10条建议
            "details": {
                "lagging_analysis": lagging,
                "component_analysis": components,
                "trend_analysis": trends,
                "user_analysis": users
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "report_type": "problem_analysis",
            "generated_at": datetime.now().isoformat()
        }


def generate_briefing(days: int = 7) -> Dict[str, Any]:
    """
    生成构建效率简报 - 用于信息流推送
    
    简报设计原则（参考 CLAUDE.md 简报生成指南）:
    1. 标题动词开头，说清核心发现
    2. 摘要包含三要素：问题 + 影响 + 行动
    3. 只在真正有价值时才推送
    
    Args:
        days: 分析天数
        
    Returns:
        简报数据，包含 should_push 字段判断是否值得推送
    """
    try:
        # 获取问题分析数据
        data = generate_problem_report(days=days)
        
        if data.get("error"):
            return data
        
        severity = data.get("severity", "low")
        summary = data.get("summary", {})
        problems = data.get("problems", [])
        suggestions = data.get("suggestions", [])
        details = data.get("details", {})
        
        # 判断是否值得推送
        should_push = False
        priority = "P2"  # 默认普通
        
        lagging_count = summary.get("lagging_platforms", 0)
        worsening_count = summary.get("worsening_platforms", 0)
        
        if severity == "high":
            should_push = True
            priority = "P1"  # 重要
        elif severity == "medium":
            should_push = True
            priority = "P2"  # 普通
        elif worsening_count > 0:
            should_push = True
            priority = "P2"
        # 如果一切正常，不推送
        
        # 生成标题（动词开头，说清核心发现）
        if severity == "high":
            if lagging_count > 5:
                title = f"门禁构建效率告警：{lagging_count}个平台P95落后，需重点关注"
            else:
                title = f"构建效率异常：发现{len(problems)}个问题需要处理"
        elif worsening_count > 0:
            # 找出恶化最严重的平台
            worsening = details.get("trend_analysis", {}).get("worsening_platforms", [])
            if worsening:
                worst = worsening[0]
                title = f"{worst.get('display_name', worst.get('platform', ''))}构建耗时恶化{worst.get('change_percent', 0)}%"
            else:
                title = f"发现{worsening_count}个平台构建趋势恶化"
        elif lagging_count > 0:
            # 找出落后最严重的平台
            lagging = details.get("lagging_analysis", {}).get("lagging_platforms", [])
            if lagging:
                worst = lagging[0]
                title = f"{worst.get('display_name', worst.get('platform', ''))} P95超出整体{worst.get('gap_percent', 0)}%"
            else:
                title = f"{lagging_count}个平台P95落后于整体水平"
        else:
            title = "构建效率保持稳定，无显著问题"
            should_push = False  # 正常情况不推送
        
        # 生成摘要（问题 + 影响 + 行动）
        summary_lines = []
        
        # 问题
        if problems:
            summary_lines.append(problems[0])  # 最重要的问题
        
        # 影响
        overall_p95 = summary.get("overall_p95_minutes", 0)
        if lagging_count > 0:
            summary_lines.append(f"整体P95为{overall_p95}分钟，{lagging_count}个平台高于此基准。")
        
        # 行动
        if suggestions:
            summary_lines.append(f"建议：{suggestions[0]}")
        
        summary_text = "\n".join(summary_lines)
        
        # 核心指标
        metrics = {
            "lagging_platforms": lagging_count,
            "worsening_platforms": worsening_count,
            "improving_platforms": summary.get("improving_platforms", 0),
            "overall_p95_minutes": overall_p95,
            "total_problems": len(problems)
        }
        
        # 关键问题（最多3个）
        key_problems = problems[:3] if problems else []
        
        # 建议行动（最多2个）
        key_suggestions = suggestions[:2] if suggestions else []
        
        return {
            "briefing_type": "build_efficiency",
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
            "should_push": should_push,
            "priority": priority,
            "severity": severity,
            "title": title,
            "summary": summary_text,
            "metrics": metrics,
            "key_problems": key_problems,
            "key_suggestions": key_suggestions,
            # 如果需要详细数据，可以从这里获取
            "details_available": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "briefing_type": "build_efficiency",
            "should_push": False
        }


def generate_summary_report(days: int = 7) -> Dict[str, Any]:
    """
    生成构建分析摘要报告
    
    Args:
        days: 分析最近多少天的数据
        
    Returns:
        完整的分析报告
    """
    try:
        # 获取基础数据
        builds = fetch_build_data(days=days, limit=50000)
        
        # 基础指标分析
        basic_metrics = analyze_build_metrics(builds)
        
        # 按平台分析分位数
        platform_percentiles = analyze_percentile_by_platform(days=days, top_n=10)
        
        # 趋势分析
        trend = analyze_trend(days=days, granularity="day")
        
        # 异常检测
        anomalies = detect_anomalies(days=days)
        
        # 按平台分组
        by_platform = analyze_by_dimension(days=days, dimension="baseline_name", top_n=10)
        
        # 按Android版本分组
        by_android = analyze_by_dimension(days=days, dimension="android_version", top_n=5)
        
        # 按编译组件分组
        by_component = analyze_by_dimension(days=days, dimension="compile_component", top_n=10)
        
        # 生成文本摘要
        summary_text = generate_text_summary(
            basic_metrics, platform_percentiles, trend, anomalies
        )
        
        return {
            "report_type": "build_analysis",
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days,
            "summary": summary_text,
            "metrics": basic_metrics,
            "platform_percentiles": platform_percentiles,
            "trend": trend,
            "anomalies": anomalies,
            "breakdown": {
                "by_platform": by_platform,
                "by_android_version": by_android,
                "by_compile_component": by_component
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "report_type": "build_analysis",
            "generated_at": datetime.now().isoformat()
        }


def generate_text_summary(
    metrics: Dict, 
    platform_percentiles: Dict, 
    trend: Dict, 
    anomalies: Dict
) -> str:
    """
    生成文本格式的分析摘要
    """
    lines = []
    lines.append("## 门禁构建分析报告\n")
    
    # 基础指标
    if metrics.get("total_builds"):
        total = metrics["total_builds"]
        duration = metrics.get("total_duration_minutes", {})
        lines.append(f"### 📊 基础指标")
        lines.append(f"- 分析构建数: **{total:,}** 次")
        lines.append(f"- 平均耗时: **{duration.get('avg', 0):.1f}** 分钟")
        lines.append(f"- P50耗时: **{duration.get('p50', 0):.1f}** 分钟")
        lines.append(f"- P95耗时: **{duration.get('p95', 0):.1f}** 分钟")
        lines.append(f"- P99耗时: **{duration.get('p99', 0):.1f}** 分钟")
        lines.append("")
    
    # 趋势
    if trend.get("overall_trend"):
        trend_map = {
            "worsening": "📈 恶化中",
            "improving": "📉 改善中", 
            "stable": "➡️ 保持稳定",
            "insufficient_data": "⚠️ 数据不足"
        }
        lines.append(f"### 📈 趋势")
        lines.append(f"- 整体趋势: **{trend_map.get(trend['overall_trend'], '未知')}**")
        lines.append("")
    
    # 异常
    if anomalies.get("anomalies"):
        lines.append(f"### ⚠️ 异常告警")
        for a in anomalies["anomalies"]:
            severity_icon = "🔴" if a["severity"] == "critical" else "🟡"
            lines.append(f"- {severity_icon} {a['message']}")
        lines.append("")
    
    # 最慢平台
    if platform_percentiles.get("platforms"):
        lines.append(f"### 🐢 构建最慢的平台 (按P95)")
        for i, p in enumerate(sorted(
            platform_percentiles["platforms"], 
            key=lambda x: x.get("p95", 0), 
            reverse=True
        )[:5]):
            lines.append(f"{i+1}. **{p['platform']}**: P50={p.get('p50', 0):.0f}分钟, P95={p.get('p95', 0):.0f}分钟")
        lines.append("")
    
    return "\n".join(lines)


def run_analysis(
    action: str = "problems",
    days: int = 7,
    **kwargs
) -> Dict[str, Any]:
    """
    执行构建分析
    
    Args:
        action: 分析类型
            【问题导向分析 - 推荐使用】
            - problems: 问题导向分析报告（默认，推荐）
            - briefing: 生成简报（用于信息流推送）
            - lagging: P95落后平台分析
            - components: 组件瓶颈分析
            - trends: 趋势变化分析（恶化/改善）
            - users: 人员维度分析
            
            【基础指标分析】
            - summary: 生成完整摘要报告
            - metrics: 仅返回基础指标
            - trend: 趋势分析（按天/周）
            - anomalies: 异常检测
            - by_platform: 按平台分析
            - by_android: 按Android版本分析
            - percentiles: 分位数分析
            
        days: 分析天数
        **kwargs: 其他参数
        
    Returns:
        分析结果
    """
    try:
        # 问题导向分析（推荐）
        if action == "problems":
            return generate_problem_report(days=days)
        elif action == "briefing":
            return generate_briefing(days=days)
        elif action == "lagging":
            return analyze_lagging_platforms(days=days, **kwargs)
        elif action == "components":
            return analyze_component_bottlenecks(days=days)
        elif action == "trends":
            return analyze_trend_changes(days=days)
        elif action == "users":
            return analyze_user_builds(days=days, **kwargs)
        
        # 基础指标分析
        elif action == "summary":
            return generate_summary_report(days=days)
        elif action == "metrics":
            builds = fetch_build_data(days=days, limit=50000, **kwargs)
            return analyze_build_metrics(builds)
        elif action == "trend":
            return analyze_trend(days=days, **kwargs)
        elif action == "anomalies":
            return detect_anomalies(days=days, **kwargs)
        elif action == "by_platform":
            return analyze_by_dimension(days=days, dimension="baseline_name", **kwargs)
        elif action == "by_android":
            return analyze_by_dimension(days=days, dimension="android_version", **kwargs)
        elif action == "percentiles":
            return analyze_percentile_by_platform(days=days, **kwargs)
        else:
            return {"error": f"Unknown action: {action}. Available: problems, lagging, components, trends, users, summary, metrics, trend, anomalies, by_platform, by_android, percentiles"}
    except Exception as e:
        return {
            "error": str(e),
            "action": action,
            "data_source": "mysql"
        }


def main():
    """主函数：从stdin读取参数，输出分析结果"""
    try:
        # 从stdin读取JSON参数
        input_data = sys.stdin.read().strip()
        
        if input_data:
            params = json.loads(input_data)
            action = params.pop("action", "summary")
            days = params.pop("days", 7)
            result = run_analysis(action=action, days=days, **params)
        else:
            # 默认生成摘要报告
            result = run_analysis(action="summary", days=7)
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
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

