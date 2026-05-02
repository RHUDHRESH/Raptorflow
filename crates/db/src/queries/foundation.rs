use super::common::*;

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
