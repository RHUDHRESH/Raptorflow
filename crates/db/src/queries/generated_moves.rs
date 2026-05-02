use super::common::*;

pub struct GeneratedCampaignMoveInsert {
    pub move_id: String,
    pub content_id: String,
    pub move_type: String,
    pub sequence_number: i32,
    pub content_body: serde_json::Value,
}

pub struct GeneratedCampaignMoveCreated {
    pub move_id: String,
    pub move_type: String,
    pub sequence_number: i32,
    pub content_body: serde_json::Value,
}

pub async fn create_generated_campaign_moves_transactional(
    pool: &PgPool,
    org_id: uuid::Uuid,
    campaign_id: &str,
    moves: Vec<GeneratedCampaignMoveInsert>,
) -> Result<Vec<GeneratedCampaignMoveCreated>, sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("SET LOCAL app.current_org_id = $1")
        .bind(org_id)
        .execute(&mut *tx)
        .await?;

    let mut results = Vec::with_capacity(moves.len());

    for m in moves {
        sqlx::query(
            r#"
            INSERT INTO campaign_moves (move_id, campaign_id, org_id, move_type, sequence_number, status, created_at)
            VALUES ($1, $2, $3, $4, $5, 'planned', now())
            "#,
        )
        .bind(&m.move_id)
        .bind(campaign_id)
        .bind(org_id)
        .bind(&m.move_type)
        .bind(m.sequence_number)
        .execute(&mut *tx)
        .await?;

        sqlx::query(
            r#"
            INSERT INTO generated_content (content_id, org_id, campaign_id, task_id, content_type, status, body)
            VALUES ($1, $2, $3, NULL, 'move_generation', 'generated', $4)
            "#,
        )
        .bind(&m.content_id)
        .bind(org_id)
        .bind(campaign_id)
        .bind(&m.content_body)
        .execute(&mut *tx)
        .await?;

        results.push(GeneratedCampaignMoveCreated {
            move_id: m.move_id,
            move_type: m.move_type,
            sequence_number: m.sequence_number,
            content_body: m.content_body,
        });
    }

    tx.commit().await?;
    Ok(results)
}
