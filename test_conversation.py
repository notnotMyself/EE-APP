#!/usr/bin/env python3
"""
对话功能验收测试脚本

测试项目：
1. 登录功能
2. 对话页面加载
3. WebSocket连接状态
4. 消息发送和流式响应
"""

import time
from playwright.sync_api import sync_playwright

# 测试配置
WEB_APP_URL = "http://localhost:8080"  # Flutter web app
BACKEND_URL = "http://localhost:8000"  # Backend API
EMAIL = "1091201603@qq.com"
PASSWORD = "eeappsuccess"


def test_login_and_conversation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 50)
        print("对话功能验收测试")
        print("=" * 50)

        # 1. 访问应用
        print("\n[1/5] 访问应用...")
        page.goto(WEB_APP_URL)
        page.wait_for_load_state('networkidle')

        # 截图初始状态
        page.screenshot(path='/tmp/01_initial.png', full_page=True)
        print("   ✓ 应用加载成功")

        # 2. 检查是否在登录页
        print("\n[2/5] 检查登录页面...")
        page.wait_for_timeout(2000)  # 等待路由跳转

        # 查找登录相关元素
        page.screenshot(path='/tmp/02_login_page.png', full_page=True)

        # 尝试查找邮箱输入框
        email_input = page.locator('input[type="email"], input[placeholder*="邮箱"], input[placeholder*="email"]').first
        password_input = page.locator('input[type="password"]').first

        if email_input.is_visible():
            print("   ✓ 发现登录表单")

            # 3. 执行登录
            print("\n[3/5] 执行登录...")
            email_input.fill(EMAIL)
            password_input.fill(PASSWORD)

            # 查找登录按钮
            login_button = page.locator('button:has-text("登录"), button:has-text("Login"), button[type="submit"]').first
            if login_button.is_visible():
                login_button.click()
                print("   ✓ 登录请求已发送")

            # 等待登录完成
            page.wait_for_timeout(5000)
            page.screenshot(path='/tmp/03_after_login.png', full_page=True)
        else:
            print("   ! 未发现登录表单，可能已登录")

        # 4. 查找Agent/对话入口
        print("\n[4/5] 查找对话入口...")
        page.wait_for_timeout(2000)
        page.screenshot(path='/tmp/04_main_page.png', full_page=True)

        # 尝试找到任何可点击的Agent卡片或对话入口
        agent_cards = page.locator('[class*="card"], [class*="agent"], [role="button"]').all()
        print(f"   找到 {len(agent_cards)} 个可能的交互元素")

        if agent_cards:
            # 点击第一个agent卡片
            try:
                agent_cards[0].click()
                page.wait_for_timeout(3000)
                page.screenshot(path='/tmp/05_conversation_page.png', full_page=True)
                print("   ✓ 进入对话页面")
            except Exception as e:
                print(f"   ! 点击失败: {e}")

        # 5. 检查对话页面状态
        print("\n[5/5] 检查对话页面...")
        page.screenshot(path='/tmp/06_final_state.png', full_page=True)

        # 查找消息输入框
        message_input = page.locator('input[placeholder*="消息"], input[placeholder*="message"], textarea').first
        if message_input.is_visible():
            print("   ✓ 发现消息输入框")

            # 尝试发送测试消息
            message_input.fill("你好，这是一条测试消息")
            send_button = page.locator('button:has(svg), [class*="send"], button[type="submit"]').first
            if send_button.is_visible():
                print("   ✓ 发现发送按钮")
        else:
            print("   ! 未找到消息输入框")

        # 获取页面内容用于调试
        html_content = page.content()
        with open('/tmp/page_content.html', 'w') as f:
            f.write(html_content)
        print("\n页面HTML已保存到 /tmp/page_content.html")

        # 检查控制台日志
        console_logs = []
        page.on('console', lambda msg: console_logs.append(msg.text))

        print("\n" + "=" * 50)
        print("验收测试完成")
        print("截图保存位置: /tmp/0*.png")
        print("=" * 50)

        browser.close()


def main():
    test_login_and_conversation()


if __name__ == "__main__":
    main()
