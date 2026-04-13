//! Predictive Ripple Memory (PRL) for RaptorFlow.
//!
//! Implements the Plutchik-based emotional memory system. Ripples are memory nodes
//! with emotion vectors (8 Plutchik emotions), protection bands, and decay
//! policies. This is the long-term memory layer for all avatars.
//!
//! ## Protection bands
//!
//! | Band | Decay half-life | Consolidation threshold |
//! |---|---|---|
//! | Protected | 90 days | 0.85 |
//! | Important | 21 days | 0.65 |
//! | Normal | 7 days | 0.50 |
//! | Disposable | 1 day | 0.35 |
//!
//! ## Key types
//!
//! - [`PrlTopology`] — policy configuration for queue, collection, decay
//! - [`MemoryIngressDecision`] — routing decision for incoming memory events
//! - [`PredictionResolutionWindow`] — lookback window for prediction verification
//! - [`classify_memory_event()`] — ingress classifier
//! - [`infer_protection_band()`] — protection band inference from prediction presence
//!
//! ## Storage
//!
//! Ripples are stored in PostgreSQL (`ripples` table) and Qdrant (vector index).
//! See `database/migrations/0005_prl.sql` for the schema.
//!
//! ## Status
//!
//! Core types, classification logic, and HTTP routes exist. The actual decay
//! computation ([`run_decay`][http::run_decay]) and Qdrant vector operations
//! are not yet wired.

use raptorflow_contracts::{MemoryEvent, PrlDecayPolicy, ProtectionBand, RippleData};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrlTopology {
    pub queue_name: &'static str,
    pub collection_name: &'static str,
    pub working_memory_key_pattern: &'static str,
    pub consolidation_job_key: &'static str,
    pub prediction_resolution_job_key: &'static str,
    pub protection_bands: Vec<ProtectionBand>,
    pub decay_policies: Vec<PrlDecayPolicy>,
}

impl Default for PrlTopology {
    fn default() -> Self {
        Self {
            queue_name: "embedding",
            collection_name: "ripples",
            working_memory_key_pattern: "wm:{org_id}:{agent_id}",
            consolidation_job_key: "swr-consolidation",
            prediction_resolution_job_key: "prediction-resolution",
            protection_bands: vec![
                ProtectionBand::Protected,
                ProtectionBand::Important,
                ProtectionBand::Normal,
                ProtectionBand::Disposable,
            ],
            decay_policies: vec![
                PrlDecayPolicy {
                    org_id: uuid::Uuid::nil(),
                    policy_id: "prl-strategic".to_string(),
                    memory_class: "strategic".to_string(),
                    protection_band: ProtectionBand::Protected,
                    decay_half_life_hours: 24 * 90,
                    consolidation_threshold: 0.85,
                },
                PrlDecayPolicy {
                    org_id: uuid::Uuid::nil(),
                    policy_id: "prl-operational".to_string(),
                    memory_class: "operational".to_string(),
                    protection_band: ProtectionBand::Important,
                    decay_half_life_hours: 24 * 21,
                    consolidation_threshold: 0.65,
                },
                PrlDecayPolicy {
                    org_id: uuid::Uuid::nil(),
                    policy_id: "prl-transient".to_string(),
                    memory_class: "transient".to_string(),
                    protection_band: ProtectionBand::Disposable,
                    decay_half_life_hours: 24,
                    consolidation_threshold: 0.35,
                },
            ],
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryIngressDecision {
    pub accepted: bool,
    pub route: &'static str,
    pub protection_band: ProtectionBand,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PredictionResolutionWindow {
    pub lookback_hours: i32,
    pub minimum_confidence: f64,
    pub retry_backoff_minutes: i32,
}

impl Default for PredictionResolutionWindow {
    fn default() -> Self {
        Self {
            lookback_hours: 24 * 30,
            minimum_confidence: 0.55,
            retry_backoff_minutes: 60,
        }
    }
}

pub fn accepts_memory_event(event: &MemoryEvent) -> bool {
    event.ripple_data.is_some() || !event.raw_content.trim().is_empty()
}

pub fn classify_memory_event(event: &MemoryEvent) -> MemoryIngressDecision {
    let route = if event.campaign_id.is_some() {
        "campaign-memory"
    } else if event.session_id.is_some() {
        "session-memory"
    } else {
        "ambient-memory"
    };

    let protection_band = infer_protection_band(event.ripple_data.as_ref());
    MemoryIngressDecision {
        accepted: accepts_memory_event(event),
        route,
        protection_band,
    }
}

pub fn infer_protection_band(ripple_data: Option<&RippleData>) -> ProtectionBand {
    match ripple_data.and_then(|ripple| ripple.prediction.as_ref()) {
        Some(_) => ProtectionBand::Important,
        None => ProtectionBand::Normal,
    }
}

pub mod http;

pub use http::router;
