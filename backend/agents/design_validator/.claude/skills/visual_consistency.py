#!/usr/bin/env python3
"""
视觉一致性检查 - Prompt 模板生成器

模式 B: 视觉一致性与清晰度验证
检查视觉设计的层级、一致性和潜在误导性
"""

import sys
import json


VISUAL_CHECK_PROMPT = """# 模式 B: 视觉一致性与清晰度验证

**评审目标**: 检查视觉设计的层级、一致性和潜在误导性

## 检查维度

### 1. 颜色使用
- 是否符合品牌色板？
- 颜色对比度是否达标？（WCAG AA级 >= 4.5:1，大文字 >= 3:1）
- 是否过度使用颜色？
- 颜色语义是否正确？（红色=错误/危险，绿色=成功，橙色=警告）

### 2. 字体字号
- 是否遵循 Type Scale？（推荐: 12/14/16/20/24/32/48）
- 最小字号是否 >= 12pt？
- 标题层级是否清晰？（H1 > H2 > H3）
- 行高是否合理？（推荐 1.4-1.6）

### 3. 间距布局
- 是否遵循 8pt Grid？（间距为 8 的倍数: 8/16/24/32/48）
- 元素对齐是否规范？
- 留白是否合理？
- 信息分组是否清晰？（相关元素靠近，无关元素分开）

### 4. 视觉层级
- 主次信息是否分明？
- 关键操作是否突出？（主按钮 vs 次按钮）
- 视觉流向是否自然？（F型/Z型阅读模式）
- 是否存在误导用户的设计？

### 5. 组件一致性
- 是否使用了设计系统中的标准组件？
- 同类元素样式是否统一？（所有卡片、所有按钮）
- 是否有重复造轮子的情况？

## 输出格式

### 问题清单

| 问题 | 严重程度 | 涉及元素 | 修复建议 |
|------|----------|----------|----------|
| [具体描述] | 高/中/低 | [位置] | [具体建议] |

### 一致性评估

- ✅/⚠️/❌ **颜色**: [评估说明]
- ✅/⚠️/❌ **字体**: [评估说明]
- ✅/⚠️/❌ **间距**: [评估说明]
- ✅/⚠️/❌ **层级**: [评估说明]
- ✅/⚠️/❌ **组件**: [评估说明]

### 优先修复建议

1. [最重要的修复项]
2. ...

## 参考规范

查阅知识库获取公司设计规范：
- `knowledge_base/design_guidelines/visual-guidelines.md` - 视觉规范
- `knowledge_base/design_guidelines/interaction-guidelines.md` - 交互规范

## 注意事项

- ⚠️ 基于设计原则客观分析，不做主观美学评价
- ⚠️ 识别具体问题，给出可操作的修复建议
- ⚠️ 优先关注影响用户理解的问题
"""


def generate_prompt(design_context: str = "", specific_concerns: str = "") -> str:
    """生成视觉一致性检查的完整 prompt"""
    
    prompt = f"""# 视觉一致性检查任务

## 设计背景

- **页面/功能**: {design_context or "请根据设计稿识别"}
- **特别关注**: {specific_concerns or "无，进行全面检查"}

---

{VISUAL_CHECK_PROMPT}

---

请分析设计稿，按照上述维度和格式输出检查结果。
"""
    return prompt


def main():
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {
            "success": True,
            "prompt": generate_prompt(),
            "usage": "将此 prompt 与设计稿图片一起发送给 Agent"
        }
    else:
        try:
            params = json.loads(input_data)
            result = {
                "success": True,
                "prompt": generate_prompt(
                    params.get("design_context", ""),
                    params.get("specific_concerns", "")
                ),
                "params": params
            }
        except json.JSONDecodeError as e:
            result = {
                "success": False,
                "error": f"JSON 解析错误: {str(e)}"
            }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
