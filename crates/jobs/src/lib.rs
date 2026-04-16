use axum::{
    extract::Extension,
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use raptorflow_acquisition::{
    BrowserFetcher, Chunker as AcquisitionChunker, ContentHasher as AcquisitionHasher, HtmlParser,
    HttpFetcher, SearchDiscoverer, UrlNormalizer,
};
use raptorflow_auth::TenantContext;
use raptorflow_cache::CacheService;
use raptorflow_config::Settings;
use raptorflow_contracts::{
    EventHarvesterRecord, InternTask, ResearchRequest, ResearchRequestKind, StreamCoordinatorRequest,
    ToolGatewayRequest,
};
use raptorflow_gcp::EmbeddingClient;
use raptorflow_research::{Citation, GroundedResult, VectorIndex};
use serde_json::{json, Value};
use sqlx::PgPool;
use std::sync::Arc;
use uuid::Uuid;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

#[derive(Debug, Clone, serde::Serialize)]
pub struct JobRegistration {
    pub key: &'static str,
    pub description: &'static str,
}

pub fn registry() -> Vec<JobRegistration> {
    vec![
        JobRegistration {
            key: "research-request",
            description: "Research request intake",
        },
        JobRegistration {
            key: "tool-gateway",
            description: "Tool gateway execution",
        },
    ]
}

pub fn router() -> Router {
    Router::new()
        .route("/", post(trigger_job))
        .route("/surfaces", get(list_surfaces))
        .route("/research", post(accept_research_request))
        .route("/tool-gateway", post(accept_tool_gateway_request))
}

async fn trigger_job() -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "jobs": registry(),
    }))
}

async fn list_surfaces() -> Json<Value> {
    Json(json!({
        "status": "ok",
        "surfaces": registry(),
    }))
}

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("jobs_internal_error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "jobs_internal_error", "detail": e.to_string() })),
    )
}

fn bad_request(message: &str) -> (StatusCode, Json<Value>) {
    (
        StatusCode::BAD_REQUEST,
        Json(json!({ "error": message })),
    )
}

#[axum::debug_handler]
pub async fn accept_research_request(
    Extension(auth): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Extension(settings): Extension<Arc<Settings>>,
    cache: Option<Extension<Arc<CacheService>>>,
    Json(request): Json<ResearchRequest>,
) -> AppResult<impl IntoResponse> {
    if request.org_id != auth.org_id {
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({"error": "org_mismatch"})),
        ));
    }

    let vector_index = VectorIndex::from_settings(settings.as_ref()).map_err(internal_error)?;
    let embedding = EmbeddingClient::from_settings(settings.as_ref());
    let cache = cache.map(|extension| extension.0);

    let result = process_research_request(
        &pool,
        cache.as_deref(),
        &vector_index,
        &embedding,
        request,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "status": "completed",
        "surface": "research-request",
        "run_id": result.run_id,
        "query": result.query,
        "citations_count": result.citations.len(),
        "total_chunks": result.total_chunks,
        "cache_hit": result.cache_hit,
        "citations": result.citations,
    })))
}

async fn process_research_request(
    pool: &PgPool,
    cache: Option<&CacheService>,
    vector_index: &VectorIndex,
    embedding: &EmbeddingClient,
    request: ResearchRequest,
) -> anyhow::Result<GroundedResult> {
    vector_index.ensure_collection().await?;

    let run_id = Uuid::new_v4();
    let request_kind = request_kind_str(&request.request_kind);
    let mut urls = request.required_sources.clone();
    if urls.is_empty() && matches!(request.request_kind, ResearchRequestKind::WebSearch) {
        urls = SearchDiscoverer::discover(&request.query, 5)
            .await?
            .into_iter()
            .map(|candidate| candidate.url)
            .collect();
    }
    if urls.is_empty() {
        return Err(anyhow::anyhow!("no_urls_available_for_research"));
    }

    sqlx::query(
        r#"
        INSERT INTO research.research_runs
        (run_id, org_id, request_id, parent_session_id, parent_agent_id, request_kind, query, status, urls_discovered, cache_hit)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'running', $8, false)
        "#,
    )
    .bind(run_id)
    .bind(request.org_id)
    .bind(&request.request_id)
    .bind(request.parent_session_id)
    .bind(&request.parent_agent_id)
    .bind(request_kind)
    .bind(&request.query)
    .bind(urls.len() as i32)
    .execute(pool)
    .await?;

    let mut urls_fetched = 0i32;
    let mut urls_failed = 0i32;
    let mut total_chunks = 0usize;
    let mut cache_hit = false;
    let fetcher = HttpFetcher::new();

    for url in &urls {
        let cache_key = format!("research:doc:{}:{}", request.org_id, AcquisitionHasher::compute_hash(url));
        let cached_document: Option<CachedDocument> = match cache {
            Some(service) => service.get(&cache_key).await.unwrap_or(None),
            None => None,
        };

        let fetched = if let Some(cached) = cached_document {
            cache_hit = true;
            Ok((
                cached.cleaned_text,
                cached.canonical_url,
                cached.domain,
                cached.title,
                "cached".to_string(),
                200i32,
            ))
        } else {
            fetch_and_parse(url, &fetcher, &request.request_kind).await
        };

        match fetched {
            Ok((cleaned_text, canonical_url, domain, title, fetch_mode, http_status)) => {
                let content_hash = AcquisitionHasher::compute_hash(&cleaned_text);
                let document_id = Uuid::new_v4();

                sqlx::query(
                    r#"
                    INSERT INTO research.research_documents
                    (document_id, org_id, discovered_via_run_id, url, canonical_url, domain, title, content_type, http_status, fetch_mode, cleaned_text, content_hash)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, 'text/html', $8, $9, $10, $11)
                    "#,
                )
                .bind(document_id)
                .bind(request.org_id)
                .bind(run_id)
                .bind(url)
                .bind(&canonical_url)
                .bind(&domain)
                .bind(&title)
                .bind(http_status)
                .bind(&fetch_mode)
                .bind(&cleaned_text)
                .bind(&content_hash)
                .execute(pool)
                .await?;

                write_audit_log(
                    pool,
                    request.org_id,
                    run_id,
                    Some(document_id),
                    "fetch_success",
                    Some(&domain),
                    Some(&canonical_url),
                    json!({ "fetch_mode": fetch_mode }),
                )
                .await?;

                let chunks = AcquisitionChunker::chunk_text(&cleaned_text);
                for (chunk_index, chunk_text) in chunks.iter().enumerate() {
                    total_chunks += 1;
                    let chunk_id = Uuid::new_v4();
                    let chunk_hash = raptorflow_research::ContentHasher::compute_hash(chunk_text);
                    let token_estimate = AcquisitionChunker::estimate_tokens(chunk_text);

                    sqlx::query(
                        r#"
                        INSERT INTO research.research_chunks
                        (chunk_id, org_id, document_id, chunk_index, token_estimate, content, content_hash, embedding_state)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')
                        "#,
                    )
                    .bind(chunk_id)
                    .bind(request.org_id)
                    .bind(document_id)
                    .bind(chunk_index as i32)
                    .bind(token_estimate as i32)
                    .bind(chunk_text)
                    .bind(&chunk_hash)
                    .execute(pool)
                    .await?;

                    match embedding.embed_text(chunk_text).await {
                        Ok(response) => {
                            if let Some(values) = response.embeddings.first().map(|vector| vector.values.clone()) {
                                vector_index
                                    .upsert_chunk(
                                        request.org_id,
                                        document_id,
                                        chunk_id,
                                        &domain,
                                        &canonical_url,
                                        chrono::Utc::now(),
                                        &chunk_text.chars().take(300).collect::<String>(),
                                        values,
                                    )
                                    .await?;

                                sqlx::query(
                                    r#"
                                    UPDATE research.research_chunks
                                    SET embedding_state = 'embedded', qdrant_point_id = $1
                                    WHERE chunk_id = $2 AND org_id = $3
                                    "#,
                                )
                                .bind(chunk_id.to_string())
                                .bind(chunk_id)
                                .bind(request.org_id)
                                .execute(pool)
                                .await?;
                            } else {
                                mark_chunk_failed(pool, request.org_id, chunk_id).await?;
                            }
                        }
                        Err(error) => {
                            write_audit_log(
                                pool,
                                request.org_id,
                                run_id,
                                Some(document_id),
                                "embedding_failed",
                                Some(&domain),
                                Some(&canonical_url),
                                json!({ "error": error.to_string(), "chunk_id": chunk_id }),
                            )
                            .await?;
                            mark_chunk_failed(pool, request.org_id, chunk_id).await?;
                        }
                    }
                }

                if let Some(service) = cache {
                    let _ = service
                        .set_with_ttl(
                            &cache_key,
                            &CachedDocument {
                                canonical_url: canonical_url.clone(),
                                domain: domain.clone(),
                                title: title.clone(),
                                cleaned_text: cleaned_text.clone(),
                            },
                            1800,
                        )
                        .await;
                }

                urls_fetched += 1;
            }
            Err(error) => {
                urls_failed += 1;
                let domain = UrlNormalizer::extract_domain(url).unwrap_or_else(|_| "unknown".to_string());
                let document_id = Uuid::new_v4();
                sqlx::query(
                    r#"
                    INSERT INTO research.research_documents
                    (document_id, org_id, discovered_via_run_id, url, domain, fetch_mode, fetch_error)
                    VALUES ($1, $2, $3, $4, $5, 'direct', $6)
                    "#,
                )
                .bind(document_id)
                .bind(request.org_id)
                .bind(run_id)
                .bind(url)
                .bind(&domain)
                .bind(error.to_string())
                .execute(pool)
                .await?;

                write_audit_log(
                    pool,
                    request.org_id,
                    run_id,
                    Some(document_id),
                    "fetch_failed",
                    Some(&domain),
                    Some(url),
                    json!({ "error": error.to_string() }),
                )
                .await?;
            }
        }
    }

    let query_embedding = embedding.embed_query(&request.query).await?;
    let query_vector = query_embedding
        .embeddings
        .first()
        .map(|value| value.values.clone())
        .ok_or_else(|| anyhow::anyhow!("empty_query_embedding"))?;
    let hits = vector_index.search(request.org_id, query_vector, 10).await?;

    let mut citations = Vec::new();
    for (index, hit) in hits.into_iter().enumerate() {
        let citation_id = Uuid::new_v4();
        sqlx::query(
            r#"
            INSERT INTO research.research_citations
            (citation_id, org_id, run_id, document_id, chunk_id, rank, snippet, relevance_score, source_domain, source_url)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            "#,
        )
        .bind(citation_id)
        .bind(request.org_id)
        .bind(run_id)
        .bind(hit.document_id)
        .bind(hit.chunk_id)
        .bind((index + 1) as i32)
        .bind(&hit.snippet)
        .bind(hit.score)
        .bind(&hit.source_domain)
        .bind(&hit.source_url)
        .execute(pool)
        .await?;

        citations.push(Citation {
            citation_id,
            rank: index + 1,
            snippet: hit.snippet,
            relevance_score: hit.score,
            source_domain: hit.source_domain,
            source_url: hit.source_url,
        });
    }

    let status = if urls_fetched == 0 {
        "failed"
    } else if urls_failed > 0 {
        "partial"
    } else {
        "completed"
    };

    sqlx::query(
        r#"
        UPDATE research.research_runs
        SET status = $1, cache_hit = $2, urls_fetched = $3, urls_failed = $4, completed_at = now()
        WHERE run_id = $5
        "#,
    )
    .bind(status)
    .bind(cache_hit)
    .bind(urls_fetched)
    .bind(urls_failed)
    .bind(run_id)
    .execute(pool)
    .await?;

    Ok(GroundedResult {
        query: request.query,
        run_id,
        citations,
        total_chunks,
        cache_hit,
    })
}

async fn fetch_and_parse(
    url: &str,
    fetcher: &HttpFetcher,
    request_kind: &ResearchRequestKind,
) -> anyhow::Result<(String, String, String, Option<String>, String, i32)> {
    let mut fetch_mode = "direct".to_string();
    let (cleaned_text, final_url, title) = match fetcher.fetch(url).await {
        Ok((body, final_url)) => {
            let html = String::from_utf8_lossy(&body).to_string();
            let parsed = HtmlParser::parse(&html)?;
            if matches!(request_kind, ResearchRequestKind::Browser)
                || HttpFetcher::should_fallback_to_browser(&html, &parsed)
            {
                fetch_mode = "browser".to_string();
                let (browser_html, browser_final_url) = BrowserFetcher::fetch(url).await?;
                let browser_parsed = HtmlParser::parse(&browser_html)?;
                (browser_parsed.cleaned_text, browser_final_url, browser_parsed.title)
            } else {
                (parsed.cleaned_text, final_url, parsed.title)
            }
        }
        Err(_) if matches!(request_kind, ResearchRequestKind::Browser) => {
            fetch_mode = "browser".to_string();
            let (browser_html, browser_final_url) = BrowserFetcher::fetch(url).await?;
            let browser_parsed = HtmlParser::parse(&browser_html)?;
            (browser_parsed.cleaned_text, browser_final_url, browser_parsed.title)
        }
        Err(error) => return Err(anyhow::anyhow!(error.to_string())),
    };

    let canonical_url = UrlNormalizer::canonical_url(url, &final_url).unwrap_or(final_url);
    let domain = UrlNormalizer::extract_domain(&canonical_url)?;
    Ok((cleaned_text, canonical_url, domain, title, fetch_mode, 200))
}

async fn mark_chunk_failed(pool: &PgPool, org_id: Uuid, chunk_id: Uuid) -> anyhow::Result<()> {
    sqlx::query(
        r#"
        UPDATE research.research_chunks
        SET embedding_state = 'failed'
        WHERE chunk_id = $1 AND org_id = $2
        "#,
    )
    .bind(chunk_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

async fn write_audit_log(
    pool: &PgPool,
    org_id: Uuid,
    run_id: Uuid,
    document_id: Option<Uuid>,
    event_type: &str,
    domain: Option<&str>,
    url: Option<&str>,
    event_data: Value,
) -> anyhow::Result<()> {
    sqlx::query(
        r#"
        INSERT INTO research.research_audit_log
        (org_id, run_id, document_id, event_type, domain, url, event_data)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        "#,
    )
    .bind(org_id)
    .bind(run_id)
    .bind(document_id)
    .bind(event_type)
    .bind(domain)
    .bind(url)
    .bind(event_data)
    .execute(pool)
    .await?;
    Ok(())
}

fn request_kind_str(request_kind: &ResearchRequestKind) -> &'static str {
    match request_kind {
        ResearchRequestKind::WebSearch => "web_search",
        ResearchRequestKind::Browser => "browser",
        ResearchRequestKind::CompetitiveAnalysis => "competitive_analysis",
        ResearchRequestKind::PerformanceAnalysis => "performance_analysis",
        ResearchRequestKind::ContentResearch => "content_research",
    }
}

#[derive(serde::Serialize, serde::Deserialize)]
struct CachedDocument {
    canonical_url: String,
    domain: String,
    title: Option<String>,
    cleaned_text: String,
}

pub async fn accept_tool_gateway_request(
    Extension(auth): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Extension(settings): Extension<Arc<Settings>>,
    cache: Option<Extension<Arc<CacheService>>>,
    Json(request): Json<ToolGatewayRequest>,
) -> AppResult<impl IntoResponse> {
    if request.org_id != auth.org_id {
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({"error": "org_mismatch"})),
        ));
    }

    let query = request
        .arguments
        .get("query")
        .and_then(|value| value.as_str())
        .unwrap_or_default()
        .trim()
        .to_string();
    if query.is_empty() {
        return Err(bad_request("tool_query_required"));
    }

    let required_sources = request
        .arguments
        .get("urls")
        .and_then(|value| value.as_array())
        .map(|items| {
            items
                .iter()
                .filter_map(|item| item.as_str().map(ToString::to_string))
                .collect::<Vec<String>>()
        })
        .unwrap_or_default();

    let request_kind = match request.tool_name.as_str() {
        "web_search" => ResearchRequestKind::WebSearch,
        "browser" => ResearchRequestKind::Browser,
        _ => return Err(bad_request("unsupported_tool_name")),
    };

    let research_request = ResearchRequest {
        org_id: request.org_id,
        request_id: request.request_id.clone(),
        parent_session_id: request.session_id.clone(),
        parent_agent_id: "tool-gateway".to_string(),
        request_kind,
        urgency: raptorflow_contracts::ResearchUrgency::Blocking,
        query,
        required_sources,
        output_format: "grounded_json".to_string(),
    };

    let vector_index = VectorIndex::from_settings(settings.as_ref()).map_err(internal_error)?;
    let embedding = EmbeddingClient::from_settings(settings.as_ref());
    let cache = cache.map(|extension| extension.0);

    let result = process_research_request(
        &pool,
        cache.as_deref(),
        &vector_index,
        &embedding,
        research_request,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "status": "completed",
        "surface": "tool-gateway",
        "tool_name": request.tool_name,
        "run_id": result.run_id,
        "citations_count": result.citations.len(),
        "cache_hit": result.cache_hit,
        "citations": result.citations,
    })))
}

pub async fn dispatch_intern_task(Json(request): Json<InternTask>) -> Json<Value> {
    Json(json!({
        "status": "not_exposed",
        "task_id": request.task_id,
    }))
}

pub async fn run_stream_coordinator(Json(request): Json<StreamCoordinatorRequest>) -> Json<Value> {
    Json(json!({
        "status": "not_exposed",
        "session_id": request.session_id,
    }))
}

pub async fn harvest_event(Json(request): Json<EventHarvesterRecord>) -> Json<Value> {
    Json(json!({
        "status": "not_exposed",
        "event_id": request.event_id,
    }))
}
