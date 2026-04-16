//! Web content acquisition layer for RaptorFlow intel.
//!
//! This crate provides the truthy fetch and discovery primitives used by
//! Block 1.5: direct HTTP fetches, browser-rendered fallback, HTML extraction,
//! URL normalization, domain throttling, and query discovery from public search
//! result pages.

use bytes::Bytes;
use chromiumoxide::browser::{Browser, BrowserConfig};
use chrono::Utc;
use futures::StreamExt;
use governor::{DefaultDirectRateLimiter, Quota};
use reqwest::Client;
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    collections::HashMap,
    num::NonZeroU32,
    sync::{Arc, OnceLock},
    time::Duration,
};
use thiserror::Error;
use tokio::sync::Mutex;
use uuid::Uuid;

const MAX_BODY_SIZE: usize = 10 * 1024 * 1024;
const FETCH_TIMEOUT: Duration = Duration::from_secs(30);
const DOMAIN_FETCHES_PER_MINUTE: u32 = 6;

static DOMAIN_LIMITERS: OnceLock<Mutex<HashMap<String, Arc<DefaultDirectRateLimiter>>>> =
    OnceLock::new();

fn limiter_registry() -> &'static Mutex<HashMap<String, Arc<DefaultDirectRateLimiter>>> {
    DOMAIN_LIMITERS.get_or_init(|| Mutex::new(HashMap::new()))
}

#[derive(Debug, Error)]
pub enum AcquisitionError {
    #[error("Network error: {0}")]
    Network(String),
    #[error("Timeout: {0}")]
    Timeout(String),
    #[error("Content too large: {size} bytes")]
    ContentTooLarge { size: usize },
    #[error("Invalid content type: {0}")]
    InvalidContentType(String),
    #[error("Invalid URL: {0}")]
    InvalidUrl(String),
    #[error("Browser error: {0}")]
    Browser(String),
    #[error("Search discovery error: {0}")]
    Discovery(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FetchResult {
    pub document_id: Uuid,
    pub url: String,
    pub canonical_url: String,
    pub domain: String,
    pub title: Option<String>,
    pub content_type: Option<String>,
    pub language: Option<String>,
    pub http_status: u16,
    pub fetch_mode: String,
    pub cleaned_text: String,
    pub content_hash: String,
    pub fetched_at: chrono::DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParsedHtml {
    pub title: Option<String>,
    pub cleaned_text: String,
    pub language: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchCandidate {
    pub url: String,
    pub title: Option<String>,
}

pub struct UrlNormalizer;

impl UrlNormalizer {
    pub fn canonical_url(_url: &str, response_url: &str) -> Result<String, AcquisitionError> {
        let response_parsed = url::Url::parse(response_url)
            .map_err(|e| AcquisitionError::InvalidUrl(e.to_string()))?;

        let mut canonical = response_parsed;
        canonical.set_fragment(None);
        canonical.set_query(None);

        if canonical.scheme() == "http" {
            let _ = canonical.set_scheme("https");
        }

        Ok(canonical.to_string())
    }

    pub fn extract_domain(url_str: &str) -> Result<String, AcquisitionError> {
        let url =
            url::Url::parse(url_str).map_err(|e| AcquisitionError::InvalidUrl(e.to_string()))?;
        url.host_str()
            .map(|h| h.to_lowercase())
            .ok_or_else(|| AcquisitionError::InvalidUrl("No host".to_string()))
    }

    pub fn maybe_decode_redirect(url_str: &str) -> Option<String> {
        let parsed = url::Url::parse(url_str).ok()?;
        if parsed.domain()?.contains("duckduckgo.com") {
            parsed
                .query_pairs()
                .find(|(key, _)| key == "uddg")
                .map(|(_, value)| value.to_string())
        } else {
            None
        }
    }
}

pub struct HtmlParser;

impl HtmlParser {
    pub fn parse(html_body: &str) -> Result<ParsedHtml, AcquisitionError> {
        let document = Html::parse_document(html_body);

        let title = Self::extract_title(&document);
        let cleaned_text = Self::extract_main_content(&document);
        let language = Self::detect_language(&document);

        Ok(ParsedHtml {
            title,
            cleaned_text,
            language,
        })
    }

    pub fn extract_search_candidates(html_body: &str, limit: usize) -> Vec<SearchCandidate> {
        let document = Html::parse_document(html_body);
        let selector = match Selector::parse("a[href]") {
            Ok(selector) => selector,
            Err(_) => return Vec::new(),
        };

        let mut results = Vec::new();

        for element in document.select(&selector) {
            let Some(href) = element.value().attr("href") else {
                continue;
            };

            let candidate = UrlNormalizer::maybe_decode_redirect(href)
                .unwrap_or_else(|| href.to_string());

            if !(candidate.starts_with("http://") || candidate.starts_with("https://")) {
                continue;
            }

            let title = element.text().collect::<String>().trim().to_string();
            let title = if title.is_empty() { None } else { Some(title) };

            results.push(SearchCandidate {
                url: candidate,
                title,
            });

            if results.len() >= limit {
                break;
            }
        }

        results
    }

    fn extract_title(document: &Html) -> Option<String> {
        let selector = Selector::parse("title").ok()?;
        document
            .select(&selector)
            .next()
            .map(|el| el.text().collect::<String>().trim().to_string())
            .filter(|t| !t.is_empty())
    }

    fn extract_main_content(document: &Html) -> String {
        let text_selector = Selector::parse("main, article, section, p, li, td, div, span").ok();

        let mut content = Vec::new();

        if let Some(sel) = text_selector {
            for element in document.select(&sel) {
                let text = element.text().collect::<String>().trim().to_string();
                if text.len() > 20 {
                    content.push(text);
                }
            }
        }

        content.join("\n")
    }

    fn detect_language(document: &Html) -> Option<String> {
        let selector = Selector::parse("html[lang]").ok()?;
        document
            .select(&selector)
            .next()
            .and_then(|el| el.value().attr("lang"))
            .map(|l| l.split('-').next().unwrap_or(l).to_lowercase())
    }
}

pub struct HttpFetcher {
    client: Client,
}

impl HttpFetcher {
    pub fn new() -> Self {
        let client = Client::builder()
            .timeout(FETCH_TIMEOUT)
            .redirect(reqwest::redirect::Policy::limited(5))
            .user_agent("RaptorFlowBot/0.1 (+https://raptorflow.dev/bot)")
            .build()
            .unwrap_or_else(|_| Client::new());

        Self { client }
    }

    async fn wait_for_domain_slot(domain: &str) -> Result<(), AcquisitionError> {
        let limiter = {
            let mut registry = limiter_registry().lock().await;
            registry
                .entry(domain.to_string())
                .or_insert_with(|| {
                    Arc::new(governor::RateLimiter::direct(
                        Quota::per_minute(NonZeroU32::new(DOMAIN_FETCHES_PER_MINUTE).unwrap()),
                    ))
                })
                .clone()
        };

        limiter
            .until_ready()
            .await;

        Ok(())
    }

    pub async fn fetch(&self, url_str: &str) -> Result<(Bytes, String), AcquisitionError> {
        let domain = UrlNormalizer::extract_domain(url_str)?;
        Self::wait_for_domain_slot(&domain).await?;

        let response = self
            .client
            .get(url_str)
            .send()
            .await
            .map_err(|e| AcquisitionError::Network(e.to_string()))?;

        let status = response.status();
        let final_url = response.url().to_string();

        if !status.is_success() {
            return Err(AcquisitionError::Network(format!("HTTP {status}")));
        }

        let content_type = response
            .headers()
            .get("content-type")
            .and_then(|v| v.to_str().ok())
            .map(|s| s.split(';').next().unwrap_or(s).trim().to_string())
            .unwrap_or_default();

        let allowed_types = ["text/html", "application/xhtml+xml", "text/plain"];
        if !allowed_types.iter().any(|ct| content_type.contains(ct)) {
            return Err(AcquisitionError::InvalidContentType(content_type));
        }

        let body = response
            .bytes()
            .await
            .map_err(|e| AcquisitionError::Network(e.to_string()))?;

        if body.len() > MAX_BODY_SIZE {
            return Err(AcquisitionError::ContentTooLarge { size: body.len() });
        }

        Ok((body, final_url))
    }

    pub fn should_fallback_to_browser(html_body: &str, parsed: &ParsedHtml) -> bool {
        parsed.cleaned_text.trim().len() < 200
            || html_body.contains("__NEXT_DATA__")
            || html_body.contains("window.__INITIAL_STATE__")
            || html_body.matches("<script").count() > 10
    }
}

impl Default for HttpFetcher {
    fn default() -> Self {
        Self::new()
    }
}

pub struct BrowserFetcher;

impl BrowserFetcher {
    pub async fn fetch(url: &str) -> Result<(String, String), AcquisitionError> {
        let config = BrowserConfig::builder()
            .no_sandbox()
            .build()
            .map_err(|e| AcquisitionError::Browser(e.to_string()))?;

        let (mut browser, mut handler) =
            Browser::launch(config).await.map_err(|e| AcquisitionError::Browser(e.to_string()))?;

        let handler_task = tokio::spawn(async move {
            while let Some(result) = handler.next().await {
                if result.is_err() {
                    break;
                }
            }
        });

        let page = browser
            .new_page(url)
            .await
            .map_err(|e| AcquisitionError::Browser(e.to_string()))?;

        page.wait_for_navigation()
            .await
            .map_err(|e| AcquisitionError::Browser(e.to_string()))?;

        let html = page
            .content()
            .await
            .map_err(|e| AcquisitionError::Browser(e.to_string()))?;

        let final_url = page
            .url()
            .await
            .ok()
            .flatten()
            .unwrap_or_else(|| url.to_string());
        let _ = browser.close().await;
        handler_task.abort();

        Ok((html, final_url))
    }
}

pub struct SearchDiscoverer;

impl SearchDiscoverer {
    pub async fn discover(query: &str, limit: usize) -> Result<Vec<SearchCandidate>, AcquisitionError> {
        let query = url::form_urlencoded::Serializer::new(String::new())
            .append_pair("q", query)
            .finish();
        let search_url = format!("https://duckduckgo.com/html/?{query}");
        let (html, _) = BrowserFetcher::fetch(&search_url).await?;
        let candidates = HtmlParser::extract_search_candidates(&html, limit);

        if candidates.is_empty() {
            return Err(AcquisitionError::Discovery(
                "no_search_candidates_discovered".to_string(),
            ));
        }

        Ok(candidates)
    }
}

pub struct Chunker;

impl Chunker {
    const TARGET_CHUNK_SIZE: usize = 512;

    pub fn chunk_text(text: &str) -> Vec<String> {
        let words: Vec<&str> = text.split_whitespace().collect();
        if words.is_empty() {
            return vec![];
        }

        let target_words = Self::TARGET_CHUNK_SIZE;
        let mut chunks = Vec::new();
        let mut start = 0;

        while start < words.len() {
            let end = (start + target_words).min(words.len());
            let chunk: String = words[start..end].join(" ");

            if !chunk.trim().is_empty() {
                chunks.push(chunk.trim().to_string());
            }

            if end >= words.len() {
                break;
            }

            start = end;
        }

        chunks
    }

    pub fn estimate_tokens(text: &str) -> usize {
        text.split_whitespace().count()
    }
}

pub struct ContentHasher;

impl ContentHasher {
    pub fn compute_hash(content: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(content.as_bytes());
        hex::encode(hasher.finalize())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_domain_extraction() {
        let domain = UrlNormalizer::extract_domain("https://www.example.com/path").unwrap();
        assert_eq!(domain, "www.example.com");
    }

    #[test]
    fn test_content_hash() {
        let hash1 = ContentHasher::compute_hash("hello world");
        let hash2 = ContentHasher::compute_hash("hello world");
        let hash3 = ContentHasher::compute_hash("hello world!");
        assert_eq!(hash1, hash2);
        assert_ne!(hash1, hash3);
    }

    #[test]
    fn test_chunker() {
        let text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10";
        let chunks = Chunker::chunk_text(text);
        assert!(!chunks.is_empty());
        assert!(chunks.iter().all(|c| !c.is_empty()));
    }

    #[test]
    fn test_html_parser() {
        let html =
            r#"<html><head><title>Test</title></head><body><main><p>Hello world from parser</p></main></body></html>"#;
        let parsed = HtmlParser::parse(html).unwrap();
        assert_eq!(parsed.title, Some("Test".to_string()));
        assert!(parsed.cleaned_text.contains("Hello world from parser"));
    }

    #[test]
    fn test_extract_search_candidates_decodes_duckduckgo_redirects() {
        let html = r#"
            <html><body>
            <a href="https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage">Example</a>
            </body></html>
        "#;

        let candidates = HtmlParser::extract_search_candidates(html, 5);
        assert_eq!(candidates.len(), 1);
        assert_eq!(candidates[0].url, "https://example.com/page");
    }
}
