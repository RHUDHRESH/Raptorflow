//! Domain types shared across all RaptorFlow crates.
//!
//! This crate is the **single source of truth** for all domain types used throughout
//! the RaptorFlow system. It is consumed by the API server, all service crates,
//! and the frontend (via the TypeScript `packages/contracts` that mirrors these types).
//!
//! ## Type categories
//!
//! | Category | Types |
//! |---|---|
//! | Identifiers | `Ulid` (type alias `String`), `TenantScoped` |
//! | Foundation | `FoundationSnapshot`, `FoundationPatch`, `FoundationScanRequest`, `FoundationScanStatus`, `FoundationCacheEvent` |
//! | Campaigns | `CampaignBrief`, `Campaign`, `Move`, `Task` |
//! | Council | `CouncilSession`, `CouncilAgentPosition` |
//! | Avatars | `AvatarRole`, `AvatarRegistryEntry`, `AvatarRegistry`, `ContextPack` |
//! | Skills | `SkillAtom`, `SkillAtomType`, `SkillAtomOrigin` |
//! | EEL / Lattice | `EelLatticeState` |
//! | PRL | `ProtectionBand`, `RippleData`, `MemoryEvent`, `PrlDecayPolicy`, `PredictionResolutionRecord` |
//! | Research | `ResearchRequest`, `ResearchRequestKind`, `ResearchUrgency`, `StreamCoordinatorRequest`, `StreamCoordinatorPhase` |
//! | Intern | `InternTask`, `InternTaskType` |
//! | Office | `OfficeEventMessage` |
//! | Muse | `MuseConversation` |
//! | Intel | `IntelAlert`, `ContentFeedbackLoop` |
//! | Billing / Nudges | `DailyWinsBrief`, `Nudge`, `CostThresholdAlert`, `OrgMonthlyCost`, `SessionTokenUsage` |
//! | Tool Gateway | `ToolGatewayRequest`, `ToolGatewayResponse` |
//!
//! ## Key invariants
//!
//! - Every domain struct that crosses a service boundary is serializable via serde.
//! - `AvatarRole` derives `Copy` to enable cheap comparisons in EEL lattice logic.
//! - `SkillAtom::initial()` is the preferred constructor for new skill atoms.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;

pub type Ulid = String;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AvatarRole {
    Strategist,
    Council,
    SupportSpecialist,
    Intern,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProtectionBand {
    Protected,
    Important,
    Normal,
    Disposable,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ResearchRequestKind {
    WebSearch,
    Browser,
    CompetitiveAnalysis,
    PerformanceAnalysis,
    ContentResearch,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ResearchUrgency {
    Blocking,
    Background,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum InternTaskType {
    WebSearch,
    Browser,
    CompetitiveAnalysis,
    PerformanceAnalysis,
    ContentResearch,
    FoundationUpdate,
    ReplanningSupport,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum StreamCoordinatorPhase {
    Precheck,
    BlockingResearch,
    Generation,
    PostProcessing,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TenantScoped {
    pub org_id: Uuid,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationSnapshot {
    pub org_id: Uuid,
    pub foundation_version: i32,
    pub sections: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationPatch {
    pub org_id: Uuid,
    pub section: String,
    pub value: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationScanRequest {
    pub org_id: Uuid,
    pub scan_id: Ulid,
    pub scan_kind: String,
    pub source_url: String,
    pub requested_sections: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationScanStatus {
    pub org_id: Uuid,
    pub scan_id: Ulid,
    pub scan_kind: String,
    pub status: String,
    pub progress_stage: String,
    pub websocket_channel: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FoundationCacheEvent {
    pub org_id: Uuid,
    pub event_id: Ulid,
    pub foundation_version: i32,
    pub event_type: String,
    pub affected_sections: Vec<String>,
    pub invalidation_scope: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CampaignBrief {
    pub org_id: Uuid,
    pub brief_id: Ulid,
    pub goal: String,
    pub timeline: String,
    pub channels: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Campaign {
    pub org_id: Uuid,
    pub campaign_id: Ulid,
    pub status: String,
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Move {
    pub org_id: Uuid,
    pub move_id: Ulid,
    pub campaign_id: Ulid,
    pub sequence_number: i32,
    pub move_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub org_id: Uuid,
    pub task_id: Ulid,
    pub campaign_id: Ulid,
    pub move_id: Ulid,
    pub title: String,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouncilSession {
    pub org_id: Uuid,
    pub session_id: Ulid,
    pub session_type: String,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouncilAgentPosition {
    pub org_id: Uuid,
    pub position_id: Ulid,
    pub session_id: Ulid,
    pub avatar_key: String,
    pub round_number: u8,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarRegistryEntry {
    pub org_id: Uuid,
    pub avatar_key: String,
    pub display_name: String,
    pub role: AvatarRole,
    pub support_domain: Option<String>,
    pub office_zone_id: String,
    pub reflection_profile: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarRegistry {
    pub entries: Vec<AvatarRegistryEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextPack {
    pub org_id: Uuid,
    pub foundation_sections: Vec<String>,
    pub retrieved_ripple_ids: Vec<Ulid>,
    pub skill_atom_ids: Vec<Ulid>,
    pub reflection_gate: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolGatewayRequest {
    pub org_id: Uuid,
    pub request_id: Ulid,
    pub session_id: Option<Ulid>,
    pub tool_name: String,
    pub arguments: Value,
    pub timeout_ms: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolGatewayResponse {
    pub org_id: Uuid,
    pub request_id: Ulid,
    pub accepted: bool,
    pub output: Value,
    pub next_action: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResearchRequest {
    pub org_id: Uuid,
    pub request_id: Ulid,
    pub parent_session_id: Option<Ulid>,
    pub parent_agent_id: String,
    pub request_kind: ResearchRequestKind,
    pub urgency: ResearchUrgency,
    pub query: String,
    pub required_sources: Vec<String>,
    pub output_format: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StreamCoordinatorRequest {
    pub org_id: Uuid,
    pub session_id: Ulid,
    pub phase: StreamCoordinatorPhase,
    pub blocking_research: Vec<ResearchRequest>,
    pub background_research: Vec<ResearchRequest>,
    pub tool_requests: Vec<ToolGatewayRequest>,
    pub foundation_sections: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventHarvesterRecord {
    pub org_id: Uuid,
    pub event_id: Ulid,
    pub source_type: String,
    pub source_id: String,
    pub event_type: String,
    pub payload: Value,
    pub ingested_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RippleData {
    pub core_claim: String,
    pub key_reasoning: String,
    pub prediction: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryEvent {
    pub org_id: Uuid,
    pub event_id: Ulid,
    pub agent_id: String,
    pub session_id: Option<Ulid>,
    pub campaign_id: Option<Ulid>,
    pub source: String,
    pub raw_content: String,
    pub ripple_data: Option<RippleData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrlDecayPolicy {
    pub org_id: Uuid,
    pub policy_id: Ulid,
    pub memory_class: String,
    pub protection_band: ProtectionBand,
    pub decay_half_life_hours: i32,
    pub consolidation_threshold: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PredictionResolutionRecord {
    pub org_id: Uuid,
    pub resolution_id: Ulid,
    pub ripple_id: Ulid,
    pub predicted_outcome: String,
    pub actual_outcome: Option<String>,
    pub resolved_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EelLatticeState {
    pub org_id: Uuid,
    pub avatar_key: String,
    pub role: AvatarRole,
    pub essence_core: Value,
    pub ego_signature: Value,
    pub skill_weave: Value,
    pub reflection_gate: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum SkillAtomType {
    StructuredRule,
    PromptTemplate,
    QualitativeProbe,
    QuantitativeModel,
    TechnicalProcess,
    Framework,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum SkillAtomOrigin {
    Initial,
    ReflectionTier1,
    ReflectionTier2,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillAtom {
    pub skill_id: String,
    pub name: String,
    pub description: String,
    #[serde(rename = "type")]
    pub skill_type: SkillAtomType,
    pub domain_tags: Vec<String>,
    pub utility_score: f64,
    pub utility_variance: f64,
    pub usage_count: u32,
    pub essence_alignment: f64,
    pub origin: SkillAtomOrigin,
}

impl SkillAtom {
    pub fn initial(
        skill_id: impl Into<String>,
        name: impl Into<String>,
        description: impl Into<String>,
        skill_type: SkillAtomType,
        domain_tags: Vec<&'static str>,
    ) -> Self {
        Self {
            skill_id: skill_id.into(),
            name: name.into(),
            description: description.into(),
            skill_type,
            domain_tags: domain_tags.into_iter().map(String::from).collect(),
            utility_score: 0.5,
            utility_variance: 0.5,
            usage_count: 0,
            essence_alignment: 1.0,
            origin: SkillAtomOrigin::Initial,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InternTask {
    pub org_id: Uuid,
    pub task_id: Ulid,
    pub parent_session_id: Ulid,
    pub parent_agent_id: String,
    pub intern_avatar_key: String,
    pub task_type: InternTaskType,
    pub urgency: ResearchUrgency,
    pub query: String,
    pub specific_requirements: Vec<String>,
    pub output_format: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OfficeEventMessage {
    pub org_id: Uuid,
    pub r#type: String,
    pub event_type: String,
    pub payload: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MuseConversation {
    pub org_id: Uuid,
    pub conversation_id: Ulid,
    pub route: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DailyWinsBrief {
    pub org_id: Uuid,
    pub briefing_id: Ulid,
    pub generated_at: DateTime<Utc>,
    pub lead_summary: String,
    pub full_briefing: String,
    pub recommended_action: String,
    pub recommended_action_type: String,
    pub recommended_action_data: Option<Value>,
    pub viewed_at: Option<DateTime<Utc>>,
    pub acted_on_at: Option<DateTime<Utc>>,
    pub action_outcome: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntelAlert {
    pub org_id: Uuid,
    pub alert_id: Ulid,
    pub campaign_id: Option<Ulid>,
    pub source_type: String,
    pub source_id: String,
    pub alert_type: String,
    pub significance: String,
    pub title: String,
    pub summary: String,
    pub payload: Value,
    pub captured_at: DateTime<Utc>,
    pub delivered_at: Option<DateTime<Utc>>,
    pub resolved_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Nudge {
    pub org_id: Uuid,
    pub nudge_id: Ulid,
    pub user_id: Uuid,
    pub nudge_type: String,
    pub priority: String,
    pub title: String,
    pub body: String,
    pub action_type: Option<String>,
    pub action_data: Option<Value>,
    pub source_type: String,
    pub source_id: String,
    pub created_at: DateTime<Utc>,
    pub delivered_at: Option<DateTime<Utc>>,
    pub viewed_at: Option<DateTime<Utc>>,
    pub acted_on_at: Option<DateTime<Utc>>,
    pub dismissed_at: Option<DateTime<Utc>>,
    pub suppressed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContentFeedbackLoop {
    pub org_id: Uuid,
    pub loop_id: Ulid,
    pub campaign_id: Option<Ulid>,
    pub source_asset_id: Option<String>,
    pub performance_signal: String,
    pub routed_to: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionTokenUsage {
    pub org_id: Uuid,
    pub session_id: Ulid,
    pub model_tier: String,
    pub input_tokens: i64,
    pub output_tokens: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrgMonthlyCost {
    pub org_id: Uuid,
    pub month: String,
    pub inference_cost_usd: f64,
    pub scraping_cost_usd: f64,
    pub storage_cost_usd: f64,
    pub session_count: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CostThresholdAlert {
    pub org_id: Uuid,
    pub alert_id: Ulid,
    pub month: String,
    pub threshold_name: String,
    pub threshold_value_usd: f64,
    pub observed_cost_usd: f64,
    pub created_at: DateTime<Utc>,
}
