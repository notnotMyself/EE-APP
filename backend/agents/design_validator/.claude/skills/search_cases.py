#!/usr/bin/env python3
"""
历史案例检索技能 - 使用Grep搜索Markdown文件
"""

import sys
import json
import subprocess
from pathlib import Path
import yaml


KNOWLEDGE_BASE = Path(__file__).parent.parent / "knowledge_base"


def search_cases(query, category=None):
    """搜索历史案例"""
    matched_files = []

    # 确定搜索目录
    if category:
        search_dirs = [KNOWLEDGE_BASE / category]
    else:
        search_dirs = [
            KNOWLEDGE_BASE / "design_decisions",
            KNOWLEDGE_BASE / "case_studies"
        ]

    # 使用grep搜索
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        try:
            result = subprocess.run(
                ["grep", "-r", "-l", "-i", query, str(search_dir)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout:
                matched_files.extend(result.stdout.strip().split("\n"))
        except Exception:
            pass

    # 读取匹配的文件（前5个）
    cases = []
    for file_path in matched_files[:5]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析Markdown frontmatter
            metadata = {}
            body = content

            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        metadata = yaml.safe_load(parts[1])
                        body = parts[2].strip()
                    except Exception:
                        pass

            cases.append({
                "file": Path(file_path).name,
                "title": metadata.get("title", "未命名"),
                "category": metadata.get("category", "unknown"),
                "tags": metadata.get("tags", []),
                "date": metadata.get("date", ""),
                "excerpt": body[:300] + "..." if len(body) > 300 else body,
                "full_path": file_path
            })
        except Exception:
            pass

    return {
        "action": "search",
        "success": True,
        "data": {
            "cases": cases,
            "total": len(matched_files),
            "query": query
        },
        "message": f"找到 {len(cases)} 个相关案例"
    }


def get_guidelines(guideline_type="all"):
    """获取设计规范"""
    guidelines_dir = KNOWLEDGE_BASE / "design_guidelines"
    guidelines = {}

    type_mapping = {
        "interaction": "interaction-guidelines.md",
        "visual": "visual-guidelines.md",
        "brand": "brand-guidelines.md"
    }

    if guideline_type == "all":
        types_to_load = type_mapping.keys()
    else:
        types_to_load = [guideline_type] if guideline_type in type_mapping else []

    for gtype in types_to_load:
        file_path = guidelines_dir / type_mapping[gtype]
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    guidelines[gtype] = f.read()
            except Exception:
                pass

    return {
        "action": "get_guidelines",
        "success": True,
        "data": {"guidelines": guidelines},
        "message": f"获取了 {len(guidelines)} 个设计规范"
    }


def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    action = params.get("action", "search")

    if action == "search":
        query = params.get("query")
        category = params.get("category")

        if not query:
            result = {
                "action": "search",
                "success": False,
                "code": "MISSING_PARAMETER",
                "message": "缺少query参数"
            }
        else:
            result = search_cases(query, category)

    elif action == "get_guidelines":
        guideline_type = params.get("type", "all")
        result = get_guidelines(guideline_type)

    else:
        result = {
            "action": action,
            "success": False,
            "code": "UNKNOWN_ACTION",
            "message": f"未知操作: {action}"
        }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
