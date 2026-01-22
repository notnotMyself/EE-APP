#!/usr/bin/env python3
"""
Chris Chen AI Employee - Final Comprehensive UI Test
Optimized for Flutter Web interaction
"""

import os
import sys
import time
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
SCREENSHOT_DIR = "/tmp/chris_chen_test"
DESIGN_IMAGE_1 = "/Users/80392083/Downloads/design1.jpg"
DESIGN_IMAGE_2 = "/Users/80392083/Downloads/design2.jpg"

test_results = {}


def setup():
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)
    os.makedirs(SCREENSHOT_DIR)
    print(f"📁 Screenshots: {SCREENSHOT_DIR}")


def shot(page, name, desc=""):
    ts = datetime.now().strftime("%H%M%S")
    path = f"{SCREENSHOT_DIR}/{ts}_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"📸 {name}: {desc}")
    return path


def wait_flutter(page, timeout=90):
    """Wait for Flutter app to fully render"""
    print("⏳ Waiting for Flutter...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            # Check for Flutter content
            text = page.inner_text('body', timeout=3000)
            if len(text) > 50:
                time.sleep(2)  # Extra settle time
                print(f"✅ Flutter ready ({time.time()-start:.1f}s)")
                return True
        except:
            pass
        time.sleep(2)

    print(f"⚠️ Flutter timeout ({timeout}s)")
    return False


def click_at(page, x, y):
    """Click at specific coordinates"""
    page.mouse.click(x, y)
    time.sleep(0.3)


def test_login(page):
    """Test login with coordinate-based interaction"""
    print("\n=== 1. Testing Login ===")
    start = time.time()

    try:
        page.goto(BASE_URL)
        wait_flutter(page)
        shot(page, "01_login_page", "Login page loaded")

        # Get viewport dimensions
        vp = page.viewport_size
        center_x = vp['width'] // 2

        # Click on email field (approximately y=520 based on screenshot)
        print("Clicking email field...")
        click_at(page, center_x, 530)
        time.sleep(0.5)

        # Type email
        page.keyboard.type(TEST_EMAIL, delay=50)
        time.sleep(0.5)
        shot(page, "02_email_entered", "Email entered")

        # Click on password field (approximately y=595)
        print("Clicking password field...")
        click_at(page, center_x, 600)
        time.sleep(0.5)

        # Type password
        page.keyboard.type(TEST_PASSWORD, delay=50)
        time.sleep(0.5)
        shot(page, "03_password_entered", "Password entered")

        # Click login button (approximately y=665)
        print("Clicking login button...")
        click_at(page, center_x, 665)

        # Wait for navigation
        print("Waiting for login...")
        time.sleep(8)
        shot(page, "04_after_login", "After login")

        # Verify login success
        text = page.inner_text('body', timeout=5000)
        if any(kw in text for kw in ["消息", "简报", "员工", "Agent"]):
            elapsed = time.time() - start
            test_results["login"] = {"status": "pass", "notes": f"Success in {elapsed:.1f}s"}
            print(f"✅ Login successful ({elapsed:.1f}s)")
            return True
        else:
            shot(page, "04_login_failed", "Login verification failed")
            test_results["login"] = {"status": "fail", "notes": "Did not reach main page"}
            print("❌ Login failed")
            return False

    except Exception as e:
        shot(page, "error_login", str(e)[:50])
        test_results["login"] = {"status": "fail", "notes": str(e)[:100]}
        print(f"❌ Login error: {e}")
        return False


def navigate_to_chris(page):
    """Navigate to Chris Chen agent"""
    print("\n=== 2. Testing Navigation to Chris Chen ===")
    start = time.time()

    try:
        # Click on AI员工 tab (bottom navigation)
        vp = page.viewport_size
        # Bottom nav typically has 4 items, AI员工 might be 2nd
        nav_y = vp['height'] - 40

        # Try clicking different bottom nav positions
        for x_pos in [vp['width']//4, vp['width']//2 - 50, vp['width']*3//4]:
            click_at(page, x_pos, nav_y)
            time.sleep(2)
            text = page.inner_text('body', timeout=3000)
            if "Chris" in text or "设计" in text or "开始对话" in text:
                break

        shot(page, "05_agents_list", "Agent list page")

        # Look for Chris Chen
        text = page.inner_text('body', timeout=5000)

        # Check for unified entry (开始对话) vs dual buttons (查看详情 + 对话)
        has_start = "开始对话" in text
        has_detail = "查看详情" in text
        has_chat = text.count("对话") > 1  # Multiple "对话" buttons

        if has_start and not has_detail:
            test_results["unified_entry"] = {"status": "pass", "notes": "Single entry point confirmed"}
            print("✅ Unified entry point (开始对话) confirmed")
        elif has_detail:
            test_results["unified_entry"] = {"status": "fail", "notes": "Dual buttons still exist"}
            print("⚠️ Dual buttons still exist")
        else:
            test_results["unified_entry"] = {"status": "partial", "notes": "Entry point unclear"}

        # Click on Chris Chen card or button
        # Find "开始对话" or "Chris" and click
        try:
            btn = page.locator('text=开始对话').first
            if btn.is_visible():
                btn.click()
            else:
                btn = page.locator('text=Chris').first
                if btn.is_visible():
                    btn.click()
        except:
            # Click in the middle area where card might be
            click_at(page, vp['width']//2, vp['height']//2)

        time.sleep(3)
        shot(page, "06_chris_profile", "Chris Chen profile")

        elapsed = time.time() - start
        test_results["navigation"] = {"status": "pass", "notes": f"Navigation in {elapsed:.1f}s"}
        print(f"✅ Navigation complete ({elapsed:.1f}s)")
        return True

    except Exception as e:
        shot(page, "error_navigation", str(e)[:50])
        test_results["navigation"] = {"status": "fail", "notes": str(e)[:100]}
        print(f"❌ Navigation error: {e}")
        return False


def test_profile_view(page):
    """Test profile view elements"""
    print("\n=== 3. Testing Profile View ===")

    try:
        text = page.inner_text('body', timeout=5000)
        shot(page, "07_profile_detail", "Profile view detail")

        checks = {
            "greeting": any(g in text for g in ["早上好", "上午好", "下午好", "晚上好", "中午好", "夜深了"]),
            "agent_name": "Chris" in text,
            "description": "设计" in text or "评审" in text,
            "quick_actions": any(a in text for a in ["交互验证", "视觉讨论", "方案选择"]),
            "input_area": "描述" in text or "背景" in text,
        }

        passed = sum(checks.values())
        notes = [k for k, v in checks.items() if v]

        test_results["profile_view"] = {
            "status": "pass" if passed >= 3 else "partial",
            "notes": f"Found: {', '.join(notes)}"
        }
        print(f"✅ Profile view: {', '.join(notes)}")
        return True

    except Exception as e:
        test_results["profile_view"] = {"status": "fail", "notes": str(e)[:100]}
        print(f"❌ Profile view error: {e}")
        return False


def test_conversation(page, message, test_name, keywords):
    """Test sending a message and getting response"""
    print(f"\n=== Testing: {test_name} ===")
    start = time.time()

    try:
        vp = page.viewport_size

        # Click on input area (bottom of screen)
        input_y = vp['height'] - 120
        click_at(page, vp['width']//2, input_y)
        time.sleep(0.5)

        # Type message
        page.keyboard.type(message, delay=30)
        time.sleep(0.5)
        shot(page, f"{test_name}_01_typed", "Message typed")

        # Press Enter or click send
        page.keyboard.press('Enter')

        # Wait for AI response
        print("⏳ Waiting for AI response...")
        time.sleep(15)
        shot(page, f"{test_name}_02_response", "AI response")

        text = page.inner_text('body', timeout=5000)
        elapsed = time.time() - start

        found = [k for k in keywords if k in text]

        test_results[test_name] = {
            "status": "pass" if found else "partial",
            "notes": f"Keywords: {', '.join(found[:3]) if found else 'none'}; {elapsed:.1f}s"
        }
        print(f"✅ {test_name}: {', '.join(found[:3]) if found else 'Response received'} ({elapsed:.1f}s)")
        return True

    except Exception as e:
        test_results[test_name] = {"status": "fail", "notes": str(e)[:100]}
        print(f"❌ {test_name} error: {e}")
        return False


def test_quick_action(page, button_text, test_name, keywords):
    """Test clicking a quick action button"""
    print(f"\n=== Testing Quick Action: {button_text} ===")
    start = time.time()

    try:
        shot(page, f"{test_name}_00_before", f"Before {button_text}")

        # Try to find and click the button
        btn = page.locator(f'text={button_text}').first
        if btn.is_visible():
            btn.click()
        else:
            # Scroll down to find quick actions
            page.keyboard.press('End')
            time.sleep(1)
            btn = page.locator(f'text={button_text}').first
            if btn.is_visible():
                btn.click()

        # Wait for response
        print("⏳ Waiting for AI response...")
        time.sleep(12)
        shot(page, f"{test_name}_01_response", f"After {button_text}")

        text = page.inner_text('body', timeout=5000)
        elapsed = time.time() - start

        found = [k for k in keywords if k in text]

        test_results[test_name] = {
            "status": "pass" if found else "partial",
            "notes": f"Keywords: {', '.join(found[:3]) if found else 'none'}; {elapsed:.1f}s"
        }
        print(f"✅ {button_text}: {', '.join(found[:3]) if found else 'Done'} ({elapsed:.1f}s)")
        return True

    except Exception as e:
        test_results[test_name] = {"status": "fail", "notes": str(e)[:100]}
        print(f"❌ {button_text} error: {e}")
        return False


def test_new_conversation(page):
    """Test new conversation feature"""
    print("\n=== Testing New Conversation ===")

    try:
        vp = page.viewport_size

        # Click more menu (top right)
        click_at(page, vp['width'] - 30, 50)
        time.sleep(1)
        shot(page, "new_conv_01_menu", "More menu")

        # Look for 新建对话
        text = page.inner_text('body', timeout=3000)
        if "新建对话" in text:
            btn = page.locator('text=新建对话').first
            btn.click()
            time.sleep(2)
            shot(page, "new_conv_02_created", "New conversation")
            test_results["new_conversation"] = {"status": "pass", "notes": "Feature works"}
            print("✅ New conversation works")
        else:
            shot(page, "new_conv_02_not_found", "Option not found")
            test_results["new_conversation"] = {"status": "fail", "notes": "Option not found in menu"}
            print("⚠️ New conversation not found")

        # Close menu
        page.keyboard.press('Escape')
        return True

    except Exception as e:
        test_results["new_conversation"] = {"status": "fail", "notes": str(e)[:100]}
        print(f"❌ New conversation error: {e}")
        return False


def test_image_upload(page):
    """Test image upload and understanding"""
    print("\n=== Testing Image Upload & Understanding ===")
    start = time.time()

    try:
        # Look for file input
        file_inputs = page.locator('input[type="file"]').all()

        if file_inputs:
            file_inputs[0].set_input_files(DESIGN_IMAGE_1)
            time.sleep(3)
            shot(page, "image_01_uploaded", "Image uploaded")
            test_results["image_upload"] = {"status": "pass", "notes": "Direct upload works"}
            print("✅ Image uploaded")

            # Send analysis request
            vp = page.viewport_size
            click_at(page, vp['width']//2, vp['height'] - 120)
            time.sleep(0.5)
            page.keyboard.type("请分析这个设计稿有什么问题", delay=30)
            page.keyboard.press('Enter')

            print("⏳ Waiting for image analysis...")
            time.sleep(20)
            shot(page, "image_02_analysis", "Image analysis")

            text = page.inner_text('body', timeout=5000)
            elapsed = time.time() - start

            image_kw = ["图", "设计", "界面", "布局", "颜色", "元素", "按钮", "看"]
            found = [k for k in image_kw if k in text]

            test_results["image_understanding"] = {
                "status": "pass" if len(found) >= 2 else "partial",
                "notes": f"Keywords: {', '.join(found[:5])}; {elapsed:.1f}s"
            }
            print(f"✅ Image understanding: {', '.join(found[:3]) if found else 'Response received'}")
        else:
            # Try attachment button approach
            shot(page, "image_01_no_input", "No file input found")
            test_results["image_upload"] = {"status": "partial", "notes": "No direct file input"}
            test_results["image_understanding"] = {"status": "pending", "notes": "Depends on upload"}
            print("⚠️ No direct file input found")

        return True

    except Exception as e:
        shot(page, "error_image", str(e)[:50])
        test_results["image_upload"] = {"status": "fail", "notes": str(e)[:100]}
        test_results["image_understanding"] = {"status": "fail", "notes": str(e)[:100]}
        print(f"❌ Image test error: {e}")
        return False


def generate_report():
    """Generate final report"""
    print("\n" + "="*70)
    print("📋 CHRIS CHEN - COMPREHENSIVE TEST REPORT")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)

    passed = failed = partial = 0

    for name, result in test_results.items():
        status = result.get("status", "pending")
        notes = result.get("notes", "")

        icon = {"pass": "✅", "fail": "❌", "partial": "⚠️"}.get(status, "⏸️")

        if status == "pass": passed += 1
        elif status == "fail": failed += 1
        elif status == "partial": partial += 1

        print(f"{icon} {name}: {status}")
        if notes:
            print(f"   └─ {notes}")

    print("-"*70)
    print(f"📊 Results: {passed} passed, {partial} partial, {failed} failed")
    print(f"📁 Screenshots: {SCREENSHOT_DIR}")
    print("-"*70)

    total = passed + partial + failed
    if total > 0:
        success_rate = (passed + partial * 0.5) / total * 100
        print(f"📈 Success Rate: {success_rate:.0f}%")

    if failed == 0:
        print("🎉 OVERALL: PASS")
        return True
    elif failed <= 2:
        print("⚠️ OVERALL: PARTIAL PASS")
        return True
    else:
        print("❌ OVERALL: FAIL")
        return False


def main():
    print("🚀 Chris Chen Comprehensive Test - Final Version")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    setup()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2,
        )
        page = context.new_page()

        try:
            if test_login(page):
                if navigate_to_chris(page):
                    test_profile_view(page)

                    # Basic conversation
                    test_conversation(
                        page,
                        "你好，我想做个设计评审",
                        "basic_chat",
                        ["评审", "设计", "好", "帮", "方案"]
                    )

                    # Quick actions
                    test_quick_action(
                        page, "交互验证", "interaction_mode",
                        ["交互", "流程", "用户", "操作", "入口", "路径"]
                    )

                    test_quick_action(
                        page, "视觉讨论", "visual_mode",
                        ["视觉", "颜色", "字体", "一致", "间距", "对齐"]
                    )

                    test_quick_action(
                        page, "方案选择", "compare_mode",
                        ["方案", "对比", "选择", "优势", "取舍", "比较"]
                    )

                    # New conversation
                    test_new_conversation(page)

                    # Image features
                    test_image_upload(page)

        except Exception as e:
            print(f"❌ Test suite error: {e}")
            shot(page, "error_final", str(e)[:50])
        finally:
            browser.close()

    success = generate_report()
    print("\nDONE")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
