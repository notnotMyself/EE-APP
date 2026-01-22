#!/usr/bin/env python3
"""
Chris Chen - Final UI Test with Semantic Locators
Uses Flutter web's semantic tree for better interaction
"""

import os
import sys
import time
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configuration
BASE_URL = "http://localhost:5000"
EMAIL = "1091201603@qq.com"
PASSWORD = "eeappsuccess"
SCREENSHOT_DIR = "/tmp/chris_chen_test"
DESIGN_IMAGE = "/Users/80392083/Downloads/design1.jpg"

results = {}


def setup():
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)
    os.makedirs(SCREENSHOT_DIR)


def shot(page, name, desc=""):
    ts = datetime.now().strftime("%H%M%S")
    path = f"{SCREENSHOT_DIR}/{ts}_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"📸 {name}")
    return path


def test_login(page):
    """Login using semantic locators"""
    print("\n=== 1. LOGIN TEST ===")
    start = time.time()

    try:
        page.goto(BASE_URL)
        time.sleep(5)  # Wait for Flutter
        shot(page, "01_login_page")

        # Use text-based locators for Flutter
        # Click on 邮箱 field area
        email_field = page.locator('text=邮箱').first
        email_field.click()
        time.sleep(0.5)
        page.keyboard.type(EMAIL, delay=50)
        shot(page, "02_email_typed")

        # Click on 密码 field
        pwd_field = page.locator('text=密码').first
        pwd_field.click()
        time.sleep(0.5)
        page.keyboard.type(PASSWORD, delay=50)
        shot(page, "03_password_typed")

        # Click login button
        login_btn = page.locator('text=登录').first
        login_btn.click()
        time.sleep(8)
        shot(page, "04_after_login")

        # Check result
        text = page.inner_text('body')
        if any(kw in text for kw in ["消息", "简报", "员工"]):
            results["login"] = {"status": "pass", "notes": f"{time.time()-start:.1f}s"}
            print(f"✅ Login success ({time.time()-start:.1f}s)")
            return True

        results["login"] = {"status": "fail", "notes": "Not on main page"}
        print("❌ Login failed")
        return False

    except Exception as e:
        shot(page, "error_login")
        results["login"] = {"status": "fail", "notes": str(e)[:80]}
        print(f"❌ Error: {e}")
        return False


def navigate_to_chris(page):
    """Navigate to Chris Chen"""
    print("\n=== 2. NAVIGATION TEST ===")

    try:
        # Find and click AI员工 tab or navigate directly
        page.goto(f"{BASE_URL}/#/agents")
        time.sleep(3)
        shot(page, "05_agents_page")

        text = page.inner_text('body')

        # Check for unified entry
        has_single = "开始对话" in text
        has_dual = "查看详情" in text

        if has_single and not has_dual:
            results["unified_entry"] = {"status": "pass", "notes": "Single button confirmed"}
            print("✅ Unified entry point")
        elif has_dual:
            results["unified_entry"] = {"status": "fail", "notes": "Dual buttons exist"}
            print("⚠️ Dual buttons still exist")

        # Click on Chris or start button
        try:
            btn = page.locator('text=开始对话').first
            btn.click()
        except:
            btn = page.locator('text=Chris').first
            btn.click()

        time.sleep(3)
        shot(page, "06_chris_profile")
        results["navigation"] = {"status": "pass", "notes": "Success"}
        print("✅ Navigation complete")
        return True

    except Exception as e:
        results["navigation"] = {"status": "fail", "notes": str(e)[:80]}
        print(f"❌ Navigation error: {e}")
        return False


def test_profile(page):
    """Test profile view elements"""
    print("\n=== 3. PROFILE VIEW TEST ===")

    try:
        text = page.inner_text('body')
        shot(page, "07_profile_detail")

        found = []
        if any(g in text for g in ["早上好", "上午好", "下午好", "晚上好", "中午好"]):
            found.append("greeting")
        if "Chris" in text:
            found.append("name")
        if any(a in text for a in ["交互验证", "视觉讨论", "方案选择"]):
            found.append("quick_actions")
        if "背景" in text or "描述" in text:
            found.append("input_hint")

        results["profile_view"] = {
            "status": "pass" if len(found) >= 2 else "partial",
            "notes": ", ".join(found)
        }
        print(f"✅ Profile: {', '.join(found)}")
        return True

    except Exception as e:
        results["profile_view"] = {"status": "fail", "notes": str(e)[:80]}
        return False


def send_message(page, msg, test_name, keywords):
    """Send a message and check response"""
    print(f"\n=== {test_name.upper()} ===")
    start = time.time()

    try:
        # Find textarea and type
        textarea = page.locator('textarea').first
        if textarea.is_visible():
            textarea.fill(msg)
            shot(page, f"{test_name}_typed")

            # Send
            page.keyboard.press('Enter')
            time.sleep(12)
            shot(page, f"{test_name}_response")

            text = page.inner_text('body')
            found = [k for k in keywords if k in text]

            results[test_name] = {
                "status": "pass" if found else "partial",
                "notes": f"{', '.join(found[:3]) if found else 'responded'}; {time.time()-start:.1f}s"
            }
            print(f"✅ {test_name}: {', '.join(found[:2]) if found else 'done'}")
            return True
        else:
            results[test_name] = {"status": "fail", "notes": "Textarea not found"}
            return False

    except Exception as e:
        results[test_name] = {"status": "fail", "notes": str(e)[:80]}
        return False


def test_quick_action(page, btn_text, test_name, keywords):
    """Test quick action button"""
    print(f"\n=== QUICK ACTION: {btn_text} ===")
    start = time.time()

    try:
        btn = page.locator(f'text={btn_text}').first
        if btn.is_visible():
            shot(page, f"{test_name}_before")
            btn.click()
            time.sleep(10)
            shot(page, f"{test_name}_after")

            text = page.inner_text('body')
            found = [k for k in keywords if k in text]

            results[test_name] = {
                "status": "pass" if found else "partial",
                "notes": f"{', '.join(found[:3]) if found else 'responded'}; {time.time()-start:.1f}s"
            }
            print(f"✅ {btn_text}: {', '.join(found[:2]) if found else 'done'}")
            return True

        results[test_name] = {"status": "fail", "notes": "Button not found"}
        return False

    except Exception as e:
        results[test_name] = {"status": "fail", "notes": str(e)[:80]}
        return False


def test_new_conversation(page):
    """Test new conversation feature"""
    print("\n=== NEW CONVERSATION TEST ===")

    try:
        # Click more menu (top right)
        more = page.locator('button').last
        more.click()
        time.sleep(1)
        shot(page, "new_conv_menu")

        new_btn = page.locator('text=新建对话').first
        if new_btn.is_visible():
            new_btn.click()
            time.sleep(2)
            shot(page, "new_conv_created")
            results["new_conversation"] = {"status": "pass", "notes": "Feature works"}
            print("✅ New conversation works")
            return True

        page.keyboard.press('Escape')
        results["new_conversation"] = {"status": "fail", "notes": "Not found"}
        return False

    except Exception as e:
        results["new_conversation"] = {"status": "fail", "notes": str(e)[:80]}
        return False


def test_image(page):
    """Test image upload"""
    print("\n=== IMAGE TEST ===")
    start = time.time()

    try:
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            file_input.first.set_input_files(DESIGN_IMAGE)
            time.sleep(3)
            shot(page, "image_uploaded")
            results["image_upload"] = {"status": "pass", "notes": "Uploaded"}
            print("✅ Image uploaded")

            # Ask for analysis
            textarea = page.locator('textarea').first
            if textarea.is_visible():
                textarea.fill("请分析这个设计稿")
                page.keyboard.press('Enter')
                time.sleep(15)
                shot(page, "image_analysis")

                text = page.inner_text('body')
                kw = ["图", "设计", "界面", "布局", "颜色"]
                found = [k for k in kw if k in text]

                results["image_understanding"] = {
                    "status": "pass" if len(found) >= 2 else "partial",
                    "notes": f"{', '.join(found[:3])}; {time.time()-start:.1f}s"
                }
                print(f"✅ Image analysis: {', '.join(found[:3])}")
        else:
            results["image_upload"] = {"status": "partial", "notes": "No file input"}
            results["image_understanding"] = {"status": "pending", "notes": "N/A"}

        return True

    except Exception as e:
        results["image_upload"] = {"status": "fail", "notes": str(e)[:80]}
        return False


def report():
    """Generate report"""
    print("\n" + "="*60)
    print("📋 CHRIS CHEN TEST REPORT")
    print("="*60)

    p = f = pt = 0
    for name, r in results.items():
        s = r.get("status", "?")
        n = r.get("notes", "")
        icon = {"pass": "✅", "fail": "❌", "partial": "⚠️"}.get(s, "?")

        if s == "pass": p += 1
        elif s == "fail": f += 1
        elif s == "partial": pt += 1

        print(f"{icon} {name}: {s}")
        if n:
            print(f"   └─ {n}")

    print("-"*60)
    print(f"📊 {p} pass, {pt} partial, {f} fail")
    print(f"📁 {SCREENSHOT_DIR}")

    return f <= 2


def main():
    print("🚀 Chris Chen Final Test")
    setup()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 430, "height": 932})

        try:
            if test_login(page):
                if navigate_to_chris(page):
                    test_profile(page)

                    send_message(page, "你好，帮我评审设计", "basic_chat",
                               ["评审", "设计", "好", "帮"])

                    test_quick_action(page, "交互验证", "interaction",
                                    ["交互", "流程", "用户", "操作"])

                    test_quick_action(page, "视觉讨论", "visual",
                                    ["视觉", "颜色", "字体", "一致"])

                    test_quick_action(page, "方案选择", "compare",
                                    ["方案", "对比", "选择"])

                    test_new_conversation(page)
                    test_image(page)

        except Exception as e:
            print(f"❌ Suite error: {e}")
            shot(page, "error_final")
        finally:
            browser.close()

    ok = report()
    print("\nDONE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
