# 🔧 SQL PARAMETER DEFAULT FIX

## ❌ **Error Fixed:**
```
ERROR: 42P13: input parameters after one with a default value must also have defaults
```

## ✅ **Solution Applied:**
Changed function signature from:
```sql
-- ❌ BROKEN - Default value in middle
CREATE OR REPLACE FUNCTION public.create_user_subscription(
    p_user_id UUID,
    p_plan_slug VARCHAR(50),
    p_billing_cycle VARCHAR(10) DEFAULT 'monthly',  -- ❌ Default here
    p_phonepe_order_id VARCHAR(100),               -- ❌ No default after default
    p_amount_paid INTEGER                          -- ❌ No default after default
)
```

To:
```sql
-- ✅ FIXED - Default only on last optional parameter
CREATE OR REPLACE FUNCTION public.create_user_subscription(
    p_user_id UUID,
    p_plan_slug VARCHAR(50),
    p_billing_cycle VARCHAR(10),                  -- ✅ No default
    p_phonepe_order_id VARCHAR(100) DEFAULT NULL,  -- ✅ Default on last optional
    p_amount_paid INTEGER                          -- ✅ Required parameter
)
```

## 🎯 **PostgreSQL Rule:**
All parameters after one with a default value must also have defaults. The default must be on the last optional parameter(s).

## 📋 **Updated Files:**
- ✅ `supabase/apply_subscription_fix.sql`
- ✅ `supabase/migrations/20260125_fix_subscription_function.sql`

## 🚀 **Ready to Run:**
The SQL script is now ready to run in Supabase SQL Editor without the parameter default error.
