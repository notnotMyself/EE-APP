#!/usr/bin/env python3
"""
初始用户导入脚本

功能：使用Supabase Admin Client创建7个初始用户
用户：80203750, 80031480, 80046887, 80268204, 80318879, 80417875, S9057330
密码：统一为 123456
邮箱：工号@oppo.com

使用方法：
1. 确保已设置环境变量 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY
2. 安装依赖: pip install supabase
3. 运行脚本: python scripts/init_users.py
"""

import os
import sys
from supabase import create_client, Client

# 初始用户列表（工号）
INITIAL_USERS = [
    '80203750',
    '80031480',
    '80046887',
    '80268204',
    '80318879',
    '80417875',
    'S9057330'
]

# 统一密码
DEFAULT_PASSWORD = '123456'

# 邮箱域名
EMAIL_DOMAIN = 'oppo.com'


def get_supabase_admin_client() -> Client:
    """获取Supabase Admin Client"""
    supabase_url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not service_role_key:
        print("错误: 请设置环境变量 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")
        print("示例:")
        print("  export SUPABASE_URL='https://xxx.supabase.co'")
        print("  export SUPABASE_SERVICE_ROLE_KEY='your-service-role-key'")
        sys.exit(1)

    return create_client(supabase_url, service_role_key)


def create_user(supabase: Client, user_id: str) -> bool:
    """创建单个用户"""
    email = f"{user_id}@{EMAIL_DOMAIN}"

    try:
        print(f"正在创建用户: {email} ...")

        # 使用Admin API创建用户
        response = supabase.auth.admin.create_user({
            'email': email,
            'password': DEFAULT_PASSWORD,
            'email_confirm': True,  # 跳过邮箱验证
            'user_metadata': {
                'username': user_id,
                'employee_id': user_id  # 保存工号
            }
        })

        if response.user:
            print(f"✓ 用户创建成功: {email} (ID: {response.user.id})")
            return True
        else:
            print(f"✗ 用户创建失败: {email}")
            return False

    except Exception as e:
        error_message = str(e)

        # 检查是否是用户已存在的错误
        if 'already registered' in error_message.lower() or 'duplicate' in error_message.lower():
            print(f"⚠ 用户已存在: {email}")
            return True  # 视为成功
        else:
            print(f"✗ 用户创建失败: {email}")
            print(f"  错误详情: {error_message}")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("初始用户导入脚本")
    print("=" * 60)
    print(f"将创建 {len(INITIAL_USERS)} 个用户")
    print(f"邮箱格式: 工号@{EMAIL_DOMAIN}")
    print(f"统一密码: {DEFAULT_PASSWORD}")
    print("=" * 60)
    print()

    # 确认操作
    confirm = input("确认继续？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        sys.exit(0)

    print()

    # 获取Supabase Admin Client
    supabase = get_supabase_admin_client()

    # 创建用户
    success_count = 0
    failed_count = 0

    for user_id in INITIAL_USERS:
        if create_user(supabase, user_id):
            success_count += 1
        else:
            failed_count += 1
        print()

    # 总结
    print("=" * 60)
    print("导入完成")
    print("=" * 60)
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    print(f"总计: {len(INITIAL_USERS)} 个")
    print()

    if success_count == len(INITIAL_USERS):
        print("✓ 所有用户导入成功！")
        print()
        print("用户可以使用以下凭证登录：")
        for user_id in INITIAL_USERS:
            print(f"  - 邮箱: {user_id}@{EMAIL_DOMAIN}, 密码: {DEFAULT_PASSWORD}")
    elif failed_count > 0:
        print("⚠ 部分用户导入失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
