# AI Agent Platform Backend

FastAPI backend for AI数字员工平台.

## Prerequisites

- Python 3.11+
- PostgreSQL (via Supabase)
- Redis (for Celery tasks)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```bash
# Required:
DATABASE_URL=postgresql://...
CLAUDE_API_KEY=your_api_key
SECRET_KEY=your_secret_key

# See .env file for all configuration options
```

3. Run database migrations:
```bash
# Migrations are managed via Supabase CLI
supabase db push --linked
```

## Running the Server

Development mode:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST /api/v1/auth/register - Register new user
- POST /api/v1/auth/login - Login
- GET /api/v1/auth/me - Get current user

### AI Agents
- GET /api/v1/agents - List agents
- GET /api/v1/agents/{id} - Get agent details
- POST /api/v1/agents - Create agent
- PUT /api/v1/agents/{id} - Update agent
- DELETE /api/v1/agents/{id} - Delete agent

### Subscriptions
- GET /api/v1/subscriptions - List my subscriptions
- POST /api/v1/subscriptions - Subscribe to agent
- DELETE /api/v1/subscriptions/{agent_id} - Unsubscribe

### Conversations
- GET /api/v1/conversations - List my conversations
- GET /api/v1/conversations/{id} - Get conversation with messages
- POST /api/v1/conversations - Create new conversation
- POST /api/v1/conversations/{id}/messages - Send message (non-streaming)
- POST /api/v1/conversations/{id}/messages/stream - Send message (SSE streaming)

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black .
```

Lint:
```bash
flake8 .
```
