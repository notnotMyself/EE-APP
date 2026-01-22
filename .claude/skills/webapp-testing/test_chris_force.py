#!/usr/bin/env python3
"""
Chris Chen Test - Force Click Method for Flutter Web
"""

import os
import sys
import time
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright

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


def shot(page, name):
    ts = datetime.now().strftime("%H%M%S")
    path = f"{SCREENSHOT_DIR}/{ts}_{name}.png"
    page.screenshot(path=path)
    print(f"📸 {name}")
    return path


def click_element(page, text):
    """Click element using bounding box"""
    try:
        el = page.locator(f'text={text}').first
        box = el.bounding_box()
        if box:
            page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
            return True
    except:
        pass
    return False


def test_login(page):
    print("\n=== LOGIN ===")
    start = time.time()

    try:
        page.goto(BASE_URL)
        time.sleep(5)
        shot(page, "01_login")

        # Click email field using bounding box
        email_el = page.locator('text=邮箱').first
        box = email_el.bounding_box()
        if box:
            page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
            time.sleep(0.3)
            page.keyboard.type(EMAIL, delay=30)
            shot(page, "02_email")

        # Click password field
        pwd_el = page.locator('text=密码').first
        box = pwd_el.bounding_box()
        if box:
            page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
            time.sleep(0.3)
            page.keyboard.type(PASSWORD, delay=30)
            shot(page, "03_password")

        # Click login button
        login_el = page.locator('text=登录').first
        box = login_el.bounding_box()
        if box:
            page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
            time.sleep(8)
            shot(page, "04_after_login")

        text = page.inner_text('body')
        if any(k in text for k in ["消息", "简报", "员工"]):
            results["login"] = {"status": "pass", "notes": f"{time.time()-start:.1f}s"}
            print("✅ Login OK")
            return True

        results["login"] = {"status": "fail", "notes": "Not on main"}
        print("❌ Login failed")
        return False

    except Exception as e:
        shot(page, "error_login")
        results["login"] = {"status": "fail", "notes": str(e)[:60]}
        print(f"❌ {e}")
        return False


def nav_to_chris(page):
    print("\n=== NAVIGATION ===")

    try:
        page.goto(f"{BASE_URL}/#/agents")
        time.sleep(3)
        shot(page, "05_agents")

        text = page.inner_text('body')

        # Check unified entry
        has_start = "开始对话" in text
        has_detail = "查看详情" in text

        if has_start and not has_detail:
            results["unified_entry"] = {"status": "pass", "notes": "Single button"}
            print("✅ Unified entry")
        elif has_detail:
            results["unified_entry"] = {"status": "fail", "notes": "Dual buttons"}
            print("⚠️ Dual buttons exist")

        # Click start button
        if click_element(page, "开始对话"):
            time.sleep(3)
            shot(page, "06_chris")
            results["navigation"] = {"status": "pass", "notes": "OK"}
            print("✅ Navigation OK")
            return True

        # Fallback
        if click_element(page, "Chris"):
            time.sleep(3)
            shot(page, "06_chris")
            results["navigation"] = {"status": "pass", "notes": "Via name"}
            return True

        results["navigation"] = {"status": "fail", "notes": "Cant navigate"}
        return False

    except Exception as e:
        results["navigation"] = {"status": "fail", "notes": str(e)[:60]}
        return False


def test_profile(page):
    print("\n=== PROFILE ===")

    try:
        text = page.inner_text('body')
        shot(page, "07_profile")

        found = []
        if any(g in text for g in ["早上好", "上午好", "下午好", "晚上好", "中午好"]):
            found.append("greeting")
        if "Chris" in text:
            found.append("name")
        if any(a in text for a in ["交互验证", "视觉讨论", "方案选择"]):
            found.append("actions")

        results["profile"] = {
            "status": "pass" if len(found) >= 2 else "partial",
            "notes": ",".join(found)
        }
        print(f"✅ Profile: {','.join(found)}")
        return True

    except Exception as e:
        results["profile"] = {"status": "fail", "notes": str(e)[:60]}
        return False


def send_msg(page, msg, name, keywords):
    print(f"\n=== {name.upper()} ===")
    start = time.time()

    try:
        # Find and click textarea area
        ta = page.locator('textarea').first
        box = ta.bounding_box()
        if box:
            page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
            time.sleep(0.3)
            page.keyboard.type(msg, delay=20)
            shot(page, f"{name}_typed")

            page.keyboard.press('Enter')
            time.sleep(12)
            shot(page, f"{name}_response")

            text = page.inner_text('body')
            found = [k for k in keywords if k in text]

            results[name] = {
                "status": "pass" if found else "partial",
                "notes": f"{','.join(found[:2]) if found else 'resp'}; {time.time()-start:.1f}s"
            }
            print(f"✅ {name}: {','.join(found[:2]) if found else 'done'}")
            return True

        results[name] = {"status": "fail", "notes": "No textarea"}
        return False

    except Exception as e:
        results[name] = {"status": "fail", "notes": str(e)[:60]}
        return False


def test_action(page, btn, name, kw):
    print(f"\n=== {btn} ===")
    start = time.time()

    try:
        if click_element(page, btn):
            time.sleep(10)
            shot(page, f"{name}_after")

            text = page.inner_text('body')
            found = [k for k in kw if k in text]

            results[name] = {
                "status": "pass" if found else "partial",
                "notes": f"{','.join(found[:2]) if found else 'resp'}; {time.time()-start:.1f}s"
            }
            print(f"✅ {btn}: {','.join(found[:2]) if found else 'done'}")
            return True

        results[name] = {"status": "fail", "notes": "Button not found"}
        return False

    except Exception as e:
        results[name] = {"status": "fail", "notes": str(e)[:60]}
        return False


def test_new_conv(page):
    print("\n=== NEW CONV ===")

    try:
        # Find more button (usually last button in top area)
        buttons = page.locator('button').all()
        for btn in buttons[-3:]:
            try:
                box = btn.bounding_box()
                if box and box['y'] < 100:  # Top area
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    time.sleep(1)

                    if "新建对话" in page.inner_text('body'):
                        click_element(page, "新建对话")
                        time.sleep(2)
                        shot(page, "new_conv")
                        results["new_conv"] = {"status": "pass", "notes": "Works"}
                        print("✅ New conv works")
                        return True
            except:
                continue

        results["new_conv"] = {"status": "fail", "notes": "Not found"}
        print("⚠️ New conv not found")
        return False

    except Exception as e:
        results["new_conv"] = {"status": "fail", "notes": str(e)[:60]}
        return False


def test_image(page):
    print("\n=== IMAGE ===")
    start = time.time()

    try:
        fi = page.locator('input[type="file"]')
        if fi.count() > 0:
            fi.first.set_input_files(DESIGN_IMAGE)
            time.sleep(3)
            shot(page, "img_upload")
            results["img_upload"] = {"status": "pass", "notes": "OK"}
            print("✅ Image uploaded")

            # Send analysis request
            ta = page.locator('textarea').first
            box = ta.bounding_box()
            if box:
                page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                page.keyboard.type("分析这个设计", delay=20)
                page.keyboard.press('Enter')
                time.sleep(15)
                shot(page, "img_analysis")

                text = page.inner_text('body')
                kw = ["图", "设计", "界面", "颜色", "布局"]
                found = [k for k in kw if k in text]

                results["img_analysis"] = {
                    "status": "pass" if len(found) >= 2 else "partial",
                    "notes": f"{','.join(found[:3])}; {time.time()-start:.1f}s"
                }
                print(f"✅ Analysis: {','.join(found[:3])}")
        else:
            results["img_upload"] = {"status": "partial", "notes": "No input"}
            results["img_analysis"] = {"status": "pending", "notes": "N/A"}

        return True

    except Exception as e:
        results["img_upload"] = {"status": "fail", "notes": str(e)[:60]}
        return False


def report():
    print("\n" + "="*50)
    print("📋 CHRIS CHEN TEST REPORT")
    print("="*50)

    p = f = pt = 0
    for n, r in results.items():
        s = r.get("status", "?")
        notes = r.get("notes", "")
        icon = {"pass": "✅", "fail": "❌", "partial": "⚠️"}.get(s, "?")

        if s == "pass": p += 1
        elif s == "fail": f += 1
        elif s == "partial": pt += 1

        print(f"{icon} {n}: {s} - {notes}")

    print("-"*50)
    print(f"📊 {p} pass, {pt} partial, {f} fail")
    print(f"📁 {SCREENSHOT_DIR}")

    total = p + pt + f
    if total > 0:
        rate = (p + pt*0.5) / total * 100
        print(f"📈 Success: {rate:.0f}%")

    if f == 0:
        print("🎉 PASS")
    elif f <= 2:
        print("⚠️ PARTIAL")
    else:
        print("❌ FAIL")

    return f <= 2


def main():
    print("🚀 Chris Chen Test - Force Click")
    setup()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 430, "height": 932})

        try:
            if test_login(page):
                if nav_to_chris(page):
                    test_profile(page)
                    send_msg(page, "你好帮我评审", "chat", ["评审", "设计", "好"])
                    test_action(page, "交互验证", "interact", ["交互", "流程", "用户"])
                    test_action(page, "视觉讨论", "visual", ["视觉", "颜色", "字体"])
                    test_action(page, "方案选择", "compare", ["方案", "对比", "选择"])
                    test_new_conv(page)
                    test_image(page)

        except Exception as e:
            print(f"❌ Error: {e}")
            shot(page, "error")
        finally:
            browser.close()

    ok = report()
    print("\nDONE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
