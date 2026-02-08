# STREAM 6: INTEGRATION & DEPLOYMENT (100 Prompts)

> **INSTRUCTIONS**: Copy each prompt to your AI assistant. Each is self-contained.
> **CONTEXT**: This stream integrates all previous streams and prepares for production deployment.
> **NOTE**: Execute this stream AFTER completing Streams 1-5.

---

## PROMPTS 1-20: System Integration

### PROMPT 1
```
Create backend/main.py: FastAPI application entry point. Include all routers from api/v1/. Add CORS middleware. Add AuthMiddleware. Lifespan handler for startup/shutdown. Health endpoint at root.
```

### PROMPT 2
```
Create backend/startup.py: Startup sequence. async initialize() verifies Supabase connection, Redis connection, Vertex AI credentials. Warms up embedding models. Compiles LangGraph workflows. Initializes tool registry. Returns startup report.
```

### PROMPT 3
```
Create backend/shutdown.py: Shutdown sequence. async cleanup() closes database connections, flushes Redis writes, saves checkpoints, completes pending jobs gracefully. Logs shutdown summary.
```

### PROMPT 4
```
Create backend/dependencies.py: FastAPI dependencies. get_db() returns Supabase client. get_redis() returns Redis client. get_memory_controller() returns MemoryController. get_cognitive_engine() returns CognitiveEngine. Dependency injection.
```

### PROMPT 5
```
Create backend/middleware/__init__.py exporting: AuthMiddleware, LoggingMiddleware, ErrorMiddleware, MetricsMiddleware.
```

### PROMPT 6
```
Create backend/middleware/logging.py: LoggingMiddleware. Logs request method, path, status, latency. Adds request_id to all logs. Structured JSON format. Excludes health endpoints.
```

### PROMPT 7
```
Create backend/middleware/errors.py: ErrorMiddleware. Catches all exceptions. Formats error responses consistently. Logs errors with stack traces. Returns appropriate status codes.
```

### PROMPT 8
```
Create backend/middleware/metrics.py: MetricsMiddleware. Records request count, latency histogram, error rate. Exposes Prometheus metrics. Per-endpoint breakdown.
```

### PROMPT 9
```
Create backend/integration/__init__.py exporting: IntegrationManager, integration test functions.
```

### PROMPT 10
```
Create backend/integration/routing_memory.py: Integration between routing and memory. async route_with_memory_context(request, workspace_id) retrieves relevant memory before routing. Injects context into routing decision.
```

### PROMPT 11
```
Create backend/integration/agents_cognitive.py: Integration between agents and cognitive engine. async execute_with_cognition(agent, state) wraps agent execution with perception, planning, reflection. Full cognitive pipeline.
```

### PROMPT 12
```
Create backend/integration/memory_database.py: Integration between memory and database. async sync_database_to_memory(workspace_id) vectorizes database records. async invalidate_on_change(table, record_id) clears relevant vectors.
```

### PROMPT 13
```
Create backend/integration/auth_all.py: Auth integration across all modules. inject_auth_context(state, user, workspace_id) adds auth to agent state. verify_workspace_access(workspace_id, user) checks all operations.
```

### PROMPT 14
```
Create backend/integration/redis_sessions.py: Redis integration for agent sessions. async persist_agent_state(session_id, state) saves to Redis. async restore_agent_state(session_id) loads from Redis. Checkpoint/resume.
```

### PROMPT 15
```
Create backend/integration/events_all.py: Event bus integration. Wire all event handlers. Foundation updates → memory reindex. Content generated → analytics. Approval timeout → notification.
```

### PROMPT 16
```
Create backend/integration/billing_usage.py: Billing integration. Track all token usage. async deduct_from_budget(workspace_id, tokens, cost) before execution. async refund_on_failure(workspace_id, tokens, cost).
```

### PROMPT 17
```
Create backend/integration/validation.py: Cross-module validation. validate_workspace_consistency(workspace_id) checks foundation, ICPs, memory alignment. validate_agent_state(state) ensures required fields.
```

### PROMPT 18
```
Create backend/integration/context_builder.py: Unified context builder. async build_full_context(workspace_id, query) gathers from memory, database, session. Returns formatted context for agents.
```

### PROMPT 19
```
Create backend/integration/output_pipeline.py: Output processing pipeline. async process_output(output, workspace_id) runs quality check, stores in database, updates memory, triggers events.
```

### PROMPT 20
```
Create backend/integration/test_harness.py: Integration test harness. async run_integration_tests() tests all integrations. Returns detailed report. For CI/CD.
```

---

## PROMPTS 21-40: End-to-End Workflows

### PROMPT 21
```
Create backend/workflows/__init__.py exporting: OnboardingWorkflow, MoveWorkflow, ContentWorkflow, ResearchWorkflow.
```

### PROMPT 22
```
Create backend/workflows/onboarding.py: OnboardingWorkflow end-to-end. async execute_step(workspace_id, step, data) handles each step. Coordinates agents, memory, database. Returns next step.
```

### PROMPT 23
```
Create backend/workflows/move.py: MoveWorkflow end-to-end. async create_move(workspace_id, goal) plans move. async execute_move(move_id) runs tasks. async complete_move(move_id) finalizes.
```

### PROMPT 24
```
Create backend/workflows/content.py: ContentWorkflow end-to-end. async generate_content(workspace_id, request) routes to agent. async review_content(content_id) runs quality check. async publish_content(content_id).
```

### PROMPT 25
```
Create backend/workflows/research.py: ResearchWorkflow end-to-end. async conduct_research(workspace_id, query) orchestrates research agent. async store_findings(workspace_id, findings). async present_results(research_id).
```

### PROMPT 26
```
Create backend/workflows/blackbox.py: BlackboxWorkflow end-to-end. async generate_strategy(workspace_id) creates bold strategy. async review_strategy(strategy_id) checks risks. async convert_to_move(strategy_id).
```

### PROMPT 27
```
Create backend/workflows/daily_wins.py: DailyWinsWorkflow. async generate_today(workspace_id) creates wins. async expand_win(win_id) generates full content. async schedule_win(win_id, platform).
```

### PROMPT 28
```
Create backend/workflows/campaign.py: CampaignWorkflow. async plan_campaign(workspace_id, goal) creates campaign. async add_moves(campaign_id, moves). async launch_campaign(campaign_id). async report_results(campaign_id).
```

### PROMPT 29
```
Create backend/workflows/approval.py: ApprovalWorkflow. async submit_for_approval(output, risk_level) creates gate. async process_approval(gate_id, decision). async handle_timeout(gate_id).
```

### PROMPT 30
```
Create backend/workflows/feedback.py: FeedbackWorkflow. async collect_feedback(output_id) prompts user. async apply_feedback(feedback_id) improves output. async learn_from_feedback(workspace_id).
```

---

## PROMPTS 31-50: Testing Suite

### PROMPT 31
```
Create tests/__init__.py and tests/conftest.py: Global fixtures. test_app (TestClient), test_user, test_workspace, test_session, mock_llm, mock_redis, mock_supabase.
```

### PROMPT 32
```
Create tests/integration/__init__.py and tests/integration/conftest.py: Integration test fixtures. live_supabase (if env set), live_redis, real credentials for integration tests.
```

### PROMPT 33
```
Create tests/integration/test_routing_to_agents.py: Test routing → agent flow. test_request_routes_correctly(), test_agent_receives_intent(), test_response_returns_to_user().
```

### PROMPT 34
```
Create tests/integration/test_agent_to_memory.py: Test agent → memory flow. test_agent_retrieves_memory(), test_agent_stores_output(), test_memory_context_injection().
```

### PROMPT 35
```
Create tests/integration/test_cognitive_pipeline.py: Test full cognitive pipeline. test_perception_to_output(), test_reflection_loop(), test_approval_gate_integration().
```

### PROMPT 36
```
Create tests/integration/test_auth_flow.py: Test auth across system. test_jwt_to_workspace(), test_workspace_isolation(), test_unauthorized_access_blocked().
```

### PROMPT 37
```
Create tests/integration/test_billing_flow.py: Test billing integration. test_usage_tracking(), test_budget_enforcement(), test_overage_handling().
```

### PROMPT 38
```
Create tests/e2e/__init__.py and tests/e2e/conftest.py: End-to-end test fixtures. Running backend server. Test database. Clean state between tests.
```

### PROMPT 39
```
Create tests/e2e/test_onboarding_flow.py: Full onboarding test. test_step_1_evidence_upload(), test_step_2_extraction(), test_complete_onboarding(). All 13 steps.
```

### PROMPT 40
```
Create tests/e2e/test_move_execution.py: Full move test. test_create_move(), test_generate_tasks(), test_execute_tasks(), test_complete_move().
```

### PROMPT 41
```
Create tests/e2e/test_content_generation.py: Full content test. test_generate_email(), test_generate_social_post(), test_quality_check(), test_revision().
```

### PROMPT 42
```
Create tests/e2e/test_research_flow.py: Full research test. test_trigger_research(), test_retrieve_findings(), test_store_results().
```

### PROMPT 43
```
Create tests/e2e/test_approval_flow.py: Full approval test. test_request_approval(), test_approve_output(), test_reject_with_feedback(), test_timeout_handling().
```

### PROMPT 44
```
Create tests/performance/__init__.py: Performance test setup.
```

### PROMPT 45
```
Create tests/performance/test_routing_latency.py: Routing performance. test_semantic_router_latency() < 50ms. test_full_pipeline_latency() < 500ms. Benchmarks.
```

### PROMPT 46
```
Create tests/performance/test_memory_latency.py: Memory performance. test_vector_search_latency() < 100ms. test_graph_query_latency() < 200ms.
```

### PROMPT 47
```
Create tests/performance/test_concurrent_requests.py: Concurrency test. test_10_concurrent_requests(), test_100_concurrent_requests(). Measure throughput.
```

### PROMPT 48
```
Create tests/security/__init__.py: Security test setup.
```

### PROMPT 49
```
Create tests/security/test_workspace_isolation.py: Isolation tests. test_cannot_access_other_workspace_data(), test_cannot_query_other_user_foundation(), test_rls_enforced().
```

### PROMPT 50
```
Create tests/security/test_input_validation.py: Input security. test_sql_injection_prevented(), test_xss_sanitized(), test_large_input_rejected().
```

---

## PROMPTS 51-70: Deployment Configuration

### PROMPT 51
```
Create backend/Dockerfile.prod: Production Dockerfile. Multi-stage build. Non-root user. Health check. Optimized layers. Minimal image size.
```

### PROMPT 52
```
Create backend/docker-compose.prod.yml: Production compose. Backend service. Redis (managed). Secrets from env. Logging driver. Restart policy.
```

### PROMPT 53
```
Create gcp/cloudbuild.yaml: Cloud Build config. Build image. Push to Artifact Registry. Deploy to Cloud Run. Set env vars. Traffic migration.
```

### PROMPT 54
```
Create gcp/cloudrun.yaml: Cloud Run service config. CPU/memory limits. Min/max instances. Concurrency. Timeout. VPC connector.
```

### PROMPT 55
```
Create gcp/terraform/cloud_run.tf: Terraform for Cloud Run. Service definition. IAM bindings. Domain mapping. SSL certificate.
```

### PROMPT 56
```
Create gcp/terraform/redis.tf: Terraform for Redis. Upstash integration or Memorystore. Connection string output.
```

### PROMPT 57
```
Create gcp/terraform/secrets.tf: Terraform for secrets. Secret Manager resources. IAM for Cloud Run access.
```

### PROMPT 58
```
Create gcp/terraform/monitoring.tf: Terraform for monitoring. Uptime checks. Alert policies. Dashboard. Notification channels.
```

### PROMPT 59
```
Create gcp/terraform/iam.tf: Terraform for IAM. Service accounts. Roles. Workload identity.
```

### PROMPT 60
```
Create .github/workflows/deploy-prod.yml: Production deployment workflow. On release tag. Run tests. Build. Deploy staging. Smoke test. Deploy prod.
```

### PROMPT 61
```
Create .github/workflows/deploy-staging.yml: Staging deployment workflow. On push to main. Build. Deploy to staging. Run e2e tests.
```

### PROMPT 62
```
Create .github/workflows/pr-checks.yml: PR checks workflow. Linting. Unit tests. Coverage. Security scan. Block if failing.
```

### PROMPT 63
```
Create scripts/deploy.sh: Deployment script. Parse args. Build image. Push. Deploy. Wait for healthy. Rollback on failure.
```

### PROMPT 64
```
Create scripts/rollback.sh: Rollback script. Get previous revision. Switch traffic. Verify health.
```

### PROMPT 65
```
Create scripts/setup-gcp.sh: GCP setup script. Enable APIs. Create service accounts. Set up secrets. Initialize Terraform.
```

### PROMPT 66
```
Create scripts/setup-supabase.sh: Supabase setup script. Run migrations. Enable extensions. Set up webhooks. Verify RLS.
```

### PROMPT 67
```
Create scripts/seed-dev.sh: Development seeding. Create test user. Populate sample data. Initialize memory.
```

### PROMPT 68
```
Create scripts/health-check.sh: Health check script. Check all endpoints. Verify integrations. Return exit code.
```

### PROMPT 69
```
Create .env.staging: Staging environment variables. Staging Supabase, Redis URLs. Feature flags for staging.
```

### PROMPT 70
```
Create .env.production: Production environment template. Production URLs. Strict settings. All required vars documented.
```

---

## PROMPTS 71-85: Documentation

### PROMPT 71
```
Create backend/README.md: Main backend documentation. Architecture overview. Setup instructions. Development workflow. API overview.
```

### PROMPT 72
```
Create docs/API.md: Complete API documentation. All endpoints. Request/response schemas. Authentication. Rate limits. Examples.
```

### PROMPT 73
```
Create docs/ARCHITECTURE.md: Architecture documentation. Component diagram. Data flow. Agent system. Memory system. Cognitive engine.
```

### PROMPT 74
```
Create docs/DEPLOYMENT.md: Deployment guide. Prerequisites. GCP setup. Supabase setup. CI/CD. Monitoring.
```

### PROMPT 75
```
Create docs/DEVELOPMENT.md: Development guide. Local setup. Running tests. Code style. PR process. Debugging.
```

### PROMPT 76
```
Create docs/AGENTS.md: Agent documentation. Available agents. Creating new agents. Tools. Memory access. Prompts.
```

### PROMPT 77
```
Create docs/MEMORY.md: Memory system documentation. Vector memory. Graph memory. Episodic memory. Working memory. Access patterns.
```

### PROMPT 78
```
Create docs/COGNITIVE.md: Cognitive engine documentation. Perception. Planning. Reflection. HITL. Protocols.
```

### PROMPT 79
```
Create docs/SECURITY.md: Security documentation. Authentication. Authorization. RLS. Data isolation. Audit logging.
```

### PROMPT 80
```
Create docs/TROUBLESHOOTING.md: Troubleshooting guide. Common errors. Debugging steps. Log analysis. Support contacts.
```

### PROMPT 81
```
Create docs/RUNBOOK.md: Operations runbook. Incident response. Scaling. Maintenance. Backup/restore.
```

### PROMPT 82
```
Create CHANGELOG.md: Changelog template. Versioning strategy. Release notes format. Breaking changes.
```

### PROMPT 83
```
Create CONTRIBUTING.md: Contributing guide. Code of conduct. Issue templates. PR templates. Review process.
```

### PROMPT 84
```
Create .github/ISSUE_TEMPLATE/bug_report.md: Bug report template. Reproduction steps. Expected/actual behavior. Environment.
```

### PROMPT 85
```
Create .github/PULL_REQUEST_TEMPLATE.md: PR template. Description. Type of change. Checklist. Testing done.
```

---

## PROMPTS 86-100: Final Verification & Launch

### PROMPT 86
```
Create scripts/verify-all.py: Comprehensive verification script. Check all imports resolve. Check all configs load. Check all connections. Generate report.
```

### PROMPT 87
```
Create scripts/run-all-tests.sh: Run all tests. Unit, integration, e2e, security, performance. Generate coverage report. Exit on failure.
```

### PROMPT 88
```
Create scripts/lint-all.sh: Run all linters. Black, isort, flake8, mypy. Auto-fix where possible. Report issues.
```

### PROMPT 89
```
Create scripts/security-scan.sh: Security scanning. Dependency vulnerabilities. Secret detection. Code analysis. Report.
```

### PROMPT 90
```
Create scripts/load-test.sh: Load testing. Run locust tests. Generate report. Compare to baseline.
```

### PROMPT 91
```
Create scripts/smoke-test.sh: Smoke tests for deployment. Check health endpoints. Check core functionality. Quick validation.
```

### PROMPT 92
```
Create backend/version.py: Version info. __version__ = "1.0.0". get_version_info() includes commit hash, build date.
```

### PROMPT 93
```
Create scripts/release.sh: Release script. Update version. Generate changelog. Create tag. Push. Trigger deployment.
```

### PROMPT 94
```
Create scripts/hotfix.sh: Hotfix script. Create hotfix branch. Cherry-pick fix. Fast-track deployment.
```

### PROMPT 95
```
Create monitoring/alerts.yaml: Alert configurations. Error rate > 1%. Latency p99 > 2s. Memory > 80%. Custom alerts.
```

### PROMPT 96
```
Create monitoring/dashboards/main.json: Main monitoring dashboard. Request rate. Latency. Errors. Agent metrics. Memory usage.
```

### PROMPT 97
```
Create monitoring/dashboards/agents.json: Agent monitoring dashboard. Per-agent metrics. Token usage. Cost. Success rate.
```

### PROMPT 98
```
Create scripts/post-deploy-verify.sh: Post-deployment verification. Run smoke tests. Check metrics. Verify integrations. Alert on failure.
```

### PROMPT 99
```
Create LAUNCH_CHECKLIST.md: Launch checklist. All tests passing. Security review. Performance baseline. Monitoring active. Documentation complete. Rollback plan ready.
```

### PROMPT 100
```
Create backend/api/v1/version.py: GET /version returns version info. GET /version/features returns feature flags. GET /version/health returns system health summary. For operational visibility.
```

---

## FINAL VERIFICATION

After ALL 600 prompts completed across 6 streams, verify:

### Stream 1: Routing & Agents
- [ ] All agents instantiate without errors
- [ ] Routing pipeline returns valid decisions
- [ ] Tools execute correctly
- [ ] LangGraph workflows compile

### Stream 2: Memory Systems
- [ ] pgvector extension enabled
- [ ] Vector search returns results
- [ ] Graph queries work
- [ ] Redis sessions persist

### Stream 3: Cognitive Engine
- [ ] Perception extracts entities/intent
- [ ] Planning creates valid plans
- [ ] Reflection improves quality
- [ ] Approval gates work

### Stream 4: Database & Auth
- [ ] All migrations run
- [ ] RLS policies active
- [ ] Auth middleware works
- [ ] Repositories CRUD correctly

### Stream 5: Redis & Infrastructure
- [ ] Redis client connects
- [ ] Sessions/cache/rate-limit work
- [ ] Background jobs execute
- [ ] Health checks pass

### Stream 6: Integration
- [ ] All modules integrate
- [ ] E2E tests pass
- [ ] Deployment succeeds
- [ ] Monitoring active

## LAUNCH READY ✓
