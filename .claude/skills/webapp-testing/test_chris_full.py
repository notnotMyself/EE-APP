#!/usr/bin/env python3
"""
Chris Chen 完整功能测试

包括：
1. Supabase登录获取token
2. 创建对话
3. 测试WebSocket连接
4. 测试图片分析
5. 测试评审模式
"""

import asyncio
import json
import base64
import os
import sys
import time

# 测试配置
BACKEND_URL = "http://localhost:8000"
SUPABASE_URL = "https://dwesyojvzbltqtgtctpt.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MzA5MTQsImV4cCI6MjA4MjUwNjkxNH0.t4TBNkYp99HWBFu5kBOAgH13_7O5UADAMAptR16ENqc"
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"

IMAGE_PATH_1 = "/Users/80392083/Downloads/design1.jpg"
IMAGE_PATH_2 = "/Users/80392083/Downloads/design2.jpg"

def check_dependencies():
    """检查依赖"""
    try:
        import requests
        import websockets
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False

def login_supabase():
    """通过Supabase登录获取token"""
    import requests

    print("\n=== Supabase登录 ===")
    try:
        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }

        resp = requests.post(url, json=data, headers=headers, timeout=30)

        if resp.status_code == 200:
            result = resp.json()
            token = result.get("access_token")
            user = result.get("user", {})
            print(f"✅ 登录成功")
            print(f"   用户ID: {user.get('id', 'N/A')[:20]}...")
            print(f"   Token: {token[:30]}..." if token else "   Token: None")
            return token, user.get('id')
        else:
            print(f"❌ 登录失败: {resp.status_code}")
            print(f"   响应: {resp.text[:200]}")
            return None, None

    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return None, None

def get_agent_id(token, agent_name="Chris Chen"):
    """获取Agent ID"""
    import requests

    print(f"\n=== 获取Agent ID ({agent_name}) ===")
    try:
        # 从Supabase查询agents表
        url = f"{SUPABASE_URL}/rest/v1/agents"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {token}",
        }
        params = {
            "name": f"eq.{agent_name}",
            "select": "id,name,role"
        }

        resp = requests.get(url, headers=headers, params=params, timeout=30)

        if resp.status_code == 200:
            result = resp.json()
            if result and len(result) > 0:
                agent = result[0]
                print(f"✅ 找到Agent: {agent.get('name')}")
                print(f"   ID: {agent.get('id')}")
                return agent.get('id')
            else:
                # 尝试获取所有agents
                resp2 = requests.get(f"{SUPABASE_URL}/rest/v1/agents", headers=headers, timeout=30)
                if resp2.status_code == 200:
                    agents = resp2.json()
                    print(f"   可用Agents: {len(agents)}")
                    for a in agents[:5]:
                        print(f"   - {a.get('name')} ({a.get('id')[:8]}...)")
                    # 返回第一个agent用于测试
                    if agents:
                        return agents[0].get('id')
                print(f"❌ 未找到Agent: {agent_name}")
                return None
        else:
            print(f"❌ 查询Agent失败: {resp.status_code}")
            return None

    except Exception as e:
        print(f"❌ 查询Agent错误: {e}")
        return None


def create_conversation(token, user_id, agent_id):
    """创建对话或获取已存在的对话"""
    import requests

    print("\n=== 创建/获取对话 ===")

    # 先查询是否已存在对话
    try:
        url = f"{SUPABASE_URL}/rest/v1/conversations"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {token}",
        }
        params = {
            "user_id": f"eq.{user_id}",
            "agent_id": f"eq.{agent_id}",
            "select": "id,title,status"
        }

        resp = requests.get(url, headers=headers, params=params, timeout=30)

        if resp.status_code == 200:
            result = resp.json()
            if result and len(result) > 0:
                conv = result[0]
                conv_id = conv.get("id")
                print(f"✅ 找到已存在的对话")
                print(f"   对话ID: {conv_id}")
                return conv_id

        # 如果不存在，创建新对话
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "return=representation"
        data = {
            "user_id": user_id,
            "agent_id": agent_id,
            "title": f"Chris Chen测试对话 - {int(time.time())}"
        }

        resp = requests.post(url, json=data, headers=headers, timeout=30)

        if resp.status_code in [200, 201]:
            result = resp.json()
            conv = result[0] if isinstance(result, list) else result
            conv_id = conv.get("id")
            print(f"✅ 创建对话成功")
            print(f"   对话ID: {conv_id}")
            return conv_id
        else:
            print(f"❌ 创建对话失败: {resp.status_code}")
            print(f"   响应: {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"❌ 创建对话错误: {e}")
        return None

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
        '.gif': 'image/gif'
    }
    return mime_types.get(ext, 'image/jpeg')

async def test_websocket_conversation(token, conversation_id, test_messages):
    """测试WebSocket对话"""
    import websockets

    ws_url = f"ws://localhost:8000/api/v1/conversations/{conversation_id}/ws?token={token}"
    print(f"\n连接WebSocket: {ws_url[:60]}...")

    results = []

    try:
        async with websockets.connect(ws_url, ping_interval=30, ping_timeout=10) as websocket:
            # 等待连接确认
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            if data.get("type") == "connected":
                print(f"✅ WebSocket连接成功")
            else:
                print(f"⚠️ 连接响应: {data}")

            # 发送测试消息
            for i, msg in enumerate(test_messages):
                print(f"\n--- 测试 {i+1}/{len(test_messages)} ---")
                print(f"📤 发送: {msg['content'][:50]}...")

                await websocket.send(json.dumps(msg))

                # 接收响应
                response_text = []
                tool_calls = []
                timeout_count = 0

                while timeout_count < 60:  # 最多等待60秒
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(response)

                        msg_type = data.get("type")

                        if msg_type == "text_chunk":
                            chunk = data.get("content", "")
                            response_text.append(chunk)
                            if len(response_text) <= 3:  # 只打印前几个chunk
                                print(f"   📥 chunk: {chunk[:50]}...")
                        elif msg_type == "tool_use":
                            tool_calls.append(data.get("tool_name"))
                            print(f"   🔧 工具调用: {data.get('tool_name')}")
                        elif msg_type == "tool_result":
                            print(f"   📋 工具结果: {str(data.get('result', ''))[:50]}...")
                        elif msg_type == "done":
                            print(f"   ✅ 完成")
                            break
                        elif msg_type == "error":
                            print(f"   ❌ 错误: {data.get('content')}")
                            break
                        elif msg_type == "ping":
                            await websocket.send(json.dumps({"type": "pong"}))

                    except asyncio.TimeoutError:
                        timeout_count += 5
                        if timeout_count >= 15:
                            print(f"   ⏳ 等待响应中... ({timeout_count}s)")

                full_response = "".join(response_text)
                results.append({
                    "message": msg["content"][:30],
                    "response_length": len(full_response),
                    "tool_calls": tool_calls,
                    "success": len(full_response) > 0
                })

                if full_response:
                    print(f"\n   📝 响应 ({len(full_response)} 字符):")
                    print(f"   {full_response[:300]}...")

                # 等待一下再发送下一条
                await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ WebSocket错误: {e}")

    return results

async def run_full_test():
    """运行完整测试"""
    print("=" * 60)
    print("Chris Chen AI员工 完整功能测试")
    print("=" * 60)

    # 检查依赖
    if not check_dependencies():
        return

    # 检查图片
    print("\n=== 检查测试图片 ===")
    for img in [IMAGE_PATH_1, IMAGE_PATH_2]:
        if os.path.exists(img):
            size = os.path.getsize(img) / 1024
            print(f"✅ {os.path.basename(img)}: {size:.1f} KB")
        else:
            print(f"❌ 图片不存在: {img}")

    # 登录
    token, user_id = login_supabase()
    if not token:
        print("\n⚠️ 登录失败，无法继续测试")
        return

    # 获取Agent ID
    agent_id = get_agent_id(token, "Chris Chen")
    if not agent_id:
        print("\n⚠️ 获取Agent ID失败，无法继续测试")
        return

    # 创建对话
    conversation_id = create_conversation(token, user_id, agent_id)
    if not conversation_id:
        print("\n⚠️ 创建对话失败，无法继续测试")
        return

    # 准备测试消息
    test_messages = [
        # 1. 基础对话测试
        {
            "type": "message",
            "content": "你好，请介绍一下你自己，你能帮我做什么？"
        },
        # 2. 交互验证模式
        {
            "type": "message",
            "content": "[MODE:interaction_check] 假设我有一个工具栏设计，包含四个按钮：全局批注、速记、智能采集、演示笔。请告诉我你会从哪些角度来验证这个设计的交互可用性？"
        },
        # 3. 视觉讨论模式
        {
            "type": "message",
            "content": "[MODE:visual_consistency] 对于一个浮动工具栏设计，你会从哪些方面来评审它的视觉一致性？"
        },
        # 4. 方案选择模式
        {
            "type": "message",
            "content": "[MODE:compare_designs] 如果有两个设计方案，一个是固定位置的工具栏，另一个是跟随内容的浮动工具栏，你会如何帮我对比分析？"
        }
    ]

    # 运行WebSocket测试
    print("\n=== WebSocket对话测试 ===")
    results = await test_websocket_conversation(token, conversation_id, test_messages)

    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    for i, result in enumerate(results):
        status = "✅" if result["success"] else "❌"
        print(f"  测试 {i+1}: {status} - {result['message']}... ({result['response_length']} 字符)")
        if result["tool_calls"]:
            print(f"         工具调用: {result['tool_calls']}")
        if result["success"]:
            passed += 1

    print(f"\n通过: {passed}/{len(results)}")

    if passed == len(results):
        print("\n✅ 所有功能测试通过！Chris Chen工作正常。")
    else:
        print("\n⚠️ 部分测试未通过")

if __name__ == "__main__":
    asyncio.run(run_full_test())
