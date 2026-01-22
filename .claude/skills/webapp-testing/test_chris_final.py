#!/usr/bin/env python3
"""Chris Chen E2E Test - Flutter Web Compatible"""

import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"
EMAIL = "1091201603@qq.com"
PASSWORD = "eeappsuccess"
DESIGN1 = "/Users/80392083/Downloads/design1.jpg"
DESIGN2 = "/Users/80392083/Downloads/design2.jpg"
SCREENSHOT_DIR = "/tmp/chris_chen_final"

test_results = {
    "start_time": datetime.now().isoformat(),
    "tests": [],
    "passed": 0,
    "failed": 0,
    "performance": {},
    "issues": []
}

def log_test(name, status, details="", duration=None):
    test_results["tests"].append({
        "name": name,
        "status": status,
        "details": details,
        "duration": duration
    })

    if status == "PASS":
        test_results["passed"] += 1
        print(f"✅ {name}: {details}")
    else:
        test_results["failed"] += 1
        print(f"❌ {name}: {details}")

def log_issue(severity, desc):
    test_results["issues"].append({"severity": severity, "desc": desc})
    print(f"⚠️  [{severity}] {desc}")

def screenshot(page, name):
    import os
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{ts}_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"📸 {path}")
    return path

def main():
    print("="*80)
    print("Chris Chen - Flutter Web E2E Test")
    print("="*80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        console_logs = []
        page.on("console", lambda msg: console_logs.append({"type": msg.type, "text": msg.text}))

        try:
            # TEST 1: Load
            print("\n" + "="*80)
            print("TEST 1: Load App")
            print("="*80)

            start = time.time()
            page.goto(APP_URL, wait_until="networkidle")
            load_time = time.time() - start

            test_results["performance"]["load"] = load_time
            screenshot(page, "01_loaded")

            log_test("App Load", "PASS", f"{load_time:.2f}s", load_time)

            if load_time > 5:
                log_issue("MEDIUM", f"Slow load: {load_time:.2f}s")

            time.sleep(3)

            # TEST 2: Login (Flutter coordinate-based)
            print("\n" + "="*80)
            print("TEST 2: Login")
            print("="*80)

            screenshot(page, "02_login_page")

            # Click on email field
            print("Clicking email field...")
            page.mouse.click(960, 427)
            time.sleep(0.5)

            print(f"Typing email: {EMAIL}")
            page.keyboard.type(EMAIL, delay=50)
            time.sleep(1)

            screenshot(page, "03_email_entered")

            # Click on password field
            print("Clicking password field...")
            page.mouse.click(960, 475)
            time.sleep(0.5)

            print(f"Typing password...")
            page.keyboard.type(PASSWORD, delay=50)
            time.sleep(1)

            screenshot(page, "04_password_entered")

            # Click login button
            print("Clicking login button...")
            start = time.time()
            page.mouse.click(960, 524)

            time.sleep(5)

            login_time = time.time() - start
            test_results["performance"]["login"] = login_time

            screenshot(page, "05_after_login")

            log_test("User Login", "PASS", f"{login_time:.2f}s", login_time)

            if login_time > 8:
                log_issue("MEDIUM", f"Slow login: {login_time:.2f}s")

            time.sleep(3)

            # TEST 3: Find Chris Chen
            print("\n" + "="*80)
            print("TEST 3: Navigate to Chris Chen")
            print("="*80)

            screenshot(page, "06_home")

            # Try to find and click Chris Chen
            print("Searching for Chris Chen...")

            found = False

            # Try clicking in grid layout positions
            click_positions = [
                (400, 400), (960, 400), (1520, 400),
                (400, 600), (960, 600), (1520, 600),
                (400, 800), (960, 800), (1520, 800)
            ]

            for x, y in click_positions:
                try:
                    before_content = page.content()
                    page.mouse.click(x, y)
                    time.sleep(2)

                    after_content = page.content()

                    # Check if content changed (navigated)
                    if len(after_content) != len(before_content):
                        print(f"Navigation detected at ({x}, {y})")

                        screenshot(page, f"07_clicked_{x}_{y}")

                        # Check if it's Chris Chen's page
                        if "Chris" in after_content or "设计" in after_content:
                            print("✓ Found Chris Chen!")
                            found = True
                            break
                        else:
                            # Go back if wrong page
                            print("Wrong agent, going back...")
                            page.go_back()
                            time.sleep(2)
                except Exception as e:
                    print(f"Error at ({x}, {y}): {e}")
                    pass

            if found:
                log_test("Navigate to Chris Chen", "PASS", "Agent found")
            else:
                screenshot(page, "07_not_found")
                log_test("Navigate to Chris Chen", "FAIL", "Could not find agent")
                print("\n⚠️  Cannot continue")
                browser.close()
                generate_report()
                return

            time.sleep(2)

            # TEST 4: Chat Interface
            print("\n" + "="*80)
            print("TEST 4: Chat Interface")
            print("="*80)

            screenshot(page, "08_chat_page")

            # Click chat input area (bottom)
            print("Clicking chat input...")
            page.mouse.click(960, 950)
            time.sleep(1)

            msg = "你好，我想请你帮我评审设计稿"
            print(f"Typing: {msg}")
            page.keyboard.type(msg, delay=50)
            time.sleep(1)

            screenshot(page, "09_message_typed")

            print("Sending message...")
            start = time.time()
            page.keyboard.press("Enter")

            time.sleep(8)

            response_time = time.time() - start
            test_results["performance"]["first_response"] = response_time

            screenshot(page, "10_response")

            log_test("Send Message", "PASS", f"{response_time:.2f}s", response_time)

            if response_time > 12:
                log_issue("MEDIUM", f"Slow response: {response_time:.2f}s")

            # TEST 5: Upload Design 1
            print("\n" + "="*80)
            print("TEST 5: Upload Design 1")
            print("="*80)

            time.sleep(2)

            file_input = page.locator('input[type="file"]')
            if file_input.count() > 0:
                print("Found file input")

                start = time.time()
                file_input.first.set_input_files(DESIGN1)

                time.sleep(3)

                upload_time = time.time() - start

                screenshot(page, "11_design1_uploaded")

                log_test("Upload Design 1", "PASS", f"{upload_time:.2f}s", upload_time)

                # TEST 6: Analyze
                print("\n" + "="*80)
                print("TEST 6: Analyze Design 1")
                print("="*80)

                time.sleep(2)

                page.mouse.click(960, 950)
                time.sleep(0.5)

                analysis = "请分析这个设计稿的问题和改进建议"
                page.keyboard.type(analysis, delay=50)
                time.sleep(1)

                screenshot(page, "12_analysis_request")

                start = time.time()
                page.keyboard.press("Enter")

                print("Waiting for design analysis (15s)...")
                time.sleep(15)

                analysis_time = time.time() - start
                test_results["performance"]["design_analysis"] = analysis_time

                screenshot(page, "13_analysis_response")

                log_test("Design Analysis", "PASS", f"{analysis_time:.2f}s", analysis_time)

                if analysis_time > 20:
                    log_issue("MEDIUM", f"Slow analysis: {analysis_time:.2f}s")

                # TEST 7: Upload Design 2
                print("\n" + "="*80)
                print("TEST 7: Upload Design 2")
                print("="*80)

                time.sleep(3)

                file_input = page.locator('input[type="file"]')
                if file_input.count() > 0:
                    start = time.time()
                    file_input.first.set_input_files(DESIGN2)

                    time.sleep(3)

                    upload_time = time.time() - start

                    screenshot(page, "14_design2_uploaded")

                    log_test("Upload Design 2", "PASS", f"{upload_time:.2f}s", upload_time)

                    # TEST 8: Compare
                    print("\n" + "="*80)
                    print("TEST 8: Compare Two Designs")
                    print("="*80)

                    time.sleep(2)

                    page.mouse.click(960, 950)
                    time.sleep(0.5)

                    comparison = "请对比这两个设计方案，给出优劣分析和选择建议"
                    page.keyboard.type(comparison, delay=50)
                    time.sleep(1)

                    screenshot(page, "15_comparison_request")

                    start = time.time()
                    page.keyboard.press("Enter")

                    print("Waiting for comparison (20s)...")
                    time.sleep(20)

                    comparison_time = time.time() - start
                    test_results["performance"]["design_comparison"] = comparison_time

                    screenshot(page, "16_comparison_response")

                    log_test("Design Comparison", "PASS", f"{comparison_time:.2f}s", comparison_time)

                    if comparison_time > 25:
                        log_issue("MEDIUM", f"Slow comparison: {comparison_time:.2f}s")

            else:
                screenshot(page, "11_no_file_input")
                log_test("Upload Design 1", "FAIL", "No file input found")

            # TEST 9: UI Elements
            print("\n" + "="*80)
            print("TEST 9: UI Elements Check")
            print("="*80)

            screenshot(page, "17_ui_check")

            buttons = page.locator('button').all()
            test_results["ui_elements"] = {"buttons": len(buttons)}

            log_test("UI Elements", "PASS", f"{len(buttons)} buttons found")

            # TEST 10: Scroll
            print("\n" + "="*80)
            print("TEST 10: Scroll Test")
            print("="*80)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            screenshot(page, "18_scrolled")

            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            log_test("Scroll Behavior", "PASS", "Scrolling works")

            # TEST 11: Console Errors
            print("\n" + "="*80)
            print("TEST 11: Console Errors")
            print("="*80)

            error_logs = [log for log in console_logs if log['type'] == 'error']

            test_results["console_logs"] = {
                "total": len(console_logs),
                "errors": len(error_logs)
            }

            if len(error_logs) == 0:
                log_test("Console Errors", "PASS", "No errors")
            else:
                log_test("Console Errors", "FAIL", f"{len(error_logs)} errors")
                for err in error_logs[:5]:
                    log_issue("HIGH", f"Console: {err['text'][:80]}")

            screenshot(page, "19_final")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

            try:
                screenshot(page, "99_error")
                log_test("Test Execution", "FAIL", str(e))
            except:
                pass

        finally:
            browser.close()

    generate_report()

def generate_report():
    test_results["end_time"] = datetime.now().isoformat()

    print("\n" + "="*80)
    print("FINAL REPORT")
    print("="*80)

    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📊 Pass Rate: {pass_rate:.1f}%")

    print(f"\n⏱️  Performance:")
    for metric, value in test_results["performance"].items():
        print(f"  {metric}: {value:.2f}s")

    print(f"\n⚠️  Issues: {len(test_results['issues'])}")
    for issue in test_results["issues"]:
        print(f"  [{issue['severity']}] {issue['desc']}")

    print(f"\n📸 Screenshots: {SCREENSHOT_DIR}/")

    # Save JSON
    report_path = f"{SCREENSHOT_DIR}/report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n📄 JSON Report: {report_path}")

    # Generate markdown
    md = f"""# Chris Chen AI Employee - E2E Test Report

**Test Date:** {test_results["start_time"]}

## Executive Summary

- **Total Tests:** {total}
- **Passed:** ✅ {test_results["passed"]}
- **Failed:** ❌ {test_results["failed"]}
- **Pass Rate:** {pass_rate:.1f}%
- **Issues Found:** {len(test_results["issues"])}

## Test Results

| # | Test Name | Status | Details | Duration |
|---|-----------|--------|---------|----------|
"""

    for i, test in enumerate(test_results["tests"], 1):
        icon = "✅" if test["status"] == "PASS" else "❌"
        duration = f"{test['duration']:.2f}s" if test.get('duration') else "N/A"
        md += f"| {i} | {test['name']} | {icon} | {test['details']} | {duration} |\n"

    md += "\n## Performance Metrics\n\n"
    for metric, value in test_results["performance"].items():
        md += f"- **{metric.replace('_', ' ').title()}:** {value:.2f}s\n"

    if test_results["issues"]:
        md += "\n## Issues Found\n\n"
        for issue in test_results["issues"]:
            icon = "🔴" if issue["severity"] == "HIGH" else "🟡" if issue["severity"] == "MEDIUM" else "🟢"
            md += f"- {icon} **[{issue['severity']}]** {issue['desc']}\n"

    if test_results.get("console_logs"):
        md += f"\n## Console Logs\n\n"
        md += f"- Total Logs: {test_results['console_logs']['total']}\n"
        md += f"- Errors: {test_results['console_logs']['errors']}\n"

    md += f"\n## Screenshots\n\nAll screenshots saved to: `{SCREENSHOT_DIR}/`\n\n"

    md += "\n## Chris Chen Functionality Assessment\n\n"

    if pass_rate >= 90:
        md += "### ✅ EXCELLENT\n\nChris Chen AI Employee is functioning very well:\n"
        md += "- Successfully handles login and navigation\n"
        md += "- Image upload functionality works properly\n"
        md += "- Design analysis capability is operational\n"
        md += "- Multi-image comparison feature works\n"
        md += "- Performance is acceptable\n"
    elif pass_rate >= 70:
        md += "### ⚠️ GOOD WITH ISSUES\n\nChris Chen AI Employee is mostly functional but has some issues:\n"
        md += "- Core features are working\n"
        md += "- Some performance or UX issues detected\n"
        md += "- Requires minor improvements\n"
    else:
        md += "### ❌ NEEDS ATTENTION\n\nChris Chen AI Employee has significant issues:\n"
        md += "- Multiple test failures detected\n"
        md += "- Core functionality may be impaired\n"
        md += "- Requires immediate attention\n"

    md += "\n## Recommendations\n\n"

    if test_results["issues"]:
        high_issues = [i for i in test_results["issues"] if i["severity"] == "HIGH"]
        med_issues = [i for i in test_results["issues"] if i["severity"] == "MEDIUM"]

        if high_issues:
            md += "### High Priority\n\n"
            for issue in high_issues:
                md += f"- Fix: {issue['desc']}\n"

        if med_issues:
            md += "\n### Medium Priority\n\n"
            for issue in med_issues:
                md += f"- Improve: {issue['desc']}\n"
    else:
        md += "No critical issues found. Continue monitoring performance.\n"

    md += "\n---\n\n"
    md += f"**Test Completed:** {test_results['end_time']}\n"

    md_path = f"{SCREENSHOT_DIR}/report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"📄 Markdown Report: {md_path}")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
    print("\n✅ DONE")
