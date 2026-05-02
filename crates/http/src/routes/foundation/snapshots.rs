use super::common::*;

pub async fn get_foundation(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let snapshot = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    match snapshot {
        Some(snapshot) => Ok(Json(map_snapshot(&snapshot))),
        None => Err(not_found("foundation_not_found")),
    }
}

pub async fn create_foundation(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let foundation_data: FoundationData =
        serde_json::from_value(payload.clone()).map_err(|e| bad_request(&e.to_string()))?;

    let org_name = foundation_data
        .company_info
        .name
        .clone()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| format!("Organization {}", auth.tenant.org_id));

    raptorflow_db::queries::create_organization(pool, auth.tenant.org_id, &org_name)
        .await
        .map_err(internal_error)?;

    let existing = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    let snapshot = match existing {
        None => {
            let snapshot_id =
                FoundationService::create_initial(pool, auth.tenant.org_id, foundation_data)
                    .await
                    .map_err(internal_error)?;
            update_org_foundation_version(pool, auth.tenant.org_id, 1)
                .await
                .map_err(internal_error)?;
            get_snapshot_row(pool, auth.tenant.org_id, &snapshot_id)
                .await
                .map_err(internal_error)?
                .ok_or_else(|| not_found("foundation_not_found"))?
        }
        Some(_current) => {
            let next = create_snapshot_from_sections(pool, auth.tenant.org_id, &payload, "manual")
                .await
                .map_err(internal_error)?;
            SnapshotRow {
                foundation_snapshot_id: next.foundation_snapshot_id,
                org_id: next.org_id,
                foundation_version: next.foundation_version,
                sections: next.sections,
                source: next.source,
                updated_at: next.updated_at,
            }
        }
    };

    let response = FoundationResponse {
        id: snapshot.foundation_snapshot_id,
        org_id: snapshot.org_id,
        version: snapshot.foundation_version,
        sections: snapshot.sections,
        updated_at: snapshot.updated_at.to_rfc3339(),
        source: snapshot.source,
    };

    Ok(Json(response))
}

pub async fn update_section(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(section): Path<String>,
    Json(payload): Json<UpdateSectionRequest>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;

    let previous_value = FoundationService::get_section(pool, auth.tenant.org_id, &section)
        .await
        .map_err(internal_error)?;

    let version =
        FoundationService::update_section(pool, auth.tenant.org_id, &section, payload.data)
            .await
            .map_err(internal_error)?;

    if let Some(prev) = previous_value {
        let latest =
            raptorflow_db::queries::get_latest_foundation_version(pool, auth.tenant.org_id)
                .await
                .map_err(internal_error)?;

        let next_version = latest.map(|v| v.foundation_version + 1).unwrap_or(1);

        let _ = raptorflow_db::queries::create_foundation_version(
            pool,
            &format!("fv-{}-{}", auth.tenant.org_id, ulid::Ulid::new()),
            auth.tenant.org_id,
            next_version,
            Some(&format!("Updated {}", section)),
            &serde_json::json!([section]),
            &prev,
            None,
        )
        .await;
    }

    update_org_foundation_version(pool, auth.tenant.org_id, version)
        .await
        .map_err(internal_error)?;

    let snapshot = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    Ok(Json(map_snapshot(&snapshot)))
}

pub async fn list_foundation_versions(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<Vec<serde_json::Value>>> {
    let pool = db_pool(&state)?;
    let versions = raptorflow_db::queries::get_foundation_versions(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<serde_json::Value> = versions
        .iter()
        .map(|v| {
            serde_json::json!({
                "version_id": v.version_id,
                "version": v.foundation_version,
                "change_description": v.change_description,
                "changed_fields": v.changed_fields,
                "previous_values": v.previous_values,
                "impact_assessment": v.impact_assessment,
                "created_at": v.created_at.to_rfc3339(),
            })
        })
        .collect();

    Ok(Json(response))
}

pub async fn list_snapshots(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<Vec<FoundationResponse>>> {
    let pool = db_pool(&state)?;
    let snapshots = raptorflow_db::queries::get_foundation_snapshots(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    let response = snapshots.iter().map(map_snapshot).collect();
    Ok(Json(response))
}

pub async fn create_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<CreateSnapshotRequest>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let current = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let snapshot = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &current.sections,
        payload
            .source
            .as_deref()
            .filter(|value| !value.trim().is_empty())
            .unwrap_or("manual_snapshot"),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(map_snapshot(&snapshot)))
}

pub async fn restore_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(id): Path<String>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let snapshot = get_snapshot_row(pool, auth.tenant.org_id, &id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_snapshot_not_found"))?;

    let restored = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &snapshot.sections,
        &format!("restore:{id}"),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(map_snapshot(&restored)))
}

pub async fn get_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(id): Path<String>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let snapshot = get_snapshot_row(pool, auth.tenant.org_id, &id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_snapshot_not_found"))?;

    Ok(Json(FoundationResponse {
        id: snapshot.foundation_snapshot_id,
        org_id: snapshot.org_id,
        version: snapshot.foundation_version,
        sections: snapshot.sections,
        updated_at: snapshot.updated_at.to_rfc3339(),
        source: snapshot.source,
    }))
}
