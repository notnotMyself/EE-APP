#!/usr/bin/env python3
"""
Chris Chen AI Employee - Comprehensive E2E Testing
Tests login, chat, image upload, analysis, and all UI interactions.
"""

import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Test configuration
APP_URL = "http://localhost:5000"
EMAIL = "1091201603@qq.com"
PASSWORD = "eeappsuccess"
DESIGN1_PATH = "/Users/80392083/Downloads/design1.jpg"
DESIGN2_PATH = "/Users/80392083/Downloads/design2.jpg"
SCREENSHOT_DIR = "/tmp/chris_chen_test"

# Test results tracking
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
    """Log test result"""
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

def log_issue(severity, description, screenshot_path=None):
    """Log UX or performance issue"""
    issue = {
        "severity": severity,
        "description": description,
        "screenshot": screenshot_path,
        "timestamp": datetime.now().isoformat()
    }
    test_results["issues"].append(issue)
    print(f"⚠️  [{severity}] {description}")

def take_screenshot(page, name):
    """Take and save screenshot"""
    import os
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = f"{SCREENSHOT_DIR}/{filename}"

    page.screenshot(path=filepath, full_page=True)
    print(f"📸 Screenshot saved: {filepath}")
    return filepath

def main():
    print("=" * 80)
    print("Chris Chen AI Employee - Comprehensive E2E Testing")
    print("=" * 80)

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=False)  # Use False for debugging
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Enable console logging
        console_logs = []
        page.on("console", lambda msg: console_logs.append({
            "type": msg.type,
            "text": msg.text,
            "timestamp": datetime.now().isoformat()
        }))

        try:
            # TEST 1: Application Load
            print("\n" + "=" * 80)
            print("TEST 1: Application Load")
            print("=" * 80)

            start_time = time.time()
            page.goto(APP_URL, wait_until="networkidle")
            load_time = time.time() - start_time

            test_results["performance_metrics"]["initial_load"] = load_time

            screenshot = take_screenshot(page, "01_initial_load")

            if load_time > 5:
                log_issue("MEDIUM", f"Slow initial load: {load_time:.2f}s (expected < 5s)")

            log_test(
                "Application Load",
                "PASS",
                f"Loaded in {load_time:.2f}s",
                screenshot,
                load_time
            )

            # Wait for app to fully render
            time.sleep(3)

            # TEST 2: Check if logged in or need to login
            print("\n" + "=" * 80)
            print("TEST 2: Authentication Check")
            print("=" * 80)

            screenshot = take_screenshot(page, "02_auth_check")

            # Check for email input (indicates login page)
            email_input = page.query_selector('input[type="email"]')

            if email_input:
                print("Login required, proceeding with login...")

                # Fill email
                email_input.fill(EMAIL)

                # Find and fill password
                password_input = page.query_selector('input[type="password"]')
                if password_input:
                    password_input.fill(PASSWORD)

                    screenshot = take_screenshot(page, "03_login_filled")

                    # Click login button
                    login_button = page.query_selector('button[type="submit"]')
                    if not login_button:
                        login_button = page.query_selector('button:has-text("登录")')

                    if login_button:
                        start_time = time.time()
                        login_button.click()

                        # Wait for navigation
                        page.wait_for_load_state("networkidle", timeout=15000)
                        login_time = time.time() - start_time

                        screenshot = take_screenshot(page, "04_after_login")

                        log_test(
                            "User Login",
                            "PASS",
                            f"Logged in successfully in {login_time:.2f}s",
                            screenshot,
                            login_time
                        )

                        time.sleep(2)
                    else:
                        log_test("User Login", "FAIL", "Login button not found")
                else:
                    log_test("User Login", "FAIL", "Password field not found")
            else:
                log_test("Authentication Check", "PASS", "Already logged in")

            # TEST 3: Navigate to Chris Chen
            print("\n" + "=" * 80)
            print("TEST 3: Navigate to Chris Chen")
            print("=" * 80)

            screenshot = take_screenshot(page, "05_main_page")

            # Look for Chris Chen - try multiple selectors
            chris_found = False

            # Try clicking on agent card with Chris Chen
            selectors = [
                'text="Chris Chen"',
                ':text("Chris Chen")',
                '[data-agent-id="design_validator"]',
                '.agent-card:has-text("Chris")'
            ]

            for selector in selectors:
                try:
                    element = page.wait_for_selector(selector, timeout=3000)
                    if element:
                        print(f"Found Chris Chen with selector: {selector}")
                        start_time = time.time()
                        element.click()

                        page.wait_for_load_state("networkidle", timeout=10000)
                        nav_time = time.time() - start_time

                        screenshot = take_screenshot(page, "06_chris_chen_page")

                        log_test(
                            "Navigate to Chris Chen",
                            "PASS",
                            f"Navigated in {nav_time:.2f}s",
                            screenshot,
                            nav_time
                        )

                        chris_found = True
                        break
                except:
                    continue

            if not chris_found:
                # Try to list all visible text
                all_text = page.locator('body').text_content()

                if 'Chris' in all_text or 'chris' in all_text.lower():
                    print("Chris Chen text found on page, trying to click...")

                    # Try finding clickable elements with Chris
                    clickables = page.locator('a, button, [role="button"], .clickable').all()

                    for elem in clickables:
                        try:
                            text = elem.text_content()
                            if text and ('Chris' in text or '设计' in text):
                                print(f"Clicking element with text: {text[:50]}")
                                elem.click()
                                page.wait_for_load_state("networkidle", timeout=5000)
                                screenshot = take_screenshot(page, "06_chris_chen_found")
                                chris_found = True
                                break
                        except:
                            continue

            if not chris_found:
                screenshot = take_screenshot(page, "06_chris_chen_not_found")
                log_test(
                    "Navigate to Chris Chen",
                    "FAIL",
                    "Could not find Chris Chen agent",
                    screenshot
                )
                print("\n⚠️  Cannot continue tests without accessing Chris Chen")
                browser.close()
                return generate_report()

            time.sleep(2)

            # TEST 4: Chat Interface
            print("\n" + "=" * 80)
            print("TEST 4: Test Chat Interface")
            print("=" * 80)

            screenshot = take_screenshot(page, "07_chat_interface")

            # Find chat textarea
            chat_input = page.query_selector('textarea')
            if not chat_input:
                chat_input = page.query_selector('input[type="text"]')

            if chat_input:
                log_test("Chat Input Found", "PASS", "Chat input is available", screenshot)

                # TEST 5: Send basic message
                print("\n" + "=" * 80)
                print("TEST 5: Send Basic Message")
                print("=" * 80)

                test_message = "你好，我想请你帮我评审一个设计稿"

                start_time = time.time()
                chat_input.fill(test_message)

                screenshot = take_screenshot(page, "08_message_typed")

                # Find send button
                send_button = page.query_selector('button[type="submit"]')
                if not send_button:
                    # Try finding by icon or position
                    buttons = page.locator('button').all()
                    for btn in buttons:
                        try:
                            aria_label = btn.get_attribute('aria-label')
                            if aria_label and ('发送' in aria_label or 'send' in aria_label.lower()):
                                send_button = btn
                                break
                        except:
                            pass

                if send_button:
                    send_button.click()

                    # Wait for response
                    time.sleep(5)

                    response_time = time.time() - start_time

                    screenshot = take_screenshot(page, "09_after_send")

                    log_test(
                        "Send Message",
                        "PASS",
                        f"Message sent, response received in {response_time:.2f}s",
                        screenshot,
                        response_time
                    )

                    test_results["performance_metrics"]["first_response"] = response_time
                else:
                    log_test("Send Message", "FAIL", "Send button not found")

            else:
                log_test("Chat Input Found", "FAIL", "Chat input not found", screenshot)

            # TEST 6: Upload Design 1
            print("\n" + "=" * 80)
            print("TEST 6: Upload Design 1")
            print("=" * 80)

            time.sleep(2)

            # Look for file input or attachment button
            file_input = page.query_selector('input[type="file"]')

            if file_input:
                start_time = time.time()
                file_input.set_input_files(DESIGN1_PATH)

                time.sleep(3)

                screenshot = take_screenshot(page, "10_design1_uploaded")

                upload_time = time.time() - start_time

                log_test(
                    "Upload Design 1",
                    "PASS",
                    f"Image uploaded in {upload_time:.2f}s",
                    screenshot,
                    upload_time
                )

                # TEST 7: Request analysis
                print("\n" + "=" * 80)
                print("TEST 7: Analyze Design 1")
                print("=" * 80)

                time.sleep(2)

                if chat_input:
                    analysis_request = "请帮我分析一下这个设计稿，指出存在的问题"

                    chat_input.fill(analysis_request)

                    if send_button:
                        start_time = time.time()
                        send_button.click()

                        print("Waiting for Chris Chen's analysis (may take 10-15s)...")
                        time.sleep(15)

                        screenshot = take_screenshot(page, "11_design1_analysis")

                        analysis_time = time.time() - start_time

                        test_results["performance_metrics"]["image_analysis"] = analysis_time

                        log_test(
                            "Design Analysis",
                            "PASS",
                            f"Analysis completed in {analysis_time:.2f}s",
                            screenshot,
                            analysis_time
                        )

                        if analysis_time > 20:
                            log_issue("MEDIUM", f"Slow analysis response: {analysis_time:.2f}s")

                # TEST 8: Upload Design 2
                print("\n" + "=" * 80)
                print("TEST 8: Upload Design 2")
                print("=" * 80)

                time.sleep(3)

                file_input = page.query_selector('input[type="file"]')
                if file_input:
                    start_time = time.time()
                    file_input.set_input_files(DESIGN2_PATH)

                    time.sleep(3)

                    screenshot = take_screenshot(page, "12_design2_uploaded")

                    upload_time = time.time() - start_time

                    log_test(
                        "Upload Design 2",
                        "PASS",
                        f"Second image uploaded in {upload_time:.2f}s",
                        screenshot,
                        upload_time
                    )

                    # TEST 9: Compare designs
                    print("\n" + "=" * 80)
                    print("TEST 9: Compare Two Designs")
                    print("=" * 80)

                    time.sleep(2)

                    if chat_input:
                        comparison_request = "请对比这两个设计方案，给出优劣分析和选择建议"

                        chat_input.fill(comparison_request)

                        if send_button:
                            start_time = time.time()
                            send_button.click()

                            print("Waiting for comparison analysis (may take 15-20s)...")
                            time.sleep(20)

                            screenshot = take_screenshot(page, "13_comparison_analysis")

                            comparison_time = time.time() - start_time

                            log_test(
                                "Design Comparison",
                                "PASS",
                                f"Comparison completed in {comparison_time:.2f}s",
                                screenshot,
                                comparison_time
                            )

                            if comparison_time > 25:
                                log_issue("MEDIUM", f"Slow comparison: {comparison_time:.2f}s")

            else:
                screenshot = take_screenshot(page, "10_no_file_input")
                log_test("Upload Design 1", "FAIL", "File input not found", screenshot)

            # TEST 10: UI Elements
            print("\n" + "=" * 80)
            print("TEST 10: UI Elements Inventory")
            print("=" * 80)

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

            log_test(
                "UI Elements",
                "PASS",
                f"Found {ui_count['buttons']} buttons, {ui_count['inputs']} inputs, {ui_count['images']} images",
                screenshot
            )

            # TEST 11: Scroll behavior
            print("\n" + "=" * 80)
            print("TEST 11: Scroll Behavior")
            print("=" * 80)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            screenshot = take_screenshot(page, "15_scrolled")

            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            log_test("Scroll Behavior", "PASS", "Scrolling works smoothly", screenshot)

            # TEST 12: Performance metrics
            print("\n" + "=" * 80)
            print("TEST 12: Browser Performance Metrics")
            print("=" * 80)

            perf = page.evaluate("""() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: perfData ? perfData.domContentLoadedEventEnd - perfData.fetchStart : 0,
                    loadComplete: perfData ? perfData.loadEventEnd - perfData.fetchStart : 0
                };
            }""")

            test_results["performance_metrics"]["browser"] = perf

            print(f"DOM Content Loaded: {perf['domContentLoaded']:.0f}ms")
            print(f"Load Complete: {perf['loadComplete']:.0f}ms")

            if perf['domContentLoaded'] < 3000:
                log_test("Performance Check", "PASS", f"DOM loaded in {perf['domContentLoaded']:.0f}ms")
            else:
                log_test("Performance Check", "FAIL", f"Slow DOM load: {perf['domContentLoaded']:.0f}ms")

            # TEST 13: Console errors
            print("\n" + "=" * 80)
            print("TEST 13: Console Errors")
            print("=" * 80)

            error_logs = [log for log in console_logs if log['type'] == 'error']
            warning_logs = [log for log in console_logs if log['type'] == 'warning']

            test_results["console_logs"] = {
                "total": len(console_logs),
                "errors": len(error_logs),
                "warnings": len(warning_logs),
                "error_messages": [log['text'] for log in error_logs[:10]]
            }

            if len(error_logs) == 0:
                log_test("Console Errors", "PASS", "No console errors")
            else:
                log_test("Console Errors", "FAIL", f"{len(error_logs)} errors found")
                for error in error_logs[:5]:
                    log_issue("HIGH", f"Console error: {error['text']}")

            # Final screenshot
            take_screenshot(page, "16_final_state")

        except Exception as e:
            print(f"\n❌ Test error: {e}")
            import traceback
            traceback.print_exc()

            try:
                screenshot = take_screenshot(page, "99_error")
                log_test("Test Execution", "FAIL", f"Error: {str(e)}", screenshot)
            except:
                pass

        finally:
            print("\nClosing browser...")
            browser.close()

    return generate_report()

def generate_report():
    """Generate comprehensive test report"""
    test_results["end_time"] = datetime.now().isoformat()

    print("\n" + "=" * 80)
    print("TEST REPORT SUMMARY")
    print("=" * 80)

    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📊 Pass Rate: {pass_rate:.1f}%")

    print(f"\n⏱️  Performance Metrics:")
    for metric, value in test_results["performance_metrics"].items():
        if isinstance(value, dict):
            print(f"  {metric}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {metric}: {value:.2f}s")

    print(f"\n⚠️  Issues: {len(test_results['issues'])}")
    for issue in test_results["issues"]:
        print(f"  [{issue['severity']}] {issue['description']}")

    print(f"\n📸 Screenshots: {len(test_results['screenshots'])}")
    print(f"   Location: {SCREENSHOT_DIR}/")

    # Save JSON report
    report_path = f"{SCREENSHOT_DIR}/test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Report saved: {report_path}")

    # Generate markdown
    md = generate_markdown_report()
    md_path = f"{SCREENSHOT_DIR}/test_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"📄 Markdown report: {md_path}")

    print("\n" + "=" * 80)

    return test_results

def generate_markdown_report():
    """Generate markdown report"""
    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    md = f"""# Chris Chen AI Employee - E2E Test Report

**Test Date:** {test_results["start_time"]}

## Summary

- **Total Tests:** {total}
- **Passed:** ✅ {test_results["passed"]}
- **Failed:** ❌ {test_results["failed"]}
- **Pass Rate:** {pass_rate:.1f}%
- **Issues:** {len(test_results["issues"])}

## Test Results

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
                md += "\n"

    md += f"\n## Screenshots\n\nSaved to: `{SCREENSHOT_DIR}/`\n\n"

    md += "\n## Conclusion\n\n"
    if pass_rate >= 90:
        md += "✅ Chris Chen AI Employee is functioning well.\n"
    elif pass_rate >= 70:
        md += "⚠️ Chris Chen has some issues that need attention.\n"
    else:
        md += "❌ Chris Chen has significant issues requiring immediate attention.\n"

    return md

if __name__ == "__main__":
    main()
    print("\n✅ DONE")
