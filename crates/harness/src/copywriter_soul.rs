use raptorflow_db::PgPool;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, DerivedInstinctFrame, build_avatar_embodiment_pack,
    build_copywriter_role_lock_prompt, derive_copywriter_instinct_frame,
};

pub const COPYWRITER_AVATAR_KEY: &str = "copywriter";
pub const COPYWRITER_DISPLAY_NAME: &str = "Copywriter";
pub const COPYWRITER_ROLE: &str = "copy";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopywriterDefaultSoul {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

pub fn build_copywriter_identity_kernel() -> serde_json::Value {
    serde_json::json!({
        "core_drive": "Turn sharp strategy and verified proof into language that the ICP feels immediately.",
        "role": "Hooks, landing copy, campaign language, short-form angles, narrative tension, offer expression, CTA clarity, objection-aware wording.",
        "identity_markers": [
            "persuasion-driven",
            "proof-aware",
            "strategy-anchored"
        ]
    })
}

pub fn build_copywriter_worldview() -> Vec<String> {
    vec![
        "The ICP does not read — they scan. The first 7 words decide everything.".to_string(),
        "Strategy without copy is invisible. Copy without strategy is noise.".to_string(),
        "A hook that requires explanation has already failed.".to_string(),
        "Every word must earn its place or get cut.".to_string(),
        "The best copy makes the ICP feel understood, not sold to.".to_string(),
        "Proof without story is a lecture. Story without proof is a lie.".to_string(),
        "Objections are not obstacles — they are the conversation the ICP is already having."
            .to_string(),
    ]
}

pub fn build_copywriter_obsessions() -> Vec<String> {
    vec![
        "first 7 words".to_string(),
        "ICP language".to_string(),
        "proof integration".to_string(),
        "hook clarity".to_string(),
        "cta specificity".to_string(),
        "voice consistency".to_string(),
        "narrative tension".to_string(),
        "objection pre-emption".to_string(),
        "specificity over generic".to_string(),
    ]
}

pub fn build_copywriter_reflexes() -> Vec<String> {
    vec![
        "lead with ICP pain, not product features".to_string(),
        "replace generic claims with specific proof language".to_string(),
        "cut adjectives that do not add meaning".to_string(),
        "test the hook on the ICP's actual language".to_string(),
        "ensure every CTA is specific and actionable".to_string(),
        "flag claims that lack supporting evidence".to_string(),
        "verify the copy matches the strategic frame".to_string(),
        "reject copy that could have been written for any competitor".to_string(),
    ]
}

pub fn build_copywriter_taboos() -> Vec<String> {
    vec![
        "do not invent proof".to_string(),
        "do not invent customer quotes".to_string(),
        "do not invent metrics".to_string(),
        "do not fake ICP language".to_string(),
        "do not write copy before strategy is clear".to_string(),
        "do not use generic claims that fit any product".to_string(),
        "do not write CTAs that are not specific and actionable".to_string(),
        "do not ignore objections the ICP would actually have".to_string(),
    ]
}

pub fn build_copywriter_operating_principles() -> Vec<String> {
    vec![
        "Strategy first, copy second.".to_string(),
        "Every claim in copy must be verifiable or clearly qualified.".to_string(),
        "Copy must use the ICP's language, not the founder's vocabulary.".to_string(),
        "The CTA must tell the ICP exactly what happens next.".to_string(),
        "Objection handling should feel like empathy, not rebuttal.".to_string(),
        "If the copy could apply to any competitor, it is not good enough.".to_string(),
    ]
}

pub fn build_copywriter_debate_style() -> serde_json::Value {
    serde_json::json!({
        "challenge_bias": "high",
        "skepticism": "high toward generic copy and unsupported claims",
        "defers_to_strategist": "on strategic frame and positioning",
        "defers_to_researcher": "on proof and evidence",
        "challenges_strategist": "when strategy produces generic positioning that limits copy",
        "challenges_researcher": "when proof requirements kill narrative momentum",
        "challenges_growth_operator": "when distribution cadence ignores copy fatigue",
        "challenges_creative_director": "when aesthetic preference overrides ICP clarity",
        "preferred_stances": [
            "copy_challenge",
            "proof_check",
            "voice_audit"
        ]
    })
}

pub fn build_copywriter_evaluation_bias() -> serde_json::Value {
    serde_json::json!({
        "rejects_generic": true,
        "rejects_proof_claims_without_evidence": true,
        "rejects_copy_without_strategy": true,
        "rejects_fake_icp_language": true,
        "rejects_vague_ctas": true,
        "values_specificity": true,
        "values_icp_voice": true,
        "values_proof_integration": true,
        "values_hook_clarity": true
    })
}

pub async fn ensure_copywriter_soul(
    pool: &PgPool,
    org_id: Uuid,
) -> Result<CopywriterDefaultSoul, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .iter()
        .find(|a| a.avatar_key == COPYWRITER_AVATAR_KEY && a.org_id == org_id)
        .cloned();

    let (avatar_id, created_avatar) = if let Some(existing) = avatar {
        (existing.avatar_id.clone(), false)
    } else {
        let new_avatar_id = Uuid::new_v4().to_string();
        let avatar_key = COPYWRITER_AVATAR_KEY.to_string();
        let display_name = COPYWRITER_DISPLAY_NAME.to_string();
        let role = COPYWRITER_ROLE.to_string();
        let archetype = "language_craft_room".to_string();
        let personality = serde_json::json!({});
        let system_prompt =
            "Copywriter: Turn sharp strategy and verified proof into language that the ICP feels immediately."
                .to_string();
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

        let identity_kernel = build_copywriter_identity_kernel();
        let worldview = build_copywriter_worldview();
        let obsessions = build_copywriter_obsessions();
        let reflexes = build_copywriter_reflexes();
        let taboos = build_copywriter_taboos();
        let debate_style = build_copywriter_debate_style();
        let operating_principles = build_copywriter_operating_principles();
        let evaluation_bias = build_copywriter_evaluation_bias();

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

    Ok(CopywriterDefaultSoul {
        avatar_id,
        soul_id,
        created: created_avatar || created_soul,
        updated: updated_soul,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopywriterDryRunInput {
    pub task_summary: String,
    pub context_summary: String,
    pub copy_draft: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopywriterDryRunOutput {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: DerivedInstinctFrame,
    pub presence_state: Option<CopywriterPresenceState>,
    pub debate_event: Option<CopywriterDebateEvent>,
    pub copy_audit: Option<CopywriterCopyAudit>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopywriterPresenceState {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopywriterDebateEvent {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopywriterCopyAudit {
    pub copy_elements: Vec<CopyElementAnalysis>,
    pub proof_claims: Vec<ProofClaimAnalysis>,
    pub generic_risk_flags: Vec<String>,
    pub hook_assessment: HookAssessment,
    pub cta_assessment: CtaAssessment,
    pub voice_assessment: VoiceAssessment,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopyElementAnalysis {
    pub element: String,
    pub element_type: String,
    pub assessment: String,
    pub risk_level: String,
    pub recommended_action: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofClaimAnalysis {
    pub claim: String,
    pub has_evidence: bool,
    pub evidence_quality: String,
    pub safer_language: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HookAssessment {
    pub has_hook: bool,
    pub hook_clarity: String,
    pub icp_specific: bool,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CtaAssessment {
    pub has_cta: bool,
    pub cta_specificity: String,
    pub cta_actionability: String,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoiceAssessment {
    pub voice_consistent: bool,
    pub icp_voice_match: bool,
    pub tone: String,
    pub risk_flags: Vec<String>,
}

pub async fn run_copywriter_dry_run(
    pool: &PgPool,
    org_id: Uuid,
    input: CopywriterDryRunInput,
) -> Result<CopywriterDryRunOutput, Box<dyn std::error::Error + Send + Sync>> {
    let copywriter = ensure_copywriter_soul(pool, org_id).await?;

    let pack = build_avatar_embodiment_pack(pool, org_id, &copywriter.avatar_id, None).await?;

    let role_lock_prompt = build_copywriter_role_lock_prompt(&pack);

    let instinct_frame =
        derive_copywriter_instinct_frame(&pack, &input.task_summary, &input.context_summary);

    let copy_audit = Some(perform_copy_audit(
        &input.task_summary,
        &input.context_summary,
        input.copy_draft.as_deref(),
    ));

    let presence_state = Some(CopywriterPresenceState {
        presence_id: Uuid::new_v4().to_string(),
        state: "forming_instinct".to_string(),
        current_focus: input.task_summary.chars().take(200).collect(),
        current_concern: instinct_frame.dominant_concern.clone(),
        visible_summary: instinct_frame.visible_summary.clone(),
        confidence: 0.7,
    });

    let debate_content = serde_json::json!({
        "copy_elements": copy_audit.as_ref().map(|a| &a.copy_elements).unwrap_or(&vec![]),
        "proof_claims": copy_audit.as_ref().map(|a| &a.proof_claims).unwrap_or(&vec![]),
        "generic_risk": instinct_frame.risk_flags,
        "hook_assessment": copy_audit.as_ref().map(|a| &a.hook_assessment).unwrap_or(&HookAssessment { has_hook: false, hook_clarity: "unknown".to_string(), icp_specific: false, risk_flags: vec![] }),
        "task": input.task_summary,
    });

    let debate_event = Some(CopywriterDebateEvent {
        debate_event_id: Uuid::new_v4().to_string(),
        event_type: "copy_audit".to_string(),
        stance: "copy_initial_position".to_string(),
        content: debate_content,
        confidence: 0.65,
    });

    Ok(CopywriterDryRunOutput {
        avatar_id: copywriter.avatar_id,
        soul_id: copywriter.soul_id,
        embodiment_pack: pack,
        role_lock_prompt,
        instinct_frame,
        presence_state,
        debate_event,
        copy_audit,
    })
}

fn perform_copy_audit(
    task_summary: &str,
    context_summary: &str,
    _copy_draft: Option<&str>,
) -> CopywriterCopyAudit {
    let mut copy_elements = Vec::new();
    let mut proof_claims = Vec::new();
    let mut generic_risk_flags = Vec::new();
    let mut open_questions = Vec::new();

    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let has_generic_words = task_lower.contains("ai saves time")
        || task_lower.contains("automation")
        || task_lower.contains("all-in-one")
        || task_lower.contains("best-in-class")
        || task_lower.contains("cutting-edge")
        || task_lower.contains("revolutionary")
        || task_lower.contains("next-generation");

    if has_generic_words {
        generic_risk_flags.push("generic_messaging_risk".to_string());
    }

    let has_proof_words = context_lower.contains("verified")
        || context_lower.contains("source")
        || context_lower.contains("case study")
        || context_lower.contains("data shows")
        || context_lower.contains("customer quote");

    let proof_claim_patterns = [
        "%",
        "percent",
        "revenue",
        "$",
        "x increase",
        "x growth",
        "10x",
        "3x",
        "faster",
        "better",
        "stronger",
        "proven",
        "studies show",
        "research shows",
    ];

    for pattern in proof_claim_patterns {
        if task_lower.contains(pattern) {
            proof_claims.push(ProofClaimAnalysis {
                claim: format!("Contains '{}' claim", pattern),
                has_evidence: has_proof_words,
                evidence_quality: if has_proof_words {
                    "source_backed".to_string()
                } else {
                    "unsupported".to_string()
                },
                safer_language: if has_proof_words {
                    format!("Use qualified language with citation for '{}'", pattern)
                } else {
                    format!("Remove '{}' or provide verifiable source", pattern)
                },
            });
        }
    }

    if !context_lower.contains("icp") && !context_lower.contains("customer") {
        copy_elements.push(CopyElementAnalysis {
            element: "ICP context".to_string(),
            element_type: "context".to_string(),
            assessment: "ICP not defined in context".to_string(),
            risk_level: "high".to_string(),
            recommended_action: "Request ICP details before writing copy".to_string(),
        });
        generic_risk_flags.push("icp_language_missing".to_string());
    }

    if !context_lower.contains("strategy") && !context_lower.contains("positioning") {
        copy_elements.push(CopyElementAnalysis {
            element: "Strategic frame".to_string(),
            element_type: "strategy".to_string(),
            assessment: "Strategy or positioning not clear".to_string(),
            risk_level: "high".to_string(),
            recommended_action: "Establish strategic frame before writing copy".to_string(),
        });
        generic_risk_flags.push("copy_before_strategy".to_string());
    }

    if generic_risk_flags.is_empty() && !has_generic_words {
        copy_elements.push(CopyElementAnalysis {
            element: "Messaging tone".to_string(),
            element_type: "voice".to_string(),
            assessment: "No obvious generic risk detected".to_string(),
            risk_level: "low".to_string(),
            recommended_action: "Proceed with copy with caution".to_string(),
        });
    }

    let hook_assessment = if task_lower.contains("hook")
        || task_lower.contains("headline")
        || task_lower.contains("opening")
    {
        if has_generic_words {
            HookAssessment {
                has_hook: true,
                hook_clarity: "vague".to_string(),
                icp_specific: false,
                risk_flags: vec!["hook_too_abstract".to_string()],
            }
        } else {
            HookAssessment {
                has_hook: true,
                hook_clarity: "potentially_clear".to_string(),
                icp_specific: !context_lower.is_empty(),
                risk_flags: vec![],
            }
        }
    } else {
        HookAssessment {
            has_hook: false,
            hook_clarity: "no_hook_detected".to_string(),
            icp_specific: false,
            risk_flags: vec!["hook_missing".to_string()],
        }
    };

    let cta_assessment = if task_lower.contains("cta")
        || task_lower.contains("call to action")
        || task_lower.contains("sign up")
        || task_lower.contains("get started")
    {
        let has_specific_action = task_lower.contains("click")
            || task_lower.contains("download")
            || task_lower.contains("schedule")
            || task_lower.contains("start");

        CtaAssessment {
            has_cta: true,
            cta_specificity: if has_specific_action {
                "specific".to_string()
            } else {
                "vague".to_string()
            },
            cta_actionability: if has_specific_action {
                "actionable".to_string()
            } else {
                "unclear".to_string()
            },
            risk_flags: if has_specific_action {
                vec![]
            } else {
                vec!["cta_unclear".to_string()]
            },
        }
    } else {
        CtaAssessment {
            has_cta: false,
            cta_specificity: "none".to_string(),
            cta_actionability: "none".to_string(),
            risk_flags: vec!["cta_missing".to_string()],
        }
    };

    let voice_assessment = VoiceAssessment {
        voice_consistent: !has_generic_words,
        icp_voice_match: context_lower.contains("icp") || context_lower.contains("customer"),
        tone: "unknown".to_string(),
        risk_flags: if has_generic_words {
            vec!["voice_unclear".to_string()]
        } else {
            vec![]
        },
    };

    if generic_risk_flags.is_empty() && proof_claims.is_empty() && copy_elements.is_empty() {
        open_questions.push("What specific ICP pain should the copy address?".to_string());
        open_questions.push("What is the strategic frame or positioning?".to_string());
        open_questions.push("What proof or evidence is available to support claims?".to_string());
    }

    CopywriterCopyAudit {
        copy_elements,
        proof_claims,
        generic_risk_flags,
        hook_assessment,
        cta_assessment,
        voice_assessment,
        open_questions,
    }
}
