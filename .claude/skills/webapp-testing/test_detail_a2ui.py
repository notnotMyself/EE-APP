#!/usr/bin/env python3
"""测试详情页 A2UI 渲染"""

from playwright.sync_api import sync_playwright
import time

def test_detail_page_a2ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("1. 访问登录页...")
        page.goto('http://localhost:8080/')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("2. 登录...")
        page.fill('input[type="text"]', '1091201603@qq.com')
        page.fill('input[type="password"]', 'eeappsuccess')
        page.click('button:has-text("登录")')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        print("3. 等待简报列表加载...")
        page.wait_for_timeout(3000)

        # 截图简报列表
        page.screenshot(path='/tmp/briefing_list.png', full_page=True)
        print("   截图已保存: /tmp/briefing_list.png")

        # 查找简报卡片
        cards = page.locator('[class*="Card"], [class*="card"]').all()
        print(f"   找到 {len(cards)} 个卡片元素")

        # 尝试点击第一个简报卡片
        print("4. 点击第一个简报卡片...")
        try:
            # 尝试多种选择器
            clickable = page.locator('text=研发效能').first
            if clickable.count() > 0:
                clickable.click()
            else:
                # 尝试点击任何看起来像卡片的元素
                page.locator('[class*="briefing"], [class*="Briefing"]').first.click()
        except:
            print("   无法找到可点击的卡片，尝试其他方式...")
            # 直接点击页面中心区域的某个元素
            page.click('body', position={'x': 200, 'y': 300})

        page.wait_for_timeout(3000)

        # 截图详情页
        page.screenshot(path='/tmp/briefing_detail.png', full_page=True)
        print("   详情页截图: /tmp/briefing_detail.png")

        # 检查页面内容
        content = page.content()

        # 检查是否有 A2UI 组件的迹象
        has_metric_cards = 'metric' in content.lower() or '指标' in content
        has_findings = 'finding' in content.lower() or '发现' in content
        has_markdown = 'markdown' in content.lower()

        print(f"\n5. 页面分析:")
        print(f"   - 包含指标相关内容: {has_metric_cards}")
        print(f"   - 包含发现相关内容: {has_findings}")
        print(f"   - 包含 markdown: {has_markdown}")

        # 查找"查看原始报告"按钮
        full_report_btn = page.locator('text=查看原始报告, text=原始报告').first
        if full_report_btn.count() > 0:
            print("\n6. 点击'查看原始报告'按钮...")
            full_report_btn.click()
            page.wait_for_timeout(2000)
            page.screenshot(path='/tmp/full_report.png', full_page=True)
            print("   完整报告截图: /tmp/full_report.png")
        else:
            print("\n6. 未找到'查看原始报告'按钮")

        browser.close()
        print("\n测试完成!")

if __name__ == "__main__":
    test_detail_page_a2ui()
