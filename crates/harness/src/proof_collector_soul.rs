use raptorflow_db::PgPool;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, DerivedInstinctFrame, build_avatar_embodiment_pack,
    build_proof_collector_role_lock_prompt, derive_proof_collector_instinct_frame,
};

pub const PROOF_COLLECTOR_AVATAR_KEY: &str = "proof_collector";
pub const PROOF_COLLECTOR_DISPLAY_NAME: &str = "Proof Collector";
pub const PROOF_COLLECTOR_ROLE: &str = "proof";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofCollectorDefaultSoul {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

pub fn build_proof_collector_identity_kernel() -> serde_json::Value {
    serde_json::json!({
        "core_drive": "Turn verified truth into trust assets and stop fake proof from entering the system.",
        "role": "Proof mapping, substantiation, testimonial discipline, case-study structure, claim-to-evidence linking, trust asset creation, proof gap detection.",
        "identity_markers": [
            "proof-protective",
            "trust-building",
            "claim-safety-focused"
        ]
    })
}

pub fn build_proof_collector_worldview() -> Vec<String> {
    vec![
        "Trust is built from specific proof, not confident language.".to_string(),
        "A strong claim without evidence is a liability.".to_string(),
        "Proof can be qualitative, quantitative, operational, or behavioral — but it must be labeled.".to_string(),
        "Customer quotes are sacred: never invent or 'clean up' beyond meaning.".to_string(),
        "Metrics need source, time window, baseline, and context.".to_string(),
        "Case studies should show situation, action, evidence, result, and limits.".to_string(),
        "Safer proof beats louder proof.".to_string(),
        "The absence of proof is a useful product and marketing signal.".to_string(),
    ]
}

pub fn build_proof_collector_obsessions() -> Vec<String> {
    vec![
        "claim substantiation".to_string(),
        "proof gaps".to_string(),
        "customer quotes".to_string(),
        "case-study structure".to_string(),
        "evidence hierarchy".to_string(),
        "metric provenance".to_string(),
        "typicality".to_string(),
        "consent/permission".to_string(),
        "before-after clarity".to_string(),
        "trust assets".to_string(),
        "safer proof wording".to_string(),
        "claims-to-evidence mapping".to_string(),
    ]
}

pub fn build_proof_collector_reflexes() -> Vec<String> {
    vec![
        "ask 'what proof supports this?'".to_string(),
        "map every strong claim to evidence".to_string(),
        "downgrade unsupported claims".to_string(),
        "separate verified outcome from anecdote".to_string(),
        "flag typicality risk".to_string(),
        "flag consent/permission gaps".to_string(),
        "preserve original customer meaning".to_string(),
        "demand source, date, time window, and context for metrics".to_string(),
        "create proof packs instead of hype".to_string(),
    ]
}

pub fn build_proof_collector_taboos() -> Vec<String> {
    vec![
        "do not invent proof".to_string(),
        "do not invent testimonials".to_string(),
        "do not invent customer quotes".to_string(),
        "do not invent customer logos".to_string(),
        "do not invent case studies".to_string(),
        "do not invent screenshots".to_string(),
        "do not invent metrics".to_string(),
        "do not imply typical results without support".to_string(),
        "do not hide uncertainty".to_string(),
        "do not publish or trigger external action".to_string(),
    ]
}

pub fn build_proof_collector_operating_principles() -> Vec<String> {
    vec![
        "Every proof asset must state what is verified, assumed, missing, and unsafe.".to_string(),
        "Every metric needs source, date/window, baseline if available, and limitation."
            .to_string(),
        "Every customer quote needs source and permission status.".to_string(),
        "Every case study must include limits and context.".to_string(),
        "If proof is weak, recommend safer wording instead of exaggeration.".to_string(),
        "Leave ripples only when there is reusable proof, claim-safety, or trust-asset learning."
            .to_string(),
    ]
}

pub fn build_proof_collector_debate_style() -> serde_json::Value {
    serde_json::json!({
        "challenge_bias": "high",
        "skepticism": "high toward unverified claims and fake proof",
        "defers_to_researcher": "on source truth",
        "defers_to_analyst": "on metric interpretation",
        "defers_to_strategist": "on strategic wedge once proof constraints are clear",
        "challenges_strategist": "when positioning depends on unsupported proof",
        "challenges_researcher": "when evidence exists but not packaged into usable trust assets",
        "challenges_copywriter": "when language outruns proof",
        "challenges_growth_operator": "when campaigns distribute claims without substantiation",
        "challenges_analyst": "when metric readouts lack source/window/baseline",
        "challenges_creative_director": "when creative implies proof visually without evidence",
        "preferred_stances": [
            "proof_challenge",
            "claim_substantiation_review",
            "testimonial_safety_review"
        ]
    })
}

pub fn build_proof_collector_evaluation_bias() -> serde_json::Value {
    serde_json::json!({
        "rejects_fake_proof": true,
        "rejects_invented_testimonials": true,
        "rejects_unverified_metrics": true,
        "rejects_typicality_claims_without_support": true,
        "rejects_permission_missing_quotes": true,
        "rejects_overstated_claims": true,
        "values_evidence_hierarchy": true,
        "values_source_quality": true,
        "values_permission_consent": true,
        "values_safe_proof_wording": true
    })
}

pub async fn ensure_proof_collector_soul(
    pool: &PgPool,
    org_id: Uuid,
) -> Result<ProofCollectorDefaultSoul, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .iter()
        .find(|a| a.avatar_key == PROOF_COLLECTOR_AVATAR_KEY && a.org_id == org_id)
        .cloned();

    let (avatar_id, created_avatar) = if let Some(existing) = avatar {
        (existing.avatar_id.clone(), false)
    } else {
        let new_avatar_id = Uuid::new_v4().to_string();
        let avatar_key = PROOF_COLLECTOR_AVATAR_KEY.to_string();
        let display_name = PROOF_COLLECTOR_DISPLAY_NAME.to_string();
        let role = PROOF_COLLECTOR_ROLE.to_string();
        let archetype = "trust_and_substantiation_room".to_string();
        let personality = serde_json::json!({});
        let system_prompt = "ProofCollector: Turn verified truth into trust assets.".to_string();
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

        let identity_kernel = build_proof_collector_identity_kernel();
        let worldview = build_proof_collector_worldview();
        let obsessions = build_proof_collector_obsessions();
        let reflexes = build_proof_collector_reflexes();
        let taboos = build_proof_collector_taboos();
        let debate_style = build_proof_collector_debate_style();
        let operating_principles = build_proof_collector_operating_principles();
        let evaluation_bias = build_proof_collector_evaluation_bias();

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

    Ok(ProofCollectorDefaultSoul {
        avatar_id,
        soul_id,
        created: created_avatar || created_soul,
        updated: updated_soul,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofCollectorDryRunInput {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofCollectorDryRunOutput {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: DerivedInstinctFrame,
    pub presence_state: Option<ProofCollectorPresenceState>,
    pub debate_event: Option<ProofCollectorDebateEvent>,
    pub proof_map: Option<ProofMap>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofCollectorPresenceState {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofCollectorDebateEvent {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofMap {
    pub known_facts: Vec<String>,
    pub claims: Vec<ClaimProofAssessment>,
    pub proof_gaps: Vec<String>,
    pub assets_to_collect: Vec<String>,
    pub unsafe_claims: Vec<String>,
    pub legal_review_flags: Vec<String>,
    pub ripple_candidates: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClaimProofAssessment {
    pub claim: String,
    pub proof_available: String,
    pub proof_type: String,
    pub proof_strength: String,
    pub source: String,
    pub permission_status: String,
    pub metric_context: MetricContext,
    pub risk: String,
    pub recommended_action: String,
    pub safer_wording: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricContext {
    pub source: String,
    pub time_window: String,
    pub baseline: String,
    pub sample_size: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofQualityScore {
    pub source_quality: u8,
    pub specificity: u8,
    pub permission_confidence: u8,
    pub typicality_clarity: u8,
    pub metric_context: u8,
    pub claim_alignment: u8,
    pub exaggeration_risk: u8,
}

pub fn classify_proof_type(proof_summary: &str, context_summary: &str) -> String {
    let combined = format!(
        "{} {}",
        proof_summary.to_lowercase(),
        context_summary.to_lowercase()
    );

    if combined.contains('%')
        || combined.contains("revenue")
        || combined.contains("ctr")
        || combined.contains("conversion")
        || combined.contains("pipeline")
        || combined.contains("retention")
        || combined.contains("ltv")
        || combined.contains("cac")
    {
        return "metric".to_string();
    }

    if combined.contains("quote") || combined.contains("said") || combined.contains("testimonial") {
        return "testimonial".to_string();
    }

    if combined.contains("case study")
        || combined.contains("before")
        || combined.contains("after")
        || combined.contains("implementation")
    {
        return "case_study".to_string();
    }

    if combined.contains("screenshot")
        || combined.contains("dashboard")
        || combined.contains("image")
    {
        return "screenshot".to_string();
    }

    if combined.contains("workflow")
        || combined.contains("process")
        || combined.contains("time saved")
        || combined.contains("cycle time")
        || combined.contains("operational")
    {
        return "operational_evidence".to_string();
    }

    if combined.contains("customer language")
        || combined.contains("review")
        || combined.contains("objection")
    {
        return "customer_language".to_string();
    }

    if combined.contains("third-party")
        || combined.contains("report")
        || combined.contains("publication")
        || combined.contains("source:")
    {
        return "third_party_source".to_string();
    }

    if combined.contains("story") || combined.contains("example") || combined.contains("anecdote") {
        return "anecdote".to_string();
    }

    "unknown".to_string()
}

pub fn score_proof_quality(
    proof_summary: &str,
    claim_summary: &str,
    context_summary: &str,
) -> ProofQualityScore {
    let combined_lower =
        format!("{} {} {}", proof_summary, claim_summary, context_summary).to_lowercase();

    let mut source_quality: u8 = 50;
    let mut specificity: u8 = 50;
    let mut permission_confidence: u8 = 100;
    let mut typicality_clarity: u8 = 80;
    let mut metric_context_score: u8 = 50;
    let mut claim_alignment: u8 = 50;
    let mut exaggeration_risk: u8 = 20;

    if !combined_lower.contains("source")
        && !combined_lower.contains("according to")
        && !combined_lower.contains("data from")
        && !combined_lower.contains("verified")
    {
        source_quality = 20;
    }

    if combined_lower.contains("who")
        || combined_lower.contains("what")
        || combined_lower.contains("when")
        || combined_lower.contains("result")
        || combined_lower.contains("limitation")
    {
        specificity = 80;
    } else if combined_lower.is_empty() || combined_lower.len() < 20 {
        specificity = 20;
    }

    if combined_lower.contains("testimonial")
        || combined_lower.contains("quote")
        || combined_lower.contains("customer said")
    {
        if combined_lower.contains("permission")
            || combined_lower.contains("consent")
            || combined_lower.contains("approved")
        {
            permission_confidence = 100;
        } else {
            permission_confidence = 30;
        }
    }

    if combined_lower.contains("typical")
        || combined_lower.contains("proven")
        || combined_lower.contains("always")
        || combined_lower.contains("#1")
        || combined_lower.contains("best")
        || combined_lower.contains("massive")
        || combined_lower.contains("10x")
        || combined_lower.contains("guaranteed")
    {
        typicality_clarity = 20;
        exaggeration_risk = 85;
    }

    if combined_lower.contains("baseline")
        || combined_lower.contains("compared")
        || combined_lower.contains("vs ")
        || combined_lower.contains("previous")
    {
        metric_context_score = 80;
    }

    if combined_lower.contains("date")
        || combined_lower.contains("time window")
        || combined_lower.contains("cohort")
    {
        metric_context_score = metric_context_score.saturating_add(15);
    }

    if combined_lower.contains("sample")
        || combined_lower.contains("n =")
        || combined_lower.contains("respondents")
    {
        metric_context_score = metric_context_score.saturating_add(10);
    }

    if combined_lower.contains("metric")
        && (combined_lower.contains("source")
            || combined_lower.contains("date")
            || combined_lower.contains("window")
            || combined_lower.contains("baseline"))
    {
        claim_alignment = 75;
    }

    ProofQualityScore {
        source_quality,
        specificity,
        permission_confidence,
        typicality_clarity,
        metric_context: metric_context_score,
        claim_alignment,
        exaggeration_risk,
    }
}

pub fn proof_safety_action(score: &ProofQualityScore) -> String {
    if score.exaggeration_risk >= 80 {
        return "remove_claim".to_string();
    }

    if score.source_quality < 30 {
        return "needs_source".to_string();
    }

    if score.permission_confidence < 50 {
        return "needs_permission".to_string();
    }

    if score.metric_context < 40 {
        return "needs_metric_context".to_string();
    }

    if score.typicality_clarity < 40 {
        return "qualify".to_string();
    }

    if score.exaggeration_risk >= 50 {
        return "qualify".to_string();
    }

    if score.source_quality >= 70 && score.specificity >= 60 && score.claim_alignment >= 70 {
        return "use_as_is".to_string();
    }

    "qualify".to_string()
}

pub fn assess_claim_against_proof(
    claim: &str,
    proof_summary: &str,
    context_summary: &str,
) -> ClaimProofAssessment {
    let proof_type = classify_proof_type(proof_summary, context_summary);
    let score = score_proof_quality(proof_summary, claim, context_summary);
    let action = proof_safety_action(&score);

    let claim_lower = claim.to_lowercase();
    let combined_lower = format!("{} {}", claim_lower, context_summary.to_lowercase());

    let mut source = String::new();
    let mut permission_status = "not_applicable".to_string();
    let mut time_window = String::new();
    let mut baseline = String::new();
    let mut sample_size = String::new();

    if combined_lower.contains("source:")
        || combined_lower.contains("source ")
        || combined_lower.contains("dashboard")
        || combined_lower.contains("analytics")
    {
        source = "present".to_string();
    }

    if combined_lower.contains("permission")
        || combined_lower.contains("consent")
        || combined_lower.contains("approved")
    {
        permission_status = "granted".to_string();
    } else if proof_type == "testimonial" {
        permission_status = "missing".to_string();
    }

    if combined_lower.contains("month")
        || combined_lower.contains("quarter")
        || combined_lower.contains("year")
        || combined_lower.contains("window")
    {
        time_window = "present".to_string();
    }

    if combined_lower.contains("baseline")
        || combined_lower.contains("previous")
        || combined_lower.contains("vs ")
        || combined_lower.contains("compared")
    {
        baseline = "present".to_string();
    }

    if combined_lower.contains("sample")
        || combined_lower.contains("n =")
        || combined_lower.contains("respondents")
        || combined_lower.contains("cohort")
    {
        sample_size = "present".to_string();
    }

    let proof_strength = if score.exaggeration_risk >= 80 {
        "unsafe"
    } else if score.source_quality < 30 || score.permission_confidence < 50 {
        "missing"
    } else if score.source_quality >= 70 && score.specificity >= 60 {
        "strong"
    } else if score.source_quality >= 50 {
        "moderate"
    } else {
        "weak"
    };

    let risk = if proof_strength == "unsafe" {
        "high_exaggeration".to_string()
    } else if proof_strength == "missing" {
        "missing_proof".to_string()
    } else if proof_strength == "weak" {
        "weak_substantiation".to_string()
    } else {
        "low".to_string()
    };

    let safer_wording = if action == "remove_claim" {
        format!(
            "Consider removing or significantly qualifying the claim: '{}'",
            claim
        )
    } else if action == "needs_source" {
        format!(
            "Add specific source, date, and methodology to support: '{}'",
            claim
        )
    } else if action == "needs_permission" {
        format!(
            "Obtain explicit permission before using this testimonial: '{}'",
            claim
        )
    } else if action == "needs_metric_context" {
        format!(
            "Add baseline, time window, and sample context to metric claim: '{}'",
            claim
        )
    } else if action == "qualify" {
        format!(
            "Add qualifier such as 'in some cases' or 'among users who...' to: '{}'",
            claim
        )
    } else {
        claim.to_string()
    };

    let recommended_action = action;
    let _missing_evidence: Vec<String> = Vec::new();

    ClaimProofAssessment {
        claim: claim.to_string(),
        proof_available: if proof_summary.is_empty() {
            "none".to_string()
        } else {
            proof_summary.to_string()
        },
        proof_type,
        proof_strength: proof_strength.to_string(),
        source: source.clone(),
        permission_status,
        metric_context: MetricContext {
            source: source.clone(),
            time_window,
            baseline,
            sample_size,
        },
        risk,
        recommended_action,
        safer_wording,
    }
}

pub async fn run_proof_collector_dry_run(
    pool: &PgPool,
    org_id: Uuid,
    input: ProofCollectorDryRunInput,
) -> Result<ProofCollectorDryRunOutput, Box<dyn std::error::Error + Send + Sync>> {
    let proof_collector = ensure_proof_collector_soul(pool, org_id).await?;

    let pack = build_avatar_embodiment_pack(pool, org_id, &proof_collector.avatar_id, None).await?;

    let role_lock_prompt = build_proof_collector_role_lock_prompt(&pack);

    let instinct_frame =
        derive_proof_collector_instinct_frame(&pack, &input.task_summary, &input.context_summary);

    let proof_map = Some(perform_proof_mapping(
        &input.task_summary,
        &input.context_summary,
    ));

    let presence_state = Some(ProofCollectorPresenceState {
        presence_id: Uuid::new_v4().to_string(),
        state: "forming_instinct".to_string(),
        current_focus: input.task_summary.chars().take(200).collect(),
        current_concern: instinct_frame.dominant_concern.clone(),
        visible_summary: instinct_frame.visible_summary.clone(),
        confidence: 0.7,
    });

    let debate_content = serde_json::json!({
        "known_facts": proof_map.as_ref().map(|p| &p.known_facts).unwrap_or(&vec![]),
        "claims": proof_map.as_ref().map(|p| &p.claims).unwrap_or(&vec![]),
        "proof_gaps": proof_map.as_ref().map(|p| &p.proof_gaps).unwrap_or(&vec![]),
        "unsafe_claims": proof_map.as_ref().map(|p| &p.unsafe_claims).unwrap_or(&vec![]),
        "task": input.task_summary,
    });

    let debate_event = Some(ProofCollectorDebateEvent {
        debate_event_id: Uuid::new_v4().to_string(),
        event_type: "proof_review".to_string(),
        stance: "proof_collector_initial_review".to_string(),
        content: debate_content,
        confidence: 0.65,
    });

    Ok(ProofCollectorDryRunOutput {
        avatar_id: proof_collector.avatar_id,
        soul_id: proof_collector.soul_id,
        embodiment_pack: pack,
        role_lock_prompt,
        instinct_frame,
        presence_state,
        debate_event,
        proof_map,
    })
}

fn perform_proof_mapping(task_summary: &str, context_summary: &str) -> ProofMap {
    let mut known_facts = Vec::new();
    let mut claims = Vec::new();
    let mut proof_gaps = Vec::new();
    let mut assets_to_collect = Vec::new();
    let mut unsafe_claims = Vec::new();
    let mut legal_review_flags = Vec::new();
    let ripple_candidates = Vec::new();

    let _task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let claim_indicators = [
        "revenue",
        "increase",
        "decrease",
        "growth",
        "conversion",
        "ctr",
        "users",
        "customers",
        "roi",
        "savings",
        "productivity",
        "efficiency",
        "faster",
        "better",
        "cheaper",
        "easier",
        "proven",
        "guaranteed",
        "#1",
        "best",
        "leading",
        "massive",
        "10x",
        "20x",
        "transformed",
    ];

    let mut claims_found = false;
    for indicator in &claim_indicators {
        if context_lower.contains(indicator) {
            claims_found = true;
            let claim_text = format!("Claim: contains '{}'", indicator);
            let assessment =
                assess_claim_against_proof(&claim_text, &context_lower, &context_lower);
            claims.push(assessment.clone());

            if assessment.proof_strength == "missing" || assessment.proof_strength == "unsafe" {
                unsafe_claims.push(claim_text.clone());
                proof_gaps.push(format!(
                    "Missing proof for claim containing '{}'",
                    indicator
                ));
            }

            if assessment.recommended_action == "needs_permission" {
                assets_to_collect.push("Customer testimonial permission".to_string());
            }

            if assessment.recommended_action == "needs_source" {
                assets_to_collect.push(format!("Source documentation for '{}'", indicator));
            }

            if indicator.contains("revenue")
                || indicator.contains("roi")
                || indicator.contains("conversion")
            {
                assets_to_collect.push("Baseline and time window documentation".to_string());
            }
        }
    }

    if (context_lower.contains("quote")
        || context_lower.contains("testimonial")
        || context_lower.contains("said"))
        && !context_lower.contains("permission")
        && !context_lower.contains("consent")
    {
        legal_review_flags.push("Testimonial may lack permission/consent".to_string());
        proof_gaps.push("Testimonial permission status unclear".to_string());
    }

    if context_lower.contains("case study") {
        let has_before = context_lower.contains("before");
        let has_after = context_lower.contains("after");
        let has_action = context_lower.contains("action") || context_lower.contains("implemented");
        let has_result = context_lower.contains("result") || context_lower.contains("outcome");

        if !has_before || !has_after || !has_action || !has_result {
            proof_gaps
                .push("Case study structure incomplete (before/action/result/limits)".to_string());
        }

        assets_to_collect
            .push("Complete case study: situation, action, evidence, result, limits".to_string());
    }

    if (context_lower.contains("typical")
        || context_lower.contains("average")
        || context_lower.contains("generally"))
        && !context_lower.contains("based on")
        && !context_lower.contains("study")
        && !context_lower.contains("data")
    {
        legal_review_flags.push("Typicality claim may lack statistical support".to_string());
    }

    let exaggeration_words = [
        "guaranteed",
        "proven",
        "always",
        "#1",
        "best",
        "massive",
        "10x",
        "20x",
        "transformed",
    ];
    for word in &exaggeration_words {
        if context_lower.contains(word) {
            legal_review_flags.push(format!(
                "Exaggeration risk: '{}' requires strong substantiation",
                word
            ));
        }
    }

    if claims_found {
        known_facts.push("Claims detected in context requiring proof review".to_string());
    } else {
        proof_gaps.push("No specific claims requiring proof detected".to_string());
    }

    if context_lower.contains("customer") && context_lower.contains("data") {
        known_facts.push("Customer data referenced".to_string());
    }

    if context_lower.contains("screenshot") || context_lower.contains("dashboard") {
        assets_to_collect.push("Screenshot source and date documentation".to_string());
        if !context_lower.contains("permission") {
            legal_review_flags.push("Screenshot may need usage permission".to_string());
        }
    }

    ProofMap {
        known_facts,
        claims,
        proof_gaps,
        assets_to_collect,
        unsafe_claims,
        legal_review_flags,
        ripple_candidates,
    }
}
