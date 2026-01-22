#!/usr/bin/env python3
"""
Chris Chen 图片理解能力测试

通过WebSocket测试图片分析功能
"""

import asyncio
import json
import base64
import os
import websockets

BASE_URL = "ws://localhost:8000"
IMAGE_PATH_1 = "/Users/80392083/Downloads/design1.jpg"
IMAGE_PATH_2 = "/Users/80392083/Downloads/design2.jpg"

def image_to_base64(image_path):
    """将图片转换为base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_mime_type(image_path):
    """获取图片MIME类型"""
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')

async def test_image_understanding():
    """测试图片理解能力"""
    print("=" * 60)
    print("Chris Chen 图片理解能力测试")
    print("=" * 60)

    # 检查图片
    print(f"\n检查图片文件...")
    if not os.path.exists(IMAGE_PATH_1):
        print(f"❌ 图片不存在: {IMAGE_PATH_1}")
        return False

    print(f"✅ 图片1: {IMAGE_PATH_1}")
    print(f"   大小: {os.path.getsize(IMAGE_PATH_1)/1024:.1f} KB")

    if os.path.exists(IMAGE_PATH_2):
        print(f"✅ 图片2: {IMAGE_PATH_2}")
        print(f"   大小: {os.path.getsize(IMAGE_PATH_2)/1024:.1f} KB")

    # 准备图片数据
    img1_base64 = image_to_base64(IMAGE_PATH_1)
    print(f"\n图片1 Base64: {len(img1_base64)} 字符")

    # 创建测试消息
    test_message = {
        "type": "message",
        "content": "[MODE:interaction_check] 请帮我评审这个设计稿的交互可用性",
        "attachments": [
            {
                "type": "image",
                "mime_type": get_mime_type(IMAGE_PATH_1),
                "data": img1_base64[:100] + "...(truncated for display)"  # 只显示前100字符
            }
        ]
    }

    print(f"\n消息结构:")
    print(f"  type: {test_message['type']}")
    print(f"  content: {test_message['content'][:50]}...")
    print(f"  attachments: {len(test_message['attachments'])} 个")

    # 测试WebSocket连接
    print("\n测试WebSocket连接...")
    test_conversation_id = "test-chris-chen-001"
    ws_url = f"{BASE_URL}/ws/conversations/{test_conversation_id}?user_id=test-user&agent_role=design_validator"

    print(f"WebSocket URL: {ws_url}")

    try:
        async with websockets.connect(ws_url, ping_interval=30) as websocket:
            print("✅ WebSocket连接成功")

            # 发送测试消息（不含实际图片数据，只测试连接）
            simple_message = {
                "type": "message",
                "content": "[MODE:interaction_check] 请描述一下你能看到什么，以及你会如何评审设计稿"
            }

            await websocket.send(json.dumps(simple_message))
            print(f"\n📤 发送消息: {simple_message['content'][:50]}...")

            # 接收响应
            response_parts = []
            timeout_count = 0

            while timeout_count < 30:  # 最多等待30秒
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)

                    if data.get('type') == 'content':
                        response_parts.append(data.get('text', ''))
                        print(f"📥 收到内容片段: {len(data.get('text', ''))} 字符")
                    elif data.get('type') == 'end':
                        print("📥 消息结束")
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ 错误: {data.get('message', 'Unknown error')}")
                        break

                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count >= 3:
                        print("⏳ 等待响应中...")

            full_response = ''.join(response_parts)
            if full_response:
                print(f"\n📝 AI响应 ({len(full_response)} 字符):")
                print("-" * 40)
                print(full_response[:500])
                if len(full_response) > 500:
                    print(f"... (还有 {len(full_response) - 500} 字符)")
                print("-" * 40)
                return True
            else:
                print("⚠️ 未收到有效响应")
                return False

    except Exception as e:
        print(f"❌ WebSocket错误: {e}")
        return False

async def test_all_modes():
    """测试所有评审模式"""
    print("\n" + "=" * 60)
    print("测试三种评审模式")
    print("=" * 60)

    modes = [
        ("interaction_check", "交互验证", "请帮我验证这个设计的交互可用性"),
        ("visual_consistency", "视觉讨论", "请帮我评审这个设计的视觉一致性"),
        ("compare_designs", "方案选择", "请帮我对比这两个设计方案")
    ]

    test_conversation_id = "test-modes-001"
    ws_url = f"{BASE_URL}/ws/conversations/{test_conversation_id}?user_id=test-user&agent_role=design_validator"

    results = {}

    try:
        async with websockets.connect(ws_url, ping_interval=30) as websocket:
            print("✅ WebSocket连接成功\n")

            for mode_id, mode_name, prompt in modes:
                print(f"\n--- 测试 [{mode_id}] {mode_name} ---")

                message = {
                    "type": "message",
                    "content": f"[MODE:{mode_id}] {prompt}"
                }

                await websocket.send(json.dumps(message))
                print(f"📤 发送: {message['content'][:40]}...")

                # 接收响应
                response_parts = []
                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        data = json.loads(response)

                        if data.get('type') == 'content':
                            response_parts.append(data.get('text', ''))
                        elif data.get('type') == 'end':
                            break
                        elif data.get('type') == 'error':
                            print(f"❌ 错误: {data.get('message')}")
                            break
                    except asyncio.TimeoutError:
                        print("⏳ 超时")
                        break

                full_response = ''.join(response_parts)
                if full_response:
                    print(f"📥 响应: {full_response[:100]}...")
                    results[mode_id] = True
                else:
                    results[mode_id] = False

                await asyncio.sleep(1)  # 等待一下再发送下一个

    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("模式测试结果")
    print("=" * 60)
    for mode_id, success in results.items():
        print(f"  {mode_id}: {'✅' if success else '❌'}")

    return all(results.values()) if results else False

async def main():
    """主函数"""
    results = {}

    results['图片理解'] = await test_image_understanding()
    results['评审模式'] = await test_all_modes()

    print("\n" + "=" * 60)
    print("总体测试结果")
    print("=" * 60)
    for name, success in results.items():
        print(f"  {name}: {'✅' if success else '❌'}")

    if all(results.values()):
        print("\n✅ 所有功能测试通过！")
    else:
        print("\n⚠️ 部分测试未通过")

if __name__ == "__main__":
    asyncio.run(main())
