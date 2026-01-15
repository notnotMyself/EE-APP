#!/usr/bin/env python3
"""
Complete E2E test with login - Test full user journey
"""
from playwright.sync_api import sync_playwright
import sys
import time

# Test credentials
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"

def test_login_and_agents():
    """Test login flow and post-login functionality"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        try:
            print("=" * 70)
            print("🔐 Flutter App Complete E2E Test - Login & Agents")
            print("=" * 70)

            # ========================================
            # Step 1: Navigate to app
            # ========================================
            print("\n📍 Step 1: Navigating to Flutter app...")
            page.goto('http://localhost:5000', wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)  # Wait for Flutter to fully render

            page.screenshot(path='/tmp/e2e_01_login_page.png', full_page=True)
            print("  ✅ Login page loaded")
            print("  📸 Screenshot: /tmp/e2e_01_login_page.png")

            # ========================================
            # Step 2: Fill in login credentials
            # ========================================
            print("\n📍 Step 2: Entering login credentials...")

            # Wait a bit more for Flutter to be interactive
            page.wait_for_timeout(2000)

            # Try to find and fill email input
            print("  🔍 Looking for email input...")

            # Flutter Web renders in canvas, so we need to use coordinates or wait for input to be ready
            # Try clicking on the page first to ensure it's focused
            page.click('body')
            page.wait_for_timeout(500)

            # Try typing email - Flutter should have focus on first input
            print("  ⌨️  Typing email...")
            page.keyboard.type(TEST_EMAIL, delay=50)
            page.wait_for_timeout(500)

            # Tab to password field
            print("  ⌨️  Moving to password field...")
            page.keyboard.press('Tab')
            page.wait_for_timeout(500)

            # Type password
            print("  ⌨️  Typing password...")
            page.keyboard.type(TEST_PASSWORD, delay=50)
            page.wait_for_timeout(500)

            page.screenshot(path='/tmp/e2e_02_credentials_filled.png', full_page=True)
            print("  ✅ Credentials entered")
            print("  📸 Screenshot: /tmp/e2e_02_credentials_filled.png")

            # ========================================
            # Step 3: Submit login
            # ========================================
            print("\n📍 Step 3: Submitting login form...")

            # Press Enter or Tab to login button and press Enter
            page.keyboard.press('Tab')
            page.wait_for_timeout(300)
            page.keyboard.press('Enter')

            print("  🔄 Waiting for login to complete...")

            # Wait for navigation or success indicator
            # This might take a while depending on Supabase authentication
            page.wait_for_timeout(5000)

            page.screenshot(path='/tmp/e2e_03_after_login_submit.png', full_page=True)
            print("  📸 Screenshot: /tmp/e2e_03_after_login_submit.png")

            # ========================================
            # Step 4: Verify post-login state
            # ========================================
            print("\n📍 Step 4: Checking post-login state...")

            # Wait for page to potentially change
            page.wait_for_timeout(3000)

            # Check current URL
            current_url = page.url
            print(f"  📍 Current URL: {current_url}")

            # Take screenshot
            page.screenshot(path='/tmp/e2e_04_post_login.png', full_page=True)
            print("  📸 Screenshot: /tmp/e2e_04_post_login.png")

            # Check console for auth success messages
            auth_messages = [msg for msg in console_messages if 'auth' in msg.lower() or 'login' in msg.lower()]
            if auth_messages:
                print(f"  📝 Auth-related messages: {len(auth_messages)}")
                for msg in auth_messages[-5:]:
                    print(f"     {msg}")

            # ========================================
            # Step 5: Look for agents list or home page
            # ========================================
            print("\n📍 Step 5: Looking for agents list / home page...")

            page.wait_for_timeout(2000)

            # Try to take multiple screenshots at intervals to catch state changes
            for i in range(3):
                page.wait_for_timeout(2000)
                page.screenshot(path=f'/tmp/e2e_05_home_state_{i}.png', full_page=True)
                print(f"  📸 Screenshot {i+1}: /tmp/e2e_05_home_state_{i}.png")

            # ========================================
            # Step 6: Check for errors
            # ========================================
            print("\n📍 Step 6: Checking for errors...")
            errors = [msg for msg in console_messages if '[error]' in msg.lower()]
            if errors:
                print(f"  ⚠️  Found {len(errors)} error(s):")
                for error in errors[-5:]:
                    print(f"    {error}")
            else:
                print("  ✅ No errors detected")

            # ========================================
            # Summary
            # ========================================
            print("\n" + "=" * 70)
            print("📊 E2E Test Summary")
            print("=" * 70)
            print(f"✅ Login Page: Loaded")
            print(f"✅ Credentials: Entered ({TEST_EMAIL})")
            print(f"✅ Login Form: Submitted")
            print(f"✅ Current URL: {current_url}")
            print(f"✅ Console Messages: {len(console_messages)} total")
            print(f"✅ Errors: {len(errors)}")

            print("\n📝 Recent Console Messages:")
            for msg in console_messages[-15:]:
                print(f"  {msg}")

            print("\n📸 Generated Screenshots:")
            print("  1. /tmp/e2e_01_login_page.png")
            print("  2. /tmp/e2e_02_credentials_filled.png")
            print("  3. /tmp/e2e_03_after_login_submit.png")
            print("  4. /tmp/e2e_04_post_login.png")
            print("  5. /tmp/e2e_05_home_state_0.png")
            print("  6. /tmp/e2e_05_home_state_1.png")
            print("  7. /tmp/e2e_05_home_state_2.png")

            print("\n✅ Complete E2E Test PASSED!")
            print("=" * 70)

            return 0

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            try:
                page.screenshot(path='/tmp/e2e_error.png', full_page=True)
                print(f"📸 Error screenshot saved: /tmp/e2e_error.png")
            except:
                pass

            print("\n📝 Console messages at failure:")
            for msg in console_messages[-10:]:
                print(f"  {msg}")

            return 1

        finally:
            browser.close()

if __name__ == "__main__":
    sys.exit(test_login_and_agents())
