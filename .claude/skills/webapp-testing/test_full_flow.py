#!/usr/bin/env python3
"""测试完整流程 - 使用 Tab 导航"""

from playwright.sync_api import sync_playwright
import time

def test_full_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        print("1. 访问登录页...")
        page.goto('http://localhost:8080/')
        page.wait_for_load_state('networkidle')
        time.sleep(4)

        print("2. 登录...")
        # 点击邮箱框
        page.click('body', position={'x': 640, 'y': 453})
        time.sleep(0.5)
        page.keyboard.type('1091201603@qq.com', delay=30)

        # 用 Tab 切换到密码框
        page.keyboard.press('Tab')
        time.sleep(0.3)
        page.keyboard.type('eeappsuccess', delay=30)

        page.screenshot(path='/tmp/filled.png')
        print("   填写完成: /tmp/filled.png")

        # 用 Enter 提交
        page.keyboard.press('Enter')
        print("   提交登录...")

        time.sleep(6)
        page.screenshot(path='/tmp/after_login.png', full_page=True)
        print("   登录后: /tmp/after_login.png")

        # 检查是否进入主页（简报列表）
        time.sleep(2)
        page.screenshot(path='/tmp/briefings.png', full_page=True)
        print("   简报列表: /tmp/briefings.png")

        # 如果登录成功，点击第一个卡片
        print("3. 点击简报卡片...")
        # 卡片通常在页面上部
        page.click('body', position={'x': 200, 'y': 250})
        time.sleep(3)
        page.screenshot(path='/tmp/detail.png', full_page=True)
        print("   详情页: /tmp/detail.png")

        # 滚动查看更多
        page.keyboard.press('PageDown')
        time.sleep(1)
        page.screenshot(path='/tmp/detail_scroll.png', full_page=True)
        print("   详情页滚动: /tmp/detail_scroll.png")

        browser.close()
        print("\n测试完成!")

if __name__ == "__main__":
    test_full_flow()
