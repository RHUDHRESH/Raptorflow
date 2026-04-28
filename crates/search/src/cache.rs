use std::collections::HashMap;
use std::time::{Duration, Instant};
use tokio::sync::RwLock;

use crate::providers::SearchResponse;

struct CacheEntry {
    response: SearchResponse,
    inserted_at: Instant,
}

pub struct SearchCache {
    entries: RwLock<HashMap<String, CacheEntry>>,
    ttl: Duration,
    max_entries: usize,
}

impl SearchCache {
    pub fn new(ttl: Duration, max_entries: usize) -> Self {
        Self {
            entries: RwLock::new(HashMap::new()),
            ttl,
            max_entries,
        }
    }

    fn make_key(query: &str, max_results: usize) -> String {
        format!("q={}|n={}", query.to_lowercase().trim(), max_results)
    }

    pub async fn get(&self, query: &str, max_results: usize) -> Option<SearchResponse> {
        let key = Self::make_key(query, max_results);
        let entries = self.entries.read().await;
        if let Some(entry) = entries.get(&key) {
            if entry.inserted_at.elapsed() < self.ttl {
                let mut resp = entry.response.clone();
                resp.cached = true;
                return Some(resp);
            }
        }
        None
    }

    pub async fn insert(&self, query: &str, max_results: usize, response: SearchResponse) {
        let key = Self::make_key(query, max_results);
        let mut entries = self.entries.write().await;

        if entries.len() >= self.max_entries {
            if let Some(old_key) = entries
                .iter()
                .min_by_key(|(_, e)| e.inserted_at)
                .map(|(k, _)| k.clone())
            {
                entries.remove(&old_key);
            }
        }

        entries.insert(
            key,
            CacheEntry {
                response,
                inserted_at: Instant::now(),
            },
        );
    }
}
