use super::*;
pub(crate) fn derive_instinct_for_avatar(
    avatar_key: &str,
    pack: &AvatarEmbodimentPack,
    task_summary: &str,
    context_summary: &str,
) -> DerivedInstinctFrame {
    match avatar_key {
        "strategist" => derive_strategist_instinct_frame(pack, task_summary, context_summary),
        "researcher" => derive_researcher_instinct_frame(pack, task_summary, context_summary),
        "copywriter" => derive_copywriter_instinct_frame(pack, task_summary, context_summary),
        "growth_operator" => {
            derive_growth_operator_instinct_frame(pack, task_summary, context_summary)
        }
        "analyst" => derive_analyst_instinct_frame(pack, task_summary, context_summary),
        "creative_director" => {
            derive_creative_director_instinct_frame(pack, task_summary, context_summary)
        }
        "proof_collector" => {
            derive_proof_collector_instinct_frame(pack, task_summary, context_summary)
        }
        _ => DerivedInstinctFrame {
            instinct_frame_id: generate_id(),
            dominant_concern: format!("No specific instinct for avatar: {}", avatar_key),
            risk_flags: vec![],
            recommended_posture: "Review context and provide guidance".to_string(),
            visible_summary: format!("{} is assessing the situation", avatar_key),
        },
    }
}

pub(crate) fn create_position_content(
    avatar_key: &str,
    instinct: &DerivedInstinctFrame,
) -> serde_json::Value {
    let base = serde_json::json!({
        "dominant_concern": instinct.dominant_concern,
        "risk_flags": instinct.risk_flags,
        "recommended_posture": instinct.recommended_posture,
    });

    match avatar_key {
        "strategist" => serde_json::json!({
            "strategic_concern": instinct.dominant_concern,
            "likely_wedge": "TBD - requires competitive analysis",
            "needed_clarity": "Positioning clarity required before strategy can be finalized",
        }),
        "researcher" => serde_json::json!({
            "evidence_concern": if instinct.risk_flags.is_empty() { "Sufficient evidence available".to_string() } else { instinct.dominant_concern.clone() },
            "unsupported_claims": instinct.risk_flags.iter().filter(|f| f.contains("unsupported") || f.contains("missing")).cloned().collect::<Vec<_>>(),
            "needed_sources": "Primary sources and verified data needed for all claims".to_string(),
        }),
        "copywriter" => serde_json::json!({
            "language_concern": instinct.dominant_concern,
            "hook_risk": if instinct.risk_flags.contains(&"hook_missing".to_string()) { "No compelling hook identified".to_string() } else { "Hook appears reasonable".to_string() },
            "needed_voice_context": "Brand voice guidelines needed for tone calibration".to_string(),
        }),
        "growth_operator" => serde_json::json!({
            "execution_concern": instinct.dominant_concern,
            "cadence_risk": if instinct.risk_flags.contains(&"no_cadence".to_string()) { "No execution cadence defined".to_string() } else { "Cadence needs confirmation".to_string() },
            "needed_channel_clarity": "Channel mix and frequency must be specified".to_string(),
        }),
        "analyst" => serde_json::json!({
            "measurement_concern": instinct.dominant_concern,
            "missing_metrics": instinct.risk_flags.iter().filter(|f| f.contains("metric") || f.contains("signal")).cloned().collect::<Vec<_>>(),
            "signal_risk": if instinct.risk_flags.contains(&"weak_signal".to_string()) { "Signal strength too weak for confident decisions".to_string() } else { "Signal strength acceptable".to_string() },
        }),
        "creative_director" => serde_json::json!({
            "creative_concern": instinct.dominant_concern,
            "concept_gap": if instinct.risk_flags.contains(&"generic_creative_risk".to_string()) { "Creative concept needs differentiation".to_string() } else { "Creative concept acceptable".to_string() },
            "genericity_risk": if instinct.risk_flags.contains(&"generic_creative_risk".to_string()) { "High risk of generic/non-differentiated creative".to_string() } else { "Low genericity risk".to_string() },
        }),
        "proof_collector" => serde_json::json!({
            "proof_concern": instinct.dominant_concern,
            "proof_gaps": instinct.risk_flags.iter().filter(|f| f.contains("missing") || f.contains("incomplete")).cloned().collect::<Vec<_>>(),
            "unsafe_claims": instinct.risk_flags.iter().filter(|f| f.contains("risk") || f.contains("overstated")).cloned().collect::<Vec<_>>(),
        }),
        _ => base,
    }
}

pub(crate) fn get_challenge_function(
    avatar_key: &str,
) -> fn(&AvatarEmbodimentPack, &AvatarDebateEvent) -> ChallengeDecision {
    match avatar_key {
        "strategist" => strategist_challenge_decision,
        "researcher" => researcher_challenge_decision,
        "copywriter" => copywriter_challenge_decision,
        "growth_operator" => growth_operator_challenge_decision,
        "analyst" => analyst_challenge_decision,
        "creative_director" => creative_director_challenge_decision,
        "proof_collector" => proof_collector_challenge_decision,
        _ => |_, _| ChallengeDecision {
            should_challenge: false,
            reason: "Unknown avatar".to_string(),
            suggested_event_type: "none".to_string(),
            confidence: 0.0,
        },
    }
}

pub(crate) fn compute_challenge_routing(avatar_key: &str) -> Vec<&'static str> {
    match avatar_key {
        "researcher" => vec![
            "strategist",
            "copywriter",
            "creative_director",
            "growth_operator",
        ],
        "proof_collector" => vec![
            "strategist",
            "copywriter",
            "creative_director",
            "growth_operator",
            "researcher",
        ],
        "analyst" => vec!["strategist", "growth_operator", "copywriter"],
        "strategist" => vec!["researcher", "copywriter"],
        "copywriter" => vec!["strategist", "creative_director"],
        "growth_operator" => vec!["strategist", "copywriter"],
        "creative_director" => vec!["strategist", "copywriter"],
        _ => vec![],
    }
}
