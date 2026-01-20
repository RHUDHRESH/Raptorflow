-- Fix RLS Policies for Billing Tables
-- Migration: 20260112_fix_rls_policies.sql

-- 1. Subscriptions: Allow INSERT and UPDATE for own rows
CREATE POLICY "Users can create own subscription" ON subscriptions
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own subscription" ON subscriptions
    FOR UPDATE USING (user_id = auth.uid());

-- 2. Payments: Allow INSERT for own rows (for creating payment intent)
CREATE POLICY "Users can create own payments" ON payments
    FOR INSERT WITH CHECK (user_id = auth.uid());
    
-- (Updates to payments usually happen via Webhook which uses Service Role, 
-- but we might allow users to update status in some edge cases? Better safe to keep it restricted for now)

-- 3. Ensure Plans are viewable (Already did this but enforcing)
DROP POLICY IF EXISTS "Public can view active plans" ON plans;
CREATE POLICY "Public can view active plans" ON plans FOR SELECT USING (is_active = true);
