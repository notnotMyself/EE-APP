# AI 员工执行问题诊断和解决方案

## 🔴 核心问题

**您的问题很准确**：AI 员工根本**不知道**9点要执行什么具体任务！

---

## 问题分析

### 当前实现（错误）

#### 代码路径
`ai_agent_platform/backend/app/services/briefing_service.py` 第239-261行

```python
async def _execute_agent_analysis(self, ...):
    system_prompt = claude_service.build_agent_system_prompt(
        agent_name=agent_name,
        agent_role=agent_role,
        agent_description=agent_description
    )

    messages = [{"role": "user", "content": task_prompt}]

    result = await claude_service.chat_completion(  # ❌ 问题所在！
        messages=messages,
        system_prompt=system_prompt,
        max_tokens=4096
    )

    return result
```

#### claude_service.chat_completion() 做了什么？

```python
# ai_agent_platform/backend/app/services/claude_service.py 第30-60行

async def chat_completion(self, messages, system_prompt=None, ...):
    kwargs = {
        "model": self.model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    if system_prompt:
        kwargs["system"] = system_prompt

    # ❌ 只是简单的 Claude API 调用！
    response = await self.client.messages.create(**kwargs)

    return response.content[0].text
```

**这是什么？**
- 这只是 `anthropic` Python SDK 的基础 API 调用
- **没有工具调用能力**（没有 `tools` 参数）
- **没有 workspace 概念**（不知道 Agent 工作目录在哪）
- **没有 skills 访问**（AI 不知道有可执行的脚本）

---

### AI 员工的实际体验

**9点定时任务触发时，AI 收到的信息**：

```
System Prompt:
You are 研发效能分析官, an AI agent with the role of dev_efficiency_analyst.
[agent_description]

User Message:
请执行每日研发效能分析：
1. 从Gerrit数据库获取昨日代码审查数据
2. 分析关键指标：Review耗时、返工率、代码变更量
3. 检测异常值（对比阈值）
4. 如果发现异常，准备推送简报
```

**AI 的处境**：
- 💭 "我收到了任务：分析研发效能"
- ❓ "但是...数据在哪里？"
- ❓ "Gerrit 数据库怎么连？连接信息呢？"
- ❓ "我有什么工具可以用？"
- ❌ "我只能根据我的训练数据，**编造**一个听起来合理的分析报告"

**结果**：AI 会返回一个**虚构的**分析报告，类似：

```markdown
# 研发效能每日分析

根据昨日数据分析：
- Review中位耗时：18小时 ✅ (正常)
- Review P95耗时：45小时 ✅ (正常)
- 返工率：12% ✅ (正常)

未发现异常，各项指标正常。
```

但这些数字**完全是编造的**！因为 AI 根本没有访问真实数据。

---

## ✅ 正确的实现方式

### 使用 Claude Agent SDK

根据项目文档 `CLAUDE.md` 和 `openspec/project.md` 的目标架构：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def execute_agent_analysis(agent_workspace: str, task_prompt: str):
    """正确的方式：使用 Agent SDK"""

    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Grep", "Glob"],
        cwd=agent_workspace,  # ← 关键：指定工作目录！
        model="saas/claude-sonnet-4.5"
    )

    result = []
    async for message in query(prompt=task_prompt, options=options):
        result.append(str(message))

    return '\n'.join(result)
```

**关键区别**：

| 方面 | 当前实现（错误） | 正确实现（Agent SDK） |
|------|----------------|-------------------|
| API 类型 | Anthropic Messages API | Claude Code CLI (bundled) |
| 工作目录 | ❌ 无 | ✅ 指定 cwd |
| 工具访问 | ❌ 无 | ✅ Bash, Read, Write 等 |
| Skills 可见 | ❌ 不知道 | ✅ 可以执行 `.claude/skills/*.py` |
| 数据访问 | ❌ 只能编造 | ✅ 可以真实查询 |
| Agent 定义 | ❌ 简单描述 | ✅ 完整的 CLAUDE.md + workspace |

---

## 🔧 Agent SDK 执行流程

**9点定时触发时，使用 Agent SDK 的流程**：

```
1. 定时任务触发 (cron: 0 9 * * *)
   ↓
2. BriefingService 调用 Agent SDK
   options = ClaudeAgentOptions(
       cwd="/backend/agents/dev_efficiency_analyst",
       allowed_tools=["Bash", "Read", "Write"]
   )
   ↓
3. Agent SDK 启动 Claude Code CLI (subprocess)
   - 工作目录：/backend/agents/dev_efficiency_analyst
   - 读取 CLAUDE.md 作为 Agent 定义
   - 加载 .claude/settings.json 配置
   ↓
4. AI 收到任务："请执行每日研发效能分析"
   ↓
5. AI 思考："我需要先获取数据"
   → 使用 Bash 工具：
     cd .claude/skills
     echo '{"days": 1}' | python gerrit_analysis.py
   ↓
6. gerrit_analysis.py 执行
   - 连接 Gerrit MySQL (10.52.61.119:33067)
   - 查询昨日数据
   - 返回 JSON 格式的统计数据
   ↓
7. AI 收到真实数据，进行分析
   - 计算指标
   - 对比阈值
   - 检测异常
   ↓
8. AI 生成结构化报告（Markdown）
   ↓
9. BriefingService 收到报告
   ↓
10. AI 二次判断：是否值得推送简报？
   ↓
11. 如果值得，创建简报记录到数据库
```

**关键点**：
- ✅ AI 可以**真正执行** gerrit_analysis skill
- ✅ AI 可以获取**真实数据**
- ✅ AI 可以在 workspace 中**读写文件**
- ✅ AI 知道自己的**完整角色定义**（CLAUDE.md）

---

## 📝 AI 使用 Skills 的示例对话

**使用 Agent SDK 时，AI 的内心活动**：

```
💭 我收到任务："执行每日研发效能分析"

💭 根据我的 CLAUDE.md 定义，我需要：
   1. 从 Gerrit 获取数据
   2. 分析指标
   3. 检测异常

💭 我看到我的 workspace 结构：
   ├── .claude/skills/
   │   ├── gerrit_analysis.py    ← 这个可以获取数据！
   │   └── report_generation.py
   └── data/
       └── mock_gerrit_data.json

💭 好，我先执行 gerrit_analysis skill 获取数据

🔧 [使用 Bash 工具]
   $ cd .claude/skills
   $ echo '{"days": 1}' | python gerrit_analysis.py

📥 [收到输出]
   {
     "summary": {
       "total_changes": 15,
       "review_median_hours": 38.5,
       "review_p95_hours": 78.2,
       "rework_rate": 18.3
     },
     "anomalies": [
       {
         "type": "REVIEW_TIME_HIGH",
         "severity": "WARNING",
         "value": 38.5,
         "threshold": 24
       },
       {
         "type": "REWORK_RATE_HIGH",
         "severity": "WARNING",
         "value": 18.3,
         "threshold": 15
       }
     ]
   }

💭 数据分析完成！发现了2个异常：
   - Review中位耗时 38.5小时（超标）
   - 返工率 18.3%（超标）

💭 这需要推送简报给用户！

📝 [生成报告]
   # 研发效能每日分析

   **日期**: 2026-01-06

   ## 核心指标摘要
   | 指标 | 数值 | 阈值 | 状态 |
   |------|------|------|------|
   | Review中位耗时 | 38.5h | 24h | ⚠️ 超标 |
   | Review P95耗时 | 78.2h | 72h | ⚠️ 超标 |
   | 返工率 | 18.3% | 15% | ⚠️ 超标 |

   ## 异常发现

   🔴 **Review积压严重**
   - 现象：中位耗时达38.5小时，超过阈值24小时
   - 影响：可能延误本周版本发布
   - 建议：增加Reviewer人手，优先处理高优先级PR

   ⚠️ **返工率偏高**
   - 现象：返工率达18.3%，超过阈值15%
   - 影响：开发效率降低，浪费时间
   - 建议：加强需求评审，提高代码质量标准

✅ 分析完成，返回报告
```

**这才是真正的 AI 员工执行流程！**

---

## 🚀 实施步骤

### Step 1: 安装 Claude Agent SDK

```bash
cd ai_agent_platform/backend
pip install claude-agent-sdk
```

### Step 2: 替换 briefing_service 的实现

将 `_execute_agent_analysis` 方法改为使用 Agent SDK：

```python
# ai_agent_platform/backend/app/services/briefing_service.py

from claude_agent_sdk import query, ClaudeAgentOptions
from pathlib import Path

async def _execute_agent_analysis(
    self,
    agent_name: str,
    agent_role: str,
    agent_description: str,
    task_prompt: str
) -> str:
    """使用 Claude Agent SDK 执行分析任务"""

    # 获取 Agent workspace 路径
    workspace = Path(__file__).parent.parent.parent.parent.parent / \
                "backend" / "agents" / agent_role

    # 读取 CLAUDE.md
    claude_md = workspace / "CLAUDE.md"
    agent_context = ""
    if claude_md.exists():
        agent_context = claude_md.read_text(encoding='utf-8')

    # 构建完整 prompt
    full_prompt = f"""
# 角色定义

{agent_context}

---

# 当前任务

{task_prompt}

---

# 可用资源

工作目录：{workspace}

你可以使用 Bash 工具执行 .claude/skills/ 中的脚本。
例如：
```bash
cd .claude/skills && echo '{{"days": 1}}' | python gerrit_analysis.py
```
"""

    # 配置 Agent SDK
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Grep", "Glob"],
        cwd=str(workspace),
        model="saas/claude-sonnet-4.5"
    )

    # 执行任务
    result_chunks = []
    async for message in query(prompt=full_prompt, options=options):
        result_chunks.append(str(message))

    return '\n'.join(result_chunks)
```

### Step 3: 测试

```bash
# 使用提供的测试脚本
python backend/execute_agent_with_sdk.py

# 或者运行完整的简报生成流程
python backend/test_briefing_quick.py
```

---

## 📊 对比总结

| 维度 | 当前实现 | Agent SDK 实现 |
|------|---------|---------------|
| **AI 知道 Skills 存在吗？** | ❌ 不知道 | ✅ 知道 |
| **AI 能执行 Skills 吗？** | ❌ 不能 | ✅ 能 |
| **AI 能访问真实数据吗？** | ❌ 不能 | ✅ 能 |
| **AI 能在 workspace 操作吗？** | ❌ 不能 | ✅ 能 |
| **分析结果是真实的吗？** | ❌ 虚构 | ✅ 真实 |
| **符合项目架构目标吗？** | ❌ 不符合 | ✅ 符合 |

---

## 💡 为什么会有这个问题？

查看 `openspec/project.md` 第279-291行，项目计划是**迁移到 Agent SDK**：

```markdown
### Phase 2: Agent SDK 迁移 🔄 (当前)
- [ ] POC 验证 - 验证 Claude Agent SDK 可行性
- [ ] 研发效能分析官迁移
- [ ] 新功能用 Agent SDK 实现
```

**目前的状态**：
- ✅ 简报系统已实现（但用的是旧 API）
- ⚠️ Agent SDK POC 还未完成
- ❌ 旧的 claude_service 还在使用 Anthropic Messages API

**所以**：
- 定时任务能触发 ✅
- 简报生成流程能运行 ✅
- **但 AI 无法真正执行分析任务** ❌

---

## 🎯 总结

**您的直觉完全正确**：AI 员工现在**不清楚**9点要执行什么具体任务。

**原因**：
1. 使用了错误的 API（Anthropic Messages API，没有工具调用）
2. 没有传递 workspace 信息（AI 不知道 skills 在哪）
3. 没有启用工具（AI 无法执行脚本）

**解决方案**：
1. 完成 Agent SDK 迁移（按照项目规划）
2. 替换 briefing_service 的实现
3. 让 AI 真正能够访问 workspace 和执行 skills

**测试方式**：
```bash
# 测试 Agent SDK 执行（提供了脚本）
python backend/execute_agent_with_sdk.py
```

需要我帮您实施这个迁移吗？
