-- RLS Policies Enhancement
-- Add missing policies and improve security

-- ============================================
-- Messages Table Policies
-- ============================================

-- Users can create messages in their own conversations
CREATE POLICY "Users can create messages in own conversations" ON messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
            AND conversations.user_id = auth.uid()
        )
    );

-- ============================================
-- Conversations Table Policies (Additional)
-- ============================================

-- Users can create conversations
CREATE POLICY "Users can create conversations" ON conversations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================
-- Agent Analytics Policies
-- ============================================

-- Service role can manage analytics (for Edge Functions)
CREATE POLICY "Service role can manage analytics" ON agent_analytics
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- Users can read analytics for agents they're subscribed to
CREATE POLICY "Users can read subscribed agent analytics" ON agent_analytics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_agent_subscriptions
            WHERE user_agent_subscriptions.agent_id = agent_analytics.agent_id
            AND user_agent_subscriptions.user_id = auth.uid()
            AND user_agent_subscriptions.is_active = TRUE
        )
    );

-- ============================================
-- Alerts Policies (Additional)
-- ============================================

-- Service role can create alerts (for Edge Functions)
CREATE POLICY "Service role can create alerts" ON alerts
    FOR INSERT WITH CHECK (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- ============================================
-- Helper Functions
-- ============================================

-- Function to get user's active subscriptions
CREATE OR REPLACE FUNCTION get_user_active_subscriptions(p_user_id UUID)
RETURNS TABLE (
    subscription_id UUID,
    agent_id UUID,
    agent_name VARCHAR,
    agent_role VARCHAR,
    subscribed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.agent_id,
        a.name,
        a.role,
        s.subscribed_at
    FROM user_agent_subscriptions s
    JOIN agents a ON a.id = s.agent_id
    WHERE s.user_id = p_user_id
    AND s.is_active = TRUE
    AND a.is_active = TRUE
    ORDER BY s.subscribed_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is subscribed to agent
CREATE OR REPLACE FUNCTION is_user_subscribed(p_user_id UUID, p_agent_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_agent_subscriptions
        WHERE user_id = p_user_id
        AND agent_id = p_agent_id
        AND is_active = TRUE
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get conversation context with agent info
CREATE OR REPLACE FUNCTION get_conversation_with_context(p_conversation_id UUID)
RETURNS TABLE (
    conversation_id UUID,
    user_id UUID,
    agent_id UUID,
    agent_name VARCHAR,
    agent_role VARCHAR,
    agent_description TEXT,
    agent_capabilities JSONB,
    conversation_context JSONB,
    message_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.user_id,
        c.agent_id,
        a.name,
        a.role,
        a.description,
        a.capabilities,
        c.context,
        COUNT(m.id)
    FROM conversations c
    JOIN agents a ON a.id = c.agent_id
    LEFT JOIN messages m ON m.conversation_id = c.id
    WHERE c.id = p_conversation_id
    GROUP BY c.id, a.id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create alert (for Edge Functions)
CREATE OR REPLACE FUNCTION create_alert_for_user(
    p_agent_id UUID,
    p_user_id UUID,
    p_title VARCHAR,
    p_description TEXT,
    p_severity VARCHAR,
    p_data JSONB
)
RETURNS UUID AS $$
DECLARE
    v_alert_id UUID;
BEGIN
    -- Check if user is subscribed to agent
    IF NOT is_user_subscribed(p_user_id, p_agent_id) THEN
        RAISE EXCEPTION 'User is not subscribed to this agent';
    END IF;

    -- Create alert
    INSERT INTO alerts (
        agent_id,
        user_id,
        title,
        description,
        severity,
        data
    ) VALUES (
        p_agent_id,
        p_user_id,
        p_title,
        p_description,
        p_severity,
        p_data
    )
    RETURNING id INTO v_alert_id;

    RETURN v_alert_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION get_user_active_subscriptions TO authenticated;
GRANT EXECUTE ON FUNCTION is_user_subscribed TO authenticated;
GRANT EXECUTE ON FUNCTION get_conversation_with_context TO authenticated;

-- Grant to service role (for Edge Functions)
GRANT EXECUTE ON FUNCTION create_alert_for_user TO service_role;

-- Add comments
COMMENT ON FUNCTION get_user_active_subscriptions IS '获取用户的活跃订阅';
COMMENT ON FUNCTION is_user_subscribed IS '检查用户是否订阅了某个AI员工';
COMMENT ON FUNCTION get_conversation_with_context IS '获取对话及相关Agent信息';
COMMENT ON FUNCTION create_alert_for_user IS '为用户创建提醒（供Edge Functions使用）';
