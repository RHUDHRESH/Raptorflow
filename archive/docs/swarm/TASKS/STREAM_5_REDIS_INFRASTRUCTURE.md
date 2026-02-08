# STREAM 5: REDIS & INFRASTRUCTURE (100 Prompts)

> **INSTRUCTIONS**: Copy each prompt to your AI assistant. Each is self-contained.
> **CONTEXT**: Reference `DOCUMENTATION/SWARM/IMPLEMENTATION/07_REDIS_ARCHITECTURE.md`

---

## PROMPTS 1-25: Redis Core Services

### PROMPT 1
```
Create backend/redis/__init__.py exporting: RedisClient, SessionService, CacheService, RateLimitService, QueueService, PubSubService.
```

### PROMPT 2
```
Create backend/redis/client.py: RedisClient singleton for Upstash Redis. __init__ loads UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN from config. Methods: get(key), set(key, value, ex=None), delete(key), exists(key), expire(key, seconds), ttl(key), incr(key), decr(key). Async versions.
```

### PROMPT 3
```
Create backend/redis/config.py: RedisConfig with UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN from env. KEY_PREFIX = "raptorflow:". DEFAULT_TTL = 3600. MAX_CONNECTIONS = 10. Connection settings.
```

### PROMPT 4
```
Create backend/redis/keys.py: Key patterns. session:{session_id}, cache:{workspace_id}:{key}, rate:{user_id}:{endpoint}, queue:{queue_name}, pubsub:{channel}, lock:{resource}, usage:{workspace_id}:{period}. Helper functions to build keys.
```

### PROMPT 5
```
Create backend/redis/session.py: SessionService. KEY_PREFIX = "session:". DEFAULT_TTL = 1800 (30 min). async create_session(user_id, workspace_id, metadata) -> session_id. async get_session(session_id) -> SessionData | None. async update_session(session_id, updates). async delete_session(session_id). async extend_session(session_id, seconds).
```

### PROMPT 6
```
Create backend/redis/session_models.py: @dataclass SessionData with session_id, user_id, workspace_id, current_agent, messages (list), context (dict), created_at, last_active_at, expires_at. Serialization to/from JSON.
```

### PROMPT 7
```
Create backend/redis/cache.py: CacheService. async get(workspace_id, key) -> Any | None. async set(workspace_id, key, value, ttl=3600). async delete(workspace_id, key). async clear_workspace(workspace_id). async get_or_set(workspace_id, key, factory_fn, ttl).
```

### PROMPT 8
```
Create backend/redis/cache_decorators.py: @cached(ttl=3600, key_fn=None) decorator for caching function results. Generates key from function name and args. Invalidation support. Async compatible.
```

### PROMPT 9
```
Create backend/redis/rate_limit.py: RateLimitService. async check_limit(user_id, endpoint, limit, window_seconds) -> RateLimitResult with allowed, remaining, reset_at. async record_request(user_id, endpoint). Sliding window algorithm.
```

### PROMPT 10
```
Create backend/redis/rate_limit_config.py: Rate limit configurations per endpoint. LIMITS = {"/api/v1/agents/execute": (10, 60), "/api/v1/muse/generate": (20, 60)}. get_limit(endpoint, user_tier) returns (limit, window).
```

### PROMPT 11
```
Create backend/redis/usage.py: UsageTracker. async record_usage(workspace_id, tokens, cost, agent). async get_usage(workspace_id, period="current_month") -> UsageStats. async get_daily_breakdown(workspace_id). async check_limit(workspace_id) -> bool.
```

### PROMPT 12
```
Create backend/redis/usage_models.py: @dataclass UsageStats with period, total_tokens, total_cost, by_agent (dict), by_day (dict), limit_tokens, limit_cost, percentage_used.
```

### PROMPT 13
```
Create backend/redis/queue.py: QueueService. async enqueue(queue_name, job_data, priority=0). async dequeue(queue_name) -> Job | None. async peek(queue_name). async queue_length(queue_name). async clear_queue(queue_name). Priority queue support.
```

### PROMPT 14
```
Create backend/redis/queue_models.py: @dataclass Job with job_id, queue_name, data, priority, created_at, started_at, completed_at, status, result, error. JobStatus enum (PENDING, PROCESSING, COMPLETED, FAILED).
```

### PROMPT 15
```
Create backend/redis/worker.py: QueueWorker. __init__(queue_name, handler_fn). async start() runs continuously. async process_job(job). async stop(). Graceful shutdown. Error handling with retry.
```

### PROMPT 16
```
Create backend/redis/pubsub.py: PubSubService. async publish(channel, message). async subscribe(channel, callback). async unsubscribe(channel). Channels: agent_updates, approval_requests, session_events.
```

### PROMPT 17
```
Create backend/redis/locks.py: DistributedLock. async acquire(resource, timeout=30, retry_delay=0.1) -> bool. async release(resource). async extend(resource, seconds). Context manager support. Prevents race conditions.
```

### PROMPT 18
```
Create backend/redis/atomic.py: AtomicOperations. async increment(key, amount=1). async decrement(key, amount=1). async compare_and_set(key, expected, new_value). async get_and_set(key, new_value). For thread-safe operations.
```

### PROMPT 19
```
Create backend/redis/pipeline.py: RedisPipeline. async execute(operations: List[RedisOp]). Batches multiple operations. Reduces round trips. Transaction support.
```

### PROMPT 20
```
Create backend/redis/lua_scripts.py: Lua scripts for atomic operations. RATE_LIMIT_SCRIPT for sliding window. QUEUE_DEQUEUE_SCRIPT for atomic dequeue. register_scripts() loads into Redis.
```

### PROMPT 21
```
Create backend/redis/ttl_manager.py: TTLManager. async set_ttl(key, seconds). async get_ttl(key). async refresh_ttl(key, seconds). async cleanup_expired(). Scheduled cleanup job.
```

### PROMPT 22
```
Create backend/redis/metrics.py: RedisMetrics. async get_metrics() -> RedisMetricsReport with memory_used, keys_count, connections, ops_per_second. For monitoring dashboard.
```

### PROMPT 23
```
Create backend/redis/health.py: RedisHealthChecker. async check_connection() -> bool. async check_latency() -> float. async check_memory() -> MemoryStatus. Returns detailed health report.
```

### PROMPT 24
```
Create backend/redis/backup.py: RedisBackup. async backup_keys(pattern) -> dict. async restore_keys(data). async export_to_file(pattern, filepath). For development/migration.
```

### PROMPT 25
```
Create backend/redis/cleanup.py: RedisCleanup. async cleanup_expired_sessions(). async cleanup_old_cache(). async cleanup_stale_locks(). Scheduled maintenance tasks.
```

---

## PROMPTS 26-50: Infrastructure Services

### PROMPT 26
```
Create backend/infrastructure/__init__.py exporting: GCPClient, CloudStorage, BigQueryClient, PubSubClient, CloudTasksClient.
```

### PROMPT 27
```
Create backend/infrastructure/gcp.py: GCPClient singleton. __init__ initializes credentials from env. get_project_id(). get_region(). For GCP service access.
```

### PROMPT 28
```
Create backend/infrastructure/storage.py: CloudStorage. async upload_file(bucket, path, content, content_type). async download_file(bucket, path) -> bytes. async delete_file(bucket, path). async generate_signed_url(bucket, path, expiration). For file storage.
```

### PROMPT 29
```
Create backend/infrastructure/storage_config.py: Storage buckets. EVIDENCE_BUCKET for uploaded files. EXPORTS_BUCKET for generated exports. ASSETS_BUCKET for muse assets. Bucket configurations.
```

### PROMPT 30
```
Create backend/infrastructure/bigquery.py: BigQueryClient. async execute_query(query, params) -> List[dict]. async insert_rows(table, rows). async create_table_if_not_exists(table, schema). For analytics.
```

### PROMPT 31
```
Create backend/infrastructure/bigquery_schemas.py: BigQuery table schemas. agent_executions_schema, usage_events_schema, user_events_schema. Schema definitions.
```

### PROMPT 32
```
Create backend/infrastructure/pubsub_client.py: PubSubClient for GCP Pub/Sub. async publish(topic, message). async subscribe(subscription, handler). For async event processing.
```

### PROMPT 33
```
Create backend/infrastructure/cloud_tasks.py: CloudTasksClient. async create_task(queue, handler_url, payload, delay_seconds). async delete_task(task_name). For scheduled/delayed tasks.
```

### PROMPT 34
```
Create backend/infrastructure/secrets.py: SecretsManager. async get_secret(secret_id) -> str. async set_secret(secret_id, value). Integrates with GCP Secret Manager.
```

### PROMPT 35
```
Create backend/infrastructure/logging.py: CloudLogging. configure_logging() sets up structured logging. log_with_context(level, message, **context). Integration with Cloud Logging.
```

### PROMPT 36
```
Create backend/infrastructure/monitoring.py: CloudMonitoring. async record_metric(name, value, labels). async create_alert_policy(name, conditions). For custom metrics.
```

### PROMPT 37
```
Create backend/infrastructure/tracing.py: CloudTracing. start_span(name). end_span(). Distributed tracing integration. OpenTelemetry compatible.
```

### PROMPT 38
```
Create backend/infrastructure/errors.py: ErrorReporting. async report_error(error, context). configure_error_reporting(). Integrates with Cloud Error Reporting.
```

---

## PROMPTS 39-60: Background Jobs & Tasks

### PROMPT 39
```
Create backend/jobs/__init__.py exporting: JobScheduler, job (decorator), JobResult, all job implementations.
```

### PROMPT 40
```
Create backend/jobs/scheduler.py: JobScheduler. register_job(name, fn, schedule). start() begins scheduler. stop() stops gracefully. Uses APScheduler or Cloud Tasks.
```

### PROMPT 41
```
Create backend/jobs/decorators.py: @job(name, queue="default", retries=3, timeout=300) decorator. Wraps functions as async jobs. Error handling. Retry logic.
```

### PROMPT 42
```
Create backend/jobs/models.py: @dataclass JobResult with job_id, status, result, error, started_at, completed_at, retries. JobStatus enum.
```

### PROMPT 43
```
Create backend/jobs/memory_jobs.py: memory_indexing_job(workspace_id) reindexes memory. memory_cleanup_job() prunes old memories. memory_sync_job() syncs vector/graph.
```

### PROMPT 44
```
Create backend/jobs/analytics_jobs.py: daily_usage_summary_job() calculates daily stats. weekly_report_job() generates reports. agent_performance_job() analyzes agents.
```

### PROMPT 45
```
Create backend/jobs/maintenance_jobs.py: cleanup_expired_sessions_job(). cleanup_old_executions_job(days=30). vacuum_database_job(). System maintenance.
```

### PROMPT 46
```
Create backend/jobs/billing_jobs.py: calculate_usage_job(workspace_id). generate_invoice_job(workspace_id, period). check_usage_limits_job(). Billing automation.
```

### PROMPT 47
```
Create backend/jobs/research_jobs.py: refresh_competitor_intel_job(workspace_id). trend_monitoring_job(). scheduled_research_job(). Background research.
```

### PROMPT 48
```
Create backend/jobs/content_jobs.py: generate_daily_wins_job(). content_quality_check_job(). schedule_content_job(). Content automation.
```

### PROMPT 49
```
Create backend/jobs/notification_jobs.py: send_approval_reminder_job(). send_usage_alert_job(). send_weekly_digest_job(). User notifications.
```

### PROMPT 50
```
Create backend/jobs/export_jobs.py: export_workspace_job(workspace_id, format). export_analytics_job(workspace_id, period). Long-running exports.
```

---

## PROMPTS 51-70: Webhooks & Events

### PROMPT 51
```
Create backend/webhooks/__init__.py exporting: WebhookHandler, verify_webhook, WebhookEvent.
```

### PROMPT 52
```
Create backend/webhooks/handler.py: WebhookHandler. register_handler(event_type, fn). async handle(event: WebhookEvent). Dispatches to registered handlers.
```

### PROMPT 53
```
Create backend/webhooks/verification.py: verify_webhook(payload, signature, secret) -> bool. Validates webhook signatures. Supports multiple formats (HMAC, etc.).
```

### PROMPT 54
```
Create backend/webhooks/models.py: @dataclass WebhookEvent with event_id, event_type, payload, timestamp, source. Common event types enum.
```

### PROMPT 55
```
Create backend/webhooks/supabase.py: SupabaseWebhookHandler. handle_auth_event(event). handle_database_event(event). For Supabase webhooks.
```

### PROMPT 56
```
Create backend/webhooks/stripe.py: StripeWebhookHandler. handle_payment_succeeded(event). handle_subscription_updated(event). For Stripe webhooks (future).
```

### PROMPT 57
```
Create backend/webhooks/phonepe.py: PhonePeWebhookHandler. handle_payment_callback(event). handle_refund_callback(event). For PhonePe webhooks.
```

### PROMPT 58
```
Create backend/events/__init__.py exporting: EventBus, Event, emit_event, subscribe_event.
```

### PROMPT 59
```
Create backend/events/bus.py: EventBus singleton. async emit(event: Event). subscribe(event_type, handler). Internal event system using Redis pub/sub.
```

### PROMPT 60
```
Create backend/events/types.py: Event types. FoundationUpdated, ICPCreated, MoveStarted, ContentGenerated, ApprovalRequested, UsageLimitReached. Type definitions.
```

### PROMPT 61
```
Create backend/events/handlers/__init__.py: Export all event handlers.
```

### PROMPT 62
```
Create backend/events/handlers/memory_handlers.py: on_foundation_updated() triggers reindexing. on_icp_created() adds to graph. Memory sync handlers.
```

### PROMPT 63
```
Create backend/events/handlers/notification_handlers.py: on_approval_requested() sends notification. on_usage_limit_reached() alerts user.
```

### PROMPT 64
```
Create backend/events/handlers/analytics_handlers.py: on_agent_execution() records metrics. on_content_generated() tracks output.
```

---

## PROMPTS 65-80: Deployment & Configuration

### PROMPT 65
```
Create backend/config/__init__.py exporting: Settings, get_settings, Environment.
```

### PROMPT 66
```
Create backend/config/settings.py: Settings(BaseSettings) with all config. Environment enum (DEV, STAGING, PROD). Loads from .env. Validation. Defaults per environment.
```

### PROMPT 67
```
Create backend/config/logging_config.py: Configure logging. JSON format for production. Pretty print for dev. Log levels per module. Request ID injection.
```

### PROMPT 68
```
Create backend/config/cors_config.py: CORS settings. ALLOWED_ORIGINS per environment. ALLOWED_METHODS. ALLOWED_HEADERS. Credentials support.
```

### PROMPT 69
```
Create backend/config/feature_flags.py: FeatureFlags. is_enabled(flag_name, user_id=None) -> bool. Gradual rollout support. Per-user flags.
```

### PROMPT 70
```
Create backend/Dockerfile: FROM python:3.11-slim. Install dependencies. Copy code. Health check. Run uvicorn. Optimized for Cloud Run.
```

### PROMPT 71
```
Create backend/docker-compose.yml: Services: backend, redis (local dev), supabase (local dev). Volume mounts. Environment variables. For local development.
```

### PROMPT 72
```
Create backend/cloudbuild.yaml: Cloud Build steps. Build Docker image. Push to Artifact Registry. Deploy to Cloud Run. Environment variables.
```

### PROMPT 73
```
Create backend/.env.example: Example environment variables. All required vars. Comments explaining each. Safe defaults.
```

### PROMPT 74
```
Create gcp/terraform/main.tf: Terraform for GCP resources. Cloud Run service. Cloud SQL (if needed). Redis (Memorystore). IAM. VPC connector.
```

### PROMPT 75
```
Create gcp/terraform/variables.tf: Terraform variables. project_id, region, environment. Service configurations. Defaults.
```

### PROMPT 76
```
Create gcp/terraform/outputs.tf: Terraform outputs. Service URL. Database connection. Redis endpoint. For CI/CD.
```

### PROMPT 77
```
Create .github/workflows/backend-deploy.yml: GitHub Actions workflow. On push to main. Run tests. Build. Deploy to Cloud Run. Notify on failure.
```

### PROMPT 78
```
Create .github/workflows/backend-test.yml: GitHub Actions workflow. On PR. Run linting. Run tests. Coverage report. Block merge if failing.
```

---

## PROMPTS 79-100: Testing & Monitoring

### PROMPT 79
```
Create tests/redis/__init__.py and tests/redis/conftest.py: Fixtures for Redis tests. mock_redis, test_session_data, test_cache_data.
```

### PROMPT 80
```
Create tests/redis/test_session.py: Tests for SessionService. test_create_session(), test_get_session(), test_session_expiry(), test_extend_session().
```

### PROMPT 81
```
Create tests/redis/test_cache.py: Tests for CacheService. test_get_set(), test_cache_expiry(), test_clear_workspace(), test_get_or_set().
```

### PROMPT 82
```
Create tests/redis/test_rate_limit.py: Tests for RateLimitService. test_within_limit(), test_exceeded_limit(), test_limit_reset(), test_sliding_window().
```

### PROMPT 83
```
Create tests/redis/test_queue.py: Tests for QueueService. test_enqueue_dequeue(), test_priority_queue(), test_queue_length().
```

### PROMPT 84
```
Create tests/redis/test_locks.py: Tests for DistributedLock. test_acquire_release(), test_lock_timeout(), test_concurrent_access().
```

### PROMPT 85
```
Create tests/jobs/test_scheduler.py: Tests for JobScheduler. test_job_registration(), test_job_execution(), test_retry_on_failure().
```

### PROMPT 86
```
Create tests/webhooks/test_handlers.py: Tests for webhook handlers. test_supabase_webhook(), test_phonepe_webhook(), test_signature_verification().
```

### PROMPT 87
```
Create tests/infrastructure/test_storage.py: Tests for CloudStorage. test_upload_download(), test_signed_url(), test_delete().
```

### PROMPT 88
```
Create tests/events/test_event_bus.py: Tests for EventBus. test_emit_subscribe(), test_multiple_handlers(), test_async_handlers().
```

### PROMPT 89
```
Create backend/monitoring/dashboard.py: Monitoring dashboard data. async get_system_status(). async get_agent_metrics(). async get_usage_metrics(). API for dashboard.
```

### PROMPT 90
```
Create backend/monitoring/alerts.py: AlertManager. async check_alerts(). async send_alert(alert_type, details). Integrates with Cloud Monitoring or Slack.
```

### PROMPT 91
```
Create backend/monitoring/health.py: HealthAggregator. async full_health_check() checks all services: Supabase, Redis, Vertex AI, Cloud Storage. Returns comprehensive report.
```

### PROMPT 92
```
Create backend/api/v1/health.py: GET /health basic check. GET /health/detailed comprehensive check. GET /health/ready readiness probe. GET /health/live liveness probe.
```

### PROMPT 93
```
Create backend/api/v1/metrics.py: GET /metrics Prometheus format. GET /metrics/system system metrics. GET /metrics/agents agent metrics. For monitoring.
```

### PROMPT 94
```
Create backend/api/v1/admin.py: Admin endpoints (protected). GET /admin/stats. POST /admin/cleanup. POST /admin/reindex. For operations.
```

### PROMPT 95
```
Create backend/scripts/health_check.py: CLI script for health checks. Runs all checks. Outputs report. Exit code for CI/CD.
```

### PROMPT 96
```
Create backend/scripts/warmup.py: Warmup script. Initializes models. Primes caches. Verifies connections. Run on startup.
```

### PROMPT 97
```
Create backend/scripts/load_test.py: Load testing script using locust. Simulates concurrent users. Measures latency, throughput. Generates report.
```

### PROMPT 98
```
Create backend/scripts/benchmark.py: Benchmark script. Tests key operations. Measures performance. Compares configurations.
```

### PROMPT 99
```
Create backend/infrastructure/README.md: Documentation for infrastructure. GCP setup guide. Redis configuration. Deployment process. Monitoring setup.
```

### PROMPT 100
```
Create backend/redis/README.md: Documentation for Redis services. Key patterns. Service usage. TTL policies. Scaling considerations.
```

---

## VERIFICATION

After all prompts completed, verify:
- [ ] Redis client connects to Upstash
- [ ] Sessions create and retrieve correctly
- [ ] Rate limiting works
- [ ] Queues process jobs
- [ ] Background jobs execute
- [ ] Webhooks validate and handle
- [ ] Health checks pass
- [ ] Deployment works
