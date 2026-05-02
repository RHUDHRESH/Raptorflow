use super::common::*;
use sqlx::FromRow;

pub async fn get_avatar_soul(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
) -> Result<Option<AvatarSoul>, sqlx::Error> {
    let row = sqlx::query_as::<_, AvatarSoul>(
        r#"
        SELECT soul_id, org_id, avatar_id, identity_kernel, worldview, obsessions,
               reflexes, taboos, debate_style, embodiment_level, operating_principles,
               evaluation_bias, is_active, created_at, updated_at
        FROM avatar_souls
        WHERE avatar_id = $1 AND org_id = $2
        "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;

    Ok(row)
}

#[allow(clippy::too_many_arguments)]
pub async fn upsert_avatar_soul(
    pool: &PgPool,
    soul_id: &str,
    org_id: uuid::Uuid,
    avatar_id: &str,
    identity_kernel: &serde_json::Value,
    worldview: &serde_json::Value,
    obsessions: &serde_json::Value,
    reflexes: &serde_json::Value,
    taboos: &serde_json::Value,
    debate_style: &serde_json::Value,
    embodiment_level: &str,
    operating_principles: &serde_json::Value,
    evaluation_bias: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_souls (
            soul_id, org_id, avatar_id, identity_kernel, worldview, obsessions,
            reflexes, taboos, debate_style, embodiment_level, operating_principles,
            evaluation_bias
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        ON CONFLICT (org_id, avatar_id) DO UPDATE SET
            identity_kernel = EXCLUDED.identity_kernel,
            worldview = EXCLUDED.worldview,
            obsessions = EXCLUDED.obsessions,
            reflexes = EXCLUDED.reflexes,
            taboos = EXCLUDED.taboos,
            debate_style = EXCLUDED.debate_style,
            embodiment_level = EXCLUDED.embodiment_level,
            operating_principles = EXCLUDED.operating_principles,
            evaluation_bias = EXCLUDED.evaluation_bias,
            updated_at = now()
        "#,
    )
    .bind(soul_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(identity_kernel)
    .bind(worldview)
    .bind(obsessions)
    .bind(reflexes)
    .bind(taboos)
    .bind(debate_style)
    .bind(embodiment_level)
    .bind(operating_principles)
    .bind(evaluation_bias)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn list_avatar_memory_edges(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
) -> Result<Vec<AvatarMemoryEdge>, sqlx::Error> {
    let rows = sqlx::query_as::<_, AvatarMemoryEdge>(
        r#"
        SELECT memory_edge_id, org_id, avatar_id, ripple_id, relationship_type,
               salience, decay_policy, use_when, last_used_at, created_at, updated_at
        FROM avatar_memory_edges
        WHERE avatar_id = $1 AND org_id = $2
        ORDER BY salience DESC
        "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;

    Ok(rows)
}

pub async fn create_avatar_memory_edge(
    pool: &PgPool,
    memory_edge_id: &str,
    org_id: uuid::Uuid,
    avatar_id: &str,
    ripple_id: &str,
    relationship_type: &str,
    salience: f64,
    decay_policy: &str,
    use_when: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_memory_edges (
            memory_edge_id, org_id, avatar_id, ripple_id, relationship_type,
            salience, decay_policy, use_when
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (org_id, avatar_id, ripple_id, relationship_type) DO UPDATE SET
            salience = EXCLUDED.salience,
            decay_policy = EXCLUDED.decay_policy,
            use_when = EXCLUDED.use_when,
            last_used_at = now(),
            updated_at = now()
        "#,
    )
    .bind(memory_edge_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(ripple_id)
    .bind(relationship_type)
    .bind(salience)
    .bind(decay_policy)
    .bind(use_when)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn delete_avatar_memory_edge(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
    memory_edge_id: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        DELETE FROM avatar_memory_edges
        WHERE memory_edge_id = $1 AND avatar_id = $2 AND org_id = $3
        "#,
    )
    .bind(memory_edge_id)
    .bind(avatar_id)
    .bind(org_id)
    .execute(pool)
    .await?;

    Ok(())
}

#[allow(clippy::too_many_arguments)]
pub async fn create_avatar_instinct_frame(
    pool: &PgPool,
    instinct_frame_id: &str,
    org_id: uuid::Uuid,
    avatar_id: &str,
    harness_run_id: Option<&str>,
    capability_run_id: Option<&str>,
    trigger_kind: &str,
    dominant_concern: &str,
    risk_flags: &serde_json::Value,
    recommended_posture: &str,
    visible_summary: &str,
    private_notes: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_instinct_frames (
            instinct_frame_id, org_id, avatar_id, harness_run_id, capability_run_id,
            trigger_kind, dominant_concern, risk_flags, recommended_posture,
            visible_summary, private_notes
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        "#,
    )
    .bind(instinct_frame_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(harness_run_id)
    .bind(capability_run_id)
    .bind(trigger_kind)
    .bind(dominant_concern)
    .bind(risk_flags)
    .bind(recommended_posture)
    .bind(visible_summary)
    .bind(private_notes)
    .execute(pool)
    .await?;

    Ok(())
}

#[allow(clippy::too_many_arguments)]
pub async fn upsert_avatar_presence_state(
    pool: &PgPool,
    presence_id: &str,
    org_id: uuid::Uuid,
    avatar_id: &str,
    harness_run_id: Option<&str>,
    state: &str,
    current_focus: &str,
    current_concern: &str,
    confidence: f64,
    visible_summary: &str,
    last_event_id: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_presence_states (
            presence_id, org_id, avatar_id, harness_run_id, state,
            current_focus, current_concern, confidence, visible_summary, last_event_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (org_id, avatar_id, harness_run_id) DO UPDATE SET
            state = EXCLUDED.state,
            current_focus = EXCLUDED.current_focus,
            current_concern = EXCLUDED.current_concern,
            confidence = EXCLUDED.confidence,
            visible_summary = EXCLUDED.visible_summary,
            last_event_id = EXCLUDED.last_event_id,
            updated_at = now()
        "#,
    )
    .bind(presence_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(harness_run_id)
    .bind(state)
    .bind(current_focus)
    .bind(current_concern)
    .bind(confidence)
    .bind(visible_summary)
    .bind(last_event_id)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn list_harness_presence(
    pool: &PgPool,
    org_id: uuid::Uuid,
    harness_run_id: &str,
) -> Result<Vec<AvatarPresenceState>, sqlx::Error> {
    let rows = sqlx::query_as::<_, AvatarPresenceState>(
        r#"
        SELECT presence_id, org_id, avatar_id, harness_run_id, state,
               current_focus, current_concern, confidence, visible_summary,
               last_event_id, updated_at
        FROM avatar_presence_states
        WHERE harness_run_id = $1 AND org_id = $2
        "#,
    )
    .bind(harness_run_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;

    Ok(rows)
}

pub async fn create_avatar_debate_event(
    pool: &PgPool,
    debate_event_id: &str,
    org_id: uuid::Uuid,
    harness_run_id: &str,
    speaker_avatar_id: Option<&str>,
    target_avatar_id: Option<&str>,
    event_type: &str,
    stance: Option<&str>,
    content: &serde_json::Value,
    confidence: f64,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_debate_events (
            debate_event_id, org_id, harness_run_id, speaker_avatar_id,
            target_avatar_id, event_type, stance, content, confidence
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        "#,
    )
    .bind(debate_event_id)
    .bind(org_id)
    .bind(harness_run_id)
    .bind(speaker_avatar_id)
    .bind(target_avatar_id)
    .bind(event_type)
    .bind(stance)
    .bind(content)
    .bind(confidence)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn list_debate_events(
    pool: &PgPool,
    org_id: uuid::Uuid,
    harness_run_id: &str,
) -> Result<Vec<AvatarDebateEvent>, sqlx::Error> {
    let rows = sqlx::query_as::<_, AvatarDebateEvent>(
        r#"
        SELECT debate_event_id, org_id, harness_run_id, speaker_avatar_id,
               target_avatar_id, event_type, stance, content, confidence, created_at
        FROM avatar_debate_events
        WHERE harness_run_id = $1 AND org_id = $2
        ORDER BY created_at ASC
        "#,
    )
    .bind(harness_run_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;

    Ok(rows)
}

pub async fn create_avatar_artifact_trail(
    pool: &PgPool,
    trail_id: &str,
    org_id: uuid::Uuid,
    avatar_id: &str,
    artifact_id: &str,
    harness_run_id: Option<&str>,
    contribution_type: &str,
    summary: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_artifact_trails (
            trail_id, org_id, avatar_id, artifact_id, harness_run_id,
            contribution_type, summary
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (org_id, avatar_id, artifact_id, contribution_type) DO UPDATE SET
            harness_run_id = EXCLUDED.harness_run_id,
            summary = EXCLUDED.summary
        "#,
    )
    .bind(trail_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(artifact_id)
    .bind(harness_run_id)
    .bind(contribution_type)
    .bind(summary)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn list_avatar_artifact_trail(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
) -> Result<Vec<AvatarArtifactTrail>, sqlx::Error> {
    let rows = sqlx::query_as::<_, AvatarArtifactTrail>(
        r#"
        SELECT trail_id, org_id, avatar_id, artifact_id, harness_run_id,
               contribution_type, summary, created_at
        FROM avatar_artifact_trails
         WHERE avatar_id = $1 AND org_id = $2
         ORDER BY created_at DESC
         "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;

    Ok(rows)
}

// ─── Council Synthesis Artifact Persistence ──────────────────────────────────

pub async fn check_council_synthesis_artifact_exists(
    pool: &PgPool,
    org_id: uuid::Uuid,
    council_run_id: &str,
) -> Result<Option<String>, sqlx::Error> {
    let row = sqlx::query_scalar::<_, String>(
        r#"
        SELECT content_id FROM generated_content
        WHERE org_id = $1
          AND content_type = 'council-synthesis'
          AND body->>'council_run_id' = $2
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .bind(council_run_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub async fn update_council_orchestration_final_artifact(
    pool: &PgPool,
    council_run_id: &str,
    org_id: uuid::Uuid,
    final_artifact_id: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE council_orchestration_runs
        SET final_artifact_id = $1, updated_at = now()
        WHERE council_run_id = $2 AND org_id = $3
        "#,
    )
    .bind(final_artifact_id)
    .bind(council_run_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

// --- COUNCIL ORCHESTRATION RUNS ---

pub async fn create_council_orchestration_run(
    pool: &PgPool,
    council_run_id: &str,
    org_id: uuid::Uuid,
    request_summary: &str,
    mode: &str,
    avatar_roster: &serde_json::Value,
    context_summary: &str,
    created_by: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO council_orchestration_runs
            (council_run_id, org_id, request_summary, mode, status, avatar_roster, context_summary, created_by)
        VALUES ($1, $2, $3, $4, 'queued', $5, $6, $7)
        "#,
    )
    .bind(council_run_id)
    .bind(org_id)
    .bind(request_summary)
    .bind(mode)
    .bind(avatar_roster)
    .bind(context_summary)
    .bind(created_by)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn get_council_orchestration_run(
    pool: &PgPool,
    council_run_id: &str,
    org_id: uuid::Uuid,
) -> Result<Option<CouncilOrchestrationRun>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CouncilOrchestrationRun>(
        r#"
        SELECT council_run_id, org_id, harness_run_id, request_summary, mode, status,
               avatar_roster, context_summary, synthesis, final_artifact_id,
               error_message, created_by, started_at, completed_at, created_at, updated_at
        FROM council_orchestration_runs
        WHERE council_run_id = $1 AND org_id = $2
        "#,
    )
    .bind(council_run_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(rows)
}

pub async fn list_council_orchestration_runs(
    pool: &PgPool,
    org_id: uuid::Uuid,
    limit: i64,
) -> Result<Vec<CouncilOrchestrationRun>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CouncilOrchestrationRun>(
        r#"
        SELECT council_run_id, org_id, harness_run_id, request_summary, mode, status,
               avatar_roster, context_summary, synthesis, final_artifact_id,
               error_message, created_by, started_at, completed_at, created_at, updated_at
        FROM council_orchestration_runs
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        "#,
    )
    .bind(org_id)
    .bind(limit)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn update_council_orchestration_status(
    pool: &PgPool,
    council_run_id: &str,
    org_id: uuid::Uuid,
    status: &str,
    started_at: Option<chrono::DateTime<chrono::Utc>>,
    completed_at: Option<chrono::DateTime<chrono::Utc>>,
    error_message: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE council_orchestration_runs
        SET status = $1,
            started_at = COALESCE($2, started_at),
            completed_at = COALESCE($3, completed_at),
            error_message = COALESCE($4, error_message),
            updated_at = now()
        WHERE council_run_id = $5 AND org_id = $6
        "#,
    )
    .bind(status)
    .bind(started_at)
    .bind(completed_at)
    .bind(error_message)
    .bind(council_run_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn update_council_orchestration_synthesis(
    pool: &PgPool,
    council_run_id: &str,
    org_id: uuid::Uuid,
    synthesis: &serde_json::Value,
    final_artifact_id: Option<&str>,
    harness_run_id: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE council_orchestration_runs
        SET synthesis = $1,
            final_artifact_id = COALESCE($2, final_artifact_id),
            harness_run_id = COALESCE($3, harness_run_id),
            updated_at = now()
        WHERE council_run_id = $4 AND org_id = $5
        "#,
    )
    .bind(synthesis)
    .bind(final_artifact_id)
    .bind(harness_run_id)
    .bind(council_run_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

// --- COUNCIL AVATAR TURNS ---

pub async fn create_council_avatar_turn(
    pool: &PgPool,
    turn_id: &str,
    org_id: uuid::Uuid,
    council_run_id: &str,
    avatar_id: &str,
    avatar_key: &str,
    turn_type: &str,
    sequence_number: i32,
    input: &serde_json::Value,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO council_avatar_turns
            (turn_id, org_id, council_run_id, avatar_id, avatar_key, turn_type, sequence_number, input)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        "#,
    )
    .bind(turn_id)
    .bind(org_id)
    .bind(council_run_id)
    .bind(avatar_id)
    .bind(avatar_key)
    .bind(turn_type)
    .bind(sequence_number)
    .bind(input)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn list_council_avatar_turns(
    pool: &PgPool,
    council_run_id: &str,
    org_id: uuid::Uuid,
) -> Result<Vec<CouncilAvatarTurn>, sqlx::Error> {
    let rows = sqlx::query_as::<_, CouncilAvatarTurn>(
        r#"
        SELECT turn_id, org_id, council_run_id, harness_run_id, avatar_id, avatar_key,
               turn_type, sequence_number, status, input, output,
               debate_event_id, instinct_frame_id, presence_id,
               error_message, started_at, completed_at, created_at
        FROM council_avatar_turns
        WHERE council_run_id = $1 AND org_id = $2
        ORDER BY sequence_number ASC
        "#,
    )
    .bind(council_run_id)
    .bind(org_id)
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

pub async fn update_council_avatar_turn_status(
    pool: &PgPool,
    turn_id: &str,
    org_id: uuid::Uuid,
    status: &str,
    output: Option<&serde_json::Value>,
    debate_event_id: Option<&str>,
    instinct_frame_id: Option<&str>,
    presence_id: Option<&str>,
    error_message: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE council_avatar_turns
        SET status = $1,
            output = COALESCE($2, output),
            debate_event_id = COALESCE($3, debate_event_id),
            instinct_frame_id = COALESCE($4, instinct_frame_id),
            presence_id = COALESCE($5, presence_id),
            error_message = COALESCE($6, error_message),
            completed_at = CASE WHEN $1 IN ('completed','failed') THEN now() ELSE completed_at END,
            started_at = CASE WHEN $1 = 'in_progress' AND started_at IS NULL THEN now() ELSE started_at END
        WHERE turn_id = $7 AND org_id = $8
        "#,
    )
    .bind(status)
    .bind(output)
    .bind(debate_event_id)
    .bind(instinct_frame_id)
    .bind(presence_id)
    .bind(error_message)
    .bind(turn_id)
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

// ────────────────────────────────────────────────────────────────
// Ripple memory retrieval for avatar working memory
// ────────────────────────────────────────────────────────────────

/// A single ripple summary fetched for an avatar's working memory.
/// Queried by joining avatar_memory_edges → ripples, ordered by edge salience.
#[derive(Debug, FromRow)]
pub struct AvatarRippleSummary {
    pub ripple_id: String,
    pub summary_text: String,
    pub salience: f64,
}

/// Returns ripples linked to an avatar via avatar_memory_edges,
/// ordered by edge salience (descending), limited to `limit` rows.
///
/// When no memory edges exist for this avatar (fresh org), returns an empty vec.
/// This is the runtime data source for SessionManager::load_working_memory().
pub async fn get_ripples_for_avatar(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
    limit: i64,
) -> Result<Vec<AvatarRippleSummary>, sqlx::Error> {
    sqlx::query_as::<_, AvatarRippleSummary>(
        r#"
        SELECT r.ripple_id,
               r.summary_text,
               COALESCE(ame.salience, r.salience) AS salience
        FROM ripples r
        INNER JOIN avatar_memory_edges ame
            ON r.ripple_id = ame.ripple_id
        WHERE ame.avatar_id = $1
          AND r.org_id = $2
        ORDER BY ame.salience DESC
        LIMIT $3
        "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .bind(limit)
    .fetch_all(pool)
    .await
}

// ────────────────────────────────────────────────────────────────
// Avatar identity persistence queries
// ────────────────────────────────────────────────────────────────

pub async fn get_avatar_identity_state(
    pool: &PgPool,
    org_id: uuid::Uuid,
    avatar_id: &str,
) -> Result<Option<AvatarIdentityState>, sqlx::Error> {
    let row = sqlx::query_as::<_, AvatarIdentityState>(
        r#"
        SELECT identity_state_id, org_id, avatar_id,
               mood_confidence, mood_skepticism, mood_creativity, mood_urgency,
               ego_drift_accumulator,
               total_debates_participated, total_challenges_issued,
               total_challenges_received, total_challenges_won,
               total_syntheses_influenced, personality_summary,
               updated_at, created_at
        FROM avatar_identity_states
        WHERE avatar_id = $1 AND org_id = $2
        "#,
    )
    .bind(avatar_id)
    .bind(org_id)
    .fetch_optional(pool)
    .await?;
    Ok(row)
}

pub struct AvatarIdentityStateUpsert<'a> {
    pub identity_state_id: &'a str,
    pub org_id: uuid::Uuid,
    pub avatar_id: &'a str,
    pub mood_confidence: f64,
    pub mood_skepticism: f64,
    pub mood_creativity: f64,
    pub mood_urgency: f64,
    pub ego_drift_accumulator: &'a serde_json::Value,
    pub total_debates_participated: i32,
    pub total_challenges_issued: i32,
    pub total_challenges_received: i32,
    pub total_challenges_won: i32,
    pub total_syntheses_influenced: i32,
    pub personality_summary: &'a str,
}

pub async fn upsert_avatar_identity_state(
    pool: &PgPool,
    state: AvatarIdentityStateUpsert<'_>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_identity_states (
            identity_state_id, org_id, avatar_id,
            mood_confidence, mood_skepticism, mood_creativity, mood_urgency,
            ego_drift_accumulator,
            total_debates_participated, total_challenges_issued,
            total_challenges_received, total_challenges_won,
            total_syntheses_influenced, personality_summary
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        ON CONFLICT (org_id, avatar_id) DO UPDATE SET
            mood_confidence = EXCLUDED.mood_confidence,
            mood_skepticism = EXCLUDED.mood_skepticism,
            mood_creativity = EXCLUDED.mood_creativity,
            mood_urgency = EXCLUDED.mood_urgency,
            ego_drift_accumulator = EXCLUDED.ego_drift_accumulator,
            total_debates_participated = EXCLUDED.total_debates_participated,
            total_challenges_issued = EXCLUDED.total_challenges_issued,
            total_challenges_received = EXCLUDED.total_challenges_received,
            total_challenges_won = EXCLUDED.total_challenges_won,
            total_syntheses_influenced = EXCLUDED.total_syntheses_influenced,
            personality_summary = EXCLUDED.personality_summary,
            updated_at = now()
        "#,
    )
    .bind(state.identity_state_id)
    .bind(state.org_id)
    .bind(state.avatar_id)
    .bind(state.mood_confidence)
    .bind(state.mood_skepticism)
    .bind(state.mood_creativity)
    .bind(state.mood_urgency)
    .bind(state.ego_drift_accumulator)
    .bind(state.total_debates_participated)
    .bind(state.total_challenges_issued)
    .bind(state.total_challenges_received)
    .bind(state.total_challenges_won)
    .bind(state.total_syntheses_influenced)
    .bind(state.personality_summary)
    .execute(pool)
    .await?;
    Ok(())
}

pub async fn create_avatar_experience(
    pool: &PgPool,
    experience_id: &str,
    org_id: uuid::Uuid,
    avatar_id: &str,
    experience_type: &str,
    summary: &str,
    outcome: &str,
    salience: f64,
    related_avatar_key: Option<&str>,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO avatar_experience_log (
            experience_id, org_id, avatar_id, experience_type,
            summary, outcome, salience, related_avatar_key
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        "#,
    )
    .bind(experience_id)
    .bind(org_id)
    .bind(avatar_id)
    .bind(experience_type)
    .bind(summary)
    .bind(outcome)
    .bind(salience)
    .bind(related_avatar_key)
    .execute(pool)
    .await?;
    Ok(())
}
