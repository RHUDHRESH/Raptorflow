use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Organization {
    pub org_id: uuid::Uuid,
    pub name: String,
    pub subscription_status: String,
    pub foundation_version: i32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct OrgUser {
    pub org_user_id: uuid::Uuid,
    pub org_id: uuid::Uuid,
    pub clerk_user_id: String,
    pub email: String,
    pub role: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AuditLog {
    pub audit_log_id: uuid::Uuid,
    pub org_id: Option<uuid::Uuid>,
    pub actor_id: Option<String>,
    pub operation_type: String,
    pub target_type: String,
    pub target_id: Option<String>,
    pub payload: serde_json::Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FoundationSnapshot {
    pub foundation_snapshot_id: String,
    pub org_id: uuid::Uuid,
    pub foundation_version: i32,
    pub sections: serde_json::Value,
    pub source: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct UploadedAsset {
    pub asset_id: String,
    pub org_id: uuid::Uuid,
    pub asset_kind: String,
    pub storage_key: String,
    pub mime_type: String,
    pub metadata: serde_json::Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Ripple {
    pub ripple_id: String,
    pub org_id: uuid::Uuid,
    pub agent_id: uuid::Uuid,
    pub campaign_id: Option<uuid::Uuid>,
    pub scope: String,
    pub hierarchy_level: i32,
    pub memory_class: String,
    pub source: String,
    pub trigger_text: String,
    pub raw_text: String,
    pub summary_text: String,
    pub embedding: Option<Vec<f32>>,
    pub simhash: Option<Vec<i64>>,
    pub emotion_vector: Option<Vec<f64>>,
    pub salience: f64,
    pub confidence: f64,
    pub importance_band: String,
    pub prediction_json: Option<serde_json::Value>,
    pub actual_json: Option<serde_json::Value>,
    pub prediction_error: Option<f64>,
    pub precision_weight: f64,
    pub retention_band: String,
    pub activation_count: i32,
    pub last_activated_at: Option<DateTime<Utc>>,
    pub state: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct RippleEdge {
    pub edge_id: uuid::Uuid,
    pub org_id: uuid::Uuid,
    pub source_ripple_id: String,
    pub target_ripple_id: String,
    pub edge_type: String,
    pub weight: f64,
    pub co_activation_count: i64,
    pub last_co_activated_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AgentEssence {
    pub agent_id: uuid::Uuid,
    pub org_id: uuid::Uuid,
    pub avatar_key: String,
    pub display_name: Option<String>,
    pub essence_core: serde_json::Value,
    pub ego_baseline: Vec<f64>,
    pub ego_state: Vec<f64>,
    pub ego_multipliers: Vec<f64>,
    pub ego_decay_rate: f64,
    pub skill_atoms: serde_json::Value,
    pub persona_vector: Option<Vec<f32>>,
    pub reflection_vfe: f64,
    pub reflection_mean: f64,
    pub reflection_std: f64,
    pub reflection_cooldown: i32,
    pub active_session_id: Option<uuid::Uuid>,
    pub last_active_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Subscription {
    pub subscription_id: uuid::Uuid,
    pub org_id: uuid::Uuid,
    pub razorpay_subscription_id: Option<String>,
    pub plan_id: String,
    pub plan_name: String,
    pub status: String,
    pub current_period_start: Option<DateTime<Utc>>,
    pub current_period_end: Option<DateTime<Utc>>,
    pub cancel_at_period_end: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct PaymentEvent {
    pub event_id: uuid::Uuid,
    pub org_id: uuid::Uuid,
    pub razorpay_event_id: String,
    pub event_type: String,
    pub payment_id: Option<String>,
    pub order_id: Option<String>,
    pub amount: Option<i64>,
    pub currency: Option<String>,
    pub status: Option<String>,
    pub metadata: Option<serde_json::Value>,
    pub processed: bool,
    pub processed_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
}
