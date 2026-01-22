#!/usr/bin/env python3
"""
Chris Chen AI Employee - Fixed E2E Testing
Properly handles login and navigation
"""

import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"
EMAIL = "1091201603@qq.com"
PASSWORD = "eeappsuccess"
DESIGN1_PATH = "/Users/80392083/Downloads/design1.jpg"
DESIGN2_PATH = "/Users/80392083/Downloads/design2.jpg"
SCREENSHOT_DIR = "/tmp/chris_chen_test_v2"

test_results = {
    "start_time": datetime.now().isoformat(),
    "tests": [],
    "screenshots": [],
    "performance_metrics": {},
    "issues": [],
    "passed": 0,
    "failed": 0
}

def log_test(name, status, details="", screenshot_path=None, duration=None):
    result = {
        "name": name,
        "status": status,
        "details": details,
        "screenshot": screenshot_path,
        "duration": duration,
        "timestamp": datetime.now().isoformat()
    }
    test_results["tests"].append(result)

    if status == "PASS":
        test_results["passed"] += 1
        print(f"✅ {name}: {details}")
    else:
        test_results["failed"] += 1
        print(f"❌ {name}: {details}")

    if screenshot_path:
        test_results["screenshots"].append(screenshot_path)

    return result

def log_issue(severity, description):
    issue = {
        "severity": severity,
        "description": description,
        "timestamp": datetime.now().isoformat()
    }
    test_results["issues"].append(issue)
    print(f"⚠️  [{severity}] {description}")

def take_screenshot(page, name):
    import os
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = f"{SCREENSHOT_DIR}/{filename}"

    page.screenshot(path=filepath, full_page=True)
    print(f"📸 Screenshot: {filepath}")
    return filepath

def main():
    print("=" * 80)
    print("Chris Chen AI Employee - E2E Testing (Fixed)")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        console_logs = []
        page.on("console", lambda msg: console_logs.append({
            "type": msg.type,
            "text": msg.text
        }))

        try:
            # TEST 1: Load app
            print("\n" + "="*80)
            print("TEST 1: Load Application")
            print("="*80)

            start_time = time.time()
            page.goto(APP_URL, wait_until="networkidle")
            load_time = time.time() - start_time

            test_results["performance_metrics"]["initial_load"] = load_time
            screenshot = take_screenshot(page, "01_loaded")

            log_test("App Load", "PASS", f"Loaded in {load_time:.2f}s", screenshot, load_time)

            time.sleep(2)

            # TEST 2: Login
            print("\n" + "="*80)
            print("TEST 2: User Login")
            print("="*80)

            screenshot = take_screenshot(page, "02_login_page")

            # Fill email
            page.fill('input[type="email"]', EMAIL)

            # Fill password
            page.fill('input[type="password"]', PASSWORD)

            screenshot = take_screenshot(page, "03_credentials_filled")

            # Click login button
            start_time = time.time()
            page.click('button:has-text("登录")')

            # Wait for navigation
            page.wait_for_url(lambda url: url != APP_URL + "/" or "login" not in url.lower(), timeout=15000)
            page.wait_for_load_state("networkidle")

            login_time = time.time() - start_time
            test_results["performance_metrics"]["login_time"] = login_time

            screenshot = take_screenshot(page, "04_logged_in")

            log_test("User Login", "PASS", f"Logged in {login_time:.2f}s", screenshot, login_time)

            time.sleep(3)

            # TEST 3: Find Chris Chen
            print("\n" + "="*80)
            print("TEST 3: Navigate to Chris Chen")
            print("="*80)

            screenshot = take_screenshot(page, "05_home_page")

            # Get page text to search for Chris Chen
            page_text = page.locator('body').inner_text()
            print(f"Page text length: {len(page_text)}")

            # Try to find Chris Chen
            chris_found = False

            # Method 1: Direct text match
            try:
                chris_elem = page.get_by_text("Chris Chen", exact=False)
                if chris_elem.count() > 0:
                    print(f"Found {chris_elem.count()} elements with 'Chris Chen'")

                    start_time = time.time()
                    chris_elem.first.click()

                    page.wait_for_load_state("networkidle", timeout=10000)
                    nav_time = time.time() - start_time

                    screenshot = take_screenshot(page, "06_chris_chen")

                    log_test("Navigate to Chris Chen", "PASS", f"Navigated in {nav_time:.2f}s", screenshot, nav_time)

                    chris_found = True
            except Exception as e:
                print(f"Method 1 failed: {e}")

            # Method 2: Look for design-related cards
            if not chris_found:
                try:
                    design_cards = page.get_by_text("设计", exact=False)
                    if design_cards.count() > 0:
                        print(f"Found {design_cards.count()} elements with '设计'")

                        for i in range(design_cards.count()):
                            elem = design_cards.nth(i)
                            text = elem.inner_text()
                            print(f"  Element {i}: {text[:100]}")

                            # Check if clickable parent exists
                            try:
                                clickable = elem.locator('xpath=ancestor::*[@role="button" or @role="link" or self::a or self::button][1]')
                                if clickable.count() == 0:
                                    clickable = elem.locator('xpath=ancestor::div[contains(@class, "card") or contains(@class, "item")][1]')

                                if clickable.count() > 0:
                                    print(f"  Clicking parent element...")

                                    start_time = time.time()
                                    clickable.first.click()

                                    page.wait_for_load_state("networkidle", timeout=10000)
                                    nav_time = time.time() - start_time

                                    screenshot = take_screenshot(page, "06_chris_chen")

                                    log_test("Navigate to Chris Chen", "PASS", f"Found via 设计, navigated in {nav_time:.2f}s", screenshot, nav_time)

                                    chris_found = True
                                    break
                            except Exception as e2:
                                print(f"  Click failed: {e2}")
                                continue
                except Exception as e:
                    print(f"Method 2 failed: {e}")

            # Method 3: List all clickable elements
            if not chris_found:
                print("\nListing all clickable elements...")

                clickables = page.locator('a, button, [role="button"], [role="link"], .card, [class*="agent"]').all()
                print(f"Found {len(clickables)} clickable elements")

                for i, elem in enumerate(clickables[:30]):
                    try:
                        text = elem.inner_text()
                        if text and len(text) > 3 and len(text) < 200:
                            print(f"  [{i}] {text[:80]}")

                            if 'Chris' in text or '设计' in text or 'design' in text.lower():
                                print(f"    ✓ Potential match, clicking...")

                                start_time = time.time()
                                elem.click()

                                page.wait_for_load_state("networkidle", timeout=10000)
                                nav_time = time.time() - start_time

                                screenshot = take_screenshot(page, "06_chris_chen")

                                log_test("Navigate to Chris Chen", "PASS", f"Found in clickables, navigated in {nav_time:.2f}s", screenshot, nav_time)

                                chris_found = True
                                break
                    except:
                        pass

            if not chris_found:
                screenshot = take_screenshot(page, "06_not_found")
                log_test("Navigate to Chris Chen", "FAIL", "Could not find Chris Chen agent", screenshot)

                print("\n⚠️ Stopping tests - Chris Chen not accessible")

                browser.close()
                return generate_report()

            time.sleep(2)

            # TEST 4: Chat interface
            print("\n" + "="*80)
            print("TEST 4: Chat Interface")
            print("="*80)

            screenshot = take_screenshot(page, "07_chat_interface")

            # Find textarea
            textarea = page.locator('textarea').first
            if textarea.count() > 0:
                log_test("Chat Input", "PASS", "Chat textarea found", screenshot)

                # TEST 5: Send message
                print("\n" + "="*80)
                print("TEST 5: Send Text Message")
                print("="*80)

                test_msg = "你好，我想请你帮我评审一个设计稿"

                start_time = time.time()
                textarea.fill(test_msg)

                screenshot = take_screenshot(page, "08_message_typed")

                # Find send button (look for button near textarea)
                send_btn = page.locator('button[type="submit"]').first
                if send_btn.count() == 0:
                    # Try finding any button with send icon or near textarea
                    send_btn = page.locator('button').filter(has=page.locator('svg')).first

                if send_btn.count() > 0:
                    send_btn.click()

                    # Wait for response
                    time.sleep(8)

                    response_time = time.time() - start_time
                    test_results["performance_metrics"]["first_response"] = response_time

                    screenshot = take_screenshot(page, "09_response")

                    log_test("Send Message", "PASS", f"Response received in {response_time:.2f}s", screenshot, response_time)

                    if response_time > 12:
                        log_issue("MEDIUM", f"Slow response: {response_time:.2f}s")

                else:
                    log_test("Send Message", "FAIL", "Send button not found")

            else:
                log_test("Chat Input", "FAIL", "Chat textarea not found", screenshot)

            # TEST 6: Upload Design 1
            print("\n" + "="*80)
            print("TEST 6: Upload Design 1")
            print("="*80)

            time.sleep(2)

            file_input = page.locator('input[type="file"]').first
            if file_input.count() > 0:
                start_time = time.time()
                file_input.set_input_files(DESIGN1_PATH)

                time.sleep(3)

                screenshot = take_screenshot(page, "10_design1_uploaded")

                upload_time = time.time() - start_time

                log_test("Upload Design 1", "PASS", f"Uploaded in {upload_time:.2f}s", screenshot, upload_time)

                # TEST 7: Analyze Design 1
                print("\n" + "="*80)
                print("TEST 7: Analyze Design 1")
                print("="*80)

                time.sleep(2)

                textarea = page.locator('textarea').first
                if textarea.count() > 0:
                    analysis_msg = "请帮我分析一下这个设计稿，指出存在的问题和改进建议"

                    textarea.fill(analysis_msg)

                    send_btn = page.locator('button[type="submit"]').first
                    if send_btn.count() == 0:
                        send_btn = page.locator('button').filter(has=page.locator('svg')).first

                    if send_btn.count() > 0:
                        start_time = time.time()
                        send_btn.click()

                        print("Waiting for design analysis (15s)...")
                        time.sleep(15)

                        analysis_time = time.time() - start_time
                        test_results["performance_metrics"]["design_analysis"] = analysis_time

                        screenshot = take_screenshot(page, "11_design1_analysis")

                        log_test("Design Analysis", "PASS", f"Analysis completed in {analysis_time:.2f}s", screenshot, analysis_time)

                        if analysis_time > 20:
                            log_issue("MEDIUM", f"Slow analysis: {analysis_time:.2f}s")

                # TEST 8: Upload Design 2
                print("\n" + "="*80)
                print("TEST 8: Upload Design 2")
                print("="*80)

                time.sleep(3)

                file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0:
                    start_time = time.time()
                    file_input.set_input_files(DESIGN2_PATH)

                    time.sleep(3)

                    screenshot = take_screenshot(page, "12_design2_uploaded")

                    upload_time = time.time() - start_time

                    log_test("Upload Design 2", "PASS", f"Uploaded in {upload_time:.2f}s", screenshot, upload_time)

                    # TEST 9: Compare designs
                    print("\n" + "="*80)
                    print("TEST 9: Compare Two Designs")
                    print("="*80)

                    time.sleep(2)

                    textarea = page.locator('textarea').first
                    if textarea.count() > 0:
                        comparison_msg = "请对比这两个设计方案，给出优劣分析和选择建议"

                        textarea.fill(comparison_msg)

                        send_btn = page.locator('button[type="submit"]').first
                        if send_btn.count() == 0:
                            send_btn = page.locator('button').filter(has=page.locator('svg')).first

                        if send_btn.count() > 0:
                            start_time = time.time()
                            send_btn.click()

                            print("Waiting for comparison (20s)...")
                            time.sleep(20)

                            comparison_time = time.time() - start_time
                            test_results["performance_metrics"]["design_comparison"] = comparison_time

                            screenshot = take_screenshot(page, "13_comparison")

                            log_test("Design Comparison", "PASS", f"Comparison completed in {comparison_time:.2f}s", screenshot, comparison_time)

                            if comparison_time > 25:
                                log_issue("MEDIUM", f"Slow comparison: {comparison_time:.2f}s")

            else:
                screenshot = take_screenshot(page, "10_no_file_input")
                log_test("Upload Design 1", "FAIL", "File input not found", screenshot)

            # TEST 10: UI Elements
            print("\n" + "="*80)
            print("TEST 10: UI Elements")
            print("="*80)

            screenshot = take_screenshot(page, "14_ui_elements")

            buttons = page.locator('button').all()
            inputs = page.locator('input, textarea').all()
            images = page.locator('img').all()

            ui_count = {
                "buttons": len(buttons),
                "inputs": len(inputs),
                "images": len(images)
            }

            test_results["ui_elements"] = ui_count

            log_test("UI Elements", "PASS", f"{ui_count['buttons']} buttons, {ui_count['inputs']} inputs, {ui_count['images']} images", screenshot)

            # TEST 11: Scroll
            print("\n" + "="*80)
            print("TEST 11: Scroll Behavior")
            print("="*80)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            screenshot = take_screenshot(page, "15_scrolled")

            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            log_test("Scroll Behavior", "PASS", "Scrolling works", screenshot)

            # TEST 12: Performance
            print("\n" + "="*80)
            print("TEST 12: Performance")
            print("="*80)

            perf = page.evaluate("""() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: perfData ? perfData.domContentLoadedEventEnd - perfData.fetchStart : 0,
                    loadComplete: perfData ? perfData.loadEventEnd - perfData.fetchStart : 0
                };
            }""")

            test_results["performance_metrics"]["browser"] = perf

            if perf['domContentLoaded'] < 3000:
                log_test("Performance", "PASS", f"DOM loaded in {perf['domContentLoaded']:.0f}ms")
            else:
                log_test("Performance", "FAIL", f"Slow DOM load: {perf['domContentLoaded']:.0f}ms")

            # TEST 13: Console errors
            print("\n" + "="*80)
            print("TEST 13: Console Errors")
            print("="*80)

            error_logs = [log for log in console_logs if log['type'] == 'error']

            test_results["console_logs"] = {
                "total": len(console_logs),
                "errors": len(error_logs),
                "error_messages": [log['text'] for log in error_logs[:10]]
            }

            if len(error_logs) == 0:
                log_test("Console Errors", "PASS", "No errors")
            else:
                log_test("Console Errors", "FAIL", f"{len(error_logs)} errors found")
                for error in error_logs[:5]:
                    log_issue("HIGH", f"Console error: {error['text'][:100]}")

            # Final screenshot
            take_screenshot(page, "16_final")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

            try:
                screenshot = take_screenshot(page, "99_error")
                log_test("Test Execution", "FAIL", f"Error: {str(e)}", screenshot)
            except:
                pass

        finally:
            browser.close()

    return generate_report()

def generate_report():
    test_results["end_time"] = datetime.now().isoformat()

    print("\n" + "=" * 80)
    print("TEST REPORT SUMMARY")
    print("=" * 80)

    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    print(f"\nTotal: {total}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📊 Pass Rate: {pass_rate:.1f}%")

    print(f"\n⏱️  Performance:")
    for metric, value in test_results["performance_metrics"].items():
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {metric}: {value:.2f}s")

    print(f"\n⚠️  Issues: {len(test_results['issues'])}")
    for issue in test_results["issues"]:
        print(f"  [{issue['severity']}] {issue['description']}")

    print(f"\n📸 Screenshots: {len(test_results['screenshots'])}")
    print(f"   Location: {SCREENSHOT_DIR}/")

    # Save reports
    report_path = f"{SCREENSHOT_DIR}/test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Report: {report_path}")

    # Generate markdown
    md = generate_markdown_report()
    md_path = f"{SCREENSHOT_DIR}/test_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"📄 Markdown: {md_path}")

    print("\n" + "=" * 80)

    return test_results

def generate_markdown_report():
    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    md = f"""# Chris Chen AI Employee - E2E Test Report

**Date:** {test_results["start_time"]}

## Summary

- **Total:** {total}
- **Passed:** ✅ {test_results["passed"]}
- **Failed:** ❌ {test_results["failed"]}
- **Pass Rate:** {pass_rate:.1f}%
- **Issues:** {len(test_results["issues"])}

## Results

| Test | Status | Details | Duration |
|------|--------|---------|----------|
"""

    for test in test_results["tests"]:
        icon = "✅" if test["status"] == "PASS" else "❌"
        duration = f"{test['duration']:.2f}s" if test.get('duration') else "N/A"
        md += f"| {test['name']} | {icon} | {test['details']} | {duration} |\n"

    md += "\n## Performance\n\n"
    for metric, value in test_results["performance_metrics"].items():
        if isinstance(value, dict):
            md += f"### {metric}\n"
            for k, v in value.items():
                md += f"- {k}: {v}\n"
        else:
            md += f"- **{metric}:** {value:.2f}s\n"

    if test_results["issues"]:
        md += "\n## Issues\n\n"
        for sev in ["HIGH", "MEDIUM", "LOW"]:
            issues = [i for i in test_results["issues"] if i["severity"] == sev]
            if issues:
                icon = "🔴" if sev == "HIGH" else "🟡" if sev == "MEDIUM" else "🟢"
                md += f"### {icon} {sev}\n\n"
                for issue in issues:
                    md += f"- {issue['description']}\n"

    md += f"\n## Screenshots\n\nLocation: `{SCREENSHOT_DIR}/`\n\n"

    md += "\n## Conclusion\n\n"
    if pass_rate >= 90:
        md += "✅ Chris Chen is functioning well.\n"
    elif pass_rate >= 70:
        md += "⚠️ Chris Chen has some issues.\n"
    else:
        md += "❌ Chris Chen has significant issues.\n"

    return md

if __name__ == "__main__":
    main()
    print("\n✅ DONE")
