#!/usr/bin/env python3
"""
上传 APK 到 Supabase Storage 并更新版本信息

使用方式：
    python scripts/upload_apk.py <apk_file_path>

环境变量：
    SUPABASE_URL: Supabase 项目 URL
    SUPABASE_SERVICE_KEY: Supabase Service Role Key
    VERSION_CODE: 版本号（可选，默认从 build.gradle 读取）
    VERSION_NAME: 版本名（可选，默认从 build.gradle 读取）
    RELEASE_NOTES: 更新说明（可选）
"""

import os
import sys
import re
import hashlib
from pathlib import Path

def get_version_from_gradle(gradle_file):
    """从 build.gradle 读取版本信息"""
    with open(gradle_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 versionCode
    version_code_match = re.search(r'versionCode\s*=\s*(\d+)', content)
    version_code = int(version_code_match.group(1)) if version_code_match else 1

    # 提取 versionName
    version_name_match = re.search(r'versionName\s*=\s*["\']([^"\']+)["\']', content)
    version_name = version_name_match.group(1) if version_name_match else '0.1.0'

    return version_code, version_name


def calculate_md5(file_path):
    """计算文件 MD5"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def upload_to_supabase(apk_path):
    """上传 APK 到 Supabase Storage"""
    try:
        from supabase import create_client
    except ImportError:
        print("错误: 请安装 supabase 库")
        print("运行: pip install supabase")
        sys.exit(1)

    # 读取环境变量
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not supabase_url or not supabase_key:
        print("错误: 缺少 SUPABASE_URL 或 SUPABASE_SERVICE_KEY 环境变量")
        sys.exit(1)

    # 读取版本信息
    gradle_file = Path(__file__).parent.parent / 'ai_agent_app/android/app/build.gradle'
    version_code = int(os.getenv('VERSION_CODE', 0))
    version_name = os.getenv('VERSION_NAME', '')

    if version_code == 0 or not version_name:
        print(f"从 {gradle_file} 读取版本信息...")
        version_code, version_name = get_version_from_gradle(gradle_file)

    print(f"版本号: {version_code}")
    print(f"版本名: {version_name}")

    # 计算文件信息
    apk_file = Path(apk_path)
    file_size = apk_file.stat().st_size
    file_md5 = calculate_md5(apk_path)

    print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
    print(f"MD5: {file_md5}")

    # 创建 Supabase 客户端
    supabase = create_client(supabase_url, supabase_key)

    # 上传到 Storage
    storage_path = f"apk-releases/app-release-v{version_code}.apk"
    print(f"\n正在上传到 Storage: {storage_path}")

    with open(apk_path, 'rb') as f:
        supabase.storage.from_('apk-releases').upload(
            storage_path,
            f.read(),
            file_options={"content-type": "application/vnd.android.package-archive"}
        )

    # 获取公开 URL
    public_url = supabase.storage.from_('apk-releases').get_public_url(storage_path)
    print(f"上传成功: {public_url}")

    # 更新数据库
    release_notes = os.getenv('RELEASE_NOTES', f'# 版本 {version_name}\n\n自动构建')

    print(f"\n正在更新版本信息到数据库...")

    # 先停用旧版本
    supabase.table('app_versions').update({'is_active': False}).execute()

    # 插入新版本
    result = supabase.table('app_versions').insert({
        'version_code': version_code,
        'version_name': version_name,
        'apk_url': public_url,
        'apk_size': file_size,
        'apk_md5': file_md5,
        'release_notes': release_notes,
        'force_update': False,
        'is_active': True,
        'published_at': 'now()'
    }).execute()

    print(f"数据库更新成功")
    print(f"\n✅ 版本 {version_name} (code: {version_code}) 发布完成！")

    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python upload_apk.py <apk_file_path>")
        sys.exit(1)

    apk_path = sys.argv[1]

    if not os.path.exists(apk_path):
        print(f"错误: 文件不存在: {apk_path}")
        sys.exit(1)

    try:
        upload_to_supabase(apk_path)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
