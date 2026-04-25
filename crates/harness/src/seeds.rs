//! Default capability definitions — seeds the 5 safe marketing capabilities.
//!
//! These capabilities are intentionally scoped to safe drafting activities:
//! - No external publishing, email sending, or ad launching
//! - No fabricated proof or metrics
//! - All output is marked draft/review status

use raptorflow_db::PgPool;
use raptorflow_db::queries as db;
use uuid::Uuid;

pub struct CapabilitySeeder;

impl CapabilitySeeder {
    pub async fn seed_default_capabilities(pool: &PgPool) -> Result<(), CapabilitySeedError> {
        let capabilities = Self::get_default_capabilities();
        let count = capabilities.len();

        for cap in &capabilities {
            db::upsert_capability_definition(
                pool,
                &cap.capability_id,
                &cap.capability_key,
                &cap.name,
                &cap.domain,
                &cap.description,
                &cap.input_schema,
                &cap.output_schema,
                &cap.required_context,
                &cap.allowed_tools,
                &cap.artifact_type,
                &cap.evaluator_key,
                &cap.ripple_policy,
                &cap.risk_level,
            )
            .await
            .map_err(|e| CapabilitySeedError::Database(e.to_string()))?;
        }

        tracing::info!(count = count, "Seeded default capability definitions");

        Ok(())
    }

    fn get_default_capabilities() -> Vec<CapabilityRecord> {
        vec![
            CapabilityRecord {
                capability_id: Uuid::new_v4().to_string(),
                capability_key: "foundation.icp.refine".to_string(),
                name: "Refine Ideal Customer Profile".to_string(),
                domain: "foundation".to_string(),
                description: "Refine and validate the Ideal Customer Profile based on company info and market signals.".to_string(),
                input_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "company_description": {
                            "type": "string",
                            "description": "Current company description or positioning"
                        },
                        "existing_icp": {
                            "type": "object",
                            "description": "Existing ICP if available"
                        },
                        "refinement_focus": {
                            "type": "string",
                            "enum": ["demographics", "psychographics", "behaviors", "pain_points", "all"],
                            "default": "all"
                        }
                    },
                    "required": ["company_description"]
                }),
                output_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "refined_icp": {
                            "type": "object",
                            "properties": {
                                "demographics": {
                                    "type": "object",
                                    "properties": {
                                        "role": { "type": "string" },
                                        "industry": { "type": "string" },
                                        "company_size": { "type": "string" },
                                        " seniority": { "type": "string" }
                                    }
                                },
                                "psychographics": {
                                    "type": "object",
                                    "properties": {
                                        "values": { "type": "array", "items": { "type": "string" } },
                                        "fears": { "type": "array", "items": { "type": "string" } },
                                        "aspirations": { "type": "array", "items": { "type": "string" } }
                                    }
                                },
                                "behaviors": {
                                    "type": "object",
                                    "properties": {
                                        "content_consumption": { "type": "array", "items": { "type": "string" } },
                                        "purchase_patterns": { "type": "array", "items": { "type": "string" } }
                                    }
                                },
                                "pain_points": {
                                    "type": "array",
                                    "items": { "type": "string" }
                                }
                            }
                        },
                        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
                        "learnings": {
                            "type": "array",
                            "items": { "type": "string" }
                        }
                    }
                }),
                required_context: serde_json::json!({
                    "foundation": ["company_info", "target_audience"],
                    "intel": false,
                    "campaign": false,
                    "ripples": true
                }),
                allowed_tools: serde_json::json!(["bedrock.fast"]),
                artifact_type: "icp_refined".to_string(),
                evaluator_key: "default".to_string(),
                ripple_policy: serde_json::json!({
                    "extract": true,
                    "max_ripples": 3,
                    "types": ["audience_learning", "foundation_learning"]
                }),
                risk_level: "low".to_string(),
            },
            CapabilityRecord {
                capability_id: Uuid::new_v4().to_string(),
                capability_key: "foundation.positioning.generate".to_string(),
                name: "Generate Positioning Statement".to_string(),
                domain: "positioning".to_string(),
                description: "Generate positioning statements based on ICP and differentiation vectors.".to_string(),
                input_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "icp_summary": {
                            "type": "string",
                            "description": "Summary of the target ICP"
                        },
                        "differentiation": {
                            "type": "string",
                            "description": "Key differentiator or unique value proposition"
                        },
                        "competing_alternatives": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "What alternatives the ICP considers"
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["bold", "empathetic", "rational", "playful"],
                            "default": "bold"
                        }
                    },
                    "required": ["icp_summary", "differentiation"]
                }),
                output_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "positioning_statements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "statement": { "type": "string" },
                                    "variant": { "type": "string" }
                                }
                            }
                        },
                        "tagline_options": {
                            "type": "array",
                            "items": { "type": "string" }
                        },
                        "proof_requirements": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "What proof/evidence would strengthen this positioning"
                        },
                        "learnings": {
                            "type": "array",
                            "items": { "type": "string" }
                        }
                    }
                }),
                required_context: serde_json::json!({
                    "foundation": ["company_info", "target_audience", "value_proposition", "competitive_positioning"],
                    "intel": true,
                    "campaign": false,
                    "ripples": true
                }),
                allowed_tools: serde_json::json!(["bedrock.fast"]),
                artifact_type: "positioning".to_string(),
                evaluator_key: "default".to_string(),
                ripple_policy: serde_json::json!({
                    "extract": true,
                    "max_ripples": 3,
                    "types": ["positioning_learning"]
                }),
                risk_level: "low".to_string(),
            },
            CapabilityRecord {
                capability_id: Uuid::new_v4().to_string(),
                capability_key: "offer.core.design".to_string(),
                name: "Design Core Offer".to_string(),
                domain: "offer".to_string(),
                description: "Design core offer structure including pricing, packaging, and value metrics.".to_string(),
                input_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "positioning_summary": {
                            "type": "string",
                            "description": "Current positioning or value proposition"
                        },
                        "target_customer": {
                            "type": "string",
                            "description": "Description of target customer segment"
                        },
                        "existing_offer": {
                            "type": "string",
                            "description": "Current offer if any"
                        },
                        "pricing_objective": {
                            "type": "string",
                            "enum": ["premium", "value", "competitive", "penetration"],
                            "default": "value"
                        }
                    },
                    "required": ["positioning_summary", "target_customer"]
                }),
                output_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "offer_components": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": { "type": "string" },
                                    "description": { "type": "string" },
                                    "included": { "type": "boolean" },
                                    "tier": { "type": "string" }
                                }
                            }
                        },
                        "pricing_structure": {
                            "type": "object",
                            "properties": {
                                "entry_price": { "type": "number" },
                                "core_price": { "type": "number" },
                                "premium_price": { "type": "number" },
                                "currency": { "type": "string", "default": "USD" }
                            }
                        },
                        "value_metrics": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "How the customer measures value"
                        },
                        "proof_requirements": {
                            "type": "array",
                            "items": { "type": "string" }
                        },
                        "learnings": {
                            "type": "array",
                            "items": { "type": "string" }
                        }
                    }
                }),
                required_context: serde_json::json!({
                    "foundation": ["company_info", "target_audience", "value_proposition"],
                    "intel": false,
                    "campaign": true,
                    "ripples": true
                }),
                allowed_tools: serde_json::json!(["bedrock.fast"]),
                artifact_type: "offer_design".to_string(),
                evaluator_key: "default".to_string(),
                ripple_policy: serde_json::json!({
                    "extract": true,
                    "max_ripples": 2,
                    "types": ["value_learning"]
                }),
                risk_level: "medium".to_string(),
            },
            CapabilityRecord {
                capability_id: Uuid::new_v4().to_string(),
                capability_key: "copy.hooks.generate".to_string(),
                name: "Generate Copy Hooks".to_string(),
                domain: "copy".to_string(),
                description: "Generate compelling copy hooks for ads, emails, or content based on offer and ICP.".to_string(),
                input_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["linkedin", "twitter", "email", "facebook", "instagram", "google"],
                            "description": "Target platform for hooks"
                        },
                        "count": {
                            "type": "integer",
                            "minimum": 5,
                            "maximum": 30,
                            "default": 20,
                            "description": "Number of hooks to generate"
                        },
                        "angle": {
                            "type": "string",
                            "enum": ["founder_led", "proof_led", "benefit_led", "pain_led", "contrast", "question"],
                            "default": "benefit_led",
                            "description": "Primary hook angle"
                        },
                        "offer_summary": {
                            "type": "string",
                            "description": "Brief summary of the offer"
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["bold", "curious", "empathetic", "provocative", "educational"],
                            "default": "bold"
                        }
                    },
                    "required": ["platform", "offer_summary"]
                }),
                output_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "hooks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": { "type": "string" },
                                    "type": { "type": "string" },
                                    "angle": { "type": "string" },
                                    "salience": { "type": "number", "minimum": 0, "maximum": 1 }
                                }
                            }
                        },
                        "winning_angles": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Angles most likely to resonate"
                        },
                        "proof_gaps": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Proof points needed to support these hooks"
                        },
                        "learnings": {
                            "type": "array",
                            "items": { "type": "string" }
                        }
                    }
                }),
                required_context: serde_json::json!({
                    "foundation": ["target_audience", "value_proposition"],
                    "intel": false,
                    "campaign": true,
                    "ripples": true
                }),
                allowed_tools: serde_json::json!(["bedrock.fast"]),
                artifact_type: "hook_set".to_string(),
                evaluator_key: "default".to_string(),
                ripple_policy: serde_json::json!({
                    "extract": true,
                    "max_ripples": 3,
                    "types": ["copy_learning", "hook_learning"]
                }),
                risk_level: "low".to_string(),
            },
            CapabilityRecord {
                capability_id: Uuid::new_v4().to_string(),
                capability_key: "content.calendar.plan".to_string(),
                name: "Plan Content Calendar".to_string(),
                domain: "content".to_string(),
                description: "Generate a content calendar aligned with campaigns and marketing motions.".to_string(),
                input_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "campaign_goal": {
                            "type": "string",
                            "description": "Primary campaign or marketing goal"
                        },
                        "duration_weeks": {
                            "type": "integer",
                            "minimum": 2,
                            "maximum": 12,
                            "default": 4
                        },
                        "content_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["blog", "social", "email", "video", "podcast", "webinar"]
                            },
                            "description": "Types of content to include"
                        },
                        "platforms": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Target platforms"
                        },
                        "cadence": {
                            "type": "string",
                            "enum": ["daily", "every_other_day", "weekly", "biweekly"],
                            "default": "weekly"
                        }
                    },
                    "required": ["campaign_goal", "duration_weeks"]
                }),
                output_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "calendar": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "week": { "type": "integer" },
                                    "date": { "type": "string" },
                                    "content_type": { "type": "string" },
                                    "platform": { "type": "string" },
                                    "topic": { "type": "string" },
                                    "angle": { "type": "string" },
                                    "call_to_action": { "type": "string" }
                                }
                            }
                        },
                        "themes": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Weekly themes or focus areas"
                        },
                        "coverage_analysis": {
                            "type": "object",
                            "properties": {
                                "platform_coverage": { "type": "object" },
                                "content_type_coverage": { "type": "object" },
                                "gaps": { "type": "array", "items": { "type": "string" } }
                            }
                        },
                        "learnings": {
                            "type": "array",
                            "items": { "type": "string" }
                        }
                    }
                }),
                required_context: serde_json::json!({
                    "foundation": ["target_audience", "value_proposition"],
                    "intel": false,
                    "campaign": true,
                    "ripples": true
                }),
                allowed_tools: serde_json::json!(["bedrock.fast"]),
                artifact_type: "calendar_plan".to_string(),
                evaluator_key: "default".to_string(),
                ripple_policy: serde_json::json!({
                    "extract": true,
                    "max_ripples": 2,
                    "types": ["content_learning"]
                }),
                risk_level: "low".to_string(),
            },
        ]
    }
}

struct CapabilityRecord {
    capability_id: String,
    capability_key: String,
    name: String,
    domain: String,
    description: String,
    input_schema: serde_json::Value,
    output_schema: serde_json::Value,
    required_context: serde_json::Value,
    allowed_tools: serde_json::Value,
    artifact_type: String,
    evaluator_key: String,
    ripple_policy: serde_json::Value,
    risk_level: String,
}

#[derive(Debug, thiserror::Error)]
pub enum CapabilitySeedError {
    #[error("Database error: {0}")]
    Database(String),
}
