#!/usr/bin/env python3
"""
Claude Agent SDK 诊断脚本

运行方式：
cd /home/ops/EE-APP/backend/agent_orchestrator
source .venv/bin/activate
python diagnose_claude_sdk.py
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def check_env_vars():
    """检查环境变量"""
    print_section("1. 环境变量检查")
    
    vars_to_check = [
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
    ]
    
    for var in vars_to_check:
        value = os.getenv(var)
        if value:
            if "TOKEN" in var or "KEY" in var:
                print(f"  ✅ {var}: 已设置 ({len(value)} 字符)")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")

def check_claude_settings():
    """检查 ~/.claude/settings.json"""
    print_section("2. Claude Settings 文件检查")
    
    settings_path = Path.home() / ".claude" / "settings.json"
    
    if not settings_path.exists():
        print(f"  ❌ 文件不存在: {settings_path}")
        print("  建议: 创建 ~/.claude/settings.json 文件")
        return
    
    print(f"  ✅ 文件存在: {settings_path}")
    
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        
        env = settings.get("env", {})
        print(f"  📄 内容:")
        for key, value in env.items():
            if "TOKEN" in key or "KEY" in key:
                print(f"     {key}: *** ({len(value)} 字符)")
            else:
                print(f"     {key}: {value}")
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")

def check_bundled_cli():
    """检查 bundled Claude CLI"""
    print_section("3. Claude CLI 检查")
    
    # 查找 bundled CLI
    import claude_agent_sdk
    sdk_path = Path(claude_agent_sdk.__file__).parent
    cli_path = sdk_path / "_bundled" / "claude"
    
    print(f"  SDK 路径: {sdk_path}")
    print(f"  CLI 路径: {cli_path}")
    
    if not cli_path.exists():
        print(f"  ❌ CLI 不存在!")
        return None
    
    print(f"  ✅ CLI 存在")
    
    # 检查权限
    import stat
    mode = os.stat(cli_path).st_mode
    is_executable = bool(mode & stat.S_IXUSR)
    print(f"  可执行权限: {'✅ 是' if is_executable else '❌ 否'}")
    
    # 检查版本
    try:
        result = subprocess.run(
            [str(cli_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"  CLI 版本输出:")
        if result.stdout:
            print(f"     stdout: {result.stdout.strip()}")
        if result.stderr:
            print(f"     stderr: {result.stderr.strip()}")
        print(f"  退出码: {result.returncode}")
    except Exception as e:
        print(f"  ❌ 运行失败: {e}")
    
    return cli_path

def test_network():
    """测试网络连通性"""
    print_section("4. 网络连通性测试")
    
    import urllib.request
    import urllib.error
    
    urls = [
        ("Anthropic 官方 API", "https://api.anthropic.com"),
        ("自定义 Gateway", os.getenv("ANTHROPIC_BASE_URL", "https://llm-gateway.oppoer.me")),
    ]
    
    for name, url in urls:
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"  ✅ {name}: 可访问 (HTTP {response.status})")
        except urllib.error.HTTPError as e:
            # HTTP 错误也算可达
            print(f"  ✅ {name}: 可访问 (HTTP {e.code})")
        except Exception as e:
            print(f"  ❌ {name}: 不可访问 ({type(e).__name__}: {e})")

async def test_sdk_query():
    """测试 SDK 调用"""
    print_section("5. Claude Agent SDK 测试")
    
    auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
    if not auth_token:
        print("  ⚠️  ANTHROPIC_AUTH_TOKEN 未设置，跳过 SDK 测试")
        return
    
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
        
        # 准备环境变量
        env = {
            "ANTHROPIC_BASE_URL": os.getenv("ANTHROPIC_BASE_URL", "https://llm-gateway.oppoer.me"),
            "ANTHROPIC_AUTH_TOKEN": auth_token,
        }
        
        print(f"  配置:")
        print(f"     BASE_URL: {env['ANTHROPIC_BASE_URL']}")
        print(f"     TOKEN: *** ({len(auth_token)} 字符)")
        
        options = ClaudeAgentOptions(
            system_prompt="你是一个测试助手。",
            env=env,
            max_turns=1,
        )
        
        print(f"  正在发送测试请求...")
        
        received_any = False
        async for message in query(prompt="请回复：测试成功", options=options):
            received_any = True
            msg_type = type(message).__name__
            print(f"  收到消息: {msg_type}")
            
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"  ✅ 文本响应: {block.text[:100]}...")
        
        if not received_any:
            print("  ⚠️  没有收到任何消息")
            
    except Exception as e:
        print(f"  ❌ SDK 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def test_anthropic_api_direct():
    """直接测试 Anthropic API"""
    print_section("6. 直接 API 测试 (绕过 SDK)")
    
    auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://llm-gateway.oppoer.me")
    
    if not auth_token:
        print("  ⚠️  ANTHROPIC_AUTH_TOKEN 未设置，跳过")
        return
    
    try:
        from anthropic import Anthropic
        
        client = Anthropic(
            api_key=auth_token,
            base_url=base_url,
        )
        
        print(f"  正在发送直接 API 请求...")
        print(f"  BASE_URL: {base_url}")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # 或 saas/claude-sonnet-4.5
            max_tokens=100,
            messages=[{"role": "user", "content": "回复：测试成功"}],
        )
        
        if response.content:
            print(f"  ✅ API 响应成功!")
            print(f"  响应: {response.content[0].text[:100]}...")
        
    except Exception as e:
        print(f"  ❌ API 测试失败: {type(e).__name__}: {e}")

def main():
    print("\n" + "🔍 Claude Agent SDK 诊断工具 ".center(60, "="))
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    check_env_vars()
    check_claude_settings()
    check_bundled_cli()
    test_network()
    
    # 同步测试
    test_anthropic_api_direct()
    
    # 异步测试
    asyncio.run(test_sdk_query())
    
    print_section("诊断完成")
    print("如果仍有问题，请检查:")
    print("  1. 确保 ANTHROPIC_AUTH_TOKEN 已正确设置")
    print("  2. 确保网络可以访问 API endpoint")
    print("  3. 检查 ~/.claude/settings.json 配置")
    print()

if __name__ == "__main__":
    main()

