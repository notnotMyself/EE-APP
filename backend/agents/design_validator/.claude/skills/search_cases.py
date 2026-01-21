#!/usr/bin/env python3
"""
知识库索引 - 告诉 Agent 去哪里找参考资料

这个 skill 提供知识库的目录结构和搜索建议。
Agent 使用自己的 Read/Grep 能力查阅具体内容。
"""

import sys
import json
from pathlib import Path


# 知识库根目录
KNOWLEDGE_BASE = Path(__file__).parent.parent.parent / "knowledge_base"


def get_knowledge_index() -> dict:
    """获取知识库索引"""
    
    index = {
        "knowledge_base_path": str(KNOWLEDGE_BASE),
        "structure": {},
        "search_tips": []
    }
    
    # 扫描知识库目录结构
    directories = {
        "design_guidelines": "设计规范（交互规范、视觉规范）",
        "design_decisions": "历史设计决策（ADR 格式）",
        "case_studies": "成功案例和问题案例",
        "user_feedback": "用户反馈汇总"
    }
    
    for dir_name, description in directories.items():
        dir_path = KNOWLEDGE_BASE / dir_name
        files = []
        
        if dir_path.exists():
            for f in dir_path.glob("*.md"):
                files.append(f.name)
        
        index["structure"][dir_name] = {
            "description": description,
            "path": str(dir_path),
            "files": files
        }
    
    # 搜索建议
    index["search_tips"] = [
        "使用 Read 工具直接读取规范文件，如: knowledge_base/design_guidelines/interaction-guidelines.md",
        "使用 Grep 搜索关键词，如: grep -r '登录' knowledge_base/design_decisions/",
        "查看 INDEX.md 获取知识库概览: knowledge_base/INDEX.md",
        "设计决策文件命名格式: XXX-功能名-决策要点.md"
    ]
    
    return index


def get_search_prompt(query: str, category: str = None) -> str:
    """生成搜索建议 prompt"""
    
    index = get_knowledge_index()
    
    if category and category in index["structure"]:
        search_path = index["structure"][category]["path"]
        search_scope = f"`{search_path}/`"
    else:
        search_scope = "`knowledge_base/`"
    
    prompt = f"""# 知识库搜索任务

## 搜索关键词
`{query}`

## 搜索范围
{search_scope}

## 知识库结构

"""
    
    for dir_name, info in index["structure"].items():
        files_list = ", ".join(info["files"][:5]) if info["files"] else "（暂无文件）"
        if len(info["files"]) > 5:
            files_list += f" 等 {len(info['files'])} 个文件"
        prompt += f"""### {dir_name}/
- **说明**: {info["description"]}
- **文件**: {files_list}

"""
    
    prompt += f"""## 搜索建议

1. 使用 Grep 搜索包含关键词的文件:
   ```bash
   grep -r -l "{query}" {search_scope}
   ```

2. 读取相关文件获取详细内容

3. 如果是查找设计规范，直接读取:
   - `knowledge_base/design_guidelines/interaction-guidelines.md`
   - `knowledge_base/design_guidelines/visual-guidelines.md`

## 开始搜索

请使用 Grep 和 Read 工具查找与「{query}」相关的案例和规范。
"""
    
    return prompt


def main():
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        # 无输入时返回知识库索引
        index = get_knowledge_index()
        result = {
            "success": True,
            "action": "index",
            "data": index,
            "message": "知识库索引获取成功，请使用 Read/Grep 查阅具体内容"
        }
    else:
        try:
            params = json.loads(input_data)
            action = params.get("action", "search")
            
            if action == "index":
                # 获取索引
                index = get_knowledge_index()
                result = {
                    "success": True,
                    "action": "index",
                    "data": index
                }
            elif action == "search":
                # 生成搜索 prompt
                query = params.get("query", "")
                category = params.get("category")
                
                if not query:
                    result = {
                        "success": False,
                        "error": "缺少 query 参数"
                    }
                else:
                    result = {
                        "success": True,
                        "action": "search",
                        "prompt": get_search_prompt(query, category),
                        "params": params
                    }
            else:
                result = {
                    "success": False,
                    "error": f"未知操作: {action}"
                }
                
        except json.JSONDecodeError as e:
            result = {
                "success": False,
                "error": f"JSON 解析错误: {str(e)}"
            }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
