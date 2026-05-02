use super::*;
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

    if all_text.contains("unsupported")
        || all_text.contains("unverified")
        || all_text.contains("hallucinated")
        || all_text.contains("fake")
        || all_text.contains("invented")
    {
        return ResearcherMemoryClassification::Warning;
    }

    if all_text.contains("verified")
        || all_text.contains("source")
        || all_text.contains("evidence")
        || all_text.contains("citation")
        || all_text.contains("case study")
    {
        return ResearcherMemoryClassification::Proof;
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

    if has_source_words && (has_numbers || claim_lower.len() > 20) {
        return EvidenceLevel::SourceBacked;
    }

    if has_uncertain {
        return EvidenceLevel::PlausibleButUnverified;
    }

    if has_numbers && !has_source_words {
        return EvidenceLevel::Unsupported;
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

    let source_negated = context_lower.contains("without source")
        || context_lower.contains("without sources")
        || context_lower.contains("no source")
        || context_lower.contains("no sources")
        || context_lower.contains("missing source");
    let has_source = !source_negated
        && (context_lower.contains("source")
            || context_lower.contains("verified")
            || context_lower.contains("citation")
            || context_lower.contains("data")
            || context_lower.contains("study")
            || context_lower.contains("customer quote"));

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
