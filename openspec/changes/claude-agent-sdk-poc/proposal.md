# Claude Agent SDK POC 验证

## 概述

验证 Claude Agent SDK (`claude-agent-sdk`) 在本项目中的可行性，为后续迁移奠定基础。

## 背景

### 当前架构
- 使用 Anthropic Python SDK 直接调用 Claude API
- 自实现工具执行层（bash, read_file, write_file, web_fetch）
- 自实现 agentic loop

### 目标架构
- 使用 Claude Agent SDK
- 利用 SDK 内置的 Agent 框架能力
- 通过 MCP 服务器扩展自定义工具

### 迁移动机
| 能力 | 当前实现 | Agent SDK |
|-----|---------|-----------|
| 工具调用循环 | 自己实现 while loop | SDK 自动处理 |
| 多步骤任务 | 自己维护状态 | 自动管理 |
| Sub-agent | 未实现 | 内置支持 |
| Skills | bash 调用脚本 | MCP 服务器 |
| 内置工具 | 4 个 | 10+ 个 |

## POC 验证范围

### 1. 基础功能验证 ✅
- [ ] 安装 `claude-agent-sdk`
- [ ] 验证 `query()` 基础查询
- [ ] 验证 `ClaudeSDKClient` 流式响应
- [ ] 验证 `cwd` 工作目录隔离

### 2. 工具调用验证
- [ ] 验证内置工具：Read, Write, Bash
- [ ] 验证 `allowed_tools` 权限控制
- [ ] 验证 `permission_mode` 自动授权

### 3. 自定义工具验证 (MCP)
- [ ] 创建简单的 MCP 工具（如 `gerrit_mock`）
- [ ] 验证 `@tool` 装饰器用法
- [ ] 验证 `create_sdk_mcp_server`
- [ ] 验证工具调用和结果返回

### 4. Sub-agent 验证
- [ ] 定义多个 AgentDefinition
- [ ] 验证 Agent 调用和切换
- [ ] 验证不同 Agent 的工具隔离

### 5. 与 FastAPI 集成
- [ ] 在 FastAPI 中调用 Agent SDK
- [ ] 验证 SSE 流式响应
- [ ] 验证错误处理

### 6. 自定义 API Gateway 验证
- [ ] 验证是否支持自定义 base_url
- [ ] 验证 `llm-gateway.oppoer.me` 兼容性
- [ ] 如不支持，确定替代方案

## 技术验证代码

### POC 脚本位置
```
backend/poc/
├── 01_basic_query.py      # 基础查询
├── 02_tools.py            # 工具调用
├── 03_mcp_tools.py        # 自定义 MCP 工具
├── 04_subagents.py        # Sub-agent
├── 05_fastapi_integration.py  # FastAPI 集成
└── README.md              # POC 说明
```

### 示例代码：基础查询
```python
# backend/poc/01_basic_query.py
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(
        cwd="/Users/80392083/develop/ee_app_claude/backend/agents/dev_efficiency_analyst",
        max_turns=3
    )

    async for message in query(
        prompt="请读取 CLAUDE.md 文件并总结你的职责",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

if __name__ == "__main__":
    anyio.run(main)
```

### 示例代码：自定义 MCP 工具
```python
# backend/poc/03_mcp_tools.py
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient
import anyio

@tool("get_review_stats", "获取代码审查统计数据", {"days": int})
async def get_review_stats(args):
    # Mock 数据
    return {
        "content": [{
            "type": "text",
            "text": f"最近 {args['days']} 天的审查数据：\n- 总审查数: 150\n- 平均耗时: 18.5 小时\n- 返工率: 12%"
        }]
    }

async def main():
    server = create_sdk_mcp_server(
        name="dev_efficiency",
        tools=[get_review_stats]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"stats": server},
        allowed_tools=["mcp__stats__get_review_stats"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("请获取最近 7 天的代码审查统计")
        async for msg in client.receive_response():
            print(msg)

if __name__ == "__main__":
    anyio.run(main)
```

## 验证成功标准

| 验证项 | 成功标准 |
|-------|---------|
| 基础查询 | 能够成功获取 Claude 响应 |
| 工具调用 | 能够读取/写入文件，执行 bash |
| MCP 工具 | 自定义工具能被 Claude 调用 |
| Sub-agent | 能够在多个 Agent 间切换 |
| FastAPI | 能够通过 HTTP/SSE 暴露服务 |
| 自定义网关 | 能够使用内部 LLM Gateway |

## 风险与备选方案

### 风险 1：不支持自定义 API Gateway
- **影响**：无法使用内部 `llm-gateway.oppoer.me`
- **备选**：查阅 SDK 源码，确认配置方式；或通过环境变量/CLI 参数配置

### 风险 2：Claude Code CLI 依赖
- **影响**：SDK 底层调用 CLI，可能有额外依赖
- **备选**：确保服务器环境满足 CLI 运行条件

### 风险 3：性能开销
- **影响**：SDK 通过 subprocess 调用 CLI，可能有延迟
- **备选**：测量延迟，评估是否可接受

## 时间计划

| 阶段 | 任务 | 预计工作量 |
|-----|------|-----------|
| 1 | 环境准备 + 基础验证 | 0.5 天 |
| 2 | 工具调用 + MCP 验证 | 1 天 |
| 3 | Sub-agent + FastAPI 集成 | 1 天 |
| 4 | 自定义网关验证 + 问题修复 | 0.5 天 |

## 下一步

POC 验证通过后：
1. 制定详细迁移计划
2. 优先迁移"研发效能分析官"
3. 新 AI 员工直接使用 Agent SDK 实现
