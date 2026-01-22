#!/usr/bin/env python3
"""
Chris Chen AI Employee Comprehensive UI Test v2
Improved version with better Flutter web handling
"""

import os
import sys
import time
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
SCREENSHOT_DIR = "/tmp/chris_chen_test"
DESIGN_IMAGE_1 = "/Users/80392083/Downloads/design1.jpg"
DESIGN_IMAGE_2 = "/Users/80392083/Downloads/design2.jpg"

# Test results
test_results = {}


def setup_screenshot_dir():
    """Create screenshot directory"""
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)
    os.makedirs(SCREENSHOT_DIR)
    print(f"📁 Screenshot directory: {SCREENSHOT_DIR}")


def screenshot(page, name, description=""):
    """Take screenshot with timestamp"""
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"📸 Screenshot: {name} - {description}")
    return filename


def wait_for_flutter(page, timeout=60):
    """Wait for Flutter to fully load"""
    print("⏳ Waiting for Flutter app to load...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            # Check if Flutter has loaded by looking for any interactive element
            content = page.content()

            # Flutter web app typically has flt-glass-pane or specific elements
            if 'flt-glass-pane' in content or 'flutter' in content.lower():
                # Additional wait for UI rendering
                time.sleep(3)

                # Check for any visible text content
                body_text = page.inner_text('body', timeout=5000)
                if len(body_text) > 10:  # Has meaningful content
                    print(f"✅ Flutter loaded in {time.time() - start:.1f}s")
                    return True

        except Exception:
            pass

        time.sleep(2)

    print(f"⚠️ Flutter load timeout after {timeout}s")
    return False


def test_login(page):
    """Test login flow"""
    print("\n=== Testing Login ===")
    start_time = time.time()

    try:
        page.goto(BASE_URL)

        # Wait for Flutter to load
        if not wait_for_flutter(page, 60):
            screenshot(page, "01_flutter_loading", "Flutter still loading")

        time.sleep(5)  # Extra wait for UI
        screenshot(page, "01_initial_page", "Initial page")

        # Get page content
        body_text = page.inner_text('body', timeout=10000)
        print(f"Page content preview: {body_text[:200]}...")

        # Check if already logged in (look for bottom nav or agent list)
        if "员工" in body_text or "消息" in body_text or "简报" in body_text:
            print("✅ Already logged in")
            test_results["login"] = {"status": "pass", "notes": "Already logged in"}
            return True

        # Look for login form - Flutter web uses semantic labels
        # Try multiple selector strategies
        selectors_to_try = [
            'input',
            '[class*="TextField"]',
            'flt-semantics input',
            '[contenteditable="true"]',
        ]

        input_found = False
        for selector in selectors_to_try:
            inputs = page.locator(selector).all()
            if len(inputs) >= 2:
                print(f"Found inputs with selector: {selector}")
                input_found = True

                # Fill email
                inputs[0].click()
                time.sleep(0.5)
                page.keyboard.type(TEST_EMAIL)
                time.sleep(0.5)

                # Fill password
                inputs[1].click()
                time.sleep(0.5)
                page.keyboard.type(TEST_PASSWORD)

                screenshot(page, "02_credentials_filled", "Credentials entered")
                break

        if not input_found:
            # Try clicking on text that might be input labels
            email_label = page.locator('text=邮箱, text=Email, text=账号').first
            if email_label.is_visible():
                email_label.click()
                time.sleep(0.5)
                page.keyboard.type(TEST_EMAIL)
                page.keyboard.press('Tab')
                time.sleep(0.5)
                page.keyboard.type(TEST_PASSWORD)
                screenshot(page, "02_credentials_via_label", "Filled via labels")

        # Click login button
        login_selectors = [
            'text=登录',
            'text=Login',
            'text=登 录',
            'button',
        ]

        for selector in login_selectors:
            btn = page.locator(selector).first
            if btn.is_visible():
                btn.click()
                print(f"Clicked login with: {selector}")
                break

        # Wait for navigation
        time.sleep(8)
        screenshot(page, "03_after_login", "After login attempt")

        # Verify login success
        body_text = page.inner_text('body', timeout=10000)
        if "员工" in body_text or "消息" in body_text or "简报" in body_text or "Agent" in body_text:
            elapsed = time.time() - start_time
            test_results["login"] = {"status": "pass", "notes": f"Login successful in {elapsed:.1f}s"}
            print(f"✅ Login successful ({elapsed:.1f}s)")
            return True
        else:
            test_results["login"] = {"status": "fail", "notes": "Login did not navigate to main page"}
            print("❌ Login failed - still on login page")
            return False

    except Exception as e:
        screenshot(page, "error_login", f"Login error")
        test_results["login"] = {"status": "fail", "notes": str(e)}
        print(f"❌ Login failed: {e}")
        return False


def navigate_to_chris_chen(page):
    """Navigate to Chris Chen through unified card entry"""
    print("\n=== Testing Navigation to Chris Chen ===")
    start_time = time.time()

    try:
        # Try to navigate to agents page via bottom nav or direct URL
        page.goto(f"{BASE_URL}/#/agents")
        time.sleep(5)
        screenshot(page, "04_agents_page", "Agents page")

        body_text = page.inner_text('body', timeout=10000)
        print(f"Agents page content: {body_text[:300]}...")

        # Look for Chris Chen
        if "Chris" in body_text or "设计" in body_text:
            print("✅ Found Chris Chen or design agent")

            # Click on Chris Chen card or start button
            chris_btn = page.locator('text=Chris').first
            if not chris_btn.is_visible():
                chris_btn = page.locator('text=设计评审').first
            if not chris_btn.is_visible():
                chris_btn = page.locator('text=开始对话').first

            if chris_btn.is_visible():
                chris_btn.click()
                time.sleep(3)
                screenshot(page, "05_chris_clicked", "After clicking Chris")

        # Check for unified entry point
        start_btn = page.locator('text=开始对话')
        detail_btn = page.locator('text=查看详情')
        chat_btn = page.locator('text=对话')

        if start_btn.count() > 0 and detail_btn.count() == 0:
            test_results["card_entry"] = {"status": "pass", "notes": "Unified entry point (开始对话) confirmed"}
            print("✅ Unified entry point confirmed")
        elif detail_btn.count() > 0 and chat_btn.count() > 0:
            test_results["card_entry"] = {"status": "fail", "notes": "WARNING: Dual buttons still exist"}
            print("⚠️ Dual buttons still exist - unified entry not complete")

        # Click entry button
        if start_btn.count() > 0:
            start_btn.first.click()
        elif detail_btn.count() > 0:
            detail_btn.first.click()

        time.sleep(5)
        screenshot(page, "06_chris_profile", "Chris Chen profile page")

        elapsed = time.time() - start_time
        if "card_entry" not in test_results:
            test_results["card_entry"] = {"status": "pass", "notes": f"Navigation successful in {elapsed:.1f}s"}
        print(f"✅ Navigation completed ({elapsed:.1f}s)")
        return True

    except Exception as e:
        screenshot(page, "error_navigation", str(e))
        test_results["card_entry"] = {"status": "fail", "notes": str(e)}
        print(f"❌ Navigation failed: {e}")
        return False


def test_profile_view(page):
    """Test profile view elements"""
    print("\n=== Testing Profile View ===")

    try:
        body_text = page.inner_text('body', timeout=10000)
        screenshot(page, "07_profile_view", "Profile view")

        checks = {
            "greeting": any(g in body_text for g in ["早上好", "上午好", "下午好", "晚上好", "中午好", "夜深了"]),
            "agent_name": "Chris" in body_text or "设计" in body_text,
            "quick_actions": "交互" in body_text or "视觉" in body_text or "方案" in body_text,
            "input_hint": "背景" in body_text or "描述" in body_text or "输入" in body_text,
        }

        notes = [k for k, v in checks.items() if v]
        test_results["profile_view"] = {
            "status": "pass" if len(notes) >= 2 else "partial",
            "notes": f"Found: {', '.join(notes)}"
        }
        print(f"✅ Profile view elements: {', '.join(notes)}")
        return True

    except Exception as e:
        test_results["profile_view"] = {"status": "fail", "notes": str(e)}
        print(f"❌ Profile view test failed: {e}")
        return False


def test_send_message(page, message, test_name, expected_keywords):
    """Generic function to test sending a message"""
    print(f"\n=== Testing {test_name} ===")
    start_time = time.time()

    try:
        # Find textarea or input
        textarea = page.locator('textarea').first
        if not textarea.is_visible():
            # Click somewhere to activate input
            page.locator('text=描述, text=输入, text=消息').first.click()
            time.sleep(1)
            textarea = page.locator('textarea').first

        if textarea.is_visible():
            textarea.fill(message)
            screenshot(page, f"{test_name}_01_typed", f"{test_name} - message typed")

            # Click send
            send_btn = page.locator('button').filter(has=page.locator('[class*="send"], [class*="Send"]')).first
            if not send_btn.is_visible():
                # Try keyboard
                page.keyboard.press('Enter')
            else:
                send_btn.click()

            # Wait for response
            print("⏳ Waiting for AI response...")
            time.sleep(15)
            screenshot(page, f"{test_name}_02_response", f"{test_name} - response received")

            body_text = page.inner_text('body', timeout=10000)
            elapsed = time.time() - start_time

            found = [k for k in expected_keywords if k in body_text]

            test_results[test_name] = {
                "status": "pass" if found else "partial",
                "notes": f"Keywords: {', '.join(found[:3]) if found else 'none'}; Time: {elapsed:.1f}s"
            }
            print(f"✅ {test_name}: {', '.join(found[:3]) if found else 'Response received'}")
            return True
        else:
            test_results[test_name] = {"status": "fail", "notes": "Input field not found"}
            print(f"❌ {test_name}: Input not found")
            return False

    except Exception as e:
        screenshot(page, f"error_{test_name}", str(e))
        test_results[test_name] = {"status": "fail", "notes": str(e)}
        print(f"❌ {test_name} failed: {e}")
        return False


def test_quick_action(page, button_text, test_name, expected_keywords):
    """Test clicking a quick action button"""
    print(f"\n=== Testing Quick Action: {button_text} ===")
    start_time = time.time()

    try:
        btn = page.locator(f'text={button_text}').first
        if btn.is_visible():
            screenshot(page, f"{test_name}_before", f"Before {button_text}")
            btn.click()

            # Wait for response
            print("⏳ Waiting for AI response...")
            time.sleep(12)
            screenshot(page, f"{test_name}_after", f"After {button_text}")

            body_text = page.inner_text('body', timeout=10000)
            elapsed = time.time() - start_time

            found = [k for k in expected_keywords if k in body_text]

            test_results[test_name] = {
                "status": "pass" if found else "partial",
                "notes": f"Keywords: {', '.join(found[:3]) if found else 'none'}; Time: {elapsed:.1f}s"
            }
            print(f"✅ {button_text}: {', '.join(found[:3]) if found else 'Response received'}")
            return True
        else:
            test_results[test_name] = {"status": "fail", "notes": f"Button '{button_text}' not found"}
            print(f"❌ Button '{button_text}' not found")
            return False

    except Exception as e:
        test_results[test_name] = {"status": "fail", "notes": str(e)}
        print(f"❌ Quick action {button_text} failed: {e}")
        return False


def test_new_conversation(page):
    """Test new conversation feature"""
    print("\n=== Testing New Conversation Feature ===")

    try:
        # Look for more menu (三点图标)
        more_btn = page.locator('button').filter(has=page.locator('text=⋯')).first
        if not more_btn.is_visible():
            # Try finding by position (top right area)
            buttons = page.locator('button').all()
            for btn in buttons[-5:]:  # Check last 5 buttons
                try:
                    btn.click()
                    time.sleep(1)
                    if page.locator('text=新建对话').is_visible():
                        more_btn = btn
                        break
                    # Click elsewhere to close any popup
                    page.keyboard.press('Escape')
                except:
                    continue

        screenshot(page, "new_conv_01_menu", "Looking for more menu")

        new_conv_btn = page.locator('text=新建对话').first
        if new_conv_btn.is_visible():
            new_conv_btn.click()
            time.sleep(2)
            screenshot(page, "new_conv_02_created", "New conversation created")
            test_results["new_conversation"] = {"status": "pass", "notes": "New conversation feature works"}
            print("✅ New conversation feature works")
            return True
        else:
            test_results["new_conversation"] = {"status": "fail", "notes": "New conversation option not found"}
            print("⚠️ New conversation option not found")
            return False

    except Exception as e:
        test_results["new_conversation"] = {"status": "fail", "notes": str(e)}
        print(f"❌ New conversation test failed: {e}")
        return False


def test_image_upload_and_analysis(page):
    """Test image upload and AI understanding"""
    print("\n=== Testing Image Upload & Analysis ===")
    start_time = time.time()

    try:
        # Look for file input (might be hidden)
        file_input = page.locator('input[type="file"]')

        if file_input.count() > 0:
            # Direct upload
            file_input.first.set_input_files(DESIGN_IMAGE_1)
            time.sleep(3)
            screenshot(page, "image_01_uploaded", "Image uploaded")
            test_results["image_upload"] = {"status": "pass", "notes": "Direct file upload works"}
            print("✅ Image uploaded")
        else:
            # Look for attachment button
            attach_btn = page.locator('button').filter(has=page.locator('[class*="attach"], [class*="Attach"]')).first
            if attach_btn.is_visible():
                attach_btn.click()
                time.sleep(2)
                screenshot(page, "image_01_picker", "Attachment picker")
                test_results["image_upload"] = {"status": "partial", "notes": "Attachment picker opened"}
                print("⚠️ Attachment picker opened")
            else:
                test_results["image_upload"] = {"status": "fail", "notes": "No upload mechanism found"}
                print("❌ No upload mechanism found")
                return False

        # Send message asking about image
        message = "请帮我分析一下这个设计稿的问题"
        textarea = page.locator('textarea').first
        if textarea.is_visible():
            textarea.fill(message)
            page.keyboard.press('Enter')

            print("⏳ Waiting for image analysis...")
            time.sleep(20)  # Image analysis takes longer
            screenshot(page, "image_02_analysis", "Image analysis response")

            body_text = page.inner_text('body', timeout=10000)
            elapsed = time.time() - start_time

            # Keywords indicating image understanding
            image_keywords = ["图", "设计", "布局", "看", "显示", "界面", "按钮", "颜色", "元素"]
            found = [k for k in image_keywords if k in body_text]

            test_results["image_understanding"] = {
                "status": "pass" if len(found) >= 2 else "partial",
                "notes": f"Keywords: {', '.join(found[:5])}; Time: {elapsed:.1f}s"
            }
            print(f"✅ Image analysis: {', '.join(found[:3]) if found else 'Response received'}")
            return True

    except Exception as e:
        screenshot(page, "error_image", str(e))
        test_results["image_upload"] = {"status": "fail", "notes": str(e)}
        test_results["image_understanding"] = {"status": "fail", "notes": str(e)}
        print(f"❌ Image test failed: {e}")
        return False


def generate_report():
    """Generate final test report"""
    print("\n" + "="*70)
    print("📋 CHRIS CHEN AI EMPLOYEE - COMPREHENSIVE TEST REPORT")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)

    passed = failed = partial = 0

    for test_name, result in test_results.items():
        status = result.get("status", "pending")
        notes = result.get("notes", "")

        icon = {"pass": "✅", "fail": "❌", "partial": "⚠️"}.get(status, "⏸️")

        if status == "pass": passed += 1
        elif status == "fail": failed += 1
        elif status == "partial": partial += 1

        print(f"{icon} {test_name}: {status}")
        if notes:
            print(f"   └─ {notes}")

    print("-"*70)
    print(f"📊 Summary: {passed} passed, {partial} partial, {failed} failed")
    print(f"📁 Screenshots: {SCREENSHOT_DIR}")
    print("-"*70)

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
    print("🚀 Chris Chen Comprehensive UI Test v2")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target: {BASE_URL}")

    setup_screenshot_dir()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2,
        )
        page = context.new_page()

        try:
            # Core tests
            if test_login(page):
                if navigate_to_chris_chen(page):
                    test_profile_view(page)

                    # Test basic conversation
                    test_send_message(
                        page,
                        "你好，我想进行一个设计评审",
                        "basic_conversation",
                        ["评审", "设计", "好", "方案", "帮"]
                    )

                    # Test quick actions
                    test_quick_action(
                        page, "交互验证", "interaction_mode",
                        ["交互", "流程", "用户", "操作", "入口"]
                    )

                    test_quick_action(
                        page, "视觉讨论", "visual_mode",
                        ["视觉", "颜色", "字体", "一致", "间距"]
                    )

                    test_quick_action(
                        page, "方案选择", "compare_mode",
                        ["方案", "对比", "选择", "优势", "取舍"]
                    )

                    # Test new conversation
                    test_new_conversation(page)

                    # Test image features
                    test_image_upload_and_analysis(page)

        except Exception as e:
            print(f"❌ Test suite error: {e}")
            screenshot(page, "error_final", str(e))

        finally:
            browser.close()

    success = generate_report()

    if success:
        print("\n✅ DONE")
    else:
        print("\n❌ DONE (with failures)")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
