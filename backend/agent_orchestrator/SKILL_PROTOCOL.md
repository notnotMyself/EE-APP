# Skill 协议规范

**版本**: 1.0
**更新日期**: 2026-01-12

## 目的

定义 AI Agent Skill 的标准接口，确保所有 Skill 具有一致的输入输出格式，便于 Agent 调用、测试和维护。

## 核心原则

1. **Stdin/Stdout 通信**: Skill 通过标准输入读取参数，通过标准输出返回结果
2. **JSON 格式**: 输入输出均使用 JSON 格式
3. **明确的错误处理**: 所有错误都通过 JSON 返回，不应让 Skill 崩溃
4. **超时控制**: 每个 Skill 应在合理时间内完成（默认 300 秒）
5. **幂等性**: 相同输入应产生相同输出（爬虫类除外）

---

## Skill 标准接口

### 输入格式

**通过 stdin 传递 JSON 对象：**

```json
{
    "action": "string",           // 必填：要执行的操作
    "params": {                   // 可选：操作参数
        "key": "value"
    },
    "context": {                  // 可选：上下文信息
        "agent_id": "uuid",
        "user_id": "uuid",
        "request_id": "string"
    }
}
```

**字段说明：**

- `action` (必填): 操作类型，由 Skill 定义支持的 action 列表
- `params` (可选): 操作参数，具体字段由 action 决定
- `context` (可选): 执行上下文，用于日志追踪和权限检查

### 输出格式

**通过 stdout 输出 JSON 对象：**

#### 成功响应

```json
{
    "success": true,
    "action": "string",           // 执行的操作
    "data": {},                   // 操作结果数据
    "message": "string",          // 可选：人类可读的消息
    "metadata": {                 // 可选：元数据
        "execution_time_ms": 1234,
        "items_count": 10
    }
}
```

#### 失败响应

```json
{
    "success": false,
    "action": "string",           // 尝试执行的操作
    "error": {
        "code": "ERROR_CODE",     // 错误代码
        "message": "错误描述",     // 错误消息
        "details": {}             // 可选：错误详情
    }
}
```

---

## Skill 文件结构

```
agents/{agent_role}/
├── agent.yaml                  # Agent 配置
├── CLAUDE.md                   # Agent 行为定义
└── .claude/
    └── skills/
        ├── {skill_name}.py     # Skill 实现
        └── README.md           # Skill 文档
```

### Skill 脚本模板

```python
#!/usr/bin/env python3
"""
{Skill Name}
{简短描述}

输入格式 (stdin JSON):
{
    "action": "action_name",
    "params": {...}
}

输出格式 (stdout JSON):
{
    "success": true,
    "data": {...}
}
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# 配置
SKILL_DIR = Path(__file__).parent
AGENT_DIR = SKILL_DIR.parent.parent
TIMEOUT = 300  # 秒


def handle_action_1(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 action_1"""
    # 实现逻辑
    return {
        "success": True,
        "data": {...}
    }


def handle_action_2(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 action_2"""
    # 实现逻辑
    return {
        "success": True,
        "data": {...}
    }


def main():
    """主入口"""
    try:
        # 读取输入
        input_data = json.loads(sys.stdin.read())
        action = input_data.get("action")
        params = input_data.get("params", {})

        # 路由到对应的处理函数
        if action == "action_1":
            result = handle_action_1(params)
        elif action == "action_2":
            result = handle_action_2(params)
        else:
            result = {
                "success": False,
                "error": {
                    "code": "UNKNOWN_ACTION",
                    "message": f"Unknown action: {action}",
                    "supported_actions": ["action_1", "action_2"]
                }
            }

        # 输出结果
        result["action"] = action
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        error_response = {
            "success": False,
            "error": {
                "code": "INVALID_JSON",
                "message": f"Failed to parse input JSON: {str(e)}"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)

    except Exception as e:
        error_response = {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Skill 调用方式

### 1. 命令行测试

```bash
# 单行 JSON
echo '{"action": "test", "params": {"key": "value"}}' | python3 skill.py

# 多行 JSON（更易读）
cat <<EOF | python3 skill.py
{
    "action": "test",
    "params": {
        "key": "value"
    }
}
EOF
```

### 2. Agent 调用（通过 Bash 工具）

```python
# 在 CLAUDE.md 的工作流程中
bash_result = bash_tool.execute(
    command=f"echo '{json.dumps(input_data)}' | python3 .claude/skills/skill_name.py",
    cwd=agent_workdir
)

# 解析结果
result = json.loads(bash_result.stdout)
if result["success"]:
    data = result["data"]
    # 处理数据
else:
    error = result["error"]
    # 处理错误
```

### 3. 定时任务调用（通过 JobExecutor）

```python
# JobExecutor 会自动构造输入并执行 Skill
executor.execute_skill(
    agent_role="dev_efficiency_analyst",
    skill_name="build_analysis",
    action="daily_briefing",
    params={}
)
```

---

## 常见 Action 约定

不同类型的 Skill 可以定义自己的 action，但建议遵循以下约定：

| Action | 用途 | 输入参数示例 | 输出数据示例 |
|--------|------|-------------|-------------|
| `analyze` | 分析数据 | `{"target": "ci_builds", "days": 7}` | `{"insights": [...], "metrics": {...}}` |
| `report` | 生成报告 | `{"type": "daily", "format": "markdown"}` | `{"report_path": "...", "content": "..."}` |
| `fetch` | 获取数据 | `{"source": "database", "query": "..."}` | `{"items": [...], "count": 10}` |
| `push` | 推送数据 | `{"destination": "supabase", "data": {...}}` | `{"pushed": true, "id": "..."}` |
| `full` | 完整流程 | 根据 Skill 定义 | 包含多个子操作的结果 |

---

## 错误代码约定

建议使用以下标准错误代码：

| 错误代码 | 含义 | 示例场景 |
|---------|------|---------|
| `INVALID_JSON` | JSON 解析失败 | 输入不是有效的 JSON |
| `UNKNOWN_ACTION` | 不支持的 action | action 不在支持列表中 |
| `MISSING_PARAM` | 缺少必填参数 | 缺少 `days` 参数 |
| `INVALID_PARAM` | 参数值无效 | `days=-1`（负数） |
| `TIMEOUT` | 执行超时 | 操作超过 300 秒 |
| `PERMISSION_DENIED` | 权限不足 | 无权访问数据源 |
| `DATA_NOT_FOUND` | 数据不存在 | 查询结果为空 |
| `EXTERNAL_SERVICE_ERROR` | 外部服务错误 | API 调用失败 |
| `INTERNAL_ERROR` | 内部错误 | 未预期的异常 |

---

## 超时和资源限制

| 限制项 | 默认值 | agent.yaml 配置 |
|-------|--------|----------------|
| 执行超时 | 300 秒 | `skills[].timeout` |
| 最大输出大小 | 10 MB | 不可配置 |
| 内存限制 | 无限制 | 由系统决定 |
| CPU 限制 | 无限制 | 由系统决定 |

**agent.yaml 示例：**

```yaml
skills:
  - name: long_running_task
    entry: .claude/skills/task.py
    timeout: 600  # 10 分钟
```

---

## 日志和调试

### Skill 内部日志

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 记录到 stderr（不影响 stdout 的 JSON 输出）
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

# 使用
logger.info("Processing started")
logger.error("Failed to connect to database")
```

### 调试模式

可以通过环境变量启用调试模式：

```bash
export SKILL_DEBUG=1
echo '{"action": "test"}' | python3 skill.py
```

在 Skill 中检查：

```python
DEBUG = os.getenv("SKILL_DEBUG") == "1"

if DEBUG:
    logger.debug(f"Input data: {input_data}")
```

---

## 测试规范

### 单元测试

```python
# test_skill.py
import json
import subprocess

def test_skill_action():
    input_data = {"action": "test", "params": {}}
    result = subprocess.run(
        ["python3", "skill.py"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["success"] == True
```

### 集成测试

```bash
# 在 agent 目录下运行
cd agents/{agent_role}

# 测试 Skill
echo '{"action": "test"}' | python3 .claude/skills/skill_name.py

# 检查输出
if [ $? -eq 0 ]; then
    echo "✅ Skill test passed"
else
    echo "❌ Skill test failed"
fi
```

---

## 最佳实践

### 1. 输入验证

```python
def validate_params(params: Dict, required: List[str]) -> Optional[Dict]:
    """验证必填参数"""
    missing = [k for k in required if k not in params]
    if missing:
        return {
            "success": False,
            "error": {
                "code": "MISSING_PARAM",
                "message": f"Missing required parameters: {missing}"
            }
        }
    return None
```

### 2. 超时控制

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Skill execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(TIMEOUT)  # 设置超时

try:
    # 执行操作
    result = do_work()
finally:
    signal.alarm(0)  # 取消超时
```

### 3. 资源清理

```python
def main():
    resources = []
    try:
        # 打开资源
        db = open_database()
        resources.append(db)

        # 执行操作
        result = process(db)
        print(json.dumps(result))

    finally:
        # 清理资源
        for resource in resources:
            resource.close()
```

### 4. 进度报告（可选）

对于长时间运行的 Skill，可以通过 stderr 报告进度：

```python
import sys

print("Processing...", file=sys.stderr)
# 执行操作
print("50% complete", file=sys.stderr)
# 继续执行
print("100% complete", file=sys.stderr)

# 最终结果输出到 stdout
print(json.dumps(result))
```

---

## 示例 Skill

### 1. 简单的数据分析 Skill

```python
#!/usr/bin/env python3
import json
import sys

def analyze(params):
    days = params.get("days", 7)
    # 模拟分析
    return {
        "success": True,
        "data": {
            "average": 85.3,
            "trend": "improving",
            "days_analyzed": days
        }
    }

def main():
    try:
        input_data = json.loads(sys.stdin.read())
        action = input_data.get("action")

        if action == "analyze":
            result = analyze(input_data.get("params", {}))
        else:
            result = {
                "success": False,
                "error": {"code": "UNKNOWN_ACTION", "message": f"Unknown action: {action}"}
            }

        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(e)}}))

if __name__ == "__main__":
    main()
```

---

## 版本历史

- **1.0** (2026-01-12): 初始版本，定义基础协议规范
