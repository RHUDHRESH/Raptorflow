-- PhonePe Payment Gateway Database Schema
-- Migration file for payment transactions and related tables

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- PAYMENT TRANSACTIONS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Transaction identifiers
    transaction_id VARCHAR(255) UNIQUE NOT NULL,  -- PhonePe transaction ID
    merchant_order_id VARCHAR(255) UNIQUE NOT NULL,  -- Merchant order ID
    merchant_transaction_id VARCHAR(255) UNIQUE NOT NULL,  -- Internal transaction ID

    -- Payment details
    amount BIGINT NOT NULL,  -- Amount in paise
    currency VARCHAR(3) DEFAULT 'INR',

    -- Customer information
    customer_id VARCHAR(255),
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_mobile VARCHAR(20),

    -- URLs
    redirect_url TEXT,
    callback_url TEXT,
    checkout_url TEXT,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'INITIATED',  -- INITIATED, PENDING, COMPLETED, FAILED, REFUNDED
    payment_mode VARCHAR(100),

    -- PhonePe specific fields
    phonepe_transaction_id VARCHAR(255),
    payment_instrument JSONB,  -- Store payment instrument details

    -- Metadata
    metadata JSONB,  -- Additional transaction metadata

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('INITIATED', 'PENDING', 'COMPLETED', 'FAILED', 'REFUNDED', 'CANCELLED')),
    CONSTRAINT positive_amount CHECK (amount > 0)
);

-- ==========================================
-- PAYMENT REFUNDS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS payment_refunds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Refund identifiers
    refund_id VARCHAR(255) UNIQUE NOT NULL,  -- PhonePe refund ID
    merchant_refund_id VARCHAR(255) UNIQUE NOT NULL,  -- Internal refund ID

    -- Reference to original transaction
    transaction_id VARCHAR(255) NOT NULL REFERENCES payment_transactions(transaction_id),

    -- Refund details
    refund_amount BIGINT NOT NULL,
    refund_reason TEXT,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'PROCESSING',  -- PROCESSING, COMPLETED, FAILED

    -- PhonePe specific fields
    phonepe_refund_id VARCHAR(255),

    -- Metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT valid_refund_status CHECK (status IN ('PROCESSING', 'COMPLETED', 'FAILED')),
    CONSTRAINT positive_refund_amount CHECK (refund_amount > 0)
);

-- ==========================================
-- PAYMENT WEBHOOK LOGS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS payment_webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Webhook details
    webhook_id VARCHAR(255) UNIQUE NOT NULL,
    transaction_id VARCHAR(255) REFERENCES payment_transactions(transaction_id),

    -- Webhook content
    callback_type VARCHAR(255) NOT NULL,
    authorization_header TEXT,
    request_body JSONB,

    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,

    -- Timestamps
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- ==========================================
-- PAYMENT EVENTS LOG TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS payment_events_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Event details
    event_type VARCHAR(100) NOT NULL,  -- PAYMENT_INITIATED, PAYMENT_COMPLETED, PAYMENT_FAILED, REFUND_INITIATED, REFUND_COMPLETED
    transaction_id VARCHAR(255) REFERENCES payment_transactions(transaction_id),
    refund_id VARCHAR(255) REFERENCES payment_refunds(refund_id),

    -- Event data
    event_data JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Payment transactions indexes
CREATE INDEX IF NOT EXISTS idx_payment_transactions_transaction_id ON payment_transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_merchant_order_id ON payment_transactions(merchant_order_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_customer_id ON payment_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_created_at ON payment_transactions(created_at);

-- Payment refunds indexes
CREATE INDEX IF NOT EXISTS idx_payment_refunds_transaction_id ON payment_refunds(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payment_refunds_refund_id ON payment_refunds(refund_id);
CREATE INDEX IF NOT EXISTS idx_payment_refunds_status ON payment_refunds(status);
CREATE INDEX IF NOT EXISTS idx_payment_refunds_created_at ON payment_refunds(created_at);

-- Webhook logs indexes
CREATE INDEX IF NOT EXISTS idx_payment_webhook_logs_transaction_id ON payment_webhook_logs(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payment_webhook_logs_callback_type ON payment_webhook_logs(callback_type);
CREATE INDEX IF NOT EXISTS idx_payment_webhook_logs_processed ON payment_webhook_logs(processed);
CREATE INDEX IF NOT EXISTS idx_payment_webhook_logs_received_at ON payment_webhook_logs(received_at);

-- Payment events log indexes
CREATE INDEX IF NOT EXISTS idx_payment_events_log_event_type ON payment_events_log(event_type);
CREATE INDEX IF NOT EXISTS idx_payment_events_log_transaction_id ON payment_events_log(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payment_events_log_created_at ON payment_events_log(created_at);

-- ==========================================
-- TRIGGERS FOR UPDATED_AT
-- ==========================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_payment_transactions_updated_at
    BEFORE UPDATE ON payment_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_refunds_updated_at
    BEFORE UPDATE ON payment_refunds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Enable RLS on payment tables
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_webhook_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_events_log ENABLE ROW LEVEL SECURITY;

-- Policy for payment transactions (users can only see their own transactions)
CREATE POLICY "Users can view own payment transactions" ON payment_transactions
    FOR SELECT USING (customer_id = current_setting('app.current_user_id', true));

-- Policy for payment refunds (users can only see their own refunds)
CREATE POLICY "Users can view own payment refunds" ON payment_refunds
    FOR SELECT USING (
        transaction_id IN (
            SELECT transaction_id FROM payment_transactions
            WHERE customer_id = current_setting('app.current_user_id', true)
        )
    );

-- ==========================================
-- VIEWS FOR COMMON QUERIES
-- ==========================================

-- View for payment summary
CREATE OR REPLACE VIEW payment_summary AS
SELECT
    pt.transaction_id,
    pt.merchant_order_id,
    pt.amount,
    pt.currency,
    pt.status,
    pt.customer_name,
    pt.customer_email,
    pt.created_at,
    pt.completed_at,
    COALESCE(pr.total_refund_amount, 0) as refunded_amount,
    pt.amount - COALESCE(pr.total_refund_amount, 0) as net_amount
FROM payment_transactions pt
LEFT JOIN (
    SELECT
        transaction_id,
        SUM(refund_amount) as total_refund_amount
    FROM payment_refunds
    WHERE status = 'COMPLETED'
    GROUP BY transaction_id
) pr ON pt.transaction_id = pr.transaction_id;

-- View for recent transactions
CREATE OR REPLACE VIEW recent_transactions AS
SELECT
    transaction_id,
    merchant_order_id,
    amount,
    status,
    customer_name,
    customer_email,
    created_at
FROM payment_transactions
ORDER BY created_at DESC
LIMIT 100;

-- ==========================================
-- SAMPLE DATA (OPTIONAL - FOR DEVELOPMENT)
-- ==========================================

-- Insert sample payment transaction (for development)
INSERT INTO payment_transactions (
    transaction_id,
    merchant_order_id,
    merchant_transaction_id,
    amount,
    currency,
    customer_id,
    customer_name,
    customer_email,
    customer_mobile,
    status,
    metadata
) VALUES (
    'TXN123456789',
    'MO123456789',
    'MT123456789',
    10000,  -- 100 INR in paise
    'INR',
    'CUST123',
    'John Doe',
    'john.doe@example.com',
    '9876543210',
    'COMPLETED',
    '{"source": "web", "device": "desktop"}'
) ON CONFLICT (transaction_id) DO NOTHING;

-- ==========================================
-- COMMENTS
-- ==========================================

COMMENT ON TABLE payment_transactions IS 'Stores all payment transactions processed through PhonePe';
COMMENT ON TABLE payment_refunds IS 'Stores refund information for payment transactions';
COMMENT ON TABLE payment_webhook_logs IS 'Logs all webhook callbacks received from PhonePe';
COMMENT ON TABLE payment_events_log IS 'Audit log for all payment-related events';

COMMENT ON COLUMN payment_transactions.amount IS 'Amount in paise (1 INR = 100 paise)';
COMMENT ON COLUMN payment_transactions.status IS 'Payment status: INITIATED, PENDING, COMPLETED, FAILED, REFUNDED, CANCELLED';
COMMENT ON COLUMN payment_refunds.refund_amount IS 'Refund amount in paise';
COMMENT ON COLUMN payment_refunds.status IS 'Refund status: PROCESSING, COMPLETED, FAILED';
