-- Refunds table migration
-- Creates comprehensive refund tracking system

BEGIN;

-- Create refunds table
CREATE TABLE IF NOT EXISTS refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_order_id VARCHAR(255) NOT NULL REFERENCES payment_transactions(merchant_order_id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    refund_amount INTEGER NOT NULL CHECK (refund_amount > 0),
    reason TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    phonepe_refund_id VARCHAR(255),
    refund_idempotency_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_refunds_original_order_id ON refunds(original_order_id);
CREATE INDEX IF NOT EXISTS idx_refunds_workspace_id ON refunds(workspace_id);
CREATE INDEX IF NOT EXISTS idx_refunds_status ON refunds(status);
CREATE INDEX IF NOT EXISTS idx_refunds_created_at ON refunds(created_at);
CREATE INDEX IF NOT EXISTS idx_refunds_idempotency_key ON refunds(refund_idempotency_key);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_refunds_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER refunds_updated_at
    BEFORE UPDATE ON refunds
    FOR EACH ROW
    EXECUTE FUNCTION update_refunds_updated_at();

-- RLS policies
ALTER TABLE refunds ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view refunds for their own workspaces
CREATE POLICY "Users can view own workspace refunds" ON refunds
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE owner_id = auth.uid()
        )
    );

-- Policy: System can insert refunds (for webhook processing)
CREATE POLICY "System can insert refunds" ON refunds
    FOR INSERT WITH CHECK (true);

-- Policy: System can update refunds (for webhook processing)
CREATE POLICY "System can update refunds" ON refunds
    FOR UPDATE USING (true);

-- Comments for documentation
COMMENT ON TABLE refunds IS 'Stores all refund records with tracking and validation';
COMMENT ON COLUMN refunds.id IS 'Unique identifier for the refund';
COMMENT ON COLUMN refunds.original_order_id IS 'Reference to original payment transaction';
COMMENT ON COLUMN refunds.workspace_id IS 'Workspace that owns this refund';
COMMENT ON COLUMN refunds.refund_amount IS 'Refund amount in paise (1 INR = 100 paise)';
COMMENT ON COLUMN refunds.reason IS 'Reason for the refund';
COMMENT ON COLUMN refunds.status IS 'Current status of the refund';
COMMENT ON COLUMN refunds.phonepe_refund_id IS 'Refund ID from PhonePe';
COMMENT ON COLUMN refunds.refund_idempotency_key IS 'Idempotency key to prevent duplicate refunds';
COMMENT ON COLUMN refunds.created_at IS 'When the refund was initiated';
COMMENT ON COLUMN refunds.updated_at IS 'When the refund was last updated';
COMMENT ON COLUMN refunds.completed_at IS 'When the refund was completed';
COMMENT ON COLUMN refunds.failed_at IS 'When the refund failed';
COMMENT ON COLUMN refunds.error_message IS 'Error message if refund failed';
COMMENT ON COLUMN refunds.metadata IS 'Additional metadata about the refund';

COMMIT;
