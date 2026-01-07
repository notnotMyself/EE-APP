# Auto-Develop by AI - 技术方案与实践策略

> **核心理念：踩着 Claude Code 过河，让 AI 成为开发流程的核心参与者**

---

## 一、什么是 Auto-Develop by AI

### 定义

> **Auto-Develop by AI** = 利用 AI 编程助手（Claude Code / Cursor）实现「规范驱动 + AI 执行」的开发模式

不是让 AI 完全取代人，而是：

- **人负责**：定义需求、审核结果、把控方向
- **AI 负责**：理解规范、生成代码、执行任务、迭代修复

### 核心价值

| 传统开发 | Auto-Develop |
|----------|--------------|
| 人写代码，人 Review | AI 写代码，人 Review |
| 需求文档 → 人理解 → 人编码 | 需求规范 → AI 理解 → AI 编码 |
| 每次迭代都是从头开始 | 规范积累，AI 学习成本递减 |
| 团队知识在人脑中 | 团队知识在规范文档中 |

---

## 二、我们的技术栈

### AI 编程工具

```
┌─────────────────────────────────────────────────────────┐
│                   开发者工作站                           │
├─────────────────────────────────────────────────────────┤
│  Cursor IDE                                             │
│  └→ 内置 Claude 模型                                    │
│  └→ @file / @folder / @codebase 上下文引用              │
│  └→ Agent Mode（自动执行多步任务）                       │
├─────────────────────────────────────────────────────────┤
│  Claude Code CLI (可选，后端 Agent 调用)                 │
│  └→ claude-agent-sdk（Python SDK）                      │
│  └→ 内置工具：Read, Write, Edit, Bash, Grep, Glob       │
│  └→ 自定义工具：MCP Server                              │
└─────────────────────────────────────────────────────────┘
```

### 规范驱动框架

```
OpenSpec（已集成）
├── openspec/project.md      # 项目约定（Tech Stack, Conventions）
├── openspec/specs/          # 已实现的功能规范
├── openspec/changes/        # 待实现的变更提案
└── openspec/AGENTS.md       # AI 助手使用指南
```

---

## 三、Auto-Develop 工作流

### 流程概览

```
┌──────────────────────────────────────────────────────────────┐
│                    Auto-Develop 工作流                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   1. 需求输入                                                 │
│   └→ 用户用自然语言描述需求                                   │
│                                                              │
│   2. AI 规范化                                                │
│   └→ AI 生成 proposal.md + tasks.md + spec delta             │
│   └→ 人审核 & 调整                                           │
│                                                              │
│   3. AI 实现                                                  │
│   └→ AI 按 tasks.md 逐步实现                                  │
│   └→ 自动运行测试 / lint                                     │
│   └→ 遇到问题自动修复                                        │
│                                                              │
│   4. 人审核                                                   │
│   └→ Review 生成的代码                                        │
│   └→ 验收功能                                                 │
│                                                              │
│   5. 归档 & 积累                                              │
│   └→ openspec archive                                        │
│   └→ 规范沉淀，下次 AI 更懂                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 详细步骤

#### Step 1: 需求输入

```markdown
# 用户输入示例
"我想给研发效能分析官增加一个能力：检测某个模块的 Review 耗时连续 3 周上涨时，
自动生成一份趋势分析报告，包含可能的原因假设。"
```

#### Step 2: AI 规范化

AI 自动生成 OpenSpec 变更提案：

```bash
# AI 创建的目录结构
openspec/changes/add-review-trend-alert/
├── proposal.md          # 变更说明
├── tasks.md             # 实现任务清单
└── specs/
    └── dev-efficiency-analyst/
        └── spec.md      # 功能规范 delta
```

**proposal.md**
```markdown
# Change: 添加 Review 耗时趋势异常检测

## Why
当前研发效能分析官只能检测单次异常，无法识别连续恶化趋势。
TL 需要更早发现问题，避免积重难返。

## What Changes
- 新增趋势检测逻辑（连续 N 周环比上涨）
- 新增趋势分析报告生成
- 新增自动触发条件

## Impact
- Affected specs: dev-efficiency-analyst
- Affected code: backend/agents/dev_efficiency_analyst/
```

**tasks.md**
```markdown
## 1. 趋势检测实现
- [ ] 1.1 添加 detect_review_trend 方法
- [ ] 1.2 实现连续 N 周检测逻辑
- [ ] 1.3 添加阈值配置

## 2. 报告生成
- [ ] 2.1 设计趋势报告模板
- [ ] 2.2 实现原因假设生成逻辑

## 3. 集成测试
- [ ] 3.1 添加单元测试
- [ ] 3.2 验证端到端流程
```

#### Step 3: AI 实现

在 Cursor 中：

```
@tasks.md 请按照任务清单实现功能，从 1.1 开始
```

AI 会：
1. 阅读相关代码（`@backend/agents/dev_efficiency_analyst/`）
2. 按任务逐步实现
3. 自动运行测试
4. 遇到 lint 错误自动修复
5. 更新 tasks.md 标记完成

#### Step 4: 人审核

- Review AI 生成的代码
- 运行完整测试
- 验收功能

#### Step 5: 归档

```bash
openspec archive add-review-trend-alert --yes
```

规范沉淀到 `openspec/specs/`，下次 AI 可以参考。

---

## 四、关键实践原则

### 原则 1：规范先于代码

> **没有规范的功能，不要让 AI 直接写代码**

```
❌ 错误做法：
   "帮我实现一个 XXX 功能"
   
✅ 正确做法：
   "帮我创建一个变更提案，实现 XXX 功能"
   然后审核 proposal.md 后，再让 AI 实现
```

### 原则 2：上下文越丰富，结果越好

> **让 AI 看到足够的上下文**

```
# 好的 Prompt
@openspec/project.md @backend/agents/dev_efficiency_analyst/CLAUDE.md
请参考现有的研发效能分析官实现，添加趋势检测功能

# 差的 Prompt
添加趋势检测功能
```

### 原则 3：小步快跑，频繁验证

> **每个任务完成后都要验证，不要一次让 AI 做太多**

```markdown
## 推荐的任务粒度

- [ ] 1.1 添加 detect_review_trend 方法（~50行代码）
- [ ] 1.2 添加单元测试（~30行代码）
- [ ] 1.3 集成到主流程（~20行代码）

## 不推荐的任务粒度

- [ ] 1.1 实现完整的趋势检测功能（~500行代码）
```

### 原则 4：积累团队知识在规范中

> **规范 = 团队知识的外化**

每次完成功能后：
1. 确保 `openspec/specs/` 有最新的功能规范
2. 更新 `openspec/project.md` 的约定
3. AI 下次就能「学会」这些知识

---

## 五、与 Claude Agent SDK 的结合

### 产品 AI（运行时）vs 开发 AI（开发时）

```
┌────────────────────────────────────────────────────────────┐
│                    两种 AI 角色                             │
├─────────────────────────────┬──────────────────────────────┤
│   产品 AI（运行时）          │   开发 AI（开发时）           │
├─────────────────────────────┼──────────────────────────────┤
│ Claude Agent SDK            │ Cursor / Claude Code         │
│ 运行在后端服务器             │ 运行在开发者工作站            │
│ 执行用户任务（分析数据）     │ 执行开发任务（写代码）        │
│ 面向产品用户                │ 面向开发者                   │
│ 需要自定义工具（MCP）       │ 使用内置工具                  │
└─────────────────────────────┴──────────────────────────────┘
```

### 开发 AI 开发产品 AI

```
开发者
   │
   │ 需求：给研发效能分析官增加趋势检测
   ▼
┌─────────────────────────────────────────────┐
│  Cursor (开发 AI)                           │
│  └→ 生成 proposal.md                        │
│  └→ 实现 Python 代码                        │
│  └→ 配置 MCP 工具                           │
│  └→ 更新 CLAUDE.md (产品 AI 的行为定义)     │
└─────────────────────────────────────────────┘
   │
   │ 产出
   ▼
┌─────────────────────────────────────────────┐
│  Claude Agent SDK (产品 AI)                 │
│  └→ 读取 CLAUDE.md 作为 system prompt       │
│  └→ 使用开发 AI 创建的 MCP 工具             │
│  └→ 执行用户的分析任务                      │
└─────────────────────────────────────────────┘
   │
   │ 服务
   ▼
产品用户
```

---

## 六、实战示例：添加新 AI 员工

### 需求

> 添加一个「NPS 洞察官」AI 员工

### Step 1: 创建变更提案

在 Cursor 中：

```
@openspec/AGENTS.md @openspec/project.md 
@backend/agents/dev_efficiency_analyst/

请帮我创建一个变更提案，添加 NPS 洞察官 AI 员工。
参考研发效能分析官的实现结构。
```

AI 会生成：
- `openspec/changes/add-nps-insight-analyst/proposal.md`
- `openspec/changes/add-nps-insight-analyst/tasks.md`
- `openspec/changes/add-nps-insight-analyst/specs/nps-insight-analyst/spec.md`

### Step 2: 审核 & 调整

人审核 proposal.md，确认：
- 职责边界是否清晰
- 触发条件是否合理
- 技术方案是否可行

### Step 3: 实现

```
@openspec/changes/add-nps-insight-analyst/tasks.md
请按任务清单实现，从 1.1 开始
```

AI 会：
1. 创建 `backend/agents/nps_insight_analyst/` 目录
2. 编写 `CLAUDE.md`（AI 员工的行为定义）
3. 创建 MCP 工具（如 `nps_query`）
4. 添加到 Agent Manager
5. 更新前端的 Agent 列表

### Step 4: 测试 & 归档

```bash
# 验证
python3 backend/agent_orchestrator/test_poc.py

# 归档
openspec archive add-nps-insight-analyst --yes
```

---

## 七、团队协作模式

### 开发者角色分工

| 角色 | 职责 | 与 AI 的协作 |
|------|------|-------------|
| 产品经理 | 定义需求、验收功能 | 审核 proposal.md |
| 开发者 | 设计方案、Review 代码 | 驱动 AI 实现、Review 结果 |
| AI 助手 | 生成规范、编写代码、修复问题 | 执行者 |

### 代码审核流程

```
1. AI 完成实现
2. 开发者 Review（重点检查）
   - 业务逻辑是否正确
   - 是否符合项目规范
   - 是否有安全问题
3. 运行测试 & lint
4. 合并代码
```

---

## 八、持续优化

### 规范迭代

每完成一个功能，问自己：
1. 这次 AI 哪里做得好？（保持）
2. 这次 AI 哪里做得不好？（补充规范）
3. 有没有可以抽象的模式？（更新 project.md）

### Prompt 库积累

建立团队的 Prompt 库：

```markdown
## 常用 Prompt

### 创建新 AI 员工
@openspec/AGENTS.md @openspec/project.md @backend/agents/dev_efficiency_analyst/
请帮我创建一个变更提案，添加 {员工名称} AI 员工。参考研发效能分析官的实现结构。

### 添加 MCP 工具
@backend/agent_sdk/mcp_tools/ @openspec/project.md
请帮我添加一个 MCP 工具 {工具名称}，功能是 {描述}。

### 修复 Bug
@{相关文件}
这个功能出现了 {问题描述}，请帮我定位并修复。
```

---

## 九、总结

### Auto-Develop by AI 的核心

1. **规范驱动**：用 OpenSpec 管理需求和规范
2. **AI 执行**：让 Cursor / Claude Code 按规范实现
3. **人审核**：开发者 Review 和验收
4. **持续积累**：规范沉淀，AI 越来越懂项目

### 期望效果

| 指标 | 传统开发 | Auto-Develop |
|------|----------|--------------|
| 简单功能开发时间 | 1-2 天 | 1-2 小时 |
| 代码风格一致性 | 依赖人的自觉 | AI 自动遵循规范 |
| 团队知识传承 | 在人脑中 | 在规范文档中 |
| 新人上手时间 | 数周 | 数天 |

### 下一步行动

1. [ ] 完善 `openspec/project.md` 的约定
2. [ ] 为已有 AI 员工补充完整的 spec
3. [ ] 建立团队 Prompt 库
4. [ ] 实践：用 Auto-Develop 流程添加 NPS 洞察官

