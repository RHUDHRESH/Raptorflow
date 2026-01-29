-- Subscriptions Table
-- Manages subscription plans and lifecycle for workspaces

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    plan VARCHAR(50) NOT NULL CHECK (plan IN ('starter', 'growth', 'enterprise', 'free', 'trial')),
    status VARCHAR(50) NOT NULL DEFAULT 'trial' CHECK (status IN ('trial', 'active', 'past_due', 'canceled', 'unpaid', 'incomplete', 'incomplete_expired', 'paused')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    grace_period_end TIMESTAMP WITH TIME ZONE,
    phonepe_subscription_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT subscriptions_workspace_unique UNIQUE (workspace_id),
    CONSTRAINT subscriptions_period_check CHECK (
        (current_period_start IS NULL AND current_period_end IS NULL) OR
        (current_period_start IS NOT NULL AND current_period_end IS NOT NULL AND current_period_end > current_period_start)
    ),
    CONSTRAINT subscriptions_trial_check CHECK (
        (plan = 'trial' AND trial_end IS NOT NULL) OR
        (plan != 'trial')
    ),
    CONSTRAINT subscriptions_grace_check CHECK (
        (status = 'past_due' AND grace_period_end IS NOT NULL) OR
        (status != 'past_due')
    )
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_id ON subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON subscriptions(plan);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_trial_end ON subscriptions(trial_end);
CREATE INDEX IF NOT EXISTS idx_subscriptions_current_period_end ON subscriptions(current_period_end);
CREATE INDEX IF NOT EXISTS idx_subscriptions_grace_period_end ON subscriptions(grace_period_end);

-- RLS (Row Level Security) Policies
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view subscriptions for their own workspaces
CREATE POLICY "Users can view own workspace subscriptions" ON subscriptions
    FOR SELECT
    USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
        )
    );

-- Policy: Service role can do anything (for webhooks and backend processes)
CREATE POLICY "Service role full access" ON subscriptions
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_subscriptions_updated_at();

-- Function to get active subscription for workspace
CREATE OR REPLACE FUNCTION get_active_subscription(p_workspace_id UUID)
RETURNS TABLE (
    id UUID,
    plan VARCHAR,
    status VARCHAR,
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    grace_period_end TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.plan,
        s.status,
        s.current_period_start,
        s.current_period_end,
        s.trial_end,
        s.grace_period_end
    FROM subscriptions s
    WHERE s.workspace_id = p_workspace_id
    AND (
        s.status = 'active' OR
        s.status = 'trial' OR
        (s.status = 'past_due' AND s.grace_period_end > NOW()) OR
        (s.status = 'canceled' AND s.current_period_end > NOW())
    )
    ORDER BY
        CASE s.status
            WHEN 'active' THEN 1
            WHEN 'trial' THEN 2
            WHEN 'past_due' THEN 3
            WHEN 'canceled' THEN 4
            ELSE 5
        END,
        s.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create or update subscription
CREATE OR REPLACE FUNCTION upsert_subscription(
    p_workspace_id UUID,
    p_plan VARCHAR,
    p_status VARCHAR DEFAULT 'active',
    p_current_period_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    p_current_period_end TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 month'),
    p_trial_end TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_grace_period_end TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_phonepe_subscription_id VARCHAR DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    v_subscription_id UUID;
BEGIN
    -- Try to update existing subscription first
    UPDATE subscriptions
    SET
        plan = p_plan,
        status = p_status,
        current_period_start = p_current_period_start,
        current_period_end = p_current_period_end,
        trial_end = p_trial_end,
        grace_period_end = p_grace_period_end,
        phonepe_subscription_id = p_phonepe_subscription_id,
        metadata = p_metadata
    WHERE workspace_id = p_workspace_id
    RETURNING id INTO v_subscription_id;

    -- If no existing subscription, create new one
    IF v_subscription_id IS NULL THEN
        INSERT INTO subscriptions (
            workspace_id,
            plan,
            status,
            current_period_start,
            current_period_end,
            trial_end,
            grace_period_end,
            phonepe_subscription_id,
            metadata
        ) VALUES (
            p_workspace_id,
            p_plan,
            p_status,
            p_current_period_start,
            p_current_period_end,
            p_trial_end,
            p_grace_period_end,
            p_phonepe_subscription_id,
            p_metadata
        )
        RETURNING id INTO v_subscription_id;
    END IF;

    RETURN v_subscription_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if workspace needs payment
CREATE OR REPLACE FUNCTION workspace_needs_payment(p_workspace_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_subscription RECORD;
    v_needs_payment BOOLEAN := TRUE;
BEGIN
    -- Get active subscription
    SELECT * INTO v_subscription FROM get_active_subscription(p_workspace_id);

    IF NOT FOUND THEN
        -- No subscription found, needs payment
        RETURN TRUE;
    END IF;

    -- Check subscription status and timestamps
    CASE v_subscription.status
        WHEN 'active' THEN
            v_needs_payment := FALSE;
        WHEN 'trial' THEN
            IF v_subscription.trial_end > NOW() THEN
                v_needs_payment := FALSE;
            ELSE
                v_needs_payment := TRUE;
            END IF;
        WHEN 'past_due' THEN
            IF v_subscription.grace_period_end > NOW() THEN
                v_needs_payment := FALSE;
            ELSE
                v_needs_payment := TRUE;
            END IF;
        WHEN 'canceled' THEN
            IF v_subscription.current_period_end > NOW() THEN
                v_needs_payment := FALSE;
            ELSE
                v_needs_payment := TRUE;
            END IF;
        ELSE
            -- unpaid, incomplete, incomplete_expired, paused
            v_needs_payment := TRUE;
    END CASE;

    RETURN v_needs_payment;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Comments for documentation
COMMENT ON TABLE subscriptions IS 'Manages subscription plans and lifecycle for workspaces';
COMMENT ON COLUMN subscriptions.id IS 'Unique identifier for the subscription';
COMMENT ON COLUMN subscriptions.workspace_id IS 'Workspace that owns this subscription';
COMMENT ON COLUMN subscriptions.plan IS 'Subscription plan (starter, growth, enterprise, free, trial)';
COMMENT ON COLUMN subscriptions.status IS 'Current status of the subscription';
COMMENT ON COLUMN subscriptions.current_period_start IS 'Start of current billing period';
COMMENT ON COLUMN subscriptions.current_period_end IS 'End of current billing period';
COMMENT ON COLUMN subscriptions.trial_end IS 'End of trial period (if applicable)';
COMMENT ON COLUMN subscriptions.grace_period_end IS 'End of grace period for past_due subscriptions';
COMMENT ON COLUMN subscriptions.phonepe_subscription_id IS 'Subscription ID from PhonePe (if applicable)';
COMMENT ON COLUMN subscriptions.metadata IS 'Additional metadata about the subscription';

COMMENT ON FUNCTION get_active_subscription(p_workspace_id UUID) IS 'Returns the active subscription for a workspace';
COMMENT ON FUNCTION upsert_subscription(...) IS 'Creates or updates a subscription for a workspace';
COMMENT ON FUNCTION workspace_needs_payment(p_workspace_id UUID) IS 'Checks if a workspace needs to make a payment';
