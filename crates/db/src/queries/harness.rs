use super::common::*;

pub async fn list_harness_runs(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<HarnessRun>, sqlx::Error> {
    let rows = sqlx::query_as::<_, HarnessRun>(
        r#"
        SELECT run_id, org_id, run_type, status, input, output, error_message,
               created_by, started_at, completed_at, created_at, updated_at
        FROM harness_runs
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 100
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_harness_run(
    pool: &PgPool,
    run_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<HarnessRun>, sqlx::Error> {
    let row = sqlx::query_as::<_, HarnessRun>(
        r#"
        SELECT run_id, org_id, run_type, status, input, output, error_message,
               created_by, started_at, completed_at, created_at, updated_at
        FROM harness_runs
        WHERE run_id = $1 AND org_id = $2
        "#,
    )
    .bind(run_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn create_harness_run(
    pool: &PgPool,
    run_id: &str,
    org_id: uuid::Uuid,
    run_type: &str,
    input: &serde_json::Value,
    created_by: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO harness_runs (run_id, org_id, run_type, status, input, created_by)
        VALUES ($1, $2, $3, 'queued', $4, $5)
        "#,
    )
    .bind(run_id)
    .bind(org_id)
    .bind(run_type)
    .bind(input)
    .bind(created_by)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_harness_run_status(
    pool: &PgPool,
    run_id: &str,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    let started = if status == "running" {
        Some(chrono::Utc::now())
    } else {
        None
    };
    let completed = if status == "completed" || status == "failed" || status == "cancelled" {
        Some(chrono::Utc::now())
    } else {
        None
    };
    sqlx::query(
        r#"
        UPDATE harness_runs
        SET status = $1,
            started_at = COALESCE($2, started_at),
            completed_at = COALESCE($3, completed_at),
            updated_at = now()
        WHERE run_id = $4 AND org_id = $5
        "#,
    )
    .bind(status)
    .bind(started)
    .bind(completed)
    .bind(run_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn cancel_harness_run(
    pool: &PgPool,
    run_id: &str,
    org_id: uuid::Uuid,
) -> Result<(), sqlx::Error> {
    update_harness_run_status(pool, run_id, org_id, "cancelled").await
}

pub async fn list_harness_steps(
    pool: &PgPool,
    run_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<HarnessStep>, sqlx::Error> {
    let rows = sqlx::query_as::<_, HarnessStep>(
        r#"
        SELECT step_id, run_id, org_id, avatar_id, step_type, status, input, output,
               error_message, sequence_number, started_at, completed_at, created_at, updated_at
        FROM harness_steps
        WHERE run_id = $1 AND org_id = $2
        ORDER BY sequence_number ASC
        "#,
    )
    .bind(run_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn create_harness_step(
    pool: &PgPool,
    step_id: &str,
    run_id: &str,
    org_id: uuid::Uuid,
    avatar_id: Option<&str>,
    step_type: &str,
    sequence_number: i32,
    input: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO harness_steps (step_id, run_id, org_id, avatar_id, step_type, sequence_number, input)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        "#,
    )
    .bind(step_id)
    .bind(run_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(step_type)
    .bind(sequence_number)
    .bind(input)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_harness_step_status(
    pool: &PgPool,
    step_id: &str,
    org_id: uuid::Uuid,
    status: &str,
    output: Option<&serde_json::Value>,
    error_message: Option<&str>,
) -> Result<(), sqlx::Error> {
    let started = if status == "running" {
        Some(chrono::Utc::now())
    } else {
        None
    };
    let completed = if status == "completed" || status == "failed" || status == "cancelled" {
        Some(chrono::Utc::now())
    } else {
        None
    };
    sqlx::query(
        r#"
        UPDATE harness_steps
        SET status = $1,
            output = COALESCE($2, output),
            error_message = COALESCE($3, error_message),
            started_at = COALESCE($4, started_at),
            completed_at = COALESCE($5, completed_at),
            updated_at = now()
        WHERE step_id = $6 AND org_id = $7
        "#,
    )
    .bind(status)
    .bind(output)
    .bind(error_message)
    .bind(started)
    .bind(completed)
    .bind(step_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}
