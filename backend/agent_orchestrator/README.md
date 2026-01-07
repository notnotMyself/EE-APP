# AI Agent Orchestrator - 基于Claude Code Agent SDK的重构方案

## 🎯 架构概述

这是使用 **Claude Code Agent SDK** 重构的AI数字员工平台后端。核心理念：

1. **工作目录隔离**：每个AI员工有独立的工作空间
2. **能力模块化**：通过Skills定义可复用的能力
3. **Multi-Agent支持**：Agent可以调用其他Agent
4. **真正的工具能力**：AI员工可以执行Bash、读写文件、获取Web数据

## 📁 目录结构

```
backend/
├── agent_orchestrator/          # Agent协调层（FastAPI服务）
│   ├── main.py                 # FastAPI入口
│   ├── agent_manager.py        # Agent生命周期管理
│   └── requirements.txt
│
└── agents/                      # AI员工工作目录
    ├── dev_efficiency_analyst/     # 研发效能分析官
    │   ├── CLAUDE.md              # Agent定义和指令
    │   ├── .claude/
    │   │   ├── settings.json      # Agent配置
    │   │   └── skills/
    │   │       ├── gerrit_analysis.py
    │   │       └── report_generation.py
    │   ├── data/                  # 数据缓存
    │   ├── reports/               # 生成的报告
    │   └── scripts/               # 分析脚本
    │
    ├── nps_insight_analyst/       # NPS洞察官
    ├── product_requirement_analyst/
    ├── competitor_tracking_analyst/
    └── knowledge_management_assistant/
```

## 🔧 环境配置

### 1. 设置环境变量

```bash
# 使用你的Claude Code Auth Token
export ANTHROPIC_AUTH_TOKEN="sk-QTakUxAFn8sR4t29yGlkWmJr5ne9JfsQKHtKKnmy8LEskgbX"
export ANTHROPIC_BASE_URL="https://llm-gateway.oppoer.me"

# 模型配置
export ANTHROPIC_MODEL="saas/claude-sonnet-4.5"
```

### 2. 安装依赖

```bash
cd backend/agent_orchestrator
pip install -r requirements.txt
```

### 3. 安装Claude Code CLI（如果还没安装）

```bash
npm install -g @anthropic-ai/claude-code
```

## 🚀 启动服务

```bash
cd backend/agent_orchestrator
python main.py
```

服务将在 `http://localhost:8000` 启动。

访问 `http://localhost:8000/docs` 查看API文档。

## 📡 API接口

### 1. 列出所有AI员工

```bash
GET /api/v1/agents
```

### 2. WebSocket流式对话（推荐）

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/chat/dev_efficiency_analyst');

ws.onopen = () => {
    ws.send(JSON.stringify({
        message: "分析一下昨天的代码审查数据",
        conversation_history: []
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'chunk') {
        console.log(data.content);  // 流式输出
    } else if (data.type === 'done') {
        console.log('对话完成');
    }
};
```

### 3. HTTP SSE流式对话（兼容旧版本）

```bash
POST /api/v1/chat/stream
Content-Type: application/json

{
    "agent_role": "dev_efficiency_analyst",
    "message": "介绍一下你的功能",
    "conversation_history": []
}
```

## 🤖 AI员工能力

### 研发效能分析官 (dev_efficiency_analyst)

**可用工具**:
- `web_fetch`: 从Gerrit API获取数据
- `bash`: 执行Python分析脚本
- `read_file`: 读取历史数据
- `write_file`: 保存分析结果

**Skills**:
- `gerrit_analysis`: 分析代码审查指标
- `report_generation`: 生成Markdown报告

**示例对话**:
```
用户: "分析一下最近7天的代码审查效率"
AI: [自动调用web_fetch获取Gerrit数据]
    [调用gerrit_analysis.py分析指标]
    [生成报告并保存到reports/目录]
    "已完成分析，发现Review中位耗时36小时，超过阈值..."
```

## 🔄 工作目录隔离原理

每个AI员工运行时：

1. **只能访问自己的工作目录**
   ```bash
   claude-code agent run --workdir /path/to/dev_efficiency_analyst
   ```

2. **读取自己的CLAUDE.md获取指令**
   - Agent的行为完全由CLAUDE.md定义
   - 不同员工有不同的职责和能力描述

3. **只能使用自己的Skills**
   - Skills位于 `.claude/skills/` 目录
   - 每个员工可以有不同的Skills

4. **数据隔离**
   - 每个员工有独立的 `data/` 和 `reports/` 目录
   - 互不干扰

## 🔗 与Flutter前端集成

Flutter前端可以继续使用现有的API接口，只需要修改：

### 旧版本（调用原始Claude API）
```dart
POST http://localhost:8000/api/v1/chat/stream
{
  "agent": {...},
  "messages": [...]
}
```

### 新版本（调用Agent SDK）
```dart
WebSocket ws://localhost:8000/api/v1/chat/dev_efficiency_analyst
{
  "message": "用户消息",
  "conversation_history": [...]
}
```

## 🎯 下一步计划

### Phase 1: 验证POC ✅
- [x] 创建研发效能分析官的工作目录
- [x] 编写CLAUDE.md定义
- [x] 实现2个基础Skills
- [x] 创建Agent管理器
- [x] 创建FastAPI接口层
- [ ] 测试端到端流程

### Phase 2: 完善其他AI员工
- [ ] 创建NPS洞察官的工作目录和Skills
- [ ] 创建其他3个AI员工
- [ ] 为每个员工编写专属Skills

### Phase 3: Multi-Agent协作
- [ ] 实现Coordinator Agent
- [ ] 实现Agent间通信协议
- [ ] 测试多员工协作场景

### Phase 4: 定时任务
- [ ] 实现ScheduledAgent
- [ ] 配置定时分析任务
- [ ] 集成Push通知

## 🐛 已知问题

1. **Claude Code CLI调用方式**
   - 当前使用 `subprocess` 调用 `claude-code agent run`
   - 需要验证这种方式是否支持流式输出
   - 如果不支持，可能需要使用Python Agent SDK

2. **环境变量传递**
   - 需要确保 `ANTHROPIC_AUTH_TOKEN` 正确传递给子进程

3. **错误处理**
   - 需要完善Agent执行失败时的错误处理逻辑

## 📚 参考文档

- [Claude Code Agent SDK](https://github.com/anthropics/claude-code)
- [Claude API Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 贡献指南

添加新的AI员工：

1. 在 `backend/agents/` 下创建新目录
2. 编写 `CLAUDE.md` 定义Agent行为
3. 创建 `.claude/settings.json` 配置
4. 添加Skills到 `.claude/skills/`
5. 在 `agent_manager.py` 中注册新员工

## 📄 License

MIT
