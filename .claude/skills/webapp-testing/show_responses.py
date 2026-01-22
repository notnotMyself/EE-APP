#!/usr/bin/env python3
"""显示Chris Chen三种评审模式的完整响应"""

import asyncio
import json
import requests
import websockets

BACKEND_URL = "http://localhost:8000"
SUPABASE_URL = "https://dwesyojvzbltqtgtctpt.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MzA5MTQsImV4cCI6MjA4MjUwNjkxNH0.t4TBNkYp99HWBFu5kBOAgH13_7O5UADAMAptR16ENqc"
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"

def login():
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    resp = requests.post(url, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}, headers=headers, timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        return result.get("access_token"), result.get("user", {}).get("id")
    return None, None

def get_conversation(token, user_id):
    headers = {"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}
    # 获取Chris Chen的agent_id
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/agents", headers=headers, params={"name": "eq.Chris Chen"}, timeout=30)
    if resp.status_code == 200 and resp.json():
        agent_id = resp.json()[0]["id"]
        # 获取对话
        resp2 = requests.get(f"{SUPABASE_URL}/rest/v1/conversations", headers=headers,
                            params={"user_id": f"eq.{user_id}", "agent_id": f"eq.{agent_id}"}, timeout=30)
        if resp2.status_code == 200 and resp2.json():
            return resp2.json()[0]["id"]
    return None

async def get_response(token, conversation_id, message):
    ws_url = f"ws://localhost:8000/api/v1/conversations/{conversation_id}/ws?token={token}"

    async with websockets.connect(ws_url, ping_interval=30) as websocket:
        # 等待连接
        await asyncio.wait_for(websocket.recv(), timeout=5.0)

        # 发送消息
        await websocket.send(json.dumps({"type": "message", "content": message}))

        # 接收响应
        response_text = []
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                data = json.loads(response)
                if data.get("type") == "text_chunk":
                    response_text.append(data.get("content", ""))
                elif data.get("type") == "done":
                    break
                elif data.get("type") == "error":
                    return f"错误: {data.get('content')}"
                elif data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                break

        return "".join(response_text)

async def main():
    print("登录中...")
    token, user_id = login()
    if not token:
        print("登录失败")
        return

    conversation_id = get_conversation(token, user_id)
    if not conversation_id:
        print("获取对话失败")
        return

    modes = [
        ("交互验证", "[MODE:interaction_check] 假设我有一个工具栏设计，包含四个按钮：全局批注、速记、智能采集、演示笔。请告诉我你会从哪些角度来验证这个设计的交互可用性？"),
        ("视觉讨论", "[MODE:visual_consistency] 对于一个浮动工具栏设计，你会从哪些方面来评审它的视觉一致性？"),
        ("方案选择", "[MODE:compare_designs] 如果有两个设计方案，一个是固定位置的工具栏，另一个是跟随内容的浮动工具栏，你会如何帮我对比分析？"),
    ]

    for mode_name, message in modes:
        print(f"\n{'='*80}")
        print(f"【{mode_name}模式】")
        print(f"{'='*80}")
        print(f"\n📤 问题: {message[message.find(']')+2:]}\n")
        print("-"*80)

        response = await get_response(token, conversation_id, message)
        print(f"\n📥 Chris Chen 回复:\n")
        print(response)
        print()

if __name__ == "__main__":
    asyncio.run(main())
