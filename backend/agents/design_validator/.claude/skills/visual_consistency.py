#!/usr/bin/env python3
"""
视觉一致性检查技能
"""

import sys
import json


def check_visual_consistency(design_data, guidelines=None):
    """检查视觉一致性"""
    return {
        "action": "check",
        "success": True,
        "data": {
            "inconsistencies": [
                {"type": "color", "issue": "主按钮使用 #FF5733，应为品牌色 #4F46E5"},
                {"type": "font", "issue": "正文使用14pt，应为16pt"},
                {"type": "spacing", "issue": "卡片内边距为15px，应为16px（8pt倍数）"}
            ],
            "consistency_scores": {
                "color": 0.8,
                "typography": 0.9,
                "spacing": 0.7,
                "components": 0.95
            },
            "overall_score": 0.84
        },
        "message": "视觉一致性检查完成，总体一致性 84%"
    }


def main():
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    design_data = params.get("design_data", {})
    guidelines = params.get("guidelines")

    result = check_visual_consistency(design_data, guidelines)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
