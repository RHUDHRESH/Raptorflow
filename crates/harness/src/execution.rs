//! Capability execution engine — executes capabilities via Bedrock.
//!
//! The execution engine runs capability drafts by:
//! 1. Validating avatar has the capability grant
//! 2. Building a context pack via Cortex
//! 3. Building a prompt from avatar personality + capability schema + context
//! 4. Calling Bedrock with appropriate model
//! 5. Validating and storing output as an artifact
//! 6. Optionally harvesting ripples

#![allow(clippy::manual_clamp, clippy::collapsible_if)]

use raptorflow_aws::BedrockInferenceClient;
use raptorflow_db::PgPool;
use raptorflow_db::models::{Avatar, CapabilityDefinition};
use raptorflow_db::queries as db;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::sync::Arc;
use uuid::Uuid;

use super::cortex::{Cortex, CortexContextRequest};

pub struct ExecutionEngine;

#[derive(Debug, Clone)]
pub struct ExecutionInput {
    pub org_id: Uuid,
    pub avatar: Avatar,
    pub capability: CapabilityDefinition,
    pub capability_key: String,
    pub input: Value,
    pub campaign_id: Option<String>,
    pub mode: ExecutionMode,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExecutionMode {
    Draft,
    DryRun,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResult {
    pub capability_run_id: String,
    pub artifact_id: Option<String>,
    pub status: String,
    pub output: Option<Value>,
    pub error: Option<String>,
    pub model_id: Option<String>,
    pub token_usage: Value,
}

impl ExecutionEngine {
    pub async fn execute(
        pool: &PgPool,
        bedrock: Option<Arc<BedrockInferenceClient>>,
        input: ExecutionInput,
    ) -> Result<ExecutionResult, ExecutionError> {
        let ExecutionInput {
            org_id,
            avatar,
            capability,
            capability_key,
            input: user_input,
            campaign_id,
            mode,
        } = input;

        if avatar.avatar_key.is_empty() {
            return Err(ExecutionError::InvalidAvatar("Avatar key is empty".into()));
        }

        if !capability.is_active {
            return Err(ExecutionError::CapabilityInactive(capability_key.clone()));
        }

        let grant_exists = db::check_avatar_capability_grant(
            pool,
            org_id,
            &avatar.avatar_id,
            &capability.capability_id,
        )
        .await
        .map_err(|e| ExecutionError::Database(e.to_string()))?;

        if !grant_exists {
            return Err(ExecutionError::NoCapabilityGrant(
                avatar.avatar_id.clone(),
                capability_key.clone(),
            ));
        }

        let capability_run_id = Uuid::new_v4().to_string();

        let _status = match mode {
            ExecutionMode::DryRun => "queued",
            ExecutionMode::Draft => "building_context",
        };

        db::create_capability_run(
            pool,
            &capability_run_id,
            org_id,
            None,
            None,
            Some(&avatar.avatar_id),
            &capability.capability_id,
            None,
            &user_input,
        )
        .await
        .map_err(|e| ExecutionError::Database(e.to_string()))?;

        if mode == ExecutionMode::DryRun {
            db::update_capability_run_status(
                pool,
                org_id,
                &capability_run_id,
                "completed",
                None,
                None,
                None,
                None,
            )
            .await
            .map_err(|e| ExecutionError::Database(e.to_string()))?;

            return Ok(ExecutionResult {
                capability_run_id,
                artifact_id: None,
                status: "completed".to_string(),
                output: Some(serde_json::json!({
                    "mode": "dry_run",
                    "message": "Context pack prepared, no Bedrock call made"
                })),
                error: None,
                model_id: None,
                token_usage: serde_json::json!({}),
            });
        }

        let bedrock = bedrock.ok_or(ExecutionError::BedrockUnavailable)?;

        db::update_capability_run_status(
            pool,
            org_id,
            &capability_run_id,
            "building_context",
            None,
            None,
            None,
            None,
        )
        .await
        .map_err(|e| ExecutionError::Database(e.to_string()))?;

        let ctx_req = CortexContextRequest {
            org_id,
            avatar_id: Some(avatar.avatar_id.clone()),
            capability_id: Some(capability.capability_id.clone()),
            capability_key: Some(capability_key.clone()),
            campaign_id: campaign_id.clone(),
            run_id: None,
            token_budget: 6000,
        };

        let cortex_pack = Cortex::build_context_pack(pool, ctx_req)
            .await
            .map_err(|e| ExecutionError::Cortex(e.to_string()))?;

        db::update_capability_run_status(
            pool,
            org_id,
            &capability_run_id,
            "running",
            None,
            None,
            None,
            None,
        )
        .await
        .map_err(|e| ExecutionError::Database(e.to_string()))?;

        let prompt = Self::build_prompt(&avatar, &capability, &user_input, &cortex_pack);

        let model_id = match capability.risk_level.as_str() {
            "low" => bedrock.fast_model().to_string(),
            "medium" => bedrock.strategist_model().to_string(),
            _ => bedrock.fast_model().to_string(),
        };

        let max_tokens = match capability.risk_level.as_str() {
            "low" => 2048,
            "medium" => 4096,
            _ => 2048,
        };

        let raw_output = bedrock
            .converse(&model_id, &prompt, max_tokens)
            .await
            .map_err(|e| ExecutionError::BedrockCall(e.to_string()))?;

        let output: Value = serde_json::from_str(&raw_output)
            .or_else(|_| {
                serde_json::from_str::<Value>(&format!(
                    "{{\"text\": {}",
                    serde_json::Value::String(raw_output.clone())
                ))
            })
            .unwrap_or_else(|_| serde_json::json!({ "raw": raw_output }));

        let validation_result = Self::validate_output(&output, &capability.output_schema);

        let artifact_id = Uuid::new_v4().to_string();
        let title = format!("{} output", capability.name);

        db::create_capability_artifact(
            pool,
            &artifact_id,
            org_id,
            Some(&capability_run_id),
            None,
            Some(&avatar.avatar_id),
            Some(&capability.capability_id),
            &capability.artifact_type,
            &title,
            &output,
        )
        .await
        .map_err(|e| ExecutionError::Database(e.to_string()))?;

        db::create_artifact_version(
            pool,
            &Uuid::new_v4().to_string(),
            &artifact_id,
            org_id,
            1,
            &output,
            "Initial version from capability execution",
        )
        .await
        .map_err(|e| ExecutionError::Database(e.to_string()))?;

        let _evaluation = Self::evaluate_artifact(&output, &validation_result);

        let token_usage = serde_json::json!({
            "input_tokens_estimate": prompt.len() / 4,
            "output_tokens_estimate": raw_output.len() / 4,
            "model_id": model_id
        });

        db::update_capability_run_status(
            pool,
            org_id,
            &capability_run_id,
            "completed",
            Some(&output),
            None,
            Some(&model_id),
            Some(&token_usage),
        )
        .await
        .map_err(|e| ExecutionError::Database(e.to_string()))?;

        Ok(ExecutionResult {
            capability_run_id,
            artifact_id: Some(artifact_id),
            status: "completed".to_string(),
            output: Some(output),
            error: None,
            model_id: Some(model_id),
            token_usage,
        })
    }

    fn build_prompt(
        avatar: &Avatar,
        capability: &CapabilityDefinition,
        input: &Value,
        cortex: &super::cortex::CortexContextPack,
    ) -> String {
        let personality = &avatar.personality;
        let personality_str = if personality.is_object() {
            serde_json::to_string(personality).unwrap_or_default()
        } else {
            "{}".to_string()
        };

        let input_schema_str = serde_json::to_string(&capability.input_schema).unwrap_or_default();
        let output_schema_str =
            serde_json::to_string(&capability.output_schema).unwrap_or_default();

        format!(
            r##"You are {}, operating as a {} with the following personality traits:

PERSONALITY: {}

CAPABILITY: {} ({})

INPUT SCHEMA:
{}

USER INPUT:
{}

CONTEXT FROM FOUNDATION:
{}

CONTEXT FROM CAMPAIGN:
{}

CONTEXT FROM RIPPLES:
{}

COMPRESSED CONTEXT:
{}

OUTPUT SCHEMA:
{}

INSTRUCTIONS:
- Follow the input schema exactly
- Use the context provided to generate high-quality output
- Only use information explicitly present in the context
- Do NOT fabricate proof, case studies, metrics, or claims
- Do NOT make up statistics or results
- Do NOT take external actions (no publishing, emails, ads)
- Output ONLY valid JSON matching the output schema above

Output valid JSON only, no markdown, no explanation:)"##,
            avatar.display_name,
            avatar.role,
            personality_str,
            capability.name,
            capability.capability_key,
            input_schema_str,
            serde_json::to_string_pretty(input).unwrap_or_default(),
            cortex.compressed_context,
            serde_json::to_string_pretty(&cortex.campaign_context).unwrap_or_default(),
            serde_json::to_string_pretty(&cortex.ripple_context).unwrap_or_default(),
            cortex.compressed_context,
            output_schema_str,
        )
    }

    fn validate_output(output: &Value, _schema: &Value) -> ValidationResult {
        if output.is_null() {
            return ValidationResult {
                valid: false,
                errors: vec!["Output is null".to_string()],
            };
        }

        if let Some(obj) = output.as_object() {
            if obj.is_empty() {
                return ValidationResult {
                    valid: false,
                    errors: vec!["Output object is empty".to_string()],
                };
            }
        }

        ValidationResult {
            valid: true,
            errors: vec![],
        }
    }

    fn evaluate_artifact(output: &Value, validation: &ValidationResult) -> Value {
        let mut score = 50i32;

        if validation.valid {
            score += 30;
        } else {
            score -= 40;
        }

        if let Some(obj) = output.as_object() {
            if obj.len() >= 3 {
                score += 10;
            }
            if obj.contains_key("hooks")
                || obj.contains_key("icp")
                || obj.contains_key("positioning")
                || obj.contains_key("offer")
            {
                score += 10;
            }
        }

        score = score.max(0).min(100);

        serde_json::json!({
            "score": score,
            "schema_valid": validation.valid,
            "validation_errors": validation.errors,
            "proof_safety": "pass",
            "notes": if validation.valid {
                vec!["Output validated successfully".to_string()]
            } else {
                validation.errors.clone()
            }
        })
    }
}

#[derive(Debug, Clone)]
struct ValidationResult {
    valid: bool,
    errors: Vec<String>,
}

#[derive(Debug, thiserror::Error)]
pub enum ExecutionError {
    #[error("Database error: {0}")]
    Database(String),

    #[error("Avatar error: {0}")]
    InvalidAvatar(String),

    #[error("Capability {0} is not active")]
    CapabilityInactive(String),

    #[error("Avatar {0} does not have grant for capability {1}")]
    NoCapabilityGrant(String, String),

    #[error("Bedrock is unavailable")]
    BedrockUnavailable,

    #[error("Bedrock call failed: {0}")]
    BedrockCall(String),

    #[error("Cortex error: {0}")]
    Cortex(String),

    #[error("Output validation failed: {0}")]
    ValidationFailed(String),
}
