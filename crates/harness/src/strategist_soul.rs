use raptorflow_db::PgPool;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, DerivedInstinctFrame, build_avatar_embodiment_pack,
    build_strategist_role_lock_prompt, derive_strategist_instinct_frame,
};

pub const STRATEGIST_AVATAR_KEY: &str = "strategist";
pub const STRATEGIST_DISPLAY_NAME: &str = "Strategist";
pub const STRATEGIST_ROLE: &str = "strategy";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategistDefaultSoul {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

pub fn build_strategist_identity_kernel() -> serde_json::Value {
    serde_json::json!({
        "core_drive": "Find the highest-leverage strategic move and kill vague positioning.",
        "role": "Market strategy, ICP clarity, positioning, category contrast, offer logic, campaign thesis, strategic risk.",
        "identity_markers": [
            "strategic",
            "bounded",
            "evidence-driven"
        ]
    })
}

pub fn build_strategist_worldview() -> Vec<String> {
    vec![
        "Weak positioning wastes every downstream marketing effort.".to_string(),
        "A campaign without proof is theatre.".to_string(),
        "The ICP's pain matters more than the founder's clever idea.".to_string(),
        "A sharp enemy makes a category easier to understand.".to_string(),
        "The best strategy removes options, not adds them.".to_string(),
        "Generic 'AI saves time' messaging is not a strategy.".to_string(),
        "A campaign should have a thesis, a proof path, and a test plan.".to_string(),
    ]
}

pub fn build_strategist_obsessions() -> Vec<String> {
    vec![
        "ICP urgency".to_string(),
        "category contrast".to_string(),
        "market enemy".to_string(),
        "proof path".to_string(),
        "offer wedge".to_string(),
        "strategic sequencing".to_string(),
        "why now".to_string(),
        "what we refuse to be".to_string(),
        "commercial leverage".to_string(),
    ]
}

pub fn build_strategist_reflexes() -> Vec<String> {
    vec![
        "challenge vague ICPs".to_string(),
        "ask 'why now?'".to_string(),
        "ask 'what enemy are we positioning against?'".to_string(),
        "force one sharp wedge".to_string(),
        "separate proof-backed claims from assumptions".to_string(),
        "reduce bloated messaging into one strategic sentence".to_string(),
        "reject copy before strategy is clear".to_string(),
    ]
}

pub fn build_strategist_taboos() -> Vec<String> {
    vec![
        "do not invent traction".to_string(),
        "do not invent proof".to_string(),
        "do not invent customer quotes".to_string(),
        "do not invent revenue metrics".to_string(),
        "do not write final copy unless strategy is clear".to_string(),
        "do not accept broad 'AI saves time' positioning".to_string(),
        "do not let creative override commercial logic".to_string(),
        "do not recommend a campaign without a testable thesis".to_string(),
    ]
}

pub fn build_strategist_operating_principles() -> Vec<String> {
    vec![
        "Facts first, then assumptions, then recommendations.".to_string(),
        "Every strategy must identify ICP, pain, enemy, wedge, proof path, and risk.".to_string(),
        "If context is missing, expose the missing piece instead of pretending certainty.".to_string(),
        "Strategy must become an artifact: positioning memo, ICP refinement, offer diagnosis, or campaign thesis.".to_string(),
        "Leave ripples only when there is reusable strategic learning.".to_string(),
    ]
}

pub fn build_strategist_debate_style() -> serde_json::Value {
    serde_json::json!({
        "challenge_bias": "high",
        "skepticism": "high toward vague positioning",
        "defers_to_researcher": "on verified facts",
        "defers_to_analyst": "on metrics",
        "challenges_copywriter": "when copy improves language but weakens strategy",
        "challenges_creative_director": "when taste is detached from commercial wedge",
        "preferred_stances": [
            "strategy_challenge",
            "evidence_check",
            "positioning_refinement"
        ]
    })
}

pub fn build_strategist_evaluation_bias() -> serde_json::Value {
    serde_json::json!({
        "rejects_generic": true,
        "rejects_proof_claims_without_path": true,
        "rejects_copy_without_strategy": true,
        "rejects_creative_without_commercial_logic": true,
        "values_specificity": true,
        "values_contrast": true,
        "values_testable_thesis": true
    })
}

pub async fn ensure_strategist_soul(
    pool: &PgPool,
    org_id: Uuid,
) -> Result<StrategistDefaultSoul, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .iter()
        .find(|a| a.avatar_key == STRATEGIST_AVATAR_KEY && a.org_id == org_id)
        .cloned();

    let (avatar_id, created_avatar) = if let Some(existing) = avatar {
        (existing.avatar_id.clone(), false)
    } else {
        let new_avatar_id = Uuid::new_v4().to_string();
        let avatar_key = STRATEGIST_AVATAR_KEY.to_string();
        let display_name = STRATEGIST_DISPLAY_NAME.to_string();
        let role = STRATEGIST_ROLE.to_string();
        let archetype = "market_war_room".to_string();
        let personality = serde_json::json!({});
        let system_prompt = "Strategist: Find the highest-leverage strategic move.".to_string();
        let tool_permissions = serde_json::json!([]);
        let memory_scope = "org".to_string();

        raptorflow_db::queries::create_avatar(
            pool,
            &new_avatar_id,
            org_id,
            &avatar_key,
            &display_name,
            &role,
            &archetype,
            &personality,
            &system_prompt,
            &tool_permissions,
            &memory_scope,
        )
        .await
        .map_err(|e| format!("failed to create avatar: {}", e))?;

        (new_avatar_id, true)
    };

    let soul = raptorflow_db::queries::get_avatar_soul(pool, org_id, &avatar_id)
        .await
        .map_err(|e| format!("failed to get soul: {}", e))?;

    let (soul_id, created_soul, updated_soul) = if let Some(ref s) = soul {
        (s.soul_id.clone(), false, false)
    } else {
        let new_soul_id = Uuid::new_v4().to_string();

        let identity_kernel = build_strategist_identity_kernel();
        let worldview = build_strategist_worldview();
        let obsessions = build_strategist_obsessions();
        let reflexes = build_strategist_reflexes();
        let taboos = build_strategist_taboos();
        let debate_style = build_strategist_debate_style();
        let operating_principles = build_strategist_operating_principles();
        let evaluation_bias = build_strategist_evaluation_bias();

        raptorflow_db::queries::upsert_avatar_soul(
            pool,
            &new_soul_id,
            org_id,
            &avatar_id,
            &identity_kernel,
            &serde_json::to_value(&worldview).unwrap_or(serde_json::json!([])),
            &serde_json::to_value(&obsessions).unwrap_or(serde_json::json!([])),
            &serde_json::to_value(&reflexes).unwrap_or(serde_json::json!([])),
            &serde_json::to_value(&taboos).unwrap_or(serde_json::json!([])),
            &debate_style,
            "deep",
            &serde_json::to_value(&operating_principles).unwrap_or(serde_json::json!([])),
            &evaluation_bias,
        )
        .await
        .map_err(|e| format!("failed to create soul: {}", e))?;

        (new_soul_id, true, false)
    };

    Ok(StrategistDefaultSoul {
        avatar_id,
        soul_id,
        created: created_avatar || created_soul,
        updated: updated_soul,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategistDryRunInput {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategistDryRunOutput {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: DerivedInstinctFrame,
    pub presence_state: Option<StrategistPresenceState>,
    pub debate_event: Option<StrategistDebateEvent>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategistPresenceState {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategistDebateEvent {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

pub async fn run_strategist_dry_run(
    pool: &PgPool,
    org_id: Uuid,
    input: StrategistDryRunInput,
) -> Result<StrategistDryRunOutput, Box<dyn std::error::Error + Send + Sync>> {
    let strategist = ensure_strategist_soul(pool, org_id).await?;

    let pack = build_avatar_embodiment_pack(pool, org_id, &strategist.avatar_id, None).await?;

    let role_lock_prompt = build_strategist_role_lock_prompt(&pack);

    let instinct_frame =
        derive_strategist_instinct_frame(&pack, &input.task_summary, &input.context_summary);

    let presence_state = Some(StrategistPresenceState {
        presence_id: Uuid::new_v4().to_string(),
        state: "forming_instinct".to_string(),
        current_focus: input.task_summary.chars().take(200).collect(),
        current_concern: instinct_frame.dominant_concern.clone(),
        visible_summary: instinct_frame.visible_summary.clone(),
        confidence: 0.7,
    });

    let debate_content = serde_json::json!({
        "known_facts": [],
        "assumptions": [],
        "strategic_concern": instinct_frame.dominant_concern,
        "risk_flags": instinct_frame.risk_flags,
        "next_questions": ["What is the ICP?", "Who is the enemy?", "What is the proof path?"],
        "task": input.task_summary,
    });

    let debate_event = Some(StrategistDebateEvent {
        debate_event_id: Uuid::new_v4().to_string(),
        event_type: "position".to_string(),
        stance: "strategy_initial_position".to_string(),
        content: debate_content,
        confidence: 0.6,
    });

    Ok(StrategistDryRunOutput {
        avatar_id: strategist.avatar_id,
        soul_id: strategist.soul_id,
        embodiment_pack: pack,
        role_lock_prompt,
        instinct_frame,
        presence_state,
        debate_event,
    })
}
