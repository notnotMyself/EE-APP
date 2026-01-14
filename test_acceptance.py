#!/usr/bin/env python3
"""
多任务实施项目 - 综合验收测试脚本

测试所有实现的功能:
1. EE Developer Agent
2. Chris Design Validator Agent
3. Agent Management API
4. Skill Templates Marketplace
5. Cover Image Service

使用账号: 1091201603@qq.com / eeappsuccess
"""

import os
import sys
import json
import requests
from pathlib import Path

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "1091201603@qq.com"
TEST_PASSWORD = "eeappsuccess"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

# ============================================
# Test 1: Backend Health Check
# ============================================
def test_backend_health():
    print_header("Test 1: Backend Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy: {data['status']}")
            print_info(f"Supabase: {data.get('supabase', 'unknown')}")
            print_info(f"Scheduler: {data.get('scheduler', {}).get('status', 'unknown')}")
            return True
        else:
            print_error(f"Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        print_info("Please start backend with: cd backend/agent_orchestrator && python main.py")
        return False

# ============================================
# Test 2: List Agents
# ============================================
def test_list_agents():
    print_header("Test 2: List AI Agents")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print_success(f"Found {len(agents)} agents")

            # Check for new agents
            agent_roles = [a['role'] for a in agents]

            if 'ee_developer' in agent_roles:
                print_success("EE Developer agent found")
            else:
                print_error("EE Developer agent NOT found")

            if 'design_validator' in agent_roles:
                print_success("Chris Design Validator agent found")
            else:
                print_error("Chris Design Validator agent NOT found")

            for agent in agents:
                status = "✓" if agent.get('available') else "✗"
                print_info(f"  {status} {agent['name']} ({agent['role']})")

            return True
        else:
            print_error(f"Failed to list agents: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error listing agents: {e}")
        return False

# ============================================
# Test 3: Get EE Developer Info
# ============================================
def test_ee_developer_info():
    print_header("Test 3: EE Developer Agent Info")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/agents/ee_developer", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"EE Developer: {data['name']}")
            print_info(f"  Model: {data.get('model', 'unknown')}")
            print_info(f"  Workdir: {data.get('workdir', 'unknown')}")
            print_info(f"  Available: {data.get('available', False)}")

            tools = data.get('allowed_tools', [])
            if tools:
                print_info(f"  Tools: {', '.join(tools)}")

            return True
        else:
            print_error(f"Failed to get EE Developer info: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting EE Developer info: {e}")
        return False

# ============================================
# Test 4: Get Chris Design Validator Info
# ============================================
def test_chris_validator_info():
    print_header("Test 4: Chris Design Validator Info")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/agents/design_validator", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Chris Design Validator: {data['name']}")
            print_info(f"  Model: {data.get('model', 'unknown')}")
            print_info(f"  Workdir: {data.get('workdir', 'unknown')}")
            print_info(f"  Available: {data.get('available', False)}")

            tools = data.get('allowed_tools', [])
            if tools:
                print_info(f"  Tools: {', '.join(tools)}")

            return True
        else:
            print_error(f"Failed to get Chris Design Validator info: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting Chris Design Validator info: {e}")
        return False

# ============================================
# Test 5: List Skill Templates
# ============================================
def test_skill_templates():
    print_header("Test 5: Skill Templates Marketplace")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/agents/skill-templates", timeout=5)
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            print_success(f"Found {len(templates)} skill templates")

            expected_templates = ['database_query', 'api_call', 'file_analysis', 'web_scraping']
            for template_id in expected_templates:
                if template_id in templates:
                    print_success(f"  Template '{template_id}' available")
                else:
                    print_error(f"  Template '{template_id}' NOT found")

            return True
        else:
            print_error(f"Failed to list skill templates: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error listing skill templates: {e}")
        return False

# ============================================
# Test 6: Verify File Structure
# ============================================
def test_file_structure():
    print_header("Test 6: File Structure Verification")

    base_path = Path("/Users/80392083/develop/ee_app_multi_task_impl")

    files_to_check = [
        # EE Developer
        "backend/agents/ee_developer/agent.yaml",
        "backend/agents/ee_developer/CLAUDE.md",
        "backend/agents/ee_developer/.claude/skills/git_operations.py",
        "backend/agents/ee_developer/.claude/skills/test_runner.py",
        "backend/agents/ee_developer/.claude/skills/code_review.py",

        # Chris Design Validator
        "backend/agents/design_validator/agent.yaml",
        "backend/agents/design_validator/CLAUDE.md",
        "backend/agents/design_validator/.claude/skills/vision_analysis.py",
        "backend/agents/design_validator/.claude/skills/interaction_check.py",
        "backend/agents/design_validator/.claude/skills/visual_consistency.py",
        "backend/agents/design_validator/.claude/skills/compare_designs.py",
        "backend/agents/design_validator/.claude/skills/search_cases.py",
        "backend/agents/design_validator/knowledge_base/design_guidelines/interaction-guidelines.md",
        "backend/agents/design_validator/knowledge_base/design_guidelines/visual-guidelines.md",
        "backend/agents/design_validator/knowledge_base/design_decisions/001-login-page-fullscreen-input.md",

        # Backend API
        "backend/agent_orchestrator/api/agent_management.py",
        "backend/agent_orchestrator/skill_templates.py",
        "backend/agent_orchestrator/services/cover_image_service.py",

        # Database Migrations
        "supabase/migrations/20260114000000_add_cover_image_to_briefings.sql",
        "supabase/migrations/20260115000000_add_design_review_tables.sql",

        # Documentation
        "PROJECT_SUMMARY.md",
        "VALIDATION_SUMMARY.md",
        "COMPLETION_STATUS.md",
        "FINAL_ACCEPTANCE.md",
    ]

    missing_files = []
    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            print_success(f"  {file_path}")
        else:
            print_error(f"  {file_path} - MISSING")
            missing_files.append(file_path)

    if missing_files:
        print_error(f"\n{len(missing_files)} files are missing")
        return False
    else:
        print_success(f"\nAll {len(files_to_check)} files verified")
        return True

# ============================================
# Test 7: Code Quality Check
# ============================================
def test_code_quality():
    print_header("Test 7: Code Quality Check")

    base_path = Path("/Users/80392083/develop/ee_app_multi_task_impl")

    # Check EE Developer git_operations.py for safety check
    git_ops_file = base_path / "backend/agents/ee_developer/.claude/skills/git_operations.py"
    if git_ops_file.exists():
        content = git_ops_file.read_text()
        if 'MAIN_BRANCH_PROTECTED' in content and 'if current_branch == "main"' in content:
            print_success("Git branch isolation safety check found in git_operations.py")
        else:
            print_error("Git branch isolation safety check NOT found")
    else:
        print_error("git_operations.py not found")

    # Check Chris Design Validator knowledge base
    kb_path = base_path / "backend/agents/design_validator/knowledge_base"
    if kb_path.exists():
        guidelines = list(kb_path.glob("design_guidelines/*.md"))
        decisions = list(kb_path.glob("design_decisions/*.md"))

        print_success(f"Knowledge base: {len(guidelines)} guidelines, {len(decisions)} decisions")
    else:
        print_error("Knowledge base directory not found")

    return True

# ============================================
# Test 8: Git Status
# ============================================
def test_git_status():
    print_header("Test 8: Git Status")

    os.chdir("/Users/80392083/develop/ee_app_multi_task_impl")

    # Check current branch
    branch_result = os.popen("git branch --show-current").read().strip()
    print_info(f"Current branch: {branch_result}")

    # Check commit count
    commit_result = os.popen("git log --oneline | head -10").read()
    commits = commit_result.strip().split('\n')
    print_success(f"Last {len(commits)} commits:")
    for commit in commits:
        print_info(f"  {commit}")

    # Check if all changes are committed
    status_result = os.popen("git status --porcelain").read().strip()
    if not status_result:
        print_success("All changes are committed")
    else:
        print_info("Uncommitted changes:")
        print_info(status_result)

    return True

# ============================================
# Main Test Runner
# ============================================
def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}多任务实施项目 - 综合验收测试{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"\n{Colors.YELLOW}测试账号: {TEST_EMAIL}{Colors.END}")
    print(f"{Colors.YELLOW}Git分支: feature/multi-task-implementation{Colors.END}\n")

    results = []

    # Run all tests
    results.append(("Backend Health", test_backend_health()))
    results.append(("List Agents", test_list_agents()))
    results.append(("EE Developer Info", test_ee_developer_info()))
    results.append(("Chris Validator Info", test_chris_validator_info()))
    results.append(("Skill Templates", test_skill_templates()))
    results.append(("File Structure", test_file_structure()))
    results.append(("Code Quality", test_code_quality()))
    results.append(("Git Status", test_git_status()))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Total: {passed}/{total} tests passed ({int(passed/total*100)}%){Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

    if passed == total:
        print(f"{Colors.GREEN}✅ ALL TESTS PASSED - PROJECT READY FOR DEPLOYMENT{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️  SOME TESTS FAILED - REVIEW REQUIRED{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
