use super::*;
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum CreativeDirectorMemoryClassification {
    #[default]
    Instinct,
    Scar,
    Preference,
    Warning,
    Proof,
    AestheticLearning,
    BrandVoice,
    StyleRule,
}

pub fn classify_creative_director_memory(
    summary: &str,
    tags: &[String],
) -> CreativeDirectorMemoryClassification {
    let summary_lower = summary.to_lowercase();
    let all_text = format!(
        "{} {}",
        summary_lower,
        tags.iter()
            .map(|t| t.to_lowercase())
            .collect::<Vec<_>>()
            .join(" ")
    );

    if all_text.contains("generic")
        || all_text.contains("off-brand")
        || all_text.contains("quality drop")
        || all_text.contains("erosion")
    {
        return CreativeDirectorMemoryClassification::Scar;
    }

    if all_text.contains("brand voice")
        || all_text.contains("tone")
        || all_text.contains("style guide")
    {
        return CreativeDirectorMemoryClassification::BrandVoice;
    }

    if all_text.contains("aesthetic")
        || all_text.contains("visual")
        || all_text.contains("design")
        || all_text.contains("differentiation")
    {
        return CreativeDirectorMemoryClassification::AestheticLearning;
    }

    if all_text.contains("approved")
        || all_text.contains("quality standard")
        || all_text.contains("benchmark")
    {
        return CreativeDirectorMemoryClassification::Proof;
    }

    if all_text.contains("avoid") || all_text.contains("warning") || all_text.contains("do not use")
    {
        return CreativeDirectorMemoryClassification::Warning;
    }

    if all_text.contains("prefer")
        || all_text.contains("favorite")
        || all_text.contains("best practice")
    {
        return CreativeDirectorMemoryClassification::Preference;
    }

    if all_text.contains("format")
        || all_text.contains("template")
        || all_text.contains("structure")
    {
        return CreativeDirectorMemoryClassification::StyleRule;
    }

    CreativeDirectorMemoryClassification::Instinct
}

pub fn derive_creative_director_instinct_frame(
    pack: &AvatarEmbodimentPack,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    let mut risk_flags = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_quality = context_lower.contains("creative")
        || context_lower.contains("design")
        || context_lower.contains("visual")
        || context_lower.contains("copy")
        || context_lower.contains("content");

    let generic_concern = context_lower.contains("generic")
        || context_lower.contains("derivative")
        || context_lower.contains("template")
        || context_lower.contains("stock");

    let brand_concern = context_lower.contains("off-brand")
        || context_lower.contains("inconsistent")
        || context_lower.contains("wrong tone")
        || context_lower.contains("mismatched");

    let emotional_concern = context_lower.contains("flat")
        || context_lower.contains("bland")
        || context_lower.contains("no hook")
        || context_lower.contains("cold");

    let hierarchy_concern = context_lower.contains("confusing")
        || context_lower.contains("cluttered")
        || context_lower.contains("unclear")
        || context_lower.contains("messy");

    let cta_concern = (task_lower.contains("conversion")
        || task_lower.contains("cta")
        || task_lower.contains("action"))
        && !context_lower.contains("call to action")
        && !context_lower.contains("cta");

    let differentiation_concern = context_lower.contains("competitive")
        && !context_lower.contains("different")
        && !context_lower.contains("unique")
        && !context_lower.contains("stands out");

    if generic_concern && has_quality {
        risk_flags.push("generic_creative_risk".to_string());
    }

    if brand_concern && has_quality {
        risk_flags.push("brand_consistency_risk".to_string());
    }

    if emotional_concern && has_quality {
        risk_flags.push("emotional_resonance_risk".to_string());
    }

    if hierarchy_concern && has_quality {
        risk_flags.push("message_clarity_risk".to_string());
    }

    if cta_concern {
        risk_flags.push("cta_missing_or_unclear".to_string());
    }

    if differentiation_concern {
        risk_flags.push("differentiation_risk".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("generic_creative_risk") => (
            "Generic or derivative creative detected".to_string(),
            "Elevate creative to differentiate from template work".to_string(),
            format!(
                "{} is demanding creative differentiation",
                pack.display_name
            ),
        ),
        Some("brand_consistency_risk") => (
            "Brand consistency issues detected".to_string(),
            "Align creative with brand voice and standards".to_string(),
            format!("{} is protecting brand integrity", pack.display_name),
        ),
        Some("emotional_resonance_risk") => (
            "Emotional resonance is weak or missing".to_string(),
            "Add emotional hook to connect with audience".to_string(),
            format!("{} is demanding emotional connection", pack.display_name),
        ),
        Some("message_clarity_risk") => (
            "Message hierarchy or clarity issues".to_string(),
            "Clarify message hierarchy and reduce confusion".to_string(),
            format!("{} is demanding message clarity", pack.display_name),
        ),
        Some("cta_missing_or_unclear") => (
            "CTA is missing or unclear".to_string(),
            "Define clear and compelling call to action".to_string(),
            format!("{} is demanding CTA clarity", pack.display_name),
        ),
        Some("differentiation_risk") => (
            "Differentiation from competitors unclear".to_string(),
            "Ensure creative stands out in competitive context".to_string(),
            format!("{} is demanding differentiation clarity", pack.display_name),
        ),
        _ => (
            format!("{} is forming creative instinct", pack.display_name),
            "Evaluate creative quality and brand alignment".to_string(),
            format!("{} is reviewing creative work", pack.display_name),
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

pub fn creative_director_challenge_decision(
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
        "signal_review",
        "execution_rhythm",
    ];

    if !challengeable_types.contains(&event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable by CreativeDirector".to_string(),
            suggested_event_type: "creative_review".to_string(),
            confidence: 0.0,
        };
    }

    let mut should_challenge = false;
    let mut reason = String::new();
    let mut confidence = 0.5;

    let generic_creative = event_text.contains("generic")
        || event_text.contains("template")
        || event_text.contains("stock")
        || event_text.contains("derivative");

    let brand_ego = event_text.contains("brand prefers")
        || event_text.contains("brand likes")
        || event_text.contains("internal preference")
        || event_text.contains("we want");

    let no_emotion = (event_text.contains("conversion") || event_text.contains("cta"))
        && !event_text.contains("emotional")
        && !event_text.contains("hook")
        && event_text.len() < 120;

    let quality_doubt = event_text.contains("good enough")
        || event_text.contains("close enough")
        || event_text.contains("ship it");

    let confusing = event_text.contains("confusing")
        || event_text.contains("unclear")
        || event_text.contains("messy");

    if generic_creative {
        should_challenge = true;
        reason = "CreativeDirector challenged: generic or derivative creative".to_string();
        confidence = 0.85;
    } else if brand_ego {
        should_challenge = true;
        reason = "CreativeDirector challenged: creative driven by brand ego over audience need"
            .to_string();
        confidence = 0.8;
    } else if quality_doubt {
        should_challenge = true;
        reason = "CreativeDirector challenged: 'good enough' mentality erodes creative standards"
            .to_string();
        confidence = 0.75;
    } else if no_emotion && event_text.contains("conversion") {
        should_challenge = true;
        reason = "CreativeDirector challenged: conversion-focused work without emotional hook"
            .to_string();
        confidence = 0.7;
    } else if confusing {
        should_challenge = true;
        reason = "CreativeDirector challenged: message hierarchy or clarity issue".to_string();
        confidence = 0.65;
    }

    ChallengeDecision {
        should_challenge,
        reason,
        suggested_event_type: if should_challenge {
            "creative_review".to_string()
        } else {
            "creative_direction".to_string()
        },
        confidence,
    }
}

pub fn build_creative_director_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
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
        "No relevant creative director memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!(
            "Relevant creative director memories: {}",
            top_memories.join("; ")
        )
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: Creative vision, aesthetic quality, brand consistency, emotional resonance, creative risk assessment, taste arbitration, creative direction.

You must raise creative standards and protect the brand's aesthetic integrity.
You must separate known facts, assumptions, and open questions.
You must not approve work that erodes brand quality.
You must not let internal brand preference override audience resonance.
You must challenge generic creative and brand ego-driven decisions.

{}
{}
{}

Creative quality discipline required:
- Known facts: what we know about the creative and brand
- Assumptions: what we are inferring about audience resonance
- Recommendations: keep, iterate, or investigate
- Open questions: what must be answered before creative approval

{}
"#,
        pack.display_name, obsessions_str, taboos_str, principles_str, memory_summary
    )
}
