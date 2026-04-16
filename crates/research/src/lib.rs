use chrono::{DateTime, Utc};
use qdrant_client::qdrant::{
    Condition, CreateCollectionBuilder, Distance, Filter, PointStruct, QueryPointsBuilder,
    UpsertPointsBuilder, VectorParamsBuilder,
};
use qdrant_client::{Payload, Qdrant};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::sync::Arc;
use thiserror::Error;
use uuid::Uuid;

pub const INTEL_COLLECTION_NAME: &str = "intel_chunks";
pub const INTEL_VECTOR_DIM: usize = 768;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GroundedResult {
    pub query: String,
    pub run_id: Uuid,
    pub citations: Vec<Citation>,
    pub total_chunks: usize,
    pub cache_hit: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Citation {
    pub citation_id: Uuid,
    pub rank: usize,
    pub snippet: String,
    pub relevance_score: f64,
    pub source_domain: String,
    pub source_url: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VectorHit {
    pub chunk_id: Uuid,
    pub document_id: Uuid,
    pub score: f64,
    pub snippet: String,
    pub source_domain: String,
    pub source_url: String,
}

#[derive(Debug, Error)]
pub enum ResearchError {
    #[error("qdrant error: {0}")]
    Qdrant(String),
    #[error("invalid vector dimension {0}, expected {1}")]
    InvalidVectorDimension(usize, usize),
}

#[derive(Clone)]
pub struct VectorIndex {
    client: Arc<Qdrant>,
}

impl VectorIndex {
    pub fn from_settings(settings: &raptorflow_config::Settings) -> Result<Self, ResearchError> {
        let url = settings.qdrant_url.clone();
        let grpc_url = if url.ends_with(":6333") {
            url.replace(":6333", ":6334")
        } else {
            url
        };
        let client = Qdrant::from_url(&grpc_url)
            .build()
            .map_err(|e| ResearchError::Qdrant(e.to_string()))?;
        Ok(Self {
            client: Arc::new(client),
        })
    }

    pub async fn ensure_collection(&self) -> Result<(), ResearchError> {
        let collections = self
            .client
            .list_collections()
            .await
            .map_err(|e| ResearchError::Qdrant(e.to_string()))?;
        let exists = collections
            .collections
            .iter()
            .any(|collection| collection.name == INTEL_COLLECTION_NAME);
        if exists {
            return Ok(());
        }

        self.client
            .create_collection(
                CreateCollectionBuilder::new(INTEL_COLLECTION_NAME)
                    .vectors_config(VectorParamsBuilder::new(INTEL_VECTOR_DIM as u64, Distance::Cosine)),
            )
            .await
            .map_err(|e| ResearchError::Qdrant(e.to_string()))?;
        Ok(())
    }

    pub async fn upsert_chunk(
        &self,
        org_id: Uuid,
        document_id: Uuid,
        chunk_id: Uuid,
        domain: &str,
        source_url: &str,
        fetched_at: DateTime<Utc>,
        snippet: &str,
        vector: Vec<f32>,
    ) -> Result<(), ResearchError> {
        if vector.len() != INTEL_VECTOR_DIM {
            return Err(ResearchError::InvalidVectorDimension(
                vector.len(),
                INTEL_VECTOR_DIM,
            ));
        }

        let payload: Payload = serde_json::json!({
            "org_id": org_id.to_string(),
            "document_id": document_id.to_string(),
            "chunk_id": chunk_id.to_string(),
            "domain": domain,
            "source_url": source_url,
            "fetched_at": fetched_at.to_rfc3339(),
            "snippet": snippet,
        })
        .try_into()
        .map_err(|e| ResearchError::Qdrant(format!("{:?}", e)))?;
        let points = vec![PointStruct::new(chunk_id.to_string(), vector, payload)];

        self.client
            .upsert_points(UpsertPointsBuilder::new(INTEL_COLLECTION_NAME, points))
            .await
            .map_err(|e| ResearchError::Qdrant(e.to_string()))?;
        Ok(())
    }

    pub async fn search(
        &self,
        org_id: Uuid,
        query_vector: Vec<f32>,
        limit: u64,
    ) -> Result<Vec<VectorHit>, ResearchError> {
        let response = self
            .client
            .query(
                QueryPointsBuilder::new(INTEL_COLLECTION_NAME)
                    .query(query_vector)
                    .limit(limit)
                    .with_payload(true)
                    .filter(Filter::all([Condition::matches(
                        "org_id",
                        org_id.to_string(),
                    )])),
            )
            .await
            .map_err(|e| ResearchError::Qdrant(e.to_string()))?;

        let mut hits = Vec::new();
        for point in response.result {
            let payload = point.payload;
            let chunk_id = payload
                .get("chunk_id")
                .and_then(value_as_string)
                .and_then(|value| Uuid::parse_str(&value).ok());
            let document_id = payload
                .get("document_id")
                .and_then(value_as_string)
                .and_then(|value| Uuid::parse_str(&value).ok());
            let snippet = payload
                .get("snippet")
                .and_then(value_as_string)
                .unwrap_or_default();
            let domain = payload
                .get("domain")
                .and_then(value_as_string)
                .unwrap_or_else(|| "unknown".to_string());
            let source_url = payload
                .get("source_url")
                .and_then(value_as_string)
                .unwrap_or_default();

            if let (Some(chunk_id), Some(document_id)) = (chunk_id, document_id) {
                hits.push(VectorHit {
                    chunk_id,
                    document_id,
                    score: point.score as f64,
                    snippet,
                    source_domain: domain,
                    source_url,
                });
            }
        }

        Ok(hits)
    }
}

fn value_as_string(value: &qdrant_client::qdrant::Value) -> Option<String> {
    let json = value.clone().into_json();
    json.as_str().map(ToString::to_string)
}

pub struct Chunker;

impl Chunker {
    const TARGET_CHUNK_SIZE: usize = 512;

    pub fn chunk_text(text: &str) -> Vec<String> {
        let words: Vec<&str> = text.split_whitespace().collect();
        if words.is_empty() {
            return Vec::new();
        }

        let mut chunks = Vec::new();
        let mut start = 0;
        while start < words.len() {
            let end = (start + Self::TARGET_CHUNK_SIZE).min(words.len());
            let chunk = words[start..end].join(" ");
            if !chunk.trim().is_empty() {
                chunks.push(chunk);
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
