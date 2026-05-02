use super::*;
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

        raptorflow_db::queries::create_council_avatar_turn(
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
        .await
        .map_err(|e| {
            CouncilOrchestratorError::DatabaseError(format!(
                "Failed to create council avatar turn: {}",
                e
            ))
        })?;

        raptorflow_db::queries::create_avatar_debate_event(
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
        .await
        .map_err(|e| {
            CouncilOrchestratorError::DatabaseError(format!(
                "Failed to create avatar debate event: {}",
                e
            ))
        })?;

        raptorflow_db::queries::update_council_avatar_turn_status(
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
        .await
        .map_err(|e| {
            CouncilOrchestratorError::DatabaseError(format!(
                "Failed to update council avatar turn status: {}",
                e
            ))
        })?;

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
                        raptorflow_db::queries::create_council_avatar_turn(
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
                        .await
                        .map_err(|e| {
                            CouncilOrchestratorError::DatabaseError(format!(
                                "Failed to create council avatar turn: {}",
                                e
                            ))
                        })?;

                        raptorflow_db::queries::create_avatar_debate_event(
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
                        .await
                        .map_err(|e| {
                            CouncilOrchestratorError::DatabaseError(format!(
                                "Failed to create avatar debate event: {}",
                                e
                            ))
                        })?;

                        raptorflow_db::queries::update_council_avatar_turn_status(
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
                        .await
                        .map_err(|e| {
                            CouncilOrchestratorError::DatabaseError(format!(
                                "Failed to update council avatar turn status: {}",
                                e
                            ))
                        })?;

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

    raptorflow_db::queries::update_council_orchestration_synthesis(
        pool,
        &council_run_id,
        req.org_id,
        &synthesis,
        None,
        Some(&harness_run_id),
    )
    .await
    .map_err(|e| {
        CouncilOrchestratorError::DatabaseError(format!(
            "Failed to update council orchestration synthesis: {}",
            e
        ))
    })?;

    persist_council_synthesis_artifact(
        pool,
        &council_run_id,
        req.org_id,
        &synthesis,
        &avatar_roster,
        &req.mode,
    )
    .await?;

    raptorflow_db::queries::update_council_orchestration_status(
        pool,
        &council_run_id,
        req.org_id,
        "completed",
        None,
        Some(chrono::Utc::now()),
        None,
    )
    .await
    .map_err(|e| {
        CouncilOrchestratorError::DatabaseError(format!(
            "Failed to update council orchestration status: {}",
            e
        ))
    })?;

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
                    derive_instinct_for_avatar(
                        avatar_key,
                        &pack,
                        &req.request_summary,
                        &req.context_summary,
                    )
                })
            } else {
                derive_instinct_for_avatar(
                    avatar_key,
                    &pack,
                    &req.request_summary,
                    &req.context_summary,
                )
            }
        } else {
            derive_instinct_for_avatar(
                avatar_key,
                &pack,
                &req.request_summary,
                &req.context_summary,
            )
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

        raptorflow_db::queries::create_council_avatar_turn(
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
        .await
        .map_err(|e| {
            CouncilOrchestratorError::DatabaseError(format!(
                "Failed to create council avatar turn: {}",
                e
            ))
        })?;

        raptorflow_db::queries::create_avatar_debate_event(
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
        .await
        .map_err(|e| {
            CouncilOrchestratorError::DatabaseError(format!(
                "Failed to create avatar debate event: {}",
                e
            ))
        })?;

        raptorflow_db::queries::update_council_avatar_turn_status(
            pool,
            &turn_id,
            req.org_id,
            "completed",
            Some(&serde_json::json!({"instinct": instinct, "position": debate_event.content})),
            Some(&debate_event_id),
            Some(&instinct_frame_id),
            Some(&presence_id),
            None,
        )
        .await
        .map_err(|e| {
            CouncilOrchestratorError::DatabaseError(format!(
                "Failed to update council avatar turn status: {}",
                e
            ))
        })?;

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

                    let decision = if use_ai {
                        if let Some(bedrock) = &bedrock {
                            council_ai::ai_evaluate_challenge(
                                bedrock,
                                pack,
                                avatar_key,
                                target_key,
                                &serde_json::to_string(&target_event.content).unwrap_or_default(),
                            )
                            .await
                            .unwrap_or_else(|| deterministic_challenge(pack, target_event))
                        } else {
                            deterministic_challenge(pack, target_event)
                        }
                    } else {
                        deterministic_challenge(pack, target_event)
                    };

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
                        raptorflow_db::queries::create_council_avatar_turn(
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
                        .await
                        .map_err(|e| {
                            CouncilOrchestratorError::DatabaseError(format!(
                                "Failed to create council avatar turn: {}",
                                e
                            ))
                        })?;

                        raptorflow_db::queries::create_avatar_debate_event(
                            pool,
                            &challenge_id,
                            req.org_id,
                            &harness_run_id,
                            Some(&challenger_avatar_id),
                            Some(&target_avatar_id),
                            "challenge",
                            Some(&decision.reason),
                            &challenge.content,
                            decision.confidence,
                        )
                        .await
                        .map_err(|e| {
                            CouncilOrchestratorError::DatabaseError(format!(
                                "Failed to create avatar debate event: {}",
                                e
                            ))
                        })?;

                        raptorflow_db::queries::update_council_avatar_turn_status(
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
                        .await
                        .map_err(|e| {
                            CouncilOrchestratorError::DatabaseError(format!(
                                "Failed to update council avatar turn status: {}",
                                e
                            ))
                        })?;

                        round_challenges.push(challenge);
                        challenge_count += 1;
                    }
                }
            }
        }

        if round_challenges.is_empty() {
            tracing::debug!(
                round = round_num,
                "No challenges generated, ending challenge rounds early"
            );
            break;
        }

        all_debate_events.extend(round_challenges);
    }

    let synthesis = if use_ai {
        if let Some(bedrock) = &bedrock {
            let debate_summary = all_debate_events
                .iter()
                .map(|e| {
                    let speaker = e.speaker_avatar_id.as_deref().unwrap_or("?");
                    let target = e.target_avatar_id.as_deref().unwrap_or("none");
                    let content_str = serde_json::to_string(&e.content).unwrap_or_default();
                    format!(
                        "[{}] {} → {} (conf: {}): {}",
                        e.event_type,
                        speaker,
                        target,
                        e.confidence,
                        truncate_c(&content_str, 200)
                    )
                })
                .collect::<Vec<_>>()
                .join("\n");

            council_ai::ai_synthesize(
                bedrock,
                &req.request_summary,
                &req.context_summary,
                &debate_summary,
            )
            .await
            .unwrap_or_else(|| {
                synthesize_council_result(
                    &req.request_summary,
                    &req.context_summary,
                    &all_debate_events,
                    &avatar_roster,
                )
            })
        } else {
            synthesize_council_result(
                &req.request_summary,
                &req.context_summary,
                &all_debate_events,
                &avatar_roster,
            )
        }
    } else {
        synthesize_council_result(
            &req.request_summary,
            &req.context_summary,
            &all_debate_events,
            &avatar_roster,
        )
    };

    raptorflow_db::queries::update_council_orchestration_synthesis(
        pool,
        &council_run_id,
        req.org_id,
        &synthesis,
        None,
        Some(&harness_run_id),
    )
    .await
    .map_err(|e| {
        CouncilOrchestratorError::DatabaseError(format!(
            "Failed to update council orchestration synthesis: {}",
            e
        ))
    })?;

    persist_council_synthesis_artifact(
        pool,
        &council_run_id,
        req.org_id,
        &synthesis,
        &avatar_roster,
        &req.mode,
    )
    .await?;

    raptorflow_db::queries::update_council_orchestration_status(
        pool,
        &council_run_id,
        req.org_id,
        "completed",
        None,
        Some(chrono::Utc::now()),
        None,
    )
    .await
    .map_err(|e| {
        CouncilOrchestratorError::DatabaseError(format!(
            "Failed to update council orchestration status: {}",
            e
        ))
    })?;

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
