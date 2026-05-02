use super::common::*;

pub async fn create_nudge(
    pool: &PgPool,
    nudge_id: &str,
    org_id: uuid::Uuid,
    user_id: uuid::Uuid,
    nudge_type: &str,
    priority: &str,
    title: &str,
    body: &str,
    action_type: Option<&str>,
    action_data: &serde_json::Value,
    source_type: &str,
    source_id: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO nudges
        (nudge_id, org_id, user_id, nudge_type, priority, title, body, action_type, action_data, source_type, source_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        "#,
    )
    .bind(nudge_id)
    .bind(org_id)
    .bind(user_id)
    .bind(nudge_type)
    .bind(priority)
    .bind(title)
    .bind(body)
    .bind(action_type)
    .bind(action_data)
    .bind(source_type)
    .bind(source_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_nudges(pool: &PgPool, org_id: uuid::Uuid) -> Result<Vec<Nudge>, sqlx::Error> {
    let rows = sqlx::query_as::<_, Nudge>(
        r#"
        SELECT nudge_id, org_id, user_id, nudge_type, priority, title, body,
               action_type, action_data, source_type, source_id,
               created_at, delivered_at, viewed_at, acted_on_at, dismissed_at
        FROM nudges
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 50
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_nudge(
    pool: &PgPool,
    nudge_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<Nudge>, sqlx::Error> {
    let row = sqlx::query_as::<_, Nudge>(
        r#"
        SELECT nudge_id, org_id, user_id, nudge_type, priority, title, body,
               action_type, action_data, source_type, source_id,
               created_at, delivered_at, viewed_at, acted_on_at, dismissed_at, suppressed
        FROM nudges
        WHERE nudge_id = $1 AND org_id = $2
        "#,
    )
    .bind(nudge_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn update_nudge_viewed(
    pool: &PgPool,
    nudge_id: &str,
    org_id: uuid::Uuid,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE nudges
        SET viewed_at = now()
        WHERE nudge_id = $1 AND org_id = $2 AND viewed_at IS NULL
        "#,
    )
    .bind(nudge_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_nudge_dismissed(
    pool: &PgPool,
    nudge_id: &str,
    org_id: uuid::Uuid,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE nudges
        SET dismissed_at = now(), suppressed = true
        WHERE nudge_id = $1 AND org_id = $2 AND dismissed_at IS NULL
        "#,
    )
    .bind(nudge_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_daily_wins(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<DailyWin>, sqlx::Error> {
    let rows = sqlx::query_as::<_, DailyWin>(
        r#"
        SELECT briefing_id, org_id, briefing_date, generated_at, lead_summary, full_briefing,
               recommended_action, recommended_action_type, recommended_action_data,
               viewed_at, acted_on_at, action_outcome, created_at
        FROM daily_wins
        WHERE org_id = $1
        ORDER BY briefing_date DESC
        LIMIT 30
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_today_daily_win(
    pool: &PgPool,
    org_id: uuid::Uuid,
    today: chrono::NaiveDate,
) -> Result<Option<DailyWin>, sqlx::Error> {
    let row = sqlx::query_as::<_, DailyWin>(
        r#"
        SELECT briefing_id, org_id, briefing_date, generated_at, lead_summary, full_briefing,
               recommended_action, recommended_action_type, recommended_action_data,
               viewed_at, acted_on_at, action_outcome, created_at
        FROM daily_wins
        WHERE org_id = $1 AND briefing_date = $2
        "#,
    )
    .bind(org_id)
    .bind(today)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn create_daily_win(
    pool: &PgPool,
    briefing_id: &str,
    org_id: uuid::Uuid,
    briefing_date: chrono::NaiveDate,
    lead_summary: &str,
    full_briefing: &str,
    recommended_action: &str,
    recommended_action_type: &str,
    recommended_action_data: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO daily_wins (briefing_id, org_id, briefing_date, generated_at, lead_summary, full_briefing, recommended_action, recommended_action_type, recommended_action_data)
        VALUES ($1, $2, $3, now(), $4, $5, $6, $7, $8)
        "#,
    )
    .bind(briefing_id)
    .bind(org_id)
    .bind(briefing_date)
    .bind(lead_summary)
    .bind(full_briefing)
    .bind(recommended_action)
    .bind(recommended_action_type)
    .bind(recommended_action_data)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_daily_win_viewed(
    pool: &PgPool,
    briefing_id: &str,
    org_id: uuid::Uuid,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE daily_wins
        SET viewed_at = now()
        WHERE briefing_id = $1 AND org_id = $2 AND viewed_at IS NULL
        "#,
    )
    .bind(briefing_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}
