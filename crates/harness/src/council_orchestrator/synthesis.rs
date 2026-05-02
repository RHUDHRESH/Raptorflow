use super::*;
pub fn synthesize_council_result(
    task_summary: &str,
    context_summary: &str,
    debate_events: &[AvatarDebateEvent],
    avatar_roster: &[String],
) -> serde_json::Value {
    let mut known_facts: Vec<String> = Vec::new();
    let mut assumptions: Vec<String> = Vec::new();
    let mut challenges: Vec<String> = Vec::new();
    let mut risks: Vec<String> = Vec::new();
    let mut open_questions: Vec<String> = Vec::new();
    let mut next_actions: Vec<String> = Vec::new();
    let mut avatar_positions: Vec<serde_json::Value> = Vec::new();
    let mut proof_assets_needed: Vec<String> = Vec::new();
    let ripple_candidates: Vec<String> = Vec::new();

    if !task_summary.is_empty() {
        known_facts.push(format!("Task: {}", task_summary));
    }

    if !context_summary.is_empty() && context_summary.len() > 10 {
        known_facts.push("Context provided for council review".to_string());
    } else {
        assumptions.push("Context is thin; recommendations are provisional".to_string());
        open_questions.push("What is the specific business context?".to_string());
    }

    for event in debate_events {
        let _text = serde_json::to_string(&event.content).unwrap_or_default();
        let avatar_key = event.speaker_avatar_id.clone().unwrap_or_default();
        let entry = serde_json::json!({
            "avatar_key": avatar_key,
            "event_type": event.event_type,
            "stance": event.stance,
            "confidence": event.confidence,
        });
        avatar_positions.push(entry);

        if event.event_type == "challenge" {
            let stance = event.stance.clone().unwrap_or_default();
            challenges.push(format!("[{}] {}", avatar_key, stance));
        }

        if event.confidence < 0.5 {
            open_questions.push(format!(
                "Low confidence position from {} requires more data",
                avatar_key
            ));
        }
    }

    for avatar_key in avatar_roster {
        match avatar_key.as_str() {
            "proof_collector" => {
                proof_assets_needed
                    .push("Proof mapping: verify all claims against evidence".to_string());
                proof_assets_needed.push(
                    "Testimonial permission: confirm consent for any customer quotes".to_string(),
                );
                proof_assets_needed.push(
                    "Metric context: ensure baseline, time window, and source for all metrics"
                        .to_string(),
                );
            }
            "analyst" => {
                open_questions.push("What specific KPIs will measure success?".to_string());
                open_questions.push("What is the baseline for comparison?".to_string());
            }
            "researcher" => {
                open_questions.push("What primary sources support the key claims?".to_string());
                open_questions.push("Are there competitive intelligence gaps?".to_string());
            }
            "strategist" => {
                known_facts.push("Strategic direction assessed by council".to_string());
                next_actions
                    .push("Define clear positioning wedge based on council findings".to_string());
            }
            "copywriter" => {
                known_facts.push("Copy direction reviewed by council".to_string());
                next_actions
                    .push("Draft messaging aligned with council strategic direction".to_string());
            }
            "growth_operator" => {
                next_actions.push("Define channel cadence and execution timeline".to_string());
            }
            "creative_director" => {
                next_actions
                    .push("Develop creative concepts aligned with strategic direction".to_string());
            }
            _ => {}
        }
    }

    if !challenges.is_empty() {
        risks.push(format!(
            "{} challenges raised during council review",
            challenges.len()
        ));
    }
    if next_actions.is_empty() {
        open_questions.push("What is the immediate next action?".to_string());
    }

    serde_json::json!({
        "known_facts": known_facts,
        "assumptions": assumptions,
        "council_recommendation": {
            "strategy": if avatar_roster.contains(&"strategist".to_string()) {
                "Strategic direction determined by council assessment. Define competitive wedge and positioning based on known facts and risks.".to_string()
            } else {
                "No strategist in roster; strategic direction not assessed.".to_string()
            },
            "research_constraints": if avatar_roster.contains(&"researcher".to_string()) {
                vec!["Verify all claims against primary sources", "Document evidence quality and limitations"]
            } else {
                vec!["No researcher in roster; evidence not formally reviewed"]
            },
            "copy_direction": if avatar_roster.contains(&"copywriter".to_string()) {
                "Copy direction set by council; final copy requires human approval with council constraints.".to_string()
            } else {
                "No copywriter in roster; copy direction not assessed.".to_string()
            },
            "execution_plan": if avatar_roster.contains(&"growth_operator".to_string()) {
                "Execution cadence and channel mix defined by council.".to_string()
            } else {
                "No growth operator in roster; execution plan not assessed.".to_string()
            },
            "measurement_plan": if avatar_roster.contains(&"analyst".to_string()) {
                "Measurement framework defined by council; KPIs and baselines identified.".to_string()
            } else {
                "No analyst in roster; measurement plan not assessed.".to_string()
            },
            "creative_direction": if avatar_roster.contains(&"creative_director".to_string()) {
                "Creative direction set by council; differentiation and brand consistency verified.".to_string()
            } else {
                "No creative director in roster; creative direction not assessed.".to_string()
            },
            "proof_assets_needed": proof_assets_needed,
        },
        "avatar_positions": avatar_positions,
        "challenges": challenges,
        "risks": risks,
        "open_questions": open_questions,
        "next_actions": next_actions,
        "ripple_candidates": ripple_candidates,
    })
}

fn normalize_synthesis_to_schema(
    raw: &serde_json::Value,
    council_run_id: &str,
    avatar_roster: &[String],
    mode: &str,
) -> serde_json::Value {
    let known_facts = raw
        .get("known_facts")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();

    let assumptions = raw
        .get("assumptions")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();

    let raw_risks = raw
        .get("risks")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .map(|r| {
                    if r.is_object() {
                        r.clone()
                    } else {
                        serde_json::json!({
                            "risk": r.as_str().unwrap_or("Unspecified risk"),
                            "severity": "medium",
                            "mitigation": ""
                        })
                    }
                })
                .collect::<Vec<_>>()
        })
        .unwrap_or_default();

    let raw_next_actions = raw
        .get("next_actions")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .map(|a| {
                    if a.is_object() {
                        a.clone()
                    } else {
                        serde_json::json!({
                            "action": a.as_str().unwrap_or("Unspecified action"),
                            "owner": "council",
                            "priority": "medium"
                        })
                    }
                })
                .collect::<Vec<_>>()
        })
        .unwrap_or_default();

    let open_questions = raw
        .get("open_questions")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();

    let strategic_recommendation = raw
        .get("council_recommendation")
        .and_then(|r| r.get("strategy"))
        .and_then(|s| s.as_str())
        .map(|s| s.to_string())
        .unwrap_or_else(|| {
            format!(
                "Council assessed by {} avatar(s) in {} mode",
                avatar_roster.len(),
                mode
            )
        });

    let synthesized_by = "council".to_string();

    serde_json::json!({
        "council_run_id": council_run_id,
        "known_facts": known_facts,
        "assumptions": assumptions,
        "risks": raw_risks,
        "next_actions": raw_next_actions,
        "open_questions": open_questions,
        "strategic_recommendation": strategic_recommendation,
        "synthesized_by": synthesized_by,
    })
}

pub(crate) async fn persist_council_synthesis_artifact(
    pool: &PgPool,
    council_run_id: &str,
    org_id: uuid::Uuid,
    synthesis: &serde_json::Value,
    avatar_roster: &[String],
    mode: &str,
) -> Result<String, CouncilOrchestratorError> {
    let existing = raptorflow_db::queries::check_council_synthesis_artifact_exists(
        pool,
        org_id,
        council_run_id,
    )
    .await
    .map_err(|e| {
        CouncilOrchestratorError::DatabaseError(format!(
            "Failed to check existing council synthesis artifact: {}",
            e
        ))
    })?;

    if let Some(content_id) = existing {
        tracing::info!(
            council_run_id = %council_run_id,
            content_id = %content_id,
            "Council synthesis artifact already exists, skipping insert"
        );
        return Ok(content_id);
    }

    let normalized = normalize_synthesis_to_schema(synthesis, council_run_id, avatar_roster, mode);

    if let Err(errors) = raptorflow_db::validation::validate_council_synthesis(&normalized) {
        let msg = format!(
            "Council synthesis artifact failed schema validation: {}",
            errors.join("; ")
        );
        tracing::error!(council_run_id = %council_run_id, errors = %msg, "Schema validation failed");
        return Err(CouncilOrchestratorError::InvalidRequest(msg));
    }

    let content_id = uuid::Uuid::new_v4().to_string();
    raptorflow_db::queries::create_generated_content(
        pool,
        &content_id,
        org_id,
        None,
        Some(council_run_id),
        "council-synthesis",
        "generated",
        &normalized,
    )
    .await
    .map_err(|e| {
        CouncilOrchestratorError::DatabaseError(format!(
            "Failed to persist council synthesis artifact: {}",
            e
        ))
    })?;

    raptorflow_db::queries::update_council_orchestration_final_artifact(
        pool,
        council_run_id,
        org_id,
        &content_id,
    )
    .await
    .map_err(|e| {
        CouncilOrchestratorError::DatabaseError(format!(
            "Failed to update council orchestration final_artifact_id: {}",
            e
        ))
    })?;

    tracing::info!(
        council_run_id = %council_run_id,
        content_id = %content_id,
        "Council synthesis artifact persisted"
    );

    Ok(content_id)
}

pub(crate) fn truncate_c(text: &str, max_chars: usize) -> String {
    if text.len() <= max_chars {
        text.to_string()
    } else {
        let boundary = text.floor_char_boundary(max_chars);
        format!("{}...", &text[..boundary])
    }
}
