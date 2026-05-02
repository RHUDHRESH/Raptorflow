use super::*;
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

    let metric_negated = context_lower.contains("no metric")
        || context_lower.contains("no metrics")
        || context_lower.contains("without metric")
        || context_lower.contains("without metrics")
        || context_lower.contains("missing metric");
    let has_metric = !metric_negated
        && (context_lower.contains("metric")
            || context_lower.contains("kpi")
            || context_lower.contains("impression")
            || context_lower.contains("conversion")
            || context_lower.contains("revenue")
            || context_lower.contains("ctr")
            || context_lower.contains("clicks")
            || context_lower.contains("leads"));

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
