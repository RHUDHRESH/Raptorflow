use super::common::*;

pub async fn list_council_sessions(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<CouncilSession>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CouncilSession>(
        r#"
        SELECT session_id, org_id, campaign_id, session_type, status, question, total_cost_usd, created_at
        FROM council_sessions
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

pub async fn get_council_session(
    pool: &PgPool,
    session_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<CouncilSession>, sqlx::Error> {
    let row = sqlx::query_as::<_, CouncilSession>(
        r#"
        SELECT session_id, org_id, campaign_id, session_type, status, question, total_cost_usd, created_at
        FROM council_sessions
        WHERE session_id = $1 AND org_id = $2
        "#,
    )
    .bind(session_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn create_council_session(
    pool: &PgPool,
    session_id: &str,
    org_id: uuid::Uuid,
    campaign_id: Option<&str>,
    session_type: &str,
    question: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO council_sessions (session_id, org_id, campaign_id, session_type, status, question)
        VALUES ($1, $2, $3, $4, 'active', $5)
        "#,
    )
    .bind(session_id)
    .bind(org_id)
    .bind(campaign_id)
    .bind(session_type)
    .bind(question)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_council_session_status(
    pool: &PgPool,
    session_id: &str,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE council_sessions
        SET status = $1
        WHERE session_id = $2 AND org_id = $3
        "#,
    )
    .bind(status)
    .bind(session_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_agent_positions(
    pool: &PgPool,
    session_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<CouncilAgentPosition>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CouncilAgentPosition>(
        r#"
        SELECT position_id, org_id, session_id, avatar_key, round_number, content, extracted_ripple_data, created_at
        FROM council_agent_positions
        WHERE session_id = $1 AND org_id = $2
        ORDER BY round_number ASC, created_at ASC
        "#,
    )
    .bind(session_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn create_agent_position(
    pool: &PgPool,
    position_id: &str,
    org_id: uuid::Uuid,
    session_id: &str,
    avatar_key: &str,
    round_number: i32,
    content: &str,
    extracted_ripple_data: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO council_agent_positions (position_id, org_id, session_id, avatar_key, round_number, content, extracted_ripple_data)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        "#,
    )
    .bind(position_id)
    .bind(org_id)
    .bind(session_id)
    .bind(avatar_key)
    .bind(round_number)
    .bind(content)
    .bind(extracted_ripple_data)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_muse_conversations(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<MuseConversation>, sqlx::Error> {
    let rows = sqlx::query_as::<_, MuseConversation>(
        r#"
        SELECT conversation_id, org_id, route, created_at
        FROM muse_conversations
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

pub async fn get_muse_conversation(
    pool: &PgPool,
    conversation_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<MuseConversation>, sqlx::Error> {
    let row = sqlx::query_as::<_, MuseConversation>(
        r#"
        SELECT conversation_id, org_id, route, created_at
        FROM muse_conversations
        WHERE conversation_id = $1 AND org_id = $2
        "#,
    )
    .bind(conversation_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn create_muse_conversation(
    pool: &PgPool,
    conversation_id: &str,
    org_id: uuid::Uuid,
    route: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO muse_conversations (conversation_id, org_id, route)
        VALUES ($1, $2, $3)
        "#,
    )
    .bind(conversation_id)
    .bind(org_id)
    .bind(route)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_muse_messages(
    pool: &PgPool,
    conversation_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<MuseMessage>, sqlx::Error> {
    let rows = sqlx::query_as::<_, MuseMessage>(
        r#"
        SELECT message_id, conversation_id, org_id, role, body, created_at
        FROM muse_messages
        WHERE conversation_id = $1 AND org_id = $2
        ORDER BY created_at ASC
        "#,
    )
    .bind(conversation_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn create_muse_message(
    pool: &PgPool,
    message_id: &str,
    conversation_id: &str,
    org_id: uuid::Uuid,
    role: &str,
    body: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO muse_messages (message_id, conversation_id, org_id, role, body)
        VALUES ($1, $2, $3, $4, $5)
        "#,
    )
    .bind(message_id)
    .bind(conversation_id)
    .bind(org_id)
    .bind(role)
    .bind(body)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_generated_content(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<GeneratedContent>, sqlx::Error> {
    let rows = sqlx::query_as::<_, GeneratedContent>(
        r#"
        SELECT content_id, org_id, campaign_id, task_id, content_type, status, body, created_at
        FROM generated_content
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

pub async fn get_generated_content(
    pool: &PgPool,
    content_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<GeneratedContent>, sqlx::Error> {
    let row = sqlx::query_as::<_, GeneratedContent>(
        r#"
        SELECT content_id, org_id, campaign_id, task_id, content_type, status, body, created_at
        FROM generated_content
        WHERE content_id = $1 AND org_id = $2
        "#,
    )
    .bind(content_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn create_generated_content(
    pool: &PgPool,
    content_id: &str,
    org_id: uuid::Uuid,
    campaign_id: Option<&str>,
    task_id: Option<&str>,
    content_type: &str,
    status: &str,
    body: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO generated_content (content_id, org_id, campaign_id, task_id, content_type, status, body)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        "#,
    )
    .bind(content_id)
    .bind(org_id)
    .bind(campaign_id)
    .bind(task_id)
    .bind(content_type)
    .bind(status)
    .bind(body)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_replan_sessions(
    pool: &PgPool,
    campaign_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<ReplanSession>, sqlx::Error> {
    let rows = sqlx::query_as::<_, ReplanSession>(
        r#"
        SELECT replan_session_id, org_id, campaign_id, trigger_type, status, created_at
        FROM replan_sessions
        WHERE campaign_id = $1 AND org_id = $2
        ORDER BY created_at DESC
        LIMIT 20
        "#,
    )
    .bind(campaign_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_replan_session(
    pool: &PgPool,
    replan_session_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<ReplanSession>, sqlx::Error> {
    let row = sqlx::query_as::<_, ReplanSession>(
        r#"
        SELECT replan_session_id, org_id, campaign_id, trigger_type, status, created_at
        FROM replan_sessions
        WHERE replan_session_id = $1 AND org_id = $2
        "#,
    )
    .bind(replan_session_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn create_replan_session(
    pool: &PgPool,
    replan_session_id: &str,
    org_id: uuid::Uuid,
    campaign_id: &str,
    trigger_type: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO replan_sessions (replan_session_id, org_id, campaign_id, trigger_type, status)
        VALUES ($1, $2, $3, $4, 'queued')
        "#,
    )
    .bind(replan_session_id)
    .bind(org_id)
    .bind(campaign_id)
    .bind(trigger_type)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_replan_session_status(
    pool: &PgPool,
    replan_session_id: &str,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE replan_sessions
        SET status = $1
        WHERE replan_session_id = $2 AND org_id = $3
        "#,
    )
    .bind(status)
    .bind(replan_session_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}
