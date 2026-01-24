#!/usr/bin/env python3
"""
插入测试版本数据到 Supabase

用法:
    export SUPABASE_SERVICE_KEY="your_key_here"
    python3 scripts/insert_test_version.py
"""
import os
import sys
from pathlib import Path

# 添加父目录到 path 以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client
except ImportError:
    print("错误: 请先安装 supabase 库")
    print("运行: pip install supabase")
    sys.exit(1)

# 配置
SUPABASE_URL = "https://dwesyojvzbltqtgtctpt.supabase.co"
service_key = os.getenv('SUPABASE_SERVICE_KEY')

if not service_key:
    print("错误: 缺少 SUPABASE_SERVICE_KEY 环境变量")
    print("\n获取方式:")
    print("1. 访问 https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt")
    print("2. 进入 Settings → API")
    print("3. 复制 service_role key (⚠️  不是 anon key)")
    print("\n使用方式:")
    print("export SUPABASE_SERVICE_KEY='your_key_here'")
    print("python3 scripts/insert_test_version.py")
    sys.exit(1)

# 创建客户端
print("🔌 连接到 Supabase...")
supabase = create_client(SUPABASE_URL, service_key)

# 测试版本数据
test_version = {
    'version_code': 2,
    'version_name': '0.1.1',
    'apk_url': 'https://dwesyojvzbltqtgtctpt.supabase.co/storage/v1/object/public/apk-releases/app-release-v2.apk',
    'apk_size': 50000000,  # 50MB
    'apk_md5': 'test_md5_hash',
    'release_notes': '''# 版本 0.1.1

## 新功能
- ✨ 应用内更新功能
- 📱 支持多下载源
- 🔄 断点续传支持

## 优化
- 🚀 提升应用性能
- 💾 减小安装包体积

## 修复
- 🐛 修复已知问题
''',
    'force_update': False,
    'is_active': True,
    'min_support_version': 1
}

try:
    # 停用旧版本
    print("📝 停用旧版本...")
    supabase.table('app_versions').update({'is_active': False}).neq('version_code', 0).execute()

    # 插入新版本
    print(f"📦 插入测试版本 v{test_version['version_name']} (code: {test_version['version_code']})...")
    result = supabase.table('app_versions').insert(test_version).execute()

    if result.data:
        print(f"\n✅ 测试版本插入成功!")
        print(f"   版本: {test_version['version_name']} ({test_version['version_code']})")
        print(f"   ID: {result.data[0]['id']}")
        print(f"   下载地址: {test_version['apk_url']}")
        print(f"\n下一步:")
        print(f"1. 确保 APK 已上传到 Supabase Storage")
        print(f"2. 测试 API: curl 'http://localhost:8000/app/version/latest?current_version=1'")
        print(f"3. 在手机上测试更新流程")
    else:
        print("❌ 插入失败: 无返回数据")
        sys.exit(1)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
