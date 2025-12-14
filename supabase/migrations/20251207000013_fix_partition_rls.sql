-- =====================================================
-- MIGRATION 013: Enable RLS on Partitioned Tables
-- =====================================================

-- PostgreSQL partitions do NOT inherit RLS from parent tables
-- We must explicitly enable RLS on each partition

-- Audit Logs Partitions
ALTER TABLE public.audit_logs_2025_q1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs_2025_q2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs_2025_q3 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs_2025_q4 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs_default ENABLE ROW LEVEL SECURITY;

-- Activity Events Partitions
ALTER TABLE public.activity_events_2025_q1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_events_2025_q2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_events_default ENABLE ROW LEVEL SECURITY;

-- Job Executions Partitions
ALTER TABLE public.job_executions_2025_q1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_executions_default ENABLE ROW LEVEL SECURITY;

-- Metrics Partitions
ALTER TABLE public.metrics_2025_q1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metrics_2025_q2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metrics_default ENABLE ROW LEVEL SECURITY;
