use sqlx::{PgPool, Row};
use crate::models::{Organization, OrgUser, FoundationSnapshot, Ripple, RippleEdge, AgentEssence, Subscription, FoundationSection, FoundationScan};

pub async fn get_organizations(pool: &PgPool) -> Result<Vec<Organization>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT org_id, name, subscription_status, foundation_version,
               foundation_complete, foundation_json, foundation_completed_at,
               created_at, updated_at
        FROM organizations
        WHERE org_id = app.current_org_id()
        "#,
    )
    .fetch_all(pool)
    .await?;

    rows.iter().map(|row| {
        Ok(Organization {
            org_id: row.get("org_id"),
            name: row.get("name"),
            subscription_status: row.get("subscription_status"),
            foundation_version: row.get("foundation_version"),
            foundation_complete: row.get("foundation_complete"),
            foundation_json: row.get("foundation_json"),
            foundation_completed_at: row.get("foundation_completed_at"),
            created_at: row.get("created_at"),
            updated_at: row.get("updated_at"),
        })
    }).collect()
}

pub async fn get_org_users(pool: &PgPool) -> Result<Vec<OrgUser>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT org_user_id, org_id, clerk_user_id, email, role, created_at
        FROM org_users
        WHERE org_id = app.current_org_id()
        "#,
    )
    .fetch_all(pool)
    .await?;

    rows.iter().map(|row| {
        Ok(OrgUser {
            org_user_id: row.get("org_user_id"),
            org_id: row.get("org_id"),
            clerk_user_id: row.get("clerk_user_id"),
            email: row.get("email"),
            role: row.get("role"),
            created_at: row.get("created_at"),
        })
    }).collect()
}

pub async fn create_organization(
    pool: &PgPool,
    org_id: uuid::Uuid,
    name: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO organizations (org_id, name)
        VALUES ($1, $2)
        ON CONFLICT (org_id) DO UPDATE SET name = EXCLUDED.name
        "#,
    )
    .bind(org_id)
    .bind(name)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn create_org_user(
    pool: &PgPool,
    org_user_id: uuid::Uuid,
    org_id: uuid::Uuid,
    clerk_user_id: &str,
    email: &str,
    role: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO org_users (org_user_id, org_id, clerk_user_id, email, role)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (org_id, clerk_user_id) DO UPDATE SET email = EXCLUDED.email
        "#,
    )
    .bind(org_user_id)
    .bind(org_id)
    .bind(clerk_user_id)
    .bind(email)
    .bind(role)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_foundation_snapshots(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<FoundationSnapshot>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT foundation_snapshot_id, org_id, foundation_version, sections, source, created_at, updated_at
        FROM foundation_snapshots
        WHERE org_id = $1
        ORDER BY foundation_version DESC
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;

    rows.iter().map(|row| {
        Ok(FoundationSnapshot {
            foundation_snapshot_id: row.get("foundation_snapshot_id"),
            org_id: row.get("org_id"),
            foundation_version: row.get("foundation_version"),
            sections: row.get("sections"),
            source: row.get("source"),
            created_at: row.get("created_at"),
            updated_at: row.get("updated_at"),
        })
    }).collect()
}

pub async fn create_foundation_snapshot(
    pool: &PgPool,
    snapshot_id: &str,
    org_id: uuid::Uuid,
    version: i32,
    sections: &serde_json::Value,
    source: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO foundation_snapshots (foundation_snapshot_id, org_id, foundation_version, sections, source)
        VALUES ($1, $2, $3, $4, $5)
        "#,
    )
    .bind(snapshot_id)
    .bind(org_id)
    .bind(version)
    .bind(sections)
    .bind(source)
    .execute(pool)
    .await?;
    Ok(())
}

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

    rows.iter().map(|row| {
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
    }).collect()
}

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

    rows.iter().map(|row| {
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
    }).collect()
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

    rows.iter().map(|row| {
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
    }).collect()
}

pub async fn get_subscription_status(pool: &PgPool, org_id: uuid::Uuid) -> Result<String, sqlx::Error> {
    let row = sqlx::query(
        r#"
        SELECT status FROM subscriptions
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;

    Ok(row.map(|r| r.get("status")).unwrap_or_else(|| "none".to_string()))
}

pub async fn create_subscription(
    pool: &PgPool,
    subscription_id: uuid::Uuid,
    org_id: uuid::Uuid,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO subscriptions (subscription_id, org_id, status)
        VALUES ($1, $2, $3)
        "#,
    )
    .bind(subscription_id)
    .bind(org_id)
    .bind(status)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_subscription_status(
    pool: &PgPool,
    subscription_id: &str,
    status: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE subscriptions
        SET status = $1, updated_at = NOW()
        WHERE subscription_id::text = $2
        "#,
    )
    .bind(status)
    .bind(subscription_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_subscription_by_razorpay_id(
    pool: &PgPool,
    org_id: uuid::Uuid,
    subscription_id_str: &str,
) -> Result<Option<Subscription>, sqlx::Error> {
    let row = sqlx::query_as::<_, Subscription>(
        r#"
        SELECT subscription_id, org_id, provider, status, plan_amount_inr,
               grace_period_ends_at, created_at, updated_at
        FROM subscriptions
        WHERE org_id = $1 AND subscription_id::text = $2
        "#,
    )
    .bind(org_id)
    .bind(subscription_id_str)
    .fetch_optional(pool)
    .await?;

    Ok(row)
}

pub async fn create_payment_event(
    pool: &PgPool,
    event_id: uuid::Uuid,
    org_id: uuid::Uuid,
    razorpay_event_id: &str,
    event_type: &str,
    payment_id: Option<&str>,
    order_id: Option<&str>,
    amount: Option<i64>,
    currency: Option<&str>,
    status: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO payment_events (event_id, org_id, razorpay_event_id, event_type, payment_id, order_id, amount, currency, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (razorpay_event_id) DO NOTHING
        "#,
    )
    .bind(event_id)
    .bind(org_id)
    .bind(razorpay_event_id)
    .bind(event_type)
    .bind(payment_id)
    .bind(order_id)
    .bind(amount)
    .bind(currency)
    .bind(status)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn upsert_foundation_section(
    pool: &PgPool,
    org_id: uuid::Uuid,
    section_key: &str,
    value: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO foundation_sections (org_id, section_key, value, updated_at)
        VALUES ($1, $2, $3, now())
        ON CONFLICT (org_id, section_key)
        DO UPDATE SET value = $3, updated_at = now()
        "#,
    )
    .bind(org_id)
    .bind(section_key)
    .bind(value)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_foundation_sections(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<FoundationSection>, sqlx::Error> {
    let rows = sqlx::query(
        r#"
        SELECT org_id, section_key, value, updated_at
        FROM foundation_sections
        WHERE org_id = $1
        ORDER BY updated_at DESC
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;

    rows.iter().map(|row| {
        Ok(FoundationSection {
            org_id: row.get("org_id"),
            section_key: row.get("section_key"),
            value: row.get("value"),
            updated_at: row.get("updated_at"),
        })
    }).collect()
}

pub async fn create_foundation_scan(
    pool: &PgPool,
    scan_id: &str,
    org_id: uuid::Uuid,
    url: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(scan_id)
    .bind(org_id)
    .bind(url)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_foundation_scan(
    pool: &PgPool,
    scan_id: &str,
) -> Result<Option<FoundationScan>, sqlx::Error> {
    let row = sqlx::query_as::<_, FoundationScan>(
        r#"
        SELECT scan_id, org_id, url, status, quick_scan_data, deep_scan_data, started_at, completed_at
        FROM foundation_scans
        WHERE scan_id = $1
        "#,
    )
    .bind(scan_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn get_latest_foundation_scan(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Option<FoundationScan>, sqlx::Error> {
    let row = sqlx::query_as::<_, FoundationScan>(
        r#"
        SELECT scan_id, org_id, url, status, quick_scan_data, deep_scan_data, started_at, completed_at
        FROM foundation_scans
        WHERE org_id = $1
        ORDER BY started_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn update_foundation_scan(
    pool: &PgPool,
    scan_id: &str,
    status: &str,
    quick_scan_data: Option<&serde_json::Value>,
    deep_scan_data: Option<&serde_json::Value>,
) -> Result<(), sqlx::Error> {
    if status == "complete" || status == "failed" {
        sqlx::query(
            r#"
            UPDATE foundation_scans
            SET status = $1, quick_scan_data = COALESCE($2, quick_scan_data),
                deep_scan_data = COALESCE($3, deep_scan_data), completed_at = now()
            WHERE scan_id = $4
            "#,
        )
        .bind(status)
        .bind(quick_scan_data)
        .bind(deep_scan_data)
        .bind(scan_id)
        .execute(pool)
        .await?;
    } else {
        sqlx::query(
            r#"
            UPDATE foundation_scans
            SET status = $1, quick_scan_data = COALESCE($2, quick_scan_data),
                deep_scan_data = COALESCE($3, deep_scan_data)
            WHERE scan_id = $4
            "#,
        )
        .bind(status)
        .bind(quick_scan_data)
        .bind(deep_scan_data)
        .bind(scan_id)
        .execute(pool)
        .await?;
    }
    Ok(())
}

pub async fn complete_foundation(
    pool: &PgPool,
    org_id: uuid::Uuid,
    foundation_json: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE organizations
        SET foundation_complete = true,
            foundation_json = $2,
            foundation_completed_at = now(),
            foundation_version = foundation_version + 1,
            updated_at = now()
        WHERE org_id = $1
        "#,
    )
    .bind(org_id)
    .bind(foundation_json)
    .execute(pool)
    .await?;
    Ok(())
}
