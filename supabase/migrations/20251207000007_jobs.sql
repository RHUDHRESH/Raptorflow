-- =====================================================
-- MIGRATION 007: Background Jobs & Task Queue
-- =====================================================

-- Scheduled jobs
CREATE TABLE public.scheduled_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(200) NOT NULL,
  description TEXT,
  cron_expression VARCHAR(100) NOT NULL,
  timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
  job_type VARCHAR(100) NOT NULL,
  payload JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  last_run_at TIMESTAMPTZ,
  last_run_status job_status,
  next_run_at TIMESTAMPTZ,
  max_retries INTEGER DEFAULT 3,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job executions
CREATE TABLE public.job_executions (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  job_id UUID NOT NULL REFERENCES public.scheduled_jobs(id) ON DELETE CASCADE,
  status job_status NOT NULL DEFAULT 'pending',
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  result JSONB,
  error_message TEXT,
  attempt_number INTEGER DEFAULT 1,
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE public.job_executions_2025_q1 PARTITION OF public.job_executions FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE public.job_executions_default PARTITION OF public.job_executions DEFAULT;

-- Task queue
CREATE TABLE public.task_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_type VARCHAR(200) NOT NULL,
  payload JSONB NOT NULL,
  priority INTEGER DEFAULT 0,
  scheduled_for TIMESTAMPTZ DEFAULT NOW(),
  status job_status DEFAULT 'pending',
  locked_by VARCHAR(200),
  locked_at TIMESTAMPTZ,
  attempts INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 3,
  next_retry_at TIMESTAMPTZ,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_task_queue_pending ON public.task_queue(scheduled_for, priority DESC) WHERE status = 'pending';
