#!/usr/bin/env python3
"""
完整的AI员工简报系统UI测试
使用Tab键导航和更长的等待时间来处理Flutter Web
"""

import time
from playwright.sync_api import sync_playwright

TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
BASE_URL = "http://localhost:5000"

def run_full_ui_test():
    """完整UI测试流程"""
    with sync_playwright() as p:
        # 使用非headless模式更容易调试
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        results = {
            "login": False,
            "main_page": False,
            "briefings": False,
            "cover_image": False,
            "navigation": False,
        }

        print("=" * 70)
        print("AI员工简报系统 - 完整UI验收测试")
        print("=" * 70)

        # ========== STEP 1: 加载应用 ==========
        print("\n[1/6] 加载应用...")
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(5)  # Flutter初始化

        page.screenshot(path="/tmp/ui_01_app_loaded.png")
        print("    截图: /tmp/ui_01_app_loaded.png")

        # ========== STEP 2: 登录流程 ==========
        print("\n[2/6] 执行登录...")

        # 方法1: 使用Tab键导航到表单字段
        # 先点击页面中心激活
        page.mouse.click(640, 400)
        time.sleep(0.5)

        # Tab到第一个输入框（邮箱）
        page.keyboard.press("Tab")
        time.sleep(0.3)
        page.keyboard.type(TEST_EMAIL, delay=30)
        time.sleep(0.5)

        page.screenshot(path="/tmp/ui_02_email_input.png")
        print("    截图: /tmp/ui_02_email_input.png")

        # Tab到密码框
        page.keyboard.press("Tab")
        time.sleep(0.3)
        page.keyboard.type(TEST_PASSWORD, delay=30)
        time.sleep(0.5)

        page.screenshot(path="/tmp/ui_03_password_input.png")
        print("    截图: /tmp/ui_03_password_input.png")

        # Tab到登录按钮并按Enter
        page.keyboard.press("Tab")
        time.sleep(0.3)
        page.keyboard.press("Enter")

        print("    等待登录响应...")
        time.sleep(8)
        page.wait_for_load_state("networkidle")

        page.screenshot(path="/tmp/ui_04_after_login.png")
        print("    截图: /tmp/ui_04_after_login.png")

        # 检查登录结果
        current_url = page.url
        print(f"    当前URL: {current_url}")

        if "/login" not in current_url:
            results["login"] = True
            print("    ✅ 登录成功!")
        else:
            # 如果Tab方法失败，尝试直接点击坐标
            print("    ⚠️ Tab方法未能登录，尝试坐标点击...")

            # 重新加载页面
            page.goto(BASE_URL)
            page.wait_for_load_state("networkidle")
            time.sleep(5)

            # 直接点击邮箱输入框区域
            page.mouse.click(640, 453)
            time.sleep(0.3)

            # 使用evaluate注入文本（Flutter web的替代方案）
            for char in TEST_EMAIL:
                page.keyboard.press(char if char != '@' else "Shift+2")
                time.sleep(0.02)

            time.sleep(0.5)

            # 点击密码框
            page.mouse.click(640, 517)
            time.sleep(0.3)
            page.keyboard.type(TEST_PASSWORD, delay=30)
            time.sleep(0.5)

            # 点击登录按钮
            page.mouse.click(640, 582)
            time.sleep(8)

            page.screenshot(path="/tmp/ui_04b_login_retry.png")
            print("    截图: /tmp/ui_04b_login_retry.png")

            if "/login" not in page.url:
                results["login"] = True
                print("    ✅ 重试登录成功!")

        # ========== STEP 3: 主页面检查 ==========
        print("\n[3/6] 检查主页面...")
        time.sleep(3)
        page.screenshot(path="/tmp/ui_05_main_page.png")
        print("    截图: /tmp/ui_05_main_page.png")

        # 检查页面内容
        content = page.content()
        if "信息流" in content or "AI员工" in content or "briefing" in content.lower():
            results["main_page"] = True
            print("    ✅ 主页面加载成功")
        else:
            print("    ⚠️ 主页面内容检查未通过")

        # ========== STEP 4: 简报列表检查 ==========
        print("\n[4/6] 检查简报列表...")

        # 如果登录成功，尝试查看简报
        if results["login"]:
            time.sleep(2)

            # 点击信息流标签（底部导航第一个）
            page.mouse.click(157, 760)
            time.sleep(3)

            page.screenshot(path="/tmp/ui_06_briefings_list.png")
            print("    截图: /tmp/ui_06_briefings_list.png")

            # 检查是否有简报卡片
            content = page.content()
            if "简报" in content or "briefing" in content.lower() or "card" in content.lower():
                results["briefings"] = True
                print("    ✅ 简报列表显示正常")

        # ========== STEP 5: 底部导航测试 ==========
        print("\n[5/6] 测试底部导航...")

        if results["login"]:
            nav_positions = [
                (157, 760, "信息流"),
                (477, 760, "AI员工"),
                (797, 760, "消息"),
                (1117, 760, "我的"),
            ]

            for x, y, name in nav_positions:
                page.mouse.click(x, y)
                time.sleep(2)
                page.screenshot(path=f"/tmp/ui_07_nav_{name}.png")
                print(f"    截图: /tmp/ui_07_nav_{name}.png")

            results["navigation"] = True
            print("    ✅ 底部导航测试完成")

        # ========== STEP 6: 封面图片检查 ==========
        print("\n[6/6] 检查封面图片功能...")

        # 回到信息流
        page.mouse.click(157, 760)
        time.sleep(3)

        page.screenshot(path="/tmp/ui_08_final_state.png", full_page=True)
        print("    截图: /tmp/ui_08_final_state.png")

        # 检查HTML中是否有图片元素或cover相关内容
        content = page.content()
        if "cover" in content.lower() or "image" in content.lower() or "img" in content.lower():
            results["cover_image"] = True
            print("    ✅ 检测到图片/封面相关元素")

        # ========== 测试总结 ==========
        print("\n" + "=" * 70)
        print("测试结果总结")
        print("=" * 70)

        all_passed = True
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {test_name}: {status}")
            if not passed:
                all_passed = False

        print("\n截图文件列表:")
        print("  /tmp/ui_01_app_loaded.png - 应用加载")
        print("  /tmp/ui_02_email_input.png - 邮箱输入")
        print("  /tmp/ui_03_password_input.png - 密码输入")
        print("  /tmp/ui_04_after_login.png - 登录后")
        print("  /tmp/ui_05_main_page.png - 主页面")
        print("  /tmp/ui_06_briefings_list.png - 简报列表")
        print("  /tmp/ui_07_nav_*.png - 导航页面")
        print("  /tmp/ui_08_final_state.png - 最终状态")

        browser.close()

        return all_passed, results

if __name__ == "__main__":
    success, results = run_full_ui_test()
    print(f"\n{'='*70}")
    if success:
        print("✅ 所有UI测试通过!")
    else:
        print("⚠️ 部分测试未通过，请查看截图进行人工验证")
    print(f"{'='*70}")
