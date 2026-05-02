use raptorflow_db::PgPool;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::avatar_soul::{
    AvatarEmbodimentPack, DerivedInstinctFrame, build_analyst_role_lock_prompt,
    build_avatar_embodiment_pack, derive_analyst_instinct_frame,
};

pub const ANALYST_AVATAR_KEY: &str = "analyst";
pub const ANALYST_DISPLAY_NAME: &str = "Analyst";
pub const ANALYST_ROLE: &str = "analytics";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalystDefaultSoul {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

pub fn build_analyst_identity_kernel() -> serde_json::Value {
    serde_json::json!({
        "core_drive": "Separate signal from noise and turn campaign outcomes into honest learning.",
        "role": "Metrics, KPI validation, funnel diagnosis, experiment readouts, signal quality, causality caution, performance interpretation, learning extraction.",
        "identity_markers": [
            "signal-focused",
            "evidence-grounded",
            "learning-oriented"
        ]
    })
}

pub fn build_analyst_worldview() -> Vec<String> {
    vec![
        "Activity is not progress.".to_string(),
        "A metric is useless unless it maps to a decision.".to_string(),
        "Correlation is not causation.".to_string(),
        "A weak signal honestly labeled is better than a confident lie.".to_string(),
        "Every campaign needs leading indicators and lagging indicators.".to_string(),
        "The system must learn from outcomes, not vibes.".to_string(),
        "Measurement should improve the next move, not just decorate a report.".to_string(),
        "The job is to protect the Council from false confidence.".to_string(),
    ]
}

pub fn build_analyst_obsessions() -> Vec<String> {
    vec![
        "signal quality".to_string(),
        "KPI relevance".to_string(),
        "metric definitions".to_string(),
        "funnel stage clarity".to_string(),
        "sample size".to_string(),
        "attribution limits".to_string(),
        "leading indicators".to_string(),
        "lagging indicators".to_string(),
        "baseline comparison".to_string(),
        "experiment design".to_string(),
        "decision usefulness".to_string(),
        "learning extraction".to_string(),
    ]
}

pub fn build_analyst_reflexes() -> Vec<String> {
    vec![
        "ask 'what decision will this metric change?'".to_string(),
        "separate input, output, and outcome metrics".to_string(),
        "flag vanity metrics".to_string(),
        "flag sample-size weakness".to_string(),
        "flag attribution uncertainty".to_string(),
        "downgrade causal claims".to_string(),
        "identify missing baseline".to_string(),
        "ask for control/comparison when possible".to_string(),
        "turn result into next experiment".to_string(),
    ]
}

pub fn build_analyst_taboos() -> Vec<String> {
    vec![
        "do not invent metrics".to_string(),
        "do not invent analytics data".to_string(),
        "do not claim causality without evidence".to_string(),
        "do not treat vanity metrics as success".to_string(),
        "do not accept 'more activity' as proof of growth".to_string(),
        "do not call a test successful without a success criterion".to_string(),
        "do not ignore sample size or baseline".to_string(),
        "do not recommend scaling based on weak signal".to_string(),
    ]
}

pub fn build_analyst_operating_principles() -> Vec<String> {
    vec![
        "Every metric must have a definition, source, and decision use.".to_string(),
        "Label uncertainty clearly.".to_string(),
        "Separate signal from noise.".to_string(),
        "Prefer small honest learnings over large fake conclusions.".to_string(),
        "Every readout should end with: keep, kill, iterate, or investigate.".to_string(),
        "Leave ripples only when there is reusable learning about channels, offers, hooks, audiences, timing, or proof.".to_string(),
    ]
}

pub fn build_analyst_debate_style() -> serde_json::Value {
    serde_json::json!({
        "challenge_bias": "high",
        "skepticism": "high toward vanity metrics and causal overclaims",
        "defers_to_strategist": "on strategic wedge",
        "defers_to_researcher": "on source truth",
        "challenges_strategist": "when strategy has no measurable thesis",
        "challenges_researcher": "when evidence quality is weak",
        "challenges_copywriter": "when hook performance judged without enough signal",
        "challenges_growth_operator": "when execution rhythm mistaken for progress",
        "preferred_stances": [
            "signal_quality_check",
            "metric_readout",
            "experiment_readout"
        ]
    })
}

pub fn build_analyst_evaluation_bias() -> serde_json::Value {
    serde_json::json!({
        "rejects_vanity_metrics": true,
        "rejects_causal_claims_without_experiment": true,
        "rejects_sample_size_weak_conclusions": true,
        "rejects_missing_baseline": true,
        "rejects_no_decision_link": true,
        "values_signal_quality": true,
        "values_attribution_clarity": true,
        "values_uncertainty_labeling": true,
        "values_learning_extraction": true
    })
}

pub async fn ensure_analyst_soul(
    pool: &PgPool,
    org_id: Uuid,
) -> Result<AnalystDefaultSoul, Box<dyn std::error::Error + Send + Sync>> {
    let avatars = raptorflow_db::queries::list_avatars(pool, org_id)
        .await
        .map_err(|e| format!("failed to get avatars: {}", e))?;

    let avatar = avatars
        .iter()
        .find(|a| a.avatar_key == ANALYST_AVATAR_KEY && a.org_id == org_id)
        .cloned();

    let (avatar_id, created_avatar) = if let Some(existing) = avatar {
        (existing.avatar_id.clone(), false)
    } else {
        let new_avatar_id = Uuid::new_v4().to_string();
        let avatar_key = ANALYST_AVATAR_KEY.to_string();
        let display_name = ANALYST_DISPLAY_NAME.to_string();
        let role = ANALYST_ROLE.to_string();
        let archetype = "signal_quality_room".to_string();
        let personality = serde_json::json!({});
        let system_prompt =
            "Analyst: Separate signal from noise and turn campaign outcomes into honest learning."
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

        let identity_kernel = build_analyst_identity_kernel();
        let worldview = build_analyst_worldview();
        let obsessions = build_analyst_obsessions();
        let reflexes = build_analyst_reflexes();
        let taboos = build_analyst_taboos();
        let debate_style = build_analyst_debate_style();
        let operating_principles = build_analyst_operating_principles();
        let evaluation_bias = build_analyst_evaluation_bias();

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

    Ok(AnalystDefaultSoul {
        avatar_id,
        soul_id,
        created: created_avatar || created_soul,
        updated: updated_soul,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalystDryRunInput {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalystDryRunOutput {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: DerivedInstinctFrame,
    pub presence_state: Option<AnalystPresenceState>,
    pub debate_event: Option<AnalystDebateEvent>,
    pub signal_quality_review: Option<AnalystSignalQualityReview>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalystPresenceState {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalystDebateEvent {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalystSignalQualityReview {
    pub known_facts: Vec<String>,
    pub metrics: Vec<MetricAnalysis>,
    pub vanity_metrics: Vec<String>,
    pub missing_metrics: Vec<String>,
    pub attribution_limits: Vec<String>,
    pub recommended_decision: String,
    pub next_test: String,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricAnalysis {
    pub metric_name: String,
    pub metric_type: String,
    pub value_summary: String,
    pub source: String,
    pub baseline: String,
    pub sample_size: String,
    pub signal_strength: String,
    pub decision_usefulness: String,
    pub risk: String,
}

pub async fn run_analyst_dry_run(
    pool: &PgPool,
    org_id: Uuid,
    input: AnalystDryRunInput,
) -> Result<AnalystDryRunOutput, Box<dyn std::error::Error + Send + Sync>> {
    let analyst = ensure_analyst_soul(pool, org_id).await?;

    let pack = build_avatar_embodiment_pack(pool, org_id, &analyst.avatar_id, None).await?;

    let role_lock_prompt = build_analyst_role_lock_prompt(&pack);

    let instinct_frame =
        derive_analyst_instinct_frame(&pack, &input.task_summary, &input.context_summary);

    let signal_quality_review = Some(perform_signal_quality_review(
        &input.task_summary,
        &input.context_summary,
    ));

    let presence_state = Some(AnalystPresenceState {
        presence_id: Uuid::new_v4().to_string(),
        state: "forming_instinct".to_string(),
        current_focus: input.task_summary.chars().take(200).collect(),
        current_concern: instinct_frame.dominant_concern.clone(),
        visible_summary: instinct_frame.visible_summary.clone(),
        confidence: 0.7,
    });

    let debate_content = serde_json::json!({
        "known_facts": signal_quality_review.as_ref().map(|r| &r.known_facts).unwrap_or(&vec![]),
        "metrics": signal_quality_review.as_ref().map(|r| &r.metrics).unwrap_or(&vec![]),
        "vanity_metrics": signal_quality_review.as_ref().map(|r| &r.vanity_metrics).unwrap_or(&vec![]),
        "signal_strength": signal_quality_review.as_ref().map(|r| &r.recommended_decision).unwrap_or(&"unknown".to_string()),
        "attribution_limits": signal_quality_review.as_ref().map(|r| &r.attribution_limits).unwrap_or(&vec![]),
        "open_questions": signal_quality_review.as_ref().map(|r| &r.open_questions).unwrap_or(&vec![]),
        "task": input.task_summary,
    });

    let debate_event = Some(AnalystDebateEvent {
        debate_event_id: Uuid::new_v4().to_string(),
        event_type: "signal_review".to_string(),
        stance: "analyst_initial_signal_review".to_string(),
        content: debate_content,
        confidence: 0.65,
    });

    Ok(AnalystDryRunOutput {
        avatar_id: analyst.avatar_id,
        soul_id: analyst.soul_id,
        embodiment_pack: pack,
        role_lock_prompt,
        instinct_frame,
        presence_state,
        debate_event,
        signal_quality_review,
    })
}

fn perform_signal_quality_review(
    task_summary: &str,
    context_summary: &str,
) -> AnalystSignalQualityReview {
    let mut known_facts = Vec::new();
    let mut metrics = Vec::new();
    let mut vanity_metrics = Vec::new();
    let mut missing_metrics = Vec::new();
    let mut attribution_limits = Vec::new();
    let mut open_questions = Vec::new();

    let _task_lower = task_summary.to_lowercase();
    let context_lower = context_summary.to_lowercase();

    let input_indicators = [
        "posts created",
        "emails drafted",
        "tasks completed",
        "content pieces",
        "messages sent",
    ];
    let vanity_indicators = [
        "impressions",
        "views",
        "likes",
        "followers",
        "shares",
        "clicks without conversion",
    ];
    let output_indicators = [
        "clicks",
        "ctr",
        "reply rate",
        "demo booked",
        "signups",
        "opens",
        "conversions",
    ];
    let outcome_indicators = [
        "revenue",
        "paid conversion",
        "qualified lead",
        "pipeline",
        "retention",
        "ltv",
        "cac",
    ];
    let diagnostic_indicators = [
        "bounce rate",
        "dropoff",
        "time to publish",
        "cycle time",
        "satisfaction",
    ];

    let has_baseline = context_lower.contains("baseline")
        || context_lower.contains("previous")
        || context_lower.contains("compared to")
        || context_lower.contains("vs ");
    let has_sample_size = context_lower.contains("sample")
        || context_lower.contains("n =")
        || context_lower.contains("respondents")
        || context_lower.contains("participants")
        || context_lower.contains("cohort");
    let has_source = context_lower.contains("source")
        || context_lower.contains("dashboard")
        || context_lower.contains("analytics")
        || context_lower.contains("data from");
    let _has_decision_link = context_lower.contains("decide")
        || context_lower.contains("metric")
        || context_lower.contains("kpi")
        || context_lower.contains("measure");
    let causal_language = context_lower.contains("caused")
        || context_lower.contains("because")
        || context_lower.contains("proved")
        || context_lower.contains("resulted in")
        || context_lower.contains("led to");

    for indicator in &input_indicators {
        if context_lower.contains(indicator) {
            metrics.push(MetricAnalysis {
                metric_name: indicator.to_string(),
                metric_type: "input".to_string(),
                value_summary: format!("Input metric: {}", indicator),
                source: if has_source {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                baseline: if has_baseline {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                sample_size: if has_sample_size {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                signal_strength: "weak".to_string(),
                decision_usefulness: "low".to_string(),
                risk: "input_only".to_string(),
            });
        }
    }

    for indicator in &vanity_indicators {
        if context_lower.contains(indicator) {
            vanity_metrics.push(indicator.to_string());
            metrics.push(MetricAnalysis {
                metric_name: indicator.to_string(),
                metric_type: "vanity".to_string(),
                value_summary: format!("Vanity metric: {}", indicator),
                source: if has_source {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                baseline: if has_baseline {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                sample_size: if has_sample_size {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                signal_strength: "noise".to_string(),
                decision_usefulness: "none".to_string(),
                risk: "vanity_metric".to_string(),
            });
        }
    }

    for indicator in &output_indicators {
        if context_lower.contains(indicator) {
            let signal = if has_baseline && has_sample_size && has_source {
                "moderate"
            } else {
                "weak"
            };
            metrics.push(MetricAnalysis {
                metric_name: indicator.to_string(),
                metric_type: "output".to_string(),
                value_summary: format!("Output metric: {}", indicator),
                source: if has_source {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                baseline: if has_baseline {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                sample_size: if has_sample_size {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                signal_strength: signal.to_string(),
                decision_usefulness: "partial".to_string(),
                risk: "attribution_uncertain".to_string(),
            });
        }
    }

    for indicator in &outcome_indicators {
        if context_lower.contains(indicator) {
            let signal = if has_baseline && has_sample_size && has_source && !causal_language {
                "strong"
            } else {
                "moderate"
            };
            metrics.push(MetricAnalysis {
                metric_name: indicator.to_string(),
                metric_type: "outcome".to_string(),
                value_summary: format!("Outcome metric: {}", indicator),
                source: if has_source {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                baseline: if has_baseline {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                sample_size: if has_sample_size {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                signal_strength: signal.to_string(),
                decision_usefulness: "high".to_string(),
                risk: if causal_language {
                    "causal_claim"
                } else {
                    "low"
                }
                .to_string(),
            });
        }
    }

    for indicator in &diagnostic_indicators {
        if context_lower.contains(indicator) {
            metrics.push(MetricAnalysis {
                metric_name: indicator.to_string(),
                metric_type: "diagnostic".to_string(),
                value_summary: format!("Diagnostic metric: {}", indicator),
                source: if has_source {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                baseline: if has_baseline {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                sample_size: if has_sample_size {
                    "present".to_string()
                } else {
                    "missing".to_string()
                },
                signal_strength: "moderate".to_string(),
                decision_usefulness: "diagnostic".to_string(),
                risk: "none".to_string(),
            });
        }
    }

    if metrics.is_empty() && vanity_metrics.is_empty() {
        missing_metrics.push("No specific metrics detected in context".to_string());
        open_questions.push("What specific metrics are being tracked?".to_string());
        open_questions.push("What is the success criterion for this test/campaign?".to_string());
    }

    if !has_baseline {
        attribution_limits.push("No baseline or comparison available".to_string());
        open_questions.push("What is the baseline or control to compare against?".to_string());
    }

    if !has_sample_size {
        open_questions.push("What is the sample size or data count?".to_string());
    }

    if !has_source {
        open_questions.push("What is the data source for these metrics?".to_string());
    }

    if causal_language {
        attribution_limits.push("Causal language detected without experiment/control".to_string());
        open_questions.push("Was this an controlled experiment or A/B test?".to_string());
    }

    if vanity_metrics.len() > 2 && !context_lower.contains("outcome") {
        attribution_limits.push("Heavy vanity metric focus without outcome metrics".to_string());
    }

    if (context_lower.contains("successful")
        || context_lower.contains("worked")
        || context_lower.contains("failed"))
        && !has_baseline
        && !context_lower.contains("experiment")
    {
        attribution_limits
            .push("Success/failure declared without baseline or experiment".to_string());
    }

    known_facts.push("Context contains metric-related language".to_string());

    let has_strong_signal = metrics.iter().any(|m| m.signal_strength == "strong");
    let recommended_decision = if !missing_metrics.is_empty() || attribution_limits.len() > 1 {
        "investigate".to_string()
    } else if vanity_metrics.len() > 2 && !metrics.iter().any(|m| m.metric_type == "outcome") {
        "iterate".to_string()
    } else if has_strong_signal {
        "keep".to_string()
    } else {
        "iterate".to_string()
    };

    let next_test = if causal_language || !has_baseline {
        "Design a controlled experiment or A/B test before drawing causal conclusions".to_string()
    } else if vanity_metrics.len() > 2 {
        "Add outcome metrics (conversion, revenue, qualified leads) to vanity metrics".to_string()
    } else {
        "Continue tracking and establish baseline for future comparison".to_string()
    };

    if recommended_decision == "investigate" {
        open_questions.push("What is the specific decision this metric should inform?".to_string());
    }

    AnalystSignalQualityReview {
        known_facts,
        metrics,
        vanity_metrics,
        missing_metrics,
        attribution_limits,
        recommended_decision,
        next_test,
        open_questions,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_derive_analyst_instinct_metric_missing() {
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

        let frame = derive_analyst_instinct_frame(&pack, "Did this work?", "No metrics defined");

        assert!(frame.risk_flags.contains(&"metric_missing".to_string()));
    }

    #[test]
    fn test_derive_analyst_instinct_baseline_missing() {
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

        let frame = derive_analyst_instinct_frame(
            &pack,
            "Evaluate performance",
            "100 impressions, 5 clicks",
        );

        assert!(frame.risk_flags.contains(&"baseline_missing".to_string()));
    }

    #[test]
    fn test_derive_analyst_instinct_causality_overclaimed() {
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

        let frame = derive_analyst_instinct_frame(
            &pack,
            "Campaign caused growth",
            "Revenue increased because of the campaign",
        );

        assert!(
            frame
                .risk_flags
                .contains(&"causality_overclaimed".to_string())
        );
    }

    #[test]
    fn test_derive_analyst_instinct_vanity_metric_risk() {
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

        let frame = derive_analyst_instinct_frame(
            &pack,
            "Campaign performance",
            "10000 impressions, 500 likes, 100 shares",
        );

        assert!(frame.risk_flags.contains(&"vanity_metric_risk".to_string()));
    }

    #[test]
    fn test_signal_quality_review_with_metrics() {
        let result = perform_signal_quality_review(
            "Evaluate campaign performance",
            "1000 impressions, 50 clicks, 5 conversions, revenue up 20%, baseline available, sample size 500",
        );

        assert!(!result.known_facts.is_empty());
        assert!(!result.metrics.is_empty());
        assert!(result.recommended_decision == "keep" || result.recommended_decision == "iterate");
    }

    #[test]
    fn test_signal_quality_review_vanity_only() {
        let result = perform_signal_quality_review(
            "Evaluate campaign",
            "10000 impressions, 500 likes, 100 shares",
        );

        assert!(!result.vanity_metrics.is_empty());
        assert!(!result.attribution_limits.is_empty());
    }

    #[test]
    fn test_signal_quality_review_missing_metrics() {
        let result = perform_signal_quality_review("Evaluate performance", "No data available yet");

        assert!(!result.missing_metrics.is_empty());
        assert!(result.recommended_decision == "investigate");
    }

    #[test]
    fn test_analyst_taboos_against_fake_metrics() {
        let taboos = build_analyst_taboos();
        assert!(taboos.iter().any(|t| t.contains("do not invent metrics")));
        assert!(taboos.iter().any(|t| t.contains("do not claim causality")));
    }

    #[test]
    fn test_analyst_identity_kernel() {
        let kernel = build_analyst_identity_kernel();
        let core_drive = kernel.get("core_drive").unwrap().as_str().unwrap();
        assert!(core_drive.contains("signal"));
        assert!(core_drive.contains("noise"));
    }

    #[test]
    fn test_analyst_worldview_activity_not_progress() {
        let worldview = build_analyst_worldview();
        assert!(
            worldview
                .iter()
                .any(|w| w.contains("Activity is not progress"))
        );
    }

    #[test]
    fn test_analyst_obsessions_signal_quality() {
        let obsessions = build_analyst_obsessions();
        assert!(obsessions.iter().any(|o| o.contains("signal quality")));
        assert!(obsessions.iter().any(|o| o.contains("KPI relevance")));
    }
}
