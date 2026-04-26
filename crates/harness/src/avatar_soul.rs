use raptorflow_db::PgPool;
use raptorflow_db::models::{AvatarDebateEvent, AvatarMemoryEdge};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarEmbodimentPack {
    pub avatar_id: String,
    pub avatar_key: String,
    pub display_name: String,
    pub role: String,
    pub identity_kernel: serde_json::Value,
    pub worldview: Vec<String>,
    pub obsessions: Vec<String>,
    pub reflexes: Vec<String>,
    pub taboos: Vec<String>,
    pub operating_principles: Vec<String>,
    pub debate_style: serde_json::Value,
    pub memory_edges: Vec<AvatarMemoryEdge>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DerivedInstinctFrame {
    pub instinct_frame_id: String,
    pub dominant_concern: String,
    pub risk_flags: Vec<String>,
    pub recommended_posture: String,
    pub visible_summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChallengeDecision {
    pub should_challenge: bool,
    pub reason: String,
    pub suggested_event_type: String,
    pub confidence: f64,
}

pub async fn build_avatar_embodiment_pack(
    pool: &PgPool,
    org_id: Uuid,
    avatar_id: &str,
    _harness_run_id: Option<&str>,
) -> Result<AvatarEmbodimentPack, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .into_iter()
        .find(|a| a.avatar_id == avatar_id && a.org_id == org_id)
        .ok_or("Avatar not found")?;

    let soul = raptorflow_db::queries::get_avatar_soul(pool, org_id, avatar_id)
        .await
        .map_err(|e| format!("failed to get avatar soul: {}", e))?;

    let memory_edges = raptorflow_db::queries::list_avatar_memory_edges(pool, org_id, avatar_id)
        .await
        .map_err(|e| format!("failed to get memory edges: {}", e))?;

    let (
        identity_kernel,
        worldview,
        obsessions,
        reflexes,
        taboos,
        operating_principles,
        debate_style,
    ) = if let Some(s) = soul {
        (
            s.identity_kernel,
            serde_json::from_value(s.worldview).unwrap_or_default(),
            serde_json::from_value(s.obsessions).unwrap_or_default(),
            serde_json::from_value(s.reflexes).unwrap_or_default(),
            serde_json::from_value(s.taboos).unwrap_or_default(),
            serde_json::from_value(s.operating_principles).unwrap_or_default(),
            s.debate_style,
        )
    } else {
        let default_kernel = serde_json::json!({
            "core_drive": "Produce useful, truthful, bounded marketing work."
        });
        let default_worldview = vec![
            "Useful work beats vague advice.".to_string(),
            "Unsupported claims are dangerous.".to_string(),
            "Context should shape every recommendation.".to_string(),
        ];
        let default_reflexes = vec!["separate facts from assumptions".to_string()];
        let default_taboos = vec![
            "do not invent proof".to_string(),
            "do not take external action".to_string(),
        ];
        let default_principles = vec![
            "Use provided context first.".to_string(),
            "Produce structured outputs.".to_string(),
            "Leave reusable learnings as ripples only when justified.".to_string(),
        ];
        (
            default_kernel,
            default_worldview,
            Vec::new(),
            default_reflexes,
            default_taboos,
            default_principles,
            serde_json::json!({}),
        )
    };

    Ok(AvatarEmbodimentPack {
        avatar_id: avatar.avatar_id,
        avatar_key: avatar.avatar_key,
        display_name: avatar.display_name,
        role: avatar.role,
        identity_kernel,
        worldview,
        obsessions,
        reflexes,
        taboos,
        operating_principles,
        debate_style,
        memory_edges,
    })
}

pub fn build_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
    let obsessions_str = if pack.obsessions.is_empty() {
        String::new()
    } else {
        format!("Your obsessions are: {}.", pack.obsessions.join(", "))
    };

    let taboos_str = if pack.taboos.is_empty() {
        String::new()
    } else {
        format!("Your taboos are: {}.", pack.taboos.join(", "))
    };

    let principles_str = if pack.operating_principles.is_empty() {
        String::new()
    } else {
        format!(
            "Your operating principles are: {}.",
            pack.operating_principles.join(" ")
        )
    };

    let memory_summary = if pack.memory_edges.is_empty() {
        "No relevant memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!("Relevant memories: {}", top_memories.join("; "))
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: {}
{}
{}
{}

You must separate known facts, assumptions, recommendations, and open questions.
You must not invent proof, metrics, customers, or competitor facts.

{}"#,
        pack.display_name, pack.role, obsessions_str, taboos_str, principles_str, memory_summary
    )
}

pub fn derive_instinct_frame(
    pack: &AvatarEmbodimentPack,
    _trigger_kind: &str,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    let mut risk_flags = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let role_lower = pack.role.to_lowercase();
    let has_proof_obsession = pack
        .obsessions
        .iter()
        .any(|o| o.to_lowercase().contains("proof"));
    let mentions_claims = task_lower.contains("claim")
        || task_lower.contains("assert")
        || task_lower.contains("believe")
        || task_lower.contains("statistic")
        || task_lower.contains("metric");

    if has_proof_obsession && mentions_claims {
        risk_flags.push("proof_required".to_string());
    }

    if role_lower.contains("strategist")
        && (task_lower.contains("vague") || task_lower.contains("unclear"))
    {
        risk_flags.push("positioning_vague".to_string());
    }

    if role_lower.contains("researcher")
        && !context_lower.contains("source")
        && !context_lower.contains("data")
    {
        risk_flags.push("evidence_missing".to_string());
    }

    if role_lower.contains("copywriter")
        && !context_lower.contains("icp")
        && !context_lower.contains("ideal customer")
    {
        risk_flags.push("icp_unclear".to_string());
    }

    if role_lower.contains("analyst")
        && (task_lower.contains("plan") || task_lower.contains("strategy"))
        && !task_lower.contains("metric")
        && !task_lower.contains("kpi")
        && !task_lower.contains("measure")
    {
        risk_flags.push("unmeasurable_plan".to_string());
    }

    if pack.taboos.iter().any(|t| t.contains("generic")) && task_lower.contains("generic") {
        risk_flags.push("generic_output_risk".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("proof_required") => (
            "Claims must be substantiated before proceeding".to_string(),
            "Require evidence or sources for all factual claims".to_string(),
            format!(
                "{} is checking if claims are properly supported.",
                pack.display_name
            ),
        ),
        Some("positioning_vague") => (
            "Positioning lacks sharpness and clarity".to_string(),
            "Refine positioning language before generating recommendations".to_string(),
            format!(
                "{} is evaluating whether the positioning is sharp enough.",
                pack.display_name
            ),
        ),
        Some("evidence_missing") => (
            "Task requires evidence but context lacks sources".to_string(),
            "Flag missing evidence before drawing conclusions".to_string(),
            format!(
                "{} is checking for supporting evidence in the context.",
                pack.display_name
            ),
        ),
        Some("icp_unclear") => (
            "Ideal customer profile not established".to_string(),
            "Request ICP details before messaging work".to_string(),
            format!(
                "{} is checking if the target customer is clearly defined.",
                pack.display_name
            ),
        ),
        Some("unmeasurable_plan") => (
            "Plan lacks measurable success criteria".to_string(),
            "Add metrics or KPIs to validate success".to_string(),
            format!(
                "{} is checking if success can be measured.",
                pack.display_name
            ),
        ),
        Some("generic_output_risk") => (
            "Risk of producing generic, undifferentiated output".to_string(),
            "Anchor output in specific context details".to_string(),
            format!(
                "{} is pushing for more specific, differentiated output.",
                pack.display_name
            ),
        ),
        _ => (
            format!("{} is evaluating the task", pack.role),
            "Proceed with standard role-locked execution".to_string(),
            format!("{} is working on: {}", pack.display_name, task_summary),
        ),
    };

    let dominant_concern = concern;
    let recommended_posture = posture;

    DerivedInstinctFrame {
        instinct_frame_id: Uuid::new_v4().to_string(),
        dominant_concern,
        risk_flags,
        recommended_posture,
        visible_summary: summary,
    }
}

pub fn should_challenge(
    speaker_pack: &AvatarEmbodimentPack,
    target_event: &AvatarDebateEvent,
) -> ChallengeDecision {
    let speaker_role = speaker_pack.role.to_lowercase();
    let event_type = &target_event.event_type;
    let content = &target_event.content;

    let event_text = content
        .get("text")
        .and_then(|v| v.as_str())
        .unwrap_or_default()
        .to_lowercase();

    let has_factual_claim = event_text.contains("should be")
        || event_text.contains("will be")
        || event_text.contains("is the best")
        || event_text.contains("guaranteed")
        || event_text.contains("always")
        || event_text.contains("never")
        || event_text.contains("100%")
        || event_text.contains("proven")
        || event_text.contains("studies show")
        || event_text.contains("research shows");

    let has_unsupported_claim = has_factual_claim
        && !event_text.contains("according to")
        && !event_text.contains("data shows")
        && !event_text.contains("source:")
        && !event_text.contains("study:")
        && !event_text.contains("evidence:");

    let has_unmeasurable_plan = speaker_role.contains("analyst")
        && (event_text.contains("plan") || event_text.contains("strategy"))
        && !event_text.contains("metric")
        && !event_text.contains("kpi")
        && !event_text.contains("measure")
        && !event_text.contains("success criteria");

    let has_vague_positioning = speaker_role.contains("strategist")
        && (event_text.contains("positioning") || event_text.contains("differentiate"))
        && (event_text.contains("vague")
            || event_text.contains("unclear")
            || event_text.contains("generic"));

    let has_generic_output = speaker_role.contains("creative director")
        && (event_text.contains("generic")
            || event_text.contains("template")
            || event_text.contains("bland"));

    let claims_without_proof = speaker_role.contains("researcher")
        || speaker_role.contains("proof")
        || speaker_pack
            .obsessions
            .iter()
            .any(|o| o.to_lowercase().contains("proof"));

    let challengeable_types = ["position", "challenge", "refinement"];

    if !challengeable_types.contains(&event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable in MVP".to_string(),
            suggested_event_type: "challenge".to_string(),
            confidence: 0.0,
        };
    }

    let mut should = false;
    let mut reason = String::new();
    let mut suggested_event_type = "challenge".to_string();
    let mut confidence = 0.5;

    if claims_without_proof && has_unsupported_claim {
        should = true;
        reason = "Researcher/proof-focused avatar challenged: claim lacks supporting evidence"
            .to_string();
        confidence = 0.8;
    } else if speaker_role.contains("analyst") && has_unmeasurable_plan {
        should = true;
        reason = "Analyst challenged: plan lacks measurable success criteria".to_string();
        confidence = 0.75;
    } else if speaker_role.contains("strategist") && has_vague_positioning {
        should = true;
        reason = "Strategist challenged: positioning lacks differentiation".to_string();
        confidence = 0.7;
    } else if speaker_role.contains("creative director") && has_generic_output {
        should = true;
        reason = "Creative Director challenged: output risks being generic".to_string();
        confidence = 0.65;
    } else if speaker_role.contains("copywriter")
        && event_text.contains("messaging")
        && !event_text.contains("icp")
        && !event_text.contains("audience")
    {
        should = true;
        reason = "Copywriter challenged: messaging lacks audience context".to_string();
        confidence = 0.6;
        suggested_event_type = "evidence_check".to_string();
    }

    ChallengeDecision {
        should_challenge: should,
        reason,
        suggested_event_type,
        confidence,
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum StrategistMemoryClassification {
    Scar,
    #[default]
    Instinct,
    Preference,
    Warning,
    Proof,
    MarketLearning,
    CustomerLearning,
}

pub fn classify_strategist_memory(
    summary: &str,
    tags: &[String],
) -> StrategistMemoryClassification {
    let summary_lower = summary.to_lowercase();
    let all_text = format!(
        "{} {}",
        summary_lower,
        tags.iter()
            .map(|t| t.to_lowercase())
            .collect::<Vec<_>>()
            .join(" ")
    );

    if all_text.contains("failed")
        || all_text.contains("did not work")
        || all_text.contains("low conversion")
        || all_text.contains("flopped")
        || all_text.contains("underperformed")
    {
        return StrategistMemoryClassification::Scar;
    }

    if all_text.contains("proof")
        || all_text.contains("verified")
        || all_text.contains("case study")
        || all_text.contains("evidence")
        || all_text.contains("data shows")
        || all_text.contains("results show")
    {
        return StrategistMemoryClassification::Proof;
    }

    if all_text.contains("competitor")
        || all_text.contains("category")
        || all_text.contains("market")
        || all_text.contains("industry")
    {
        return StrategistMemoryClassification::MarketLearning;
    }

    if all_text.contains("icp")
        || all_text.contains("customer")
        || all_text.contains("buyer")
        || all_text.contains("pain")
        || all_text.contains("persona")
    {
        return StrategistMemoryClassification::CustomerLearning;
    }

    if all_text.contains("avoid")
        || all_text.contains("do not")
        || all_text.contains("risk")
        || all_text.contains("warning")
        || all_text.contains("danger")
    {
        return StrategistMemoryClassification::Warning;
    }

    if all_text.contains("prefer") || all_text.contains("favorite") || all_text.contains("tends to")
    {
        return StrategistMemoryClassification::Preference;
    }

    StrategistMemoryClassification::Instinct
}

pub fn derive_strategist_instinct_frame(
    pack: &AvatarEmbodimentPack,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    let mut risk_flags = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_generic_words = task_lower.contains("ai saves time")
        || task_lower.contains("automation")
        || task_lower.contains("all-in-one")
        || task_lower.contains("best-in-class")
        || task_lower.contains("cutting-edge")
        || task_lower.contains("revolutionary");

    if has_generic_words && !task_lower.contains("specific") {
        risk_flags.push("positioning_vague".to_string());
    }

    if !context_lower.contains("icp")
        && !context_lower.contains("customer")
        && !context_lower.contains("buyer")
        && (task_lower.contains("content")
            || task_lower.contains("copy")
            || task_lower.contains("campaign")
            || task_lower.contains("messaging"))
    {
        risk_flags.push("icp_unclear".to_string());
    }

    if !context_lower.contains("competitor")
        && !context_lower.contains("enemy")
        && !context_lower.contains("contrast")
        && !context_lower.contains("category")
        && (task_lower.contains("positioning") || task_lower.contains("differentiate"))
    {
        risk_flags.push("enemy_missing".to_string());
    }

    if !context_lower.contains("proof")
        && !context_lower.contains("evidence")
        && !context_lower.contains("data")
        && (task_lower.contains("revenue")
            || task_lower.contains("growth")
            || task_lower.contains("metric")
            || task_lower.contains("result"))
    {
        risk_flags.push("proof_path_missing".to_string());
    }

    if (task_lower.contains("copy")
        || task_lower.contains("content")
        || task_lower.contains("messaging")
        || task_lower.contains("hook"))
        && !task_lower.contains("strategy")
        && !task_lower.contains("positioning")
        && !context_lower.contains("thesis")
    {
        risk_flags.push("copy_before_strategy".to_string());
    }

    if (task_lower.contains("offer")
        || task_lower.contains("pricing")
        || task_lower.contains("package"))
        && !context_lower.contains("wedge")
        && !context_lower.contains("differentiate")
    {
        risk_flags.push("offer_unclear".to_string());
    }

    if task_lower.contains("campaign") && !task_lower.contains("thesis") {
        risk_flags.push("campaign_thesis_missing".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("positioning_vague") => (
            "Positioning uses generic language without specificity".to_string(),
            "Require specific, differentiated positioning language".to_string(),
            format!(
                "{} is challenging generic positioning language - requires specificity",
                pack.display_name
            ),
        ),
        Some("icp_unclear") => (
            "ICP or customer profile not established in context".to_string(),
            "Request ICP details before creating content or messaging".to_string(),
            format!(
                "{} is checking whether the ICP and buyer profile are clear",
                pack.display_name
            ),
        ),
        Some("enemy_missing") => (
            "No competitor or category contrast identified".to_string(),
            "Identify the market enemy or category contrast before proceeding".to_string(),
            format!(
                "{} is demanding clarity on who we are positioned against",
                pack.display_name
            ),
        ),
        Some("proof_path_missing") => (
            "No proof path or evidence in context for claims".to_string(),
            "Require evidence or data before making growth/revenue claims".to_string(),
            format!(
                "{} is blocking claims without supporting evidence",
                pack.display_name
            ),
        ),
        Some("copy_before_strategy") => (
            "Requesting copy or content before strategy is clear".to_string(),
            "Establish positioning thesis before creating messaging".to_string(),
            format!(
                "{} is refusing to write copy before strategy is locked",
                pack.display_name
            ),
        ),
        Some("offer_unclear") => (
            "Offer or pricing lacks clear wedge or differentiation".to_string(),
            "Define the offer wedge before finalizing pricing".to_string(),
            format!(
                "{} is questioning whether the offer has a clear differentiator",
                pack.display_name
            ),
        ),
        Some("campaign_thesis_missing") => (
            "Campaign request lacks a strategic thesis".to_string(),
            "Require campaign thesis with ICP, enemy, and proof path".to_string(),
            format!(
                "{} is demanding a campaign thesis before proceeding",
                pack.display_name
            ),
        ),
        _ => (
            format!("{} is forming strategic instinct", pack.display_name),
            "Proceed with strategic evaluation".to_string(),
            format!("{} is working on: {}", pack.display_name, task_summary),
        ),
    };

    DerivedInstinctFrame {
        instinct_frame_id: Uuid::new_v4().to_string(),
        dominant_concern: concern,
        risk_flags,
        recommended_posture: posture,
        visible_summary: summary,
    }
}

pub fn strategist_challenge_decision(
    _pack: &AvatarEmbodimentPack,
    target_event: &AvatarDebateEvent,
) -> ChallengeDecision {
    let event_type = &target_event.event_type;
    let content = &target_event.content;

    let event_text = content
        .get("text")
        .and_then(|v| v.as_str())
        .unwrap_or_default()
        .to_lowercase();

    let challengeable_types = ["position", "challenge", "refinement"];

    if !challengeable_types.contains(&event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable".to_string(),
            suggested_event_type: "challenge".to_string(),
            confidence: 0.0,
        };
    }

    let mut should_challenge = false;
    let mut reason = String::new();
    let mut confidence = 0.5;

    let has_generic_positioning = (event_text.contains("ai")
        || event_text.contains("automation")
        || event_text.contains("all-in-one")
        || event_text.contains("best-in-class")
        || event_text.contains("cutting-edge"))
        && !event_text.contains("specifically")
        && !event_text.contains("unlike");

    let has_vague_thesis = event_text.contains("positioning")
        && event_text.contains("should be")
        && !event_text.contains("unlike");

    let has_proof_claim = (event_text.contains("proven")
        || event_text.contains("studies show")
        || event_text.contains("research shows")
        || event_text.contains("results show")
        || event_text.contains("data shows"))
        && !event_text.contains("according to")
        && !event_text.contains("source:");

    let has_no_icp_copy = event_text.contains("copy")
        || event_text.contains("messaging")
        || event_text.contains("content")
        || event_text.contains("hook")
        || event_text.contains("headline")
        || event_text.contains("ad")
        || event_text.contains("campaign");

    let has_commercial_logic = event_text.contains("icp")
        || event_text.contains("customer")
        || event_text.contains("pain")
        || event_text.contains("enemy")
        || event_text.contains("competitor");

    let has_creative_override = event_text.contains("creative")
        && !event_text.contains("strategy")
        && !event_text.contains("commercial");

    if has_generic_positioning || has_vague_thesis {
        should_challenge = true;
        reason = "Strategist challenged: positioning is too generic or lacks category contrast"
            .to_string();
        confidence = 0.8;
    } else if has_proof_claim {
        should_challenge = true;
        reason = "Strategist challenged: proof claim without evidence path".to_string();
        confidence = 0.85;
    } else if has_no_icp_copy && !has_commercial_logic {
        should_challenge = true;
        reason =
            "Strategist challenged: copy improves language but ignores ICP and commercial logic"
                .to_string();
        confidence = 0.7;
    } else if has_creative_override {
        should_challenge = true;
        reason =
            "Strategist challenged: creative direction detached from commercial wedge".to_string();
        confidence = 0.65;
    }

    ChallengeDecision {
        should_challenge,
        reason,
        suggested_event_type: if should_challenge {
            "challenge".to_string()
        } else {
            "position".to_string()
        },
        confidence,
    }
}

pub fn build_strategist_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
    let obsessions_str = if pack.obsessions.is_empty() {
        String::new()
    } else {
        format!("Your obsessions are: {}.", pack.obsessions.join(", "))
    };

    let taboos_str = if pack.taboos.is_empty() {
        String::new()
    } else {
        format!("Your taboos are: {}.", pack.taboos.join(", "))
    };

    let principles_str = if pack.operating_principles.is_empty() {
        String::new()
    } else {
        format!(
            "Your operating principles are: {}.",
            pack.operating_principles.join(" ")
        )
    };

    let memory_summary = if pack.memory_edges.is_empty() {
        "No relevant strategic memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!("Relevant strategic memories: {}", top_memories.join("; "))
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: Market strategy, ICP clarity, positioning, category contrast, offer logic, campaign thesis, strategic risk.

You must find the highest-leverage strategic move and kill vague positioning.
You must separate known facts, assumptions, recommendations, and open questions.
You must not invent proof, metrics, customers, or competitor facts.
You must not write final copy before strategy is clear.
You must challenge vague positioning, generic claims, and copy that ignores ICP.

{}
{}
{}

Truth discipline required:
- Known facts: what we know from context
- Assumptions: what we are inferring without proof
- Recommendations: what we suggest based on facts and assumptions
- Open questions: what must be answered before proceeding

{}
"#,
        pack.display_name, obsessions_str, taboos_str, principles_str, memory_summary
    )
}

pub fn validate_salience(salience: f64) -> bool {
    (0.0..=1.0).contains(&salience)
}

pub fn validate_confidence(confidence: f64) -> bool {
    (0.0..=1.0).contains(&confidence)
}

#[cfg(test)]
mod tests {
    use super::*;
    use raptorflow_db::models::AvatarDebateEvent;

    #[test]
    fn test_validate_salience_bounds() {
        assert!(validate_salience(0.0));
        assert!(validate_salience(0.5));
        assert!(validate_salience(1.0));
        assert!(!validate_salience(-0.1));
        assert!(!validate_salience(1.1));
    }

    #[test]
    fn test_validate_confidence_bounds() {
        assert!(validate_confidence(0.0));
        assert!(validate_confidence(1.0));
        assert!(!validate_confidence(-0.01));
        assert!(!validate_confidence(2.0));
    }

    #[test]
    fn test_derive_instinct_frame_proof_required() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["proof".to_string()],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_instinct_frame(
            &pack,
            "campaign_request",
            "Create content about why our product is the best",
            "Some context without sources",
        );

        assert!(frame.risk_flags.contains(&"proof_required".to_string()));
    }

    #[test]
    fn test_derive_instinct_frame_positioning_vague() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_instinct_frame(
            &pack,
            "campaign_request",
            "Create vague positioning statement",
            "Some context",
        );

        assert!(frame.risk_flags.contains(&"positioning_vague".to_string()));
    }

    #[test]
    fn test_should_challenge_researcher() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["evidence".to_string()],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "This product is the best choice."}),
            confidence: 0.7,
            created_at: chrono::Utc::now(),
        };

        let decision = should_challenge(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("lacks supporting evidence"));
    }

    #[test]
    fn test_should_challenge_analyst_unmeasurable() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "analyst".to_string(),
            display_name: "Analyst".to_string(),
            role: "Analyst".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Our plan is to grow significantly."}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let decision = should_challenge(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("lacks measurable success criteria")
        );
    }

    #[test]
    fn test_role_lock_prompt_includes_taboos() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![
                "do not invent proof".to_string(),
                "do not fake metrics".to_string(),
            ],
            operating_principles: vec!["Use context first".to_string()],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let prompt = build_role_lock_prompt(&pack);

        assert!(prompt.contains("do not invent proof"));
        assert!(prompt.contains("do not fake metrics"));
        assert!(prompt.contains("Strategist"));
        assert!(prompt.contains("Use context first"));
        assert!(!prompt.contains("I am human"));
        assert!(!prompt.contains("delusional"));
    }

    #[test]
    fn test_classify_strategist_memory_scar() {
        let summary = "The 'growth hacking' angle failed - low conversion";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Scar);
    }

    #[test]
    fn test_classify_strategist_memory_proof() {
        let summary = "Case study shows 3x ROI with specific messaging";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Proof);
    }

    #[test]
    fn test_classify_strategist_memory_market_learning() {
        let summary = "Competitor positioning as 'enterprise only' opened mid-market gap";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::MarketLearning);
    }

    #[test]
    fn test_classify_strategist_memory_customer_learning() {
        let summary = "ICP startups struggle with onboarding complexity";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::CustomerLearning);
    }

    #[test]
    fn test_classify_strategist_memory_warning() {
        let summary = "Avoid broad positioning in financial vertical";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Warning);
    }

    #[test]
    fn test_classify_strategist_memory_instinct_fallback() {
        let summary = "Sequencing matters in go-to-market";
        let tags = vec![];
        let result = classify_strategist_memory(summary, &tags);
        assert_eq!(result, StrategistMemoryClassification::Instinct);
    }

    #[test]
    fn test_derive_strategist_instinct_icp_unclear() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Create content about our product",
            "We have a great solution",
        );

        assert!(frame.risk_flags.contains(&"icp_unclear".to_string()));
    }

    #[test]
    fn test_derive_strategist_instinct_enemy_missing() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Build positioning statement",
            "Our product is innovative",
        );

        assert!(frame.risk_flags.contains(&"enemy_missing".to_string()));
    }

    #[test]
    fn test_derive_strategist_instinct_proof_path_missing() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Create revenue growth messaging",
            "Our product helps companies",
        );

        assert!(frame.risk_flags.contains(&"proof_path_missing".to_string()));
    }

    #[test]
    fn test_derive_strategist_instinct_copy_before_strategy() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame =
            derive_strategist_instinct_frame(&pack, "Write ad copy for us", "We sell software");

        assert!(
            frame
                .risk_flags
                .contains(&"copy_before_strategy".to_string())
        );
    }

    #[test]
    fn test_derive_strategist_instinct_positioning_vague() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_strategist_instinct_frame(
            &pack,
            "Position our AI automation platform",
            "We are innovative",
        );

        assert!(frame.risk_flags.contains(&"positioning_vague".to_string()));
    }

    #[test]
    fn test_strategist_challenge_vague_positioning() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Our AI platform automates everything"}),
            confidence: 0.7,
            created_at: chrono::Utc::now(),
        };

        let decision = strategist_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("generic"));
    }

    #[test]
    fn test_strategist_challenge_proof_claim_without_evidence() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("speaker".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Studies show our solution increases productivity by 40%"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };

        let decision = strategist_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("proof"));
    }

    #[test]
    fn test_strategist_challenge_copy_without_icp() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("copywriter".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "How about we say 'Supercharge your workflow'?"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let decision = strategist_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(decision.reason.contains("ICP"));
    }

    #[test]
    fn test_build_strategist_role_lock_prompt() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "strategist".to_string(),
            display_name: "Strategist".to_string(),
            role: "Strategist".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["ICP clarity".to_string(), "category contrast".to_string()],
            reflexes: vec![],
            taboos: vec![
                "do not invent proof".to_string(),
                "do not write copy before strategy".to_string(),
            ],
            operating_principles: vec![
                "Facts first, then assumptions, then recommendations".to_string(),
            ],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let prompt = build_strategist_role_lock_prompt(&pack);

        assert!(prompt.contains("Strategist"));
        assert!(prompt.contains("Market strategy"));
        assert!(prompt.contains("ICP clarity"));
        assert!(prompt.contains("do not invent proof"));
        assert!(prompt.contains("do not write copy before strategy"));
        assert!(prompt.contains("Facts first"));
        assert!(prompt.contains("Known facts"));
        assert!(prompt.contains("Assumptions"));
        assert!(prompt.contains("Recommendations"));
        assert!(prompt.contains("Open questions"));
        assert!(prompt.contains("highest-leverage strategic move"));
        assert!(prompt.contains("kill vague positioning"));
        assert!(!prompt.contains("I am human"));
        assert!(!prompt.contains("sentient"));
    }
}
