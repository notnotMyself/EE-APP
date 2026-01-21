#!/usr/bin/env python3
"""
测试简报详情页 - 精确点击版本
"""

import time
from playwright.sync_api import sync_playwright

TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
BASE_URL = "http://localhost:5000"

def test_briefing_detail():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("=" * 70)
        print("测试简报详情页 - 精确点击")
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

        if "/login" in page.url:
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

        print(f"    URL: {page.url}")
        if "/feed" in page.url:
            print("    ✅ 登录成功")
        else:
            print("    ❌ 登录失败")
            browser.close()
            return

        # 2. 等待并截图主页
        time.sleep(3)
        page.screenshot(path="/tmp/click_01_main.png")

        # 3. 尝试多个点击位置找到卡片
        print("\n[2] 尝试点击简报卡片...")

        # 根据截图分析，卡片大约在以下位置:
        # 卡片起始y约130，高度约220
        # 卡片x从约20开始，宽度约600

        click_positions = [
            (350, 200, "卡片顶部"),
            (350, 280, "卡片中部"),
            (500, 250, "卡片右侧"),
            (200, 250, "卡片左侧"),
        ]

        for x, y, desc in click_positions:
            print(f"    尝试点击 ({x}, {y}) - {desc}")
            page.mouse.click(x, y)
            time.sleep(3)

            current_url = page.url
            page.screenshot(path=f"/tmp/click_02_{desc}.png")

            if "/feed" not in current_url or "briefing" in current_url or "detail" in current_url:
                print(f"    ✅ 导航成功! URL: {current_url}")
                break
            else:
                print(f"    仍在主页")
                # 如果打开了什么弹窗，按Escape关闭
                page.keyboard.press("Escape")
                time.sleep(1)

        # 4. 查看当前页面状态
        print("\n[3] 当前页面状态...")
        time.sleep(2)
        page.screenshot(path="/tmp/click_03_current.png")
        print(f"    URL: {page.url}")

        # 5. 尝试通过消息页面进入对话
        print("\n[4] 通过消息页面测试对话...")
        page.mouse.click(797, 760)  # 点击消息导航
        time.sleep(3)
        page.screenshot(path="/tmp/click_04_messages.png")

        # 点击第一个对话
        page.mouse.click(640, 120)
        time.sleep(3)
        page.screenshot(path="/tmp/click_05_conversation.png")
        print(f"    对话页URL: {page.url}")

        # 6. 在对话中查看简报上下文
        print("\n[5] 查看对话内容...")
        for i in range(3):
            page.screenshot(path=f"/tmp/click_06_chat_{i}.png")
            page.mouse.wheel(0, 200)
            time.sleep(1)

        browser.close()

        print("\n" + "=" * 70)
        print("测试完成 - 请查看截图验证功能")
        print("=" * 70)

if __name__ == "__main__":
    test_briefing_detail()
