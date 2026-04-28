use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Semaphore;
use tracing::instrument;

use crate::SearchError;
use crate::cache::SearchCache;
use crate::providers::duckduckgo::DuckDuckGoProvider;
use crate::providers::searxng::SearXNGProvider;
use crate::providers::{SearchProvider, SearchQuery, SearchResponse};

const MAX_RETRIES: u32 = 3;
const BASE_BACKOFF_MS: u64 = 1000;
const MAX_BACKOFF_MS: u64 = 16000;

#[derive(Clone)]
pub struct SearchClient {
    primary: Arc<dyn SearchProvider>,
    fallback: Arc<dyn SearchProvider>,
    cache: Arc<SearchCache>,
    semaphore: Arc<Semaphore>,
}

impl SearchClient {
    pub fn searxng_with_ddg_fallback(
        searxng_url: String,
        cache_ttl: Duration,
    ) -> Result<Self, SearchError> {
        Ok(Self {
            primary: Arc::new(SearXNGProvider::new(searxng_url)?),
            fallback: Arc::new(DuckDuckGoProvider::new()?),
            cache: Arc::new(SearchCache::new(cache_ttl, 200)),
            semaphore: Arc::new(Semaphore::new(10)),
        })
    }

    pub fn duckduckgo_only(cache_ttl: Duration) -> Result<Self, SearchError> {
        let ddg = Arc::new(DuckDuckGoProvider::new()?);
        Ok(Self {
            primary: ddg.clone(),
            fallback: ddg,
            cache: Arc::new(SearchCache::new(cache_ttl, 200)),
            semaphore: Arc::new(Semaphore::new(3)),
        })
    }

    #[instrument(skip(self), fields(query = %query.query))]
    pub async fn search(&self, query: &SearchQuery) -> Result<SearchResponse, SearchError> {
        if query.query.trim().is_empty() {
            return Err(SearchError::InvalidQuery("query must not be empty".into()));
        }

        if let Some(cached) = self.cache.get(&query.query, query.max_results).await {
            tracing::debug!(query = %query.query, results = cached.results.len(), "Search cache hit");
            return Ok(cached);
        }

        let _permit = self
            .semaphore
            .acquire()
            .await
            .map_err(|_| SearchError::Provider("Semaphore closed".into()))?;

        let same = std::ptr::addr_eq(Arc::as_ptr(&self.primary), Arc::as_ptr(&self.fallback));
        let mut last_error = None;

        'providers: for (idx, provider) in [&self.primary, &self.fallback].iter().enumerate() {
            if idx == 1 && same {
                continue;
            }
            for attempt in 0..=MAX_RETRIES {
                match provider.search(query).await {
                    Ok(response) => {
                        self.cache
                            .insert(&query.query, query.max_results, response.clone())
                            .await;
                        return Ok(response);
                    }
                    Err(e) => {
                        let retryable = matches!(
                            &e,
                            SearchError::RateLimited { .. }
                                | SearchError::Network(_)
                                | SearchError::Timeout(_)
                        );
                        if !retryable || attempt == MAX_RETRIES {
                            last_error = Some(e);
                            continue 'providers;
                        }
                        let backoff = Duration::from_millis(
                            (BASE_BACKOFF_MS * 2u64.pow(attempt)).min(MAX_BACKOFF_MS),
                        );
                        tokio::time::sleep(backoff).await;
                        last_error = Some(e);
                    }
                }
            }
        }

        Err(last_error.unwrap_or(SearchError::Provider("All providers exhausted".into())))
    }

    pub fn primary_provider_name(&self) -> &'static str {
        self.primary.provider_name()
    }
}
