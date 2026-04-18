use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CampaignStatus {
    Draft,
    Active,
    Paused,
    Completed,
    Archived,
}

impl CampaignStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            CampaignStatus::Draft => "draft",
            CampaignStatus::Active => "active",
            CampaignStatus::Paused => "paused",
            CampaignStatus::Completed => "completed",
            CampaignStatus::Archived => "archived",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "draft" => Some(CampaignStatus::Draft),
            "active" => Some(CampaignStatus::Active),
            "paused" => Some(CampaignStatus::Paused),
            "completed" => Some(CampaignStatus::Completed),
            "archived" => Some(CampaignStatus::Archived),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MoveStatus {
    Planned,
    InProgress,
    Completed,
    Skipped,
}

impl MoveStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            MoveStatus::Planned => "planned",
            MoveStatus::InProgress => "in_progress",
            MoveStatus::Completed => "completed",
            MoveStatus::Skipped => "skipped",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "planned" => Some(MoveStatus::Planned),
            "in_progress" => Some(MoveStatus::InProgress),
            "completed" => Some(MoveStatus::Completed),
            "skipped" => Some(MoveStatus::Skipped),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TaskStatus {
    Pending,
    InProgress,
    Completed,
    Cancelled,
}

impl TaskStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            TaskStatus::Pending => "pending",
            TaskStatus::InProgress => "in_progress",
            TaskStatus::Completed => "completed",
            TaskStatus::Cancelled => "cancelled",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "pending" => Some(TaskStatus::Pending),
            "in_progress" => Some(TaskStatus::InProgress),
            "completed" => Some(TaskStatus::Completed),
            "cancelled" => Some(TaskStatus::Cancelled),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Campaign {
    pub campaign_id: String,
    pub org_id: uuid::Uuid,
    pub name: String,
    pub goal: String,
    pub status: String,
    pub active_move_id: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CampaignMove {
    pub move_id: String,
    pub campaign_id: String,
    pub org_id: uuid::Uuid,
    pub move_type: String,
    pub sequence_number: i32,
    pub status: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CampaignTask {
    pub task_id: String,
    pub move_id: String,
    pub campaign_id: String,
    pub org_id: uuid::Uuid,
    pub title: String,
    pub status: String,
    pub scheduled_date: Option<chrono::NaiveDate>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CampaignBrief {
    pub brief_id: String,
    pub org_id: uuid::Uuid,
    pub campaign_id: Option<String>,
    pub status: String,
    pub original_text: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ReplanSession {
    pub replan_session_id: String,
    pub org_id: uuid::Uuid,
    pub campaign_id: String,
    pub trigger_type: String,
    pub status: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct GeneratedContent {
    pub content_id: String,
    pub org_id: uuid::Uuid,
    pub campaign_id: Option<String>,
    pub task_id: Option<String>,
    pub content_type: String,
    pub status: String,
    pub body: serde_json::Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Organization {
    pub org_id: uuid::Uuid,
    pub name: String,
    pub subscription_status: String,
    pub foundation_version: i32,
    pub foundation_complete: bool,
    pub foundation_json: Option<serde_json::Value>,
    pub foundation_completed_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FoundationSection {
    pub org_id: uuid::Uuid,
    pub section_key: String,
    pub value: serde_json::Value,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FoundationScan {
    pub scan_id: String,
    pub org_id: uuid::Uuid,
    pub url: String,
    pub status: String,
    pub quick_scan_data: Option<serde_json::Value>,
    pub deep_scan_data: Option<serde_json::Value>,
    pub started_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CompetitorSnapshot {
    pub snapshot_id: String,
    pub org_id: uuid::Uuid,
    pub competitor_url: String,
    pub hash: Option<String>,
    pub status: String,
    pub scrape_data: Option<serde_json::Value>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ContentStrategy {
    pub strategy_id: String,
    pub org_id: uuid::Uuid,
    pub territories: serde_json::Value,
    pub pillar_pages: serde_json::Value,
    pub editorial_calendar: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FoundationVersion {
    pub version_id: String,
    pub org_id: uuid::Uuid,
    pub foundation_version: i32,
    pub change_description: Option<String>,
    pub changed_fields: serde_json::Value,
    pub previous_values: serde_json::Value,
    pub impact_assessment: Option<serde_json::Value>,
    pub created_at: DateTime<Utc>,
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
    pub campaign_id: Option<String>,
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
    pub provider: String,
    pub status: String,
    pub plan_amount_inr: i32,
    pub plan_tier: String,
    pub referral_code: Option<String>,
    pub discount_percent: i32,
    pub grace_period_ends_at: Option<DateTime<Utc>>,
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

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Nudge {
    pub nudge_id: String,
    pub org_id: uuid::Uuid,
    pub user_id: uuid::Uuid,
    pub nudge_type: String,
    pub priority: String,
    pub title: String,
    pub body: String,
    pub action_type: Option<String>,
    pub action_data: serde_json::Value,
    pub source_type: String,
    pub source_id: String,
    pub created_at: DateTime<Utc>,
    pub delivered_at: Option<DateTime<Utc>>,
    pub viewed_at: Option<DateTime<Utc>>,
    pub acted_on_at: Option<DateTime<Utc>>,
    pub dismissed_at: Option<DateTime<Utc>>,
    pub suppressed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CouncilSession {
    pub session_id: String,
    pub org_id: uuid::Uuid,
    pub campaign_id: Option<String>,
    pub session_type: String,
    pub status: String,
    pub question: String,
    pub total_cost_usd: f64,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CouncilAgentPosition {
    pub position_id: String,
    pub org_id: uuid::Uuid,
    pub session_id: String,
    pub avatar_key: String,
    pub round_number: i32,
    pub content: String,
    pub extracted_ripple_data: serde_json::Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct MuseConversation {
    pub conversation_id: String,
    pub org_id: uuid::Uuid,
    pub route: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct MuseMessage {
    pub message_id: String,
    pub conversation_id: String,
    pub org_id: uuid::Uuid,
    pub role: String,
    pub body: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct DailyWin {
    pub briefing_id: String,
    pub org_id: uuid::Uuid,
    pub briefing_date: chrono::NaiveDate,
    pub generated_at: DateTime<Utc>,
    pub lead_summary: String,
    pub full_briefing: String,
    pub recommended_action: String,
    pub recommended_action_type: String,
    pub recommended_action_data: serde_json::Value,
    pub viewed_at: Option<DateTime<Utc>>,
    pub acted_on_at: Option<DateTime<Utc>>,
    pub action_outcome: Option<String>,
    pub created_at: DateTime<Utc>,
}
