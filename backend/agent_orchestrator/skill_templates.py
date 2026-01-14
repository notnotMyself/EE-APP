"""
技能市场 - 预置技能模板

提供常用技能模板，降低开发门槛
"""

from typing import Dict, List, Any


class SkillTemplate:
    """技能模板基类"""

    def __init__(
        self,
        name: str,
        display_name: str,
        description: str,
        script_template: str,
        parameters: List[Dict[str, Any]],
        category: str = "general",
        icon: str = "code",
    ):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.script_template = script_template
        self.parameters = parameters
        self.category = category
        self.icon = icon

    def generate_script(self, params: Dict[str, Any]) -> str:
        """根据参数生成脚本"""
        return self.script_template.format(**params)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "parameters": self.parameters,
            "category": self.category,
            "icon": self.icon,
        }


# ============================================
# 预置技能模板
# ============================================

DATABASE_QUERY_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
数据库查询技能 - 查询{db_type}数据库
\"\"\"

import sys
import json
import pymysql  # 或 psycopg2, 根据数据库类型
from typing import Dict, Any


def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    # 数据库连接配置
    db_config = {{
        "host": "{db_host}",
        "port": {db_port},
        "user": "{db_user}",
        "password": "{db_password}",
        "database": "{db_name}",
    }}

    try:
        # 连接数据库
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # 执行查询
        query = params.get("query")
        cursor.execute(query)

        # 获取结果
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # 转换为字典列表
        rows = [dict(zip(column_names, row)) for row in results]

        # 返回结果
        output = {{
            "action": "query",
            "success": True,
            "data": {{"rows": rows, "count": len(rows)}},
            "message": f"查询成功，返回 {{len(rows)}} 行数据"
        }}

        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        output = {{
            "action": "query",
            "success": False,
            "code": "QUERY_FAILED",
            "message": str(e)
        }}
        print(json.dumps(output, ensure_ascii=False))

    finally:
        if 'connection' in locals():
            connection.close()


if __name__ == "__main__":
    main()
"""

API_CALL_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
API调用技能 - 调用HTTP API
\"\"\"

import sys
import json
import httpx
from typing import Dict, Any


async def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    # API配置
    base_url = "{api_base_url}"
    api_key = "{api_key}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 构建请求
            method = params.get("method", "GET").upper()
            endpoint = params.get("endpoint", "")
            headers = {{
                "Authorization": f"Bearer {{api_key}}",
                "Content-Type": "application/json",
            }}
            headers.update(params.get("headers", {{}}))

            url = f"{{base_url}}/{{endpoint}}"

            # 发送请求
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(
                    url, headers=headers, json=params.get("body", {{}})
                )
            elif method == "PUT":
                response = await client.put(
                    url, headers=headers, json=params.get("body", {{}})
                )
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {{method}}")

            response.raise_for_status()

            # 返回结果
            output = {{
                "action": "api_call",
                "success": True,
                "data": response.json(),
                "message": f"API调用成功: {{method}} {{url}}"
            }}
            print(json.dumps(output, ensure_ascii=False))

    except httpx.HTTPError as e:
        output = {{
            "action": "api_call",
            "success": False,
            "code": "API_ERROR",
            "message": str(e)
        }}
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""

FILE_ANALYSIS_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
文件分析技能 - 分析CSV/Excel文件
\"\"\"

import sys
import json
import pandas as pd
from typing import Dict, Any


def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    file_path = params.get("file_path")
    analysis_type = params.get("analysis_type", "summary")

    try:
        # 读取文件
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {{file_path}}")

        # 执行分析
        result = {{}}

        if analysis_type == "summary":
            # 基础统计摘要
            result = {{
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "summary": df.describe().to_dict(),
            }}

        elif analysis_type == "head":
            # 前N行
            n = params.get("n", 10)
            result = {{
                "rows": df.head(n).to_dict(orient="records")
            }}

        elif analysis_type == "filter":
            # 筛选
            condition = params.get("condition")  # 例如: "age > 18"
            filtered_df = df.query(condition)
            result = {{
                "rows": filtered_df.to_dict(orient="records"),
                "count": len(filtered_df)
            }}

        # 返回结果
        output = {{
            "action": "file_analysis",
            "success": True,
            "data": result,
            "message": f"文件分析完成: {{analysis_type}}"
        }}
        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        output = {{
            "action": "file_analysis",
            "success": False,
            "code": "ANALYSIS_FAILED",
            "message": str(e)
        }}
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
"""

WEB_SCRAPING_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
网页抓取技能 - 抓取网页内容
\"\"\"

import sys
import json
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any


async def main():
    # 从stdin读取参数
    input_data = sys.stdin.read()
    params = json.loads(input_data)

    url = params.get("url")
    selector = params.get("selector", "")  # CSS选择器

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 获取网页
            response = await client.get(url)
            response.raise_for_status()

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取内容
            if selector:
                elements = soup.select(selector)
                content = [{{
                    "text": elem.get_text(strip=True),
                    "html": str(elem),
                    "attrs": elem.attrs
                }} for elem in elements]
            else:
                # 默认提取所有文本
                content = soup.get_text(strip=True)

            # 返回结果
            output = {{
                "action": "web_scraping",
                "success": True,
                "data": {{
                    "url": url,
                    "content": content,
                    "title": soup.title.string if soup.title else None
                }},
                "message": f"网页抓取成功: {{url}}"
            }}
            print(json.dumps(output, ensure_ascii=False))

    except httpx.HTTPError as e:
        output = {{
            "action": "web_scraping",
            "success": False,
            "code": "SCRAPING_FAILED",
            "message": str(e)
        }}
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""


# ============================================
# 技能模板注册表
# ============================================

SKILL_TEMPLATES: Dict[str, SkillTemplate] = {
    "database_query": SkillTemplate(
        name="database_query",
        display_name="数据库查询",
        description="查询MySQL/PostgreSQL数据库，执行SQL查询并返回结果",
        script_template=DATABASE_QUERY_TEMPLATE,
        parameters=[
            {
                "name": "db_type",
                "type": "select",
                "label": "数据库类型",
                "options": ["MySQL", "PostgreSQL"],
                "default": "MySQL",
                "required": True,
            },
            {
                "name": "db_host",
                "type": "text",
                "label": "数据库主机",
                "default": "localhost",
                "required": True,
            },
            {
                "name": "db_port",
                "type": "number",
                "label": "端口",
                "default": 3306,
                "required": True,
            },
            {
                "name": "db_user",
                "type": "text",
                "label": "用户名",
                "required": True,
            },
            {
                "name": "db_password",
                "type": "password",
                "label": "密码",
                "required": True,
            },
            {
                "name": "db_name",
                "type": "text",
                "label": "数据库名称",
                "required": True,
            },
        ],
        category="data",
        icon="database",
    ),
    "api_call": SkillTemplate(
        name="api_call",
        display_name="API调用",
        description="调用HTTP API，支持GET/POST/PUT/DELETE请求",
        script_template=API_CALL_TEMPLATE,
        parameters=[
            {
                "name": "api_base_url",
                "type": "text",
                "label": "API Base URL",
                "placeholder": "https://api.example.com",
                "required": True,
            },
            {
                "name": "api_key",
                "type": "password",
                "label": "API Key",
                "required": False,
            },
        ],
        category="integration",
        icon="api",
    ),
    "file_analysis": SkillTemplate(
        name="file_analysis",
        display_name="文件分析",
        description="分析CSV/Excel文件，提供统计摘要、筛选等功能",
        script_template=FILE_ANALYSIS_TEMPLATE,
        parameters=[],
        category="data",
        icon="file",
    ),
    "web_scraping": SkillTemplate(
        name="web_scraping",
        display_name="网页抓取",
        description="抓取网页内容，支持CSS选择器",
        script_template=WEB_SCRAPING_TEMPLATE,
        parameters=[],
        category="integration",
        icon="web",
    ),
}


def get_all_templates() -> List[Dict[str, Any]]:
    """获取所有技能模板"""
    return [template.to_dict() for template in SKILL_TEMPLATES.values()]


def get_template(name: str) -> SkillTemplate:
    """获取指定技能模板"""
    if name not in SKILL_TEMPLATES:
        raise ValueError(f"Template '{name}' not found")
    return SKILL_TEMPLATES[name]


def generate_skill_script(template_name: str, params: Dict[str, Any]) -> str:
    """根据模板生成技能脚本"""
    template = get_template(template_name)
    return template.generate_script(params)
