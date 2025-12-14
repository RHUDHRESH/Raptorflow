# Background Jobs & Task Queue

Built-in job system to handle async processing without external dependencies like Redis (for simple use cases).

## Schema

### `public.scheduled_jobs`
Cron-like scheduler for recurring tasks.
-   `cron_expression`: e.g. `0 0 * * *` (Daily)
-   `job_type`: Name of the handler function/worker
-   `last_run_at`, `next_run_at`: Scheduling state

### `public.job_executions`
History of job runs.
-   `status`: `pending`, `running`, `completed`, `failed`
-   `result`: JSONB output
-   `duration_ms`: Performance tracking

### `public.task_queue`
Priority queue for one-off async tasks (e.g., "Send Email", "Generate Report").
-   `payload`: JSONB arguments
-   `priority`: Integer (higher runs first)
-   `scheduled_for`: For delayed execution
-   `locked_by`: Worker ID (for concurrency control)

## Usage
Workers poll `task_queue` using `FOR UPDATE SKIP LOCKED` pattern to safely claim tasks without race conditions.
