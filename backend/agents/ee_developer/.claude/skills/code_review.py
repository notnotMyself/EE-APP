#!/usr/bin/env python3
"""
代码审查技能 - 基本的静态分析和风格检查
"""

import sys
import json
import subprocess
from pathlib import Path


REPO_DIR = Path(__file__).parent.parent.parent.parent.parent / "ee_app_claude"


def review_code(files):
    """审查代码文件"""
    issues = []

    for file_path in files:
        full_path = REPO_DIR / file_path

        if not full_path.exists():
            issues.append({
                "file": file_path,
                "type": "error",
                "message": "文件不存在"
            })
            continue

        # Python文件检查
        if file_path.endswith(".py"):
            # 使用flake8进行代码检查（如果安装）
            try:
                result = subprocess.run(
                    ["flake8", "--max-line-length=120", str(full_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.stdout:
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            issues.append({
                                "file": file_path,
                                "type": "warning",
                                "message": line
                            })
            except FileNotFoundError:
                # flake8未安装，跳过
                pass
            except Exception as e:
                issues.append({
                    "file": file_path,
                    "type": "error",
                    "message": f"检查失败: {str(e)}"
                })

        # Dart文件检查
        elif file_path.endswith(".dart"):
            # 使用dart analyze进行检查
            try:
                result = subprocess.run(
                    ["dart", "analyze", str(full_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=REPO_DIR / "ai_agent_app"
                )

                if result.stdout and "No issues found!" not in result.stdout:
                    issues.append({
                        "file": file_path,
                        "type": "warning",
                        "message": result.stdout.strip()
                    })
            except FileNotFoundError:
                # dart未安装，跳过
                pass
            except Exception as e:
                issues.append({
                    "file": file_path,
                    "type": "error",
                    "message": f"检查失败: {str(e)}"
                })

        # 基本检查：文件大小
        file_size = full_path.stat().st_size
        if file_size > 1024 * 1024:  # 1MB
            issues.append({
                "file": file_path,
                "type": "warning",
                "message": f"文件过大: {file_size / 1024:.1f} KB"
            })

    return {
        "action": "review",
        "success": True,
        "data": {
            "issues": issues,
            "files_reviewed": len(files),
            "issues_found": len(issues)
        },
        "message": f"审查完成，发现 {len(issues)} 个问题"
    }


def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    files = params.get("files", [])

    if not files:
        result = {
            "action": "review",
            "success": False,
            "code": "MISSING_PARAMETER",
            "message": "缺少files参数"
        }
    else:
        result = review_code(files)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
