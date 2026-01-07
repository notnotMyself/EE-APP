# conversation-persistence Specification Delta

## ADDED Requirements

### Requirement: REQ-CONV-001 Conversation Persistence
The system MUST persist conversations between users and AI agents in the database with the following properties:
- Each conversation is uniquely identified by `(user_id, agent_id)` pair
- Conversations are created on-demand when a user interacts with an agent
- Conversations remain persistent across sessions
- Conversations track `started_at` and `last_message_at` timestamps

#### Scenario: First interaction creates conversation
- **GIVEN** user A has never interacted with agent B
- **WHEN** user A clicks "继续对话" on a briefing from agent B
- **THEN** a new conversation is created with `user_id=A`, `agent_id=B`

#### Scenario: Subsequent interactions reuse conversation
- **GIVEN** user A has an existing conversation with agent B
- **WHEN** user A clicks "继续对话" on another briefing from agent B
- **THEN** the existing conversation is reused (no new conversation created)

#### Scenario: Separate conversations per agent
- **GIVEN** user A has conversations with agents B and C
- **WHEN** user A interacts with agent B
- **THEN** only conversation B is accessed (conversation C remains separate)

---

### Requirement: REQ-CONV-002 Message Polymorphism
The system MUST support multiple message content types within a conversation:
- `text`: Regular user or assistant messages
- `briefing_card`: Briefing embedded as a card in the conversation

Each message MUST contain:
- `conversation_id`: Link to parent conversation
- `role`: One of 'user', 'assistant', 'system'
- `content_type`: Type of message content
- `content`: Message content (text or structured data)
- `created_at`: Timestamp of message creation

#### Scenario: Text message storage
- **GIVEN** a conversation exists
- **WHEN** user sends a text message "为什么会这样?"
- **THEN** a message is created with `content_type='text'`, `role='user'`, `content="为什么会这样?"`

#### Scenario: Briefing card storage
- **GIVEN** a briefing with title "代码返工率50%" and summary "最近7天..."
- **WHEN** the briefing is added to a conversation
- **THEN** a message is created with `content_type='briefing_card'`, `role='system'`, `content` containing structured briefing data

#### Scenario: Mixed message types in chronological order
- **GIVEN** a conversation with 2 briefing cards and 3 text messages
- **WHEN** messages are retrieved
- **THEN** all messages are returned in chronological order regardless of content type

---

### Requirement: REQ-CONV-003 Get-or-Create Pattern
The system MUST implement a get-or-create pattern for conversations to ensure:
- Only one conversation exists per `(user_id, agent_id)` pair
- No duplicate conversations are created due to race conditions
- Existing conversations are reused seamlessly

#### Scenario: Concurrent conversation creation attempts
- **GIVEN** user A interacts with agent B for the first time
- **WHEN** two briefings arrive simultaneously and both try to create a conversation
- **THEN** only one conversation is created, and both briefings link to it

#### Scenario: Query before insert
- **GIVEN** a request to get-or-create conversation for (user A, agent B)
- **WHEN** the get-or-create method is called
- **THEN** the system first queries for existing conversation, and only inserts if not found

---

### Requirement: REQ-CONV-004 Conversation Context Building
The system MUST construct AI conversation context by including:
- Recent conversation history (last N messages, where N is configurable)
- Briefing cards formatted as structured information
- User and assistant text messages formatted as dialogue

The context MUST:
- Limit message count to prevent token overflow (default: 20 messages)
- Preserve chronological order
- Distinguish briefing cards from text in the prompt

#### Scenario: Context includes briefing cards
- **GIVEN** a conversation with 2 briefing cards and 1 user message
- **WHEN** AI context is built for the next response
- **THEN** the context includes formatted briefing summaries followed by user message

#### Scenario: Context respects message limit
- **GIVEN** a conversation with 50 messages
- **WHEN** AI context is built with limit=20
- **THEN** only the most recent 20 messages are included in the context

#### Scenario: Briefing card formatting in context
- **GIVEN** a briefing card message with title "Review耗时超标" and summary "中位耗时30小时"
- **WHEN** the briefing card is included in AI context
- **THEN** it is formatted as:
  ```
  [简报 2026-01-07 10:00]
  标题：Review耗时超标
  摘要：中位耗时30小时...
  优先级：P1
  ```

---

### Requirement: REQ-CONV-005 Briefing-to-Conversation Integration
The system MUST enable seamless transition from briefings to conversations:
- Briefings can trigger conversation creation or reuse
- Briefing data is embedded as a message in the conversation
- Users can discuss multiple briefings in one conversation thread

#### Scenario: Briefing action creates conversation
- **GIVEN** a briefing with action "start_conversation"
- **WHEN** user executes the action
- **THEN** a conversation is created or reused, the briefing is added as a card, and `conversation_id` is returned

#### Scenario: Multiple briefings in one conversation
- **GIVEN** user A receives 3 briefings from agent B on the same day
- **WHEN** user clicks "继续对话" on each briefing
- **THEN** all 3 briefings appear as cards in the same conversation

#### Scenario: Cross-briefing questions
- **GIVEN** a conversation with 2 briefing cards: "返工率50%" and "Review耗时超标"
- **WHEN** user asks "这两个问题有关联吗？"
- **THEN** AI response references both briefings and analyzes their relationship

---

### Requirement: REQ-CONV-006 Conversation API Endpoints
The system MUST provide REST API endpoints for conversation management:
- `GET /conversations/{agent_id}`: Get or create conversation with an agent
- `GET /conversations/{conversation_id}/messages`: Retrieve conversation messages
- `POST /conversations/{conversation_id}/messages`: Send a message (streaming response)

All endpoints MUST:
- Require authentication
- Enforce Row Level Security (users can only access their own conversations)
- Return appropriate HTTP status codes (200, 404, 403, 500)

#### Scenario: Get conversation by agent ID
- **GIVEN** user A is authenticated
- **WHEN** user requests `GET /conversations/{agent_B_id}`
- **THEN** the system returns the conversation between user A and agent B (creating one if it doesn't exist)

#### Scenario: Unauthorized conversation access
- **GIVEN** user A requests conversation between user B and agent C
- **WHEN** the request is processed
- **THEN** the system returns 403 Forbidden

#### Scenario: Retrieve messages with briefing cards
- **GIVEN** a conversation with 2 briefing cards and 5 text messages
- **WHEN** user requests `GET /conversations/{id}/messages`
- **THEN** all 7 messages are returned in chronological order with `content_type` indicating message type

#### Scenario: Send message with streaming response
- **GIVEN** user sends message "为什么会这样?"
- **WHEN** `POST /conversations/{id}/messages` is called
- **THEN** the system streams AI response chunks in real-time using Server-Sent Events (SSE) format

---

### Requirement: REQ-CONV-007 Database Schema for Conversations
The database MUST support the conversation persistence model with:
- `conversations` table with `(user_id, agent_id)` unique constraint
- `messages` table with `content_type` and `briefing_id` columns
- Foreign key relationships ensuring data integrity
- Indexes for efficient querying

#### Scenario: Unique constraint prevents duplicate conversations
- **GIVEN** a conversation exists for (user A, agent B)
- **WHEN** an attempt is made to insert another conversation with the same (user A, agent B)
- **THEN** the database rejects the insert due to unique constraint violation

#### Scenario: Briefing reference in message
- **GIVEN** a message with `content_type='briefing_card'` and `briefing_id=X`
- **WHEN** briefing X is deleted
- **THEN** the message's `briefing_id` is set to NULL (soft reference), but message content is preserved

#### Scenario: Message indexing for fast retrieval
- **GIVEN** 10,000 messages across multiple conversations
- **WHEN** messages for conversation C are queried
- **THEN** the query uses index `idx_messages_conversation` for efficient lookup
