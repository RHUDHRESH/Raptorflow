use raptorflow_db::PgPool;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, DerivedInstinctFrame, build_avatar_embodiment_pack,
    build_creative_director_role_lock_prompt, derive_creative_director_instinct_frame,
};

pub const CREATIVE_DIRECTOR_AVATAR_KEY: &str = "creative_director";
pub const CREATIVE_DIRECTOR_DISPLAY_NAME: &str = "CreativeDirector";
pub const CREATIVE_DIRECTOR_ROLE: &str = "creative";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreativeDirectorDefaultSoul {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

pub fn build_creative_director_identity_kernel() -> serde_json::Value {
    serde_json::json!({
        "core_drive": "Raise creative standards and protect the brand's aesthetic integrity while ensuring work resonates with the audience.",
        "role": "Creative vision, aesthetic quality, brand consistency, emotional resonance, creative risk assessment, taste arbitration, creative direction.",
        "identity_markers": [
            "taste-driven",
            "quality-focused",
            "brand-protective"
        ]
    })
}

pub fn build_creative_director_worldview() -> Vec<String> {
    vec![
        "Good enough is the enemy of great.".to_string(),
        "Creative work must earn attention before it can convert.".to_string(),
        "Taste is not subjective — it is the ability to recognize what works and what does not.".to_string(),
        "A brand is a promise, and every piece of creative either fulfills or breaks that promise.".to_string(),
        "Emotional resonance drives action more reliably than rational argument.".to_string(),
        "Consistency builds trust; chaos erodes it.".to_string(),
        "The job is not to make creative that the brand likes — it is to make creative that the audience needs.".to_string(),
        "Creative quality is not a nice-to-have; it is the difference between noise and signal.".to_string(),
    ]
}

pub fn build_creative_director_obsessions() -> Vec<String> {
    vec![
        "aesthetic quality".to_string(),
        "brand consistency".to_string(),
        "emotional resonance".to_string(),
        "clarity of message".to_string(),
        "visual hierarchy".to_string(),
        "copy and design unity".to_string(),
        "audience empathy".to_string(),
        "differentiation".to_string(),
        "first impression".to_string(),
        "call to action effectiveness".to_string(),
        "creative risk calibration".to_string(),
        "taste standards".to_string(),
    ]
}

pub fn build_creative_director_reflexes() -> Vec<String> {
    vec![
        "ask 'does this connect with the audience?'".to_string(),
        "assess first-impression quality".to_string(),
        "check brand voice consistency".to_string(),
        "evaluate emotional pull".to_string(),
        "flag generic or derivative work".to_string(),
        "demand clear hierarchy".to_string(),
        "check CTA clarity and visibility".to_string(),
        "assess creative risk level".to_string(),
        "protect brand integrity".to_string(),
        "challenge work that prioritizes brand preference over audience need".to_string(),
    ]
}

pub fn build_creative_director_taboos() -> Vec<String> {
    vec![
        "do not approve work that erodes brand quality".to_string(),
        "do not let internal brand preference override audience resonance".to_string(),
        "do not approve generic or derivative creative".to_string(),
        "do not let creative chase trends at the expense of authenticity".to_string(),
        "do not approve work with unclear hierarchy or confusing message".to_string(),
        "do not let creative quality become an afterthought".to_string(),
        "do not approve work that prioritizes brand ego over audience need".to_string(),
        "do not ignore emotional resonance in favor of rational argument".to_string(),
    ]
}

pub fn build_creative_director_operating_principles() -> Vec<String> {
    vec![
        "Every piece of creative must earn its place in the audience's attention.".to_string(),
        "Brand consistency is not rigidity — it is reliability that builds trust.".to_string(),
        "Taste is the ability to recognize quality and the courage to demand it.".to_string(),
        "Creative risk is acceptable when calibrated to audience tolerance.".to_string(),
        "The first impression is the lasting impression.".to_string(),
        "Leave ripples only when there is reusable learning about creative execution, aesthetic choices, or brand voice.".to_string(),
    ]
}

pub fn build_creative_director_debate_style() -> serde_json::Value {
    serde_json::json!({
        "challenge_bias": "high",
        "skepticism": "high toward generic creative and brand ego",
        "defers_to_strategist": "on strategic direction",
        "defers_to_copywriter": "on language and copy decisions",
        "defers_to_analyst": "on performance signal",
        "challenges_strategist": "when creative strategy lacks aesthetic coherence",
        "challenges_copywriter": "when copy lacks emotional resonance or brand voice",
        "challenges_growth_operator": "when execution rhythm sacrifices creative quality",
        "challenges_analyst": "when metric optimization drives generic creative",
        "preferred_stances": [
            "creative_quality_review",
            "brand_consistency_check",
            "emotional_resonance_assessment"
        ]
    })
}

pub fn build_creative_director_evaluation_bias() -> serde_json::Value {
    serde_json::json!({
        "rejects_generic_creative": true,
        "rejects_brand_ego_driven_work": true,
        "rejects_inconsistent_brand_voice": true,
        "rejects_confusing_hierarchy": true,
        "rejects_emotionally_flat_work": true,
        "values_aesthetic_quality": true,
        "values_brand_consistency": true,
        "values_emotional_resonance": true,
        "values_audience_clarity": true,
        "values_differentiation": true
    })
}

pub async fn ensure_creative_director_soul(
    pool: &PgPool,
    org_id: Uuid,
) -> Result<CreativeDirectorDefaultSoul, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .iter()
        .find(|a| a.avatar_key == CREATIVE_DIRECTOR_AVATAR_KEY && a.org_id == org_id)
        .cloned();

    let (avatar_id, created_avatar) = if let Some(existing) = avatar {
        (existing.avatar_id.clone(), false)
    } else {
        let new_avatar_id = Uuid::new_v4().to_string();
        let avatar_key = CREATIVE_DIRECTOR_AVATAR_KEY.to_string();
        let display_name = CREATIVE_DIRECTOR_DISPLAY_NAME.to_string();
        let role = CREATIVE_DIRECTOR_ROLE.to_string();
        let archetype = "creative_brief_room".to_string();
        let personality = serde_json::json!({});
        let system_prompt =
            "CreativeDirector: Raise creative standards and protect aesthetic integrity."
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

        let identity_kernel = build_creative_director_identity_kernel();
        let worldview = build_creative_director_worldview();
        let obsessions = build_creative_director_obsessions();
        let reflexes = build_creative_director_reflexes();
        let taboos = build_creative_director_taboos();
        let debate_style = build_creative_director_debate_style();
        let operating_principles = build_creative_director_operating_principles();
        let evaluation_bias = build_creative_director_evaluation_bias();

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

    Ok(CreativeDirectorDefaultSoul {
        avatar_id,
        soul_id,
        created: created_avatar || created_soul,
        updated: updated_soul,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreativeDirectorDryRunInput {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreativeDirectorDryRunOutput {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: DerivedInstinctFrame,
    pub presence_state: Option<CreativeDirectorPresenceState>,
    pub debate_event: Option<CreativeDirectorDebateEvent>,
    pub creative_review: Option<CreativeQualityReview>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreativeDirectorPresenceState {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreativeDirectorDebateEvent {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreativeQualityReview {
    pub aesthetic_quality: AestheticQualityAssessment,
    pub brand_consistency: BrandConsistencyAssessment,
    pub emotional_resonance: EmotionalResonanceAssessment,
    pub message_clarity: MessageClarityAssessment,
    pub creative_risk: CreativeRiskAssessment,
    pub overall_verdict: String,
    pub recommended_action: String,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AestheticQualityAssessment {
    pub visual_hierarchy_clear: bool,
    pub design_unity: bool,
    pub first_impression_score: u8,
    pub quality_concerns: Vec<String>,
    pub strengths: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrandConsistencyAssessment {
    pub voice_consistent: bool,
    pub tone_appropriate: bool,
    pub brand_values_aligned: bool,
    pub consistency_score: u8,
    pub deviations: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmotionalResonanceAssessment {
    pub has_emotional_hook: bool,
    pub audience_empathy_present: bool,
    pub resonance_level: String,
    pub emotional_tone: String,
    pub concerns: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageClarityAssessment {
    pub primary_message_clear: bool,
    pub cta_visible: bool,
    pub cta_compelling: bool,
    pub hierarchy_clarity_score: u8,
    pub confusion_points: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreativeRiskAssessment {
    pub risk_level: String,
    pub audience_tolerance_appropriate: bool,
    pub differentiation_achieved: bool,
    pub risk_concerns: Vec<String>,
}

pub async fn run_creative_director_dry_run(
    pool: &PgPool,
    org_id: Uuid,
    input: CreativeDirectorDryRunInput,
) -> Result<CreativeDirectorDryRunOutput, Box<dyn std::error::Error + Send + Sync>> {
    let creative_director = ensure_creative_director_soul(pool, org_id).await?;

    let pack =
        build_avatar_embodiment_pack(pool, org_id, &creative_director.avatar_id, None).await?;

    let role_lock_prompt = build_creative_director_role_lock_prompt(&pack);

    let instinct_frame =
        derive_creative_director_instinct_frame(&pack, &input.task_summary, &input.context_summary);

    let creative_review = Some(perform_creative_quality_review(
        &input.task_summary,
        &input.context_summary,
    ));

    let presence_state = Some(CreativeDirectorPresenceState {
        presence_id: Uuid::new_v4().to_string(),
        state: "forming_instinct".to_string(),
        current_focus: input.task_summary.chars().take(200).collect(),
        current_concern: instinct_frame.dominant_concern.clone(),
        visible_summary: instinct_frame.visible_summary.clone(),
        confidence: 0.7,
    });

    let debate_content = serde_json::json!({
        "aesthetic_quality": creative_review.as_ref().map(|r| &r.aesthetic_quality).unwrap_or(&AestheticQualityAssessment {
            visual_hierarchy_clear: false,
            design_unity: false,
            first_impression_score: 0,
            quality_concerns: vec![],
            strengths: vec![],
        }),
        "brand_consistency": creative_review.as_ref().map(|r| &r.brand_consistency).unwrap_or(&BrandConsistencyAssessment {
            voice_consistent: false,
            tone_appropriate: false,
            brand_values_aligned: false,
            consistency_score: 0,
            deviations: vec![],
        }),
        "emotional_resonance": creative_review.as_ref().map(|r| &r.emotional_resonance).unwrap_or(&EmotionalResonanceAssessment {
            has_emotional_hook: false,
            audience_empathy_present: false,
            resonance_level: "unknown".to_string(),
            emotional_tone: "unknown".to_string(),
            concerns: vec![],
        }),
        "overall_verdict": creative_review.as_ref().map(|r| &r.overall_verdict).unwrap_or(&"unknown".to_string()),
        "recommended_action": creative_review.as_ref().map(|r| &r.recommended_action).unwrap_or(&"investigate".to_string()),
        "task": input.task_summary,
    });

    let debate_event = Some(CreativeDirectorDebateEvent {
        debate_event_id: Uuid::new_v4().to_string(),
        event_type: "creative_review".to_string(),
        stance: "creative_director_initial_review".to_string(),
        content: debate_content,
        confidence: 0.65,
    });

    Ok(CreativeDirectorDryRunOutput {
        avatar_id: creative_director.avatar_id,
        soul_id: creative_director.soul_id,
        embodiment_pack: pack,
        role_lock_prompt,
        instinct_frame,
        presence_state,
        debate_event,
        creative_review,
    })
}

fn perform_creative_quality_review(
    task_summary: &str,
    context_summary: &str,
) -> CreativeQualityReview {
    let task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let mut aesthetic_quality = AestheticQualityAssessment {
        visual_hierarchy_clear: true,
        design_unity: true,
        first_impression_score: 70,
        quality_concerns: Vec::new(),
        strengths: Vec::new(),
    };

    let mut brand_consistency = BrandConsistencyAssessment {
        voice_consistent: true,
        tone_appropriate: true,
        brand_values_aligned: true,
        consistency_score: 75,
        deviations: Vec::new(),
    };

    let mut emotional_resonance = EmotionalResonanceAssessment {
        has_emotional_hook: false,
        audience_empathy_present: true,
        resonance_level: "moderate".to_string(),
        emotional_tone: "neutral".to_string(),
        concerns: Vec::new(),
    };

    let mut message_clarity = MessageClarityAssessment {
        primary_message_clear: true,
        cta_visible: true,
        cta_compelling: true,
        hierarchy_clarity_score: 70,
        confusion_points: Vec::new(),
    };

    let mut creative_risk = CreativeRiskAssessment {
        risk_level: "calibrated".to_string(),
        audience_tolerance_appropriate: true,
        differentiation_achieved: true,
        risk_concerns: Vec::new(),
    };

    let mut overall_verdict = "conditional_pass".to_string();
    let mut recommended_action = "iterate".to_string();
    let mut open_questions = Vec::new();

    let generic_indicators = [
        "generic",
        "derivative",
        "template",
        "stock",
        "boring",
        "safe",
        "basic",
        "typical",
        "standard",
    ];
    for indicator in &generic_indicators {
        if context_lower.contains(indicator) {
            aesthetic_quality.quality_concerns.push(format!(
                "Generic or derivative creative detected: {}",
                indicator
            ));
            aesthetic_quality.first_impression_score =
                aesthetic_quality.first_impression_score.saturating_sub(20);
            overall_verdict = "needs_work".to_string();
            recommended_action = "iterate".to_string();
        }
    }

    let weak_hierarchy_indicators = [
        "confusing",
        "unclear",
        "messy",
        "cluttered",
        "no hierarchy",
        "hard to read",
        "overwhelming",
    ];
    for indicator in &weak_hierarchy_indicators {
        if context_lower.contains(indicator) {
            aesthetic_quality.visual_hierarchy_clear = false;
            aesthetic_quality.first_impression_score =
                aesthetic_quality.first_impression_score.saturating_sub(15);
            message_clarity
                .confusion_points
                .push(format!("Hierarchy concern: {}", indicator));
            message_clarity.hierarchy_clarity_score =
                message_clarity.hierarchy_clarity_score.saturating_sub(20);
            overall_verdict = "needs_work".to_string();
        }
    }

    let brand_voice_indicators = [
        "inconsistent",
        "off-brand",
        "wrong tone",
        "doesn't fit",
        "mismatched",
        "not us",
    ];
    for indicator in &brand_voice_indicators {
        if context_lower.contains(indicator) {
            brand_consistency.voice_consistent = false;
            brand_consistency.consistency_score =
                brand_consistency.consistency_score.saturating_sub(30);
            brand_consistency
                .deviations
                .push(format!("Brand voice issue: {}", indicator));
            overall_verdict = "needs_work".to_string();
            recommended_action = "iterate".to_string();
        }
    }

    let emotional_indicators = [
        "emotional",
        "feel",
        "connect",
        "resonate",
        "touch",
        "move",
        "inspire",
        "laugh",
        "cry",
        "surprise",
    ];
    let has_emotional_hook = emotional_indicators
        .iter()
        .any(|i| context_lower.contains(i));
    if has_emotional_hook {
        emotional_resonance.has_emotional_hook = true;
        emotional_resonance.resonance_level = "strong".to_string();
        aesthetic_quality
            .strengths
            .push("Emotional resonance detected".to_string());
    }

    let no_emotion_indicators = [
        "flat",
        "bland",
        "cold",
        "clinical",
        "informational",
        "dry",
        "transactional",
    ];
    for indicator in &no_emotion_indicators {
        if context_lower.contains(indicator) {
            emotional_resonance.has_emotional_hook = false;
            emotional_resonance.resonance_level = "weak".to_string();
            emotional_resonance
                .concerns
                .push(format!("Emotional hook missing: {}", indicator));
            aesthetic_quality.first_impression_score =
                aesthetic_quality.first_impression_score.saturating_sub(15);
        }
    }

    let cta_indicators = [
        "call to action",
        "cta",
        "sign up",
        "buy now",
        "learn more",
        "get started",
        "book a demo",
        "download",
    ];
    let has_clear_cta = cta_indicators.iter().any(|i| context_lower.contains(i));
    if !has_clear_cta
        && (task_lower.contains("conversion")
            || task_lower.contains("cta")
            || task_lower.contains("action"))
    {
        message_clarity.cta_visible = false;
        message_clarity.cta_compelling = false;
        message_clarity
            .confusion_points
            .push("CTA unclear or missing".to_string());
        message_clarity.hierarchy_clarity_score =
            message_clarity.hierarchy_clarity_score.saturating_sub(20);
        open_questions.push("What is the desired call to action?".to_string());
    }

    let differentiation_indicators = [
        "different",
        "unique",
        "stands out",
        "memorable",
        "distinctive",
        "fresh",
    ];
    let has_differentiation = differentiation_indicators
        .iter()
        .any(|i| context_lower.contains(i));
    if !has_differentiation && context_lower.contains("compete") {
        creative_risk.differentiation_achieved = false;
        creative_risk
            .risk_concerns
            .push("Differentiation unclear — may blend into noise".to_string());
    }

    let risk_level_indicators = [
        "bold",
        "risky",
        "edgy",
        "controversial",
        "provocative",
        "unexpected",
    ];
    let creative_risky = risk_level_indicators
        .iter()
        .any(|i| context_lower.contains(i));
    if creative_risky {
        creative_risk.risk_level = "elevated".to_string();
        if !creative_risk.audience_tolerance_appropriate {
            creative_risk
                .risk_concerns
                .push("Creative risk may exceed audience tolerance".to_string());
            overall_verdict = "needs_work".to_string();
            recommended_action = "iterate".to_string();
        }
    }

    if aesthetic_quality.first_impression_score >= 80
        && brand_consistency.consistency_score >= 75
        && emotional_resonance.resonance_level == "strong"
        && message_clarity.hierarchy_clarity_score >= 70
    {
        overall_verdict = "pass".to_string();
        recommended_action = "keep".to_string();
    } else if overall_verdict == "needs_work" {
        // already set
    } else if aesthetic_quality.first_impression_score >= 60 {
        overall_verdict = "conditional_pass".to_string();
        recommended_action = "iterate".to_string();
    } else {
        overall_verdict = "needs_work".to_string();
        recommended_action = "iterate".to_string();
    }

    if overall_verdict == "pass" && !has_clear_cta {
        open_questions.push("Should a CTA be added for conversion tracking?".to_string());
    }

    if !has_differentiation && context_lower.contains("competitive") {
        open_questions.push("How does this creative differentiate from competitors?".to_string());
    }

    if emotional_resonance.resonance_level == "weak" {
        open_questions.push("How can emotional resonance be improved?".to_string());
    }

    CreativeQualityReview {
        aesthetic_quality,
        brand_consistency,
        emotional_resonance,
        message_clarity,
        creative_risk,
        overall_verdict,
        recommended_action,
        open_questions,
    }
}
