use std::time::Duration;

use reqwest::Client;
use serde::Deserialize;

use super::SearchProvider;
use crate::SearchError;
use crate::providers::{RateLimit, SearchQuery, SearchResponse, SearchResult};

#[derive(Debug, Clone)]
pub struct SearXNGProvider {
    client: Client,
    base_url: String,
}

impl SearXNGProvider {
    pub fn new(base_url: impl Into<String>) -> Result<Self, SearchError> {
        let base_url = base_url.into().trim_end_matches('/').to_string();

        Ok(Self {
            client: Client::builder()
                .timeout(Duration::from_secs(30))
                .user_agent("RaptorFlow/1.0 (AI Marketing Platform)")
                .build()
                .map_err(|e| {
                    SearchError::Provider(format!("Failed to build reqwest Client: {e}"))
                })?,
            base_url,
        })
    }
}

#[async_trait::async_trait]
impl SearchProvider for SearXNGProvider {
    fn provider_name(&self) -> &'static str {
        "searxng"
    }

    fn rate_limit(&self) -> RateLimit {
        RateLimit {
            requests_per_second: 5,
            max_burst: 15,
        }
    }

    fn request_timeout(&self) -> Duration {
        Duration::from_secs(30)
    }

    async fn search(&self, query: &SearchQuery) -> Result<SearchResponse, SearchError> {
        let start = std::time::Instant::now();

        #[derive(Deserialize)]
        struct SearXNGResult {
            title: String,
            url: String,
            #[serde(default)]
            content: String,
            #[allow(dead_code)]
            engine: String,
            #[allow(dead_code)]
            score: f64,
            #[serde(default, rename = "publishedDate")]
            published_date: Option<String>,
        }

        #[derive(Deserialize)]
        struct SearXNGResponse {
            #[serde(default)]
            results: Vec<SearXNGResult>,
            #[serde(default)]
            number_of_results: usize,
        }

        let url = format!("{}/search", self.base_url);

        let response = self
            .client
            .get(&url)
            .query(&[
                ("q", query.query.as_str()),
                ("format", "json"),
                ("categories", "general"),
                ("language", "en"),
                ("pageno", "1"),
            ])
            .send()
            .await
            .map_err(|e| {
                if e.is_timeout() {
                    SearchError::Timeout(Duration::from_secs(30))
                } else if e.is_connect() {
                    SearchError::Provider(format!(
                        "SearXNG unreachable at {} — is the service running?",
                        self.base_url
                    ))
                } else {
                    SearchError::Network(e.to_string())
                }
            })?;

        if !response.status().is_success() {
            return Err(SearchError::Provider(format!(
                "SearXNG returned HTTP {}",
                response.status().as_u16()
            )));
        }

        let body: SearXNGResponse = response.json().await.map_err(|e| {
            SearchError::Provider(format!("Failed to parse SearXNG response: {}", e))
        })?;

        let results: Vec<SearchResult> = body
            .results
            .into_iter()
            .take(query.max_results)
            .enumerate()
            .map(|(i, r)| {
                let relevance = 1.0 - (i as f64 / query.max_results.max(1) as f64 * 0.4);
                SearchResult {
                    title: r.title,
                    url: r.url,
                    snippet: r.content,
                    published_date: r
                        .published_date
                        .and_then(|d| chrono::DateTime::parse_from_rfc3339(&d).ok())
                        .map(|d| d.with_timezone(&chrono::Utc)),
                    relevance_score: (relevance * 100.0).round() / 100.0,
                }
            })
            .collect();

        Ok(SearchResponse {
            query: query.query.clone(),
            results,
            total_results: body.number_of_results,
            provider: "searxng".to_string(),
            cached: false,
            search_time_ms: start.elapsed().as_millis() as u64,
        })
    }
}
