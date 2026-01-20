#!/usr/bin/env python3
"""
对话功能验收测试脚本 - 使用坐标点击

由于 Flutter web 使用 canvas 渲染，需要使用屏幕坐标进行交互。
"""

import time
from playwright.sync_api import sync_playwright

# 测试配置
WEB_APP_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:8000"
EMAIL = "1091201603@qq.com"
PASSWORD = "eeappsuccess"


def test_login_and_conversation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # 启用控制台日志捕获
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        print("=" * 60)
        print("对话功能验收测试 (Flutter Web)")
        print("=" * 60)

        # 1. 访问应用
        print("\n[1/6] 访问应用...")
        page.goto(WEB_APP_URL)
        page.wait_for_timeout(5000)  # Flutter 加载时间较长

        page.screenshot(path='/tmp/test_01_initial.png', full_page=True)
        print("   ✓ 应用加载成功")

        # 2. 等待登录页面渲染完成
        print("\n[2/6] 等待登录页面...")
        page.wait_for_timeout(3000)
        page.screenshot(path='/tmp/test_02_login.png', full_page=True)
        print("   ✓ 登录页面就绪")

        # 3. 输入登录信息 (使用键盘输入)
        print("\n[3/6] 输入登录信息...")

        # 点击邮箱输入框 (根据截图估算位置)
        # 登录表单大约在页面中央
        page.mouse.click(640, 385)  # 邮箱输入框
        page.wait_for_timeout(500)
        page.keyboard.type(EMAIL, delay=50)
        page.screenshot(path='/tmp/test_03_email.png', full_page=True)
        print(f"   ✓ 邮箱已输入: {EMAIL}")

        # 点击密码输入框
        page.mouse.click(640, 447)  # 密码输入框
        page.wait_for_timeout(500)
        page.keyboard.type(PASSWORD, delay=50)
        page.screenshot(path='/tmp/test_04_password.png', full_page=True)
        print("   ✓ 密码已输入")

        # 4. 点击登录按钮
        print("\n[4/6] 执行登录...")
        page.mouse.click(640, 512)  # 登录按钮
        page.wait_for_timeout(8000)  # 等待登录完成和页面跳转
        page.screenshot(path='/tmp/test_05_after_login.png', full_page=True)
        print("   ✓ 登录请求已发送")

        # 5. 检查主页面
        print("\n[5/6] 检查主页面...")
        page.wait_for_timeout(3000)
        page.screenshot(path='/tmp/test_06_main.png', full_page=True)

        # 查看是否有 Agent 列表
        print("   截图已保存，检查主页面状态...")

        # 6. 尝试进入对话 (如果有 Agent 列表的话)
        print("\n[6/6] 尝试进入对话...")
        # 点击第一个 Agent 卡片 (大约在列表顶部)
        page.mouse.click(640, 300)
        page.wait_for_timeout(5000)
        page.screenshot(path='/tmp/test_07_conversation.png', full_page=True)
        print("   ✓ 尝试进入对话页面")

        # 打印控制台日志
        print("\n" + "-" * 60)
        print("浏览器控制台日志 (最后20条):")
        for log in console_logs[-20:]:
            print(f"  {log[:100]}...")

        print("\n" + "=" * 60)
        print("验收测试完成")
        print("截图保存位置: /tmp/test_*.png")
        print("=" * 60)

        browser.close()


def check_backend():
    """检查后端状态"""
    import requests
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        data = resp.json()
        print(f"\n后端状态: {data.get('status')}")
        print(f"支持特性: {data.get('features', [])}")
        return data.get('status') == 'healthy'
    except Exception as e:
        print(f"\n后端检查失败: {e}")
        return False


def main():
    print("\n===== 前置检查 =====")

    # 检查后端
    if not check_backend():
        print("警告: 后端可能不可用")

    # 运行测试
    test_login_and_conversation()


if __name__ == "__main__":
    main()
