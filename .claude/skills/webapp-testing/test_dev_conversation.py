#!/usr/bin/env python3
"""
测试研发效能分析官对话和简报上下文
"""

import time
from playwright.sync_api import sync_playwright

TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
BASE_URL = "http://localhost:5000"

def test_dev_efficiency_conversation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("=" * 70)
        print("测试研发效能分析官对话")
        print("=" * 70)

        # 1. 登录
        print("\n[1] 登录...")
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(6)

        page.mouse.click(640, 400)
        time.sleep(0.5)
        page.keyboard.press("Tab")
        time.sleep(0.3)
        page.keyboard.type(TEST_EMAIL, delay=30)
        page.keyboard.press("Tab")
        time.sleep(0.3)
        page.keyboard.type(TEST_PASSWORD, delay=30)
        page.keyboard.press("Tab")
        time.sleep(0.3)
        page.keyboard.press("Enter")
        time.sleep(10)

        if "/feed" not in page.url:
            print("    登录失败，重试...")
            page.reload()
            time.sleep(5)
            page.mouse.click(640, 400)
            time.sleep(0.5)
            page.keyboard.press("Tab")
            time.sleep(0.3)
            page.keyboard.type(TEST_EMAIL, delay=30)
            page.keyboard.press("Tab")
            time.sleep(0.3)
            page.keyboard.type(TEST_PASSWORD, delay=30)
            page.keyboard.press("Tab")
            time.sleep(0.3)
            page.keyboard.press("Enter")
            time.sleep(10)

        print(f"    ✅ 登录成功: {page.url}")

        # 2. 进入消息页面
        print("\n[2] 进入消息页面...")
        page.mouse.click(797, 760)
        time.sleep(3)
        page.screenshot(path="/tmp/dev_01_messages.png")
        print("    截图: /tmp/dev_01_messages.png")

        # 3. 点击研发效能分析官（第二个对话）
        print("\n[3] 进入研发效能分析官对话...")
        page.mouse.click(640, 225)  # 第二个对话项
        time.sleep(4)
        page.screenshot(path="/tmp/dev_02_conversation.png")
        print("    截图: /tmp/dev_02_conversation.png")
        print(f"    URL: {page.url}")

        # 4. 滚动查看对话历史和简报卡片
        print("\n[4] 查看对话内容...")

        # 先滚动到顶部
        for _ in range(5):
            page.mouse.wheel(0, -500)
            time.sleep(0.5)

        time.sleep(1)
        page.screenshot(path="/tmp/dev_03_top.png")
        print("    截图: /tmp/dev_03_top.png")

        # 逐步向下滚动
        for i in range(6):
            page.screenshot(path=f"/tmp/dev_04_scroll_{i}.png")
            print(f"    截图: /tmp/dev_04_scroll_{i}.png")
            page.mouse.wheel(0, 300)
            time.sleep(1)

        # 5. 测试发送消息
        print("\n[5] 测试消息输入...")
        # 点击输入框
        page.mouse.click(640, 705)
        time.sleep(0.5)
        page.keyboard.type("你好", delay=50)
        time.sleep(1)
        page.screenshot(path="/tmp/dev_05_input.png")
        print("    截图: /tmp/dev_05_input.png")

        browser.close()

        print("\n" + "=" * 70)
        print("研发效能分析官对话测试完成")
        print("=" * 70)

if __name__ == "__main__":
    test_dev_efficiency_conversation()
