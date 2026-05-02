use super::common::*;

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
