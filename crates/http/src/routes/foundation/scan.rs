use super::common::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct ScanStartRequest {
    pub url: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ScanStatus {
    Queued,
    Running,
    Completed,
    Failed,
}

impl ScanStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            ScanStatus::Queued => "queued",
            ScanStatus::Running => "running",
            ScanStatus::Completed => "completed",
            ScanStatus::Failed => "failed",
        }
    }

    #[allow(clippy::should_implement_trait)]
    pub fn from_str(s: &str) -> Self {
        match s {
            "queued" => ScanStatus::Queued,
            "running" => ScanStatus::Running,
            "completed" | "complete" => ScanStatus::Completed,
            "failed" => ScanStatus::Failed,
            _ => ScanStatus::Running,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct ScanStartResponse {
    pub scan_id: String,
    pub status: String,
}

#[derive(Debug, Serialize)]
pub struct ScanStatusResponse {
    pub scan_id: Option<String>,
    pub status: String,
    pub data: Option<serde_json::Value>,
    pub error_message: Option<String>,
}

async fn resolve_scan_url(
    pool: &sqlx::PgPool,
    org_id: Uuid,
) -> Result<Option<String>, sqlx::Error> {
    let row = sqlx::query_as::<_, (Option<String>,)>(
        r#"
        SELECT value::text as url
        FROM foundation_sections
        WHERE org_id = $1 AND section_key IN ('company_url', 'url', 'website')
        ORDER BY updated_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;

    Ok(row.and_then(|(url,)| {
        if url.as_ref().is_some_and(|u| !u.is_empty()) {
            url
        } else {
            None
        }
    }))
}

enum ScanMode {
    Quick,
    Deep,
}

impl ScanMode {
    #[allow(dead_code)]
    fn as_str(&self) -> &'static str {
        match self {
            ScanMode::Quick => "quick",
            ScanMode::Deep => "deep",
        }
    }
}

async fn launch_scan(
    scan_id: String,
    url: String,
    pool: sqlx::PgPool,
    mode: ScanMode,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let scan_id_clone = scan_id.clone();
    let pool_clone = pool.clone();

    let data = match mode {
        ScanMode::Quick => quick_scan(&url).await,
        ScanMode::Deep => deep_scan(&url).await,
    };

    let final_status = match &data {
        Ok(d) => {
            let is_failed = d
                .get("confidence")
                .and_then(|c: &serde_json::Value| c.as_str())
                .map(|s| s == "failed")
                .unwrap_or(false);
            if is_failed { "failed" } else { "completed" }
        }
        Err(_) => "failed",
    };

    let error_msg = match &data {
        Ok(d) => {
            let is_failed = d
                .get("confidence")
                .and_then(|c: &serde_json::Value| c.as_str())
                .map(|s| s == "failed")
                .unwrap_or(false);
            if is_failed {
                d.get("error")
                    .and_then(|e: &serde_json::Value| e.as_str())
                    .map(String::from)
            } else {
                None
            }
        }
        Err(e) => Some(e.to_string()),
    };

    let scan_data_json = data.as_ref().unwrap_or(&serde_json::Value::Null);

    match mode {
        ScanMode::Quick => {
            let _ = sqlx::query(
                r#"
                UPDATE foundation_scans
                SET status = $1, quick_scan_data = $2, completed_at = now(), error_message = $3
                WHERE scan_id = $4
                "#,
            )
            .bind(final_status)
            .bind(scan_data_json)
            .bind(&error_msg)
            .bind(&scan_id_clone)
            .execute(&pool_clone)
            .await;
        }
        ScanMode::Deep => {
            let _ = sqlx::query(
                r#"
                UPDATE foundation_scans
                SET status = $1, deep_scan_data = $2, completed_at = now(), error_message = $3
                WHERE scan_id = $4
                "#,
            )
            .bind(final_status)
            .bind(scan_data_json)
            .bind(&error_msg)
            .bind(&scan_id_clone)
            .execute(&pool_clone)
            .await;
        }
    }

    Ok(())
}

pub async fn start_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<ScanStartRequest>,
) -> AppResult<Json<ScanStartResponse>> {
    let pool = db_pool(&state)?;

    let url = match &payload.url {
        Some(u) if !u.is_empty() => u.clone(),
        _ => resolve_scan_url(pool, auth.tenant.org_id)
            .await
            .map_err(internal_error)?
            .ok_or_else(|| bad_request("scan_url_required"))?,
    };

    let scan_id = format!("scan-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .bind(&url)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let pool_clone = pool.clone();
    let scan_id_clone = scan_id.clone();

    tokio::spawn(async move {
        if let Err(e) = launch_scan(scan_id_clone, url, pool_clone, ScanMode::Quick).await {
            tracing::error!("Scan failed: {}", e);
        }
    });

    Ok(Json(ScanStartResponse {
        scan_id,
        status: ScanStatus::Queued.as_str().to_string(),
    }))
}

pub async fn start_quick_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<ScanStartRequest>,
) -> AppResult<Json<ScanStartResponse>> {
    let pool = db_pool(&state)?;

    let url = match &payload.url {
        Some(u) if !u.is_empty() => u.clone(),
        _ => resolve_scan_url(pool, auth.tenant.org_id)
            .await
            .map_err(internal_error)?
            .ok_or_else(|| bad_request("scan_url_required"))?,
    };

    let scan_id = format!("scan-quick-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .bind(&url)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let pool_clone = pool.clone();
    let scan_id_clone = scan_id.clone();

    tokio::spawn(async move {
        if let Err(e) = launch_scan(scan_id_clone, url, pool_clone, ScanMode::Quick).await {
            tracing::error!("Quick scan failed: {}", e);
        }
    });

    Ok(Json(ScanStartResponse {
        scan_id,
        status: ScanStatus::Queued.as_str().to_string(),
    }))
}

pub async fn start_deep_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<ScanStartRequest>,
) -> AppResult<Json<ScanStartResponse>> {
    let pool = db_pool(&state)?;

    let url = match &payload.url {
        Some(u) if !u.is_empty() => u.clone(),
        _ => resolve_scan_url(pool, auth.tenant.org_id)
            .await
            .map_err(internal_error)?
            .ok_or_else(|| bad_request("scan_url_required"))?,
    };

    let scan_id = format!("scan-deep-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .bind(&url)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let pool_clone = pool.clone();
    let scan_id_clone = scan_id.clone();

    tokio::spawn(async move {
        if let Err(e) = launch_scan(scan_id_clone, url, pool_clone, ScanMode::Deep).await {
            tracing::error!("Deep scan failed: {}", e);
        }
    });

    Ok(Json(ScanStartResponse {
        scan_id,
        status: ScanStatus::Queued.as_str().to_string(),
    }))
}

#[derive(Debug, Deserialize)]
pub struct UpdateScanRequest {
    pub scan_id: String,
    pub deep_scan_data: Option<serde_json::Value>,
}

pub async fn update_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<UpdateScanRequest>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    sqlx::query(
        r#"
        UPDATE foundation_scans
        SET deep_scan_data = $1, status = 'completed', completed_at = now()
        WHERE scan_id = $2 AND org_id = $3
        "#,
    )
    .bind(payload.deep_scan_data)
    .bind(&payload.scan_id)
    .bind(auth.tenant.org_id)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "ok": true })))
}

pub async fn get_scan_by_id(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(scan_id): Path<String>,
) -> AppResult<Json<ScanStatusResponse>> {
    let pool = db_pool(&state)?;

    let row = sqlx::query_as::<
        _,
        (
            String,
            Option<serde_json::Value>,
            Option<serde_json::Value>,
            Option<String>,
        ),
    >(
        r#"
        SELECT status, quick_scan_data, deep_scan_data, error_message
        FROM foundation_scans
        WHERE scan_id = $1 AND org_id = $2
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .fetch_optional(pool)
    .await
    .map_err(internal_error)?;

    match row {
        Some((status, quick_data, deep_data, error_message)) => {
            let normalized_status = ScanStatus::from_str(&status).as_str().to_string();
            let data = if status == "completed" || status == "complete" {
                if deep_data.is_some() {
                    deep_data
                } else {
                    quick_data
                }
            } else {
                None
            };
            Ok(Json(ScanStatusResponse {
                scan_id: Some(scan_id),
                status: normalized_status,
                data,
                error_message,
            }))
        }
        None => Err(not_found("scan_not_found")),
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateCompetitorSnapshotRequest {
    pub competitor_url: String,
}

#[derive(Debug, Serialize)]
pub struct CreateCompetitorSnapshotResponse {
    pub snapshot_id: String,
}

pub async fn create_competitor_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<CreateCompetitorSnapshotRequest>,
) -> AppResult<Json<CreateCompetitorSnapshotResponse>> {
    let pool = db_pool(&state)?;

    let snapshot_id = format!("comp-snap-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    raptorflow_db::queries::create_competitor_snapshot(
        pool,
        &snapshot_id,
        auth.tenant.org_id,
        &payload.competitor_url,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(CreateCompetitorSnapshotResponse { snapshot_id }))
}

#[derive(Debug, Deserialize)]
pub struct UpdateCompetitorSnapshotRequest {
    pub hash: Option<String>,
    pub status: String,
    pub scrape_data: Option<serde_json::Value>,
}

pub async fn update_competitor_snapshot(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(snapshot_id): Path<String>,
    Json(payload): Json<UpdateCompetitorSnapshotRequest>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    raptorflow_db::queries::update_competitor_snapshot(
        pool,
        &snapshot_id,
        payload.hash.as_deref(),
        &payload.status,
        payload.scrape_data.as_ref(),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "ok": true })))
}

#[derive(Debug, Deserialize)]
pub struct GetLatestCompetitorSnapshotQuery {
    pub competitor_url: String,
}

pub async fn get_latest_competitor_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Query(query): Query<GetLatestCompetitorSnapshotQuery>,
) -> AppResult<Json<Option<serde_json::Value>>> {
    let pool = db_pool(&state)?;

    let snapshot = raptorflow_db::queries::get_latest_competitor_snapshot_by_url(
        pool,
        auth.tenant.org_id,
        &query.competitor_url,
    )
    .await
    .map_err(internal_error)?;

    match snapshot {
        Some(snap) => Ok(Json(Some(serde_json::json!({
            "snapshot_id": snap.snapshot_id,
            "hash": snap.hash,
            "status": snap.status,
            "scrape_data": snap.scrape_data,
            "created_at": snap.created_at
        })))),
        None => Ok(Json(None)),
    }
}

pub async fn get_scan_status(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<ScanStatusResponse>> {
    let pool = db_pool(&state)?;

    let row = sqlx::query_as::<
        _,
        (
            String,
            Option<serde_json::Value>,
            Option<serde_json::Value>,
            Option<String>,
        ),
    >(
        r#"
        SELECT status, quick_scan_data, deep_scan_data, error_message
        FROM foundation_scans
        WHERE org_id = $1
        ORDER BY started_at DESC
        LIMIT 1
        "#,
    )
    .bind(auth.tenant.org_id)
    .fetch_optional(pool)
    .await
    .map_err(internal_error)?;

    match row {
        Some((status, quick_data, deep_data, error_message)) => {
            let data = if status == "completed" {
                if deep_data.is_some() {
                    deep_data
                } else {
                    quick_data
                }
            } else {
                None
            };
            Ok(Json(ScanStatusResponse {
                scan_id: None,
                status,
                data,
                error_message,
            }))
        }
        None => Ok(Json(ScanStatusResponse {
            scan_id: None,
            status: "not_found".to_string(),
            data: None,
            error_message: None,
        })),
    }
}

async fn deep_scan(url: &str) -> Result<serde_json::Value, String> {
    let fetcher = HttpFetcher::new();
    let (body, final_url) = fetcher
        .fetch(url)
        .await
        .map_err(|e| format!("fetch_failed: {}", e))?;

    let html = String::from_utf8_lossy(&body).to_string();
    let parsed = HtmlParser::parse(&html).map_err(|e| format!("parse_failed: {}", e))?;

    let title = parsed.title;
    let description = parsed.language.clone();

    let json_ld: Option<serde_json::Value> = scraper::Html::parse_document(&html)
        .select(
            &scraper::Selector::parse("script[type=\"application/ld+json\"]")
                .ok()
                .unwrap(),
        )
        .next()
        .map(|el| el.text().collect::<String>())
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok());

    let social_links = extract_social_links(&html);

    let business_name = json_ld
        .as_ref()
        .and_then(|j| j.get("name").and_then(|n| n.as_str()))
        .map(String::from)
        .or_else(|| title.clone());

    let canonical = UrlNormalizer::canonical_url(url, &final_url).ok();
    let domain = UrlNormalizer::extract_domain(&final_url).ok();
    let logo_url = json_ld
        .as_ref()
        .and_then(|j| j.get("logo").and_then(|l| l.as_str()).map(String::from));

    let primary_offering = json_ld.as_ref().and_then(|j| {
        j.get("description")
            .and_then(|d| d.as_str())
            .map(String::from)
    });

    let industry = infer_industry(title.as_ref().or(description.as_ref()));

    let confidence = if business_name.is_some() {
        "medium"
    } else {
        "low"
    };

    Ok(serde_json::json!({
        "business_name": business_name,
        "industry": industry,
        "description": description,
        "primary_offering": primary_offering,
        "competitor_suggestions": [],
        "keyword_suggestions": [],
        "confidence": confidence,
        "social_links": social_links,
        "logo_url": logo_url,
        "domain": domain,
        "raw": {
            "title": title,
            "url": final_url,
            "canonical": canonical,
            "json_ld": json_ld
        }
    }))
}

async fn quick_scan(url: &str) -> Result<serde_json::Value, String> {
    let fetcher = HttpFetcher::new();
    let (body, final_url) = fetcher
        .fetch(url)
        .await
        .map_err(|e| format!("fetch_failed: {}", e))?;

    let html = String::from_utf8_lossy(&body).to_string();
    let parsed = HtmlParser::parse(&html).map_err(|e| format!("parse_failed: {}", e))?;

    let title = parsed.title;
    let description = parsed.language.clone();
    let og_image = scraper::Html::parse_document(&html)
        .select(
            &scraper::Selector::parse("meta[property=\"og:image\"]")
                .ok()
                .unwrap(),
        )
        .next()
        .and_then(|el| el.value().attr("content"))
        .map(String::from);

    let json_ld: Option<serde_json::Value> = scraper::Html::parse_document(&html)
        .select(
            &scraper::Selector::parse("script[type=\"application/ld+json\"]")
                .ok()
                .unwrap(),
        )
        .next()
        .map(|el| el.text().collect::<String>())
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok());

    let social_links = extract_social_links(&html);

    let business_name = json_ld
        .as_ref()
        .and_then(|j| j.get("name").and_then(|n| n.as_str()))
        .map(String::from)
        .or_else(|| title.clone());

    let canonical = UrlNormalizer::canonical_url(url, &final_url).ok();
    let domain = UrlNormalizer::extract_domain(&final_url).ok();
    let logo_url = json_ld
        .as_ref()
        .and_then(|j| j.get("logo").and_then(|l| l.as_str()).map(String::from))
        .or(og_image);

    let primary_offering = json_ld.as_ref().and_then(|j| {
        j.get("description")
            .and_then(|d| d.as_str())
            .map(String::from)
    });

    let industry = infer_industry(title.as_ref().or(description.as_ref()));

    let confidence = if business_name.is_some() {
        "medium"
    } else {
        "low"
    };

    Ok(serde_json::json!({
        "business_name": business_name,
        "industry": industry,
        "description": description,
        "primary_offering": primary_offering,
        "competitor_suggestions": [],
        "keyword_suggestions": [],
        "confidence": confidence,
        "social_links": social_links,
        "logo_url": logo_url,
        "domain": domain,
        "raw": {
            "title": title,
            "url": final_url,
            "canonical": canonical,
            "json_ld": json_ld
        }
    }))
}

fn extract_social_links(html: &str) -> Vec<String> {
    let mut links = Vec::new();
    let domains = [
        "twitter.com",
        "linkedin.com",
        "facebook.com",
        "instagram.com",
        "youtube.com",
        "github.com",
    ];

    let document = scraper::Html::parse_document(html);

    for domain in &domains {
        if let Ok(selector) = scraper::Selector::parse(&format!("a[href*=\"{}\"]", domain)) {
            for el in document.select(&selector) {
                if let Some(href) = el.value().attr("href") {
                    let href = href.to_string();
                    if !links.contains(&href) {
                        links.push(href);
                    }
                }
            }
        }
    }
    links
}

fn infer_industry(text: Option<&String>) -> Option<String> {
    let desc = text?.to_lowercase();
    if desc.contains("software")
        || desc.contains("tech")
        || desc.contains("saas")
        || desc.contains("cloud")
    {
        Some("SaaS / Technology".to_string())
    } else if desc.contains("finance")
        || desc.contains("bank")
        || desc.contains("payment")
        || desc.contains("fintech")
    {
        Some("Financial Services".to_string())
    } else if desc.contains("health")
        || desc.contains("medical")
        || desc.contains("wellness")
        || desc.contains("healthcare")
    {
        Some("Healthcare & Wellness".to_string())
    } else if desc.contains("retail")
        || desc.contains("ecommerce")
        || desc.contains("e-commerce")
        || desc.contains("shop")
    {
        Some("D2C / E-commerce".to_string())
    } else if desc.contains("education")
        || desc.contains("learning")
        || desc.contains("training")
        || desc.contains("course")
    {
        Some("Education & Training".to_string())
    } else if desc.contains("real estate") || desc.contains("property") {
        Some("Real Estate".to_string())
    } else if desc.contains("food") || desc.contains("restaurant") || desc.contains("beverage") {
        Some("Food & Beverage".to_string())
    } else if desc.contains("logistics")
        || desc.contains("supply chain")
        || desc.contains("shipping")
    {
        Some("Logistics & Supply Chain".to_string())
    } else {
        None
    }
}
