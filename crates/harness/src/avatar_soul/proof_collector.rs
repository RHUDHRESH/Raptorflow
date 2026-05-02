use super::*;
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum ProofCollectorMemoryClassification {
    #[default]
    Instinct,
    Scar,
    Preference,
    Warning,
    Proof,
    TrustAsset,
    LegalFlag,
    ProofGap,
}

pub fn classify_proof_collector_memory(
    summary: &str,
    tags: &[String],
) -> ProofCollectorMemoryClassification {
    let summary_lower = summary.to_lowercase();
    let all_text = format!(
        "{} {}",
        summary_lower,
        tags.iter()
            .map(|t| t.to_lowercase())
            .collect::<Vec<_>>()
            .join(" ")
    );

    if all_text.contains("fake")
        || all_text.contains("invented")
        || all_text.contains("fabricated")
        || all_text.contains("unsubstantiated")
    {
        return ProofCollectorMemoryClassification::Scar;
    }

    if all_text.contains("verified")
        || all_text.contains("source")
        || all_text.contains("permission")
        || all_text.contains("consent")
        || all_text.contains("testimonial")
        || all_text.contains("case study")
    {
        return ProofCollectorMemoryClassification::Proof;
    }

    if all_text.contains("legal")
        || all_text.contains("ftc")
        || all_text.contains("compliance")
        || all_text.contains("lawsuit")
        || all_text.contains("risk")
    {
        return ProofCollectorMemoryClassification::LegalFlag;
    }

    if all_text.contains("trust asset")
        || all_text.contains("proof pack")
        || all_text.contains("evidence package")
    {
        return ProofCollectorMemoryClassification::TrustAsset;
    }

    if all_text.contains("missing")
        || all_text.contains("gap")
        || all_text.contains("unsupported")
        || all_text.contains("unverified")
    {
        return ProofCollectorMemoryClassification::ProofGap;
    }

    if all_text.contains("warning") || all_text.contains("caution") || all_text.contains("flag") {
        return ProofCollectorMemoryClassification::Warning;
    }

    ProofCollectorMemoryClassification::Instinct
}

pub fn derive_proof_collector_instinct_frame(
    pack: &AvatarEmbodimentPack,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    let mut risk_flags = Vec::new();

    let _task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let proof_missing = context_lower.contains("claim")
        && !context_lower.contains("proof")
        && !context_lower.contains("evidence")
        && !context_lower.contains("source");

    let source_missing = (context_lower.contains("metric")
        || context_lower.contains("data")
        || context_lower.contains("result"))
        && !context_lower.contains("source")
        && !context_lower.contains("dashboard")
        && !context_lower.contains("analytics");

    let permission_missing = (context_lower.contains("testimonial")
        || context_lower.contains("quote")
        || context_lower.contains("customer said"))
        && !context_lower.contains("permission")
        && !context_lower.contains("consent")
        && !context_lower.contains("approved");

    let metric_context_missing = (context_lower.contains("%")
        || context_lower.contains("revenue")
        || context_lower.contains("roi")
        || context_lower.contains("conversion"))
        && !context_lower.contains("baseline")
        && !context_lower.contains("window")
        && !context_lower.contains("cohort");

    let typicality_risk = context_lower.contains("typical")
        || context_lower.contains("proven")
        || context_lower.contains("always")
        || context_lower.contains("best")
        || context_lower.contains("guaranteed")
        || context_lower.contains("massive")
        || context_lower.contains("10x");

    let testimonial_risk = context_lower.contains("testimonial")
        && (context_lower.contains("invented")
            || context_lower.contains("fake")
            || context_lower.contains("clean up"));

    let case_study_incomplete = context_lower.contains("case study")
        && (!context_lower.contains("before")
            || !context_lower.contains("after")
            || !context_lower.contains("result"));

    let claim_overstated = (context_lower.contains("10x")
        || context_lower.contains("20x")
        || context_lower.contains("massive")
        || context_lower.contains("guaranteed"))
        && !context_lower.contains("based on")
        && !context_lower.contains("study");

    let visual_proof_misleading = (context_lower.contains("screenshot")
        || context_lower.contains("dashboard"))
        && !context_lower.contains("source")
        && !context_lower.contains("date")
        && !context_lower.contains("permission");

    let legal_review_needed = context_lower.contains("ftc")
        || context_lower.contains("before/after")
        || context_lower.contains("testimonial")
        || context_lower.contains("earnings claim");

    if proof_missing {
        risk_flags.push("proof_missing".to_string());
    }

    if source_missing {
        risk_flags.push("source_missing".to_string());
    }

    if permission_missing {
        risk_flags.push("permission_missing".to_string());
    }

    if metric_context_missing {
        risk_flags.push("metric_context_missing".to_string());
    }

    if typicality_risk {
        risk_flags.push("typicality_risk".to_string());
    }

    if testimonial_risk {
        risk_flags.push("testimonial_risk".to_string());
    }

    if case_study_incomplete {
        risk_flags.push("case_study_incomplete".to_string());
    }

    if claim_overstated {
        risk_flags.push("claim_overstated".to_string());
    }

    if visual_proof_misleading {
        risk_flags.push("visual_proof_misleading".to_string());
    }

    if legal_review_needed {
        risk_flags.push("legal_review_needed".to_string());
    }

    let (concern, posture, summary) = match risk_flags.first().map(|s| s.as_str()) {
        Some("proof_missing") => (
            "Strong claim made without supporting proof".to_string(),
            "Demand proof mapping for every strong claim".to_string(),
            format!("{} is demanding proof substantiation", pack.display_name),
        ),
        Some("source_missing") => (
            "Metric or data presented without source".to_string(),
            "Require source, date, and methodology for all metrics".to_string(),
            format!("{} is demanding metric provenance", pack.display_name),
        ),
        Some("permission_missing") => (
            "Customer quote or testimonial without permission".to_string(),
            "Obtain explicit permission before using customer words".to_string(),
            format!(
                "{} is protecting consent and permission standards",
                pack.display_name
            ),
        ),
        Some("metric_context_missing") => (
            "Metric lacks baseline, time window, or sample context".to_string(),
            "Add baseline, time window, and sample size to all metric claims".to_string(),
            format!("{} is demanding metric context", pack.display_name),
        ),
        Some("typicality_risk") => (
            "Typicality or superiority claim without statistical support".to_string(),
            "Downgrade to anecdotal or require statistical evidence".to_string(),
            format!(
                "{} is blocking unsupported typicality claims",
                pack.display_name
            ),
        ),
        Some("testimonial_risk") => (
            "Testimonial safety concern detected".to_string(),
            "Verify authenticity and obtain proper consent".to_string(),
            format!("{} is protecting testimonial integrity", pack.display_name),
        ),
        Some("case_study_incomplete") => (
            "Case study missing required structural elements".to_string(),
            "Complete case study with situation, action, result, and limits".to_string(),
            format!(
                "{} is demanding complete case study structure",
                pack.display_name
            ),
        ),
        Some("claim_overstated") => (
            "Exaggerated or legally risky claim detected".to_string(),
            "Significantly qualify or remove overstated language".to_string(),
            format!("{} is blocking exaggerated claims", pack.display_name),
        ),
        Some("visual_proof_misleading") => (
            "Visual proof (screenshot/dashboard) may be misleading".to_string(),
            "Add source, date, and permission to visual proof".to_string(),
            format!(
                "{} is demanding visual proof documentation",
                pack.display_name
            ),
        ),
        Some("legal_review_needed") => (
            "Content may require legal or FTC review".to_string(),
            "Flag for legal review before publishing".to_string(),
            format!("{} is escalating to legal review", pack.display_name),
        ),
        _ => (
            "General proof substantiation concern".to_string(),
            "Map claims to evidence and qualify unsupported statements".to_string(),
            format!("{} is reviewing proof quality", pack.display_name),
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

pub fn proof_collector_challenge_decision(
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
        "proof_review",
    ];

    if !challengeable_types.contains(&event_type.as_str()) {
        return ChallengeDecision {
            should_challenge: false,
            reason: "Event type not challengeable by Proof Collector".to_string(),
            suggested_event_type: "proof_review".to_string(),
            confidence: 0.0,
        };
    }

    let mut should_challenge = false;
    let mut reason = String::new();
    let mut confidence = 0.5;

    let invented_testimonial = (event_text.contains("testimonial")
        || event_text.contains("quote")
        || event_text.contains("customer said"))
        && (event_text.contains("invented")
            || event_text.contains("fake")
            || event_text.contains("made up")
            || event_text.contains("clean up"));

    let unverified_metric = (event_text.contains("revenue")
        || event_text.contains("roi")
        || event_text.contains("conversion")
        || event_text.contains("% increase")
        || event_text.contains("10x")
        || event_text.contains("20x"))
        && !event_text.contains("source")
        && !event_text.contains("dashboard")
        && !event_text.contains("data from");

    let typicality_unsupported = (event_text.contains("typical")
        || event_text.contains("average")
        || event_text.contains("proven")
        || event_text.contains("always"))
        && !event_text.contains("based on")
        && !event_text.contains("study")
        && !event_text.contains("data");

    let permission_missing = (event_text.contains("testimonial")
        || event_text.contains("quote")
        || event_text.contains("case study"))
        && !event_text.contains("permission")
        && !event_text.contains("consent")
        && event_text.len() < 200;

    let screenshot_without_source = event_text.contains("screenshot")
        || event_text.contains("dashboard")
        || event_text.contains("image");

    let exaggerated_claim = (event_text.contains("guaranteed")
        || event_text.contains("massive")
        || event_text.contains("transformed")
        || event_text.contains("#1")
        || event_text.contains("best ever"))
        && !event_text.contains("legal")
        && !event_text.contains("disclaimer");

    if invented_testimonial {
        should_challenge = true;
        reason =
            "Proof Collector challenged: invented or fabricated testimonial detected".to_string();
        confidence = 0.95;
    } else if exaggerated_claim {
        should_challenge = true;
        reason = "Proof Collector challenged: exaggerated claim requires strong substantiation"
            .to_string();
        confidence = 0.9;
    } else if unverified_metric {
        should_challenge = true;
        reason =
            "Proof Collector challenged: metric presented without source or context".to_string();
        confidence = 0.85;
    } else if typicality_unsupported {
        should_challenge = true;
        reason =
            "Proof Collector challenged: typicality claim without statistical support".to_string();
        confidence = 0.8;
    } else if permission_missing {
        should_challenge = true;
        reason =
            "Proof Collector challenged: testimonial or case study without permission".to_string();
        confidence = 0.75;
    } else if screenshot_without_source {
        should_challenge = true;
        reason =
            "Proof Collector challenged: visual proof without source/date/permission".to_string();
        confidence = 0.7;
    }

    ChallengeDecision {
        should_challenge,
        reason,
        suggested_event_type: if should_challenge {
            "proof_review".to_string()
        } else {
            "trust_asset_creation".to_string()
        },
        confidence,
    }
}

pub fn build_proof_collector_role_lock_prompt(pack: &AvatarEmbodimentPack) -> String {
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
        "No relevant proof collector memories loaded.".to_string()
    } else {
        let top_memories: Vec<String> = pack
            .memory_edges
            .iter()
            .take(5)
            .map(|e| format!("[{}] {}", e.relationship_type, e.use_when))
            .collect();
        format!(
            "Relevant proof collector memories: {}",
            top_memories.join("; ")
        )
    };

    format!(
        r#"You are operating as {}.
You are not a generic AI assistant.
Your role is: Proof mapping, substantiation, testimonial discipline, case-study structure, claim-to-evidence linking, trust asset creation, proof gap detection.

You must turn verified truth into trust assets and stop fake proof from entering the system.
You must separate known facts, assumptions, and open questions.
You must not invent proof, testimonials, metrics, or case studies.
You must demand source, date, time window, and context for all metrics.
You must obtain explicit permission before using customer quotes.
You must challenge unsupported typicality and superiority claims.

{}
{}
{}

Proof discipline required:
- Known facts: what proof we have verified
- Assumptions: what we are inferring without strong evidence
- Recommendations: use as-is, qualify, downgrade, or remove
- Open questions: what proof must be collected before publishing

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
