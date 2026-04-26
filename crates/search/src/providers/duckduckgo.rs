use std::time::Duration;

use reqwest::Client;

use super::SearchProvider;
use crate::providers::{RateLimit, SearchQuery, SearchResponse, SearchResult};
use crate::SearchError;

#[derive(Debug, Clone)]
pub struct DuckDuckGoProvider {
    client: Client,
}

impl DuckDuckGoProvider {
    pub fn new() -> Self {
        Self {
            client: Client::builder()
                .timeout(Duration::from_secs(25))
                .user_agent("RaptorFlow/1.0 (AI Marketing Platform; +https://raptorflow.ai)")
                .build()
                .expect("reqwest Client construction is infallible"),
        }
    }
}

impl Default for DuckDuckGoProvider {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait::async_trait]
impl SearchProvider for DuckDuckGoProvider {
    fn provider_name(&self) -> &'static str {
        "duckduckgo"
    }

    fn rate_limit(&self) -> RateLimit {
        RateLimit {
            requests_per_second: 1,
            max_burst: 2,
        }
    }

    fn request_timeout(&self) -> Duration {
        Duration::from_secs(25)
    }

    async fn search(&self, query: &SearchQuery) -> Result<SearchResponse, SearchError> {
        let start = std::time::Instant::now();

        let html = self
            .client
            .get("https://html.duckduckgo.com/html/")
            .query(&[("q", query.query.as_str())])
            .header("Accept", "text/html")
            .send()
            .await
            .map_err(|e| {
                if e.is_timeout() {
                    SearchError::Timeout(Duration::from_secs(25))
                } else {
                    SearchError::Network(e.to_string())
                }
            })?;

        if !html.status().is_success() {
            return Err(SearchError::Provider(format!(
                "DuckDuckGo returned HTTP {}",
                html.status().as_u16()
            )));
        }

        let body = html.text().await.map_err(|e| {
            SearchError::Network(format!("Failed to read DuckDuckGo response: {}", e))
        })?;

        let results = parse_ddg_html(&body, query.max_results);

        Ok(SearchResponse {
            query: query.query.clone(),
            results,
            total_results: 0,
            provider: "duckduckgo".to_string(),
            cached: false,
            search_time_ms: start.elapsed().as_millis() as u64,
        })
    }
}

fn parse_ddg_html(html: &str, max_results: usize) -> Vec<SearchResult> {
    let mut results = Vec::new();
    let document = scraper::Html::parse_document(html);

    let result_sel = scraper::Selector::parse(".result").unwrap();
    let title_sel = scraper::Selector::parse(".result__title a").unwrap();
    let snippet_sel = scraper::Selector::parse(".result__snippet").unwrap();
    let url_sel = scraper::Selector::parse(".result__url").unwrap();

    for (i, result_node) in document.select(&result_sel).enumerate() {
        if i >= max_results {
            break;
        }

        let title: Option<String> = result_node
            .select(&title_sel)
            .next()
            .map(|el: scraper::ElementRef| {
                el.text().collect::<String>().trim().to_string()
            })
            .filter(|t: &String| !t.is_empty());

        let url: Option<String> = result_node
            .select(&url_sel)
            .next()
            .map(|el: scraper::ElementRef| {
                let text = el.text().collect::<String>().trim().to_string();
                text.strip_prefix("udg_").unwrap_or(&text).to_string()
            })
            .filter(|u: &String| !u.is_empty());

        let snippet: String = result_node
            .select(&snippet_sel)
            .next()
            .map(|el: scraper::ElementRef| {
                el.text().collect::<String>().trim().to_string()
            })
            .unwrap_or_default();

        if let (Some(title), Some(url)) = (title, url) {
            let relevance = 1.0 - (i as f64 / max_results.max(1) as f64 * 0.5);
            results.push(SearchResult {
                title,
                url,
                snippet,
                published_date: None,
                relevance_score: (relevance * 100.0).round() / 100.0,
            });
        }
    }

    results
}
