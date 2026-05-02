use super::*;
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

    if all_text.contains("sequencing") || all_text.contains("timing matters") {
        return StrategistMemoryClassification::Instinct;
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
    let speaker_is_copywriter = target_event
        .speaker_avatar_id
        .as_deref()
        .unwrap_or_default()
        .to_lowercase()
        .contains("copywriter");

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

    let has_no_icp_copy = (speaker_is_copywriter
        && (event_text.contains("say ") || event_text.contains('\'') || event_text.contains('"')))
        || event_text.contains("copy")
        || event_text.contains("messaging")
        || event_text.contains("content")
        || event_text.contains("hook")
        || event_text.contains("headline")
        || event_text.contains("say ")
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
