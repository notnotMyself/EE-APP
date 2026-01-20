#!/usr/bin/env python3
"""
清空存量样板数据，使用AI员工skills生成真实简报数据

Usage:
    python3 backend/scripts/generate_real_briefings.py
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "ai_agent_platform" / "backend"))

from supabase import create_client

# Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dwesyojvzbltqtgtctpt.supabase.co")

# Skills脚本路径
GERRIT_SKILL_PATH = project_root / "backend" / "agents" / "dev_efficiency_analyst" / ".claude" / "skills" / "gerrit_analysis.py"


def load_env_file(env_path: Path) -> dict:
    """加载.env文件"""
    env_vars = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


def get_supabase_client():
    """获取Supabase客户端"""
    # 尝试从环境变量获取
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not key:
        # 尝试从多个.env文件读取
        env_paths = [
            project_root / "ai_agent_platform" / "backend" / ".env",
            project_root / "backend" / "agent_orchestrator" / ".env",
            project_root / ".env",
        ]
        
        for env_path in env_paths:
            env_vars = load_env_file(env_path)
            key = env_vars.get("SUPABASE_SERVICE_ROLE_KEY") or env_vars.get("SUPABASE_SERVICE_KEY") or env_vars.get("SUPABASE_KEY")
            if key:
                print(f"   ℹ️  从 {env_path.name} 加载配置")
                break
    
    if not key:
        raise ValueError("SUPABASE_SERVICE_KEY not found in environment or .env files")
    
    return create_client(SUPABASE_URL, key)


def clear_sample_briefings(supabase):
    """清空存量的样板简报数据"""
    print("\n" + "=" * 60)
    print("🗑️  清空存量样板简报数据")
    print("=" * 60)
    
    try:
        # 获取当前简报数量
        result = supabase.table("briefings").select("id", count="exact").execute()
        current_count = result.count or 0
        print(f"   当前简报数量: {current_count}")
        
        if current_count > 0:
            # 删除所有简报
            supabase.table("briefings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print(f"   ✅ 已删除 {current_count} 条简报")
        else:
            print("   ℹ️  没有需要清理的简报")
        
        return True
    except Exception as e:
        print(f"   ❌ 清空失败: {e}")
        return False


def run_skill(action: str, params: dict) -> dict:
    """运行skills脚本"""
    params["action"] = action
    input_json = json.dumps(params)
    
    result = subprocess.run(
        ["python3", str(GERRIT_SKILL_PATH)],
        input=input_json,
        capture_output=True,
        text=True,
        cwd=str(GERRIT_SKILL_PATH.parent)
    )
    
    if result.returncode != 0:
        print(f"   ❌ Skill执行失败: {result.stderr}")
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON解析失败: {e}")
        return None


def generate_briefing_from_skill(days: int, departments: list = None) -> dict:
    """使用skill生成简报数据"""
    params = {"days": days}
    if departments:
        params["departments"] = departments
    
    # 生成briefing
    briefing = run_skill("briefing", params)
    if not briefing:
        return None
    
    # 生成ui_schema
    ui_schema = run_skill("ui_schema", params)
    
    return {
        "briefing": briefing,
        "ui_schema": ui_schema
    }


def create_briefing_record(supabase, agent_id: str, user_id: str, skill_result: dict, period_label: str) -> dict:
    """创建简报记录
    
    新版本：
    - summary: 使用briefing的summary（Markdown格式的有价值内容）
    - context_data.analysis_result.response: 使用full_report（完整Markdown报告）
    """
    briefing_data = skill_result["briefing"]
    ui_schema = skill_result.get("ui_schema")
    
    # 提取核心数据
    findings = briefing_data.get("findings", [])
    key_data = briefing_data.get("key_data", {})
    full_report = briefing_data.get("full_report", "")
    
    # 构建actions - 根据发现添加具体的操作
    actions = [
        {"label": "查看完整报告", "action": "view_report", "data": {}},
    ]
    
    # 根据发现添加具体的对话prompt
    if findings:
        top_finding = findings[0]
        if top_finding.get("type") == "借单风险":
            actions.append({
                "label": "分析借单原因", 
                "action": "start_conversation", 
                "data": {"prompt": f"请详细分析Story #{key_data.get('suspicious_stories', [{}])[0].get('issue_id', '')}的借单情况，包括参与者和可能原因"}
            })
        elif top_finding.get("type") == "工作分散":
            actions.append({
                "label": "分析工作分配", 
                "action": "start_conversation", 
                "data": {"prompt": f"请分析{key_data.get('scattered_people', [{}])[0].get('name', '')}的工作分散情况，是否需要调整"}
            })
        else:
            actions.append({
                "label": "深入分析", 
                "action": "start_conversation", 
                "data": {"prompt": "请帮我详细分析这些问题的根本原因"}
            })
    
    actions.append({"label": "已知悉", "action": "dismiss", "data": {}})
    
    # 映射priority（数据库只允许P0, P1, P2）
    raw_priority = briefing_data.get("priority", "P2")
    priority = raw_priority if raw_priority in ["P0", "P1", "P2"] else "P2"
    
    # 确定briefing_type
    severity = briefing_data.get("severity", "low")
    if severity == "high":
        briefing_type = "alert"
    elif severity == "medium":
        briefing_type = "insight"
    else:
        briefing_type = "summary"
    
    # 构建简报记录
    record = {
        "id": str(uuid4()),
        "agent_id": agent_id,
        "user_id": user_id,
        "briefing_type": briefing_type,
        "priority": priority,
        "title": briefing_data.get("title", f"{period_label}研发效能分析"),
        "summary": briefing_data.get("summary", ""),  # 现在是Markdown格式的有价值内容
        "impact": briefing_data.get("impact"),
        "actions": actions,
        "importance_score": 0.9 if severity == "high" else (0.7 if severity == "medium" else 0.5),
        "status": "new",
        "context_data": {
            "analysis_result": {
                # 完整的Markdown报告，用于"查看详情"
                "response": full_report if full_report else briefing_data.get("summary", ""),
                "metrics": briefing_data.get("metrics", {}),
                "findings": findings,
                "key_data": key_data
            },
            "generated_at": briefing_data.get("generated_at"),
            "period_days": briefing_data.get("analysis_period_days"),
            "should_push": briefing_data.get("should_push", False)
        },
        "created_at": datetime.utcnow().isoformat()
    }
    
    # 添加ui_schema（如果有）- 存储在context_data中
    if ui_schema:
        record["context_data"]["ui_schema"] = ui_schema
    
    return record


def main():
    print("\n" + "=" * 60)
    print("🚀 AI员工真实简报生成脚本")
    print("=" * 60)
    
    # 1. 获取Supabase客户端
    try:
        supabase = get_supabase_client()
        print("✅ Supabase连接成功")
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        return
    
    # 2. 获取研发效能分析官Agent
    try:
        agents = supabase.table("agents").select("id, name, role").eq("role", "dev_efficiency_analyst").execute()
        if not agents.data:
            print("❌ 未找到研发效能分析官Agent")
            return
        agent = agents.data[0]
        print(f"✅ 找到Agent: {agent['name']} (ID: {agent['id'][:8]}...)")
    except Exception as e:
        print(f"❌ 获取Agent失败: {e}")
        return
    
    # 3. 获取第一个用户
    try:
        users = supabase.table("users").select("id, email").limit(1).execute()
        if not users.data:
            print("❌ 未找到用户，请先创建用户")
            return
        user = users.data[0]
        print(f"✅ 找到用户: {user.get('email', 'unknown')}")
    except Exception as e:
        print(f"❌ 获取用户失败: {e}")
        return
    
    # 4. 清空存量数据
    if not clear_sample_briefings(supabase):
        print("⚠️  清空失败，继续生成新数据")
    
    # 5. 生成真实简报数据
    print("\n" + "=" * 60)
    print("📊 使用AI员工Skills生成真实简报")
    print("=" * 60)
    
    departments = ["系统开发部", "应用开发一部", "应用开发二部", "互联通信开发部"]
    briefings_to_create = []
    
    # 生成多个时间维度的简报
    analysis_configs = [
        {"days": 365, "label": "年度", "departments": departments},
        {"days": 90, "label": "季度", "departments": departments},
        {"days": 30, "label": "月度", "departments": departments},
    ]
    
    for config in analysis_configs:
        print(f"\n   📈 生成{config['label']}分析简报 ({config['days']}天)...")
        
        result = generate_briefing_from_skill(config["days"], config.get("departments"))
        if result:
            record = create_briefing_record(
                supabase,
                agent["id"],
                user["id"],
                result,
                config["label"]
            )
            briefings_to_create.append(record)
            print(f"      ✅ [{record['priority']}] {record['title'][:40]}...")
        else:
            print(f"      ⚠️  生成失败，跳过")
    
    # 6. 写入数据库
    print("\n" + "=" * 60)
    print("💾 写入数据库")
    print("=" * 60)
    
    if not briefings_to_create:
        print("   ⚠️  没有生成任何简报")
        return
    
    try:
        result = supabase.table("briefings").insert(briefings_to_create).execute()
        print(f"   ✅ 成功写入 {len(result.data)} 条简报")
        
        print("\n📋 已创建的简报：")
        for i, briefing in enumerate(result.data, 1):
            print(f"\n   {i}. [{briefing['priority']}] {briefing['title']}")
            print(f"      类型: {briefing['briefing_type']}")
            print(f"      重要性: {briefing['importance_score']}")
            has_ui = "✅" if briefing.get("ui_schema") else "❌"
            print(f"      UI Schema: {has_ui}")
            
    except Exception as e:
        print(f"   ❌ 写入失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✨ 完成！现在可以刷新前端查看真实简报了")
    print("=" * 60)


if __name__ == "__main__":
    main()

