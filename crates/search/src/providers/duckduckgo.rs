use std::time::Duration;

use reqwest::Client;
use tracing::warn;

use super::SearchProvider;
use crate::SearchError;
use crate::providers::{RateLimit, SearchQuery, SearchResponse, SearchResult};

fn normalize_url(href: &str) -> Option<String> {
    let href = if let Some(encoded) = href.strip_prefix("/l/?uddg=") {
        urlencoding_decode(encoded)?
    } else {
        href.to_string()
    };

    let href = if href.starts_with("//") {
        format!("https:{}", href)
    } else {
        href
    };

    if href.starts_with("http://") || href.starts_with("https://") {
        Some(href)
    } else {
        None
    }
}

fn urlencoding_decode(input: &str) -> Option<String> {
    let mut result = String::with_capacity(input.len());
    let mut chars = input.chars().peekable();

    while let Some(c) = chars.next() {
        if c == '%' {
            let hex: String = chars.by_ref().take(2).collect();
            if hex.len() == 2 {
                let byte = u8::from_str_radix(&hex, 16).ok()?;
                result.push(byte as char);
            } else {
                return None;
            }
        } else if c == '+' {
            result.push(' ');
        } else {
            result.push(c);
        }
    }

    Some(result)
}

fn detect_ddg_block_or_anomaly(html: &str) -> Option<&'static str> {
    let lower = html.to_lowercase();
    let markers = [
        ("anomaly", "anomaly"),
        ("unusual traffic", "unusual traffic"),
        ("captcha", "captcha"),
        ("automated", "automated"),
        ("bot", "bot"),
        ("verify you are human", "verify you are human"),
        ("please prove you are human", "please prove you are human"),
        ("rate limit", "rate limit"),
        ("too many requests", "too many requests"),
        ("blocked", "blocked"),
    ];
    for (marker, name) in markers {
        if lower.contains(marker) {
            return Some(name);
        }
    }
    None
}

#[derive(Debug, Clone)]
pub struct DuckDuckGoProvider {
    client: Client,
}

impl DuckDuckGoProvider {
    pub fn new() -> Result<Self, SearchError> {
        Ok(Self {
            client: Client::builder()
                .timeout(Duration::from_secs(25))
                .user_agent("RaptorFlow/1.0 (AI Marketing Platform; +https://raptorflow.ai)")
                .build()
                .map_err(|e| {
                    SearchError::Provider(format!("Failed to build reqwest Client: {e}"))
                })?,
        })
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

        if let Some(reason) = detect_ddg_block_or_anomaly(&body) {
            warn!(
                provider = "duckduckgo",
                reason = reason,
                "DuckDuckGo anomaly/block page detected"
            );
            return Err(SearchError::RateLimited {
                retry_after: Duration::from_secs(60),
            });
        }

        let results = parse_ddg_html(&body, query.max_results);

        if results.is_empty() {
            if body.to_lowercase().contains("no results for") {
                return Ok(SearchResponse {
                    query: query.query.clone(),
                    results: vec![],
                    total_results: 0,
                    provider: "duckduckgo".to_string(),
                    cached: false,
                    search_time_ms: start.elapsed().as_millis() as u64,
                });
            } else {
                return Err(SearchError::Provider(
                    "DuckDuckGo returned empty/unparseable page; possible layout change or soft block"
                        .into(),
                ));
            }
        }

        let total_results = results.len();

        Ok(SearchResponse {
            query: query.query.clone(),
            results,
            total_results,
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

    for (i, result_node) in document.select(&result_sel).enumerate() {
        if i >= max_results {
            break;
        }

        let title: Option<String> = result_node
            .select(&title_sel)
            .next()
            .map(|el: scraper::ElementRef| el.text().collect::<String>().trim().to_string())
            .filter(|t: &String| !t.is_empty());

        let url: Option<String> = result_node
            .select(&title_sel)
            .next()
            .and_then(|el: scraper::ElementRef| el.value().attr("href"))
            .and_then(|href: &str| normalize_url(href));

        let snippet: String = result_node
            .select(&snippet_sel)
            .next()
            .map(|el: scraper::ElementRef| el.text().collect::<String>().trim().to_string())
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_normalize_url_direct_https() {
        assert_eq!(
            normalize_url("https://example.com/path"),
            Some("https://example.com/path".to_string())
        );
    }

    #[test]
    fn test_normalize_url_ddg_redirect() {
        assert_eq!(
            normalize_url("/l/?uddg=https%3A%2F%2Fexample.com%2Fpath"),
            Some("https://example.com/path".to_string())
        );
    }

    #[test]
    fn test_normalize_url_scheme_relative() {
        assert_eq!(
            normalize_url("//example.com/path"),
            Some("https://example.com/path".to_string())
        );
    }

    #[test]
    fn test_normalize_url_invalid_no_scheme() {
        assert_eq!(normalize_url("example.com/path"), None);
    }

    #[test]
    fn test_normalize_url_http() {
        assert_eq!(
            normalize_url("http://example.com/path"),
            Some("http://example.com/path".to_string())
        );
    }

    #[test]
    fn test_urlencoding_decode() {
        assert_eq!(
            urlencoding_decode("https%3A%2F%2Fexample.com%2Ftest"),
            Some("https://example.com/test".to_string())
        );
    }

    #[test]
    fn test_urlencoding_decode_with_plus() {
        assert_eq!(
            urlencoding_decode("hello+world"),
            Some("hello world".to_string())
        );
    }

    #[test]
    fn test_detect_ddg_block_anomaly() {
        assert_eq!(
            detect_ddg_block_or_anomaly("Anomaly detected"),
            Some("anomaly")
        );
    }

    #[test]
    fn test_detect_ddg_block_unusual_traffic() {
        assert_eq!(
            detect_ddg_block_or_anomaly("Unusual traffic"),
            Some("unusual traffic")
        );
    }

    #[test]
    fn test_detect_ddg_block_captcha() {
        assert_eq!(
            detect_ddg_block_or_anomaly("CAPTCHA required"),
            Some("captcha")
        );
    }

    #[test]
    fn test_detect_ddg_block_normal_page() {
        let normal_html = r#"
            <html>
            <body>
                <div class="result">
                    <a href="http://example.com">Example</a>
                </div>
            </body>
            </html>
        "#;
        assert_eq!(detect_ddg_block_or_anomaly(normal_html), None);
    }

    #[test]
    fn test_detect_ddg_block_empty_non_block() {
        let empty_html = "<html><body></body></html>";
        assert_eq!(detect_ddg_block_or_anomaly(empty_html), None);
    }
}
