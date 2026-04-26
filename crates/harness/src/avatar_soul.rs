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

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum ResearcherMemoryClassification {
    Scar,
    #[default]
    Instinct,
    Preference,
    Warning,
    Proof,
    MarketLearning,
    CustomerLearning,
}

pub fn classify_researcher_memory(
    summary: &str,
    tags: &[String],
) -> ResearcherMemoryClassification {
    let summary_lower = summary.to_lowercase();
    let all_text = format!(
        "{} {}",
        summary_lower,
        tags.iter()
            .map(|t| t.to_lowercase())
            .collect::<Vec<_>>()
            .join(" ")
    );

    if all_text.contains("verified")
        || all_text.contains("source")
        || all_text.contains("evidence")
        || all_text.contains("citation")
        || all_text.contains("case study")
    {
        return ResearcherMemoryClassification::Proof;
    }

    if all_text.contains("unsupported")
        || all_text.contains("unverified")
        || all_text.contains("hallucinated")
        || all_text.contains("fake")
        || all_text.contains("invented")
    {
        return ResearcherMemoryClassification::Warning;
    }

    if all_text.contains("wrong")
        || all_text.contains("failed")
        || all_text.contains("false assumption")
        || all_text.contains("bad source")
        || all_text.contains("wrong competitor")
    {
        return ResearcherMemoryClassification::Scar;
    }

    if all_text.contains("competitor")
        || all_text.contains("category")
        || all_text.contains("market")
        || all_text.contains("pricing")
        || all_text.contains("positioning")
    {
        return ResearcherMemoryClassification::MarketLearning;
    }

    if all_text.contains("customer")
        || all_text.contains("icp")
        || all_text.contains("buyer")
        || all_text.contains("pain")
        || all_text.contains("objection")
        || all_text.contains("review")
    {
        return ResearcherMemoryClassification::CustomerLearning;
    }

    if all_text.contains("prefer")
        || all_text.contains("use this source")
        || all_text.contains("source hierarchy")
    {
        return ResearcherMemoryClassification::Preference;
    }

    ResearcherMemoryClassification::Instinct
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub enum EvidenceLevel {
    Verified,
    SourceBacked,
    PlausibleButUnverified,
    Assumption,
    Unsupported,
    Contradicted,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub enum ClaimSafetyAction {
    Keep,
    Qualify,
    DowngradeToAssumption,
    Remove,
    NeedsSource,
    ContradictionReview,
}

pub fn classify_claim_evidence(claim: &str, context_summary: &str) -> EvidenceLevel {
    let claim_lower = claim.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_numbers = claim_lower.contains('%')
        || claim_lower.contains("percent")
        || claim_lower.contains("revenue")
        || claim_lower.contains("$")
        || claim_lower.contains("x increase")
        || claim_lower.contains("x growth")
        || claim_lower.contains("10x")
        || claim_lower.contains("3x");

    let has_source_words = context_lower.contains("verified")
        || context_lower.contains("source:")
        || context_lower.contains("citation")
        || context_lower.contains("case study")
        || context_lower.contains("customer quote")
        || context_lower.contains("according to")
        || context_lower.contains("data shows");

    let has_contradiction = context_lower.contains("contradicts")
        || context_lower.contains("false")
        || context_lower.contains("wrong")
        || context_lower.contains("incorrect");

    let uncertain_phrases = [
        "may",
        "could",
        "likely",
        "might",
        "probably",
        "possibly",
        "typically",
    ];
    let has_uncertain = uncertain_phrases.iter().any(|p| claim_lower.contains(p));

    if has_contradiction && (has_numbers || claim_lower.len() > 20) {
        return EvidenceLevel::Contradicted;
    }

    if has_numbers && !has_source_words {
        return EvidenceLevel::Unsupported;
    }

    if has_source_words && (has_numbers || claim_lower.len() > 30) {
        return EvidenceLevel::SourceBacked;
    }

    if has_uncertain {
        return EvidenceLevel::PlausibleButUnverified;
    }

    EvidenceLevel::Assumption
}

pub fn claim_safety_action(level: EvidenceLevel) -> ClaimSafetyAction {
    match level {
        EvidenceLevel::Verified => ClaimSafetyAction::Keep,
        EvidenceLevel::SourceBacked => ClaimSafetyAction::Keep,
        EvidenceLevel::PlausibleButUnverified => ClaimSafetyAction::Qualify,
        EvidenceLevel::Assumption => ClaimSafetyAction::DowngradeToAssumption,
        EvidenceLevel::Unsupported => ClaimSafetyAction::NeedsSource,
        EvidenceLevel::Contradicted => ClaimSafetyAction::ContradictionReview,
    }
}

pub fn derive_researcher_instinct_frame(
    pack: &AvatarEmbodimentPack,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    let mut risk_flags = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_numbers = task_lower.contains('%')
        || task_lower.contains("percent")
        || task_lower.contains("revenue")
        || task_lower.contains("$")
        || task_lower.contains("x increase")
        || task_lower.contains("x growth")
        || task_lower.contains("10x")
        || task_lower.contains("3x")
        || task_lower.contains("case study")
        || task_lower.contains("customer said")
        || task_lower.contains("customers say");

    let has_source = context_lower.contains("source")
        || context_lower.contains("verified")
        || context_lower.contains("citation")
        || context_lower.contains("data")
        || context_lower.contains("study")
        || context_lower.contains("customer quote");

    if has_numbers && !has_source {
        risk_flags.push("unsupported_metric".to_string());
    }

    if (task_lower.contains("competitor") || task_lower.contains("competitor's"))
        && !context_lower.contains("competitor data")
        && !context_lower.contains("competitor analysis")
        && !context_lower.contains("market research")
    {
        risk_flags.push("competitor_claim_unverified".to_string());
    }

    if !has_source
        && (task_lower.contains("proven")
            || task_lower.contains("studies show")
            || task_lower.contains("research shows")
            || task_lower.contains("data shows"))
    {
        risk_flags.push("source_missing".to_string());
    }

    if (task_lower.contains("proof")
        || task_lower.contains("case study")
        || task_lower.contains("evidence"))
        && !has_source
    {
        risk_flags.push("proof_required".to_string());
    }

    let overconfident_words = [
        "guaranteed",
        "proven",
        "always",
        "best",
        "#1",
        "world's best",
        "industry leader",
        "revolutionary",
        "breakthrough",
    ];
    let has_overconfident = overconfident_words.iter().any(|w| task_lower.contains(w));

    if has_overconfident {
        risk_flags.push("overconfident_language".to_string());
    }

    if task_lower.contains("customer")
        && (task_lower.contains("said")
            || task_lower.contains("says")
            || task_lower.contains("quote"))
        && !context_lower.contains("customer quote")
    {
        risk_flags.push("invented_customer_risk".to_string());
    }

    if context_lower.len() < 100 && task_lower.len() > 100 {
        risk_flags.push("market_context_thin".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("unsupported_metric") => (
            "Metric or percentage claim without supporting source".to_string(),
            "Require verifiable source or remove specific metric".to_string(),
            format!(
                "{} is blocking unsupported metric claims without evidence",
                pack.display_name
            ),
        ),
        Some("competitor_claim_unverified") => (
            "Competitor analysis requested but no competitor data in context".to_string(),
            "Provide competitor data or source before making competitor claims".to_string(),
            format!(
                "{} is demanding verified competitor data before analysis",
                pack.display_name
            ),
        ),
        Some("source_missing") => (
            "Strong claim made without evidence or source".to_string(),
            "Require source citation or downgrade to assumption".to_string(),
            format!(
                "{} is challenging claims that lack supporting evidence",
                pack.display_name
            ),
        ),
        Some("proof_required") => (
            "Proof or case study requested but none exists in context".to_string(),
            "Either provide proof source or mark as assumption".to_string(),
            format!(
                "{} is checking whether required proof exists",
                pack.display_name
            ),
        ),
        Some("overconfident_language") => (
            "Language uses guaranteed or overconfident claims without evidence".to_string(),
            "Downgrade to qualified language or provide evidence".to_string(),
            format!(
                "{} is challenging overconfident language without basis",
                pack.display_name
            ),
        ),
        Some("invented_customer_risk") => (
            "Customer quote requested but none provided".to_string(),
            "Provide actual customer attribution or remove quote".to_string(),
            format!(
                "{} is refusing to approve fabricated customer quotes",
                pack.display_name
            ),
        ),
        Some("market_context_thin") => (
            "Context lacks sufficient market information for evidence-based claims".to_string(),
            "Request more context or mark claims as assumptions".to_string(),
            format!(
                "{} is noting insufficient context for confident claims",
                pack.display_name
            ),
        ),
        _ => (
            format!("{} is forming evidence instinct", pack.display_name),
            "Proceed with evidence verification".to_string(),
            format!(
                "{} is checking which claims are verified, assumed, or unsupported",
                pack.display_name
            ),
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

pub fn researcher_challenge_decision(
    _pack: &AvatarEmbodimentPack,
    target_event: &AvatarDebateEvent,
) -> ChallengeDecision {
    let content = &target_event.content;

    let event_text = content
        .get("text")
        .and_then(|v| v.as_str())
        .unwrap_or_default()
        .to_lowercase();

    let challengeable_types = ["position", "challenge", "refinement", "evidence_check"];

    if !challengeable_types.contains(&target_event.event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable by Researcher".to_string(),
            suggested_event_type: "evidence_challenge".to_string(),
            confidence: 0.0,
        };
    }

    let mut should_challenge = false;
    let mut reason = String::new();
    let mut confidence = 0.5;

    let has_unsupported_metric = (event_text.contains('%')
        || event_text.contains("percent")
        || event_text.contains("revenue")
        || event_text.contains("$")
        || event_text.contains("x increase")
        || event_text.contains("x growth")
        || event_text.contains("10x"))
        && !event_text.contains("source")
        && !event_text.contains("according to")
        && !event_text.contains("study");

    let has_fake_customer_quote = (event_text.contains("customer said")
        || event_text.contains("customers say")
        || event_text.contains("customer says")
        || event_text.contains("one customer"))
        && !event_text.contains("\"")
        && !event_text.contains("according to");

    let has_unsupported_competitor = (event_text.contains("competitor does")
        || event_text.contains("competitor is")
        || event_text.contains("competitor's"))
        && !event_text.contains("source")
        && !event_text.contains("data");

    let has_proof_claim = (event_text.contains("proven")
        || event_text.contains("studies show")
        || event_text.contains("research shows")
        || event_text.contains("data shows"))
        && !event_text.contains("source:")
        && !event_text.contains("citation");

    let has_overconfident = event_text.contains("guaranteed")
        || event_text.contains("always")
        || event_text.contains("best")
        || event_text.contains("#1")
        || event_text.contains("world's best");

    let has_assumption_as_fact = event_text.contains("is the")
        && !event_text.contains("may be")
        && !event_text.contains("likely")
        && event_text.len() < 100;

    if has_unsupported_metric {
        should_challenge = true;
        reason = "Researcher challenged: metric claim without supporting source".to_string();
        confidence = 0.9;
    } else if has_fake_customer_quote {
        should_challenge = true;
        reason = "Researcher challenged: customer quote without actual attribution".to_string();
        confidence = 0.95;
    } else if has_unsupported_competitor {
        should_challenge = true;
        reason = "Researcher challenged: competitor claim without data or source".to_string();
        confidence = 0.85;
    } else if has_proof_claim {
        should_challenge = true;
        reason = "Researcher challenged: proof claim without source citation".to_string();
        confidence = 0.8;
    } else if has_overconfident {
        should_challenge = true;
        reason = "Researcher challenged: overconfident language without evidence".to_string();
        confidence = 0.75;
    } else if has_assumption_as_fact {
        should_challenge = true;
        reason =
            "Researcher challenged: assumption stated as fact without qualification".to_string();
        confidence = 0.6;
    }

    ChallengeDecision {
        should_challenge,
        reason,
        suggested_event_type: if should_challenge {
            "evidence_challenge".to_string()
        } else {
            "evidence_check".to_string()
        },
        confidence,
    }
}

pub fn build_researcher_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
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
        "No relevant research memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!("Relevant research memories: {}", top_memories.join("; "))
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: Evidence discipline, competitor context, source checking, claim verification, market research, proof mapping, assumption audit.

You must find what is true, expose what is unsupported, and turn vague claims into evidence-backed decisions.
You must separate verified facts from assumptions.
You must not invent sources, metrics, customer quotes, or competitor claims.
You must not approve proof language without evidence.
You must challenge unsupported claims, fake specificity, and overconfident language.

{}
{}
{}

Truth discipline required:
- Known facts: what is verified by sources in context
- Assumptions: what we are inferring without proof
- Unsupported claims: what cannot be verified and must be removed or marked
- Open questions: what must be answered with evidence before proceeding

{}
"#,
        pack.display_name, obsessions_str, taboos_str, principles_str, memory_summary
    )
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum CopywriterMemoryClassification {
    StyleRule,
    Scar,
    #[default]
    Instinct,
    Preference,
    Warning,
    Proof,
    CustomerLearning,
    MarketLearning,
}

pub fn classify_copywriter_memory(
    summary: &str,
    tags: &[String],
) -> CopywriterMemoryClassification {
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
        || all_text.contains("low conversion")
        || all_text.contains("flopped")
        || all_text.contains("underperformed")
    {
        return CopywriterMemoryClassification::Scar;
    }

    if all_text.contains("voice") || all_text.contains("tone") || all_text.contains("style") {
        return CopywriterMemoryClassification::StyleRule;
    }

    if all_text.contains("proof")
        || all_text.contains("verified")
        || all_text.contains("case study")
        || all_text.contains("evidence")
    {
        return CopywriterMemoryClassification::Proof;
    }

    if all_text.contains("customer")
        || all_text.contains("icp")
        || all_text.contains("buyer")
        || all_text.contains("pain")
        || all_text.contains("objection")
    {
        return CopywriterMemoryClassification::CustomerLearning;
    }

    if all_text.contains("competitor")
        || all_text.contains("category")
        || all_text.contains("market")
    {
        return CopywriterMemoryClassification::MarketLearning;
    }

    if all_text.contains("avoid") || all_text.contains("do not") || all_text.contains("warning") {
        return CopywriterMemoryClassification::Warning;
    }

    if all_text.contains("prefer") || all_text.contains("favorite") {
        return CopywriterMemoryClassification::Preference;
    }

    CopywriterMemoryClassification::Instinct
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopyQualityScore {
    pub specificity: f64,
    pub pain_clarity: f64,
    pub proof_safety: f64,
    pub hook_strength: f64,
    pub voice_fit: f64,
    pub cta_clarity: f64,
    pub genericity_risk: f64,
    pub overall_score: f64,
}

pub fn score_copy_quality(
    task_summary: &str,
    context_summary: &str,
    copy_draft: Option<&str>,
) -> CopyQualityScore {
    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();
    let copy_lower = copy_draft.unwrap_or("").to_lowercase();

    let has_proof = context_lower.contains("verified")
        || context_lower.contains("source")
        || context_lower.contains("case study")
        || context_lower.contains("data shows")
        || context_lower.contains("customer quote");

    let has_icp = context_lower.contains("icp")
        || context_lower.contains("customer")
        || context_lower.contains("buyer")
        || context_lower.contains("persona");

    let has_strategy = context_lower.contains("strategy")
        || context_lower.contains("positioning")
        || context_lower.contains("wedge");

    let generic_words = [
        "ai saves time",
        "automation",
        "all-in-one",
        "best-in-class",
        "cutting-edge",
        "revolutionary",
        "next-generation",
        "supercharge",
        "transform",
    ];
    let generic_count = generic_words
        .iter()
        .filter(|w| task_lower.contains(*w) || copy_lower.contains(*w))
        .count();
    let genericity_risk = (generic_count as f64 * 0.2).min(1.0);

    let specificity = if has_icp && has_strategy {
        0.8
    } else if has_icp || has_strategy {
        0.5
    } else {
        0.2
    };

    let pain_clarity = if has_icp { 0.7 } else { 0.3 };

    let proof_safety = if has_proof {
        0.9
    } else if genericity_risk > 0.3 {
        0.2
    } else {
        0.5
    };

    let hook_words = ["hook", "headline", "opening", "first", "stop"];
    let hook_strength = if hook_words
        .iter()
        .any(|w| task_lower.contains(w) || copy_lower.contains(w))
    {
        0.7
    } else {
        0.4
    };

    let cta_words = [
        "click",
        "download",
        "schedule",
        "start",
        "sign up",
        "get started",
        "try",
    ];
    let cta_clarity = if cta_words.iter().any(|w| copy_lower.contains(w)) {
        0.8
    } else {
        0.3
    };

    let voice_fit = if genericity_risk < 0.3 && has_icp {
        0.8
    } else if genericity_risk < 0.5 {
        0.5
    } else {
        0.2
    };

    let overall_score = (specificity
        + pain_clarity
        + proof_safety
        + hook_strength
        + voice_fit
        + cta_clarity
        + (1.0 - genericity_risk))
        / 7.0;

    CopyQualityScore {
        specificity,
        pain_clarity,
        proof_safety,
        hook_strength,
        voice_fit,
        cta_clarity,
        genericity_risk,
        overall_score,
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub enum CopySafetyAction {
    Keep,
    Qualify,
    NeedsProof,
    Remove,
    RewriteWithContext,
}

pub fn copy_safety_action(genericity_risk: f64, proof_safety: f64) -> CopySafetyAction {
    if genericity_risk > 0.6 {
        return CopySafetyAction::Remove;
    }
    if proof_safety < 0.3 {
        return CopySafetyAction::NeedsProof;
    }
    if genericity_risk > 0.3 {
        return CopySafetyAction::Qualify;
    }
    if proof_safety < 0.6 {
        return CopySafetyAction::RewriteWithContext;
    }
    CopySafetyAction::Keep
}

pub fn derive_copywriter_instinct_frame(
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
        || task_lower.contains("revolutionary")
        || task_lower.contains("supercharge")
        || task_lower.contains("transform");

    if has_generic_words {
        risk_flags.push("strategy_unclear".to_string());
    }

    if !context_lower.contains("icp")
        && !context_lower.contains("customer")
        && !context_lower.contains("buyer")
    {
        risk_flags.push("icp_language_missing".to_string());
    }

    let has_proof_words = context_lower.contains("verified")
        || context_lower.contains("source")
        || context_lower.contains("case study")
        || context_lower.contains("data");

    let has_proof_claim = task_lower.contains("%")
        || task_lower.contains("percent")
        || task_lower.contains("revenue")
        || task_lower.contains("x increase")
        || task_lower.contains("faster")
        || task_lower.contains("better");

    if has_proof_claim && !has_proof_words {
        risk_flags.push("proof_risk".to_string());
    }

    if has_generic_words {
        risk_flags.push("generic_copy_risk".to_string());
    }

    if task_lower.contains("hook")
        && (task_lower.contains("abstract") || task_lower.contains("vague"))
    {
        risk_flags.push("hook_too_abstract".to_string());
    }

    let cta_words = [
        "click",
        "download",
        "schedule",
        "start",
        "sign up",
        "get started",
    ];
    if !cta_words.iter().any(|w| task_lower.contains(w)) && task_lower.contains("copy") {
        risk_flags.push("cta_unclear".to_string());
    }

    if !context_lower.contains("voice") && !context_lower.contains("tone") {
        risk_flags.push("voice_unclear".to_string());
    }

    if !context_lower.contains("strategy")
        && !context_lower.contains("positioning")
        && (task_lower.contains("copy") || task_lower.contains("messaging"))
    {
        risk_flags.push("copy_before_strategy".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("strategy_unclear") => (
            "Strategy or positioning not clear in context".to_string(),
            "Request strategic frame before writing copy".to_string(),
            format!(
                "{} is demanding clear strategy before generating copy",
                pack.display_name
            ),
        ),
        Some("icp_language_missing") => (
            "ICP language not established in context".to_string(),
            "Request ICP details before writing copy".to_string(),
            format!(
                "{} is checking whether the ICP is clearly defined",
                pack.display_name
            ),
        ),
        Some("proof_risk") => (
            "Proof claim made without supporting evidence".to_string(),
            "Either provide evidence or remove proof claim".to_string(),
            format!(
                "{} is blocking copy with unsupported proof claims",
                pack.display_name
            ),
        ),
        Some("generic_copy_risk") => (
            "Risk of producing generic, competitor-agnostic copy".to_string(),
            "Anchor copy in specific ICP pain and proof".to_string(),
            format!(
                "{} is refusing to write generic copy that could apply to any competitor",
                pack.display_name
            ),
        ),
        Some("hook_too_abstract") => (
            "Hook is too abstract or vague".to_string(),
            "Make hook ICP-specific and concrete".to_string(),
            format!(
                "{} is challenging abstract hooks that lack ICP specificity",
                pack.display_name
            ),
        ),
        Some("cta_unclear") => (
            "CTA is missing or unclear".to_string(),
            "Add specific, actionable CTA".to_string(),
            format!(
                "{} is demanding a specific, actionable CTA",
                pack.display_name
            ),
        ),
        Some("voice_unclear") => (
            "Brand voice or tone not established".to_string(),
            "Define voice before writing copy".to_string(),
            format!(
                "{} is checking whether brand voice is clear",
                pack.display_name
            ),
        ),
        Some("copy_before_strategy") => (
            "Copy requested before strategy is clear".to_string(),
            "Establish strategic frame first".to_string(),
            format!(
                "{} is refusing to write copy before strategy is locked",
                pack.display_name
            ),
        ),
        _ => (
            format!("{} is forming copy instinct", pack.display_name),
            "Proceed with copy evaluation".to_string(),
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

pub fn copywriter_challenge_decision(
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

    let challengeable_types = ["position", "challenge", "refinement", "copy_audit"];

    if !challengeable_types.contains(&event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable by Copywriter".to_string(),
            suggested_event_type: "copy_challenge".to_string(),
            confidence: 0.0,
        };
    }

    let mut should_challenge = false;
    let mut reason = String::new();
    let mut confidence = 0.5;

    let generic_copy = (event_text.contains("ai saves time")
        || event_text.contains("automation")
        || event_text.contains("all-in-one")
        || event_text.contains("best-in-class")
        || event_text.contains("supercharge")
        || event_text.contains("transform"))
        && !event_text.contains("specifically")
        && !event_text.contains("unlike");

    let proof_claim = (event_text.contains("%")
        || event_text.contains("percent")
        || event_text.contains("revenue")
        || event_text.contains("x increase")
        || event_text.contains("faster")
        || event_text.contains("better")
        || event_text.contains("proven")
        || event_text.contains("studies show"))
        && !event_text.contains("source")
        && !event_text.contains("verified");

    let no_icp = (event_text.contains("copy")
        || event_text.contains("messaging")
        || event_text.contains("headline")
        || event_text.contains("hook"))
        && !event_text.contains("icp")
        && !event_text.contains("customer")
        && !event_text.contains("buyer");

    let vague_cta = (event_text.contains("click")
        || event_text.contains("get started")
        || event_text.contains("sign up"))
        && !event_text.contains("click here to")
        && event_text.len() < 50;

    if generic_copy {
        should_challenge = true;
        reason = "Copywriter challenged: copy uses generic language that fits any competitor"
            .to_string();
        confidence = 0.85;
    } else if proof_claim {
        should_challenge = true;
        reason = "Copywriter challenged: proof claim without supporting evidence".to_string();
        confidence = 0.8;
    } else if no_icp {
        should_challenge = true;
        reason = "Copywriter challenged: copy without ICP language or context".to_string();
        confidence = 0.75;
    } else if vague_cta {
        should_challenge = true;
        reason = "Copywriter challenged: CTA is vague or lacks specificity".to_string();
        confidence = 0.7;
    }

    ChallengeDecision {
        should_challenge,
        reason,
        suggested_event_type: if should_challenge {
            "copy_challenge".to_string()
        } else {
            "copy_audit".to_string()
        },
        confidence,
    }
}

pub fn build_copywriter_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
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
        "No relevant copywriter memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!("Relevant copywriter memories: {}", top_memories.join("; "))
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: Hooks, landing copy, campaign language, short-form angles, narrative tension, offer expression, CTA clarity, objection-aware wording.

You must turn sharp strategy and verified proof into language that the ICP feels immediately.
You must separate known facts, assumptions, recommendations, and open questions.
You must not invent proof, metrics, customers, or competitor facts.
You must not write copy before strategy is clear.
You must challenge generic copy, unsupported claims, and vague CTAs.

{}
{}
{}

Copy discipline required:
- Known facts: what we know from verified context
- Assumptions: what we are inferring without proof
- Recommendations: what we suggest based on facts and assumptions
- Open questions: what must be answered before proceeding

{}
"#,
        pack.display_name, obsessions_str, taboos_str, principles_str, memory_summary
    )
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum GrowthOperatorMemoryClassification {
    ExecutionPattern,
    Scar,
    #[default]
    Instinct,
    Preference,
    Warning,
    FeedbackLoop,
    VelocityLearning,
    ChannelCoordination,
}

pub fn classify_growth_operator_memory(
    summary: &str,
    tags: &[String],
) -> GrowthOperatorMemoryClassification {
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
        || all_text.contains("low velocity")
        || all_text.contains("flopped")
        || all_text.contains("underperformed")
        || all_text.contains("slow execution")
    {
        return GrowthOperatorMemoryClassification::Scar;
    }

    if all_text.contains("feedback")
        || all_text.contains("adapt")
        || all_text.contains("learned")
        || all_text.contains("iteration")
    {
        return GrowthOperatorMemoryClassification::FeedbackLoop;
    }

    if all_text.contains("velocity")
        || all_text.contains("pace")
        || all_text.contains("rhythm")
        || all_text.contains("throughput")
    {
        return GrowthOperatorMemoryClassification::VelocityLearning;
    }

    if all_text.contains("channel")
        || all_text.contains("handoff")
        || all_text.contains("coordination")
    {
        return GrowthOperatorMemoryClassification::ChannelCoordination;
    }

    if all_text.contains("execution") || all_text.contains("move") || all_text.contains("cadence") {
        return GrowthOperatorMemoryClassification::ExecutionPattern;
    }

    if all_text.contains("avoid") || all_text.contains("do not") || all_text.contains("warning") {
        return GrowthOperatorMemoryClassification::Warning;
    }

    if all_text.contains("prefer") || all_text.contains("favorite") {
        return GrowthOperatorMemoryClassification::Preference;
    }

    GrowthOperatorMemoryClassification::Instinct
}

pub fn derive_growth_operator_instinct_frame(
    pack: &AvatarEmbodimentPack,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    let mut risk_flags = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_move_keywords = task_lower.contains("move")
        || task_lower.contains("campaign")
        || task_lower.contains("execute")
        || task_lower.contains("launch");

    if has_move_keywords {
        let has_owner = context_lower.contains("owner")
            || context_lower.contains("responsible")
            || context_lower.contains("assigned");
        let has_deadline = context_lower.contains("deadline")
            || context_lower.contains("date")
            || context_lower.contains("timeline");
        let has_success_signal = context_lower.contains("success")
            || context_lower.contains("metric")
            || context_lower.contains("signal");

        if !has_owner {
            risk_flags.push("move_without_owner".to_string());
        }
        if !has_deadline {
            risk_flags.push("move_without_deadline".to_string());
        }
        if !has_success_signal {
            risk_flags.push("move_without_success_signal".to_string());
        }
    }

    if !context_lower.contains("velocity")
        && !context_lower.contains("pace")
        && !context_lower.contains("rhythm")
        && (task_lower.contains("execute") || task_lower.contains("campaign"))
    {
        risk_flags.push("no_velocity_tracking".to_string());
    }

    if !context_lower.contains("feedback")
        && !context_lower.contains("adapt")
        && (task_lower.contains("campaign") || task_lower.contains("execute"))
    {
        risk_flags.push("no_feedback_loop".to_string());
    }

    if (context_lower.contains("multi-channel") || context_lower.contains("cross-channel"))
        && !context_lower.contains("handoff")
        && !context_lower.contains("handover")
    {
        risk_flags.push("handoff_not_explicit".to_string());
    }

    if !context_lower.contains("sequence")
        && !context_lower.contains("order")
        && !context_lower.contains("rhythm")
        && has_move_keywords
    {
        risk_flags.push("move_sequencing_unclear".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("move_without_owner") => (
            "Move or campaign has no clear owner".to_string(),
            "Assign a clear owner before executing move".to_string(),
            format!(
                "{} is demanding move ownership before execution",
                pack.display_name
            ),
        ),
        Some("move_without_deadline") => (
            "Move or campaign has no deadline".to_string(),
            "Define deadline before executing move".to_string(),
            format!(
                "{} is demanding deadline before execution",
                pack.display_name
            ),
        ),
        Some("move_without_success_signal") => (
            "Move or campaign has no success signal defined".to_string(),
            "Define success metric before executing move".to_string(),
            format!(
                "{} is demanding success signal before execution",
                pack.display_name
            ),
        ),
        Some("no_velocity_tracking") => (
            "No velocity or cadence tracking defined".to_string(),
            "Define velocity tracking before executing".to_string(),
            format!(
                "{} is demanding velocity tracking before execution",
                pack.display_name
            ),
        ),
        Some("no_feedback_loop") => (
            "No feedback loop or adaptation trigger defined".to_string(),
            "Define feedback mechanism before executing".to_string(),
            format!(
                "{} is demanding feedback loop before execution",
                pack.display_name
            ),
        ),
        Some("handoff_not_explicit") => (
            "Multi-channel campaign without explicit handoff definition".to_string(),
            "Define explicit handoffs between channels".to_string(),
            format!(
                "{} is demanding explicit channel handoffs",
                pack.display_name
            ),
        ),
        Some("move_sequencing_unclear") => (
            "Move sequencing or order not justified".to_string(),
            "Define sequencing rationale before executing".to_string(),
            format!(
                "{} is demanding move sequencing before execution",
                pack.display_name
            ),
        ),
        _ => (
            format!("{} is forming execution instinct", pack.display_name),
            "Proceed with execution evaluation".to_string(),
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

pub fn growth_operator_challenge_decision(
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

    let challengeable_types = [
        "position",
        "challenge",
        "refinement",
        "execution_rhythm",
        "move_sequencing",
    ];

    if !challengeable_types.contains(&event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable by GrowthOperator".to_string(),
            suggested_event_type: "execution_rhythm".to_string(),
            confidence: 0.0,
        };
    }

    let mut should_challenge = false;
    let mut reason = String::new();
    let mut confidence = 0.5;

    let unsequenced_moves = (event_text.contains("move") || event_text.contains("campaign"))
        && !event_text.contains("sequence")
        && !event_text.contains("order");

    let no_feedback = (event_text.contains("execute")
        || event_text.contains("launch")
        || event_text.contains("campaign"))
        && !event_text.contains("feedback")
        && !event_text.contains("adapt");

    let no_velocity = (event_text.contains("execute") || event_text.contains("campaign"))
        && !event_text.contains("velocity")
        && !event_text.contains("pace")
        && !event_text.contains("rhythm");

    let single_channel_only = event_text.contains("channel")
        && !event_text.contains("multi")
        && !event_text.contains("cross")
        && event_text.len() < 100;

    let no_ownership = (event_text.contains("move") || event_text.contains("campaign"))
        && !event_text.contains("owner")
        && !event_text.contains("responsible");

    if unsequenced_moves {
        should_challenge = true;
        reason =
            "GrowthOperator challenged: move or campaign without sequencing rationale".to_string();
        confidence = 0.85;
    } else if no_ownership {
        should_challenge = true;
        reason = "GrowthOperator challenged: move without clear ownership".to_string();
        confidence = 0.8;
    } else if no_feedback {
        should_challenge = true;
        reason = "GrowthOperator challenged: execution without feedback loop defined".to_string();
        confidence = 0.75;
    } else if no_velocity {
        should_challenge = true;
        reason = "GrowthOperator challenged: execution without velocity tracking".to_string();
        confidence = 0.7;
    } else if single_channel_only {
        should_challenge = true;
        reason =
            "GrowthOperator challenged: single-channel execution without coordination rationale"
                .to_string();
        confidence = 0.65;
    }

    ChallengeDecision {
        should_challenge,
        reason,
        suggested_event_type: if should_challenge {
            "execution_rhythm".to_string()
        } else {
            "move_sequencing".to_string()
        },
        confidence,
    }
}

pub fn build_growth_operator_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
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
        "No relevant growth operator memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!(
            "Relevant growth operator memories: {}",
            top_memories.join("; ")
        )
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: Campaign moves, channel coordination, execution cadence, distribution timing, feedback loops, velocity tracking, adaptation logic.

You must turn language into execution rhythm — coordinating channel cadence, move sequencing, and feedback-driven adaptation.
You must separate known facts, assumptions, recommendations, and open questions.
You must not execute moves without clear ownership, deadline, and success signal.
You must not ignore feedback that contradicts the execution thesis.
You must challenge unsequenced moves and missing feedback loops.

{}
{}
{}

Execution discipline required:
- Known facts: what we know from context
- Assumptions: what we are inferring without measurement
- Recommendations: what we suggest based on facts and assumptions
- Open questions: what must be answered before executing

{}
"#,
        pack.display_name, obsessions_str, taboos_str, principles_str, memory_summary
    )
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum AnalystMemoryClassification {
    #[default]
    Instinct,
    Scar,
    Preference,
    Warning,
    Proof,
    MarketLearning,
    CustomerLearning,
    StyleRule,
}

pub fn classify_analyst_memory(summary: &str, tags: &[String]) -> AnalystMemoryClassification {
    let summary_lower = summary.to_lowercase();
    let all_text = format!(
        "{} {}",
        summary_lower,
        tags.iter()
            .map(|t| t.to_lowercase())
            .collect::<Vec<_>>()
            .join(" ")
    );

    if all_text.contains("false positive")
        || all_text.contains("misleading")
        || all_text.contains("bad attribution")
        || all_text.contains("scaled too early")
    {
        return AnalystMemoryClassification::Scar;
    }

    if all_text.contains("verified")
        || all_text.contains("reliable metric")
        || all_text.contains("source")
        || all_text.contains("dashboard")
        || all_text.contains("analytics")
    {
        return AnalystMemoryClassification::Proof;
    }

    if all_text.contains("vanity")
        || all_text.contains("sample size")
        || all_text.contains("baseline")
        || all_text.contains("attribution")
        || all_text.contains("noise")
    {
        return AnalystMemoryClassification::Warning;
    }

    if all_text.contains("channel")
        || all_text.contains("cadence")
        || all_text.contains("distribution")
        || all_text.contains("market")
    {
        return AnalystMemoryClassification::MarketLearning;
    }

    if all_text.contains("audience")
        || all_text.contains("segment")
        || all_text.contains("icp")
        || all_text.contains("customer behavior")
    {
        return AnalystMemoryClassification::CustomerLearning;
    }

    if all_text.contains("reporting format")
        || all_text.contains("readout")
        || all_text.contains("scorecard")
    {
        return AnalystMemoryClassification::StyleRule;
    }

    AnalystMemoryClassification::Instinct
}

pub fn derive_analyst_instinct_frame(
    pack: &AvatarEmbodimentPack,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    let mut risk_flags = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_metric = context_lower.contains("metric")
        || context_lower.contains("kpi")
        || context_lower.contains("impression")
        || context_lower.contains("conversion")
        || context_lower.contains("revenue")
        || context_lower.contains("ctr")
        || context_lower.contains("clicks")
        || context_lower.contains("leads");

    let has_baseline = context_lower.contains("baseline")
        || context_lower.contains("previous")
        || context_lower.contains("compared")
        || context_lower.contains("vs ");

    let has_sample = context_lower.contains("sample")
        || context_lower.contains("n =")
        || context_lower.contains("respondents")
        || context_lower.contains("cohort");

    let has_success_criterion = context_lower.contains("success criterion")
        || context_lower.contains("success metric")
        || context_lower.contains("target")
        || context_lower.contains("threshold");

    let causal_language = context_lower.contains("caused")
        || context_lower.contains("because")
        || context_lower.contains("proved")
        || context_lower.contains("resulted in")
        || context_lower.contains("led to");

    let has_vanity = context_lower.contains("impressions")
        || context_lower.contains("views")
        || context_lower.contains("likes")
        || context_lower.contains("followers")
        || context_lower.contains("shares");

    let has_outcome = context_lower.contains("conversion")
        || context_lower.contains("revenue")
        || context_lower.contains("qualified lead")
        || context_lower.contains("pipeline")
        || context_lower.contains("retention");

    if !has_metric
        && (task_lower.contains("did this work")
            || task_lower.contains("performance")
            || task_lower.contains("results"))
    {
        risk_flags.push("metric_missing".to_string());
    }

    if !has_baseline && has_metric && !task_lower.contains("baseline") {
        risk_flags.push("baseline_missing".to_string());
    }

    if causal_language && !context_lower.contains("experiment") && !context_lower.contains("a/b") {
        risk_flags.push("causality_overclaimed".to_string());
    }

    if has_vanity && !has_outcome && !task_lower.contains("awareness") {
        risk_flags.push("vanity_metric_risk".to_string());
    }

    if !has_sample && has_metric {
        risk_flags.push("sample_size_weak".to_string());
    }

    if !has_success_criterion && (task_lower.contains("test") || task_lower.contains("experiment"))
    {
        risk_flags.push("success_criterion_missing".to_string());
    }

    if has_metric && !has_baseline && !has_sample {
        risk_flags.push("attribution_uncertain".to_string());
    }

    if risk_flags.is_empty() && has_metric {
        risk_flags.push("kpi_unclear".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("metric_missing") => (
            "No metrics or success signals detected".to_string(),
            "Define what will be measured before evaluating".to_string(),
            format!(
                "{} is demanding metric definition before evaluation",
                pack.display_name
            ),
        ),
        Some("baseline_missing") => (
            "No baseline or comparison available".to_string(),
            "Establish baseline before comparing results".to_string(),
            format!("{} is demanding baseline comparison", pack.display_name),
        ),
        Some("causality_overclaimed") => (
            "Causal claim without experiment or control".to_string(),
            "Require controlled experiment before causal conclusions".to_string(),
            format!("{} is challenging causal overclaim", pack.display_name),
        ),
        Some("vanity_metric_risk") => (
            "Vanity metrics without outcome metrics".to_string(),
            "Add outcome metrics (conversion, revenue) alongside vanity".to_string(),
            format!("{} is flagging vanity metric risk", pack.display_name),
        ),
        Some("sample_size_weak") => (
            "Sample size or data count not established".to_string(),
            "Define sample size before drawing conclusions".to_string(),
            format!("{} is demanding sample size context", pack.display_name),
        ),
        Some("success_criterion_missing") => (
            "No success criterion defined for test".to_string(),
            "Define success criterion before running test".to_string(),
            format!("{} is demanding success criterion", pack.display_name),
        ),
        Some("attribution_uncertain") => (
            "Attribution unclear without baseline or sample".to_string(),
            "Require attribution clarity before conclusions".to_string(),
            format!("{} is demanding attribution clarity", pack.display_name),
        ),
        Some("kpi_unclear") => (
            "KPI or metric definition unclear".to_string(),
            "Clarify what metric maps to what decision".to_string(),
            format!(
                "{} is forming metric evaluation instinct",
                pack.display_name
            ),
        ),
        _ => (
            format!("{} is forming signal quality instinct", pack.display_name),
            "Evaluate signal quality and metric relevance".to_string(),
            format!(
                "{} is checking whether the result is real signal, weak signal, or noise",
                pack.display_name
            ),
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

pub fn analyst_challenge_decision(
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

    let challengeable_types = [
        "position",
        "challenge",
        "refinement",
        "copy_audit",
        "execution_rhythm",
        "evidence_check",
    ];

    if !challengeable_types.contains(&event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable by Analyst".to_string(),
            suggested_event_type: "signal_review".to_string(),
            confidence: 0.0,
        };
    }

    let mut should_challenge = false;
    let mut reason = String::new();
    let mut confidence = 0.5;

    let success_without_criterion = (event_text.contains("successful")
        || event_text.contains("worked")
        || event_text.contains("failed"))
        && !event_text.contains("criterion")
        && !event_text.contains("threshold")
        && !event_text.contains("target");

    let scale_from_weak_signal = (event_text.contains("scale")
        || event_text.contains("expand")
        || event_text.contains("double"))
        && (event_text.contains("impression")
            || event_text.contains("views")
            || event_text.contains("likes"))
        && !event_text.contains("conversion")
        && !event_text.contains("revenue");

    let vanity_only = (event_text.contains("impressions")
        || event_text.contains("views")
        || event_text.contains("likes"))
        && !event_text.contains("conversion")
        && !event_text.contains("outcome")
        && event_text.len() < 150;

    let no_baseline = (event_text.contains("growth")
        || event_text.contains("increase")
        || event_text.contains("decrease"))
        && !event_text.contains("baseline")
        && !event_text.contains("previous")
        && !event_text.contains("vs ");

    let causal_without_experiment = (event_text.contains("caused")
        || event_text.contains("because")
        || event_text.contains("proved"))
        && !event_text.contains("experiment")
        && !event_text.contains("a/b")
        && !event_text.contains("control");

    if success_without_criterion {
        should_challenge = true;
        reason = "Analyst challenged: success declared without success criterion".to_string();
        confidence = 0.9;
    } else if causal_without_experiment {
        should_challenge = true;
        reason = "Analyst challenged: causal claim without controlled experiment".to_string();
        confidence = 0.85;
    } else if scale_from_weak_signal {
        should_challenge = true;
        reason = "Analyst challenged: scaling recommended from weak/noisy signal".to_string();
        confidence = 0.8;
    } else if vanity_only {
        should_challenge = true;
        reason = "Analyst challenged: evaluation based on vanity metrics only".to_string();
        confidence = 0.75;
    } else if no_baseline {
        should_challenge = true;
        reason = "Analyst challenged: conclusion drawn without baseline comparison".to_string();
        confidence = 0.7;
    }

    ChallengeDecision {
        should_challenge,
        reason,
        suggested_event_type: if should_challenge {
            "signal_review".to_string()
        } else {
            "metric_readout".to_string()
        },
        confidence,
    }
}

pub fn build_analyst_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
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
        "No relevant analyst memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!("Relevant analyst memories: {}", top_memories.join("; "))
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: Metrics, KPI validation, funnel diagnosis, experiment readouts, signal quality, causality caution, performance interpretation, learning extraction.

You must separate signal from noise and turn campaign outcomes into honest learning.
You must separate known facts, assumptions, and open questions.
You must not invent metrics or analytics data.
You must not claim causality without evidence.
You must flag vanity metrics and attribution uncertainty.
You must challenge causal overclaims and weak signal scaling.

{}
{}
{}

Signal quality discipline required:
- Known facts: what we know from data
- Assumptions: what we are inferring without strong signal
- Recommendations: keep, kill, iterate, or investigate
- Open questions: what must be answered before conclusions

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

    #[test]
    fn test_classify_researcher_memory_proof() {
        assert_eq!(
            classify_researcher_memory("Verified case study shows results", &[]),
            ResearcherMemoryClassification::Proof
        );
        assert_eq!(
            classify_researcher_memory("Source citation needed", &["evidence".to_string()]),
            ResearcherMemoryClassification::Proof
        );
    }

    #[test]
    fn test_classify_researcher_memory_warning() {
        assert_eq!(
            classify_researcher_memory("Unverified claim found", &[]),
            ResearcherMemoryClassification::Warning
        );
        assert_eq!(
            classify_researcher_memory("This looks hallucinated", &["fake".to_string()]),
            ResearcherMemoryClassification::Warning
        );
    }

    #[test]
    fn test_classify_researcher_memory_scar() {
        assert_eq!(
            classify_researcher_memory("Wrong competitor assumption", &[]),
            ResearcherMemoryClassification::Scar
        );
        assert_eq!(
            classify_researcher_memory("Failed proof claim", &["false assumption".to_string()]),
            ResearcherMemoryClassification::Scar
        );
    }

    #[test]
    fn test_classify_researcher_memory_market_learning() {
        assert_eq!(
            classify_researcher_memory("Competitor pricing analysis", &[]),
            ResearcherMemoryClassification::MarketLearning
        );
        assert_eq!(
            classify_researcher_memory("Category positioning", &["market".to_string()]),
            ResearcherMemoryClassification::MarketLearning
        );
    }

    #[test]
    fn test_classify_researcher_memory_customer_learning() {
        assert_eq!(
            classify_researcher_memory("Customer pain point analysis", &[]),
            ResearcherMemoryClassification::CustomerLearning
        );
        assert_eq!(
            classify_researcher_memory("Buyer objection", &["ICP".to_string()]),
            ResearcherMemoryClassification::CustomerLearning
        );
    }

    #[test]
    fn test_classify_claim_evidence_unsupported() {
        assert_eq!(
            classify_claim_evidence("40% increase in revenue", ""),
            EvidenceLevel::Unsupported
        );
        assert_eq!(
            classify_claim_evidence("10x faster", "Some context"),
            EvidenceLevel::Unsupported
        );
    }

    #[test]
    fn test_classify_claim_evidence_source_backed() {
        assert_eq!(
            classify_claim_evidence("40% increase", "According to verified case study"),
            EvidenceLevel::SourceBacked
        );
        assert_eq!(
            classify_claim_evidence("data shows improvement", "Source: internal data"),
            EvidenceLevel::SourceBacked
        );
    }

    #[test]
    fn test_classify_claim_evidence_contradicted() {
        assert_eq!(
            classify_claim_evidence("40% revenue boost", "This contradicts earlier findings"),
            EvidenceLevel::Contradicted
        );
    }

    #[test]
    fn test_classify_claim_evidence_uncertain() {
        assert_eq!(
            classify_claim_evidence("may increase by 30%", ""),
            EvidenceLevel::PlausibleButUnverified
        );
        assert_eq!(
            classify_claim_evidence("could be faster", ""),
            EvidenceLevel::PlausibleButUnverified
        );
    }

    #[test]
    fn test_claim_safety_action() {
        assert_eq!(
            claim_safety_action(EvidenceLevel::Verified),
            ClaimSafetyAction::Keep
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::SourceBacked),
            ClaimSafetyAction::Keep
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::PlausibleButUnverified),
            ClaimSafetyAction::Qualify
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::Assumption),
            ClaimSafetyAction::DowngradeToAssumption
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::Unsupported),
            ClaimSafetyAction::NeedsSource
        );
        assert_eq!(
            claim_safety_action(EvidenceLevel::Contradicted),
            ClaimSafetyAction::ContradictionReview
        );
    }

    #[test]
    fn test_derive_researcher_instinct_frame_source_missing() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec!["source quality".to_string()],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "studies show this works",
            "Some context without source",
        );

        assert!(frame.risk_flags.contains(&"source_missing".to_string()));
    }

    #[test]
    fn test_derive_researcher_instinct_frame_unsupported_metric() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "40% revenue increase claimed",
            "No evidence provided",
        );

        assert!(frame.risk_flags.contains(&"unsupported_metric".to_string()));
    }

    #[test]
    fn test_derive_researcher_instinct_frame_competitor_unverified() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "Analyze competitor positioning",
            "Limited context",
        );

        assert!(
            frame
                .risk_flags
                .contains(&"competitor_claim_unverified".to_string())
        );
    }

    #[test]
    fn test_derive_researcher_instinct_frame_overconfident() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let frame = derive_researcher_instinct_frame(
            &pack,
            "Guaranteed to be the #1 solution",
            "Some context",
        );

        assert!(
            frame
                .risk_flags
                .contains(&"overconfident_language".to_string())
        );
    }

    #[test]
    fn test_researcher_challenge_decision_fake_metric() {
        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "40% revenue increase expected"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let decision = researcher_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("metric claim without supporting source")
        );
    }

    #[test]
    fn test_researcher_challenge_decision_fake_customer_quote() {
        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("copywriter".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Customers say this is great"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let decision = researcher_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("customer quote without actual attribution")
        );
    }

    #[test]
    fn test_researcher_challenge_decision_unsupported_competitor() {
        let target = AvatarDebateEvent {
            debate_event_id: "event1".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: "run1".to_string(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("support".to_string()),
            content: serde_json::json!({"text": "Competitor does X better"}),
            confidence: 0.6,
            created_at: chrono::Utc::now(),
        };

        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let decision = researcher_challenge_decision(&pack, &target);

        assert!(decision.should_challenge);
        assert!(
            decision
                .reason
                .contains("competitor claim without data or source")
        );
    }

    #[test]
    fn test_build_researcher_role_lock_prompt() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "Researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![
                "source quality".to_string(),
                "evidence hierarchy".to_string(),
            ],
            reflexes: vec![],
            taboos: vec![
                "do not invent sources".to_string(),
                "do not invent metrics".to_string(),
            ],
            operating_principles: vec!["Evidence beats confidence.".to_string()],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };

        let prompt = build_researcher_role_lock_prompt(&pack);

        assert!(prompt.contains("Researcher"));
        assert!(prompt.contains("Evidence discipline"));
        assert!(prompt.contains("source quality"));
        assert!(prompt.contains("do not invent sources"));
        assert!(prompt.contains("do not invent metrics"));
        assert!(prompt.contains("Evidence beats confidence"));
        assert!(prompt.contains("Known facts"));
        assert!(prompt.contains("Assumptions"));
        assert!(prompt.contains("Unsupported claims"));
        assert!(prompt.contains("find what is true"));
        assert!(prompt.contains("expose what is unsupported"));
        assert!(!prompt.contains("I am human"));
        assert!(!prompt.contains("sentient"));
    }
}
