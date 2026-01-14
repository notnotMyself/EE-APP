#!/usr/bin/env python3
"""
AI News Crawler Skill
AI资讯追踪官技能 - 标准化入口，支持 Agent SDK 调用

功能：
1. 爬取 AI 资讯（ai-bot.cn, bestblogs.dev）
2. 生成简报（兼容 Flutter 信息流）
3. 推送到 Supabase 数据库

输入格式 (stdin JSON):
{
    "action": "crawl|briefing|push|full",
    "source": "aibot|bestblogs|all",
    "days": 3,
    "push": false
}

输出格式 (stdout JSON):
{
    "success": true,
    "action": "full",
    "data": {...},
    "briefing": {...},
    "pushed": false,
    "message": "..."
}
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# 获取脚本所在目录
SKILL_DIR = Path(__file__).parent
AGENT_DIR = SKILL_DIR.parent.parent
DATA_DIR = AGENT_DIR / "data"
REPORTS_DIR = AGENT_DIR / "reports"


def run_aibot_crawler(days: int = 3, report_type: str = "all") -> Dict[str, Any]:
    """运行 ai-bot.cn 爬虫"""
    script = AGENT_DIR / "crawl_aibot.py"
    
    cmd = [sys.executable, str(script), "--days", str(days), "--report", report_type]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(AGENT_DIR),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        success = result.returncode == 0
        
        # 尝试读取生成的简报文件
        briefing = None
        today = datetime.now().strftime("%Y-%m-%d")
        briefing_file = REPORTS_DIR / f"briefing_{today}.json"
        
        if briefing_file.exists():
            with open(briefing_file, 'r', encoding='utf-8') as f:
                briefing = json.load(f)
        
        return {
            "success": success,
            "source": "aibot",
            "output": result.stdout,
            "error": result.stderr if not success else None,
            "briefing": briefing
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "source": "aibot", "error": "Timeout after 120s"}
    except Exception as e:
        return {"success": False, "source": "aibot", "error": str(e)}


def run_bestblogs_crawler(days: int = 7, report_type: str = "briefing") -> Dict[str, Any]:
    """运行 bestblogs.dev 爬虫"""
    script = AGENT_DIR / "crawl_articles.py"
    
    cmd = [sys.executable, str(script), "--days", str(days), "--report", report_type]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(AGENT_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 可能需要更长时间
        )
        
        success = result.returncode == 0
        
        # 尝试读取生成的简报文件
        briefing = None
        today = datetime.now().strftime("%Y-%m-%d")
        briefing_file = REPORTS_DIR / f"briefing_articles_{today}.json"
        
        if briefing_file.exists():
            with open(briefing_file, 'r', encoding='utf-8') as f:
                briefing = json.load(f)
        
        return {
            "success": success,
            "source": "bestblogs",
            "output": result.stdout,
            "error": result.stderr if not success else None,
            "briefing": briefing
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "source": "bestblogs", "error": "Timeout after 300s"}
    except Exception as e:
        return {"success": False, "source": "bestblogs", "error": str(e)}


def push_to_feed(briefing: Dict[str, Any], agent_name: str = "AI资讯追踪官") -> bool:
    """推送简报到信息流"""
    import uuid
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        return False
    
    try:
        from supabase import create_client
        
        supabase = create_client(supabase_url, supabase_key)
        
        # 查找 Agent
        agents = supabase.table('agents').select('id').eq('role', 'ai_news_crawler').limit(1).execute()
        if not agents.data:
            return False
        
        agent_id = agents.data[0]['id']
        
        # 获取活跃用户
        users = supabase.table('users').select('id').eq('is_active', True).execute()
        if not users.data:
            return False
        
        # 批量创建简报
        briefings_to_insert = []
        for user in users.data:
            briefings_to_insert.append({
                'id': str(uuid.uuid4()),
                'agent_id': agent_id,
                'user_id': user['id'],
                'briefing_type': briefing.get('briefing_type', 'summary'),
                'priority': briefing.get('priority', 'P2'),
                'title': briefing['title'],
                'summary': briefing['summary'],
                'impact': briefing.get('impact'),
                'actions': briefing.get('actions', []),
                'context_data': briefing.get('context_data', {}),
                'importance_score': briefing.get('importance_score', 0.5),
                'status': 'new'
            })
        
        supabase.table('briefings').insert(briefings_to_insert).execute()
        return True
        
    except Exception as e:
        print(f"Push failed: {e}", file=sys.stderr)
        return False


def merge_briefings(briefings: list[Dict]) -> Optional[Dict]:
    """合并多个来源的简报为一个"""
    valid_briefings = [b for b in briefings if b and b.get('should_push')]
    
    if not valid_briefings:
        return None
    
    # 选择优先级最高的
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
    valid_briefings.sort(key=lambda x: priority_order.get(x.get('priority', 'P2'), 2))
    
    primary = valid_briefings[0]
    
    # 如果有多个来源，合并到 context_data
    if len(valid_briefings) > 1:
        primary['context_data']['merged_sources'] = [
            {
                'source': b.get('context_data', {}).get('source', 'unknown'),
                'priority': b.get('priority'),
                'key_news_count': len(b.get('key_news', []))
            }
            for b in valid_briefings
        ]
    
    return primary


def run_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行分析任务 - 主入口
    
    支持的 action:
    - crawl: 仅爬取数据
    - briefing: 爬取并生成简报
    - push: 爬取、生成简报并推送
    - full: 完整流程（爬取 + 简报 + 推送）
    """
    action = params.get("action", "briefing")
    source = params.get("source", "aibot")  # aibot, bestblogs, all
    days = params.get("days", 3)
    should_push = params.get("push", False) or action in ["push", "full"]
    
    results = {
        "success": True,
        "action": action,
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "crawl_results": [],
        "briefing": None,
        "pushed": False,
        "message": ""
    }
    
    briefings = []
    
    # 1. 爬取数据
    if source in ["aibot", "all"]:
        aibot_result = run_aibot_crawler(days=min(days, 7), report_type="all")
        results["crawl_results"].append(aibot_result)
        if aibot_result.get("briefing"):
            briefings.append(aibot_result["briefing"])
    
    if source in ["bestblogs", "all"]:
        bestblogs_result = run_bestblogs_crawler(days=days, report_type="briefing")
        results["crawl_results"].append(bestblogs_result)
        if bestblogs_result.get("briefing"):
            briefings.append(bestblogs_result["briefing"])
    
    # 2. 合并简报
    if action in ["briefing", "push", "full"]:
        merged = merge_briefings(briefings)
        if merged:
            results["briefing"] = merged
            results["message"] = f"生成简报成功，优先级: {merged.get('priority')}"
        else:
            results["message"] = "无值得推送的资讯"
    
    # 3. 推送到信息流
    if should_push and results.get("briefing"):
        briefing = results["briefing"]
        if briefing.get("should_push"):
            pushed = push_to_feed(briefing)
            results["pushed"] = pushed
            if pushed:
                results["message"] += "，已推送到信息流"
            else:
                results["message"] += "，推送失败（检查 Supabase 配置）"
        else:
            results["message"] += "，简报价值不足，跳过推送"
    
    # 检查是否有错误
    for crawl in results["crawl_results"]:
        if not crawl.get("success"):
            results["success"] = False
            results["message"] = f"爬取失败: {crawl.get('error')}"
            break
    
    return results


def main():
    """主入口 - 从 stdin 读取参数"""
    try:
        # 读取输入
        if not sys.stdin.isatty():
            input_data = sys.stdin.read().strip()
            if input_data:
                params = json.loads(input_data)
            else:
                params = {}
        else:
            # 交互模式，使用默认参数
            params = {"action": "briefing", "source": "aibot", "days": 1}
        
        # 执行分析
        result = run_analysis(params)
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        error_result = {
            "success": False,
            "error": f"Invalid JSON input: {e}",
            "usage": {
                "action": "crawl|briefing|push|full",
                "source": "aibot|bestblogs|all",
                "days": "1-7",
                "push": "true|false"
            }
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()


