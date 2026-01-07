# briefing-system Specification Delta

## MODIFIED Requirements

### Requirement: REQ-BRIEF-006 Briefing Interactions
The system MUST support the following user interactions with briefings:
- 点击卡片：标记已读，显示详情或跳转对话
- 点击"开始对话"：创建或复用关联对话，将简报作为卡片插入对话流，携带简报上下文
- 点击"忽略"：标记为 dismissed，从信息流移除

**Modified Behavior**: The "开始对话" action MUST now:
- Use get-or-create pattern to find or create a conversation for the user-agent pair
- Insert the briefing as a `briefing_card` message in the conversation
- Return the `conversation_id` (not NULL)
- Preserve briefing context for AI to reference in responses

#### Scenario: 从简报开始对话（新行为）
**Given** 一条关于 Review 积压的简报
**When** 用户点击"深入分析"按钮
**Then** 系统查找或创建与该 Agent 的对话，将简报作为卡片插入对话流，返回 `conversation_id`，用户进入对话页面看到简报卡片

#### Scenario: 同一 Agent 的多个简报共享对话（新场景）
**Given** 用户已收到 Agent A 的简报 B1，并已开始对话
**When** 用户收到 Agent A 的新简报 B2，点击"开始对话"
**Then** 系统复用现有对话，将简报 B2 作为新卡片插入同一对话流

#### Scenario: 不同 Agent 的简报独立对话（新场景）
**Given** 用户收到 Agent A 的简报和 Agent B 的简报
**When** 用户分别点击两个简报的"开始对话"
**Then** 系统创建两个独立的对话（一个与 Agent A，一个与 Agent B）

#### Scenario: 忽略简报（保持原有行为）
**Given** 一条用户不关心的简报
**When** 用户点击"忽略"
**Then** 简报状态变为 `dismissed`，从信息流消失

---

## ADDED Requirements

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
**Then** 创建消息记录：
```json
{
  "conversation_id": "conv-uuid",
  "role": "system",
  "content_type": "briefing_card",
  "briefing_id": "uuid",
  "content": {
    "title": "代码返工率50%",
    "summary": "最近7天...",
    "priority": "P1",
    "created_at": "2026-01-07T09:00:00Z"
  }
}
```

#### Scenario: 简报卡片在对话流中的顺序
**Given** 一个对话包含：简报 A（9:00），用户消息（9:05），简报 B（10:00）
**When** 用户查看对话历史
**Then** 消息按时间顺序展示：简报 A → 用户消息 → 简报 B

---

### Requirement: REQ-BRIEF-010 Cross-Briefing Context in AI Responses
When responding to user questions in a conversation, the AI MUST:
- Include all briefing cards from the conversation in its context
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
