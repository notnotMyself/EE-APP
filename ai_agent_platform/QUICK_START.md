# AI Agent Platform - Quick Start Guide

## Phase 1 Progress

✅ Database schema designed
✅ Backend project structure created
✅ Supabase connection configured
✅ User authentication API implemented

## Next Steps

### 1. Run Database Migrations

First, you need to run the database migrations in Supabase:

1. Go to [Supabase SQL Editor](https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/sql/new)
2. Copy the content from `backend/migrations/001_initial_schema.sql`
3. Paste and run the SQL

### 2. Install Backend Dependencies

```bash
cd ai_agent_platform/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

The `.env` file is already configured with your Supabase credentials. You just need to:

1. Get your database password from Supabase Dashboard
2. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://postgres.dwesyojvzbltqtgtctpt:[YOUR_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
3. Add your Claude API key:
   ```
   CLAUDE_API_KEY=your_claude_api_key_here
   ```

### 4. Start the Backend Server

```bash
cd backend
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Test Authentication

Once the server is running, you can test authentication:

**Register a new user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

**Get current user** (use the access_token from login):
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Structure

```
ai_agent_platform/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── endpoints/
│   │   │       └── auth.py    # ✅ Authentication endpoints
│   │   ├── core/
│   │   │   ├── config.py      # ✅ Configuration
│   │   │   └── security.py    # ✅ JWT & password hashing
│   │   ├── db/
│   │   │   ├── session.py     # ✅ Database session
│   │   │   └── supabase.py    # ✅ Supabase client
│   │   ├── models/
│   │   │   └── user.py        # ✅ User model
│   │   └── schemas/
│   │       └── user.py        # ✅ User schemas
│   ├── migrations/
│   │   └── 001_initial_schema.sql  # ✅ Database schema
│   ├── .env                   # ✅ Environment variables
│   ├── requirements.txt       # ✅ Python dependencies
│   └── main.py                # ✅ Application entry point
│
├── flutter_app/               # Flutter app (TODO)
├── docs/                      # Documentation
└── scripts/                   # Utility scripts
```

## What's Implemented

### Backend (Phase 1 - Part 1)

**✅ Database Schema:**
- users
- agents (AI员工定义)
- user_agent_subscriptions (订阅关系)
- alerts (AI提醒)
- conversations (对话)
- messages (消息)
- tasks (持续任务)
- artifacts (AI产出)
- agent_analytics (分析数据)

**✅ User Authentication:**
- POST `/api/v1/auth/register` - Register new user
- POST `/api/v1/auth/login` - Login and get JWT token
- GET `/api/v1/auth/me` - Get current user
- POST `/api/v1/auth/test-token` - Test JWT token

**✅ Security:**
- JWT authentication
- Password hashing (bcrypt)
- OAuth2 password flow

**✅ Configuration:**
- Supabase integration
- Environment variables management
- CORS setup

## Next Tasks (Phase 1 - Part 2)

- [ ] Implement AI员工 CRUD API
- [ ] Implement 订阅管理 API
- [ ] Integrate Claude API
- [ ] Implement SSE streaming
- [ ] Initialize Flutter project

## Troubleshooting

**Database connection issues:**
- Make sure you've run the migrations in Supabase
- Check your DATABASE_URL has the correct password
- Verify Supabase project is active

**Import errors:**
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Authentication not working:**
- Check SECRET_KEY is set in .env
- Make sure migrations have created the users table
- Verify JWT token is being sent in Authorization header

## Database Password

To get your database password:
1. Go to [Supabase Dashboard](https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/settings/database)
2. Click "Database" in settings
3. Copy the password (or reset if needed)
