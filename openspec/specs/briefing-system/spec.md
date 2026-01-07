# briefing-system Specification

## Purpose
Define the briefing feed, scheduled briefing generation, and briefing interactions, including seamless transition into a persistent conversation with the relevant AI agent.
## Requirements
### Requirement: REQ-BRIEF-001 Briefing Data Model
The system MUST support a briefing data structure containing:
- 类型（alert/insight/summary/action）
- 优先级（P0/P1/P2）
- 标题（≤30字）
- 摘要（≤100字）
- 影响说明
- 操作按钮列表
- 上下文数据（用于对话）
- 状态（new/read/actioned/dismissed）

#### Scenario: 创建警报类型简报
**Given** AI 员工发现 Review 积压严重
**When** 生成简报时
**Then** 简报类型为 `alert`，优先级为 `P0`，包含标题、摘要和影响说明

#### Scenario: 简报包含操作按钮
**Given** 一条新简报
**When** 展示给用户时
**Then** 应显示至少一个操作按钮（如"深入分析"、"忽略"）

---

### Requirement: REQ-BRIEF-002 Scheduled Job Execution
The system MUST support scheduled task execution with:
- Cron 表达式定义执行时间
- 任务提示词配置
- 上次/下次执行时间记录
- 任务启用/禁用状态

#### Scenario: 每日早9点执行分析
**Given** 定时任务配置 cron 表达式为 `0 9 * * *`
**When** 到达早9点
**Then** 自动触发 AI 员工执行分析任务

#### Scenario: 手动触发任务
**Given** 一个已配置的定时任务
**When** 管理员手动触发
**Then** 立即执行分析任务，不影响原定时计划

---

### Requirement: REQ-BRIEF-003 AI Decision for Push Worthiness
The AI agent MUST perform a second judgment after analysis to decide whether to push a briefing:
- 使用专门的决策 prompt
- 计算重要性评分（0.0-1.0）
- 仅当 `importance_score > 0.6` 时才推送
- 返回不推送时需说明原因

#### Scenario: 发现重要异常应推送
**Given** AI 分析发现 Review 中位耗时达 72 小时（超标 3 倍）
**When** 进行推送判断
**Then** 返回 `should_push: true`，`importance_score: 0.9`

#### Scenario: 数据正常不应推送
**Given** AI 分析发现所有指标在正常范围内（±10%）
**When** 进行推送判断
**Then** 返回 `should_push: false`，原因为"数据正常，无异常"

---

### Requirement: REQ-BRIEF-004 Daily Briefing Quota
The system MUST enforce a daily briefing quota per agent:
- 每个 Agent 每天最多推送 3 条简报
- 超出配额时跳过推送，记录日志
- 配额按 UTC 日期重置

#### Scenario: 超出每日配额
**Given** Agent 当天已推送 3 条简报
**When** 尝试推送第 4 条
**Then** 推送被跳过，记录日志"已达每日简报配额上限"

---

### Requirement: REQ-BRIEF-005 Briefing Feed Display
The Flutter client MUST provide a feed page to display briefings:
- 按创建时间倒序排列
- 显示未读数量 Badge
- 支持下拉刷新
- 简报卡片包含：Agent头像、类型标签、时间、标题、摘要、影响说明、操作按钮

#### Scenario: 显示未读简报
**Given** 用户有 5 条未读简报
**When** 打开信息流页面
**Then** AppBar 显示未读数量 Badge (5)，未读简报卡片有视觉区分（边框加粗、阴影）

#### Scenario: 空状态展示
**Given** 用户没有任何简报
**When** 打开信息流页面
**Then** 显示空状态提示"暂无简报，AI员工会在发现重要信息时主动通知你"

---

### Requirement: REQ-BRIEF-006 Briefing Interactions
The system MUST support the following user interactions with briefings:
- 点击卡片：标记已读，显示详情或跳转对话
- 点击"开始对话"：创建或复用关联对话，将简报作为卡片插入对话流，携带简报上下文，并返回 `conversation_id`
- 点击"忽略"：标记为 dismissed，从信息流移除

#### Scenario: 从简报开始对话
**Given** 一条关于 Review 积压的简报
**When** 用户点击"深入分析"按钮
**Then** 系统查找或创建与该 Agent 的对话，将简报作为卡片插入对话流，返回 `conversation_id`，用户进入对话页面看到简报卡片

#### Scenario: 忽略简报
**Given** 一条用户不关心的简报
**When** 用户点击"忽略"
**Then** 简报状态变为 `dismissed`，从信息流消失

#### Scenario: 同一 Agent 的多个简报共享对话
**Given** 用户已收到 Agent A 的简报 B1，并已开始对话
**When** 用户收到 Agent A 的新简报 B2，点击"开始对话"
**Then** 系统复用现有对话，将简报 B2 作为新卡片插入同一对话流

#### Scenario: 不同 Agent 的简报独立对话
**Given** 用户收到 Agent A 的简报和 Agent B 的简报
**When** 用户分别点击两个简报的"开始对话"
**Then** 系统创建两个独立的对话（一个与 Agent A，一个与 Agent B）

---

### Requirement: REQ-BRIEF-007 Briefing Card Color Coding
Briefing cards MUST display different colors based on type and priority:
- **优先级颜色**：P0=红色, P1=橙色, P2=蓝色
- **类型颜色**：alert=红色, insight=紫色, summary=蓝色, action=绿色

#### Scenario: P0 警报显示红色
**Given** 一条 P0 优先级的 alert 类型简报
**When** 在信息流展示
**Then** 卡片边框为红色，未读指示器为红色圆点

---

### Requirement: REQ-BRIEF-008 API Endpoints
The backend MUST provide the following API endpoints:
- `GET /api/v1/briefings` - 获取简报列表
- `GET /api/v1/briefings/unread-count` - 获取未读数量
- `PATCH /api/v1/briefings/{id}/read` - 标记已读
- `POST /api/v1/briefings/{id}/start-conversation` - 从简报开始对话
- `DELETE /api/v1/briefings/{id}` - 忽略/删除简报

#### Scenario: 获取简报列表
**Given** 用户已登录
**When** 请求 `GET /api/v1/briefings?limit=20`
**Then** 返回最多 20 条简报，按创建时间倒序，包含 Agent 信息

---

### Requirement: REQ-BRIEF-009 Briefing Card in Conversation
When a briefing is added to a conversation, it MUST be stored as a special message with:
- `content_type = 'briefing_card'`
- `role = 'system'`
- `content` containing structured briefing data (title, summary, priority, created_at)
- `briefing_id` linking to the original briefing record

The briefing card MUST be visually distinct from text messages in the UI.

#### Scenario: 简报卡片数据结构
**Given** 一个简报 {id: "uuid", title: "代码返工率50%", summary: "最近7天...", priority: "P1"}
**When** 简报被添加到对话中
**Then** 创建消息记录，且 `content_type='briefing_card'` 并绑定 `briefing_id`

#### Scenario: 简报卡片在对话流中的顺序
**Given** 一个对话包含：简报 A（9:00），用户消息（9:05），简报 B（10:00）
**When** 用户查看对话历史
**Then** 消息按时间顺序展示：简报 A → 用户消息 → 简报 B

---

### Requirement: REQ-BRIEF-010 Cross-Briefing Context in AI Responses
When responding to user questions in a conversation, the AI MUST:
- Include recent conversation history (including briefing cards) in its context
- Be able to reference and correlate multiple briefings
- Provide analysis that spans across briefings when relevant

#### Scenario: AI 引用单个简报
**Given** 对话中有简报"返工率50%"
**When** 用户问"为什么返工率这么高？"
**Then** AI 响应引用该简报的数据和上下文

#### Scenario: AI 关联多个简报
**Given** 对话中有简报"返工率50%"和"Review耗时超标"
**When** 用户问"这两个问题有关联吗？"
**Then** AI 分析两个简报的相关性，例如"审查时间过长可能导致更多返工"

#### Scenario: AI 提及简报时使用自然语言
**Given** 对话中有简报"代码返工率50%（2026-01-07 09:00）"
**When** AI 响应用户问题
**Then** AI 说"根据今天早上的简报，返工率达到了50%..."

