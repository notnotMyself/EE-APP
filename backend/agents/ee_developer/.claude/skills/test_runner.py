#!/usr/bin/env python3
"""
测试运行技能 - 运行pytest和flutter test
"""

import sys
import json
import subprocess
from pathlib import Path


REPO_DIR = Path(__file__).parent.parent.parent.parent.parent / "ee_app_claude"


def run_tests(test_type, path=""):
    """运行测试"""
    try:
        if test_type == "flutter":
            # Flutter测试
            cwd = REPO_DIR / "ai_agent_app"
            cmd = ["flutter", "test"]
            if path:
                cmd.append(path)

        elif test_type == "python":
            # Python测试
            cwd = REPO_DIR / "backend"
            cmd = ["pytest", "-v"]
            if path:
                cmd.append(path)

        else:
            return {
                "action": "run",
                "success": False,
                "code": "UNKNOWN_TYPE",
                "message": f"未知测试类型: {test_type}"
            }

        # 运行测试
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=600
        )

        passed = result.returncode == 0

        return {
            "action": "run",
            "success": True,
            "data": {
                "passed": passed,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            },
            "message": f"测试{'通过' if passed else '失败'}"
        }

    except subprocess.TimeoutExpired:
        return {
            "action": "run",
            "success": False,
            "code": "TIMEOUT",
            "message": "测试运行超时（600秒）"
        }
    except Exception as e:
        return {
            "action": "run",
            "success": False,
            "code": "EXCEPTION",
            "message": str(e)
        }


def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    test_type = params.get("type", "flutter")
    path = params.get("path", "")

    result = run_tests(test_type, path)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
