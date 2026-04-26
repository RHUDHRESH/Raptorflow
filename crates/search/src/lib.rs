pub mod cache;
pub mod client;
pub mod providers;

pub use client::SearchClient;
pub use providers::{SearchDepth, SearchQuery, SearchResponse, SearchResult};
pub use providers::duckduckgo::DuckDuckGoProvider;
pub use providers::searxng::SearXNGProvider;

#[derive(Debug, thiserror::Error)]
pub enum SearchError {
    #[error("Provider error: {0}")]
    Provider(String),

    #[error("Rate limited — retry after {retry_after:?}")]
    RateLimited { retry_after: std::time::Duration },

    #[error("Request timed out after {0:?}")]
    Timeout(std::time::Duration),

    #[error("Network error: {0}")]
    Network(String),

    #[error("No results found for query")]
    NoResults,

    #[error("Invalid query: {0}")]
    InvalidQuery(String),
}
