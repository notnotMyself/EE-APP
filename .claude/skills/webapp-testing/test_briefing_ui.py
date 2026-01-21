#!/usr/bin/env python3
"""
Test script for AI Employee Briefing System UI
Uses mouse coordinates for Flutter web canvas-based rendering
"""

import time
from playwright.sync_api import sync_playwright

TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
BASE_URL = "http://localhost:5000"

def test_briefing_ui():
    """Test login and briefings UI"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Console logging
        page.on("console", lambda msg: print(f"[Console] {msg.text}") if "error" in msg.text.lower() else None)

        print("=" * 60)
        print("STEP 1: Navigate to app")
        print("=" * 60)

        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(5)  # Flutter initialization

        page.screenshot(path="/tmp/b_01_initial.png")
        print("Screenshot: /tmp/b_01_initial.png")

        print("\n" + "=" * 60)
        print("STEP 2: Fill login form using mouse coordinates")
        print("=" * 60)

        # Click on email field area (coordinates from screenshot)
        page.mouse.click(640, 453)
        time.sleep(0.5)

        # Type email
        page.keyboard.type(TEST_EMAIL, delay=50)
        time.sleep(0.5)

        page.screenshot(path="/tmp/b_02_email.png")
        print("Screenshot: /tmp/b_02_email.png")

        # Click on password field
        page.mouse.click(640, 517)
        time.sleep(0.5)
        page.keyboard.type(TEST_PASSWORD, delay=50)
        time.sleep(0.5)

        page.screenshot(path="/tmp/b_03_password.png")
        print("Screenshot: /tmp/b_03_password.png")

        print("\n" + "=" * 60)
        print("STEP 3: Submit login")
        print("=" * 60)

        # Click the login button
        page.mouse.click(640, 582)
        print("Clicked login button, waiting for response...")

        time.sleep(8)
        page.wait_for_load_state("networkidle")

        page.screenshot(path="/tmp/b_04_after_login.png")
        print("Screenshot: /tmp/b_04_after_login.png")

        # Check URL
        current_url = page.url
        print(f"Current URL: {current_url}")

        if "/login" not in current_url:
            print("✅ Login successful!")

            print("\n" + "=" * 60)
            print("STEP 4: Check main page content")
            print("=" * 60)

            time.sleep(3)
            page.screenshot(path="/tmp/b_05_main.png")
            print("Screenshot: /tmp/b_05_main.png")

            # Navigate through the app
            # Click on bottom nav items if present

            # Check for briefings by clicking on different sections
            for i, y_pos in enumerate([700, 750]):  # Bottom nav approximate positions
                page.mouse.click(320, y_pos)
                time.sleep(2)
                page.screenshot(path=f"/tmp/b_06_nav_{i}.png")
                print(f"Screenshot: /tmp/b_06_nav_{i}.png")

        else:
            print("⚠️ Still on login page")

        # Final screenshot
        page.screenshot(path="/tmp/b_07_final.png", full_page=True)
        print("\nFinal screenshot: /tmp/b_07_final.png")

        browser.close()

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

        return True

if __name__ == "__main__":
    test_briefing_ui()
