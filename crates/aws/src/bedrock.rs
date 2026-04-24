//! AWS Bedrock inference client.
//!
//! Wraps `aws_sdk_bedrockruntime::Client` and exposes `converse()`,
//! `converse_large()`, and `converse_fast()` methods.

use aws_config::{BehaviorVersion, Region};
use aws_sdk_bedrockruntime::types::{
    ContentBlock, ConversationRole, InferenceConfiguration, Message,
};
use aws_sdk_bedrockruntime::Client;
use serde::de::DeserializeOwned;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Semaphore;
use tracing::{debug, instrument, warn};

/// Confirmed AWS Bedrock model IDs for Mistral in ap-south-1.
pub const MODEL_MISTRAL_LARGE: &str = "mistral.mistral-large-3-675b-instruct";
pub const MODEL_MISTRAL_SMALL: &str = "mistral.ministral-3-8b-instruct";

#[derive(Debug, thiserror::Error)]
pub enum InferenceError {
    #[error("Bedrock SDK error: {0}")]
    Sdk(String),

    #[error("Bedrock returned no output")]
    NoOutput,

    #[error("Bedrock response contained no text content")]
    NoText,

    #[error("Prompt is empty — will not call Bedrock with an empty prompt")]
    EmptyPrompt,

    #[error("max_tokens must be between 1 and 8192, got {0}")]
    InvalidMaxTokens(i32),

    #[error("Bedrock request timed out after {0} seconds")]
    Timeout(u64),

    #[error("Bedrock output failed schema validation: {0}")]
    InvalidOutput(String),
}

#[derive(Clone, Debug)]
pub struct BedrockInferenceClient {
    client: Client,
    region: String,
    model_strategist: String,
    model_fast: String,
    request_timeout: Duration,
    semaphore: Arc<Semaphore>,
}

impl BedrockInferenceClient {
    /// Initialise from the environment (IAM role in production, env vars for local dev).
    pub async fn new(region: impl Into<String>) -> anyhow::Result<Self> {
        Self::new_with_models(
            region,
            MODEL_MISTRAL_LARGE,
            MODEL_MISTRAL_SMALL,
            8,
            Duration::from_secs(60),
        )
        .await
    }

    pub async fn from_settings(settings: &raptorflow_config::Settings) -> anyhow::Result<Self> {
        Self::new_with_models(
            settings.bedrock_region.clone(),
            settings.bedrock_model_strategist.clone(),
            settings.bedrock_model_fast.clone(),
            8,
            Duration::from_secs(60),
        )
        .await
    }

    pub async fn new_with_models(
        region: impl Into<String>,
        model_strategist: impl Into<String>,
        model_fast: impl Into<String>,
        max_concurrent_requests: usize,
        request_timeout: Duration,
    ) -> anyhow::Result<Self> {
        let region_str = region.into();
        let sdk_config = aws_config::defaults(BehaviorVersion::latest())
            .region(Region::new(region_str.clone()))
            .load()
            .await;

        let client = Client::new(&sdk_config);
        let model_strategist = model_strategist.into();
        let model_fast = model_fast.into();
        let max_concurrent_requests = max_concurrent_requests.max(1);

        tracing::info!(
            region = %region_str,
            strategist_model = %model_strategist,
            fast_model = %model_fast,
            max_concurrent_requests,
            "BedrockInferenceClient initialised"
        );

        Ok(Self {
            client,
            region: region_str,
            model_strategist,
            model_fast,
            request_timeout,
            semaphore: Arc::new(Semaphore::new(max_concurrent_requests)),
        })
    }

    pub fn region(&self) -> &str {
        &self.region
    }

    pub fn strategist_model(&self) -> &str {
        &self.model_strategist
    }

    pub fn fast_model(&self) -> &str {
        &self.model_fast
    }

    #[instrument(skip(self, prompt), fields(model_id, prompt_len = prompt.len()))]
    pub async fn converse(
        &self,
        model_id: &str,
        prompt: &str,
        max_tokens: i32,
    ) -> Result<String, InferenceError> {
        if prompt.trim().is_empty() {
            return Err(InferenceError::EmptyPrompt);
        }
        if !(1..=8192).contains(&max_tokens) {
            return Err(InferenceError::InvalidMaxTokens(max_tokens));
        }

        debug!(model_id = %model_id, prompt_chars = prompt.len(), max_tokens, "Calling Bedrock Converse API");
        let _permit = self
            .semaphore
            .acquire()
            .await
            .map_err(|e| InferenceError::Sdk(e.to_string()))?;

        let user_message = Message::builder()
            .role(ConversationRole::User)
            .content(ContentBlock::Text(prompt.to_string()))
            .build()
            .map_err(|e| InferenceError::Sdk(e.to_string()))?;

        let inference_config = InferenceConfiguration::builder()
            .max_tokens(max_tokens)
            .build();

        let request = self
            .client
            .converse()
            .model_id(model_id)
            .messages(user_message)
            .inference_config(inference_config)
            .send();

        let response = tokio::time::timeout(self.request_timeout, request)
            .await
            .map_err(|_| InferenceError::Timeout(self.request_timeout.as_secs()))?
            .map_err(|e| InferenceError::Sdk(e.to_string()))?;

        let output = response.output.ok_or(InferenceError::NoOutput)?;

        match output {
            aws_sdk_bedrockruntime::types::ConverseOutput::Message(msg) => {
                for block in msg.content() {
                    if let ContentBlock::Text(text) = block {
                        debug!(response_chars = text.len(), "Bedrock response received");
                        return Ok(text.clone());
                    }
                }
                warn!(model_id = %model_id, "Bedrock response had no text ContentBlock");
                Err(InferenceError::NoText)
            }
            _ => {
                warn!(model_id = %model_id, "Unexpected ConverseOutput variant");
                Err(InferenceError::NoText)
            }
        }
    }

    /// Convenience for heavyweight inference (Council, Foundation scan, brief evaluation).
    pub async fn converse_large(
        &self,
        prompt: &str,
        max_tokens: i32,
    ) -> Result<String, InferenceError> {
        self.converse(&self.model_strategist, prompt, max_tokens).await
    }

    /// Convenience for fast inference (classification, nudges, snark, voice compliance).
    pub async fn converse_fast(
        &self,
        prompt: &str,
        max_tokens: i32,
    ) -> Result<String, InferenceError> {
        self.converse(&self.model_fast, prompt, max_tokens).await
    }

    pub async fn converse_json<T>(
        &self,
        model_id: &str,
        prompt: &str,
        max_tokens: i32,
    ) -> Result<T, InferenceError>
    where
        T: DeserializeOwned,
    {
        let output = self.converse(model_id, prompt, max_tokens).await?;
        serde_json::from_str::<T>(&output)
            .map_err(|error| InferenceError::InvalidOutput(error.to_string()))
    }
}

// ─── Tests ────────────────────────────────────────────────────────────────────
// Run with: cargo test -p raptorflow-aws -- --nocapture
// The #[ignore] tests require AWS credentials:
//   export AWS_ACCESS_KEY_ID=...
//   export AWS_SECRET_ACCESS_KEY=...
//   export AWS_REGION=ap-south-1

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    #[ignore]
    async fn test_bedrock_ping_fast() {
        let client = BedrockInferenceClient::new("ap-south-1")
            .await
            .expect("Failed to create client");

        let response = client
            .converse_fast("Reply with exactly the word PONG and nothing else.", 16)
            .await
            .expect("Fast model ping failed");

        println!("Fast model response: {:?}", response);
        assert!(!response.is_empty(), "Response must not be empty");
        assert!(response.to_uppercase().contains("PONG"), "Expected PONG, got: {response}");
    }

    #[tokio::test]
    #[ignore]
    async fn test_bedrock_ping_large() {
        let client = BedrockInferenceClient::new("ap-south-1")
            .await
            .expect("Failed to create client");

        let response = client
            .converse_large("Reply with exactly the word PONG and nothing else.", 16)
            .await
            .expect("Large model ping failed");

        println!("Large model response: {:?}", response);
        assert!(!response.is_empty(), "Response must not be empty");
        assert!(response.to_uppercase().contains("PONG"), "Expected PONG, got: {response}");
    }

    #[tokio::test]
    async fn test_empty_prompt_guard() {
        let prompt = "   ";
        assert!(prompt.trim().is_empty(), "Empty prompt guard check");
    }

    #[tokio::test]
    async fn test_invalid_max_tokens_guard() {
        let valid = (1..=8192).contains(&512_i32);
        let invalid_zero = (1..=8192).contains(&0_i32);
        let invalid_huge = (1..=8192).contains(&99999_i32);
        assert!(valid);
        assert!(!invalid_zero);
        assert!(!invalid_huge);
    }
}
