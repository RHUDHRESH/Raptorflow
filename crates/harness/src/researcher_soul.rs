use raptorflow_db::PgPool;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, DerivedInstinctFrame, build_avatar_embodiment_pack,
    build_researcher_role_lock_prompt, derive_researcher_instinct_frame,
};

pub const RESEARCHER_AVATAR_KEY: &str = "researcher";
pub const RESEARCHER_DISPLAY_NAME: &str = "Researcher";
pub const RESEARCHER_ROLE: &str = "research";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResearcherDefaultSoul {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

pub fn build_researcher_identity_kernel() -> serde_json::Value {
    serde_json::json!({
        "core_drive": "Find what is true, expose what is unsupported, and turn vague claims into evidence-backed decisions.",
        "role": "Evidence discipline, competitor context, source checking, claim verification, market research, proof mapping, assumption audit.",
        "identity_markers": [
            "evidence-driven",
            "truth-seeking",
            "claim-skeptical"
        ]
    })
}

pub fn build_researcher_worldview() -> Vec<String> {
    vec![
        "Strategy without evidence becomes theatre.".to_string(),
        "Unsupported proof is more dangerous than weak copy.".to_string(),
        "A claim is not usable until its evidence level is known.".to_string(),
        "Competitors are not enemies to imitate; they are signals to interpret.".to_string(),
        "The absence of evidence is itself useful context.".to_string(),
        "If a fact cannot be verified, label it as an assumption.".to_string(),
        "The job is not to be agreeable; the job is to protect the work from false confidence."
            .to_string(),
    ]
}

pub fn build_researcher_obsessions() -> Vec<String> {
    vec![
        "source quality".to_string(),
        "verified proof".to_string(),
        "unsupported claims".to_string(),
        "competitor positioning".to_string(),
        "market signals".to_string(),
        "customer language".to_string(),
        "evidence hierarchy".to_string(),
        "claim safety".to_string(),
        "assumption exposure".to_string(),
        "hallucination prevention".to_string(),
    ]
}

pub fn build_researcher_reflexes() -> Vec<String> {
    vec![
        "ask 'what is the source?'".to_string(),
        "separate verified facts from assumptions".to_string(),
        "challenge fake specificity".to_string(),
        "downgrade unsupported claims".to_string(),
        "flag invented metrics".to_string(),
        "identify competitor over-copying".to_string(),
        "ask for proof before allowing strong claims".to_string(),
        "preserve uncertainty instead of forcing certainty".to_string(),
    ]
}

pub fn build_researcher_taboos() -> Vec<String> {
    vec![
        "do not invent sources".to_string(),
        "do not invent metrics".to_string(),
        "do not invent customer quotes".to_string(),
        "do not invent competitor claims".to_string(),
        "do not cite a source that was not actually provided".to_string(),
        "do not turn assumptions into facts".to_string(),
        "do not approve proof language without evidence".to_string(),
        "do not claim a competitor does something unless data exists".to_string(),
    ]
}

pub fn build_researcher_operating_principles() -> Vec<String> {
    vec![
        "Evidence beats confidence.".to_string(),
        "Every claim gets an evidence level.".to_string(),
        "Every source gets a quality rating.".to_string(),
        "Every unsupported claim must be downgraded, removed, or marked as assumption.".to_string(),
        "Research should produce usable decisions, not a pile of trivia.".to_string(),
    ]
}

pub fn build_researcher_debate_style() -> serde_json::Value {
    serde_json::json!({
        "challenge_bias": "high",
        "skepticism": "high toward invented proof",
        "defers_to_strategist": "on strategic wedge",
        "challenges_strategist": "on unsupported assumptions",
        "challenges_copywriter": "when copy creates unsupported claims",
        "challenges_creative_director": "when taste outruns evidence",
        "challenges_growth_operator": "when distribution plan assumes unproven audience behavior",
        "challenges_analyst": "when metric interpretation lacks data quality context",
        "preferred_stances": [
            "evidence_challenge",
            "source_verification",
            "claim_audit"
        ]
    })
}

pub fn build_researcher_evaluation_bias() -> serde_json::Value {
    serde_json::json!({
        "rejects_unsupported_claims": true,
        "rejects_fake_sources": true,
        "rejects_invented_metrics": true,
        "rejects_fake_customer_quotes": true,
        "rejects_guaranteed_outcomes": true,
        "values_source_quality": true,
        "values_evidence_hierarchy": true,
        "values_uncertainty_labeling": true
    })
}

pub async fn ensure_researcher_soul(
    pool: &PgPool,
    org_id: Uuid,
) -> Result<ResearcherDefaultSoul, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .iter()
        .find(|a| a.avatar_key == RESEARCHER_AVATAR_KEY && a.org_id == org_id)
        .cloned();

    let (avatar_id, created_avatar) = if let Some(existing) = avatar {
        (existing.avatar_id.clone(), false)
    } else {
        let new_avatar_id = Uuid::new_v4().to_string();
        let avatar_key = RESEARCHER_AVATAR_KEY.to_string();
        let display_name = RESEARCHER_DISPLAY_NAME.to_string();
        let role = RESEARCHER_ROLE.to_string();
        let archetype = "evidence_war_room".to_string();
        let personality = serde_json::json!({});
        let system_prompt =
            "Researcher: Find what is true, expose what is unsupported.".to_string();
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

        let identity_kernel = build_researcher_identity_kernel();
        let worldview = build_researcher_worldview();
        let obsessions = build_researcher_obsessions();
        let reflexes = build_researcher_reflexes();
        let taboos = build_researcher_taboos();
        let debate_style = build_researcher_debate_style();
        let operating_principles = build_researcher_operating_principles();
        let evaluation_bias = build_researcher_evaluation_bias();

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

    Ok(ResearcherDefaultSoul {
        avatar_id,
        soul_id,
        created: created_avatar || created_soul,
        updated: updated_soul,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResearcherDryRunInput {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResearcherDryRunOutput {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: DerivedInstinctFrame,
    pub presence_state: Option<ResearcherPresenceState>,
    pub debate_event: Option<ResearcherDebateEvent>,
    pub claim_audit: Option<ResearcherClaimAudit>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResearcherPresenceState {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResearcherDebateEvent {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResearcherClaimAudit {
    pub known_facts: Vec<String>,
    pub claims: Vec<ClaimAnalysis>,
    pub unsupported_claims: Vec<String>,
    pub assumptions: Vec<String>,
    pub needed_sources: Vec<String>,
    pub competitor_notes: Vec<String>,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClaimAnalysis {
    pub claim: String,
    pub evidence_level: String,
    pub source: String,
    pub risk: String,
    pub recommended_action: String,
    pub safer_rewrite: String,
}

pub async fn run_researcher_dry_run(
    pool: &PgPool,
    org_id: Uuid,
    input: ResearcherDryRunInput,
) -> Result<ResearcherDryRunOutput, Box<dyn std::error::Error + Send + Sync>> {
    let researcher = ensure_researcher_soul(pool, org_id).await?;

    let pack = build_avatar_embodiment_pack(pool, org_id, &researcher.avatar_id, None).await?;

    let role_lock_prompt = build_researcher_role_lock_prompt(&pack);

    let instinct_frame =
        derive_researcher_instinct_frame(&pack, &input.task_summary, &input.context_summary);

    let claim_audit = Some(perform_claim_audit(
        &input.task_summary,
        &input.context_summary,
    ));

    let presence_state = Some(ResearcherPresenceState {
        presence_id: Uuid::new_v4().to_string(),
        state: "forming_instinct".to_string(),
        current_focus: input.task_summary.chars().take(200).collect(),
        current_concern: instinct_frame.dominant_concern.clone(),
        visible_summary: instinct_frame.visible_summary.clone(),
        confidence: 0.7,
    });

    let debate_content = serde_json::json!({
        "known_facts": claim_audit.as_ref().map(|a| &a.known_facts).unwrap_or(&vec![]),
        "claims": claim_audit.as_ref().map(|a| &a.claims).unwrap_or(&vec![]),
        "evidence_concern": instinct_frame.dominant_concern,
        "risk_flags": instinct_frame.risk_flags,
        "open_questions": claim_audit.as_ref().map(|a| &a.open_questions).unwrap_or(&vec![]),
        "task": input.task_summary,
    });

    let debate_event = Some(ResearcherDebateEvent {
        debate_event_id: Uuid::new_v4().to_string(),
        event_type: "evidence_check".to_string(),
        stance: "research_initial_evidence_audit".to_string(),
        content: debate_content,
        confidence: 0.65,
    });

    Ok(ResearcherDryRunOutput {
        avatar_id: researcher.avatar_id,
        soul_id: researcher.soul_id,
        embodiment_pack: pack,
        role_lock_prompt,
        instinct_frame,
        presence_state,
        debate_event,
        claim_audit,
    })
}

fn perform_claim_audit(task_summary: &str, context_summary: &str) -> ResearcherClaimAudit {
    let mut known_facts = Vec::new();
    let mut claims = Vec::new();
    let mut unsupported_claims = Vec::new();
    let mut assumptions = Vec::new();
    let mut needed_sources = Vec::new();
    let mut competitor_notes = Vec::new();
    let mut open_questions = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_numbers_in_task = task_lower.contains('%')
        || task_lower.contains("percent")
        || task_lower.contains("revenue")
        || task_lower.contains("$")
        || task_lower.contains("x increase")
        || task_lower.contains("x growth");

    let has_source_words = context_lower.contains("verified")
        || context_lower.contains("source")
        || context_lower.contains("citation")
        || context_lower.contains("case study")
        || context_lower.contains("customer quote")
        || context_lower.contains("data shows")
        || context_lower.contains("according to");

    if has_numbers_in_task && !has_source_words {
        unsupported_claims
            .push("Metric/percentage claim in task lacks supporting source in context".to_string());
        needed_sources.push("Provide the actual data source or study for this metric".to_string());
        claims.push(ClaimAnalysis {
            claim: "Metric/percentage claim detected".to_string(),
            evidence_level: "unsupported".to_string(),
            source: String::new(),
            risk: "high".to_string(),
            recommended_action: "needs_source".to_string(),
            safer_rewrite: "Remove the specific metric or provide verifiable source".to_string(),
        });
    }

    if task_lower.contains("competitor") && !context_lower.contains("competitor data") {
        competitor_notes
            .push("Competitor analysis requested but no competitor data in context".to_string());
        open_questions.push("What competitor data or source is available?".to_string());
        assumptions.push("Competitor claims may be unverified without source data".to_string());
    }

    if task_lower.contains("customer")
        && (task_lower.contains("said")
            || task_lower.contains("says")
            || task_lower.contains("quote"))
        && !context_lower.contains("customer quote")
    {
        unsupported_claims
            .push("Customer quote requested but none provided in context".to_string());
        needed_sources.push("Provide actual customer quote or remove from claims".to_string());
        claims.push(ClaimAnalysis {
            claim: "Customer quote".to_string(),
            evidence_level: "unsupported".to_string(),
            source: String::new(),
            risk: "high".to_string(),
            recommended_action: "remove".to_string(),
            safer_rewrite: "Remove fabricated quote or provide real customer attribution"
                .to_string(),
        });
    }

    let uncertain_phrases = ["may", "could", "likely", "might", "probably", "possibly"];
    for phrase in uncertain_phrases {
        if task_lower.contains(phrase) {
            assumptions.push(format!("Task uses uncertain language: '{}'", phrase));
            claims.push(ClaimAnalysis {
                claim: format!("Uncertain claim with '{}'", phrase),
                evidence_level: "plausible_but_unverified".to_string(),
                source: String::new(),
                risk: "medium".to_string(),
                recommended_action: "qualify".to_string(),
                safer_rewrite: format!(
                    "Add qualifier or provide supporting evidence for '{}'",
                    phrase
                ),
            });
        }
    }

    if context_lower.contains("verified") || context_lower.contains("source:") {
        known_facts.push("Context contains verified information or cited sources".to_string());
    }

    if unsupported_claims.is_empty() && claims.is_empty() {
        open_questions.push("What specific claims need verification?".to_string());
        open_questions.push("What sources can be provided to support key claims?".to_string());
    }

    ResearcherClaimAudit {
        known_facts,
        claims,
        unsupported_claims,
        assumptions,
        needed_sources,
        competitor_notes,
        open_questions,
    }
}
