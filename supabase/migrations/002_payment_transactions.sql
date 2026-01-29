-- Payment Transactions Table
-- Stores all payment transaction records with PhonePe integration

CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    merchant_order_id VARCHAR(255) UNIQUE NOT NULL,
    phonepe_transaction_id VARCHAR(255),
    amount INTEGER NOT NULL CHECK (amount >= 100), -- in paise (1 INR = 100 paise), minimum ₹1
    currency VARCHAR(3) DEFAULT 'INR' CHECK (currency IN ('INR')),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded', 'cancelled')),
    payment_method VARCHAR(100),
    payment_gateway VARCHAR(50) DEFAULT 'phonepe',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    phonepe_response JSONB,
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT payment_transactions_amount_check CHECK (amount > 0),
    CONSTRAINT payment_transactions_status_check CHECK (status IS NOT NULL)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_payment_transactions_workspace_id ON payment_transactions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_merchant_order_id ON payment_transactions(merchant_order_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_phonepe_transaction_id ON payment_transactions(phonepe_transaction_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_created_at ON payment_transactions(created_at);

-- RLS (Row Level Security) Policies
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view transactions for their own workspaces
CREATE POLICY "Users can view own workspace transactions" ON payment_transactions
    FOR SELECT
    USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
        )
    );

-- Policy: Users can insert transactions for their own workspaces
CREATE POLICY "Users can insert own workspace transactions" ON payment_transactions
    FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
        )
    );

-- Policy: Service role can do anything (for webhooks and backend processes)
CREATE POLICY "Service role full access" ON payment_transactions
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_payment_transactions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER payment_transactions_updated_at
    BEFORE UPDATE ON payment_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_payment_transactions_updated_at();

-- Comments for documentation
COMMENT ON TABLE payment_transactions IS 'Stores all payment transaction records with PhonePe integration';
COMMENT ON COLUMN payment_transactions.id IS 'Unique identifier for the transaction';
COMMENT ON COLUMN payment_transactions.workspace_id IS 'Workspace that owns this transaction';
COMMENT ON COLUMN payment_transactions.merchant_order_id IS 'Unique order ID from our system';
COMMENT ON COLUMN payment_transactions.phonepe_transaction_id IS 'Transaction ID from PhonePe';
COMMENT ON COLUMN payment_transactions.amount IS 'Amount in paise (1 INR = 100 paise)';
COMMENT ON COLUMN payment_transactions.currency IS 'Currency code (currently only INR supported)';
COMMENT ON COLUMN payment_transactions.status IS 'Current status of the transaction';
COMMENT ON COLUMN payment_transactions.payment_method IS 'Payment method used (UPI, card, etc.)';
COMMENT ON COLUMN payment_transactions.payment_gateway IS 'Payment gateway used (phonepe)';
COMMENT ON COLUMN payment_transactions.phonepe_response IS 'Raw response from PhonePe API';
COMMENT ON COLUMN payment_transactions.metadata IS 'Additional metadata about the transaction';
