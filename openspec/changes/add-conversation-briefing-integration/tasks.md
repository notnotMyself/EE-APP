# Implementation Tasks

## Phase 1: Database Schema + Service Layer (4-6 hours)

### 1.1 Database Schema Changes
- [x] 1.1.1 Create Supabase migration `20250107000000_add_conversation_briefing_integration.sql`
- [x] 1.1.2 Add `content_type TEXT NOT NULL DEFAULT 'text'` column to `messages` table
- [x] 1.1.3 Add `briefing_id UUID REFERENCES briefings(id) ON DELETE SET NULL` column to `messages` table
- [x] 1.1.4 Add unique constraint `UNIQUE(user_id, agent_id)` to `conversations` table (prevent duplicate conversations)
- [x] 1.1.5 Create index `idx_messages_briefing` on `messages(briefing_id)` for fast lookups
- [ ] 1.1.6 Apply migration to Supabase database
- [ ] 1.1.7 Verify schema changes with `psql` or Supabase Studio

### 1.2 Data Models
- [x] 1.2.1 Create `backend/agent_orchestrator/models/__init__.py` if not exists
- [x] 1.2.2 Create `backend/agent_orchestrator/models/conversation.py` with `ConversationModel` class
  - [x] Implement `__init__(supabase: Client)`
  - [x] Implement `get_or_create(user_id: str, agent_id: str) -> dict`
  - [x] Implement `get_by_id(conversation_id: str) -> Optional[dict]`
  - [x] Implement `update_last_message_time(conversation_id: str) -> None`
- [x] 1.2.3 Create `backend/agent_orchestrator/models/message.py` with `MessageModel` class
  - [x] Implement `__init__(supabase: Client)`
  - [x] Implement `create_text_message(conversation_id, role, content) -> dict`
  - [x] Implement `create_briefing_card(conversation_id, briefing_id, briefing_data) -> dict`
  - [x] Implement `list_by_conversation(conversation_id, limit=50) -> List[dict]`
  - [x] Implement `get_recent_messages(conversation_id, count=20) -> List[dict]`
- [ ] 1.2.4 Test: Verify `get_or_create()` creates conversation on first call, reuses on second call
- [ ] 1.2.5 Test: Verify `create_briefing_card()` stores correct JSON structure

### 1.3 ConversationService
- [x] 1.3.1 Create `backend/agent_orchestrator/services/conversation_service.py`
- [x] 1.3.2 Implement `ConversationService.__init__(supabase, agent_manager, briefing_service)`
- [x] 1.3.3 Implement `get_or_create_conversation(user_id, agent_id) -> str` (returns conversation_id)
- [x] 1.3.4 Implement `add_briefing_to_conversation(briefing_id, user_id, agent_id) -> str`
  - [x] Call `get_or_create_conversation()`
  - [x] Fetch briefing details via `briefing_service` (fallback to direct DB query)
  - [x] Call `message_model.create_briefing_card()`
  - [x] Update conversation timestamp
  - [x] Return conversation_id
- [x] 1.3.5 Implement `send_message(conversation_id, user_message) -> AsyncGenerator`
  - [x] Save user message to database
  - [x] Fetch conversation context (last 20 messages)
  - [x] Build context prompt with `_build_context_with_briefings()`
  - [x] Stream AI response via `agent_manager.execute_query()`
  - [x] Save assistant response to database
  - [x] Update conversation timestamp
- [x] 1.3.6 Implement `_build_context_with_briefings(conversation, messages) -> str` (private helper)
  - [x] Format briefing cards as structured text
  - [x] Format text messages as dialogue
  - [x] Limit to last 20 messages
- [ ] 1.3.7 Test: Verify briefing card appears in context prompt correctly

### 1.4 BriefingService Integration
- [x] 1.4.1 Modify `backend/agent_orchestrator/services/briefing_service.py`
- [x] 1.4.2 Inject `ConversationService` into `BriefingService.__init__()` (handle circular dependency)
- [x] 1.4.3 Replace L283-294 `conversation_id = None` with call to `conversation_service.add_briefing_to_conversation()`
- [ ] 1.4.4 Test: Create briefing → Execute "start_conversation" action → Verify conversation_id returned
- [ ] 1.4.5 Test: Create second briefing for same agent → Verify same conversation_id returned

## Phase 2: API Layer (3-4 hours)

### 2.1 Conversation API Endpoints
- [x] 2.1.1 Create `backend/agent_orchestrator/api/__init__.py` if not exists
- [x] 2.1.2 Create `backend/agent_orchestrator/api/conversations.py` router
- [ ] 2.1.3 Define Pydantic schemas:
  - [ ] `ConversationResponse` (id, user_id, agent_id, title, started_at, last_message_at)
  - [ ] `MessageResponse` (id, conversation_id, role, content_type, content, briefing_id, created_at)
  - [ ] `MessageCreate` (content: str)
- [x] 2.1.4 Implement `GET /api/v1/conversations/{agent_id}` endpoint
  - [ ] Call `conversation_service.get_or_create_conversation(current_user.id, agent_id)`
  - [ ] Return `ConversationResponse`
  - [ ] Handle authentication with `Depends(get_current_user)`
- [x] 2.1.5 Implement `GET /api/v1/conversations/{conversation_id}/messages` endpoint
  - [ ] Call `conversation_service.message_model.list_by_conversation()`
  - [ ] Return `List[MessageResponse]`
  - [ ] Verify user owns conversation (security check)
- [x] 2.1.6 Implement `POST /api/v1/conversations/{conversation_id}/messages` endpoint (streaming)
  - [ ] Parse `MessageCreate` body
  - [ ] Call `conversation_service.send_message()` (returns AsyncGenerator)
  - [ ] Return `StreamingResponse` with `media_type="text/event-stream"`
  - [ ] Format chunks as `data: {chunk}\n\n`
- [x] 2.1.7 Add error handling for 404 (conversation not found), 403 (unauthorized), 500 (server error)

### 2.2 Router Registration
- [x] 2.2.1 Modify `backend/agent_orchestrator/main.py`
- [x] 2.2.2 Import `conversations` router
- [x] 2.2.3 Initialize `ConversationService` instance (inject dependencies)
- [x] 2.2.4 Register router: `app.include_router(conversations_router, prefix="/api/v1", tags=["conversations"])`
- [ ] 2.2.5 Test: Start server, verify `/docs` shows new conversation endpoints

### 2.3 API Testing
- [ ] 2.3.1 Test `GET /conversations/{agent_id}` with curl/Postman
  - [ ] Verify creates conversation on first call
  - [ ] Verify returns same conversation on second call
- [ ] 2.3.2 Test `GET /conversations/{id}/messages` with curl/Postman
  - [ ] Verify empty messages list for new conversation
  - [ ] Verify briefing card appears after adding briefing
- [ ] 2.3.3 Test `POST /conversations/{id}/messages` with curl/Postman
  - [ ] Verify streaming response works
  - [ ] Verify message saved to database
  - [ ] Verify AI references briefing in response

## Phase 3: Frontend Integration (4-6 hours)

### 3.1 Flutter Service Layer
- [ ] 3.1.1 Update `ai_agent_app/lib/services/briefing_service.dart`
  - [ ] Modify `executeBriefingAction()` to handle new conversation flow
  - [ ] Parse `conversation_id` from response
- [ ] 3.1.2 Create `ai_agent_app/lib/services/conversation_service.dart` (if not exists)
  - [ ] Add `getConversationWithAgent(agentId)` method
  - [ ] Add `getMessages(conversationId)` method
  - [ ] Add `sendMessage(conversationId, content)` method (streaming)
- [ ] 3.1.3 Test: Verify service methods work with backend API

### 3.2 UI Components
- [ ] 3.2.1 Create `ai_agent_app/lib/widgets/briefing_card.dart` widget
  - [ ] Display briefing title, summary, priority badge, timestamp
  - [ ] Show expandable/collapsible detail view
  - [ ] Style differently from text messages (card with border)
- [ ] 3.2.2 Modify `ai_agent_app/lib/screens/conversation_screen.dart`
  - [ ] Fetch messages including briefing cards
  - [ ] Render `BriefingCard` widget for `content_type='briefing_card'`
  - [ ] Render `MessageBubble` widget for `content_type='text'`
  - [ ] Maintain chronological order
- [ ] 3.2.3 Update briefing feed screen
  - [ ] Modify "继续对话" button handler
  - [ ] Navigate to conversation screen with `conversation_id`

### 3.3 End-to-End Testing
- [ ] 3.3.1 Test: Create briefing → Tap "继续对话" → Verify enters conversation with briefing card visible
- [ ] 3.3.2 Test: Send message "为什么会这样?" → Verify AI response references briefing
- [ ] 3.3.3 Test: Create second briefing for same agent → Tap "继续对话" → Verify enters same conversation
- [ ] 3.3.4 Test: Ask cross-briefing question "这两个问题有关联吗？" → Verify AI correlates both briefings
- [ ] 3.3.5 Test: Close and reopen app → Verify conversation persists
- [ ] 3.3.6 Test: Multiple agents → Verify separate conversations per agent

## Phase 4: Documentation & Validation

### 4.1 Code Documentation
- [ ] 4.1.1 Add docstrings to all new Python classes and methods
- [ ] 4.1.2 Add inline comments for complex logic (context building, get-or-create pattern)
- [ ] 4.1.3 Update `backend/agent_orchestrator/README.md` with conversation service description

### 4.2 OpenSpec Validation
- [ ] 4.2.1 Run `openspec validate add-conversation-briefing-integration --strict`
- [ ] 4.2.2 Fix any validation errors
- [ ] 4.2.3 Verify all scenarios pass

### 4.3 User Acceptance Testing
- [ ] 4.3.1 Deploy to staging environment
- [ ] 4.3.2 Test complete user flow: briefing → conversation → cross-briefing analysis
- [ ] 4.3.3 Collect feedback, iterate if needed
- [ ] 4.3.4 Deploy to production

## Dependencies

- Phase 2 depends on Phase 1 (service layer must exist before API)
- Phase 3 depends on Phase 2 (API must exist before frontend integration)
- All phases depend on 1.1 (database schema must be updated first)

## Parallelizable Work

- 1.2.2 and 1.2.3 (models) can be developed in parallel
- 3.1 and 3.2 can be developed in parallel (service + UI components)

## Estimated Time

- Phase 1: 4-6 hours
- Phase 2: 3-4 hours
- Phase 3: 4-6 hours
- Phase 4: 2-3 hours
- **Total: 13-19 hours (~2 days)**
