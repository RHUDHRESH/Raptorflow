use super::common::*;
use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct SnapshotFullResponse {
    pub status: String,
    pub completed_sections: Vec<String>,
    pub missing_sections: Vec<String>,
    pub last_updated_section: Option<String>,
    pub version: i32,
    pub sections: serde_json::Value,
}

const ALL_SECTIONS: [&str; 21] = [
    "company_url",
    "company_info",
    "company_stage",
    "product_catalog",
    "problem_statement",
    "target_audience",
    "secondary_icps",
    "competitors",
    "differentiation",
    "positioning",
    "brand_personality",
    "voice_practice",
    "content_territories",
    "channels",
    "goals",
    "seo_keywords",
    "asset_inventory",
    "frustrations",
    "tools",
    "reference_brands",
    "strategist",
];

fn canonical_section_key(section: &str) -> &str {
    match section {
        // Legacy aliases retained for older snapshots and old clients.
        "url" | "scan_results" => "company_url",
        "business_stage" => "company_stage",
        "primary_product" | "pricing_model" => "product_catalog",
        "customer_problem" => "problem_statement",
        "icp" => "target_audience",
        "transformation" => "secondary_icps",
        "differentiation" => "differentiation",
        "keywords" => "seo_keywords",
        "content_channels" | "content_history" => "channels",
        "primary_goal" | "budget" => "goals",
        "existing_assets" => "asset_inventory",
        "analytics_tracking" => "frustrations",
        other => other,
    }
}

pub async fn get_snapshot_full(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<SnapshotFullResponse>> {
    let pool = db_pool(&state)?;

    let rows = sqlx::query_as::<_, (String, serde_json::Value, chrono::DateTime<chrono::Utc>)>(
        r#"
        SELECT section_key, value, updated_at
        FROM foundation_sections
        WHERE org_id = $1
        ORDER BY updated_at DESC
        "#,
    )
    .bind(auth.tenant.org_id)
    .fetch_all(pool)
    .await
    .map_err(internal_error)?;

    if rows.is_empty() {
        return Ok(Json(SnapshotFullResponse {
            status: "not_started".to_string(),
            completed_sections: vec![],
            missing_sections: ALL_SECTIONS.iter().map(|s| s.to_string()).collect(),
            last_updated_section: None,
            version: 0,
            sections: serde_json::json!({}),
        }));
    }

    let mut sections_map = serde_json::Map::new();
    let mut latest_by_section: std::collections::HashMap<
        String,
        (serde_json::Value, chrono::DateTime<chrono::Utc>),
    > = std::collections::HashMap::new();
    let mut last_updated = None;
    let mut last_updated_at =
        chrono::DateTime::<chrono::Utc>::from_timestamp(0, 0).unwrap_or_else(Utc::now);

    for (raw_key, value, updated_at) in rows {
        let key = canonical_section_key(&raw_key).to_string();
        match latest_by_section.get(&key) {
            Some((_, existing_at)) if *existing_at >= updated_at => {}
            _ => {
                latest_by_section.insert(key.clone(), (value, updated_at));
            }
        }
    }

    let mut completed = Vec::new();
    for key in ALL_SECTIONS {
        if let Some((value, updated_at)) = latest_by_section.get(key) {
            sections_map.insert(key.to_string(), value.clone());
            completed.push(key.to_string());
            if *updated_at > last_updated_at {
                last_updated_at = *updated_at;
                last_updated = Some(key.to_string());
            }
        }
    }

    let missing: Vec<String> = ALL_SECTIONS
        .iter()
        .filter(|s| !completed.iter().any(|completed_key| completed_key == *s))
        .map(|s| s.to_string())
        .collect();

    let status = if missing.is_empty() {
        "completed"
    } else {
        "in_progress"
    };

    let current_version = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .map(|snapshot| snapshot.foundation_version)
        .unwrap_or(completed.len() as i32);

    Ok(Json(SnapshotFullResponse {
        status: status.to_string(),
        completed_sections: completed.clone(),
        missing_sections: missing,
        last_updated_section: last_updated,
        version: current_version,
        sections: serde_json::to_value(sections_map).unwrap_or(serde_json::json!({})),
    }))
}

#[derive(Debug, Serialize)]
pub struct CompleteResponse {
    pub ok: bool,
    pub office_ready: bool,
    pub strategist_name: String,
    pub first_nudge_id: Option<String>,
}

pub async fn complete_foundation(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<CompleteResponse>> {
    let pool = db_pool(&state)?;
    let org_id = auth.tenant.org_id;

    let rows = sqlx::query_as::<_, (String, serde_json::Value)>(
        r#"
        SELECT section_key, value
        FROM foundation_sections
        WHERE org_id = $1
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await
    .map_err(internal_error)?;

    let mut sections = serde_json::Map::new();
    for (key, value) in rows {
        sections.insert(key, value);
    }

    let foundation_json = serde_json::json!({ "sections": sections });

    let avatar_check =
        sqlx::query_as::<_, (i64,)>("SELECT COUNT(*) FROM agent_essences WHERE org_id = $1")
            .bind(org_id)
            .fetch_optional(pool)
            .await
            .map_err(internal_error)?;

    let needs_seeding = avatar_check.map(|row| row.0 == 0).unwrap_or(true);

    if needs_seeding {
        let foundation_snapshot = FoundationSnapshot {
            foundation_snapshot_id: format!("found-{}-complete", org_id),
            org_id,
            foundation_version: 1,
            sections: foundation_json.clone(),
            source: "completion".to_string(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };
        if let Err(e) = seed_org_avatars(pool, org_id, Some(&foundation_snapshot)).await {
            tracing::warn!(org_id = %org_id, error = %e, "avatar seeding failed during completion");
        }
    }

    let company_name = foundation_json
        .get("sections")
        .and_then(|s| s.get("company_info"))
        .and_then(|ci| ci.get("name"))
        .and_then(|v| v.as_str())
        .unwrap_or("there");

    let (nudge_title, nudge_body) = {
        (
            "Your Strategist is ready!".to_string(),
            format!(
                "Welcome {}! Your Strategist is now active and ready to help craft campaigns that truly resonate with your audience. Head to your Office to meet your team and get started!",
                company_name
            ),
        )
    };

    let first_user = sqlx::query_as::<_, (Uuid,)>(
        "SELECT org_user_id FROM org_users WHERE org_id = $1 ORDER BY created_at ASC LIMIT 1",
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await
    .map_err(internal_error)?;

    let nudge_id = Ulid::new().to_string();
    let mut first_nudge_id: Option<String> = None;

    if let Some((user_id,)) = first_user {
        let nudge_type = "foundation_complete";
        let priority = "high";
        let action_data = serde_json::json!({ "action": "open_office" });

        if let Err(e) = db::create_nudge(
            pool,
            &nudge_id,
            org_id,
            user_id,
            nudge_type,
            priority,
            &nudge_title,
            &nudge_body,
            Some("navigate"),
            &action_data,
            "foundation",
            &format!("found-{}", org_id),
        )
        .await
        {
            tracing::warn!(org_id = %org_id, error = %e, "failed to create nudge record");
        } else {
            first_nudge_id = Some(nudge_id.clone());
            tracing::info!(org_id = %org_id, nudge_id = %nudge_id, "first strategist nudge created");
        }
    }

    Ok(Json(CompleteResponse {
        ok: true,
        office_ready: true,
        strategist_name: "Strategist".to_string(),
        first_nudge_id,
    }))
}

pub async fn content_strategy_create(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;
    let strategy_id = format!(
        "content-strategy-{}-{}",
        auth.tenant.org_id,
        ulid::Ulid::new()
    );

    raptorflow_db::queries::create_content_strategy(pool, &strategy_id, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "strategy_id": strategy_id,
        "status": "created"
    })))
}

pub async fn content_strategy_get(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;
    let strategy = raptorflow_db::queries::get_content_strategy(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    match strategy {
        Some(s) => Ok(Json(serde_json::json!({
            "strategy_id": s.strategy_id,
            "territories": s.territories,
            "pillar_pages": s.pillar_pages,
            "editorial_calendar": s.editorial_calendar,
            "created_at": s.created_at,
            "updated_at": s.updated_at
        }))),
        None => Ok(Json(serde_json::json!({
            "territories": [],
            "pillar_pages": [],
            "editorial_calendar": []
        }))),
    }
}

pub async fn content_strategy_update_territories(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(territories): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Ensure strategy exists
    let existing = raptorflow_db::queries::get_content_strategy(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    if existing.is_none() {
        raptorflow_db::queries::create_content_strategy(
            pool,
            &format!(
                "content-strategy-{}-{}",
                auth.tenant.org_id,
                ulid::Ulid::new()
            ),
            auth.tenant.org_id,
        )
        .await
        .map_err(internal_error)?;
    }

    raptorflow_db::queries::update_content_strategy_territories(
        pool,
        auth.tenant.org_id,
        &territories,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "success": true })))
}

pub async fn content_strategy_generate_calendar(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    let strategy = raptorflow_db::queries::get_content_strategy(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("content_strategy_not_found"))?;

    let territories: Vec<serde_json::Value> =
        serde_json::from_value(strategy.territories).unwrap_or_default();
    let pillar_pages: Vec<serde_json::Value> =
        serde_json::from_value(strategy.pillar_pages).unwrap_or_default();

    let calendar = generate_fallback_calendar(&territories, &pillar_pages);

    raptorflow_db::queries::update_content_strategy_calendar(
        pool,
        auth.tenant.org_id,
        &serde_json::to_value(&calendar).unwrap_or(serde_json::json!([])),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "calendar": calendar })))
}

fn generate_fallback_calendar(
    territories: &[serde_json::Value],
    pillar_pages: &[serde_json::Value],
) -> Vec<serde_json::Value> {
    let mut calendar = Vec::new();
    let mut content_id = 1;
    let today = chrono::Utc::now();

    for territory in territories {
        if let Some(territory_name) = territory.get("name").and_then(|v| v.as_str()) {
            for week in 0..12 {
                let date = today + chrono::Duration::days(week * 7);
                calendar.push(serde_json::json!({
                    "id": content_id,
                    "title": format!("{} Content - Week {}", territory_name, week + 1),
                    "territory": territory_name,
                    "date": date.format("%Y-%m-%d").to_string(),
                    "status": "planned",
                    "content_type": "blog_post"
                }));
                content_id += 1;
            }
        }
    }

    for pillar in pillar_pages {
        if let Some(pillar_title) = pillar.get("title").and_then(|v| v.as_str()) {
            for (i, month) in [1, 4, 7, 10].iter().enumerate() {
                let date = chrono::NaiveDate::from_ymd_opt(2026, *month, 1)
                    .unwrap_or(today.naive_utc().date());
                calendar.push(serde_json::json!({
                    "id": content_id,
                    "title": format!("{} Update - Q{}", pillar_title, i + 1),
                    "pillar_page": pillar_title,
                    "date": date.format("%Y-%m-%d").to_string(),
                    "status": "planned",
                    "content_type": "pillar_update"
                }));
                content_id += 1;
            }
        }
    }

    calendar
}

pub async fn add_secondary_icp(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    let mode = payload
        .get("mode")
        .and_then(|v| v.as_str())
        .ok_or_else(|| bad_request("mode is required (b2b or b2c)"))?;
    let icp_data = payload
        .get("icp")
        .ok_or_else(|| bad_request("icp data is required"))?;

    // Validate B2B structure
    fn validate_b2b_icp(icp: &serde_json::Value) -> Result<(), &'static str> {
        if icp
            .get("name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2B ICP requires non-empty name");
        }
        if icp
            .get("persona_name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2B ICP requires non-empty persona_name");
        }
        if icp
            .get("role_identity")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2B ICP requires non-empty role_identity");
        }
        Ok(())
    }

    // Validate B2C structure
    fn validate_b2c_icp(icp: &serde_json::Value) -> Result<(), &'static str> {
        if icp
            .get("name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2C ICP requires non-empty name");
        }
        if icp
            .get("persona_name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2C ICP requires non-empty persona_name");
        }
        if icp
            .get("life_situation")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2C ICP requires non-empty life_situation");
        }
        Ok(())
    }

    match mode {
        "b2b" => validate_b2b_icp(icp_data).map_err(bad_request)?,
        "b2c" => validate_b2c_icp(icp_data).map_err(bad_request)?,
        _ => return Err(bad_request("mode must be 'b2b' or 'b2c'")),
    }

    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let mut foundation_json: serde_json::Value = foundation_data.sections;

    if foundation_json.get("secondary_icps").is_none() {
        foundation_json["secondary_icps"] = serde_json::json!([]);
    }

    let secondary_icps_count = {
        let secondary_icps = foundation_json
            .get_mut("secondary_icps")
            .and_then(|v| v.as_array_mut())
            .ok_or_else(|| bad_request("secondary_icps must be an array"))?;

        if secondary_icps.len() >= 3 {
            return Err(bad_request("Maximum 3 secondary ICPs allowed"));
        }

        let secondary_icp = serde_json::json!({
            "mode": mode,
            "icp": icp_data
        });

        secondary_icps.push(secondary_icp);
        secondary_icps.len()
    };

    let new_version = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &foundation_json,
        "add_secondary_icp",
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "secondary_icps_count": secondary_icps_count,
        "new_version": new_version.foundation_version
    })))
}

pub async fn update_secondary_icp(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(icp_index): Path<usize>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Validate payload has mode and icp data
    let mode = payload
        .get("mode")
        .and_then(|v| v.as_str())
        .ok_or_else(|| bad_request("mode is required (b2b or b2c)"))?;
    let icp_data = payload
        .get("icp")
        .ok_or_else(|| bad_request("icp data is required"))?;

    // Get current foundation
    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let mut foundation_json: serde_json::Value = foundation_data.sections;

    // Get secondary_icps array
    if foundation_json.get("secondary_icps").is_none() {
        foundation_json["secondary_icps"] = serde_json::json!([]);
    }
    let _secondary_icps_len = {
        let secondary_icps = foundation_json
            .get_mut("secondary_icps")
            .and_then(|v| v.as_array_mut())
            .ok_or_else(|| bad_request("secondary_icps must be an array"))?;

        // Validate index
        if icp_index >= secondary_icps.len() {
            return Err(bad_request("invalid icp index"));
        }

        // Update secondary ICP entry
        secondary_icps[icp_index] = serde_json::json!({
            "mode": mode,
            "icp": icp_data
        });

        secondary_icps.len()
    };

    // Create new foundation version
    let new_version = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &foundation_json,
        "update_secondary_icp",
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "updated_index": icp_index,
        "new_version": new_version.foundation_version
    })))
}

pub async fn delete_secondary_icp(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(icp_index): Path<usize>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Get current foundation
    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let mut foundation_json: serde_json::Value = foundation_data.sections;

    // Get secondary_icps array
    if foundation_json.get("secondary_icps").is_none() {
        foundation_json["secondary_icps"] = serde_json::json!([]);
    }
    let remaining_count = {
        let secondary_icps = foundation_json
            .get_mut("secondary_icps")
            .and_then(|v| v.as_array_mut())
            .ok_or_else(|| bad_request("secondary_icps must be an array"))?;

        // Validate index
        if icp_index >= secondary_icps.len() {
            return Err(bad_request("invalid icp index"));
        }

        // Remove secondary ICP
        secondary_icps.remove(icp_index);
        secondary_icps.len()
    };

    // Create new foundation version
    let new_version = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &foundation_json,
        "delete_secondary_icp",
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "deleted_index": icp_index,
        "remaining_count": remaining_count,
        "new_version": new_version.foundation_version
    })))
}

pub async fn generate_positioning_draft(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;
    let bedrock = state.bedrock.as_ref().ok_or_else(|| {
        (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(serde_json::json!({ "error": "bedrock_unavailable" })),
        )
    })?;

    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let foundation_json: serde_json::Value = foundation_data.sections;

    let icp = foundation_json
        .get("target_audience")
        .and_then(|ta| ta.get("primary_icp"));
    let _competitors = foundation_json.get("competitors");
    let differentiation = foundation_json.get("differentiation");
    let _product = foundation_json
        .get("product_catalog")
        .and_then(|pc| pc.get("primary_product"));
    let problem = foundation_json.get("problem_statement");

    let company_name = foundation_json
        .get("company_info")
        .and_then(|ci| ci.get("name"))
        .and_then(|n| n.as_str())
        .unwrap_or("our brand");
    let category = foundation_json
        .get("company_info")
        .and_then(|ci| ci.get("industry"))
        .and_then(|n| n.as_str())
        .unwrap_or("solution provider");
    let for_who = icp
        .and_then(|i| i.get("name"))
        .and_then(|n| n.as_str())
        .unwrap_or("our target customers");
    let who_problem = problem
        .and_then(|p| p.as_str())
        .unwrap_or("face challenges");
    let differentiation_text = differentiation
        .and_then(|d| d.as_array())
        .and_then(|arr| arr.first())
        .and_then(|v| v.as_str())
        .unwrap_or("unique value");
    let because = "we deliver proven results";

    let prompt = format!(
        r#"You are RaptorFlow's positioning strategist.
Return only valid JSON. No markdown, no code fences, no explanation.

Use this exact schema:
{{
  "statement": string,
  "templateComponents": {{
    "forWho": string,
    "whoProblem": string,
    "brand": string,
    "category": string,
    "differentiation": string,
    "because": string
  }},
  "qualityScore": number,
  "qualityFeedback": string
}}

Requirements:
- Write one concise positioning statement.
- qualityScore must be a number from 0 to 1.
- qualityFeedback must be one short sentence with the most important improvement.

Context:
- forWho: {for_who}
- whoProblem: {who_problem}
- brand: {company_name}
- category: {category}
- differentiation: {differentiation_text}
- because: {because}
"#
    );

    let raw = bedrock
        .converse_large(&prompt, 768)
        .await
        .map_err(internal_error)?;

    let trimmed = raw.trim();
    let json_text = if let Ok(value) = serde_json::from_str::<serde_json::Value>(trimmed) {
        value
    } else {
        let start = trimmed.find('{').ok_or_else(|| {
            (
                StatusCode::BAD_GATEWAY,
                Json(serde_json::json!({ "error": "bedrock_response_missing_json" })),
            )
        })?;
        let end = trimmed.rfind('}').ok_or_else(|| {
            (
                StatusCode::BAD_GATEWAY,
                Json(serde_json::json!({ "error": "bedrock_response_missing_json" })),
            )
        })?;
        serde_json::from_str::<serde_json::Value>(&trimmed[start..=end]).map_err(|e| {
            (
                StatusCode::BAD_GATEWAY,
                Json(serde_json::json!({
                    "error": "bedrock_response_invalid_json",
                    "details": e.to_string()
                })),
            )
        })?
    };

    let response: PositioningDraftResponse = serde_json::from_value(json_text).map_err(|e| {
        (
            StatusCode::BAD_GATEWAY,
            Json(serde_json::json!({
                "error": "bedrock_positioning_schema_mismatch",
                "details": e.to_string()
            })),
        )
    })?;

    Ok(Json(
        serde_json::to_value(response).map_err(internal_error)?,
    ))
}

pub async fn lock_positioning(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Get active campaigns that might be affected
    // Note: This assumes there's a campaigns table and API to get active campaigns
    // For now, we'll return a placeholder impact assessment
    let downstream_impact = vec![serde_json::json!({
        "campaignId": "placeholder-campaign-1",
        "campaignName": "Q1 Growth Campaign",
        "impactDescription": "Campaign messaging may need alignment with new positioning statement."
    })];

    // Update foundation positioning with isLocked: true
    let positioning_data = payload
        .get("positioning")
        .ok_or_else(|| bad_request("positioning data required"))?;

    let mut locked_positioning = positioning_data.clone();
    if let Some(obj) = locked_positioning.as_object_mut() {
        obj.insert("is_locked".to_string(), serde_json::json!(true));
        obj.insert(
            "locked_at".to_string(),
            serde_json::json!(chrono::Utc::now().to_rfc3339()),
        );
    }

    // Update foundation section
    raptorflow_db::queries::upsert_foundation_section(
        pool,
        auth.tenant.org_id,
        "positioning",
        &locked_positioning,
    )
    .await
    .map_err(internal_error)?;

    // Create FoundationVersion record
    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let version_id = format!("version-{}-{}", auth.tenant.org_id, ulid::Ulid::new());
    raptorflow_db::queries::create_foundation_version(
        pool,
        &version_id,
        auth.tenant.org_id,
        foundation_data.foundation_version + 1,
        Some("positioning_locked"),
        &serde_json::json!({}),
        &serde_json::json!({}),
        Some(&serde_json::json!(downstream_impact)),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "downstreamImpact": downstream_impact,
        "newVersion": foundation_data.foundation_version + 1
    })))
}
