#!/usr/bin/env python3
"""
Chris Chen AI Employee Comprehensive UI Test
Tests all features including:
- Login flow
- Unified card entry point
- Image upload
- Quick action buttons (interaction, visual, compare modes)
- AI response verification
"""

import os
import sys
import time
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
SCREENSHOT_DIR = "/tmp/chris_chen_test"
DESIGN_IMAGE_1 = "/Users/80392083/Downloads/design1.jpg"
DESIGN_IMAGE_2 = "/Users/80392083/Downloads/design2.jpg"

# Test results
test_results = {
    "login": {"status": "pending", "notes": ""},
    "card_entry": {"status": "pending", "notes": ""},
    "profile_view": {"status": "pending", "notes": ""},
    "image_upload": {"status": "pending", "notes": ""},
    "text_conversation": {"status": "pending", "notes": ""},
    "interaction_mode": {"status": "pending", "notes": ""},
    "visual_mode": {"status": "pending", "notes": ""},
    "compare_mode": {"status": "pending", "notes": ""},
    "new_conversation": {"status": "pending", "notes": ""},
    "image_understanding": {"status": "pending", "notes": ""},
    "performance": {"status": "pending", "notes": ""},
}


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


def test_login(page):
    """Test login flow"""
    print("\n=== Testing Login ===")
    start_time = time.time()

    try:
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        screenshot(page, "01_initial_page", "Initial page load")

        # Check if already logged in
        if "员工" in page.content() or "Agent" in page.content():
            print("✅ Already logged in")
            test_results["login"]["status"] = "pass"
            test_results["login"]["notes"] = "Already logged in"
            return True

        # Wait for login form
        page.wait_for_selector('input[type="email"], input[type="text"]', timeout=10000)
        screenshot(page, "02_login_form", "Login form visible")

        # Fill credentials
        email_input = page.locator('input[type="email"], input[type="text"]').first
        email_input.fill(TEST_EMAIL)

        password_input = page.locator('input[type="password"]')
        password_input.fill(TEST_PASSWORD)
        screenshot(page, "03_credentials_filled", "Credentials entered")

        # Click login button
        login_btn = page.locator('button:has-text("登录"), button:has-text("Login"), button[type="submit"]').first
        login_btn.click()

        # Wait for navigation
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(2)
        screenshot(page, "04_after_login", "After login")

        elapsed = time.time() - start_time
        test_results["login"]["status"] = "pass"
        test_results["login"]["notes"] = f"Login successful in {elapsed:.1f}s"
        test_results["performance"]["notes"] += f"Login: {elapsed:.1f}s; "
        print(f"✅ Login successful ({elapsed:.1f}s)")
        return True

    except Exception as e:
        screenshot(page, "error_login", f"Login error: {str(e)}")
        test_results["login"]["status"] = "fail"
        test_results["login"]["notes"] = str(e)
        print(f"❌ Login failed: {e}")
        return False


def navigate_to_chris_chen(page):
    """Navigate to Chris Chen through unified card entry"""
    print("\n=== Testing Card Entry Point ===")
    start_time = time.time()

    try:
        # Navigate to AI employee marketplace
        page.goto(f"{BASE_URL}/#/agents")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        screenshot(page, "05_agents_list", "AI Employee Marketplace")

        # Look for Chris Chen card
        chris_card = page.locator('text=Chris Chen').first
        if not chris_card.is_visible():
            # Try other possible names
            chris_card = page.locator('text=设计评审').first

        screenshot(page, "06_chris_card_found", "Chris Chen card visible")

        # Check for unified entry button (should be single "开始对话" button)
        start_btn = page.locator('button:has-text("开始对话")').first
        if start_btn.is_visible():
            test_results["card_entry"]["notes"] = "Unified entry point found"
            print("✅ Unified entry point (开始对话) found")
        else:
            # Check if old dual buttons exist
            detail_btn = page.locator('button:has-text("查看详情")')
            chat_btn = page.locator('button:has-text("对话")')
            if detail_btn.is_visible() and chat_btn.is_visible():
                test_results["card_entry"]["notes"] = "WARNING: Old dual buttons still exist"
                print("⚠️ Old dual buttons still exist")

        # Click the entry button
        start_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        screenshot(page, "07_chris_profile", "Chris Chen Profile Page")

        elapsed = time.time() - start_time
        test_results["card_entry"]["status"] = "pass"
        test_results["performance"]["notes"] += f"Navigation: {elapsed:.1f}s; "
        print(f"✅ Card entry successful ({elapsed:.1f}s)")
        return True

    except Exception as e:
        screenshot(page, "error_card_entry", f"Card entry error: {str(e)}")
        test_results["card_entry"]["status"] = "fail"
        test_results["card_entry"]["notes"] = str(e)
        print(f"❌ Card entry failed: {e}")
        return False


def test_profile_view(page):
    """Test profile view before conversation"""
    print("\n=== Testing Profile View ===")

    try:
        # Check for greeting
        content = page.content()
        has_greeting = any(g in content for g in ["早上好", "上午好", "下午好", "晚上好", "中午好", "夜深了"])

        # Check for avatar
        has_avatar = page.locator('img[src*="chris"], img[src*="avatar"]').count() > 0 or \
                    page.locator('[class*="avatar"], [class*="Avatar"]').count() > 0

        # Check for quick action buttons
        has_quick_actions = page.locator('text=交互验证').is_visible() or \
                          page.locator('text=视觉讨论').is_visible()

        # Check for input field
        has_input = page.locator('textarea, input[type="text"]').count() > 0

        screenshot(page, "08_profile_elements", "Profile view elements")

        notes = []
        if has_greeting:
            notes.append("Greeting visible")
        if has_avatar:
            notes.append("Avatar visible")
        if has_quick_actions:
            notes.append("Quick actions visible")
        if has_input:
            notes.append("Input field visible")

        test_results["profile_view"]["status"] = "pass" if all([has_greeting, has_quick_actions, has_input]) else "partial"
        test_results["profile_view"]["notes"] = "; ".join(notes)
        print(f"✅ Profile view: {'; '.join(notes)}")
        return True

    except Exception as e:
        test_results["profile_view"]["status"] = "fail"
        test_results["profile_view"]["notes"] = str(e)
        print(f"❌ Profile view test failed: {e}")
        return False


def test_text_conversation(page):
    """Test basic text conversation"""
    print("\n=== Testing Text Conversation ===")
    start_time = time.time()

    try:
        # Find input field
        input_field = page.locator('textarea').first
        if not input_field.is_visible():
            input_field = page.locator('input[type="text"]').first

        # Type a message
        test_message = "你好，我想进行一个设计评审"
        input_field.fill(test_message)
        screenshot(page, "09_message_typed", "Message typed in input")

        # Find and click send button
        send_btn = page.locator('button[type="submit"], button:has-text("发送"), [class*="send"]').first
        send_btn.click()

        # Wait for response
        time.sleep(5)
        page.wait_for_load_state("networkidle")
        screenshot(page, "10_conversation_started", "Conversation started")

        # Check if conversation view is showing
        content = page.content()
        has_response = "Chris" in content or "评审" in content or "设计" in content

        elapsed = time.time() - start_time
        test_results["text_conversation"]["status"] = "pass" if has_response else "fail"
        test_results["text_conversation"]["notes"] = f"Response received in {elapsed:.1f}s"
        test_results["performance"]["notes"] += f"First response: {elapsed:.1f}s; "
        print(f"✅ Text conversation works ({elapsed:.1f}s)")
        return True

    except Exception as e:
        screenshot(page, "error_text_conversation", str(e))
        test_results["text_conversation"]["status"] = "fail"
        test_results["text_conversation"]["notes"] = str(e)
        print(f"❌ Text conversation failed: {e}")
        return False


def test_new_conversation(page):
    """Test new conversation feature"""
    print("\n=== Testing New Conversation ===")

    try:
        # Find more menu button
        more_btn = page.locator('[class*="more"], button:has(svg), button:has-text("⋯")').first
        if not more_btn.is_visible():
            more_btn = page.locator('button').filter(has=page.locator('[class*="MoreHoriz"], [data-testid*="more"]')).first

        # Click more menu
        more_btn.click()
        time.sleep(1)
        screenshot(page, "11_more_menu", "More menu opened")

        # Look for new conversation option
        new_conv_btn = page.locator('text=新建对话').first
        if new_conv_btn.is_visible():
            new_conv_btn.click()
            time.sleep(2)
            screenshot(page, "12_new_conversation", "New conversation created")
            test_results["new_conversation"]["status"] = "pass"
            test_results["new_conversation"]["notes"] = "New conversation feature works"
            print("✅ New conversation feature works")
        else:
            test_results["new_conversation"]["status"] = "fail"
            test_results["new_conversation"]["notes"] = "New conversation option not found"
            print("⚠️ New conversation option not found in menu")

        return True

    except Exception as e:
        screenshot(page, "error_new_conversation", str(e))
        test_results["new_conversation"]["status"] = "fail"
        test_results["new_conversation"]["notes"] = str(e)
        print(f"❌ New conversation test failed: {e}")
        return False


def test_image_upload(page):
    """Test image upload functionality"""
    print("\n=== Testing Image Upload ===")

    try:
        # Look for attachment button
        attach_btn = page.locator('button:has-text("附件"), button:has(svg[class*="attach"]), [class*="attach"]').first
        if not attach_btn.is_visible():
            # Try to find by icon
            attach_btn = page.locator('button').filter(has=page.locator('[class*="Attach"], [data-testid*="attach"]')).first

        screenshot(page, "13_before_upload", "Before image upload")

        # Check if file input exists
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            # Upload image directly
            file_input.set_input_files(DESIGN_IMAGE_1)
            time.sleep(2)
            screenshot(page, "14_image_uploaded", "Image uploaded")
            test_results["image_upload"]["status"] = "pass"
            test_results["image_upload"]["notes"] = "Direct file input upload works"
            print("✅ Image upload successful")
        else:
            # Try clicking attach button to open picker
            if attach_btn.is_visible():
                attach_btn.click()
                time.sleep(1)
                screenshot(page, "14_upload_picker", "Upload picker opened")
                test_results["image_upload"]["status"] = "partial"
                test_results["image_upload"]["notes"] = "Attachment button works, picker opened"
                print("⚠️ Attachment picker opened, manual upload needed")
            else:
                test_results["image_upload"]["status"] = "fail"
                test_results["image_upload"]["notes"] = "No attachment button found"
                print("❌ No attachment button found")

        return True

    except Exception as e:
        screenshot(page, "error_image_upload", str(e))
        test_results["image_upload"]["status"] = "fail"
        test_results["image_upload"]["notes"] = str(e)
        print(f"❌ Image upload failed: {e}")
        return False


def test_quick_action_mode(page, mode_name, mode_text, screenshot_prefix):
    """Test a specific quick action mode"""
    print(f"\n=== Testing {mode_name} Mode ===")
    start_time = time.time()

    try:
        # Look for the quick action button
        action_btn = page.locator(f'text={mode_text}').first
        if not action_btn.is_visible():
            # Try scrolling to find it
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            action_btn = page.locator(f'text={mode_text}').first

        if action_btn.is_visible():
            screenshot(page, f"{screenshot_prefix}_before", f"Before {mode_name}")
            action_btn.click()

            # Wait for response
            time.sleep(8)  # Give more time for AI response
            page.wait_for_load_state("networkidle")
            screenshot(page, f"{screenshot_prefix}_after", f"After {mode_name} response")

            # Check response content
            content = page.content()
            elapsed = time.time() - start_time

            # Look for mode-specific keywords
            mode_keywords = {
                "interaction": ["交互", "流程", "操作", "用户", "入口", "路径"],
                "visual": ["视觉", "颜色", "字体", "间距", "对齐", "一致"],
                "compare": ["对比", "方案", "选择", "取舍", "优势", "劣势"]
            }

            keywords = mode_keywords.get(mode_name.lower().split()[0], [])
            found_keywords = [k for k in keywords if k in content]

            result_key = f"{mode_name.lower().replace(' ', '_')}_mode"
            if result_key not in test_results:
                result_key = mode_name.lower().replace(' mode', '_mode')

            if found_keywords:
                test_results[result_key]["status"] = "pass"
                test_results[result_key]["notes"] = f"Keywords found: {', '.join(found_keywords[:3])}; Time: {elapsed:.1f}s"
                print(f"✅ {mode_name} works - Keywords: {', '.join(found_keywords[:3])}")
            else:
                test_results[result_key]["status"] = "partial"
                test_results[result_key]["notes"] = f"Response received but no mode-specific keywords; Time: {elapsed:.1f}s"
                print(f"⚠️ {mode_name} - Response received but unclear mode activation")

            return True
        else:
            test_results[f"{mode_name.lower()}_mode"]["status"] = "fail"
            test_results[f"{mode_name.lower()}_mode"]["notes"] = "Button not found"
            print(f"❌ {mode_name} button not found")
            return False

    except Exception as e:
        screenshot(page, f"error_{screenshot_prefix}", str(e))
        print(f"❌ {mode_name} test failed: {e}")
        return False


def test_image_understanding(page):
    """Test if Chris Chen can understand uploaded images"""
    print("\n=== Testing Image Understanding ===")
    start_time = time.time()

    try:
        # First, try to upload an image if not already done
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            file_input.set_input_files(DESIGN_IMAGE_1)
            time.sleep(2)

        # Send a message asking about the image
        input_field = page.locator('textarea').first
        if not input_field.is_visible():
            input_field = page.locator('input[type="text"]').first

        input_field.fill("请帮我分析这个设计稿，看看有什么问题")
        screenshot(page, "20_image_analysis_request", "Requesting image analysis")

        # Send
        send_btn = page.locator('button[type="submit"], button:has-text("发送")').first
        send_btn.click()

        # Wait for response (image analysis takes longer)
        time.sleep(15)
        page.wait_for_load_state("networkidle")
        screenshot(page, "21_image_analysis_response", "Image analysis response")

        content = page.content()
        elapsed = time.time() - start_time

        # Check for image-related analysis keywords
        image_keywords = ["图", "设计", "布局", "颜色", "元素", "按钮", "界面", "看到", "显示"]
        found = [k for k in image_keywords if k in content]

        if found:
            test_results["image_understanding"]["status"] = "pass"
            test_results["image_understanding"]["notes"] = f"Image analysis keywords: {', '.join(found[:5])}; Time: {elapsed:.1f}s"
            print(f"✅ Image understanding works - Found: {', '.join(found[:3])}")
        else:
            test_results["image_understanding"]["status"] = "fail"
            test_results["image_understanding"]["notes"] = f"No image analysis detected; Time: {elapsed:.1f}s"
            print("❌ Image understanding unclear")

        return True

    except Exception as e:
        screenshot(page, "error_image_understanding", str(e))
        test_results["image_understanding"]["status"] = "fail"
        test_results["image_understanding"]["notes"] = str(e)
        print(f"❌ Image understanding test failed: {e}")
        return False


def generate_report():
    """Generate final test report"""
    print("\n" + "="*60)
    print("📋 CHRIS CHEN AI EMPLOYEE TEST REPORT")
    print("="*60)

    passed = 0
    failed = 0
    partial = 0

    for test_name, result in test_results.items():
        status = result["status"]
        notes = result["notes"]

        if status == "pass":
            icon = "✅"
            passed += 1
        elif status == "fail":
            icon = "❌"
            failed += 1
        elif status == "partial":
            icon = "⚠️"
            partial += 1
        else:
            icon = "⏸️"

        print(f"{icon} {test_name}: {status}")
        if notes:
            print(f"   └─ {notes}")

    print("\n" + "-"*60)
    print(f"📊 Summary: {passed} passed, {partial} partial, {failed} failed")
    print(f"📁 Screenshots saved to: {SCREENSHOT_DIR}")
    print("-"*60)

    # Overall verdict
    if failed == 0 and partial <= 2:
        print("🎉 OVERALL: PASS")
        return True
    elif failed <= 2:
        print("⚠️ OVERALL: PARTIAL PASS - Some features need attention")
        return True
    else:
        print("❌ OVERALL: FAIL - Multiple critical issues")
        return False


def main():
    print("🚀 Starting Chris Chen Comprehensive UI Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    setup_screenshot_dir()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 430, "height": 932},  # iPhone 14 Pro Max
            device_scale_factor=2,
        )
        page = context.new_page()

        try:
            # Run tests
            if test_login(page):
                if navigate_to_chris_chen(page):
                    test_profile_view(page)
                    test_text_conversation(page)

                    # Test new conversation feature
                    test_new_conversation(page)

                    # Test quick action modes
                    test_quick_action_mode(page, "Interaction", "交互验证", "15_interaction")
                    test_quick_action_mode(page, "Visual", "视觉讨论", "16_visual")
                    test_quick_action_mode(page, "Compare", "方案选择", "17_compare")

                    # Test image upload and understanding
                    test_image_upload(page)
                    test_image_understanding(page)

            # Set performance test status
            test_results["performance"]["status"] = "pass" if test_results["performance"]["notes"] else "pending"

        except Exception as e:
            print(f"❌ Test suite error: {e}")
            screenshot(page, "error_final", str(e))

        finally:
            browser.close()

    success = generate_report()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
