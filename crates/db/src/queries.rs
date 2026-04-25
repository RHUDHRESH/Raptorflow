use crate::models::{
    AgentEssence, Avatar, Campaign, CampaignBrief, CampaignMove, CampaignTask, CapabilityArtifact,
    CapabilityDefinition, CapabilityRun, CompetitorSnapshot, ContentStrategy, CouncilAgentPosition,
    CouncilSession, DailyWin, FoundationScan, FoundationSection, FoundationSnapshot,
    FoundationVersion, GeneratedContent, HarnessContextPack, HarnessRun, HarnessStep,
    MuseConversation, MuseMessage, Nudge, OrgUser, Organization, ReplanSession, Ripple, RippleEdge,
    Subscription,
};
use sqlx::{PgPool, Row};

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

    rows.iter()
        .map(|row| {
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
        })
        .collect()
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

    rows.iter()
        .map(|row| {
            Ok(OrgUser {
                org_user_id: row.get("org_user_id"),
                org_id: row.get("org_id"),
                clerk_user_id: row.get("clerk_user_id"),
                email: row.get("email"),
                role: row.get("role"),
                created_at: row.get("created_at"),
            })
        })
        .collect()
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

    sqlx::query(
        r#"
        INSERT INTO org_members (member_id, org_id, user_id, role)
        VALUES ($1, $2, $3, $4::org_member_role)
        ON CONFLICT (org_id, user_id) DO UPDATE SET
            role = EXCLUDED.role,
            updated_at = NOW()
        "#,
    )
    .bind(uuid::Uuid::new_v4())
    .bind(org_id)
    .bind(clerk_user_id)
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

    rows.iter()
        .map(|row| {
            Ok(FoundationSnapshot {
                foundation_snapshot_id: row.get("foundation_snapshot_id"),
                org_id: row.get("org_id"),
                foundation_version: row.get("foundation_version"),
                sections: row.get("sections"),
                source: row.get("source"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            })
        })
        .collect()
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

pub async fn get_subscription_status(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<String, sqlx::Error> {
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

    Ok(row
        .map(|r| r.get("status"))
        .unwrap_or_else(|| "none".to_string()))
}

pub async fn get_latest_subscription(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Option<Subscription>, sqlx::Error> {
    let row = sqlx::query_as::<_, Subscription>(
        r#"
        SELECT subscription_id, org_id, provider, status, plan_amount_inr,
               plan_tier, referral_code, discount_percent, grace_period_ends_at,
               created_at, updated_at
        FROM subscriptions
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;

    Ok(row)
}

pub async fn create_subscription(
    pool: &PgPool,
    subscription_id: uuid::Uuid,
    org_id: uuid::Uuid,
    status: &str,
    plan_tier: &str,
    plan_amount_inr: i32,
    referral_code: Option<&str>,
    discount_percent: i32,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO subscriptions (
            subscription_id,
            org_id,
            provider,
            status,
            plan_amount_inr,
            plan_tier,
            referral_code,
            discount_percent
        )
        VALUES ($1, $2, 'referral', $3, $4, $5, $6, $7)
        ON CONFLICT (subscription_id) DO UPDATE SET
            status = EXCLUDED.status,
            plan_amount_inr = EXCLUDED.plan_amount_inr,
            plan_tier = EXCLUDED.plan_tier,
            referral_code = EXCLUDED.referral_code,
            discount_percent = EXCLUDED.discount_percent,
            updated_at = NOW()
        "#,
    )
    .bind(subscription_id)
    .bind(org_id)
    .bind(status)
    .bind(plan_amount_inr)
    .bind(plan_tier)
    .bind(referral_code)
    .bind(discount_percent)
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
               plan_tier, referral_code, discount_percent, grace_period_ends_at,
               created_at, updated_at
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

pub async fn upsert_referral_subscription(
    pool: &PgPool,
    org_id: uuid::Uuid,
    plan_tier: &str,
    referral_code: &str,
) -> Result<(), sqlx::Error> {
    let subscription_id = uuid::Uuid::new_v4();

    create_subscription(
        pool,
        subscription_id,
        org_id,
        "active",
        plan_tier,
        0,
        Some(referral_code),
        100,
    )
    .await
}

pub async fn get_user_referral_code(
    pool: &PgPool,
    clerk_user_id: &str,
) -> Result<Option<String>, sqlx::Error> {
    let row = sqlx::query(
        r#"
        SELECT referral_code
        FROM users
        WHERE clerk_user_id = $1
        ORDER BY updated_at DESC
        LIMIT 1
        "#,
    )
    .bind(clerk_user_id)
    .fetch_optional(pool)
    .await?;

    Ok(row.and_then(|row| {
        row.try_get::<Option<String>, _>("referral_code")
            .ok()
            .flatten()
    }))
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

    rows.iter()
        .map(|row| {
            Ok(FoundationSection {
                org_id: row.get("org_id"),
                section_key: row.get("section_key"),
                value: row.get("value"),
                updated_at: row.get("updated_at"),
            })
        })
        .collect()
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

pub async fn create_competitor_snapshot(
    pool: &PgPool,
    snapshot_id: &str,
    org_id: uuid::Uuid,
    competitor_url: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO competitor_snapshots (snapshot_id, org_id, competitor_url, status, created_at, updated_at)
        VALUES ($1, $2, $3, 'scanning', now(), now())
        "#,
    )
    .bind(snapshot_id)
    .bind(org_id)
    .bind(competitor_url)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_competitor_snapshot(
    pool: &PgPool,
    snapshot_id: &str,
) -> Result<Option<CompetitorSnapshot>, sqlx::Error> {
    let row = sqlx::query_as::<_, CompetitorSnapshot>(
        r#"
        SELECT snapshot_id, org_id, competitor_url, hash, status, scrape_data, created_at, updated_at
        FROM competitor_snapshots
        WHERE snapshot_id = $1
        "#,
    )
    .bind(snapshot_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn get_latest_competitor_snapshot(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Option<CompetitorSnapshot>, sqlx::Error> {
    let row = sqlx::query_as::<_, CompetitorSnapshot>(
        r#"
        SELECT snapshot_id, org_id, competitor_url, hash, status, scrape_data, created_at, updated_at
        FROM competitor_snapshots
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn get_latest_competitor_snapshot_by_url(
    pool: &PgPool,
    org_id: uuid::Uuid,
    competitor_url: &str,
) -> Result<Option<CompetitorSnapshot>, sqlx::Error> {
    let row = sqlx::query_as::<_, CompetitorSnapshot>(
        r#"
        SELECT snapshot_id, org_id, competitor_url, hash, status, scrape_data, created_at, updated_at
        FROM competitor_snapshots
        WHERE org_id = $1 AND competitor_url = $2
        ORDER BY created_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .bind(competitor_url)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn update_competitor_snapshot(
    pool: &PgPool,
    snapshot_id: &str,
    hash: Option<&str>,
    status: &str,
    scrape_data: Option<&serde_json::Value>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE competitor_snapshots
        SET hash = $1, status = $2, scrape_data = $3, updated_at = now()
        WHERE snapshot_id = $4
        "#,
    )
    .bind(hash)
    .bind(status)
    .bind(scrape_data)
    .bind(snapshot_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn create_content_strategy(
    pool: &PgPool,
    strategy_id: &str,
    org_id: uuid::Uuid,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO content_strategy (strategy_id, org_id, territories, pillar_pages, editorial_calendar)
        VALUES ($1, $2, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb)
        "#,
    )
    .bind(strategy_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_content_strategy(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Option<ContentStrategy>, sqlx::Error> {
    let row = sqlx::query_as::<_, ContentStrategy>(
        r#"
        SELECT strategy_id, org_id, territories, pillar_pages, editorial_calendar, created_at, updated_at
        FROM content_strategy
        WHERE org_id = $1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn update_content_strategy_territories(
    pool: &PgPool,
    org_id: uuid::Uuid,
    territories: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE content_strategy
        SET territories = $1, updated_at = now()
        WHERE org_id = $2
        "#,
    )
    .bind(territories)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_content_strategy_pillar_pages(
    pool: &PgPool,
    org_id: uuid::Uuid,
    pillar_pages: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE content_strategy
        SET pillar_pages = $1, updated_at = now()
        WHERE org_id = $2
        "#,
    )
    .bind(pillar_pages)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_content_strategy_calendar(
    pool: &PgPool,
    org_id: uuid::Uuid,
    editorial_calendar: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE content_strategy
        SET editorial_calendar = $1, updated_at = now()
        WHERE org_id = $2
        "#,
    )
    .bind(editorial_calendar)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn create_foundation_version(
    pool: &PgPool,
    version_id: &str,
    org_id: uuid::Uuid,
    foundation_version: i32,
    change_description: Option<&str>,
    changed_fields: &serde_json::Value,
    previous_values: &serde_json::Value,
    impact_assessment: Option<&serde_json::Value>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO foundation_versions (version_id, org_id, foundation_version, change_description, changed_fields, previous_values, impact_assessment, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, now())
        "#,
    )
    .bind(version_id)
    .bind(org_id)
    .bind(foundation_version)
    .bind(change_description)
    .bind(changed_fields)
    .bind(previous_values)
    .bind(impact_assessment)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_foundation_versions(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<FoundationVersion>, sqlx::Error> {
    let rows = sqlx::query_as::<_, FoundationVersion>(
        r#"
        SELECT version_id, org_id, foundation_version, change_description, changed_fields, previous_values, impact_assessment, created_at
        FROM foundation_versions
        WHERE org_id = $1
        ORDER BY foundation_version DESC
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_latest_foundation_version(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Option<FoundationVersion>, sqlx::Error> {
    let row = sqlx::query_as::<_, FoundationVersion>(
        r#"
        SELECT version_id, org_id, foundation_version, change_description, changed_fields, previous_values, impact_assessment, created_at
        FROM foundation_versions
        WHERE org_id = $1
        ORDER BY foundation_version DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
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

#[allow(clippy::too_many_arguments)]
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

pub async fn list_avatars(pool: &PgPool, org_id: uuid::Uuid) -> Result<Vec<Avatar>, sqlx::Error> {
    let rows = sqlx::query_as::<_, Avatar>(
        r#"
        SELECT avatar_id, org_id, avatar_key, display_name, role, archetype,
               personality, system_prompt, tool_permissions, memory_scope,
               is_active, created_at, updated_at
        FROM avatars
        WHERE org_id = $1 AND is_active = TRUE
        ORDER BY avatar_key ASC
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_avatar(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
) -> Result<Option<Avatar>, sqlx::Error> {
    let row = sqlx::query_as::<_, Avatar>(
        r#"
        SELECT avatar_id, org_id, avatar_key, display_name, role, archetype,
               personality, system_prompt, tool_permissions, memory_scope,
               is_active, created_at, updated_at
        FROM avatars
        WHERE avatar_id = $1 AND org_id = $2
        "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn get_avatar_by_key(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_key: &str,
) -> Result<Option<Avatar>, sqlx::Error> {
    let row = sqlx::query_as::<_, Avatar>(
        r#"
        SELECT avatar_id, org_id, avatar_key, display_name, role, archetype,
               personality, system_prompt, tool_permissions, memory_scope,
               is_active, created_at, updated_at
        FROM avatars
        WHERE org_id = $1 AND avatar_key = $2 AND is_active = TRUE
        "#,
    )
    .bind(org_id)
    .bind(avatar_key)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

#[allow(clippy::too_many_arguments)]
pub async fn create_avatar(
    pool: &PgPool,
    avatar_id: &str,
    org_id: uuid::Uuid,
    avatar_key: &str,
    display_name: &str,
    role: &str,
    archetype: &str,
    personality: &serde_json::Value,
    system_prompt: &str,
    tool_permissions: &serde_json::Value,
    memory_scope: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatars (avatar_id, org_id, avatar_key, display_name, role, archetype,
                            personality, system_prompt, tool_permissions, memory_scope)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .bind(avatar_key)
    .bind(display_name)
    .bind(role)
    .bind(archetype)
    .bind(personality)
    .bind(system_prompt)
    .bind(tool_permissions)
    .bind(memory_scope)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_avatar(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
    display_name: Option<&str>,
    personality: Option<&serde_json::Value>,
    system_prompt: Option<&str>,
    tool_permissions: Option<&serde_json::Value>,
    is_active: Option<bool>,
) -> Result<(), sqlx::Error> {
    let current = get_avatar(pool, org_id, avatar_id).await?;
    match current {
        Some(avatar) => {
            sqlx::query(
                r#"
                UPDATE avatars
                SET display_name = $1,
                    personality = $2,
                    system_prompt = $3,
                    tool_permissions = $4,
                    is_active = $5,
                    updated_at = now()
                WHERE avatar_id = $6 AND org_id = $7
                "#,
            )
            .bind(display_name.unwrap_or(&avatar.display_name))
            .bind(personality.unwrap_or(&avatar.personality))
            .bind(system_prompt.unwrap_or(&avatar.system_prompt))
            .bind(tool_permissions.unwrap_or(&avatar.tool_permissions))
            .bind(is_active.unwrap_or(avatar.is_active))
            .bind(avatar_id)
            .bind(org_id)
            .execute(pool)
            .await?;
            Ok(())
        }
        None => Err(sqlx::Error::RowNotFound),
    }
}

// ─── Capability Definitions ──────────────────────────────────────────────────

pub async fn list_capabilities(pool: &PgPool) -> Result<Vec<CapabilityDefinition>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CapabilityDefinition>(
        r#"
        SELECT capability_id, capability_key, name, domain, description,
               input_schema, output_schema, required_context, allowed_tools,
               artifact_type, evaluator_key, ripple_policy, risk_level,
               is_active, created_at, updated_at
        FROM capability_definitions
        WHERE is_active = TRUE
        ORDER BY domain ASC, capability_key ASC
        "#,
    )
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_capability(
    pool: &PgPool,
    capability_id: &str,
) -> Result<Option<CapabilityDefinition>, sqlx::Error> {
    let row = sqlx::query_as::<_, CapabilityDefinition>(
        r#"
        SELECT capability_id, capability_key, name, domain, description,
               input_schema, output_schema, required_context, allowed_tools,
               artifact_type, evaluator_key, ripple_policy, risk_level,
               is_active, created_at, updated_at
        FROM capability_definitions
        WHERE capability_id = $1
        "#,
    )
    .bind(capability_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn get_capability_by_key(
    pool: &PgPool,
    capability_key: &str,
) -> Result<Option<CapabilityDefinition>, sqlx::Error> {
    let row = sqlx::query_as::<_, CapabilityDefinition>(
        r#"
        SELECT capability_id, capability_key, name, domain, description,
               input_schema, output_schema, required_context, allowed_tools,
               artifact_type, evaluator_key, ripple_policy, risk_level,
               is_active, created_at, updated_at
        FROM capability_definitions
        WHERE capability_key = $1 AND is_active = TRUE
        "#,
    )
    .bind(capability_key)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

#[allow(clippy::too_many_arguments)]
pub async fn upsert_capability_definition(
    pool: &PgPool,
    capability_id: &str,
    capability_key: &str,
    name: &str,
    domain: &str,
    description: &str,
    input_schema: &serde_json::Value,
    output_schema: &serde_json::Value,
    required_context: &serde_json::Value,
    allowed_tools: &serde_json::Value,
    artifact_type: &str,
    evaluator_key: &str,
    ripple_policy: &serde_json::Value,
    risk_level: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO capability_definitions (
            capability_id, capability_key, name, domain, description,
            input_schema, output_schema, required_context, allowed_tools,
            artifact_type, evaluator_key, ripple_policy, risk_level
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        ON CONFLICT (capability_key) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            input_schema = EXCLUDED.input_schema,
            output_schema = EXCLUDED.output_schema,
            required_context = EXCLUDED.required_context,
            allowed_tools = EXCLUDED.allowed_tools,
            artifact_type = EXCLUDED.artifact_type,
            evaluator_key = EXCLUDED.evaluator_key,
            ripple_policy = EXCLUDED.ripple_policy,
            risk_level = EXCLUDED.risk_level,
            updated_at = now()
        "#,
    )
    .bind(capability_id)
    .bind(capability_key)
    .bind(name)
    .bind(domain)
    .bind(description)
    .bind(input_schema)
    .bind(output_schema)
    .bind(required_context)
    .bind(allowed_tools)
    .bind(artifact_type)
    .bind(evaluator_key)
    .bind(ripple_policy)
    .bind(risk_level)
    .execute(pool)
    .await?;
    Ok(())
}

// ─── Avatar Capability Grants ────────────────────────────────────────────────

pub async fn list_avatar_capabilities(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
) -> Result<Vec<CapabilityDefinition>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CapabilityDefinition>(
        r#"
        SELECT cd.capability_id, cd.capability_key, cd.name, cd.domain, cd.description,
               cd.input_schema, cd.output_schema, cd.required_context, cd.allowed_tools,
               cd.artifact_type, cd.evaluator_key, cd.ripple_policy, cd.risk_level,
               cd.is_active, cd.created_at, cd.updated_at
        FROM capability_definitions cd
        INNER JOIN avatar_capability_grants acg
            ON cd.capability_id = acg.capability_id
        WHERE acg.org_id = $1 AND acg.avatar_id = $2 AND acg.is_enabled = TRUE AND cd.is_active = TRUE
        ORDER BY cd.domain ASC, cd.capability_key ASC
        "#,
    )
    .bind(org_id)
    .bind(avatar_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn grant_capability_to_avatar(
    pool: &PgPool,
    grant_id: &str,
    org_id: uuid::Uuid,
    avatar_id: &str,
    capability_id: &str,
    grant_scope: &str,
    constraints: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_capability_grants (
            grant_id, org_id, avatar_id, capability_id, grant_scope, constraints
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (org_id, avatar_id, capability_id) DO UPDATE SET
            grant_scope = EXCLUDED.grant_scope,
            constraints = EXCLUDED.constraints,
            is_enabled = TRUE,
            updated_at = now()
        "#,
    )
    .bind(grant_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(capability_id)
    .bind(grant_scope)
    .bind(constraints)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn revoke_capability_from_avatar(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
    capability_id: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE avatar_capability_grants
        SET is_enabled = FALSE, updated_at = now()
        WHERE org_id = $1 AND avatar_id = $2 AND capability_id = $3 AND is_enabled = TRUE
        "#,
    )
    .bind(org_id)
    .bind(avatar_id)
    .bind(capability_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn check_avatar_capability_grant(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
    capability_id: &str,
) -> Result<bool, sqlx::Error> {
    let row: Option<(bool,)> = sqlx::query_as(
        r#"
        SELECT TRUE as enabled
        FROM avatar_capability_grants
        WHERE org_id = $1 AND avatar_id = $2 AND capability_id = $3 AND is_enabled = TRUE
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .bind(avatar_id)
    .bind(capability_id)
    .fetch_optional(pool)
    .await?;
    Ok(row.is_some())
}

// ─── Harness Context Packs ───────────────────────────────────────────────────

#[allow(clippy::too_many_arguments)]
pub async fn create_context_pack(
    pool: &PgPool,
    context_pack_id: &str,
    org_id: uuid::Uuid,
    run_id: Option<&str>,
    capability_id: Option<&str>,
    avatar_id: Option<&str>,
    scope: &str,
    token_budget: i32,
    foundation_context: &serde_json::Value,
    intel_context: &serde_json::Value,
    campaign_context: &serde_json::Value,
    office_context: &serde_json::Value,
    ripple_context: &serde_json::Value,
    compressed_context: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO harness_context_packs (
            context_pack_id, org_id, run_id, capability_id, avatar_id,
            scope, token_budget, foundation_context, intel_context,
            campaign_context, office_context, ripple_context, compressed_context
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        "#,
    )
    .bind(context_pack_id)
    .bind(org_id)
    .bind(run_id)
    .bind(capability_id)
    .bind(avatar_id)
    .bind(scope)
    .bind(token_budget)
    .bind(foundation_context)
    .bind(intel_context)
    .bind(campaign_context)
    .bind(office_context)
    .bind(ripple_context)
    .bind(compressed_context)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_context_pack(
    pool: &PgPool,
    org_id: uuid::Uuid,
    context_pack_id: &str,
) -> Result<Option<HarnessContextPack>, sqlx::Error> {
    let row = sqlx::query_as::<_, HarnessContextPack>(
        r#"
        SELECT context_pack_id, org_id, run_id, capability_id, avatar_id,
               scope, token_budget, foundation_context, intel_context,
               campaign_context, office_context, ripple_context, compressed_context, created_at
        FROM harness_context_packs
        WHERE context_pack_id = $1 AND org_id = $2
        "#,
    )
    .bind(context_pack_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

// ─── Capability Runs ─────────────────────────────────────────────────────────

pub async fn create_capability_run(
    pool: &PgPool,
    capability_run_id: &str,
    org_id: uuid::Uuid,
    harness_run_id: Option<&str>,
    harness_step_id: Option<&str>,
    avatar_id: Option<&str>,
    capability_id: &str,
    context_pack_id: Option<&str>,
    input: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO capability_runs (
            capability_run_id, org_id, harness_run_id, harness_step_id,
            avatar_id, capability_id, context_pack_id, status, input
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'queued', $8)
        "#,
    )
    .bind(capability_run_id)
    .bind(org_id)
    .bind(harness_run_id)
    .bind(harness_step_id)
    .bind(avatar_id)
    .bind(capability_id)
    .bind(context_pack_id)
    .bind(input)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_capability_run_status(
    pool: &PgPool,
    org_id: uuid::Uuid,
    capability_run_id: &str,
    status: &str,
    output: Option<&serde_json::Value>,
    error_message: Option<&str>,
    model_id: Option<&str>,
    token_usage: Option<&serde_json::Value>,
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
        UPDATE capability_runs
        SET status = $3,
            output = COALESCE($4, output),
            error_message = COALESCE($5, error_message),
            model_id = COALESCE($6, model_id),
            token_usage = COALESCE($7, token_usage),
            started_at = COALESCE($8, started_at),
            completed_at = COALESCE($9, completed_at),
            updated_at = now()
        WHERE capability_run_id = $1 AND org_id = $2
        "#,
    )
    .bind(capability_run_id)
    .bind(org_id)
    .bind(status)
    .bind(output)
    .bind(error_message)
    .bind(model_id)
    .bind(token_usage)
    .bind(started)
    .bind(completed)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_capability_runs(
    pool: &PgPool,
    org_id: uuid::Uuid,
    limit: i64,
) -> Result<Vec<CapabilityRun>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CapabilityRun>(
        r#"
        SELECT capability_run_id, org_id, harness_run_id, harness_step_id,
               avatar_id, capability_id, context_pack_id, status, input, output,
               error_message, model_id, token_usage, started_at, completed_at,
               created_at, updated_at
        FROM capability_runs
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        "#,
    )
    .bind(org_id)
    .bind(limit)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn get_capability_run(
    pool: &PgPool,
    org_id: uuid::Uuid,
    capability_run_id: &str,
) -> Result<Option<CapabilityRun>, sqlx::Error> {
    let row = sqlx::query_as::<_, CapabilityRun>(
        r#"
        SELECT capability_run_id, org_id, harness_run_id, harness_step_id,
               avatar_id, capability_id, context_pack_id, status, input, output,
               error_message, model_id, token_usage, started_at, completed_at,
               created_at, updated_at
        FROM capability_runs
        WHERE capability_run_id = $1 AND org_id = $2
        "#,
    )
    .bind(capability_run_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

// ─── Capability Artifacts ────────────────────────────────────────────────────

pub async fn create_capability_artifact(
    pool: &PgPool,
    artifact_id: &str,
    org_id: uuid::Uuid,
    capability_run_id: Option<&str>,
    harness_run_id: Option<&str>,
    avatar_id: Option<&str>,
    capability_id: Option<&str>,
    artifact_type: &str,
    title: &str,
    body: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO capability_artifacts (
            artifact_id, org_id, capability_run_id, harness_run_id,
            avatar_id, capability_id, artifact_type, title, body
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        "#,
    )
    .bind(artifact_id)
    .bind(org_id)
    .bind(capability_run_id)
    .bind(harness_run_id)
    .bind(avatar_id)
    .bind(capability_id)
    .bind(artifact_type)
    .bind(title)
    .bind(body)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_capability_artifact(
    pool: &PgPool,
    org_id: uuid::Uuid,
    artifact_id: &str,
) -> Result<Option<CapabilityArtifact>, sqlx::Error> {
    let row = sqlx::query_as::<_, CapabilityArtifact>(
        r#"
        SELECT artifact_id, org_id, capability_run_id, harness_run_id,
               avatar_id, capability_id, artifact_type, title, body, status,
               version, evaluation, created_at, updated_at
        FROM capability_artifacts
        WHERE artifact_id = $1 AND org_id = $2
        "#,
    )
    .bind(artifact_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn list_artifacts(
    pool: &PgPool,
    org_id: uuid::Uuid,
    artifact_type: Option<&str>,
    status: Option<&str>,
    limit: i64,
) -> Result<Vec<CapabilityArtifact>, sqlx::Error> {
    let rows = if let (Some(at), Some(st)) = (artifact_type, status) {
        sqlx::query_as::<_, CapabilityArtifact>(
            r#"
            SELECT artifact_id, org_id, capability_run_id, harness_run_id,
                   avatar_id, capability_id, artifact_type, title, body, status,
                   version, evaluation, created_at, updated_at
            FROM capability_artifacts
            WHERE org_id = $1 AND artifact_type = $2 AND status = $3
            ORDER BY created_at DESC
            LIMIT $4
            "#,
        )
        .bind(org_id)
        .bind(at)
        .bind(st)
        .bind(limit)
        .fetch_all(pool)
        .await?
    } else if let Some(at) = artifact_type {
        sqlx::query_as::<_, CapabilityArtifact>(
            r#"
            SELECT artifact_id, org_id, capability_run_id, harness_run_id,
                   avatar_id, capability_id, artifact_type, title, body, status,
                   version, evaluation, created_at, updated_at
            FROM capability_artifacts
            WHERE org_id = $1 AND artifact_type = $2
            ORDER BY created_at DESC
            LIMIT $3
            "#,
        )
        .bind(org_id)
        .bind(at)
        .bind(limit)
        .fetch_all(pool)
        .await?
    } else {
        sqlx::query_as::<_, CapabilityArtifact>(
            r#"
            SELECT artifact_id, org_id, capability_run_id, harness_run_id,
                   avatar_id, capability_id, artifact_type, title, body, status,
                   version, evaluation, created_at, updated_at
            FROM capability_artifacts
            WHERE org_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            "#,
        )
        .bind(org_id)
        .bind(limit)
        .fetch_all(pool)
        .await?
    };
    Ok(rows)
}

pub async fn create_artifact_version(
    pool: &PgPool,
    artifact_version_id: &str,
    artifact_id: &str,
    org_id: uuid::Uuid,
    version: i32,
    body: &serde_json::Value,
    change_reason: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO artifact_versions (
            artifact_version_id, artifact_id, org_id, version, body, change_reason
        ) VALUES ($1, $2, $3, $4, $5, $6)
        "#,
    )
    .bind(artifact_version_id)
    .bind(artifact_id)
    .bind(org_id)
    .bind(version)
    .bind(body)
    .bind(change_reason)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn link_artifact_to_ripple(
    pool: &PgPool,
    link_id: &str,
    org_id: uuid::Uuid,
    artifact_id: &str,
    ripple_id: &str,
    link_type: &str,
    salience: f64,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO artifact_ripple_links (
            link_id, org_id, artifact_id, ripple_id, link_type, salience
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (artifact_id, ripple_id, link_type) DO UPDATE SET
            salience = EXCLUDED.salience
        "#,
    )
    .bind(link_id)
    .bind(org_id)
    .bind(artifact_id)
    .bind(ripple_id)
    .bind(link_type)
    .bind(salience)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn soft_delete_avatar(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE avatars
        SET is_active = FALSE, updated_at = now()
        WHERE avatar_id = $1 AND org_id = $2 AND is_active = TRUE
        "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn ensure_default_avatars(
    pool: &PgPool,
    org_id: uuid::Uuid,
) -> Result<Vec<Avatar>, sqlx::Error> {
    let defaults = vec![
        ("strategist", "Strategist", "strategy", "market_war_room"),
        (
            "growth_operator",
            "Growth Operator",
            "growth",
            "demand_generation",
        ),
        ("copywriter", "Copywriter", "copy", "content_studio"),
        ("researcher", "Researcher", "research", "intel_station"),
        ("analyst", "Analyst", "analysis", "data_hub"),
        (
            "creative_director",
            "Creative Director",
            "creative",
            "brand_voice",
        ),
        (
            "proof_collector",
            "Proof Collector",
            "proof",
            "social_proof",
        ),
    ];

    for (key, name, role, archetype) in defaults {
        let existing = get_avatar_by_key(pool, org_id, key).await?;
        if existing.is_none() {
            let avatar_id = uuid::Uuid::new_v4().to_string();
            let personality = serde_json::json!({
                "tone": "direct",
                "risk_tolerance": "medium",
                "creativity": 0.7,
                "skepticism": 0.6,
                "detail_level": "high"
            });
            let tool_permissions = serde_json::json!({
                "can_use_bedrock": true,
                "can_read_foundation": true,
                "can_read_intel": true,
                "can_write_artifacts": false,
                "can_trigger_jobs": false,
                "requires_approval_for_external_actions": true
            });
            create_avatar(
                pool,
                &avatar_id,
                org_id,
                key,
                name,
                role,
                archetype,
                &personality,
                "",
                &tool_permissions,
                "org",
            )
            .await?;
        }
    }

    list_avatars(pool, org_id).await
}

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
