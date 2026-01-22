#!/usr/bin/env python3
"""测试详情页 - 使用坐标点击适配 Flutter Web"""

from playwright.sync_api import sync_playwright
import time

def test_detail_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        print("1. 访问登录页...")
        page.goto('http://localhost:8080/')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        print("2. 登录...")
        # Flutter Web 使用 canvas，需要用坐标点击
        # 邮箱输入框 (根据截图位置)
        page.click('body', position={'x': 640, 'y': 384})
        time.sleep(0.5)
        page.keyboard.type('1091201603@qq.com')

        # 密码输入框
        page.click('body', position={'x': 640, 'y': 447})
        time.sleep(0.5)
        page.keyboard.type('eeappsuccess')

        # 登录按钮
        page.click('body', position={'x': 640, 'y': 511})
        print("   点击登录按钮...")

        time.sleep(5)
        page.screenshot(path='/tmp/after_login.png', full_page=True)
        print("   登录后截图: /tmp/after_login.png")

        print("3. 等待简报列表加载...")
        time.sleep(3)
        page.screenshot(path='/tmp/briefing_list.png', full_page=True)
        print("   简报列表截图: /tmp/briefing_list.png")

        print("4. 点击第一个简报卡片...")
        # 假设卡片在页面左侧区域
        page.click('body', position={'x': 300, 'y': 300})
        time.sleep(3)
        page.screenshot(path='/tmp/briefing_detail.png', full_page=True)
        print("   详情页截图: /tmp/briefing_detail.png")

        print("5. 查找并点击'查看原始报告'按钮...")
        # 滚动到底部
        page.keyboard.press('End')
        time.sleep(1)
        page.screenshot(path='/tmp/detail_bottom.png', full_page=True)
        print("   详情页底部截图: /tmp/detail_bottom.png")

        browser.close()
        print("\n测试完成! 请查看截图文件。")

if __name__ == "__main__":
    test_detail_page()
