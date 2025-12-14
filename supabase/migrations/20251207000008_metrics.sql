-- =====================================================
-- MIGRATION 008: Metrics (Analytics Warehouse Lite)
-- =====================================================

-- Metric definitions
CREATE TABLE public.metric_definitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  unit VARCHAR(50),
  aggregation VARCHAR(20) DEFAULT 'sum' CHECK (aggregation IN ('sum', 'avg', 'min', 'max', 'count')),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metrics (time-series data)
CREATE TABLE public.metrics (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  metric_id UUID NOT NULL REFERENCES public.metric_definitions(id),
  subject_type VARCHAR(100) NOT NULL,
  subject_id UUID,
  value DECIMAL(15,4) NOT NULL,
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  PRIMARY KEY (id, recorded_at)
) PARTITION BY RANGE (recorded_at);

CREATE TABLE public.metrics_2025_q1 PARTITION OF public.metrics FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE public.metrics_2025_q2 PARTITION OF public.metrics FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE public.metrics_default PARTITION OF public.metrics DEFAULT;

-- Indexes
CREATE INDEX idx_metrics_recorded ON public.metrics USING BRIN(recorded_at);
CREATE INDEX idx_metrics_org ON public.metrics(organization_id);
