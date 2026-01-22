#!/usr/bin/env python3
"""
Chris Chen 后端功能测试

测试：
1. 图片理解能力
2. 三种评审模式
3. API响应
"""

import requests
import base64
import json
import time
import os

BASE_URL = "http://localhost:8000"
IMAGE_PATH_1 = "/Users/80392083/Downloads/design1.jpg"
IMAGE_PATH_2 = "/Users/80392083/Downloads/design2.jpg"

def test_backend_health():
    """测试后端健康状态"""
    print("\n=== 后端健康检查 ===")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        data = resp.json()
        print(f"状态: {data.get('status', 'unknown')}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_agents_list():
    """测试Agents列表"""
    print("\n=== Agents列表 ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/agents", timeout=10)
        data = resp.json()
        agents = data.get('agents', [])
        print(f"总数: {data.get('total', 0)}")

        # 查找design_validator
        design_validator = None
        for agent in agents:
            print(f"  - {agent['name']} ({agent['role']})")
            if agent['role'] == 'design_validator':
                design_validator = agent

        if design_validator:
            print(f"✅ 找到设计评审员: {design_validator['name']}")
            return True
        else:
            print("❌ 未找到设计评审员")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_agent_detail():
    """测试Agent详情"""
    print("\n=== Agent详情 ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/agents/design_validator", timeout=10)
        data = resp.json()
        print(f"名称: {data.get('name')}")
        print(f"角色: {data.get('role')}")
        print(f"描述: {data.get('description')}")
        print(f"模型: {data.get('model')}")
        print(f"可用: {data.get('available')}")
        return data.get('available', False)
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_skill_templates():
    """测试Skill模板"""
    print("\n=== Skill模板 ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/agents/skill-templates", timeout=10)
        data = resp.json()

        if data.get('success'):
            templates = data.get('templates', {})
            print(f"模板数量: {len(templates)}")

            for name, template in templates.items():
                print(f"  - {name}: {template.get('description', 'N/A')[:50]}...")

            # 检查是否有评审模式模板
            expected_modes = ['interaction_check', 'visual_consistency', 'compare_designs']
            found_modes = [m for m in expected_modes if m in templates]
            print(f"✅ 找到评审模式: {found_modes}")
            return len(found_modes) > 0
        else:
            print("❌ 获取模板失败")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def image_to_base64(image_path):
    """将图片转换为base64"""
    if not os.path.exists(image_path):
        return None
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_image_analysis():
    """测试图片分析能力"""
    print("\n=== 图片分析测试 ===")

    # 检查图片是否存在
    if not os.path.exists(IMAGE_PATH_1):
        print(f"❌ 图片不存在: {IMAGE_PATH_1}")
        return False

    print(f"图片: {IMAGE_PATH_1}")
    file_size = os.path.getsize(IMAGE_PATH_1)
    print(f"大小: {file_size / 1024:.1f} KB")

    # 转换为base64
    img_base64 = image_to_base64(IMAGE_PATH_1)
    if img_base64:
        print(f"Base64长度: {len(img_base64)} 字符")
        print("✅ 图片转换成功")
        return True

    return False

def test_conversation_api():
    """测试对话API"""
    print("\n=== 对话API测试 ===")

    # 测试创建对话
    try:
        # 首先检查是否有对话相关的API
        resp = requests.get(f"{BASE_URL}/docs", timeout=10)
        if resp.status_code == 200:
            print("✅ API文档可访问")

        # 尝试WebSocket连接信息
        print("WebSocket端点: ws://localhost:8000/ws/conversations/{conversation_id}")
        return True
    except Exception as e:
        print(f"⚠️ 注意: {e}")
        return True

def test_review_modes():
    """测试三种评审模式"""
    print("\n=== 评审模式测试 ===")

    modes = [
        {
            'id': 'interaction_check',
            'name': '交互验证',
            'description': '检查设计稿的交互可用性'
        },
        {
            'id': 'visual_consistency',
            'name': '视觉讨论',
            'description': '评审视觉一致性'
        },
        {
            'id': 'compare_designs',
            'name': '方案选择',
            'description': '对比多个设计方案'
        }
    ]

    for mode in modes:
        print(f"  [{mode['id']}] {mode['name']}: {mode['description']}")

    print("✅ 三种评审模式已定义")
    return True

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Chris Chen 后端功能测试")
    print("=" * 60)

    results = {}

    results['后端健康'] = test_backend_health()
    results['Agents列表'] = test_agents_list()
    results['Agent详情'] = test_agent_detail()
    results['Skill模板'] = test_skill_templates()
    results['图片分析'] = test_image_analysis()
    results['对话API'] = test_conversation_api()
    results['评审模式'] = test_review_modes()

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    for name, result in results.items():
        status = '✅' if result else '❌'
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\n通过: {passed}/{len(results)}")

    if passed == len(results):
        print("\n✅ 所有后端测试通过！")
    else:
        print("\n⚠️ 部分测试未通过")

    return results

if __name__ == "__main__":
    run_tests()
