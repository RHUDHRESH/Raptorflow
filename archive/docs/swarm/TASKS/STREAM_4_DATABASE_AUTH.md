# STREAM 4: DATABASE & AUTH (100 Prompts)

> **INSTRUCTIONS**: Copy each prompt to your AI assistant. Each is self-contained.
> **CONTEXT**: Reference `DOCUMENTATION/SWARM/IMPLEMENTATION/05_AUTHENTICATION.md` and `06_DATABASE_SCHEMA.md`

---

## PROMPTS 1-25: Core Database Schema

### PROMPT 1
```
Create supabase/migrations/20240101_users_workspaces.sql: Table users (id UUID PK DEFAULT auth.uid(), email TEXT UNIQUE NOT NULL, full_name TEXT, avatar_url TEXT, subscription_tier TEXT DEFAULT 'free' CHECK IN ('free','starter','pro','enterprise'), created_at, updated_at). Table workspaces (id UUID PK, user_id UUID FK users ON DELETE CASCADE, name TEXT NOT NULL, slug TEXT UNIQUE, settings JSONB DEFAULT '{}', created_at, updated_at). RLS enabled on both.
```

### PROMPT 2
```
Create supabase/migrations/20240101_users_rls.sql: RLS policies for users table. "Users can view own profile" SELECT WHERE id = auth.uid(). "Users can update own profile" UPDATE WHERE id = auth.uid(). No INSERT policy (handled by trigger).
```

### PROMPT 3
```
Create supabase/migrations/20240101_workspaces_rls.sql: RLS policies for workspaces. "Users can view own workspaces" SELECT WHERE user_id = auth.uid(). "Users can create workspaces" INSERT WITH CHECK user_id = auth.uid(). "Users can update own workspaces" UPDATE WHERE user_id = auth.uid(). "Users can delete own workspaces" DELETE WHERE user_id = auth.uid().
```

### PROMPT 4
```
Create supabase/migrations/20240102_foundations.sql: Table foundations (id UUID PK, workspace_id UUID FK workspaces ON DELETE CASCADE UNIQUE, company_name TEXT, mission TEXT, vision TEXT, values JSONB DEFAULT '[]', industry TEXT, target_market TEXT, positioning TEXT, brand_voice TEXT, messaging_guardrails JSONB DEFAULT '[]', summary TEXT, created_at, updated_at). Index on workspace_id. RLS enabled.
```

### PROMPT 5
```
Create supabase/migrations/20240102_foundations_rls.sql: RLS for foundations. Policy checks workspace_id IN (SELECT id FROM workspaces WHERE user_id = auth.uid()). Apply to SELECT, INSERT, UPDATE, DELETE.
```

### PROMPT 6
```
Create supabase/migrations/20240103_icp_profiles.sql: Table icp_profiles (id UUID PK, workspace_id UUID FK workspaces ON DELETE CASCADE, name TEXT NOT NULL, tagline TEXT, market_sophistication INT CHECK 1-5, demographics JSONB, psychographics JSONB, behaviors JSONB, pain_points JSONB DEFAULT '[]', goals JSONB DEFAULT '[]', fit_score INT CHECK 0-100, summary TEXT, is_primary BOOLEAN DEFAULT false, created_at, updated_at). Index on (workspace_id, is_primary).
```

### PROMPT 7
```
Create supabase/migrations/20240103_icp_rls.sql: RLS for icp_profiles using workspace ownership check. Same pattern as foundations.
```

### PROMPT 8
```
Create supabase/migrations/20240104_moves.sql: Table moves (id UUID PK, workspace_id UUID FK, campaign_id UUID FK campaigns NULL, name TEXT NOT NULL, category TEXT CHECK IN ('ignite','capture','authority','repair','rally'), goal TEXT, target_icp_id UUID FK icp_profiles, strategy JSONB, execution_plan JSONB DEFAULT '[]', status TEXT DEFAULT 'draft' CHECK IN ('draft','active','paused','completed','archived'), duration_days INT, started_at, completed_at, success_metrics JSONB DEFAULT '[]', results JSONB, created_at, updated_at). Indexes.
```

### PROMPT 9
```
Create supabase/migrations/20240104_moves_rls.sql: RLS for moves table. Workspace ownership check pattern.
```

### PROMPT 10
```
Create supabase/migrations/20240105_campaigns.sql: Table campaigns (id UUID PK, workspace_id UUID FK, name TEXT NOT NULL, description TEXT, target_icps JSONB DEFAULT '[]', phases JSONB DEFAULT '[]', budget_usd DECIMAL(10,2), status TEXT DEFAULT 'planning', started_at, ended_at, success_metrics JSONB, results JSONB, created_at, updated_at). RLS enabled.
```

### PROMPT 11
```
Create supabase/migrations/20240106_muse_assets.sql: Table muse_assets (id UUID PK, workspace_id UUID FK, asset_type TEXT CHECK IN ('email','social_post','blog','ad_copy','headline','script','carousel'), title TEXT, content TEXT NOT NULL, content_html TEXT, metadata JSONB DEFAULT '{}', target_icp_id UUID FK, move_id UUID FK NULL, status TEXT DEFAULT 'draft', quality_score INT, created_at, updated_at). Indexes on workspace_id, asset_type.
```

### PROMPT 12
```
Create supabase/migrations/20240107_blackbox_strategies.sql: Table blackbox_strategies (id UUID PK, workspace_id UUID FK, name TEXT NOT NULL, focus_area TEXT CHECK IN ('acquisition','retention','revenue','brand_equity','virality'), risk_level INT CHECK 1-10, risk_reasons JSONB DEFAULT '[]', phases JSONB DEFAULT '[]', expected_upside TEXT, potential_downside TEXT, status TEXT DEFAULT 'proposed', accepted_at, converted_move_id UUID FK moves NULL, created_at). RLS enabled.
```

### PROMPT 13
```
Create supabase/migrations/20240108_daily_wins.sql: Table daily_wins (id UUID PK, workspace_id UUID FK, win_date DATE NOT NULL, topic TEXT NOT NULL, angle TEXT, hook TEXT, outline TEXT, platform TEXT, estimated_minutes INT, trend_source TEXT, relevance_score INT, status TEXT DEFAULT 'idea', posted_at, expanded_content_id UUID FK muse_assets NULL, created_at). Index on (workspace_id, win_date).
```

### PROMPT 14
```
Create supabase/migrations/20240109_agent_executions.sql: Table agent_executions (id UUID PK, workspace_id UUID FK, user_id UUID FK, session_id UUID NOT NULL, agent_name TEXT NOT NULL, input JSONB, output JSONB, status TEXT DEFAULT 'running', tokens_used INT DEFAULT 0, cost_usd DECIMAL(10,6) DEFAULT 0, started_at DEFAULT NOW(), completed_at, error TEXT). Index on (workspace_id, session_id).
```

### PROMPT 15
```
Create supabase/migrations/20240110_onboarding_sessions.sql: Table onboarding_sessions (id UUID PK, workspace_id UUID FK UNIQUE, current_step INT DEFAULT 1, completed_steps JSONB DEFAULT '[]', step_data JSONB DEFAULT '{}', evidence_items JSONB DEFAULT '[]', extracted_facts JSONB DEFAULT '[]', status TEXT DEFAULT 'in_progress', started_at DEFAULT NOW(), completed_at). RLS enabled.
```

### PROMPT 16
```
Create supabase/migrations/20240111_evidence_vault.sql: Table evidence_vault (id UUID PK, workspace_id UUID FK, session_id UUID FK onboarding_sessions, source_type TEXT CHECK IN ('file','url'), source_name TEXT NOT NULL, file_path TEXT, url TEXT, content TEXT, content_type TEXT, word_count INT, key_topics JSONB DEFAULT '[]', processing_status TEXT DEFAULT 'pending', processed_at, created_at). Indexes.
```

### PROMPT 17
```
Create supabase/migrations/20240112_research_findings.sql: Table research_findings (id UUID PK, workspace_id UUID FK, research_type TEXT CHECK IN ('market','competitor','customer','trend'), query TEXT, sources JSONB DEFAULT '[]', findings JSONB DEFAULT '[]', summary TEXT, confidence_score INT, created_at). For storing research agent outputs.
```

### PROMPT 18
```
Create supabase/migrations/20240113_competitor_profiles.sql: Table competitor_profiles (id UUID PK, workspace_id UUID FK, name TEXT NOT NULL, website TEXT, positioning TEXT, strengths JSONB DEFAULT '[]', weaknesses JSONB DEFAULT '[]', content_strategy JSONB, last_analyzed_at, created_at, updated_at). Track competitor intelligence.
```

### PROMPT 19
```
Create supabase/migrations/20240114_feedback.sql: Table user_feedback (id UUID PK, workspace_id UUID FK, user_id UUID FK, output_type TEXT, output_id UUID, rating INT CHECK 1-5, comments TEXT, corrections TEXT, applied BOOLEAN DEFAULT false, created_at). For learning from user feedback.
```

### PROMPT 20
```
Create supabase/migrations/20240115_billing.sql: Tables: subscriptions (id, workspace_id, plan, status, current_period_start, current_period_end, cancel_at), usage_records (id, workspace_id, period_start, period_end, tokens_used, cost_usd, agent_breakdown JSONB), invoices (id, workspace_id, amount, status, paid_at, invoice_url). RLS on all.
```

### PROMPT 21
```
Create supabase/migrations/20240116_indexes.sql: Create additional indexes for performance. Composite indexes on (workspace_id, created_at DESC) for pagination. Partial indexes for status filters. GIN indexes on JSONB columns.
```

### PROMPT 22
```
Create supabase/migrations/20240117_functions.sql: Helper functions. get_workspace_id() returns first workspace for auth.uid(). is_workspace_owner(workspace_id) checks ownership. increment_usage(workspace_id, tokens) updates usage.
```

### PROMPT 23
```
Create supabase/migrations/20240118_triggers.sql: Triggers. on_auth_user_created() creates user profile and default workspace. on_foundation_update() updates summary. update_updated_at() on all tables.
```

### PROMPT 24
```
Create supabase/migrations/20240119_views.sql: Views. workspace_summary (foundation + ICPs + recent moves). usage_summary (current period usage). agent_performance (avg tokens, cost, success rate by agent).
```

### PROMPT 25
```
Create supabase/migrations/20240120_seed.sql: Seed data for development. Creates test user, workspace, sample foundation, 2 ICPs, sample moves. Wrapped in transaction. Only runs in dev.
```

---

## PROMPTS 26-50: Authentication System

### PROMPT 26
```
Create backend/core/__init__.py exporting: get_current_user, get_workspace_id, AuthMiddleware, SupabaseClient.
```

### PROMPT 27
```
Create backend/core/supabase.py: SupabaseClient singleton. __init__ creates client from config. get_client() -> Client. get_admin_client() with service role key. Connection pooling.
```

### PROMPT 28
```
Create backend/core/auth.py: get_current_user(request: Request, authorization: str = Header()) -> User. Extracts JWT from header, verifies with Supabase, returns user. Raises 401 on invalid.
```

### PROMPT 29
```
Create backend/core/models.py: @dataclass User with id, email, full_name, subscription_tier. @dataclass Workspace with id, user_id, name, slug, settings. @dataclass AuthContext with user, workspace_id, permissions.
```

### PROMPT 30
```
Create backend/core/workspace.py: get_workspace_id(user: User = Depends(get_current_user), workspace_id: str = Header(None)) -> str. Gets workspace from header or user's default. Validates ownership.
```

### PROMPT 31
```
Create backend/core/middleware.py: AuthMiddleware(BaseHTTPMiddleware). async dispatch extracts auth, attaches user to request.state. Allows public endpoints. Logs auth events.
```

### PROMPT 32
```
Create backend/core/permissions.py: Permission enum (READ, WRITE, DELETE, ADMIN). check_permission(user, workspace_id, permission) -> bool. For future role-based access.
```

### PROMPT 33
```
Create backend/core/session.py: SessionManager. async create_session(user_id, workspace_id) -> session_id. async validate_session(session_id) -> Session. async invalidate_session(session_id). Redis-backed.
```

### PROMPT 34
```
Create backend/core/jwt.py: JWTValidator. verify_token(token: str) -> JWTPayload. decode_token(token: str) -> dict. validate_claims(payload: dict) -> bool. Handles Supabase JWT format.
```

### PROMPT 35
```
Create backend/core/rate_limiting.py: RateLimiter. async check_rate_limit(user_id, endpoint) -> RateLimitResult with allowed, remaining, reset_at. Config per endpoint. Redis-backed.
```

### PROMPT 36
```
Create backend/core/api_keys.py: APIKeyManager. async create_api_key(workspace_id, name) -> key. async validate_api_key(key) -> APIKeyInfo. async revoke_api_key(key_id). For programmatic access.
```

### PROMPT 37
```
Create supabase/migrations/20240121_api_keys.sql: Table api_keys (id UUID PK, workspace_id UUID FK, key_hash TEXT NOT NULL, name TEXT, permissions JSONB, last_used_at, expires_at, created_at). Never store raw keys.
```

### PROMPT 38
```
Create backend/core/audit.py: AuditLogger. async log_action(user_id, workspace_id, action, resource_type, resource_id, details). Writes to audit_logs table. For compliance.
```

### PROMPT 39
```
Create supabase/migrations/20240122_audit_logs.sql: Table audit_logs (id UUID PK, workspace_id UUID FK, user_id UUID, action TEXT, resource_type TEXT, resource_id UUID, details JSONB, ip_address TEXT, user_agent TEXT, created_at). Index on (workspace_id, created_at).
```

### PROMPT 40
```
Create backend/core/security.py: sanitize_input(text: str) -> str removes XSS. validate_email(email: str) -> bool. hash_api_key(key: str) -> str. Security utilities.
```

### PROMPT 41
```
Create backend/core/cors.py: Configure CORS middleware. Allowed origins from config. Allowed methods, headers. Credentials support. For frontend integration.
```

### PROMPT 42
```
Create backend/core/errors.py: Custom HTTP exceptions. AuthenticationError(401), AuthorizationError(403), NotFoundError(404), ValidationError(422), RateLimitError(429). Consistent error responses.
```

### PROMPT 43
```
Create backend/api/v1/auth.py: POST /auth/signup (disabled, use Supabase directly). POST /auth/login returns session. POST /auth/logout invalidates session. POST /auth/refresh refreshes token. GET /auth/me returns current user.
```

### PROMPT 44
```
Create backend/api/v1/workspaces.py: GET /workspaces lists user's workspaces. POST /workspaces creates new. GET /workspaces/{id} details. PUT /workspaces/{id} update. DELETE /workspaces/{id} delete. GET /workspaces/{id}/settings.
```

### PROMPT 45
```
Create backend/api/v1/users.py: GET /users/me profile. PUT /users/me update profile. DELETE /users/me delete account. GET /users/me/usage current usage. GET /users/me/billing billing info.
```

---

## PROMPTS 46-70: Database Access Layer

### PROMPT 46
```
Create backend/db/__init__.py exporting: Database, Repository base classes, all repository implementations.
```

### PROMPT 47
```
Create backend/db/base.py: Repository base class. __init__(supabase: Client). async get(id) -> Model | None. async list(workspace_id, filters, pagination) -> List[Model]. async create(data) -> Model. async update(id, data) -> Model. async delete(id) -> bool.
```

### PROMPT 48
```
Create backend/db/pagination.py: @dataclass Pagination with page, page_size, sort_by, sort_order. @dataclass PaginatedResult with items, total, page, page_size, total_pages. Helper functions.
```

### PROMPT 49
```
Create backend/db/filters.py: @dataclass Filter with field, operator (eq, neq, gt, gte, lt, lte, like, in), value. build_query(query, filters: List[Filter]) applies filters to Supabase query.
```

### PROMPT 50
```
Create backend/db/foundations.py: FoundationRepository(Repository). async get_by_workspace(workspace_id). async upsert(workspace_id, data). Specific methods for foundation CRUD.
```

### PROMPT 51
```
Create backend/db/icps.py: ICPRepository(Repository). async list_by_workspace(workspace_id). async get_primary(workspace_id). async set_primary(workspace_id, icp_id). async count_by_workspace(workspace_id).
```

### PROMPT 52
```
Create backend/db/moves.py: MoveRepository(Repository). async list_by_campaign(campaign_id). async list_active(workspace_id). async update_status(move_id, status). async get_with_tasks(move_id).
```

### PROMPT 53
```
Create backend/db/campaigns.py: CampaignRepository(Repository). async get_with_moves(campaign_id). async update_status(campaign_id, status). async calculate_results(campaign_id).
```

### PROMPT 54
```
Create backend/db/muse_assets.py: MuseAssetRepository(Repository). async list_by_type(workspace_id, asset_type). async list_by_move(move_id). async search(workspace_id, query).
```

### PROMPT 55
```
Create backend/db/blackbox.py: BlackboxRepository(Repository). async accept_strategy(strategy_id) creates move from strategy. async list_pending(workspace_id).
```

### PROMPT 56
```
Create backend/db/daily_wins.py: DailyWinsRepository(Repository). async get_today(workspace_id). async list_by_date_range(workspace_id, start, end). async mark_posted(win_id).
```

### PROMPT 57
```
Create backend/db/agent_executions.py: AgentExecutionRepository(Repository). async create_execution(workspace_id, user_id, session_id, agent_name, input). async complete_execution(execution_id, output, tokens, cost). async get_by_session(session_id).
```

### PROMPT 58
```
Create backend/db/onboarding.py: OnboardingRepository(Repository). async get_or_create(workspace_id). async update_step(workspace_id, step, step_data). async complete_step(workspace_id, step). async get_evidence(workspace_id).
```

### PROMPT 59
```
Create backend/db/evidence.py: EvidenceRepository(Repository). async add_evidence(workspace_id, session_id, source_type, source_name, content). async mark_processed(evidence_id, topics). async list_pending(workspace_id).
```

### PROMPT 60
```
Create backend/db/research.py: ResearchRepository(Repository). async save_findings(workspace_id, research_type, findings). async search_findings(workspace_id, query). async get_recent(workspace_id, limit).
```

### PROMPT 61
```
Create backend/db/competitors.py: CompetitorRepository(Repository). async upsert_competitor(workspace_id, name, data). async list_competitors(workspace_id). async update_analysis(competitor_id, analysis).
```

### PROMPT 62
```
Create backend/db/feedback.py: FeedbackRepository(Repository). async save_feedback(workspace_id, user_id, output_type, output_id, rating, comments). async list_feedback(workspace_id). async apply_feedback(feedback_id).
```

### PROMPT 63
```
Create backend/db/billing.py: BillingRepository. async get_subscription(workspace_id). async update_subscription(workspace_id, plan). async record_usage(workspace_id, tokens, cost). async get_usage_summary(workspace_id, period).
```

### PROMPT 64
```
Create backend/db/transactions.py: TransactionManager. async begin() -> Transaction. async commit(transaction). async rollback(transaction). Context manager for atomic operations.
```

### PROMPT 65
```
Create backend/db/migrations.py: MigrationRunner. async run_migrations(). async rollback_migration(version). async get_current_version(). For programmatic migration management.
```

---

## PROMPTS 66-85: Data Services

### PROMPT 66
```
Create backend/services/__init__.py exporting: FoundationService, ICPService, MoveService, CampaignService, ContentService, OnboardingService, BillingService.
```

### PROMPT 67
```
Create backend/services/foundation.py: FoundationService. async get_foundation(workspace_id). async update_foundation(workspace_id, data). async generate_summary(workspace_id). Business logic layer.
```

### PROMPT 68
```
Create backend/services/icp.py: ICPService. async create_icp(workspace_id, data). async generate_from_foundation(workspace_id). async set_primary(workspace_id, icp_id). Validation and business rules.
```

### PROMPT 69
```
Create backend/services/move.py: MoveService. async create_move(workspace_id, data). async start_move(move_id). async pause_move(move_id). async complete_move(move_id). async generate_tasks(move_id).
```

### PROMPT 70
```
Create backend/services/campaign.py: CampaignService. async create_campaign(workspace_id, data). async add_move(campaign_id, move_id). async launch_campaign(campaign_id). async calculate_roi(campaign_id).
```

### PROMPT 71
```
Create backend/services/content.py: ContentService. async create_asset(workspace_id, data). async update_quality_score(asset_id, score). async list_assets_for_move(move_id). async export_asset(asset_id, format).
```

### PROMPT 72
```
Create backend/services/onboarding.py: OnboardingService. async advance_step(workspace_id). async save_step_data(workspace_id, step, data). async complete_onboarding(workspace_id). async reset_step(workspace_id, step).
```

### PROMPT 73
```
Create backend/services/research.py: ResearchService. async trigger_research(workspace_id, query). async get_research_summary(workspace_id). async invalidate_old_research(workspace_id, days).
```

### PROMPT 74
```
Create backend/services/billing.py: BillingService. async check_usage_limit(workspace_id). async record_usage(workspace_id, tokens, cost, agent). async get_invoice(workspace_id, period). async upgrade_plan(workspace_id, plan).
```

### PROMPT 75
```
Create backend/services/export.py: ExportService. async export_foundation(workspace_id, format). async export_icps(workspace_id, format). async export_content(workspace_id, filters, format). PDF, DOCX, JSON support.
```

### PROMPT 76
```
Create backend/services/import.py: ImportService. async import_foundation(workspace_id, data). async import_icps(workspace_id, data). Validate and merge with existing data.
```

### PROMPT 77
```
Create backend/services/cleanup.py: CleanupService. async cleanup_orphaned_data(workspace_id). async archive_old_content(workspace_id, days). async delete_workspace_data(workspace_id). Maintenance operations.
```

---

## PROMPTS 78-100: API Endpoints & Testing

### PROMPT 78
```
Create backend/api/v1/foundation.py: GET /foundation returns workspace foundation. PUT /foundation updates. POST /foundation/generate-summary triggers AI summary. GET /foundation/export/{format}.
```

### PROMPT 79
```
Create backend/api/v1/icps.py: GET /icps list. POST /icps create. GET /icps/{id}. PUT /icps/{id}. DELETE /icps/{id}. POST /icps/{id}/set-primary. POST /icps/generate-from-foundation.
```

### PROMPT 80
```
Create backend/api/v1/moves.py: CRUD endpoints. POST /moves/{id}/start. POST /moves/{id}/pause. POST /moves/{id}/complete. GET /moves/{id}/tasks. POST /moves/{id}/generate-tasks.
```

### PROMPT 81
```
Create backend/api/v1/campaigns.py: CRUD endpoints. GET /campaigns/{id}/moves. POST /campaigns/{id}/add-move. POST /campaigns/{id}/launch. GET /campaigns/{id}/results.
```

### PROMPT 82
```
Create backend/api/v1/muse.py: GET /muse/assets list. POST /muse/generate with type, topic, icp_id. GET /muse/assets/{id}. PUT /muse/assets/{id}. DELETE /muse/assets/{id}. GET /muse/templates.
```

### PROMPT 83
```
Create backend/api/v1/blackbox.py: POST /blackbox/generate creates strategy. GET /blackbox/strategies list. GET /blackbox/strategies/{id}. POST /blackbox/strategies/{id}/accept converts to move.
```

### PROMPT 84
```
Create backend/api/v1/daily_wins.py: POST /daily-wins/generate for today. GET /daily-wins list. GET /daily-wins/{id}. POST /daily-wins/{id}/expand. POST /daily-wins/{id}/mark-posted.
```

### PROMPT 85
```
Create backend/api/v1/onboarding.py: GET /onboarding status. POST /onboarding/step/{step} save step data. POST /onboarding/advance move to next step. POST /onboarding/evidence/upload. POST /onboarding/evidence/url.
```

### PROMPT 86
```
Create backend/api/v1/research.py: POST /research/trigger with query. GET /research/findings list. GET /research/findings/{id}. GET /research/competitors.
```

### PROMPT 87
```
Create tests/db/__init__.py and tests/db/conftest.py: Fixtures for database tests. test_supabase_client, test_workspace, test_user, sample_foundation, sample_icp.
```

### PROMPT 88
```
Create tests/db/test_repositories.py: Tests for all repositories. test_foundation_crud(), test_icp_crud(), test_move_crud(), test_workspace_isolation().
```

### PROMPT 89
```
Create tests/db/test_pagination.py: Tests for pagination. test_pagination_params(), test_paginated_results(), test_sorting().
```

### PROMPT 90
```
Create tests/db/test_filters.py: Tests for filtering. test_filter_operators(), test_multiple_filters(), test_jsonb_filters().
```

### PROMPT 91
```
Create tests/auth/test_authentication.py: Tests for auth. test_jwt_validation(), test_get_current_user(), test_invalid_token(), test_expired_token().
```

### PROMPT 92
```
Create tests/auth/test_authorization.py: Tests for authorization. test_workspace_ownership(), test_cross_workspace_access_denied(), test_permissions().
```

### PROMPT 93
```
Create tests/auth/test_rate_limiting.py: Tests for rate limiting. test_rate_limit_applied(), test_rate_limit_reset(), test_rate_limit_bypass_for_premium().
```

### PROMPT 94
```
Create tests/services/test_services.py: Tests for services. test_foundation_service(), test_icp_service(), test_move_service(), test_billing_service().
```

### PROMPT 95
```
Create tests/api/test_endpoints.py: Integration tests for API endpoints. test_foundation_endpoints(), test_icp_endpoints(), test_auth_required().
```

### PROMPT 96
```
Create backend/db/scripts/reset_db.py: Script to reset database. Drops all tables, runs migrations, seeds data. For development. Protected from production.
```

### PROMPT 97
```
Create backend/db/scripts/backup.py: Script to backup workspace data. Exports to JSON. Includes all related tables. For migration or recovery.
```

### PROMPT 98
```
Create backend/db/scripts/migrate_data.py: Script for data migrations between schema versions. Transforms data, validates, applies changes.
```

### PROMPT 99
```
Create backend/db/health.py: DatabaseHealthChecker. async check_connection(). async check_rls_enabled(). async check_indexes(). Returns health report.
```

### PROMPT 100
```
Create backend/db/README.md: Documentation for database layer. Schema overview, RLS policies explanation, repository usage, migration guide, performance tips.
```

---

## VERIFICATION

After all prompts completed, verify:
- [ ] All migrations run in Supabase
- [ ] RLS policies are active
- [ ] Auth middleware works
- [ ] API endpoints respond
- [ ] Workspace isolation enforced
- [ ] All tests pass
