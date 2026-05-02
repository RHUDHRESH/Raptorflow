use super::*;
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
