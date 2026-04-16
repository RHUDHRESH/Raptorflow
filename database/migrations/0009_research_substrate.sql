-- Block 1.5: Research substrate for grounded web intelligence
-- Raw fetch/provenance/chunk/vector pipeline (separate from downstream intel tables)

CREATE SCHEMA IF NOT EXISTS research;

-- ============================================================================
-- research_sources: tracked web sources for an org
-- ============================================================================
CREATE TABLE research.research_sources (
    source_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    source_type text NOT NULL CHECK (source_type IN ('targeted_domain', 'serp_discovery', 'competitor', 'manual')),
    display_name text NOT NULL,
    base_url text NOT NULL,
    domain text NOT NULL,
    config_json jsonb NOT NULL DEFAULT '{}',
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, domain)
);

ALTER TABLE research.research_sources ENABLE ROW LEVEL SECURITY;
CREATE POLICY research_sources_tenant ON research.research_sources
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

-- ============================================================================
-- research_runs: a single research session/request
-- ============================================================================
CREATE TABLE research.research_runs (
    run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    request_id text NOT NULL,
    parent_session_id uuid,
    parent_agent_id text,
    request_kind text NOT NULL CHECK (request_kind IN ('web_search', 'browser', 'competitive_analysis', 'performance_analysis', 'content_research')),
    query text NOT NULL,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'partial')),
    summary_json jsonb,
    cache_hit boolean NOT NULL DEFAULT false,
    urls_discovered integer NOT NULL DEFAULT 0,
    urls_fetched integer NOT NULL DEFAULT 0,
    urls_failed integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz,
    error_message text
);

ALTER TABLE research.research_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY research_runs_tenant ON research.research_runs
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

CREATE INDEX research_runs_org_created_idx ON research.research_runs (org_id, created_at DESC);
CREATE INDEX research_runs_status_idx ON research.research_runs (org_id, status);

-- ============================================================================
-- research_documents: individual fetched documents with provenance
-- ============================================================================
CREATE TABLE research.research_documents (
    document_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    source_id uuid REFERENCES research.research_sources(source_id) ON DELETE SET NULL,
    discovered_via_run_id uuid REFERENCES research.research_runs(run_id) ON DELETE SET NULL,
    url text NOT NULL,
    canonical_url text,
    domain text NOT NULL,
    title text,
    content_type text,
    language text,
    http_status integer,
    fetch_mode text NOT NULL CHECK (fetch_mode IN ('direct', 'browser', 'cached')),
    fetch_error text,
    robots_policy text CHECK (robots_policy IN ('allowed', 'disallowed', 'unknown')),
    fetched_at timestamptz NOT NULL DEFAULT now(),
    raw_object_key text,
    cleaned_text text,
    content_hash text,
    simhash bigint,
    metadata_json jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE research.research_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY research_documents_tenant ON research.research_documents
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

CREATE INDEX research_documents_org_domain_idx ON research.research_documents (org_id, domain);
CREATE INDEX research_documents_org_created_idx ON research.research_documents (org_id, created_at DESC);
CREATE INDEX research_documents_content_hash_idx ON research.research_documents (org_id, content_hash);
CREATE INDEX research_documents_url_idx ON research.research_documents (org_id, url);

-- ============================================================================
-- research_chunks: chunked content ready for embedding
-- ============================================================================
CREATE TABLE research.research_chunks (
    chunk_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    document_id uuid NOT NULL REFERENCES research.research_documents(document_id) ON DELETE CASCADE,
    chunk_index integer NOT NULL,
    token_estimate integer NOT NULL DEFAULT 0,
    content text NOT NULL,
    content_hash text NOT NULL,
    embedding_state text NOT NULL DEFAULT 'pending' CHECK (embedding_state IN ('pending', 'embedded', 'failed')),
    qdrant_point_id text,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE research.research_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY research_chunks_tenant ON research.research_chunks
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

CREATE INDEX research_chunks_org_doc_idx ON research.research_chunks (org_id, document_id);
CREATE INDEX research_chunks_embedding_state_idx ON research.research_chunks (org_id, embedding_state);

-- ============================================================================
-- research_citations: retrieved results linking runs to chunks with relevance
-- ============================================================================
CREATE TABLE research.research_citations (
    citation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    run_id uuid NOT NULL REFERENCES research.research_runs(run_id) ON DELETE CASCADE,
    document_id uuid NOT NULL REFERENCES research.research_documents(document_id) ON DELETE CASCADE,
    chunk_id uuid REFERENCES research.research_chunks(chunk_id) ON DELETE SET NULL,
    rank integer NOT NULL DEFAULT 0,
    snippet text NOT NULL,
    relevance_score double precision NOT NULL DEFAULT 0.0,
    source_domain text NOT NULL,
    source_url text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE research.research_citations ENABLE ROW LEVEL SECURITY;
CREATE POLICY research_citations_tenant ON research.research_citations
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

CREATE INDEX research_citations_run_idx ON research.research_citations (org_id, run_id);
CREATE INDEX research_citations_rank_idx ON research.research_citations (org_id, run_id, rank);

-- ============================================================================
-- Audit log extension for fetch events
-- ============================================================================
CREATE TABLE research.research_audit_log (
    audit_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    run_id uuid,
    document_id uuid,
    actor_id text,
    event_type text NOT NULL,
    domain text,
    url text,
    event_data jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE research.research_audit_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY research_audit_log_tenant ON research.research_audit_log
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

CREATE INDEX research_audit_log_org_created_idx ON research.research_audit_log (org_id, created_at DESC);

-- ============================================================================
-- Per-domain rate limiting tracking
-- ============================================================================
CREATE TABLE research.domain_rate_limits (
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    domain text NOT NULL,
    requests_count integer NOT NULL DEFAULT 0,
    window_start timestamptz NOT NULL DEFAULT now(),
    last_request_at timestamptz NOT NULL DEFAULT now(),
    blocked_until timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (org_id, domain)
);

ALTER TABLE research.domain_rate_limits ENABLE ROW LEVEL SECURITY;
CREATE POLICY domain_rate_limits_tenant ON research.domain_rate_limits
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

-- Per-org run budget tracking
CREATE TABLE research.org_run_budgets (
    org_id uuid PRIMARY KEY REFERENCES organizations(org_id) ON DELETE CASCADE,
    total_runs_this_month integer NOT NULL DEFAULT 0,
    total_fetches_this_month integer NOT NULL DEFAULT 0,
    month_start timestamptz NOT NULL DEFAULT date_trunc('month', now()),
    max_runs_per_month integer NOT NULL DEFAULT 1000,
    max_fetches_per_month integer NOT NULL DEFAULT 50000,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE research.org_run_budgets ENABLE ROW LEVEL SECURITY;
CREATE POLICY org_run_budgets_tenant ON research.org_run_budgets
    USING (org_id = app.current_org_id()) WITH CHECK (org_id = app.current_org_id());

CREATE INDEX domain_rate_limits_last_request_idx ON research.domain_rate_limits (org_id, last_request_at DESC);
CREATE INDEX org_run_budgets_month_start_idx ON research.org_run_budgets (month_start DESC);
