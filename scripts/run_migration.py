#!/usr/bin/env python3
"""
执行数据库迁移脚本
"""
import os
import sys

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from supabase import create_client

# Supabase 配置
SUPABASE_URL = "https://dwesyojvzbltqtgtctpt.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjkzMDkxNCwiZXhwIjoyMDUyNTA2OTE0fQ.f4uXVJEyN9U-xY4r1TjQGbV-GFpQP7Vr5OBMmY5wL1Q"

def run_migration():
    """执行迁移"""
    # 读取 SQL 文件
    sql_file = "supabase/migrations/20260124000000_create_app_versions.sql"
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    # 创建 Supabase 客户端
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # 执行 SQL（需要使用 PostgREST 或直接 SQL）
    # 由于 Supabase Python SDK 不直接支持执行原始 SQL
    # 我们需要拆分 SQL 语句
    print("正在执行迁移...")

    # 简单方法：使用 supabase REST API
    import requests

    # 使用 PostgREST 的 rpc 功能
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }

    # 直接执行 SQL 需要使用数据库连接，这里先手动执行
    print(f"请手动执行 SQL 文件：{sql_file}")
    print("\n或者在 Supabase Dashboard 的 SQL Editor 中执行")
    print(f"\nSQL 内容：\n{sql}")

if __name__ == "__main__":
    run_migration()
