# Change: Add Conversation-Briefing Integration

## Why

Currently, the briefing system generates AI employee briefings but lacks a persistent conversation system to enable users to discuss them. The existing chat endpoints in `agent_orchestrator` provide streaming responses but don't save conversation history or link briefings to conversations.

**Critical Gap**: When users click "继续对话" (Start Conversation) on a briefing, the system returns `conversation_id = None` (`briefing_service.py:283`), breaking the user experience loop.

**Design Decision**: Instead of creating a separate conversation for each briefing (one-to-one model), we adopt a **shared conversation model** where each user + AI agent pair has ONE continuous conversation, with briefings appearing as special message cards within the conversation stream. This enables:
- Cross-briefing analysis (AI can see relationships between multiple briefings)
- Continuous dialogue experience (like chatting with a colleague)
- Long-term memory (AI remembers previous discussions)
- Better alignment with "AI employee" positioning

## What Changes

- **Database Schema** (Supabase migration):
  - Add `content_type` column to `messages` table (values: 'text', 'briefing_card')
  - Add `briefing_id` column to `messages` table (nullable UUID reference)

- **New Data Models** (`backend/agent_orchestrator/models/`):
  - `conversation.py` - Conversation model with get-or-create pattern
  - `message.py` - Message model supporting polymorphic content types

- **New Service** (`backend/agent_orchestrator/services/`):
  - `conversation_service.py` - Orchestrates conversation logic, briefing integration, Agent SDK streaming

- **Modified Service**:
  - `briefing_service.py:283-294` - Integrate `add_briefing_to_conversation()` method

- **New API** (`backend/agent_orchestrator/api/`):
  - `conversations.py` - 3 REST endpoints (simplified from original 8-endpoint design)

- **Router Registration**:
  - `main.py` - Register conversation routes

## Impact

### Affected Specs
- `briefing-system` - MODIFIED (add briefing-to-conversation linkage requirement)
- `conversation-persistence` - ADDED (new capability for conversation management)

### Affected Code
- **Database**: Supabase `messages` table schema
- **Backend**:
  - `backend/agent_orchestrator/models/` (2 new files)
  - `backend/agent_orchestrator/services/conversation_service.py` (new)
  - `backend/agent_orchestrator/services/briefing_service.py` (modified)
  - `backend/agent_orchestrator/api/conversations.py` (new)
  - `backend/agent_orchestrator/main.py` (modified)
- **Frontend**:
  - `ai_agent_app/lib/services/briefing_service.dart` (to be modified in Phase 3)
  - `ai_agent_app/lib/screens/conversation_screen.dart` (to be modified in Phase 3)

### Breaking Changes
- None (additive changes only, existing chat endpoints remain functional)

### Non-Breaking Enhancements
- Briefings can now be linked to conversations via `conversation_id`
- Users can discuss multiple briefings in a single conversation thread
- AI gains context across briefings for better analysis

## Dependencies

- Claude Agent SDK (already integrated in `agent_manager.py`)
- Supabase Python client (already configured)
- FastAPI streaming (already implemented in `main.py`)

## Rollback Strategy

If issues arise:
1. Database changes are additive (new columns with defaults) - no data loss
2. Old chat endpoints remain functional
3. Can disable new conversation API endpoints via feature flag
4. Briefings continue to work independently without conversation linkage

## Success Metrics

- Users can click "继续对话" on briefings and enter a persistent conversation
- One conversation per user-agent pair (verified by querying conversations table)
- Briefing cards appear as special messages in conversation stream
- AI can reference multiple briefings when answering questions
- Conversation history persists across sessions
