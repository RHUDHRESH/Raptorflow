//! Google Cloud Platform (GCP) inference client for RaptorFlow.
//!
//! Wraps the Gemini REST API via reqwest. Supports content generation with optional
//! context caching to reduce inference cost. This is the ONLY crate that makes
//! external HTTP calls to Gemini.
//!
//! ## Model tiers
//!
//! | Model | Tier | Used for |
//! |---|---|---|
//! | `gemini-pro` | Strategist | Complex synthesis tasks |
//! | `gemini-flash-lite` | Council/Generation | Fast council reasoning, content generation |
//!
//! ## Context caching
//!
//! Foundation JSON can be cached server-side via [`GcpInferenceService::create_foundation_cache`]
//! and reused across requests, significantly reducing token cost.
//!
//! ## Error handling
//!
//! [`GcpError`] is a typed enum — `Network`, `Parse`, `Api(status, body)`, `Config`.

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::sync::Arc;

const BASE_URL: &str = "https://generativelanguage.googleapis.com/v1beta";

#[derive(Clone)]
pub struct GeminiClient {
    client: Client,
    api_key: String,
}

impl GeminiClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
        }
    }

    pub fn from_settings(settings: &raptorflow_config::Settings) -> Self {
        Self::new(settings.gcp_api_key.clone())
    }

    pub async fn generate_content(
        &self,
        model: &str,
        prompt: &str,
    ) -> Result<GenerateContentResponse, GcpError> {
        let request = GenerateContentRequest {
            contents: vec![Content {
                role: "user".to_string(),
                parts: vec![Part { text: prompt.to_string() }],
            }],
            generation_config: Some(GenerationConfig {
                temperature: Some(0.7),
                max_output_tokens: Some(2048),
                top_p: Some(0.9),
                top_k: Some(40),
            }),
            system_instruction: None,
            cached_content: None,
        };

        let url = format!(
            "{}/models/{}:generateContent?key={}",
            BASE_URL, model, self.api_key
        );

        let response = self
            .client
            .post(&url)
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| GcpError::Network(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| GcpError::Parse(e.to_string()))
        } else {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            tracing::error!(status = %status, body = %text, "Gemini API error");
            Err(GcpError::Api(status.as_u16(), text))
        }
    }

    pub async fn generate_content_with_context(
        &self,
        model: &str,
        prompt: &str,
        context: &str,
        cache_name: Option<&str>,
    ) -> Result<GenerateContentResponse, GcpError> {
        let system_instruction = Some(Part {
            text: context.to_string(),
        });

        let request = GenerateContentRequest {
            contents: vec![Content {
                role: "user".to_string(),
                parts: vec![Part { text: prompt.to_string() }],
            }],
            generation_config: Some(GenerationConfig {
                temperature: Some(0.7),
                max_output_tokens: Some(2048),
                top_p: Some(0.9),
                top_k: Some(40),
            }),
            system_instruction,
            cached_content: cache_name.map(|s| s.to_string()),
        };

        let url = format!(
            "{}/models/{}:generateContent?key={}",
            BASE_URL, model, self.api_key
        );

        let response = self
            .client
            .post(&url)
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| GcpError::Network(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| GcpError::Parse(e.to_string()))
        } else {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            Err(GcpError::Api(status.as_u16(), text))
        }
    }

    pub async fn create_cached_content(
        &self,
        model: &str,
        contents: &str,
        system_instruction: Option<&str>,
        ttl_seconds: Option<i64>,
    ) -> Result<CachedContent, GcpError> {
        let parts = vec![Part {
            text: contents.to_string(),
        }];

        let request = CreateCachedContentRequest {
            display_name: Some("foundation_cache".to_string()),
            model: format!("models/{}", model),
            contents: vec![Content {
                role: "user".to_string(),
                parts,
            }],
            system_instruction: system_instruction.map(|s| Content {
                role: "user".to_string(),
                parts: vec![Part { text: s.to_string() }],
            }),
            ttl: ttl_seconds.map(|s| format!("{}s", s)),
            expire_time: None,
        };

        let url = format!("{}/cachedContents?key={}", BASE_URL, self.api_key);

        let response = self
            .client
            .post(&url)
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| GcpError::Network(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| GcpError::Parse(e.to_string()))
        } else {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            Err(GcpError::Api(status.as_u16(), text))
        }
    }

    pub async fn delete_cached_content(&self, cache_name: &str) -> Result<(), GcpError> {
        let url = format!("{}/{}?key={}", BASE_URL, cache_name, self.api_key);

        let response = self
            .client
            .delete(&url)
            .send()
            .await
            .map_err(|e| GcpError::Network(e.to_string()))?;

        if response.status().is_success() {
            Ok(())
        } else {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            Err(GcpError::Api(status.as_u16(), text))
        }
    }

    pub async fn list_models(&self) -> Result<Vec<ModelInfo>, GcpError> {
        let url = format!("{}/models?key={}", BASE_URL, self.api_key);

        let response = self
            .client
            .get(&url)
            .send()
            .await
            .map_err(|e| GcpError::Network(e.to_string()))?;

        if response.status().is_success() {
            let result: ListModelsResponse = response
                .json()
                .await
                .map_err(|e| GcpError::Parse(e.to_string()))?;
            Ok(result.models)
        } else {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            Err(GcpError::Api(status.as_u16(), text))
        }
    }
}

#[derive(Debug, Serialize)]
struct GenerateContentRequest {
    contents: Vec<Content>,
    #[serde(skip_serializing_if = "Option::is_none")]
    generation_config: Option<GenerationConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    system_instruction: Option<Part>,
    #[serde(skip_serializing_if = "Option::is_none")]
    cached_content: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Content {
    role: String,
    parts: Vec<Part>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Part {
    text: String,
}

#[derive(Debug, Serialize)]
struct GenerationConfig {
    temperature: Option<f32>,
    max_output_tokens: Option<i32>,
    top_p: Option<f32>,
    top_k: Option<i32>,
}

#[derive(Debug, Deserialize)]
pub struct GenerateContentResponse {
    pub candidates: Option<Vec<Candidate>>,
    pub usage_metadata: Option<UsageMetadata>,
    pub model_version: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct Candidate {
    pub content: Option<Content>,
    pub finish_reason: Option<String>,
    pub index: Option<i32>,
}

#[derive(Debug, Deserialize)]
pub struct UsageMetadata {
    pub prompt_token_count: Option<i32>,
    pub candidates_token_count: Option<i32>,
    pub total_token_count: Option<i32>,
    pub cached_content_token_count: Option<i32>,
}

#[derive(Debug, Serialize)]
struct CreateCachedContentRequest {
    display_name: Option<String>,
    model: String,
    contents: Vec<Content>,
    #[serde(skip_serializing_if = "Option::is_none")]
    system_instruction: Option<Content>,
    #[serde(skip_serializing_if = "Option::is_none")]
    ttl: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    expire_time: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CachedContent {
    pub name: String,
    pub model: String,
    pub display_name: Option<String>,
    pub usage_metadata: Option<CachedContentUsageMetadata>,
    pub create_time: Option<String>,
    pub update_time: Option<String>,
    pub expire_time: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CachedContentUsageMetadata {
    pub total_token_count: Option<i32>,
}

#[derive(Debug, Deserialize)]
struct ListModelsResponse {
    models: Vec<ModelInfo>,
}

#[derive(Debug, Deserialize)]
pub struct ModelInfo {
    pub name: String,
    pub version: Option<String>,
    pub display_name: Option<String>,
    pub description: Option<String>,
    pub supported_generation_methods: Option<Vec<String>>,
    pub base_model_id: Option<String>,
}

#[derive(Debug, thiserror::Error)]
pub enum GcpError {
    #[error("Network error: {0}")]
    Network(String),

    #[error("Parse error: {0}")]
    Parse(String),

    #[error("API error ({0}): {1}")]
    Api(u16, String),

    #[error("Configuration error: {0}")]
    Config(String),
}

pub struct GcpInferenceService {
    client: Arc<GeminiClient>,
    strategist_model: String,
    council_model: String,
    default_model: String,
}

impl GcpInferenceService {
    pub fn new(client: Arc<GeminiClient>, strategist_model: String, council_model: String, default_model: String) -> Self {
        Self {
            client,
            strategist_model,
            council_model,
            default_model,
        }
    }

    pub fn from_settings(settings: &raptorflow_config::Settings) -> Self {
        let client = Arc::new(GeminiClient::from_settings(settings));
        Self {
            client,
            strategist_model: "gemini-pro".to_string(),
            council_model: "gemini-flash-lite".to_string(),
            default_model: "gemini-flash-lite".to_string(),
        }
    }

    pub async fn generate_strategist_response(
        &self,
        prompt: &str,
        context: Option<&str>,
    ) -> Result<GenerateContentResponse, GcpError> {
        match context {
            Some(ctx) => {
                self.client
                    .generate_content_with_context(&self.strategist_model, prompt, ctx, None)
                    .await
            }
            None => {
                self.client
                    .generate_content(&self.strategist_model, prompt)
                    .await
            }
        }
    }

    pub async fn generate_council_reasoning(
        &self,
        prompt: &str,
        context: &str,
    ) -> Result<GenerateContentResponse, GcpError> {
        self.client
            .generate_content_with_context(&self.council_model, prompt, context, None)
            .await
    }

    pub async fn generate_default(
        &self,
        prompt: &str,
    ) -> Result<GenerateContentResponse, GcpError> {
        self.client
            .generate_content(&self.default_model, prompt)
            .await
    }

    pub async fn generate_with_foundation_cache(
        &self,
        prompt: &str,
        foundation_json: &str,
        cache_name: &str,
    ) -> Result<GenerateContentResponse, GcpError> {
        self.client
            .generate_content_with_context(&self.default_model, prompt, foundation_json, Some(cache_name))
            .await
    }

    pub async fn create_foundation_cache(
        &self,
        foundation_json: &str,
        ttl_seconds: i64,
    ) -> Result<CachedContent, GcpError> {
        let system_instruction = Some("You are an expert marketing strategist analyzing a company's foundation data.");
        self.client
            .create_cached_content(&self.default_model, foundation_json, system_instruction, Some(ttl_seconds))
            .await
    }

    pub async fn invalidate_foundation_cache(&self, cache_name: &str) -> Result<(), GcpError> {
        self.client.delete_cached_content(cache_name).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_client_creation() {
        let client = GeminiClient::new("test-key".to_string());
        assert_eq!(client.api_key, "test-key");
        assert_eq!(client.default_model, "gemini-2.0-flash");
    }
}
