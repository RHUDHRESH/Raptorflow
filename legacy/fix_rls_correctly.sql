-- Fix RLS Policies correctly (Fixing UUID mismatch)
-- Migration: 20260112_fix_rls_correctly.sql

-- Drop incorrect policies
DROP POLICY IF EXISTS "Users can create own subscription" ON subscriptions;
DROP POLICY IF EXISTS "Users can update own subscription" ON subscriptions;
DROP POLICY IF EXISTS "Users can create own payments" ON payments;

-- 1. Subscriptions: Allow INSERT and UPDATE for own public user ID
-- We must check if the user_id (public UUID) belongs to the auth user (auth UUID)
CREATE POLICY "Users can create own subscription" ON subscriptions
    FOR INSERT WITH CHECK (
        user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Users can update own subscription" ON subscriptions
    FOR UPDATE USING (
        user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
    );

-- 2. Payments: Allow INSERT for own rows
CREATE POLICY "Users can create own payments" ON payments
    FOR INSERT WITH CHECK (
         user_id IN (SELECT id FROM public.users WHERE auth_user_id = auth.uid())
    );
