# Tasks: Add Briefing System

## Implementation Checklist

### Phase 1: Database Schema
- [x] Create migration file `supabase/migrations/20250104000000_add_briefings.sql`
- [x] Define `briefings` table (type, priority, title, summary, impact, actions, context_data, status)
- [x] Define `scheduled_jobs` table (cron_expression, task_prompt, briefing_config)
- [x] Add RLS policies and indexes

### Phase 2: Backend Models & Schemas
- [x] Create `app/models/briefing.py` - SQLAlchemy models for Briefing and ScheduledJob
- [x] Create `app/schemas/briefing.py` - Pydantic schemas with enums
- [x] Create `app/crud/crud_briefing.py` - CRUD operations

### Phase 3: Backend Services
- [x] Create `app/services/briefing_service.py` - 简报生成核心逻辑
  - [x] Implement `BRIEFING_DECISION_PROMPT` for AI judgment
  - [x] Implement `execute_and_generate_briefing()` main entry
  - [x] Implement `_decide_briefing()` with importance score check
  - [x] Implement `_create_briefing_for_user()` for record creation
- [x] Create `app/services/scheduler_service.py` - APScheduler 调度器
  - [x] Implement `_load_jobs_from_db()` for startup job loading
  - [x] Implement `_execute_scheduled_job()` for task execution
  - [x] Implement `trigger_job_manually()` for testing

### Phase 4: Backend API
- [x] Create `app/api/v1/endpoints/briefings.py`
  - [x] GET `/briefings` - list briefings (feed)
  - [x] GET `/briefings/unread-count` - unread count
  - [x] PATCH `/briefings/{id}/read` - mark as read
  - [x] POST `/briefings/{id}/start-conversation` - start conversation from briefing
  - [x] DELETE `/briefings/{id}` - dismiss briefing

### Phase 5: Backend Integration
- [x] Update `main.py` - add lifespan context manager for scheduler
- [x] Update `app/api/v1/__init__.py` - register briefings router
- [x] Update `requirements.txt` - add apscheduler, croniter, supabase dependencies

### Phase 6: Flutter Data Layer
- [x] Create `lib/features/briefings/domain/models/briefing.dart`
  - [x] Define Freezed models: Briefing, BriefingAction, BriefingListResponse
  - [x] Define enums: BriefingType, BriefingPriority, BriefingStatus
- [x] Create `lib/features/briefings/data/briefing_repository.dart`
  - [x] Implement API calls for getBriefings, markAsRead, startConversation, dismissBriefing

### Phase 7: Flutter Presentation Layer
- [x] Create `lib/features/briefings/presentation/controllers/briefing_controller.dart`
  - [x] Implement Riverpod providers: briefingsProvider, briefingUnreadCountProvider
  - [x] Implement BriefingController with state management
- [x] Create `lib/features/briefings/presentation/widgets/briefing_card.dart`
  - [x] Implement card UI with header, title, summary, impact, actions
  - [x] Implement color coding by priority and type
- [x] Create `lib/features/briefings/presentation/pages/briefings_feed_page.dart`
  - [x] Implement main feed page with RefreshIndicator
  - [x] Implement empty state and error state
  - [x] Implement bottom sheet for briefing details
  - [x] Implement navigation to conversation page

### Phase 8: Routing & Configuration
- [x] Update `lib/core/router/app_router.dart` - add `/feed` route, update default redirect
- [x] Update `backend/agents/dev_efficiency_analyst/CLAUDE.md` - add 简报生成指南 section

## File Summary

### New Files Created
| File | Purpose |
|------|---------|
| `supabase/migrations/20250104000000_add_briefings.sql` | Database migration |
| `ai_agent_platform/backend/app/models/briefing.py` | SQLAlchemy models |
| `ai_agent_platform/backend/app/schemas/briefing.py` | Pydantic schemas |
| `ai_agent_platform/backend/app/crud/crud_briefing.py` | CRUD operations |
| `ai_agent_platform/backend/app/services/briefing_service.py` | Briefing generation service |
| `ai_agent_platform/backend/app/services/scheduler_service.py` | APScheduler service |
| `ai_agent_platform/backend/app/api/v1/endpoints/briefings.py` | API endpoints |
| `ai_agent_app/lib/features/briefings/domain/models/briefing.dart` | Flutter data models |
| `ai_agent_app/lib/features/briefings/data/briefing_repository.dart` | Flutter repository |
| `ai_agent_app/lib/features/briefings/presentation/controllers/briefing_controller.dart` | Riverpod controllers |
| `ai_agent_app/lib/features/briefings/presentation/widgets/briefing_card.dart` | Card widget |
| `ai_agent_app/lib/features/briefings/presentation/pages/briefings_feed_page.dart` | Feed page |

### Modified Files
| File | Changes |
|------|---------|
| `ai_agent_platform/backend/main.py` | Added scheduler lifespan management |
| `ai_agent_platform/backend/app/api/v1/__init__.py` | Registered briefings router |
| `ai_agent_platform/backend/requirements.txt` | Added apscheduler, croniter, supabase |
| `ai_agent_app/lib/core/router/app_router.dart` | Added /feed route |
| `backend/agents/dev_efficiency_analyst/CLAUDE.md` | Added briefing generation guide |

## Dependencies Added
- `apscheduler>=3.10.0` - Python task scheduling
- `croniter>=1.3.0` - Cron expression parsing
- `supabase>=2.0.0` - Supabase Python client
