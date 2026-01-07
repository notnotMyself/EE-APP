# Design: Conversation-Briefing Integration

## Context

The AI Agent Platform has two separate systems:
1. **Briefing System**: AI agents generate and push briefings to users (working, backed by database)
2. **Chat System**: Streaming chat via WebSocket/SSE (working, but no persistence)

**Problem**: No connection between briefings and conversations. When users want to discuss a briefing, the system returns `conversation_id = None`.

**Stakeholders**:
- Users: Need seamless briefing-to-conversation experience
- Backend: Need conversation persistence without duplicating Agent SDK integration
- Frontend: Need to display briefing cards in conversation UI

**Constraints**:
- Must use existing Claude Agent SDK integration (no reimplementation)
- Must work with existing Supabase schema (additive changes only)
- Must maintain streaming chat experience
- Must handle multiple briefings per agent gracefully

## Goals / Non-Goals

### Goals
- ✅ Enable persistent conversations linked to briefings
- ✅ Support "one conversation per user-agent pair" model (shared conversation)
- ✅ Display briefings as special message cards in conversation stream
- ✅ Allow AI to reference multiple briefings in one conversation (cross-briefing analysis)
- ✅ Preserve streaming response experience
- ✅ Implement in ~2 days (simplified design)

### Non-Goals
- ❌ Multi-turn planning or complex workflows (use simple query-response)
- ❌ Conversation summarization or context window management (future enhancement)
- ❌ Real-time collaboration (multiple users in one conversation)
- ❌ Voice or video messages
- ❌ Message editing or deletion (keep immutable for now)

## Decisions

### Decision 1: Shared Conversation Model ⭐

**What**: Each user + AI agent pair has ONE persistent conversation. Briefings are inserted as special message cards.

**Why**:
- **Better UX**: Users can discuss multiple briefings in one thread (like chatting with a colleague)
- **Cross-briefing analysis**: AI sees all briefings in context, enabling correlation insights
- **Simpler implementation**: Get-or-create pattern instead of managing conversation creation for each briefing
- **Aligns with product vision**: "AI employee" not "ticket system"

**Alternative Considered**: One conversation per briefing (one-to-one model)
- **Rejected because**:
  - Fragments conversations (users jump between dozens of threads)
  - AI can't see relationships between briefings
  - More complex state management
  - Doesn't match "continuous collaboration" mental model

**Impact**:
- Database: Conversations identified by `(user_id, agent_id)` unique pair
- Service: `get_or_create_conversation()` method ensures reuse
- Frontend: Conversation list shows one entry per agent, not per briefing

### Decision 2: Briefing Cards as System Messages

**What**: Briefings are stored as `content_type = 'briefing_card'` messages with `role = 'system'`.

**Why**:
- Unified message stream (no separate briefing table lookup needed for conversation rendering)
- Message ordering is chronological (briefings appear in timeline naturally)
- Easy to filter (frontend can render briefing cards differently from text)
- Enables context building (AI prompt includes briefing cards in history)

**Alternative Considered**: Store briefings separately, link via foreign key
- **Rejected because**:
  - Requires JOIN queries for every conversation render
  - Harder to maintain chronological order
  - More complex frontend logic (fetch messages + fetch briefings + merge)

**Impact**:
- Database: Add `content_type` and `briefing_id` columns to `messages`
- Service: `create_briefing_card()` method in MessageModel
- Context building: Include briefing cards when constructing AI prompt

### Decision 3: Simplified API (3 Endpoints)

**What**: Expose minimal conversation API:
- `GET /conversations/{agent_id}` - Get or create conversation with agent
- `GET /conversations/{conversation_id}/messages` - List messages (including briefing cards)
- `POST /conversations/{conversation_id}/messages` - Send message (streaming)

**Why**:
- Sufficient for MVP (cover all user flows)
- Reduces implementation time (3 endpoints vs original 8-endpoint design)
- Easier to test and maintain

**Alternative Considered**: Full CRUD API (8 endpoints: create, get, list, update, delete, archive, search, stats)
- **Rejected for MVP because**:
  - Overkill for current needs (no conversation editing, archiving, or search required yet)
  - Can be added incrementally if needed

**Impact**:
- API: `conversations.py` router (~100 lines instead of ~250)
- Frontend: Simpler service layer (fewer API methods)

### Decision 4: Context Building Strategy

**What**: Include last 20 messages (including briefing cards) in AI context prompt.

**Why**:
- Balances context richness with token efficiency
- 20 messages typically cover 1-2 hours of conversation
- Briefing cards are concise (title + summary), fit within limits

**Alternative Considered**: Full conversation history every time
- **Rejected because**:
  - Token waste for long conversations
  - Slower response times
  - Can implement smart summarization later if needed

**Alternative Considered**: Only include current briefing context
- **Rejected because**:
  - Defeats purpose of cross-briefing analysis
  - AI can't reference previous discussions

**Impact**:
- Service: `_build_context_with_briefings()` method limits to last 20 messages
- Future: Can add summarization or RAG for long conversations

### Decision 5: Database Schema Changes

**What**: Add two columns to existing `messages` table:
```sql
ALTER TABLE messages
ADD COLUMN content_type TEXT NOT NULL DEFAULT 'text',
ADD COLUMN briefing_id UUID REFERENCES briefings(id);
```

**Why**:
- Minimal schema change (additive only, no data migration)
- Backward compatible (existing messages default to 'text' type)
- No need for new tables

**Alternative Considered**: Create separate `briefing_messages` table
- **Rejected because**:
  - Complicates queries (UNION or multiple tables)
  - Harder to maintain chronological order
  - More complex data model

**Impact**:
- Migration: One new Supabase migration file
- Existing data: Unaffected (default value 'text' applies)

## Architecture

### Data Flow: Briefing Generation → Conversation

```
1. Scheduled Job triggers → BriefingService.generate_briefing()
   ↓
2. BriefingService creates briefing in database
   ↓
3. BriefingService.execute_action("start_conversation")
   ↓
4. ConversationService.add_briefing_to_conversation()
   ├─ ConversationModel.get_or_create(user_id, agent_id)  ← 核心！
   │   ├─ Query: SELECT * WHERE user_id=? AND agent_id=?
   │   ├─ If found: Return existing conversation
   │   └─ If not: INSERT new conversation, return it
   ├─ MessageModel.create_briefing_card(conversation_id, briefing_data)
   │   └─ INSERT message with content_type='briefing_card'
   └─ Return conversation_id
   ↓
5. Frontend receives conversation_id
   ↓
6. Frontend navigates to conversation page
   ↓
7. Frontend fetches messages (includes briefing card)
   ↓
8. User sees briefing card in conversation timeline ✅
```

### Data Flow: User Sends Message

```
1. User types message → POST /conversations/{id}/messages
   ↓
2. ConversationService.send_message()
   ├─ Save user message (content_type='text')
   ├─ Fetch conversation context (last 20 messages)
   ├─ Build prompt including briefing cards:
   │   [简报 2026-01-07 09:00]
   │   标题：代码返工率达到50%
   │   摘要：最近7天...
   │
   │   用户: 为什么这么高？
   │   助手: 我分析了数据，发现...
   │
   │   [简报 2026-01-07 10:00]
   │   标题：Review耗时超标
   │   ...
   ├─ Call AgentManager.execute_query() with context
   ├─ Stream AI response chunks
   └─ Save assistant message (content_type='text')
   ↓
3. Frontend displays streaming response ✅
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Flutter)                                         │
│  ┌──────────────┐     ┌──────────────────┐                │
│  │ BriefingCard │ ──→ │ConversationScreen│                │
│  │  [开始对话]   │     │  - Briefing Cards │                │
│  └──────────────┘     │  - Messages       │                │
│                       │  - Input Box      │                │
│                       └──────────────────┘                │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/SSE
┌──────────────▼──────────────────────────────────────────────┐
│  Backend API (FastAPI)                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ conversations.py Router                               │  │
│  │  GET  /conversations/{agent_id}                       │  │
│  │  GET  /conversations/{id}/messages                    │  │
│  │  POST /conversations/{id}/messages (streaming)        │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼─────────────┐  ┌─────────────────┐ │
│  │ ConversationService              │  │BriefingService  │ │
│  │  - get_or_create_conversation()  │◀─│ (modified)      │ │
│  │  - add_briefing_to_conversation()│  └─────────────────┘ │
│  │  - send_message()                │                      │
│  │  - _build_context_with_briefings()│                     │
│  └──────┬────────────────────┬──────┘                      │
│         │                    │                             │
│  ┌──────▼──────┐     ┌──────▼──────┐   ┌───────────────┐ │
│  │Conversation │     │   Message   │   │ AgentManager  │ │
│  │   Model     │     │    Model    │   │ (Agent SDK)   │ │
│  └─────────────┘     └─────────────┘   └───────────────┘ │
└──────────────┬──────────────────────────────────────────────┘
               │ Supabase Client
┌──────────────▼──────────────────────────────────────────────┐
│  Database (Supabase PostgreSQL)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │conversations │  │   messages   │  │    briefings     │ │
│  │              │  │ + content_type│  │                  │ │
│  │              │  │ + briefing_id │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

### Risk 1: Context Window Limits
**Risk**: Long conversations may exceed Claude's context window.

**Mitigation**:
- Limit to last 20 messages for now (typically fits in ~4k tokens)
- Future: Implement conversation summarization
- Future: Use RAG to retrieve relevant past messages

**Trade-off**: Short-term memory vs implementation complexity

### Risk 2: Briefing Card Formatting Consistency
**Risk**: Frontend and AI might interpret briefing card content differently.

**Mitigation**:
- Use strict JSON schema for briefing card `content` field
- Document format in spec
- Add validation in MessageModel

**Trade-off**: Flexibility vs consistency

### Risk 3: Conversation List Growth
**Risk**: Users may have many conversations (one per agent), cluttering UI.

**Mitigation**:
- Frontend can filter inactive conversations
- Future: Add conversation archiving feature
- MVP: Limited agents means limited conversations

**Trade-off**: Simplicity now vs scalability later

### Risk 4: Concurrent Briefings
**Risk**: If two briefings arrive simultaneously, both try to create conversation (race condition).

**Mitigation**:
- Database unique constraint on `(user_id, agent_id)` (not added yet, but can be)
- Python `get_or_create` pattern handles race gracefully (query first)
- Low probability (briefings spaced by minutes/hours)

**Trade-off**: Accept small risk vs complex locking mechanism

## Migration Plan

### Phase 1: Database + Service Layer (~4-6h)
1. Create Supabase migration: Add columns to `messages` table
2. Create `models/conversation.py` (~80 lines)
3. Create `models/message.py` (~80 lines)
4. Create `services/conversation_service.py` (~150 lines)
5. Modify `services/briefing_service.py:283-294` to call `add_briefing_to_conversation()`
6. Test: Verify briefing creates conversation and inserts briefing card

### Phase 2: API Layer (~3-4h)
1. Create `api/conversations.py` with 3 endpoints (~100 lines)
2. Register router in `main.py`
3. Test: Verify endpoints work via curl/Postman
4. Test: Verify streaming response includes conversation context

### Phase 3: Frontend Integration (~4-6h)
1. Update `briefing_service.dart` to handle new conversation flow
2. Create `BriefingCard` widget component
3. Update `ConversationScreen` to render briefing cards
4. Test: Full flow from briefing → conversation → cross-briefing question

### Rollback Steps
1. If Phase 1 fails: Drop new columns, revert code changes
2. If Phase 2 fails: Remove router registration, keep old chat endpoints
3. If Phase 3 fails: Frontend can still use old chat flow (no breaking changes)

## Open Questions

1. **Q**: Should we add a unique constraint on `(user_id, agent_id)` in conversations table?
   **A**: Yes, add in migration to prevent duplicate conversations.

2. **Q**: How to handle deleted briefings that are referenced in messages?
   **A**: Use `ON DELETE SET NULL` for `briefing_id` foreign key. Message content is preserved even if briefing deleted.

3. **Q**: Should conversation title be auto-generated or user-editable?
   **A**: Auto-generate for now (`"与 {agent_name} 的对话"`), add editing later if needed.

4. **Q**: How to indicate "new briefing" vs "old briefing" in conversation UI?
   **A**: Frontend can check `briefing.created_at` and show badge if < 24h old.

5. **Q**: Should we support multiple users in one conversation (team collaboration)?
   **A**: Not in MVP. Each user has their own conversation with each agent.

## Performance Considerations

- **Database queries**: Added index on `(user_id, agent_id)` for fast conversation lookup
- **Message retrieval**: Existing index on `(conversation_id, created_at)` covers it
- **Context building**: Limiting to 20 messages keeps prompt size manageable
- **Streaming**: No change to existing streaming mechanism (already optimized)

## Security Considerations

- **RLS Policies**: Existing policies ensure users only see their own conversations
- **Briefing access**: Users can only add briefings they own to conversations
- **Agent access**: Users can only create conversations with agents they subscribe to (enforcement needed in service layer)

## Testing Strategy

### Unit Tests
- `ConversationModel.get_or_create()` - Test both create and reuse paths
- `MessageModel.create_briefing_card()` - Test JSON structure
- `ConversationService._build_context_with_briefings()` - Test prompt formatting

### Integration Tests
- Full briefing-to-conversation flow
- Streaming response with context
- Multiple briefings in one conversation

### Manual Testing
- Create briefing → Click "继续对话" → Verify conversation created
- Send message → Verify AI references briefing in response
- Create second briefing → Verify added to same conversation
- Ask cross-briefing question → Verify AI correlates both briefings
