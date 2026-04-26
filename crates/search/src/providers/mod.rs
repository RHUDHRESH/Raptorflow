pub mod duckduckgo;
pub mod searxng;

use std::time::Duration;

use serde::{Deserialize, Serialize};

use crate::SearchError;

#[derive(Debug, Clone, Copy)]
pub struct RateLimit {
    pub requests_per_second: u32,
    pub max_burst: u32,
}

impl Default for RateLimit {
    fn default() -> Self {
        Self {
            requests_per_second: 1,
            max_burst: 3,
        }
    }
}

#[async_trait::async_trait]
pub trait SearchProvider: Send + Sync {
    async fn search(&self, query: &SearchQuery) -> Result<SearchResponse, SearchError>;
    fn provider_name(&self) -> &'static str;
    fn rate_limit(&self) -> RateLimit;
    fn request_timeout(&self) -> Duration;
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchQuery {
    pub query: String,
    #[serde(default = "default_max_results")]
    pub max_results: usize,
    #[serde(default)]
    pub search_depth: SearchDepth,
}

fn default_max_results() -> usize {
    10
}

impl SearchQuery {
    pub fn new(query: impl Into<String>) -> Self {
        Self {
            query: query.into(),
            max_results: 10,
            search_depth: SearchDepth::Moderate,
        }
    }

    pub fn with_max_results(mut self, n: usize) -> Self {
        self.max_results = n.clamp(1, 30);
        self
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum SearchDepth {
    #[default]
    Moderate,
    Deep,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub title: String,
    pub url: String,
    pub snippet: String,
    #[serde(default)]
    pub published_date: Option<chrono::DateTime<chrono::Utc>>,
    #[serde(default = "default_relevance")]
    pub relevance_score: f64,
}

fn default_relevance() -> f64 {
    0.5
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResponse {
    pub query: String,
    pub results: Vec<SearchResult>,
    pub total_results: usize,
    pub provider: String,
    #[serde(default)]
    pub cached: bool,
    pub search_time_ms: u64,
}
