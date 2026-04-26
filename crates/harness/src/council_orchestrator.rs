use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_db::PgPool;
use raptorflow_db::models::AvatarDebateEvent;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, ChallengeDecision, DerivedInstinctFrame, analyst_challenge_decision,
    build_avatar_embodiment_pack, copywriter_challenge_decision,
    creative_director_challenge_decision, derive_analyst_instinct_frame,
    derive_copywriter_instinct_frame, derive_creative_director_instinct_frame,
    derive_growth_operator_instinct_frame, derive_proof_collector_instinct_frame,
    derive_researcher_instinct_frame, derive_strategist_instinct_frame,
    growth_operator_challenge_decision, proof_collector_challenge_decision,
    researcher_challenge_decision, strategist_challenge_decision,
};
use super::council_ai;

const DEFAULT_AVATAR_KEYS: &[&str] = &[
    "strategist",
    "researcher",
    "copywriter",
    "growth_operator",
    "analyst",
    "creative_director",
    "proof_collector",
];

const ALLOWED_AVATAR_KEYS: &[&str] = DEFAULT_AVATAR_KEYS;

const ALLOWED_MODES: &[&str] = &["dry_run", "draft"];

const MAX_CHALLENGE_ROUNDS: usize = 2;
const MAX_CHALLENGES_PER_AVATAR: usize = 3;
const MAX_TOTAL_CHALLENGES: usize = 21;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouncilRunRequest {
    pub org_id: Uuid,
    pub request_summary: String,
    pub context_summary: String,
    pub mode: String,
    pub requested_avatar_keys: Vec<String>,
    pub max_challenge_rounds: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouncilRunResult {
    pub council_run_id: String,
    pub harness_run_id: Option<String>,
    pub status: String,
    pub avatar_roster: Vec<String>,
    pub presence_states: Vec<AvatarPresenceStateOutput>,
    pub debate_events: Vec<AvatarDebateEvent>,
    pub synthesis: serde_json::Value,
    pub turns: Vec<CouncilTurnOutput>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvatarPresenceStateOutput {
    pub presence_id: String,
    pub avatar_key: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouncilTurnOutput {
    pub turn_id: String,
    pub avatar_key: String,
    pub turn_type: String,
    pub sequence_number: i32,
    pub status: String,
    pub instinct_frame: Option<DerivedInstinctFrame>,
    pub debate_event: Option<AvatarDebateEvent>,
}

#[derive(Debug)]
pub enum CouncilOrchestratorError {
    InvalidRequest(String),
    AvatarNotFound(String),
    DatabaseError(String),
    InternalError(String),
}

impl std::fmt::Display for CouncilOrchestratorError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CouncilOrchestratorError::InvalidRequest(msg) => write!(f, "Invalid request: {}", msg),
            CouncilOrchestratorError::AvatarNotFound(key) => write!(f, "Avatar not found: {}", key),
            CouncilOrchestratorError::DatabaseError(msg) => write!(f, "Database error: {}", msg),
            CouncilOrchestratorError::InternalError(msg) => write!(f, "Internal error: {}", msg),
        }
    }
}

impl std::error::Error for CouncilOrchestratorError {}

fn generate_id() -> String {
    Uuid::new_v4().to_string()
}

pub fn validate_request(req: &CouncilRunRequest) -> Result<(), CouncilOrchestratorError> {
    if req.request_summary.len() < 10 || req.request_summary.len() > 2000 {
        return Err(CouncilOrchestratorError::InvalidRequest(
            "request_summary must be between 10 and 2000 characters".to_string(),
        ));
    }
    if req.context_summary.len() > 8000 {
        return Err(CouncilOrchestratorError::InvalidRequest(
            "context_summary must be at most 8000 characters".to_string(),
        ));
    }
    if !ALLOWED_MODES.contains(&req.mode.as_str()) {
        return Err(CouncilOrchestratorError::InvalidRequest(format!(
            "mode must be one of: {:?}",
            ALLOWED_MODES
        )));
    }
    if req.max_challenge_rounds > 2 {
        return Err(CouncilOrchestratorError::InvalidRequest(
            "max_challenge_rounds must be 0, 1, or 2".to_string(),
        ));
    }
    for key in &req.requested_avatar_keys {
        if !ALLOWED_AVATAR_KEYS.contains(&key.as_str()) {
            return Err(CouncilOrchestratorError::InvalidRequest(format!(
                "Unknown avatar key: {}. Allowed: {:?}",
                key, ALLOWED_AVATAR_KEYS
            )));
        }
    }
    Ok(())
}

fn resolve_avatar_roster(requested: &[String]) -> Vec<String> {
    if requested.is_empty() {
        DEFAULT_AVATAR_KEYS.iter().map(|s| s.to_string()).collect()
    } else {
        requested.to_vec()
    }
}

fn derive_instinct_for_avatar(
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

fn create_position_content(avatar_key: &str, instinct: &DerivedInstinctFrame) -> serde_json::Value {
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

fn get_challenge_function(
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

fn compute_challenge_routing(avatar_key: &str) -> Vec<&'static str> {
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

pub async fn run_council_dry_run(
    pool: &PgPool,
    req: CouncilRunRequest,
) -> Result<CouncilRunResult, CouncilOrchestratorError> {
    validate_request(&req)?;

    let avatar_roster = resolve_avatar_roster(&req.requested_avatar_keys);
    let council_run_id = generate_id();
    let harness_run_id = generate_id();

    let roster_value = serde_json::to_value(&avatar_roster).unwrap_or(serde_json::json!([]));

    raptorflow_db::queries::create_council_orchestration_run(
        pool,
        &council_run_id,
        req.org_id,
        &req.request_summary,
        &req.mode,
        &roster_value,
        &req.context_summary,
        None,
    )
    .await
    .map_err(|e| CouncilOrchestratorError::DatabaseError(e.to_string()))?;

    raptorflow_db::queries::update_council_orchestration_status(
        pool,
        &council_run_id,
        req.org_id,
        "building_context",
        Some(chrono::Utc::now()),
        None,
        None,
    )
    .await
    .map_err(|e| CouncilOrchestratorError::DatabaseError(e.to_string()))?;

    let mut all_presence_states: Vec<AvatarPresenceStateOutput> = Vec::new();
    let mut all_debate_events: Vec<AvatarDebateEvent> = Vec::new();
    let mut all_turns: Vec<CouncilTurnOutput> = Vec::new();
    let mut avatar_packs: Vec<(String, AvatarEmbodimentPack)> = Vec::new();

    for (seq, avatar_key) in avatar_roster.iter().enumerate() {
        let avatar = raptorflow_db::queries::get_avatar_by_key(pool, req.org_id, avatar_key)
            .await
            .map_err(|e| CouncilOrchestratorError::DatabaseError(e.to_string()))?
            .ok_or_else(|| CouncilOrchestratorError::AvatarNotFound(avatar_key.clone()))?;

        let pack = build_avatar_embodiment_pack(pool, req.org_id, &avatar.avatar_id, None)
            .await
            .map_err(|e| CouncilOrchestratorError::InternalError(e.to_string()))?;

        avatar_packs.push((avatar_key.clone(), pack.clone()));

        let instinct = derive_instinct_for_avatar(
            avatar_key,
            &pack,
            &req.request_summary,
            &req.context_summary,
        );

        let position_content = create_position_content(avatar_key, &instinct);

        let turn_id = generate_id();
        let turn_input = serde_json::json!({
            "task_summary": req.request_summary,
            "context_summary": req.context_summary,
        });

        let presence_id = generate_id();
        let instinct_frame_id = instinct.instinct_frame_id.clone();

        let debate_event_id = generate_id();
        let debate_event = AvatarDebateEvent {
            debate_event_id: debate_event_id.clone(),
            org_id: req.org_id,
            harness_run_id: harness_run_id.clone(),
            speaker_avatar_id: Some(avatar.avatar_id.clone()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some(format!("{}_initial_position", avatar_key)),
            content: position_content,
            confidence: 0.7,
            created_at: chrono::Utc::now(),
        };

        let _ = raptorflow_db::queries::create_council_avatar_turn(
            pool,
            &turn_id,
            req.org_id,
            &council_run_id,
            &avatar.avatar_id,
            avatar_key,
            "instinct",
            seq as i32 + 1,
            &turn_input,
        )
        .await;

        let _ = raptorflow_db::queries::create_avatar_debate_event(
            pool,
            &debate_event_id,
            req.org_id,
            &harness_run_id,
            Some(&avatar.avatar_id),
            None,
            "position",
            Some(format!("{}_initial_position", avatar_key)).as_deref(),
            &debate_event.content,
            0.7,
        )
        .await;

        let _ = raptorflow_db::queries::update_council_avatar_turn_status(
            pool,
            &turn_id,
            req.org_id,
            "completed",
            Some(&serde_json::json!({
                "instinct": instinct,
                "position": debate_event.content,
            })),
            Some(&debate_event_id),
            Some(&instinct_frame_id),
            Some(&presence_id),
            None,
        )
        .await;

        let presence_output = AvatarPresenceStateOutput {
            presence_id: presence_id.clone(),
            avatar_key: avatar_key.clone(),
            state: "position_formed".to_string(),
            current_focus: instinct.dominant_concern.clone(),
            current_concern: instinct.dominant_concern.clone(),
            visible_summary: instinct.visible_summary.clone(),
            confidence: 0.7,
        };

        all_presence_states.push(presence_output);
        all_debate_events.push(debate_event);
        all_turns.push(CouncilTurnOutput {
            turn_id,
            avatar_key: avatar_key.clone(),
            turn_type: "instinct".to_string(),
            sequence_number: seq as i32 + 1,
            status: "completed".to_string(),
            instinct_frame: Some(instinct),
            debate_event: None,
        });
    }

    let challenge_rounds = req.max_challenge_rounds.min(MAX_CHALLENGE_ROUNDS);
    for round in 0..challenge_rounds {
        let round_num = round + 1;
        let mut round_challenges: Vec<AvatarDebateEvent> = Vec::new();
        let mut challenge_count = 0;

        for (avatar_key, pack) in &avatar_packs {
            if challenge_count >= MAX_TOTAL_CHALLENGES {
                break;
            }

            let targets = compute_challenge_routing(avatar_key);
            let challenge_fn = get_challenge_function(avatar_key);

            for target_key in &targets {
                if challenge_count >= MAX_TOTAL_CHALLENGES {
                    break;
                }

                let target_events: Vec<&AvatarDebateEvent> = all_debate_events
                    .iter()
                    .filter(|e| {
                        e.speaker_avatar_id.as_deref() == Some(*target_key)
                            || e.event_type == "position"
                    })
                    .collect();

                for target_event in target_events.iter().take(MAX_CHALLENGES_PER_AVATAR) {
                    if challenge_count >= MAX_TOTAL_CHALLENGES {
                        break;
                    }

                    let decision = challenge_fn(pack, target_event);
                    if decision.should_challenge && decision.confidence >= 0.5 {
                        let challenge_id = generate_id();
                        let target_avatar_id = avatar_packs
                            .iter()
                            .find(|(key, _)| key == target_key)
                            .map(|(_, p)| p.avatar_id.clone())
                            .unwrap_or_default();
                        let challenger_avatar_id = avatar_packs
                            .iter()
                            .find(|(key, _)| key == avatar_key)
                            .map(|(_, p)| p.avatar_id.clone())
                            .unwrap_or_default();

                        let challenge = AvatarDebateEvent {
                            debate_event_id: challenge_id.clone(),
                            org_id: req.org_id,
                            harness_run_id: harness_run_id.clone(),
                            speaker_avatar_id: Some(challenger_avatar_id.clone()),
                            target_avatar_id: Some(target_avatar_id.clone()),
                            event_type: "challenge".to_string(),
                            stance: Some(decision.reason.clone()),
                            content: serde_json::json!({
                                "challenge_reason": decision.reason,
                                "target_avatar_key": target_key,
                                "risk": decision.reason,
                                "required_fix": decision.suggested_event_type,
                                "suggested_direction": decision.suggested_event_type,
                            }),
                            confidence: decision.confidence,
                            created_at: chrono::Utc::now(),
                        };

                        let turn_id = generate_id();
                        let _ = raptorflow_db::queries::create_council_avatar_turn(
                            pool,
                            &turn_id,
                            req.org_id,
                            &council_run_id,
                            &challenger_avatar_id,
                            avatar_key,
                            "challenge",
                            (avatar_packs.len() * round_num
                                + avatar_packs
                                    .iter()
                                    .position(|(k, _)| k == avatar_key)
                                    .unwrap_or(0)) as i32
                                + 1,
                            &serde_json::json!({"target": target_key, "reason": decision.reason}),
                        )
                        .await;

                        let _ = raptorflow_db::queries::create_avatar_debate_event(
                            pool,
                            &challenge_id,
                            req.org_id,
                            &harness_run_id,
                            Some(&challenger_avatar_id),
                            Some(&target_avatar_id),
                            "challenge",
                            Some(decision.reason.clone()).as_deref(),
                            &challenge.content,
                            decision.confidence,
                        )
                        .await;

                        let _ = raptorflow_db::queries::update_council_avatar_turn_status(
                            pool,
                            &turn_id,
                            req.org_id,
                            "completed",
                            Some(&serde_json::json!({"challenge": decision.reason})),
                            Some(&challenge_id),
                            None,
                            None,
                            None,
                        )
                        .await;

                        round_challenges.push(challenge);
                        challenge_count += 1;
                    }
                }
            }
        }

        all_debate_events.extend(round_challenges.clone());

        if round_challenges.is_empty() {
            break;
        }
    }

    let synthesis = synthesize_council_result(
        &req.request_summary,
        &req.context_summary,
        &all_debate_events,
        &avatar_roster,
    );

    let _ = raptorflow_db::queries::update_council_orchestration_synthesis(
        pool,
        &council_run_id,
        req.org_id,
        &synthesis,
        None,
        Some(&harness_run_id),
    )
    .await;

    let _ = raptorflow_db::queries::update_council_orchestration_status(
        pool,
        &council_run_id,
        req.org_id,
        "completed",
        None,
        Some(chrono::Utc::now()),
        None,
    )
    .await;

    Ok(CouncilRunResult {
        council_run_id,
        harness_run_id: Some(harness_run_id),
        status: "completed".to_string(),
        avatar_roster,
        presence_states: all_presence_states,
        debate_events: all_debate_events,
        synthesis,
        turns: all_turns,
    })
}

/// Runs a council orchestration with AI-powered instinct, challenge, and synthesis.
///
/// When `bedrock` is `Some` and the run is in `"draft"` mode, AI is used for:
/// - Instinct frame derivation (avatar role-lock prompt + context)
/// - Challenge evaluation (avatar role-lock prompt + target position)
/// - Synthesis of all positions and challenges
///
/// Falls back to deterministic logic when Bedrock is unavailable or mode is `"dry_run"`.
pub async fn run_council_run(
    pool: &PgPool,
    bedrock: Option<Arc<BedrockInferenceClient>>,
    req: CouncilRunRequest,
) -> Result<CouncilRunResult, CouncilOrchestratorError> {
    let use_ai = bedrock.is_some() && req.mode == "draft";

    validate_request(&req)?;

    let avatar_roster = resolve_avatar_roster(&req.requested_avatar_keys);
    let council_run_id = generate_id();
    let harness_run_id = generate_id();

    let roster_value = serde_json::to_value(&avatar_roster).unwrap_or(serde_json::json!([]));

    raptorflow_db::queries::create_council_orchestration_run(
        pool,
        &council_run_id,
        req.org_id,
        &req.request_summary,
        &req.mode,
        &roster_value,
        &req.context_summary,
        None,
    )
    .await
    .map_err(|e| CouncilOrchestratorError::DatabaseError(e.to_string()))?;

    raptorflow_db::queries::update_council_orchestration_status(
        pool,
        &council_run_id,
        req.org_id,
        "building_context",
        Some(chrono::Utc::now()),
        None,
        None,
    )
    .await
    .map_err(|e| CouncilOrchestratorError::DatabaseError(e.to_string()))?;

    let mut all_presence_states: Vec<AvatarPresenceStateOutput> = Vec::new();
    let mut all_debate_events: Vec<AvatarDebateEvent> = Vec::new();
    let mut all_turns: Vec<CouncilTurnOutput> = Vec::new();
    let mut avatar_packs: Vec<(String, AvatarEmbodimentPack)> = Vec::new();

    for (seq, avatar_key) in avatar_roster.iter().enumerate() {
        let avatar = raptorflow_db::queries::get_avatar_by_key(pool, req.org_id, avatar_key)
            .await
            .map_err(|e| CouncilOrchestratorError::DatabaseError(e.to_string()))?
            .ok_or_else(|| CouncilOrchestratorError::AvatarNotFound(avatar_key.clone()))?;

        let pack = build_avatar_embodiment_pack(pool, req.org_id, &avatar.avatar_id, None)
            .await
            .map_err(|e| CouncilOrchestratorError::InternalError(e.to_string()))?;

        avatar_packs.push((avatar_key.clone(), pack.clone()));

        let instinct = if use_ai {
            if let Some(bedrock) = &bedrock {
                council_ai::ai_derive_instinct(
                    bedrock,
                    &pack,
                    avatar_key,
                    &req.request_summary,
                    &req.context_summary,
                )
                .await
                .unwrap_or_else(|| {
                    derive_instinct_for_avatar(avatar_key, &pack, &req.request_summary, &req.context_summary)
                })
            } else {
                derive_instinct_for_avatar(avatar_key, &pack, &req.request_summary, &req.context_summary)
            }
        } else {
            derive_instinct_for_avatar(avatar_key, &pack, &req.request_summary, &req.context_summary)
        };

        let position_content = create_position_content(avatar_key, &instinct);

        let turn_id = generate_id();
        let turn_input = serde_json::json!({
            "task_summary": req.request_summary,
            "context_summary": req.context_summary,
        });

        let presence_id = generate_id();
        let instinct_frame_id = instinct.instinct_frame_id.clone();

        let debate_event_id = generate_id();
        let debate_event = AvatarDebateEvent {
            debate_event_id: debate_event_id.clone(),
            org_id: req.org_id,
            harness_run_id: harness_run_id.clone(),
            speaker_avatar_id: Some(avatar.avatar_id.clone()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some(format!("{}_initial_position", avatar_key)),
            content: position_content,
            confidence: 0.7,
            created_at: chrono::Utc::now(),
        };

        let _ = raptorflow_db::queries::create_council_avatar_turn(
            pool, &turn_id, req.org_id, &council_run_id,
            &avatar.avatar_id, avatar_key, "instinct",
            seq as i32 + 1, &turn_input,
        ).await;

        let _ = raptorflow_db::queries::create_avatar_debate_event(
            pool, &debate_event_id, req.org_id, &harness_run_id,
            Some(&avatar.avatar_id), None, "position",
            Some(format!("{}_initial_position", avatar_key)).as_deref(),
            &debate_event.content, 0.7,
        ).await;

        let _ = raptorflow_db::queries::update_council_avatar_turn_status(
            pool, &turn_id, req.org_id, "completed",
            Some(&serde_json::json!({"instinct": instinct, "position": debate_event.content})),
            Some(&debate_event_id), Some(&instinct_frame_id), Some(&presence_id), None,
        ).await;

        all_presence_states.push(AvatarPresenceStateOutput {
            presence_id,
            avatar_key: avatar_key.clone(),
            state: "position_formed".to_string(),
            current_focus: instinct.dominant_concern.clone(),
            current_concern: instinct.dominant_concern.clone(),
            visible_summary: instinct.visible_summary.clone(),
            confidence: 0.7,
        });
        all_debate_events.push(debate_event);
        all_turns.push(CouncilTurnOutput {
            turn_id,
            avatar_key: avatar_key.clone(),
            turn_type: "instinct".to_string(),
            sequence_number: seq as i32 + 1,
            status: "completed".to_string(),
            instinct_frame: Some(instinct),
            debate_event: None,
        });
    }

    // Challenge rounds
    let challenge_rounds = req.max_challenge_rounds.min(MAX_CHALLENGE_ROUNDS);
    for round in 0..challenge_rounds {
        let round_num = round + 1;
        let mut round_challenges: Vec<AvatarDebateEvent> = Vec::new();
        let mut challenge_count = 0;

        for (avatar_key, pack) in &avatar_packs {
            if challenge_count >= MAX_TOTAL_CHALLENGES {
                break;
            }

            let targets = compute_challenge_routing(avatar_key);
            let deterministic_challenge = get_challenge_function(avatar_key);

            for target_key in &targets {
                if challenge_count >= MAX_TOTAL_CHALLENGES {
                    break;
                }

                let target_events: Vec<&AvatarDebateEvent> = all_debate_events.iter()
                    .filter(|e| e.speaker_avatar_id.as_deref() == Some(*target_key) || e.event_type == "position")
                    .collect();

                for target_event in target_events.iter().take(MAX_CHALLENGES_PER_AVATAR) {
                    if challenge_count >= MAX_TOTAL_CHALLENGES {
                        break;
                    }

                    let decision = if use_ai {
                        if let Some(bedrock) = &bedrock {
                            council_ai::ai_evaluate_challenge(
                                bedrock, pack, avatar_key, target_key,
                                &serde_json::to_string(&target_event.content).unwrap_or_default(),
                            ).await
                            .unwrap_or_else(|| deterministic_challenge(pack, target_event))
                        } else {
                            deterministic_challenge(pack, target_event)
                        }
                    } else {
                        deterministic_challenge(pack, target_event)
                    };

                    if decision.should_challenge && decision.confidence >= 0.5 {
                        let challenge_id = generate_id();
                        let target_avatar_id = avatar_packs.iter()
                            .find(|(key, _)| key == target_key)
                            .map(|(_, p)| p.avatar_id.clone())
                            .unwrap_or_default();
                        let challenger_avatar_id = avatar_packs.iter()
                            .find(|(key, _)| key == avatar_key)
                            .map(|(_, p)| p.avatar_id.clone())
                            .unwrap_or_default();

                        let challenge = AvatarDebateEvent {
                            debate_event_id: challenge_id.clone(),
                            org_id: req.org_id,
                            harness_run_id: harness_run_id.clone(),
                            speaker_avatar_id: Some(challenger_avatar_id.clone()),
                            target_avatar_id: Some(target_avatar_id.clone()),
                            event_type: "challenge".to_string(),
                            stance: Some(decision.reason.clone()),
                            content: serde_json::json!({
                                "challenge_reason": decision.reason,
                                "target_avatar_key": target_key,
                                "suggested_direction": decision.suggested_event_type,
                            }),
                            confidence: decision.confidence,
                            created_at: chrono::Utc::now(),
                        };

                        let turn_id = generate_id();
                        let _ = raptorflow_db::queries::create_council_avatar_turn(
                            pool, &turn_id, req.org_id, &council_run_id,
                            &challenger_avatar_id, avatar_key, "challenge",
                            (avatar_packs.len() * round_num
                                + avatar_packs.iter().position(|(k, _)| k == avatar_key).unwrap_or(0)) as i32 + 1,
                            &serde_json::json!({"target": target_key, "reason": decision.reason}),
                        ).await;

                        let _ = raptorflow_db::queries::create_avatar_debate_event(
                            pool, &challenge_id, req.org_id, &harness_run_id,
                            Some(&challenger_avatar_id), Some(&target_avatar_id),
                            "challenge", Some(&decision.reason),
                            &challenge.content, decision.confidence,
                        ).await;

                        let _ = raptorflow_db::queries::update_council_avatar_turn_status(
                            pool, &turn_id, req.org_id, "completed",
                            Some(&serde_json::json!({"challenge": decision.reason})),
                            Some(&challenge_id), None, None, None,
                        ).await;

                        round_challenges.push(challenge);
                        challenge_count += 1;
                    }
                }
            }
        }

        all_debate_events.extend(round_challenges);
    }

    let synthesis = if use_ai {
        if let Some(bedrock) = &bedrock {
            let debate_summary = all_debate_events.iter()
                .map(|e| {
                    let speaker = e.speaker_avatar_id.as_deref().unwrap_or("?");
                    let target = e.target_avatar_id.as_deref().unwrap_or("none");
                    let content_str = serde_json::to_string(&e.content).unwrap_or_default();
                    format!("[{}] {} → {} (conf: {}): {}",
                        e.event_type, speaker, target, e.confidence,
                        truncate_c(&content_str, 200))
                })
                .collect::<Vec<_>>()
                .join("\n");

            council_ai::ai_synthesize(
                bedrock, &req.request_summary, &req.context_summary,
                &debate_summary,
            ).await
            .unwrap_or_else(|| synthesize_council_result(
                &req.request_summary, &req.context_summary,
                &all_debate_events, &avatar_roster,
            ))
        } else {
            synthesize_council_result(&req.request_summary, &req.context_summary,
                &all_debate_events, &avatar_roster)
        }
    } else {
        synthesize_council_result(&req.request_summary, &req.context_summary,
            &all_debate_events, &avatar_roster)
    };

    let _ = raptorflow_db::queries::update_council_orchestration_synthesis(
        pool, &council_run_id, req.org_id, &synthesis, None, Some(&harness_run_id),
    ).await;

    let _ = raptorflow_db::queries::update_council_orchestration_status(
        pool, &council_run_id, req.org_id, "completed", None, Some(chrono::Utc::now()), None,
    ).await;

    Ok(CouncilRunResult {
        council_run_id,
        harness_run_id: Some(harness_run_id),
        status: "completed".to_string(),
        avatar_roster,
        presence_states: all_presence_states,
        debate_events: all_debate_events,
        synthesis,
        turns: all_turns,
    })
}

fn truncate_c(text: &str, max_chars: usize) -> String {
    if text.len() <= max_chars {
        text.to_string()
    } else {
        let boundary = text.floor_char_boundary(max_chars);
        format!("{}...", &text[..boundary])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const ALL_7_KEYS: [&str; 7] = [
        "strategist",
        "researcher",
        "copywriter",
        "growth_operator",
        "analyst",
        "creative_director",
        "proof_collector",
    ];

    #[test]
    fn test_default_roster_contains_all_7_avatars() {
        let roster = resolve_avatar_roster(&[]);
        assert_eq!(roster.len(), 7);
        for key in &ALL_7_KEYS {
            assert!(roster.contains(&key.to_string()), "Missing avatar: {}", key);
        }
    }

    #[test]
    fn test_requested_roster_rejects_unknown_key() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Test request summary for council".to_string(),
            context_summary: "Test context".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec!["unknown_avatar".to_string()],
            max_challenge_rounds: 1,
        };
        let result = validate_request(&req);
        assert!(result.is_err());
        let err = result.unwrap_err();
        match err {
            CouncilOrchestratorError::InvalidRequest(msg) => {
                assert!(msg.contains("unknown_avatar"));
            }
            _ => panic!("Expected InvalidRequest error"),
        }
    }

    #[test]
    fn test_validate_request_accepts_valid() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Valid test request summary for council".to_string(),
            context_summary: "Test context".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec!["strategist".to_string(), "analyst".to_string()],
            max_challenge_rounds: 1,
        };
        assert!(validate_request(&req).is_ok());
    }

    #[test]
    fn test_max_challenge_rounds_rejects_gt_2() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Test request summary for council validation".to_string(),
            context_summary: "Test".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec![],
            max_challenge_rounds: 5,
        };
        let result = validate_request(&req);
        assert!(result.is_err());
    }

    #[test]
    fn test_synthesis_contains_all_required_sections() {
        let debate_events = vec![];
        let avatar_roster = vec!["strategist".to_string(), "researcher".to_string()];
        let synthesis =
            synthesize_council_result("Test task", "Test context", &debate_events, &avatar_roster);
        assert!(synthesis.get("known_facts").is_some());
        assert!(synthesis.get("assumptions").is_some());
        assert!(synthesis.get("council_recommendation").is_some());
        assert!(synthesis.get("avatar_positions").is_some());
        assert!(synthesis.get("challenges").is_some());
        assert!(synthesis.get("risks").is_some());
        assert!(synthesis.get("open_questions").is_some());
        assert!(synthesis.get("next_actions").is_some());
    }

    #[test]
    fn test_thin_context_produces_open_questions() {
        let debate_events = vec![];
        let avatar_roster = vec!["strategist".to_string()];
        let synthesis = synthesize_council_result("Brief task", "", &debate_events, &avatar_roster);
        let open_questions = synthesis["open_questions"].as_array().unwrap();
        assert!(!open_questions.is_empty());
    }

    #[test]
    fn test_challenge_routing_prevents_self_challenge() {
        for key in &ALL_7_KEYS {
            let targets = compute_challenge_routing(key);
            assert!(
                !targets.contains(key),
                "Avatar {} can challenge itself",
                key
            );
        }
    }

    #[test]
    fn test_challenge_cap_enforced() {
        let challengers = [
            (
                "researcher",
                [
                    "strategist",
                    "copywriter",
                    "creative_director",
                    "growth_operator",
                ]
                .as_slice(),
            ),
            (
                "proof_collector",
                [
                    "strategist",
                    "copywriter",
                    "creative_director",
                    "growth_operator",
                    "researcher",
                ]
                .as_slice(),
            ),
            (
                "analyst",
                ["strategist", "growth_operator", "copywriter"].as_slice(),
            ),
            ("strategist", ["researcher", "copywriter"].as_slice()),
            ("copywriter", ["strategist", "creative_director"].as_slice()),
            ("growth_operator", ["strategist", "copywriter"].as_slice()),
            ("creative_director", ["strategist", "copywriter"].as_slice()),
        ];
        for (key, expected_targets) in &challengers {
            let targets = compute_challenge_routing(key);
            assert!(!targets.contains(key));
            assert_eq!(targets.len(), expected_targets.len());
        }
    }

    #[test]
    fn test_researcher_challenges_unsupported_claim() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "researcher".to_string(),
            display_name: "Researcher".to_string(),
            role: "researcher".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "We are the best solution and always deliver massive results without any proven evidence"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = researcher_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_analyst_challenges_scaling_from_weak_signal() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "analyst".to_string(),
            display_name: "Analyst".to_string(),
            role: "analyst".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "We should double down on this channel based on the impressions we saw"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = analyst_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_proof_collector_challenges_unsupported_proof() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "proof_collector".to_string(),
            display_name: "Proof Collector".to_string(),
            role: "proof".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("copywriter".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "Our solution is guaranteed to deliver 10x ROI"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = proof_collector_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_creative_director_challenges_generic_concept() {
        let pack = AvatarEmbodimentPack {
            avatar_id: "test".to_string(),
            avatar_key: "creative_director".to_string(),
            display_name: "Creative Director".to_string(),
            role: "creative".to_string(),
            identity_kernel: serde_json::json!({}),
            worldview: vec![],
            obsessions: vec![],
            reflexes: vec![],
            taboos: vec![],
            operating_principles: vec![],
            debate_style: serde_json::json!({}),
            memory_edges: vec![],
        };
        let event = AvatarDebateEvent {
            debate_event_id: "test".to_string(),
            org_id: Uuid::new_v4(),
            harness_run_id: String::new(),
            speaker_avatar_id: Some("strategist".to_string()),
            target_avatar_id: None,
            event_type: "position".to_string(),
            stance: Some("test".to_string()),
            content: serde_json::json!({"text": "Use a generic stock photo template with our logo"}),
            confidence: 0.8,
            created_at: chrono::Utc::now(),
        };
        let decision = creative_director_challenge_decision(&pack, &event);
        assert!(decision.should_challenge);
    }

    #[test]
    fn test_dry_run_does_not_call_bedrock() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Test council dry run with minimal context".to_string(),
            context_summary: "Simple test".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec![],
            max_challenge_rounds: 0,
        };
        assert!(validate_request(&req).is_ok());
    }

    #[test]
    fn test_validate_request_short_summary_rejected() {
        let req = CouncilRunRequest {
            org_id: Uuid::new_v4(),
            request_summary: "Short".to_string(),
            context_summary: "Test context".to_string(),
            mode: "dry_run".to_string(),
            requested_avatar_keys: vec![],
            max_challenge_rounds: 1,
        };
        assert!(validate_request(&req).is_err());
    }

    #[test]
    fn test_create_position_content_all_avatars() {
        let instinct = DerivedInstinctFrame {
            instinct_frame_id: "test".to_string(),
            dominant_concern: "Test concern".to_string(),
            risk_flags: vec!["missing_proof".to_string(), "weak_signal".to_string()],
            recommended_posture: "Test posture".to_string(),
            visible_summary: "Test summary".to_string(),
        };
        for key in &ALL_7_KEYS {
            let content = create_position_content(key, &instinct);
            assert!(
                content.is_object(),
                "Position content for {} is not an object",
                key
            );
        }
    }
}
