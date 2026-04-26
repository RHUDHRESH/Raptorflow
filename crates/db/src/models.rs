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

    pub fn parse_from_str(s: &str) -> Option<Self> {
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

    pub fn parse_from_str(s: &str) -> Option<Self> {
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

    pub fn parse_from_str(s: &str) -> Option<Self> {
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

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Avatar {
    pub avatar_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_key: String,
    pub display_name: String,
    pub role: String,
    pub archetype: String,
    pub personality: serde_json::Value,
    pub system_prompt: String,
    pub tool_permissions: serde_json::Value,
    pub memory_scope: String,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct HarnessRun {
    pub run_id: String,
    pub org_id: uuid::Uuid,
    pub run_type: String,
    pub status: String,
    pub input: serde_json::Value,
    pub output: Option<serde_json::Value>,
    pub error_message: Option<String>,
    pub created_by: Option<String>,
    pub started_at: Option<DateTime<Utc>>,
    pub completed_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct HarnessStep {
    pub step_id: String,
    pub run_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_id: Option<String>,
    pub step_type: String,
    pub status: String,
    pub input: serde_json::Value,
    pub output: Option<serde_json::Value>,
    pub error_message: Option<String>,
    pub sequence_number: i32,
    pub started_at: Option<DateTime<Utc>>,
    pub completed_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CapabilityDefinition {
    pub capability_id: String,
    pub capability_key: String,
    pub name: String,
    pub domain: String,
    pub description: String,
    pub input_schema: serde_json::Value,
    pub output_schema: serde_json::Value,
    pub required_context: serde_json::Value,
    pub allowed_tools: serde_json::Value,
    pub artifact_type: String,
    pub evaluator_key: String,
    pub ripple_policy: serde_json::Value,
    pub risk_level: String,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AvatarCapabilityGrant {
    pub grant_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_id: String,
    pub capability_id: String,
    pub grant_scope: String,
    pub constraints: serde_json::Value,
    pub is_enabled: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct HarnessContextPack {
    pub context_pack_id: String,
    pub org_id: uuid::Uuid,
    pub run_id: Option<String>,
    pub capability_id: Option<String>,
    pub avatar_id: Option<String>,
    pub scope: String,
    pub token_budget: i32,
    pub foundation_context: serde_json::Value,
    pub intel_context: serde_json::Value,
    pub campaign_context: serde_json::Value,
    pub office_context: serde_json::Value,
    pub ripple_context: serde_json::Value,
    pub compressed_context: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CapabilityRun {
    pub capability_run_id: String,
    pub org_id: uuid::Uuid,
    pub harness_run_id: Option<String>,
    pub harness_step_id: Option<String>,
    pub avatar_id: Option<String>,
    pub capability_id: String,
    pub context_pack_id: Option<String>,
    pub status: String,
    pub input: serde_json::Value,
    pub output: Option<serde_json::Value>,
    pub error_message: Option<String>,
    pub model_id: Option<String>,
    pub token_usage: serde_json::Value,
    pub started_at: Option<DateTime<Utc>>,
    pub completed_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct CapabilityArtifact {
    pub artifact_id: String,
    pub org_id: uuid::Uuid,
    pub capability_run_id: Option<String>,
    pub harness_run_id: Option<String>,
    pub avatar_id: Option<String>,
    pub capability_id: Option<String>,
    pub artifact_type: String,
    pub title: String,
    pub body: serde_json::Value,
    pub status: String,
    pub version: i32,
    pub evaluation: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ArtifactVersion {
    pub artifact_version_id: String,
    pub artifact_id: String,
    pub org_id: uuid::Uuid,
    pub version: i32,
    pub body: serde_json::Value,
    pub change_reason: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ArtifactRippleLink {
    pub link_id: String,
    pub org_id: uuid::Uuid,
    pub artifact_id: String,
    pub ripple_id: String,
    pub link_type: String,
    pub salience: f64,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AvatarSoul {
    pub soul_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_id: String,
    pub identity_kernel: serde_json::Value,
    pub worldview: serde_json::Value,
    pub obsessions: serde_json::Value,
    pub reflexes: serde_json::Value,
    pub taboos: serde_json::Value,
    pub debate_style: serde_json::Value,
    pub embodiment_level: String,
    pub operating_principles: serde_json::Value,
    pub evaluation_bias: serde_json::Value,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AvatarMemoryEdge {
    pub memory_edge_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_id: String,
    pub ripple_id: String,
    pub relationship_type: String,
    pub salience: f64,
    pub decay_policy: String,
    pub use_when: String,
    pub last_used_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AvatarInstinctFrame {
    pub instinct_frame_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_id: String,
    pub harness_run_id: Option<String>,
    pub capability_run_id: Option<String>,
    pub trigger_kind: String,
    pub dominant_concern: String,
    pub risk_flags: serde_json::Value,
    pub recommended_posture: String,
    pub visible_summary: String,
    pub private_notes: serde_json::Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AvatarPresenceState {
    pub presence_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_id: String,
    pub harness_run_id: Option<String>,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub confidence: f64,
    pub visible_summary: String,
    pub last_event_id: Option<String>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AvatarDebateEvent {
    pub debate_event_id: String,
    pub org_id: uuid::Uuid,
    pub harness_run_id: String,
    pub speaker_avatar_id: Option<String>,
    pub target_avatar_id: Option<String>,
    pub event_type: String,
    pub stance: Option<String>,
    pub content: serde_json::Value,
    pub confidence: f64,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AvatarArtifactTrail {
    pub trail_id: String,
    pub org_id: uuid::Uuid,
    pub avatar_id: String,
    pub artifact_id: String,
    pub harness_run_id: Option<String>,
    pub contribution_type: String,
    pub summary: String,
    pub created_at: DateTime<Utc>,
}
