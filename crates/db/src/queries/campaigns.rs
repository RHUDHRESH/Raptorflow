use super::common::*;

pub async fn list_campaigns(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<Campaign>, sqlx::Error> {
    let rows = sqlx::query_as::<_, Campaign>(
        r#"
        SELECT campaign_id, org_id, name, goal, status, active_move_id, created_at, updated_at
        FROM campaigns
        WHERE org_id = $1
        ORDER BY created_at DESC
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_campaign(
    pool: &PgPool,
    campaign_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<Campaign>, sqlx::Error> {
    let row = sqlx::query_as::<_, Campaign>(
        r#"
        SELECT campaign_id, org_id, name, goal, status, active_move_id, created_at, updated_at
        FROM campaigns
        WHERE campaign_id = $1 AND org_id = $2
        "#,
    )
    .bind(campaign_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn create_campaign(
    pool: &PgPool,
    campaign_id: &str,
    org_id: uuid::Uuid,
    name: &str,
    goal: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO campaigns (campaign_id, org_id, name, goal, status, created_at, updated_at)
        VALUES ($1, $2, $3, $4, 'draft', now(), now())
        "#,
    )
    .bind(campaign_id)
    .bind(org_id)
    .bind(name)
    .bind(goal)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_campaign_status(
    pool: &PgPool,
    campaign_id: &str,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE campaigns
        SET status = $1, updated_at = now()
        WHERE campaign_id = $2 AND org_id = $3
        "#,
    )
    .bind(status)
    .bind(campaign_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_campaign_moves(
    pool: &PgPool,
    campaign_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<CampaignMove>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CampaignMove>(
        r#"
        SELECT move_id, campaign_id, org_id, move_type, sequence_number, status, created_at
        FROM campaign_moves
        WHERE campaign_id = $1 AND org_id = $2
        ORDER BY sequence_number ASC
        "#,
    )
    .bind(campaign_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn create_campaign_move(
    pool: &PgPool,
    move_id: &str,
    campaign_id: &str,
    org_id: uuid::Uuid,
    move_type: &str,
    sequence_number: i32,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO campaign_moves (move_id, campaign_id, org_id, move_type, sequence_number, status, created_at)
        VALUES ($1, $2, $3, $4, $5, 'planned', now())
        "#,
    )
    .bind(move_id)
    .bind(campaign_id)
    .bind(org_id)
    .bind(move_type)
    .bind(sequence_number)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_move_status(
    pool: &PgPool,
    move_id: &str,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE campaign_moves
        SET status = $1
        WHERE move_id = $2 AND org_id = $3
        "#,
    )
    .bind(status)
    .bind(move_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_campaign_tasks(
    pool: &PgPool,
    campaign_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<CampaignTask>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CampaignTask>(
        r#"
        SELECT task_id, move_id, campaign_id, org_id, title, status, scheduled_date, created_at
        FROM campaign_tasks
        WHERE campaign_id = $1 AND org_id = $2
        ORDER BY created_at ASC
        "#,
    )
    .bind(campaign_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn list_move_tasks(
    pool: &PgPool,
    move_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<CampaignTask>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CampaignTask>(
        r#"
        SELECT task_id, move_id, campaign_id, org_id, title, status, scheduled_date, created_at
        FROM campaign_tasks
        WHERE move_id = $1 AND org_id = $2
        ORDER BY created_at ASC
        "#,
    )
    .bind(move_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn create_campaign_task(
    pool: &PgPool,
    task_id: &str,
    move_id: &str,
    campaign_id: &str,
    org_id: uuid::Uuid,
    title: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO campaign_tasks (task_id, move_id, campaign_id, org_id, title, status, created_at)
        VALUES ($1, $2, $3, $4, $5, 'pending', now())
        "#,
    )
    .bind(task_id)
    .bind(move_id)
    .bind(campaign_id)
    .bind(org_id)
    .bind(title)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_task_status(
    pool: &PgPool,
    task_id: &str,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE campaign_tasks
        SET status = $1
        WHERE task_id = $2 AND org_id = $3
        "#,
    )
    .bind(status)
    .bind(task_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn create_campaign_brief(
    pool: &PgPool,
    brief_id: &str,
    org_id: uuid::Uuid,
    campaign_id: Option<&str>,
    original_text: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO campaign_briefs (brief_id, org_id, campaign_id, status, original_text, created_at)
        VALUES ($1, $2, $3, 'draft', $4, now())
        "#,
    )
    .bind(brief_id)
    .bind(org_id)
    .bind(campaign_id)
    .bind(original_text)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_campaign_brief(
    pool: &PgPool,
    campaign_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<CampaignBrief>, sqlx::Error> {
    let row = sqlx::query_as::<_, CampaignBrief>(
        r#"
        SELECT brief_id, org_id, campaign_id, status, original_text, created_at
        FROM campaign_briefs
        WHERE campaign_id = $1 AND org_id = $2
        ORDER BY created_at DESC
        LIMIT 1
        "#,
    )
    .bind(campaign_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn update_brief_status(
    pool: &PgPool,
    brief_id: &str,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE campaign_briefs
        SET status = $1
        WHERE brief_id = $2 AND org_id = $3
        "#,
    )
    .bind(status)
    .bind(brief_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}
