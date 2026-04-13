# Jobs Runbook

Background jobs are dispatched via AWS SQS. Each job has a registered type in [`crates/jobs/src/lib.rs`](../../crates/jobs/src/lib.rs) (`registry()`).

## All registered jobs

| Job key                         | Trigger                | Description                                                                                                         |
| ------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `swr-consolidation`             | Nightly cron           | Sharp wave ripple consolidation — replays selected ripples through Oja edges, updates BARR, distills and compresses |
| `daily-wins`                    | Nightly cron           | Generates the daily briefing for each org based on overnight PRL activity                                           |
| `intel-scan`                    | Operator-triggered     | Competitive intelligence scan — pulls from configured intel sources                                                 |
| `campaign-replanning`           | Campaign-level trigger | Autonomous replanning when performance signals diverge from targets                                                 |
| `embedding-worker`              | SQS queue              | Generates vector embeddings for ripple text via `text-embedding-004` → 64-dim                                       |
| `prediction-resolution`         | Event-driven           | Records prediction outcomes, pushes results back into PRL confidence and memory hygiene                             |
| `foundation-quick-scan`         | Operator-triggered     | Quick ingestion of new foundation sections from source documents                                                    |
| `foundation-deep-scan`          | Operator-triggered     | Deep crawl + enrichment of foundation data from intel sources                                                       |
| `foundation-cache-invalidation` | Event-driven           | Records foundation version/section invalidation events and affected cache scope                                     |
| `content-feedback-loop`         | Event-driven           | Routes performance signals to update skill utility, specialist routing, or reflection inputs                        |
| `monthly-cost-thresholds`       | Monthly cron           | Converts `org_monthly_costs` deltas into operator-visible `system_alerts`                                           |
| `avatar-registry-sync`          | Event-driven           | Syncs avatar registry changes to the office canvas roster                                                           |
| `research-request`              | Operator-triggered     | Triage research requests to the appropriate intern or council                                                       |
| `tool-gateway`                  | SQS queue              | Executes tools on behalf of AI agents (web search, browser, competitive analysis)                                   |
| `intern-dispatch`               | SQS queue              | Dispatches research tasks to the intern agent system                                                                |
| `stream-coordinator`            | SQS queue              | Coordinates precheck and routing for multi-turn AI sessions                                                         |
| `event-harvester`               | SQS queue              | Ingests events into PRL as ripples with normalized salience scoring                                                 |

## Every job must

- **Acquire an org-scoped lock** before running if duplication is harmful. Use Dragonfly `lock:{org_id}:{job_name}`.
- **Emit structured tracing** with `org_id`, `job_key`, `run_id` fields.
- **Emit Sentry context** for error attribution.
- **Emit a durable loop record** before mutating downstream state (Foundation, PRL, EEL, or cost-control).
- **Be runnable as a one-off ECS task** in staging or production.

## Running a job manually

Jobs are triggered by SQS messages. To run a job manually:

```bash
# Via the internal jobs API (when implemented)
curl -X POST http://localhost:8080/internal/jobs/{job_key} \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"org_id": "..."}'
```

For now, the jobs infrastructure is scaffolded but workers are stubs — every dispatched job returns `accepted` without real processing.

## Job lock keys (Dragonfly)

| Job                     | Lock key pattern                      |
| ----------------------- | ------------------------------------- |
| `swr-consolidation`     | `lock:{org_id}:swr-consolidation`     |
| `daily-wins`            | `lock:{org_id}:daily-wins`            |
| `intel-scan`            | `lock:{org_id}:intel-scan`            |
| `campaign-replanning`   | `lock:{org_id}:campaign-replanning`   |
| `foundation-quick-scan` | `lock:{org_id}:foundation-quick-scan` |
| `foundation-deep-scan`  | `lock:{org_id}:foundation-deep-scan`  |
