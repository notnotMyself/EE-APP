#!/usr/bin/env python3
"""
测试简报详情页和A2UI组件渲染 - 改进版
"""

import time
from playwright.sync_api import sync_playwright

TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
BASE_URL = "http://localhost:5000"

def test_briefing_detail():
    """测试简报详情页"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("=" * 70)
        print("测试简报详情页和A2UI组件")
        print("=" * 70)

        # 1. 登录 - 增加等待时间
        print("\n[1] 登录...")
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(8)  # 增加Flutter初始化等待

        # 先点击页面激活
        page.mouse.click(640, 400)
        time.sleep(1)

        # Tab导航并输入
        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.type(TEST_EMAIL, delay=50)
        time.sleep(1)

        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.type(TEST_PASSWORD, delay=50)
        time.sleep(1)

        page.keyboard.press("Tab")
        time.sleep(0.5)
        page.keyboard.press("Enter")

        print("    等待登录...")
        time.sleep(10)  # 增加登录等待
        page.wait_for_load_state("networkidle")

        print(f"    URL: {page.url}")

        if "/login" in page.url:
            # 重试一次
            print("    第一次登录失败，重试...")
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
            print(f"    重试后URL: {page.url}")

            if "/login" in page.url:
                print("    ❌ 登录仍然失败")
                page.screenshot(path="/tmp/detail_login_failed.png")
                browser.close()
                return

        print("    ✅ 登录成功")

        # 2. 等待主页加载
        print("\n[2] 等待主页加载...")
        time.sleep(5)
        page.screenshot(path="/tmp/detail_01_main.png")
        print("    截图: /tmp/detail_01_main.png")

        # 3. 点击简报卡片进入详情
        print("\n[3] 点击简报卡片...")

        # 卡片在页面中间偏上位置
        page.mouse.click(400, 280)
        time.sleep(4)

        page.screenshot(path="/tmp/detail_02_after_click.png")
        print("    截图: /tmp/detail_02_after_click.png")

        current_url = page.url
        print(f"    URL: {current_url}")

        # 4. 如果进入了详情页，滚动查看内容
        print("\n[4] 查看详情页内容...")
        time.sleep(2)

        for i in range(4):
            page.screenshot(path=f"/tmp/detail_03_content_{i}.png")
            print(f"    截图: /tmp/detail_03_content_{i}.png")
            page.mouse.wheel(0, 250)
            time.sleep(1.5)

        # 5. 返回主页
        print("\n[5] 返回主页...")
        page.keyboard.press("Escape")
        time.sleep(1)
        page.mouse.click(157, 760)  # 点击信息流
        time.sleep(2)

        page.screenshot(path="/tmp/detail_04_final.png")
        print("    截图: /tmp/detail_04_final.png")

        browser.close()

        print("\n" + "=" * 70)
        print("详情页测试完成")
        print("=" * 70)

if __name__ == "__main__":
    test_briefing_detail()
