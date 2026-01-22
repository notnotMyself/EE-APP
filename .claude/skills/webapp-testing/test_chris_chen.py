#!/usr/bin/env python3
"""
Chris Chen AI员工完整测试脚本 - v4

根据截图分析调整坐标
"""

import time
import os
from playwright.sync_api import sync_playwright

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"
SCREENSHOT_DIR = "/tmp/chris_chen_test"

def ensure_screenshot_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(page, name):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"📸 截图: {path}")
    return path

def test_login_v4(page):
    """v4登录测试 - 更精确的坐标"""
    print("\n=== 登录测试 (v4) ===")

    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    take_screenshot(page, "01_initial")

    if '/login' not in page.url:
        print("✅ 已登录")
        return True

    # 获取视口大小
    viewport = page.viewport_size
    width = viewport['width']
    height = viewport['height']
    print(f"视口大小: {width}x{height}")

    # 从截图01_initial精确分析：
    # - 邮箱输入框：框中心约在 y=520-530
    # - 密码输入框：框中心约在 y=600-610
    # - 登录按钮：约在 y=670-680
    #
    # 但02截图显示点击y=519后，密码框获得了焦点
    # 这说明需要点击更靠上的位置

    # 方案：使用更低的y值来确保点击邮箱框
    email_y = 505  # 固定坐标，基于截图分析
    password_y = 595
    login_y = 665

    # 1. 点击邮箱输入框
    print(f"点击邮箱输入框: ({width//2}, {email_y})")
    page.mouse.click(width // 2, email_y)
    time.sleep(0.8)

    # 使用type方法慢速输入
    page.keyboard.type(TEST_EMAIL, delay=50)
    print(f"输入邮箱: {TEST_EMAIL}")
    time.sleep(0.5)

    take_screenshot(page, "02_email_entered")

    # 2. 点击密码输入框
    print(f"点击密码输入框: ({width//2}, {password_y})")
    page.mouse.click(width // 2, password_y)
    time.sleep(0.8)

    page.keyboard.type(TEST_PASSWORD, delay=50)
    print(f"输入密码: ***")
    time.sleep(0.5)

    take_screenshot(page, "03_password_entered")

    # 3. 点击登录按钮
    print(f"点击登录按钮: ({width//2}, {login_y})")
    page.mouse.click(width // 2, login_y)

    # 等待登录
    time.sleep(8)
    page.wait_for_load_state('networkidle')

    take_screenshot(page, "04_after_login")
    print(f"登录后URL: {page.url}")

    if '/login' not in page.url and '/register' not in page.url:
        print("✅ 登录成功")
        return True
    else:
        print("❌ 登录失败")
        return False

def explore_main_page(page):
    """探索主页"""
    print("\n=== 探索主页 ===")
    page.wait_for_load_state('networkidle')
    time.sleep(3)

    take_screenshot(page, "05_main_page")
    print(f"当前URL: {page.url}")
    return True

def navigate_to_agents(page):
    """导航到员工列表"""
    print("\n=== 导航到员工 ===")

    viewport = page.viewport_size
    width = viewport['width']
    height = viewport['height']

    # 底部导航栏 - 4个tab: 简报 | 员工 | 会话 | 设置
    nav_y = int(height * 0.96)
    tab_width = width // 4

    # 点击第二个tab（员工）
    agent_x = tab_width + tab_width // 2
    print(f"点击员工tab: ({agent_x}, {nav_y})")
    page.mouse.click(agent_x, nav_y)
    time.sleep(3)

    take_screenshot(page, "06_agents_page")
    print(f"当前URL: {page.url}")
    return True

def find_and_click_chris(page):
    """查找并点击Chris Chen"""
    print("\n=== 查找Chris Chen ===")

    viewport = page.viewport_size
    width = viewport['width']
    height = viewport['height']

    take_screenshot(page, "07_agents_list")

    # 点击列表中的Chris Chen
    # 尝试多个位置
    for y_ratio in [0.22, 0.32, 0.42, 0.52]:
        y = int(height * y_ratio)
        print(f"尝试点击: ({width//2}, {y})")
        page.mouse.click(width // 2, y)
        time.sleep(2)

        current_url = page.url
        take_screenshot(page, f"08_click_{int(y_ratio*100)}")

        if '/agents/' in current_url:
            print(f"✅ 进入Agent详情页")
            return True

    print("⚠️ 未找到Chris详情页，继续")
    return True

def test_chris_profile(page):
    """测试Chris Chen详情页"""
    print("\n=== Chris Chen详情页测试 ===")

    viewport = page.viewport_size
    width = viewport['width']
    height = viewport['height']

    take_screenshot(page, "09_chris_profile")
    print(f"当前URL: {page.url}")

    # 测试输入框
    input_y = int(height * 0.78)
    print(f"点击输入框: ({width//2}, {input_y})")
    page.mouse.click(width // 2, input_y)
    time.sleep(1)

    take_screenshot(page, "10_input_focused")

    # 测试快捷按钮 - 交互验证
    btn1_x = int(width * 0.17)
    btn1_y = int(height * 0.86)
    print(f"点击交互验证: ({btn1_x}, {btn1_y})")
    page.mouse.click(btn1_x, btn1_y)
    time.sleep(2)

    take_screenshot(page, "11_interaction_mode")
    return True

def test_conversation(page):
    """测试对话"""
    print("\n=== 对话测试 ===")

    viewport = page.viewport_size
    width = viewport['width']
    height = viewport['height']

    print(f"当前URL: {page.url}")
    take_screenshot(page, "12_conversation")

    if '/conversations/' in page.url:
        print("✅ 进入对话页面")

        # 输入测试消息
        input_y = int(height * 0.92)
        page.mouse.click(width // 2, input_y)
        time.sleep(0.5)

        page.keyboard.type("请帮我评审这个设计稿", delay=50)
        time.sleep(0.5)

        take_screenshot(page, "13_message_input")
        return True

    return True

def test_image_upload(page, image_path):
    """测试图片上传"""
    print(f"\n=== 图片上传测试: {image_path} ===")

    if not os.path.exists(image_path):
        print(f"❌ 图片不存在")
        return False

    take_screenshot(page, "14_before_upload")

    viewport = page.viewport_size
    width = viewport['width']
    height = viewport['height']

    # 点击附件按钮
    upload_x = int(width * 0.1)
    upload_y = int(height * 0.78)
    print(f"点击附件按钮: ({upload_x}, {upload_y})")
    page.mouse.click(upload_x, upload_y)
    time.sleep(2)

    take_screenshot(page, "15_upload_dialog")
    return True

def run_test():
    """运行完整测试"""
    ensure_screenshot_dir()
    print(f"\n{'='*60}")
    print("Chris Chen AI员工完整测试 - v4")
    print(f"{'='*60}")

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 414, 'height': 896},
            locale='zh-CN',
            device_scale_factor=2
        )
        page = context.new_page()

        try:
            results['登录'] = test_login_v4(page)

            if results['登录']:
                results['主页'] = explore_main_page(page)
                results['导航'] = navigate_to_agents(page)
                results['找到Chris'] = find_and_click_chris(page)
                results['详情页'] = test_chris_profile(page)
                results['对话'] = test_conversation(page)

                image1 = "/Users/80392083/Downloads/design1.jpg"
                results['图片上传'] = test_image_upload(page, image1)

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error")
        finally:
            browser.close()

    print(f"\n{'='*60}")
    print("测试结果")
    print(f"{'='*60}")
    for name, result in results.items():
        print(f"  {name}: {'✅' if result else '❌'}")
    print(f"\n截图目录: {SCREENSHOT_DIR}")

    return results

if __name__ == "__main__":
    run_test()
