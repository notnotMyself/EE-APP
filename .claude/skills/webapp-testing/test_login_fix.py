#!/usr/bin/env python3
"""测试详情页 - 修正坐标"""

from playwright.sync_api import sync_playwright
import time

def test_detail_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        print("1. 访问登录页...")
        page.goto('http://localhost:8080/')
        page.wait_for_load_state('networkidle')
        time.sleep(4)

        print("2. 登录...")
        # 根据截图调整坐标：
        # 邮箱输入框 y≈454
        # 密码输入框 y≈517
        # 登录按钮 y≈581

        # 先点击邮箱框
        page.click('body', position={'x': 640, 'y': 425})
        time.sleep(0.3)
        page.keyboard.type('1091201603@qq.com', delay=50)
        time.sleep(0.3)

        # 点击密码框
        page.click('body', position={'x': 640, 'y': 517})
        time.sleep(0.3)
        page.keyboard.type('eeappsuccess', delay=50)
        time.sleep(0.3)

        page.screenshot(path='/tmp/before_login.png')
        print("   填写完成截图: /tmp/before_login.png")

        # 点击登录按钮
        page.click('body', position={'x': 640, 'y': 582})
        print("   点击登录按钮...")

        time.sleep(6)
        page.screenshot(path='/tmp/after_login.png', full_page=True)
        print("   登录后截图: /tmp/after_login.png")

        # 检查是否还在登录页
        page.screenshot(path='/tmp/main_page.png', full_page=True)
        print("   主页截图: /tmp/main_page.png")

        browser.close()
        print("\n测试完成!")

if __name__ == "__main__":
    test_detail_page()
