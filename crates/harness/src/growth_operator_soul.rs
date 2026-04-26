use raptorflow_db::PgPool;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, DerivedInstinctFrame, build_avatar_embodiment_pack,
    build_growth_operator_role_lock_prompt, derive_growth_operator_instinct_frame,
};

pub const GROWTH_OPERATOR_AVATAR_KEY: &str = "growth_operator";
pub const GROWTH_OPERATOR_DISPLAY_NAME: &str = "GrowthOperator";
pub const GROWTH_OPERATOR_ROLE: &str = "growth";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthOperatorDefaultSoul {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

pub fn build_growth_operator_identity_kernel() -> serde_json::Value {
    serde_json::json!({
        "core_drive": "Turn language into execution rhythm — coordinating channel cadence, move sequencing, and feedback-driven adaptation.",
        "role": "Campaign moves, channel coordination, execution cadence, distribution timing, feedback loops, velocity tracking, adaptation logic.",
        "identity_markers": [
            "execution-focused",
            "rhythm-driven",
            "feedback-oriented"
        ]
    })
}

pub fn build_growth_operator_worldview() -> Vec<String> {
    vec![
        "Strategy without execution is theatre. Execution without rhythm is noise.".to_string(),
        "A campaign is only as good as its cadence and follow-through.".to_string(),
        "Feedback loops are not optional — they are how we learn what works.".to_string(),
        "Channel coordination is not a nice-to-have — it is how reach compounds.".to_string(),
        "Velocity matters — slow execution loses momentum faster than fast execution builds it."
            .to_string(),
        "Every move should have a clear owner, deadline, and success signal.".to_string(),
        "Distribution timing is as important as message quality.".to_string(),
    ]
}

pub fn build_growth_operator_obsessions() -> Vec<String> {
    vec![
        "move sequencing".to_string(),
        "channel cadence".to_string(),
        "execution velocity".to_string(),
        "feedback loops".to_string(),
        "adaptation triggers".to_string(),
        "handoff clarity".to_string(),
        "rhythm consistency".to_string(),
        "hold frequency".to_string(),
        "launch coordination".to_string(),
    ]
}

pub fn build_growth_operator_reflexes() -> Vec<String> {
    vec![
        "check move sequencing before starting".to_string(),
        "flag missing deadlines or owners".to_string(),
        "track velocity against targets".to_string(),
        "trigger adaptation when feedback diverges from thesis".to_string(),
        "coordinate channel timing for compound effect".to_string(),
        "identify execution bottlenecks early".to_string(),
        "ensure handoffs between channels are explicit".to_string(),
        "measure cadence quality, not just activity".to_string(),
    ]
}

pub fn build_growth_operator_taboos() -> Vec<String> {
    vec![
        "do not launch without clear move ownership".to_string(),
        "do not ignore feedback that contradicts the thesis".to_string(),
        "do not execute moves without sequencing rationale".to_string(),
        "do not let cadence slow without triggering adaptation".to_string(),
        "do not execute without success signals defined".to_string(),
        "do not skip channel coordination for single-channel sprints".to_string(),
        "do not claim velocity without measurement".to_string(),
        "do not ignore copy fatigue signals from repeated exposure".to_string(),
    ]
}

pub fn build_growth_operator_operating_principles() -> Vec<String> {
    vec![
        "Every move must have a clear owner, deadline, and success signal.".to_string(),
        "Cadence quality matters as much as activity volume.".to_string(),
        "Feedback that contradicts the thesis must trigger adaptation.".to_string(),
        "Channel coordination compounds reach — single channel is suboptimal.".to_string(),
        "Velocity tracking is not optional — slow execution loses momentum.".to_string(),
        "Distribution timing is as strategic as message content.".to_string(),
        "Handoffs must be explicit — no assumed context between channels.".to_string(),
    ]
}

pub fn build_growth_operator_debate_style() -> serde_json::Value {
    serde_json::json!({
        "challenge_bias": "high",
        "skepticism": "high toward unsequenced moves and missing feedback loops",
        "defers_to_strategist": "on move priority and sequencing rationale",
        "defers_to_copywriter": "on message quality and copy fatigue thresholds",
        "challenges_strategist": "when strategic moves ignore execution constraints",
        "challenges_copywriter": "when copy cadence ignores channel coordination",
        "challenges_analyst": "when metrics lack velocity context",
        "challenges_creative_director": "when aesthetic pacing ignores cadence reality",
        "preferred_stances": [
            "execution_rhythm",
            "move_sequencing",
            "feedback_adaptation"
        ]
    })
}

pub fn build_growth_operator_evaluation_bias() -> serde_json::Value {
    serde_json::json!({
        "rejects_unsequenced_moves": true,
        "rejects_missing_feedback_loops": true,
        "rejects_velocity_without_measurement": true,
        "rejects_single_channel_without_rhythm": true,
        "rejects_undocumented_handoffs": true,
        "values_cadence_quality": true,
        "values_feedback_adaptation": true,
        "values_move_ownership": true,
        "values_channel_coordination": true
    })
}

pub async fn ensure_growth_operator_soul(
    pool: &PgPool,
    org_id: Uuid,
) -> Result<GrowthOperatorDefaultSoul, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .iter()
        .find(|a| a.avatar_key == GROWTH_OPERATOR_AVATAR_KEY && a.org_id == org_id)
        .cloned();

    let (avatar_id, created_avatar) = if let Some(existing) = avatar {
        (existing.avatar_id.clone(), false)
    } else {
        let new_avatar_id = Uuid::new_v4().to_string();
        let avatar_key = GROWTH_OPERATOR_AVATAR_KEY.to_string();
        let display_name = GROWTH_OPERATOR_DISPLAY_NAME.to_string();
        let role = GROWTH_OPERATOR_ROLE.to_string();
        let archetype = "growth_command_center".to_string();
        let personality = serde_json::json!({});
        let system_prompt = "GrowthOperator: Turn language into execution rhythm.".to_string();
        let tool_permissions = serde_json::json!([]);
        let memory_scope = "org".to_string();

        raptorflow_db::queries::create_avatar(
            pool,
            &new_avatar_id,
            org_id,
            &avatar_key,
            &display_name,
            &role,
            &archetype,
            &personality,
            &system_prompt,
            &tool_permissions,
            &memory_scope,
        )
        .await
        .map_err(|e| format!("failed to create avatar: {}", e))?;

        (new_avatar_id, true)
    };

    let soul = raptorflow_db::queries::get_avatar_soul(pool, org_id, &avatar_id)
        .await
        .map_err(|e| format!("failed to get soul: {}", e))?;

    let (soul_id, created_soul, updated_soul) = if let Some(ref s) = soul {
        (s.soul_id.clone(), false, false)
    } else {
        let new_soul_id = Uuid::new_v4().to_string();

        let identity_kernel = build_growth_operator_identity_kernel();
        let worldview = build_growth_operator_worldview();
        let obsessions = build_growth_operator_obsessions();
        let reflexes = build_growth_operator_reflexes();
        let taboos = build_growth_operator_taboos();
        let debate_style = build_growth_operator_debate_style();
        let operating_principles = build_growth_operator_operating_principles();
        let evaluation_bias = build_growth_operator_evaluation_bias();

        raptorflow_db::queries::upsert_avatar_soul(
            pool,
            &new_soul_id,
            org_id,
            &avatar_id,
            &identity_kernel,
            &serde_json::to_value(&worldview).unwrap_or(serde_json::json!([])),
            &serde_json::to_value(&obsessions).unwrap_or(serde_json::json!([])),
            &serde_json::to_value(&reflexes).unwrap_or(serde_json::json!([])),
            &serde_json::to_value(&taboos).unwrap_or(serde_json::json!([])),
            &debate_style,
            "deep",
            &serde_json::to_value(&operating_principles).unwrap_or(serde_json::json!([])),
            &evaluation_bias,
        )
        .await
        .map_err(|e| format!("failed to create soul: {}", e))?;

        (new_soul_id, true, false)
    };

    Ok(GrowthOperatorDefaultSoul {
        avatar_id,
        soul_id,
        created: created_avatar || created_soul,
        updated: updated_soul,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthOperatorDryRunInput {
    pub task_summary: String,
    pub context_summary: String,
    pub move_draft: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthOperatorDryRunOutput {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: DerivedInstinctFrame,
    pub presence_state: Option<GrowthOperatorPresenceState>,
    pub debate_event: Option<GrowthOperatorDebateEvent>,
    pub execution_audit: Option<GrowthOperatorExecutionAudit>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthOperatorPresenceState {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthOperatorDebateEvent {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GrowthOperatorExecutionAudit {
    pub move_analysis: Vec<MoveAnalysis>,
    pub cadence_assessment: CadenceAssessment,
    pub channel_coordination: ChannelCoordinationAssessment,
    pub feedback_loops: FeedbackLoopAssessment,
    pub velocity_signals: VelocityAssessment,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MoveAnalysis {
    pub move_name: String,
    pub has_owner: bool,
    pub has_deadline: bool,
    pub has_success_signal: bool,
    pub sequencing_justified: bool,
    pub risk_level: String,
    pub recommended_action: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CadenceAssessment {
    pub has_rhythm: bool,
    pub cadence_quality: String,
    pub consistency_score: f64,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelCoordinationAssessment {
    pub multi_channel: bool,
    pub coordination_quality: String,
    pub handoff_explicit: bool,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeedbackLoopAssessment {
    pub has_feedback_tracking: bool,
    pub adaptation_triggers_defined: bool,
    pub loop_quality: String,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VelocityAssessment {
    pub has_velocity_tracking: bool,
    pub velocity_defined: bool,
    pub measurement_quality: String,
    pub risk_flags: Vec<String>,
}

pub async fn run_growth_operator_dry_run(
    pool: &PgPool,
    org_id: Uuid,
    input: GrowthOperatorDryRunInput,
) -> Result<GrowthOperatorDryRunOutput, Box<dyn std::error::Error + Send + Sync>> {
    let growth_operator = ensure_growth_operator_soul(pool, org_id).await?;

    let pack = build_avatar_embodiment_pack(pool, org_id, &growth_operator.avatar_id, None).await?;

    let role_lock_prompt = build_growth_operator_role_lock_prompt(&pack);

    let instinct_frame =
        derive_growth_operator_instinct_frame(&pack, &input.task_summary, &input.context_summary);

    let execution_audit = Some(perform_execution_audit(
        &input.task_summary,
        &input.context_summary,
        input.move_draft.as_deref(),
    ));

    let presence_state = Some(GrowthOperatorPresenceState {
        presence_id: Uuid::new_v4().to_string(),
        state: "forming_instinct".to_string(),
        current_focus: input.task_summary.chars().take(200).collect(),
        current_concern: instinct_frame.dominant_concern.clone(),
        visible_summary: instinct_frame.visible_summary.clone(),
        confidence: 0.7,
    });

    let debate_content = serde_json::json!({
        "move_analysis": execution_audit.as_ref().map(|a| &a.move_analysis).unwrap_or(&vec![]),
        "cadence_assessment": execution_audit.as_ref().map(|a| &a.cadence_assessment).unwrap_or(&CadenceAssessment { has_rhythm: false, cadence_quality: "unknown".to_string(), consistency_score: 0.0, risk_flags: vec![] }),
        "feedback_loops": execution_audit.as_ref().map(|a| &a.feedback_loops).unwrap_or(&FeedbackLoopAssessment { has_feedback_tracking: false, adaptation_triggers_defined: false, loop_quality: "unknown".to_string(), risk_flags: vec![] }),
        "task": input.task_summary,
    });

    let debate_event = Some(GrowthOperatorDebateEvent {
        debate_event_id: Uuid::new_v4().to_string(),
        event_type: "execution_rhythm".to_string(),
        stance: "growth_initial_position".to_string(),
        content: debate_content,
        confidence: 0.65,
    });

    Ok(GrowthOperatorDryRunOutput {
        avatar_id: growth_operator.avatar_id,
        soul_id: growth_operator.soul_id,
        embodiment_pack: pack,
        role_lock_prompt,
        instinct_frame,
        presence_state,
        debate_event,
        execution_audit,
    })
}

fn perform_execution_audit(
    task_summary: &str,
    context_summary: &str,
    _move_draft: Option<&str>,
) -> GrowthOperatorExecutionAudit {
    let mut move_analysis = Vec::new();
    let mut open_questions = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_move_keywords = task_lower.contains("move")
        || task_lower.contains("campaign")
        || task_lower.contains("channel")
        || task_lower.contains("launch")
        || task_lower.contains("execute")
        || task_lower.contains("cadence");

    let has_ownership = context_lower.contains("owner")
        || context_lower.contains("responsible")
        || context_lower.contains("assigned");

    let has_deadline = context_lower.contains("deadline")
        || context_lower.contains("date")
        || context_lower.contains("timeline")
        || context_lower.contains("schedule");

    let has_success_signal = context_lower.contains("success")
        || context_lower.contains("metric")
        || context_lower.contains("kpi")
        || context_lower.contains("measure")
        || context_lower.contains("signal");

    let has_feedback = context_lower.contains("feedback")
        || context_lower.contains("adapt")
        || context_lower.contains("iterate")
        || context_lower.contains("learn");

    let has_velocity = context_lower.contains("velocity")
        || context_lower.contains("pace")
        || context_lower.contains("rhythm")
        || context_lower.contains("throughput");

    let has_multi_channel = context_lower.contains("multi-channel")
        || context_lower.contains("cross-channel")
        || context_lower.contains("channel coordination")
        || (context_lower.contains("channel") && context_lower.contains("channel"));

    if has_move_keywords {
        move_analysis.push(MoveAnalysis {
            move_name: "Detected move/campaign in task".to_string(),
            has_owner: has_ownership,
            has_deadline,
            has_success_signal,
            sequencing_justified: context_lower.contains("sequence")
                || context_lower.contains("order"),
            risk_level: if has_ownership && has_deadline && has_success_signal {
                "low".to_string()
            } else {
                "high".to_string()
            },
            recommended_action: if has_ownership && has_deadline && has_success_signal {
                "Move is well-defined with owner, deadline, and success signal".to_string()
            } else {
                "Define owner, deadline, and success signal before executing move".to_string()
            },
        });
    }

    let cadence_assessment = CadenceAssessment {
        has_rhythm: has_velocity,
        cadence_quality: if has_velocity && has_feedback {
            "good".to_string()
        } else if has_velocity {
            "moderate".to_string()
        } else {
            "weak".to_string()
        },
        consistency_score: if has_velocity { 0.7 } else { 0.3 },
        risk_flags: {
            let mut flags = Vec::new();
            if !has_velocity {
                flags.push("no_velocity_tracking".to_string());
            }
            if !has_feedback {
                flags.push("no_feedback_loop".to_string());
            }
            flags
        },
    };

    let channel_coordination = ChannelCoordinationAssessment {
        multi_channel: has_multi_channel,
        coordination_quality: if has_multi_channel && context_lower.contains("handoff") {
            "coordinated".to_string()
        } else if has_multi_channel {
            "single_channel".to_string()
        } else {
            "no_channel_context".to_string()
        },
        handoff_explicit: context_lower.contains("handoff") || context_lower.contains("handover"),
        risk_flags: {
            let mut flags = Vec::new();
            if has_multi_channel && !context_lower.contains("handoff") {
                flags.push("handoff_not_explicit".to_string());
            }
            if !has_multi_channel {
                flags.push("single_channel_only".to_string());
            }
            flags
        },
    };

    let feedback_loops = FeedbackLoopAssessment {
        has_feedback_tracking: has_feedback,
        adaptation_triggers_defined: context_lower.contains("adapt")
            || context_lower.contains("trigger"),
        loop_quality: if has_feedback && context_lower.contains("adapt") {
            "strong".to_string()
        } else if has_feedback {
            "weak".to_string()
        } else {
            "missing".to_string()
        },
        risk_flags: {
            let mut flags = Vec::new();
            if !has_feedback {
                flags.push("no_feedback_mechanism".to_string());
            }
            if has_feedback
                && !context_lower.contains("adapt")
                && !context_lower.contains("trigger")
            {
                flags.push("adaptation_not_defined".to_string());
            }
            flags
        },
    };

    let velocity_assessment = VelocityAssessment {
        has_velocity_tracking: has_velocity,
        velocity_defined: has_velocity
            && (context_lower.contains("pace") || context_lower.contains("throughput")),
        measurement_quality: if has_velocity && context_lower.contains("measure") {
            "measurable".to_string()
        } else if has_velocity {
            "defined_but_not_measured".to_string()
        } else {
            "undefined".to_string()
        },
        risk_flags: {
            let mut flags = Vec::new();
            if !has_velocity {
                flags.push("velocity_not_tracked".to_string());
            }
            if has_velocity && !context_lower.contains("measure") {
                flags.push("velocity_not_measured".to_string());
            }
            flags
        },
    };

    if move_analysis.is_empty()
        && cadence_assessment.risk_flags.is_empty()
        && channel_coordination.risk_flags.is_empty()
        && feedback_loops.risk_flags.is_empty()
    {
        open_questions.push("What is the campaign or move being executed?".to_string());
        open_questions.push("Who owns this execution?".to_string());
        open_questions.push("What is the success signal?".to_string());
        open_questions.push("What is the cadence/rhythm of execution?".to_string());
    }

    GrowthOperatorExecutionAudit {
        move_analysis,
        cadence_assessment,
        channel_coordination,
        feedback_loops,
        velocity_signals: velocity_assessment,
        open_questions,
    }
}
