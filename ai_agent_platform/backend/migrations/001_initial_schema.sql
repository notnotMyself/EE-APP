-- AI Agent Platform - Initial Database Schema
-- Migration 001: Create core tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI Agents table (AI员工定义)
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    role VARCHAR(100) NOT NULL, -- e.g., "dev_efficiency_analyst"
    avatar_url TEXT,

    -- Agent configuration
    data_sources JSONB, -- e.g., {"gerrit": {...}, "jira": {...}}
    trigger_conditions JSONB, -- e.g., {"review_time_threshold": 48}
    capabilities JSONB, -- e.g., {"can_generate_reports": true, "can_create_charts": true}

    -- System fields
    is_active BOOLEAN DEFAULT TRUE,
    is_builtin BOOLEAN DEFAULT FALSE, -- True for system-provided agents
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- User-Agent Subscriptions (用户订阅AI员工)
CREATE TABLE IF NOT EXISTS user_agent_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

    -- Subscription configuration (user-specific settings for this agent)
    config JSONB DEFAULT '{}'::jsonb,

    -- Notification preferences
    notify_on_alert BOOLEAN DEFAULT TRUE,
    notify_via_push BOOLEAN DEFAULT TRUE,
    notify_via_email BOOLEAN DEFAULT FALSE,

    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unsubscribed_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Ensure a user can only subscribe to an agent once (active subscription)
    UNIQUE(user_id, agent_id, is_active)
);

-- Alerts (AI员工的主动提醒)
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Alert content
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info', -- info, warning, error, critical

    -- Alert data (for generating insights)
    data JSONB DEFAULT '{}'::jsonb, -- Raw data that triggered this alert

    -- Status tracking
    status VARCHAR(20) DEFAULT 'new', -- new, read, handling, resolved, dismissed
    read_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,

    -- Link to conversation (if user clicked and started conversation)
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Index for faster queries
    INDEX idx_alerts_user_status (user_id, status),
    INDEX idx_alerts_agent (agent_id),
    INDEX idx_alerts_created (created_at DESC)
);

-- Conversations (用户与AI员工的对话)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

    -- Conversation metadata
    title VARCHAR(255), -- Auto-generated or user-set
    context JSONB DEFAULT '{}'::jsonb, -- Context data for this conversation

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, archived, closed

    -- Related alert (if this conversation started from an alert)
    source_alert_id UUID REFERENCES alerts(id) ON DELETE SET NULL,

    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,

    -- Index for faster queries
    INDEX idx_conversations_user (user_id, last_message_at DESC),
    INDEX idx_conversations_agent (agent_id)
);

-- Messages (对话中的消息)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Message content
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,

    -- Message metadata
    metadata JSONB DEFAULT '{}'::jsonb, -- e.g., {"tokens": 150, "model": "claude-3-5-sonnet"}

    -- Attachments (if any)
    attachments JSONB, -- e.g., [{"type": "chart", "url": "..."}]

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Index for faster queries
    INDEX idx_messages_conversation (conversation_id, created_at)
);

-- Tasks (持续任务 - 用户托付给AI的任务)
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Task details
    description TEXT NOT NULL,
    instructions JSONB, -- Detailed instructions from user

    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    progress INTEGER DEFAULT 0, -- 0-100

    -- Results
    result JSONB, -- Task execution result
    error_message TEXT, -- If failed

    -- Scheduling (for recurring tasks)
    schedule JSONB, -- e.g., {"type": "daily", "time": "09:00"}
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_run_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Index for faster queries
    INDEX idx_tasks_user_status (user_id, status),
    INDEX idx_tasks_agent (agent_id),
    INDEX idx_tasks_next_run (next_run_at) WHERE next_run_at IS NOT NULL
);

-- Artifacts (AI生成的产出: 报告、图表、文案等)
CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Related entities
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Artifact details
    type VARCHAR(50) NOT NULL, -- 'report', 'chart', 'document', 'briefing'
    title VARCHAR(255),
    content TEXT NOT NULL, -- Markdown, JSON, or other format
    format VARCHAR(20) DEFAULT 'markdown', -- markdown, json, html, pdf_url

    -- File storage (if applicable)
    file_url TEXT, -- URL to stored file (e.g., Supabase Storage)
    file_size INTEGER, -- in bytes

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Index for faster queries
    INDEX idx_artifacts_user (user_id, created_at DESC),
    INDEX idx_artifacts_conversation (conversation_id),
    INDEX idx_artifacts_type (type)
);

-- Agent Analytics (AI员工的分析数据 - 用于定时任务)
CREATE TABLE IF NOT EXISTS agent_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

    -- Analysis time range
    analysis_date DATE NOT NULL,
    analysis_period VARCHAR(20) DEFAULT 'daily', -- daily, weekly, monthly

    -- Analysis results
    data JSONB NOT NULL, -- Raw analysis data
    insights JSONB, -- Extracted insights
    anomalies JSONB, -- Detected anomalies

    -- Alerts generated from this analysis
    alerts_generated INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique analysis per agent per date
    UNIQUE(agent_id, analysis_date, analysis_period),
    INDEX idx_analytics_agent_date (agent_id, analysis_date DESC)
);

-- Update timestamps trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update_updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_agent_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_analytics ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Anyone can read active agents
CREATE POLICY "Anyone can read active agents" ON agents
    FOR SELECT USING (is_active = TRUE);

-- Users can manage their subscriptions
CREATE POLICY "Users can manage own subscriptions" ON user_agent_subscriptions
    FOR ALL USING (auth.uid() = user_id);

-- Users can only see their own alerts
CREATE POLICY "Users can read own alerts" ON alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own alerts" ON alerts
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can only see their own conversations
CREATE POLICY "Users can read own conversations" ON conversations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own conversations" ON conversations
    FOR ALL USING (auth.uid() = user_id);

-- Users can only see messages in their conversations
CREATE POLICY "Users can read messages in own conversations" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
            AND conversations.user_id = auth.uid()
        )
    );

-- Users can manage their tasks
CREATE POLICY "Users can manage own tasks" ON tasks
    FOR ALL USING (auth.uid() = user_id);

-- Users can manage their artifacts
CREATE POLICY "Users can manage own artifacts" ON artifacts
    FOR ALL USING (auth.uid() = user_id);

-- Comments
COMMENT ON TABLE users IS '用户表';
COMMENT ON TABLE agents IS 'AI员工定义表';
COMMENT ON TABLE user_agent_subscriptions IS '用户订阅AI员工关系表';
COMMENT ON TABLE alerts IS 'AI员工主动提醒表';
COMMENT ON TABLE conversations IS '用户与AI员工的对话表';
COMMENT ON TABLE messages IS '对话消息表';
COMMENT ON TABLE tasks IS '用户托付给AI的持续任务表';
COMMENT ON TABLE artifacts IS 'AI生成的产出(报告、图表等)';
COMMENT ON TABLE agent_analytics IS 'AI员工的分析数据表(用于定时任务)';
