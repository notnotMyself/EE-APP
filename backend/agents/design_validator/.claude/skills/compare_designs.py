#!/usr/bin/env python3
"""
方案对比 - Prompt 模板生成器

模式 C: 方案对比与专业评估
从专家视角对比多个方案的可用性与体验差异
"""

import sys
import json


COMPARE_PROMPT = """# 模式 C: 方案对比与专业评估

**评审目标**: 从专家视角对比多个方案的可用性与体验差异

## 评估维度

### 1. 认知难度
- 用户理解设计意图所需的认知成本
- 信息架构是否清晰易懂
- 学习成本高低

### 2. 操作效率
- 完成任务所需的步骤数
- 操作复杂度
- 是否存在冗余操作

### 3. 决策负荷
- 用户需要做出的选择和判断数量
- 决策点是否过多
- 选项是否清晰明确

### 4. 符合预期
- 是否符合用户的心智模型
- 是否符合平台规范（iOS HIG / Material Design）
- 交互模式是否熟悉

### 5. 心理负担
- 操作过程中可能产生的焦虑或困惑
- 错误恢复的难易程度
- 容错性设计

## 输出格式

### 方案对比矩阵

| 维度 | 方案A | 方案B | ... |
|------|-------|-------|-----|
| **认知难度** | [具体分析] | [具体分析] | ... |
| **操作效率** | [具体分析] | [具体分析] | ... |
| **决策负荷** | [具体分析] | [具体分析] | ... |
| **符合预期** | [具体分析] | [具体分析] | ... |
| **心理负担** | [具体分析] | [具体分析] | ... |

### 各方案优缺点

#### 方案 A
- ✅ 优点: ...
- ❌ 缺点: ...

#### 方案 B
- ✅ 优点: ...
- ❌ 缺点: ...

### 推荐方案

**推荐: [方案X]**

**理由**:
1. [具体理由]
2. [具体理由]

**需要注意的风险**:
- [风险点]

**备选方案说明**:
[在什么条件下可以选择其他方案]

## 参考资料

查阅知识库中的历史方案对比：
- `knowledge_base/design_decisions/` - 历史设计决策
- `knowledge_base/case_studies/` - 成功案例

## 注意事项

- ⚠️ 从专业角度客观分析
- ⚠️ 不做主观美学评价
- ⚠️ 识别具体问题，不给综合评分
- ⚠️ 基于用户场景和业务目标给出推荐
"""


def generate_prompt(
    design_context: str = "",
    core_task: str = "",
    user_persona: str = "",
    schemes: list = None
) -> str:
    """生成方案对比的完整 prompt"""
    
    schemes_desc = ""
    if schemes:
        schemes_desc = "\n".join([f"- {s}" for s in schemes])
    else:
        schemes_desc = "请根据上传的设计稿识别各方案"
    
    prompt = f"""# 方案对比任务

## 设计背景

- **页面/功能**: {design_context or "请根据设计稿识别"}
- **核心任务**: {core_task or "请根据设计稿推断用户要完成的主要任务"}
- **目标用户**: {user_persona or "普通用户"}

## 待对比方案

{schemes_desc}

---

{COMPARE_PROMPT}

---

请分析各方案的设计稿，按照上述维度和格式输出对比结果。
"""
    return prompt


def main():
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {
            "success": True,
            "prompt": generate_prompt(),
            "usage": "将此 prompt 与多个设计方案图片一起发送给 Agent"
        }
    else:
        try:
            params = json.loads(input_data)
            result = {
                "success": True,
                "prompt": generate_prompt(
                    params.get("design_context", ""),
                    params.get("core_task", ""),
                    params.get("user_persona", ""),
                    params.get("schemes", [])
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
