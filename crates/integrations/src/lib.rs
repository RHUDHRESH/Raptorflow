//! Re-exports of all external service client configurations for RaptorFlow.
//!
//! This crate provides a single struct ([`IntegrationClients`]) that aggregates
//! configuration for every external service from [`Settings`]. It is useful for
//! generating documentation or bootstrapping service wiring — it does NOT
//! create actual clients. Each actual client crate (`gcp`, `aws`, `cache`, etc.)
//! is instantiated separately in `raptorflow_api::main`.
//!
//! ## Clients aggregated
//!
//! | Client | Config struct | Actual crate |
//! |---|---|---|
//! | GCP/Gemini | [`GcpClients`] | `raptorflow_gcp` |
//! | Clerk | [`ClerkClient`] | `raptorflow_auth` |
//! | Razorpay | [`RazorpayClient`] | `raptorflow_billing` |
//! | DragonflyDB | [`DragonflyClient`] | `raptorflow_cache` |
//! | Qdrant | [`QdrantClient`] | (not yet wired) |
//! | AWS S3 | [`S3Client`] | `raptorflow_aws` |
//! | AWS SQS | [`SqsClient`] | `raptorflow_sqs` |
//! | Tool Gateway | [`ToolGatewayClient`] | (not implemented) |
//! | Scraping | [`ScrapingClient`] | (not implemented) |

use raptorflow_config::Settings;
use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub struct GcpClients {
    pub api_key: String,
    pub strategist_model: String,
    pub council_reasoning_model: String,
    pub default_model: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct ClerkClient {
    pub jwks_url: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct RazorpayClient {
    pub key_id: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct DragonflyClient {
    pub url: String,
    pub namespace_prefixes: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct QdrantClient {
    pub url: String,
    pub collection: String,
    pub vector_dimensions: usize,
    pub distance_metric: String,
    pub quantization: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct S3Client {
    pub bucket: String,
    pub region: String,
    pub object_prefixes: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct SqsClient {
    pub embedding_queue: String,
    pub content_pregeneration_queue: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct ToolGatewayClient {
    pub enabled_tools: Vec<String>,
    pub max_concurrency: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct ScrapingClient {
    pub browser_engine: String,
    pub user_agent_pool: Vec<String>,
    pub proxy_pool: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct IntegrationClients {
    pub gcp: GcpClients,
    pub clerk: ClerkClient,
    pub razorpay: RazorpayClient,
    pub dragonfly: DragonflyClient,
    pub qdrant: QdrantClient,
    pub s3: S3Client,
    pub sqs: SqsClient,
    pub tool_gateway: ToolGatewayClient,
    pub scraping: ScrapingClient,
}

impl IntegrationClients {
    pub fn from_settings(settings: &Settings) -> Self {
        Self {
            gcp: GcpClients {
                api_key: settings.gcp_api_key.clone(),
                strategist_model: "gemini-pro".to_string(),
                council_reasoning_model: "gemini-flash-lite-reasoning".to_string(),
                default_model: "gemini-flash-lite".to_string(),
            },
            clerk: ClerkClient {
                jwks_url: settings.clerk_jwks_url.clone(),
            },
            razorpay: RazorpayClient {
                key_id: settings.razorpay_key_id.clone(),
            },
            dragonfly: DragonflyClient {
                url: settings.dragonfly_url.clone(),
                namespace_prefixes: vec![
                    "wm".to_string(),
                    "foundation".to_string(),
                    "lock".to_string(),
                    "stream".to_string(),
                    "session".to_string(),
                    "snark".to_string(),
                ],
            },
            qdrant: QdrantClient {
                url: settings.qdrant_url.clone(),
                collection: "ripples".to_string(),
                vector_dimensions: 64,
                distance_metric: "cosine".to_string(),
                quantization: "scalar".to_string(),
            },
            s3: S3Client {
                bucket: settings.s3_bucket.clone(),
                region: settings.aws_region.clone(),
                object_prefixes: vec![
                    "uploads/".to_string(),
                    "screenshots/".to_string(),
                    "exports/".to_string(),
                    "backups/".to_string(),
                ],
            },
            sqs: SqsClient {
                embedding_queue: settings.sqs_embedding_queue.clone(),
                content_pregeneration_queue: settings.sqs_content_queue.clone(),
            },
            tool_gateway: ToolGatewayClient {
                enabled_tools: vec![
                    "web_search".to_string(),
                    "browser".to_string(),
                    "competitive_analysis".to_string(),
                    "performance_analysis".to_string(),
                    "content_research".to_string(),
                ],
                max_concurrency: 8,
            },
            scraping: ScrapingClient {
                browser_engine: "chromiumoxide".to_string(),
                user_agent_pool: vec![
                    "RaptorFlowBot/0.1".to_string(),
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36".to_string(),
                ],
                proxy_pool: "managed".to_string(),
            },
        }
    }
}
