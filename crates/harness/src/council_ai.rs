use raptorflow_aws::bedrock::BedrockInferenceClient;
use serde::Deserialize;
use tracing::instrument;

use super::avatar_soul::{
    AvatarEmbodimentPack, ChallengeDecision, DerivedInstinctFrame, build_analyst_role_lock_prompt,
    build_copywriter_role_lock_prompt, build_creative_director_role_lock_prompt,
    build_growth_operator_role_lock_prompt, build_proof_collector_role_lock_prompt,
    build_researcher_role_lock_prompt, build_strategist_role_lock_prompt,
};

#[derive(Deserialize)]
struct AiInstinctFrame {
    dominant_concern: String,
    risk_flags: Vec<String>,
    recommended_posture: String,
    visible_summary: String,
}

#[derive(Deserialize)]
struct AiChallengeResponse {
    should_challenge: bool,
    reason: String,
    suggested_event_type: String,
    confidence: f64,
}

#[derive(Deserialize)]
struct AiSynthesisResponse {
    known_facts: Vec<String>,
    assumptions: Vec<String>,
    risks: Vec<String>,
    next_actions: Vec<String>,
    open_questions: Vec<String>,
    strategic_recommendation: String,
}

fn role_lock_for_avatar(pack: &AvatarEmbodimentPack, avatar_key: &str) -> String {
    match avatar_key {
        "strategist" => build_strategist_role_lock_prompt(pack),
        "researcher" => build_researcher_role_lock_prompt(pack),
        "copywriter" => build_copywriter_role_lock_prompt(pack),
        "growth_operator" => build_growth_operator_role_lock_prompt(pack),
        "analyst" => build_analyst_role_lock_prompt(pack),
        "creative_director" => build_creative_director_role_lock_prompt(pack),
        "proof_collector" => build_proof_collector_role_lock_prompt(pack),
        _ => format!(
            "You are {}. Provide your strategic input.",
            pack.display_name
        ),
    }
}

#[instrument(skip(bedrock, pack), fields(avatar = avatar_key))]
pub async fn ai_derive_instinct(
    bedrock: &BedrockInferenceClient,
    pack: &AvatarEmbodimentPack,
    avatar_key: &str,
    task_summary: &str,
    context_summary: &str,
) -> Option<DerivedInstinctFrame> {
    let role_lock = role_lock_for_avatar(pack, avatar_key);

    let prompt = format!(
        r#"{}

Given the following task and context, determine your instinct frame.

TASK: {}
CONTEXT: {}

Respond as JSON only:
{{"dominant_concern": "your primary concern as this avatar",
  "risk_flags": ["risk1", "risk2"],
  "recommended_posture": "your recommended stance",
  "visible_summary": "one-line summary visible to other avatars"}}
"#,
        role_lock,
        truncate_context(task_summary, 500),
        truncate_context(context_summary, 2000),
    );

    let parsed: AiInstinctFrame = bedrock
        .converse_json(&bedrock.fast_model(), &prompt, 600)
        .await
        .ok()?;

    if parsed.dominant_concern.len() < 10 || parsed.visible_summary.len() < 5 {
        return None;
    }

    Some(DerivedInstinctFrame {
        instinct_frame_id: uuid::Uuid::new_v4().to_string(),
        dominant_concern: parsed.dominant_concern,
        risk_flags: parsed.risk_flags.into_iter().take(5).collect(),
        recommended_posture: parsed.recommended_posture,
        visible_summary: parsed.visible_summary,
    })
}

#[instrument(skip(bedrock, pack), fields(avatar = avatar_key, target = target_avatar_key))]
pub async fn ai_evaluate_challenge(
    bedrock: &BedrockInferenceClient,
    pack: &AvatarEmbodimentPack,
    avatar_key: &str,
    target_avatar_key: &str,
    position_text: &str,
) -> Option<ChallengeDecision> {
    let role_lock = role_lock_for_avatar(pack, avatar_key);

    let prompt = format!(
        r#"{}

Review this position from {}:

POSITION: {}

Should you challenge this? If so, explain why.

Respond as JSON only:
{{"should_challenge": true/false,
  "reason": "why you challenge or why not",
  "suggested_event_type": "challenge" or "none",
  "confidence": 0.0-1.0}}
"#,
        role_lock,
        target_avatar_key,
        truncate_context(position_text, 1500),
    );

    let parsed: AiChallengeResponse = bedrock
        .converse_json(&bedrock.fast_model(), &prompt, 400)
        .await
        .ok()?;

    let confidence = parsed.confidence.clamp(0.0, 1.0);
    if confidence < 0.3 {
        return None;
    }

    Some(ChallengeDecision {
        should_challenge: parsed.should_challenge,
        reason: parsed.reason,
        suggested_event_type: parsed.suggested_event_type,
        confidence,
    })
}

#[instrument(skip(bedrock))]
pub async fn ai_synthesize(
    bedrock: &BedrockInferenceClient,
    task_summary: &str,
    context_summary: &str,
    debate_summary: &str,
) -> Option<serde_json::Value> {
    let prompt = format!(
        r#"You are the Strategist — the synthesis authority for a multi-avatar council.
Synthesize the following debate into a strategic decision.

TASK: {}
CONTEXT: {}

COUNCIL DEBATE:
{}

Respond as JSON only:
{{"known_facts": ["fact1", "fact2"],
  "assumptions": ["assumption1"],
  "risks": ["risk1", "risk2"],
  "next_actions": ["action1", "action2"],
  "open_questions": ["question1"],
  "strategic_recommendation": "clear strategic direction"}}
"#,
        truncate_context(task_summary, 300),
        truncate_context(context_summary, 1000),
        truncate_context(debate_summary, 3000),
    );

    let parsed: AiSynthesisResponse = bedrock
        .converse_json(&bedrock.strategist_model(), &prompt, 1200)
        .await
        .ok()?;

    if parsed.strategic_recommendation.len() < 10 {
        return None;
    }

    Some(serde_json::json!({
        "known_facts": parsed.known_facts,
        "assumptions": parsed.assumptions,
        "risks": parsed.risks,
        "next_actions": parsed.next_actions,
        "open_questions": parsed.open_questions,
        "strategic_recommendation": parsed.strategic_recommendation,
        "synthesized_by": "ai",
    }))
}

fn truncate_context(text: &str, max_chars: usize) -> String {
    if text.len() <= max_chars {
        text.to_string()
    } else {
        let boundary = text.floor_char_boundary(max_chars);
        format!(
            "{}...[{} chars truncated]",
            &text[..boundary],
            text.len() - boundary
        )
    }
}
