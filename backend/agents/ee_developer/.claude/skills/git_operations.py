#!/usr/bin/env python3
"""
Git操作技能 - 分支创建、提交、推送、创建PR

核心功能：
1. create_feature_branch: 创建feature分支
2. commit: 提交到当前分支
3. push: 推送到远程
4. create_pr: 创建Pull Request
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


REPO_DIR = Path(__file__).parent.parent.parent.parent.parent / "ee_app_claude"


def run_command(cmd, cwd=REPO_DIR, timeout=120):
    """运行命令并返回结果"""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    return result


def create_feature_branch(description):
    """创建feature分支（基于main）"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    branch_name = f"feature/{description}-{timestamp}"

    # 1. 确保在main分支且是最新的
    checkout_main = run_command(["git", "checkout", "main"])
    if checkout_main.returncode != 0:
        return {
            "action": "create_feature_branch",
            "success": False,
            "code": "CHECKOUT_MAIN_FAILED",
            "message": f"切换到main分支失败: {checkout_main.stderr}"
        }

    pull_main = run_command(["git", "pull", "origin", "main"])
    if pull_main.returncode != 0:
        # 如果pull失败（可能没有upstream），继续尝试
        pass

    # 2. 创建并切换到新分支
    create_branch = run_command(["git", "checkout", "-b", branch_name])

    if create_branch.returncode == 0:
        return {
            "action": "create_feature_branch",
            "success": True,
            "data": {"branch_name": branch_name},
            "message": f"创建分支 {branch_name} 成功"
        }
    else:
        return {
            "action": "create_feature_branch",
            "success": False,
            "code": "BRANCH_CREATION_FAILED",
            "message": create_branch.stderr
        }


def git_commit(message, files=None):
    """提交到当前分支"""
    # 确保不在main分支
    current_branch_result = run_command(["git", "branch", "--show-current"])
    current_branch = current_branch_result.stdout.strip()

    if current_branch == "main":
        return {
            "action": "commit",
            "success": False,
            "code": "MAIN_BRANCH_PROTECTED",
            "message": "禁止直接提交到main分支，请先创建feature分支"
        }

    # git add
    if files:
        for file in files:
            run_command(["git", "add", file])
    else:
        run_command(["git", "add", "-A"])

    # git commit
    commit_result = run_command(["git", "commit", "-m", message])

    if commit_result.returncode == 0:
        # 获取commit hash
        commit_hash_result = run_command(["git", "rev-parse", "HEAD"])
        commit_hash = commit_hash_result.stdout.strip()

        return {
            "action": "commit",
            "success": True,
            "data": {
                "commit_hash": commit_hash,
                "branch": current_branch,
                "message": message
            },
            "message": f"提交成功: {commit_hash[:7]}"
        }
    else:
        return {
            "action": "commit",
            "success": False,
            "code": "COMMIT_FAILED",
            "message": commit_result.stderr
        }


def git_push():
    """推送当前分支到远程"""
    current_branch_result = run_command(["git", "branch", "--show-current"])
    current_branch = current_branch_result.stdout.strip()

    push_result = run_command(
        ["git", "push", "-u", "origin", current_branch],
        timeout=180
    )

    if push_result.returncode == 0:
        return {
            "action": "push",
            "success": True,
            "data": {"branch": current_branch},
            "message": f"推送到 {current_branch} 成功"
        }
    else:
        return {
            "action": "push",
            "success": False,
            "code": "PUSH_FAILED",
            "message": push_result.stderr
        }


def create_pr(title, body=""):
    """创建Pull Request"""
    current_branch_result = run_command(["git", "branch", "--show-current"])
    current_branch = current_branch_result.stdout.strip()

    # 使用gh CLI创建PR
    pr_result = run_command([
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--base", "main"
    ])

    if pr_result.returncode == 0:
        pr_url = pr_result.stdout.strip()
        return {
            "action": "create_pr",
            "success": True,
            "data": {"pr_url": pr_url, "branch": current_branch},
            "message": f"PR创建成功: {pr_url}"
        }
    else:
        return {
            "action": "create_pr",
            "success": False,
            "code": "PR_CREATION_FAILED",
            "message": pr_result.stderr
        }


def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    action = params.get("action")

    try:
        if action == "create_feature_branch":
            description = params.get("description", "task")
            result = create_feature_branch(description)

        elif action == "commit":
            message = params.get("message")
            files = params.get("files")
            if not message:
                result = {
                    "action": "commit",
                    "success": False,
                    "code": "MISSING_PARAMETER",
                    "message": "缺少commit message参数"
                }
            else:
                result = git_commit(message, files)

        elif action == "push":
            result = git_push()

        elif action == "create_pr":
            title = params.get("title")
            body = params.get("body", "")
            if not title:
                result = {
                    "action": "create_pr",
                    "success": False,
                    "code": "MISSING_PARAMETER",
                    "message": "缺少PR title参数"
                }
            else:
                result = create_pr(title, body)

        else:
            result = {
                "action": action or "unknown",
                "success": False,
                "code": "UNKNOWN_ACTION",
                "message": f"未知操作: {action}"
            }

        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        result = {
            "action": action or "unknown",
            "success": False,
            "code": "EXCEPTION",
            "message": str(e)
        }
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
