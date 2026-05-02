use super::common::*;

pub async fn get_ripples(pool: &PgPool) -> Result<Vec<Ripple>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT ripple_id, org_id, agent_id, campaign_id, scope, hierarchy_level, memory_class,
               source, trigger_text, raw_text, summary_text, salience, confidence,
               importance_band, prediction_json, created_at
        FROM ripples
        WHERE org_id = app.current_org_id()
        ORDER BY created_at DESC
        "#,
    )
    .fetch_all(pool)
    .await?;

    rows.iter()
        .map(|row| {
            Ok(Ripple {
                ripple_id: row.get("ripple_id"),
                org_id: row.get("org_id"),
                agent_id: row.get("agent_id"),
                campaign_id: row.get("campaign_id"),
                scope: row.get("scope"),
                hierarchy_level: row.get("hierarchy_level"),
                memory_class: row.get("memory_class"),
                source: row.get("source"),
                trigger_text: row.get("trigger_text"),
                raw_text: row.get("raw_text"),
                summary_text: row.get("summary_text"),
                embedding: None,
                simhash: None,
                emotion_vector: None,
                salience: row.get("salience"),
                confidence: row.get("confidence"),
                importance_band: row.get("importance_band"),
                prediction_json: row.get("prediction_json"),
                created_at: row.get("created_at"),
            })
        })
        .collect()
}

#[allow(clippy::too_many_arguments)]
pub async fn create_ripple(
    pool: &PgPool,
    ripple_id: &str,
    org_id: uuid::Uuid,
    agent_id: uuid::Uuid,
    scope: &str,
    hierarchy_level: i32,
    memory_class: &str,
    source: &str,
    trigger_text: &str,
    raw_text: &str,
    summary_text: &str,
    salience: f64,
    confidence: f64,
    importance_band: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO ripples (ripple_id, org_id, agent_id, scope, hierarchy_level,
                            memory_class, source, trigger_text, raw_text, summary_text,
                            salience, confidence, importance_band)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        "#,
    )
    .bind(ripple_id)
    .bind(org_id)
    .bind(agent_id)
    .bind(scope)
    .bind(hierarchy_level)
    .bind(memory_class)
    .bind(source)
    .bind(trigger_text)
    .bind(raw_text)
    .bind(summary_text)
    .bind(salience)
    .bind(confidence)
    .bind(importance_band)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_ripple_edges(pool: &PgPool) -> Result<Vec<RippleEdge>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT edge_id, org_id, source_ripple_id, target_ripple_id, edge_type, weight, created_at
        FROM ripple_edges
        WHERE org_id = app.current_org_id()
        "#,
    )
    .fetch_all(pool)
    .await?;

    rows.iter()
        .map(|row| {
            Ok(RippleEdge {
                edge_id: row.get("edge_id"),
                org_id: row.get("org_id"),
                source_ripple_id: row.get("source_ripple_id"),
                target_ripple_id: row.get("target_ripple_id"),
                edge_type: row.get("edge_type"),
                weight: row.get("weight"),
                co_activation_count: 0,
                last_co_activated_at: None,
                created_at: row.get("created_at"),
            })
        })
        .collect()
}

pub async fn create_ripple_edge(
    pool: &PgPool,
    edge_id: uuid::Uuid,
    org_id: uuid::Uuid,
    source_ripple_id: &str,
    target_ripple_id: &str,
    edge_type: &str,
    weight: f64,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO ripple_edges (edge_id, org_id, source_ripple_id, target_ripple_id, edge_type, weight)
        VALUES ($1, $2, $3, $4, $5, $6)
        "#,
    )
    .bind(edge_id)
    .bind(org_id)
    .bind(source_ripple_id)
    .bind(target_ripple_id)
    .bind(edge_type)
    .bind(weight)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_agent_essences(pool: &PgPool) -> Result<Vec<AgentEssence>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT agent_id, org_id, avatar_key, display_name, essence_core,
               ego_baseline, ego_state, ego_multipliers, ego_decay_rate,
               skill_atoms, persona_vector,
               reflection_vfe, reflection_mean, reflection_std, reflection_cooldown,
               active_session_id, last_active_at,
               created_at, updated_at
        FROM agent_essences
        WHERE org_id = app.current_org_id()
        "#,
    )
    .fetch_all(pool)
    .await?;

    rows.iter()
        .map(|row| {
            Ok(AgentEssence {
                agent_id: row.get("agent_id"),
                org_id: row.get("org_id"),
                avatar_key: row.get("avatar_key"),
                display_name: row.get("display_name"),
                essence_core: row.get("essence_core"),
                ego_baseline: row.get("ego_baseline"),
                ego_state: row.get("ego_state"),
                ego_multipliers: row.get("ego_multipliers"),
                ego_decay_rate: row.get("ego_decay_rate"),
                skill_atoms: row.get("skill_atoms"),
                persona_vector: row.get("persona_vector"),
                reflection_vfe: row.get("reflection_vfe"),
                reflection_mean: row.get("reflection_mean"),
                reflection_std: row.get("reflection_std"),
                reflection_cooldown: row.get("reflection_cooldown"),
                active_session_id: row.get("active_session_id"),
                last_active_at: row.get("last_active_at"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            })
        })
        .collect()
}
