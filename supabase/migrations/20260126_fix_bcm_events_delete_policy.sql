-- Fix BCM Evolution Engine - Add Delete Policy for Sweeper
-- Migration: 20260126_fix_bcm_events_delete_policy.sql

-- Enable deletion for authenticated users who are members of the workspace
-- This is required for BCMSweeper to clean up old events after compression
DROP POLICY IF EXISTS "bcm_events_delete_isolation" ON public.bcm_events;
CREATE POLICY "bcm_events_delete_isolation" ON public.bcm_events
    FOR DELETE USING (check_membership(workspace_id));

-- Ensure RLS is enabled (should already be)
ALTER TABLE public.bcm_events ENABLE ROW LEVEL SECURITY;
