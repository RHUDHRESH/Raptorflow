# RAPTORFLOW DATABASE SCHEMA

Generated: 2026-01-23T04:52:44.885Z

## Tables

### ;

| Column | Type | Notes |
|--------|------|-------|
| CREATE | TABLE |  |
| id | UUID |  |
| email | TEXT |  |
| full_name | TEXT |  |
| avatar_url | TEXT |  |
| ucid | TEXT |  |
| role | TEXT |  |
| onboarding_status | TEXT |  |
| subscription_plan | TEXT |  |
| subscription_status | TEXT |  |
| workspace_preferences | JSONB |  |
| created_at | TIMESTAMPTZ |  |
| updated_at | TIMESTAMPTZ |  |

### ;

| Column | Type | Notes |
|--------|------|-------|
| CREATE | TABLE |  |
| id | UUID |  |
| user_id | UUID |  |
| plan_id | TEXT |  |
| status | TEXT |  |
| current_period_start | TIMESTAMPTZ |  |
| current_period_end | TIMESTAMPTZ |  |
| cancel_at_period_end | BOOLEAN |  |
| phonepe_subscription_id | TEXT |  |
| For | future |  |
| created_at | TIMESTAMPTZ |  |
| updated_at | TIMESTAMPTZ |  |

### ;

| Column | Type | Notes |
|--------|------|-------|
| CREATE | TABLE |  |
| id | UUID |  |
| user_id | UUID |  |
| transaction_id | TEXT |  |
| PhonePe | Merchant |  |
| phonepe_transaction_id | TEXT |  |
| PhonePe | Gateway |  |
| amount | INTEGER |  |
| In | Paise |  |
| currency | TEXT |  |
| status | TEXT |  |
| plan_id | TEXT |  |
| invoice_url | TEXT |  |
| metadata | JSONB |  |
| created_at | TIMESTAMPTZ |  |
| verified_at | TIMESTAMPTZ |  |

### ;

| Column | Type | Notes |
|--------|------|-------|
| CREATE | TABLE |  |
| id | UUID |  |
| user_id | UUID |  |
| email_type | TEXT |  |
| recipient_email | TEXT |  |
| resend_id | TEXT |  |
| ID | from |  |
| status | TEXT |  |
| metadata | JSONB |  |
| created_at | TIMESTAMPTZ |  |

### ;

| Column | Type | Notes |
|--------|------|-------|
| CREATE | TABLE |  |
| id | UUID |  |
| owner_id | UUID |  |
| name | TEXT |  |
| settings | JSONB |  |
| created_at | TIMESTAMPTZ |  |
| updated_at | TIMESTAMPTZ |  |

