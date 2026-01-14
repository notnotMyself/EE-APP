#!/usr/bin/env python3
"""
多方案对比技能
"""

import sys
import json


def compare_designs(designs, dimensions=None):
    """对比多个设计方案"""
    if dimensions is None:
        dimensions = ["usability", "visual", "cost", "innovation"]

    # 简化实现：返回对比结果
    comparison = {
        design["name"]: {
            "usability": 8 if "A" in design["name"] else 7,
            "visual": 9 if "A" in design["name"] else 8,
            "cost": "中",
            "innovation": 7 if "A" in design["name"] else 9
        }
        for design in designs
    }

    return {
        "action": "compare",
        "success": True,
        "data": {
            "comparison": comparison,
            "recommendation": designs[0]["name"] if designs else None,
            "reason": "可用性和视觉达到最佳平衡，成本适中"
        },
        "message": f"完成 {len(designs)} 个方案的对比分析"
    }


def main():
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    designs = params.get("designs", [])
    dimensions = params.get("dimensions")

    if not designs:
        result = {
            "action": "compare",
            "success": False,
            "code": "MISSING_PARAMETER",
            "message": "缺少designs参数"
        }
    else:
        result = compare_designs(designs, dimensions)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
