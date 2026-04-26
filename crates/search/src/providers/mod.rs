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

#[derive(Debug, Clone, Serialize)]
pub struct SearchQuery {
    pub query: String,
    pub max_results: usize,
    pub search_depth: SearchDepth,
}

impl<'de> Deserialize<'de> for SearchQuery {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        #[derive(Deserialize)]
        struct RawSearchQuery {
            query: String,
            #[serde(default)]
            max_results: Option<usize>,
            #[serde(default)]
            search_depth: SearchDepth,
        }

        let raw = RawSearchQuery::deserialize(deserializer)?;
        let max_results = raw.max_results.unwrap_or(10).clamp(1, 30);

        Ok(SearchQuery {
            query: raw.query,
            max_results,
            search_depth: raw.search_depth,
        })
    }
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

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json;

    #[test]
    fn test_deserialize_max_results_zero_clamped_to_one() {
        let json = r#"{"query": "test", "max_results": 0}"#;
        let query: SearchQuery = serde_json::from_str(json).unwrap();
        assert_eq!(query.max_results, 1);
    }

    #[test]
    fn test_deserialize_max_results_above_max_clamped_to_thirty() {
        let json = r#"{"query": "test", "max_results": 100}"#;
        let query: SearchQuery = serde_json::from_str(json).unwrap();
        assert_eq!(query.max_results, 30);
    }

    #[test]
    fn test_deserialize_max_results_within_range_unchanged() {
        let json = r#"{"query": "test", "max_results": 5}"#;
        let query: SearchQuery = serde_json::from_str(json).unwrap();
        assert_eq!(query.max_results, 5);
    }

    #[test]
    fn test_deserialize_without_max_results_uses_default() {
        let json = r#"{"query": "test"}"#;
        let query: SearchQuery = serde_json::from_str(json).unwrap();
        assert_eq!(query.max_results, 10);
    }
}
