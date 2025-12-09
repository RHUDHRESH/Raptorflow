-- =====================================================
-- MIGRATION 006: Audit & Activity Logs (Partitioned)
-- =====================================================

-- Audit logs
CREATE TABLE public.audit_logs (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  action audit_action NOT NULL,
  resource_type VARCHAR(100) NOT NULL,
  resource_id UUID,
  description TEXT,
  old_values JSONB,
  new_values JSONB,
  ip_address INET,
  user_agent TEXT,
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE public.audit_logs_2025_q1 PARTITION OF public.audit_logs FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE public.audit_logs_2025_q2 PARTITION OF public.audit_logs FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE public.audit_logs_2025_q3 PARTITION OF public.audit_logs FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE public.audit_logs_2025_q4 PARTITION OF public.audit_logs FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE public.audit_logs_default PARTITION OF public.audit_logs DEFAULT;

-- Activity events
CREATE TABLE public.activity_events (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  session_id UUID,
  event_name VARCHAR(200) NOT NULL,
  event_category VARCHAR(100),
  entity_type VARCHAR(100),
  entity_id UUID,
  properties JSONB DEFAULT '{}',
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE TABLE public.activity_events_2025_q1 PARTITION OF public.activity_events FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE public.activity_events_2025_q2 PARTITION OF public.activity_events FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE public.activity_events_default PARTITION OF public.activity_events DEFAULT;

-- Indexes (BRIN for time-series)
CREATE INDEX idx_audit_created ON public.audit_logs USING BRIN(created_at);
CREATE INDEX idx_audit_org ON public.audit_logs(organization_id);
CREATE INDEX idx_activity_occurred ON public.activity_events USING BRIN(occurred_at);
CREATE INDEX idx_activity_user ON public.activity_events(user_id);
