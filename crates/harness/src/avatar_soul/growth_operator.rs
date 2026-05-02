use super::*;
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
