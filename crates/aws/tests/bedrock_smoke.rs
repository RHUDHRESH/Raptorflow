//! Bedrock Reality Smoke Test
//!
//! Verifies AWS Bedrock can:
//! 1. Accept a tiny safe smoke prompt
//! 2. Return valid JSON with expected fields
//! 3. Confirm inference actually works
//!
//! # Environment
//!
//! - `BEDROCK_SMOKE_TEST=1` — required to run this test (never runs by default)
//! - AWS credentials via standard AWS env/provider chain
//! - `RAPTORFLOW_BEDROCK_REGION` — AWS region (e.g. ap-south-1)
//! - `RAPTORFLOW_BEDROCK_MODEL_FAST` — fast model ID
//!
//! # Rules
//!
//! - Does not run unless `BEDROCK_SMOKE_TEST=1`
//! - Never sends business/customer/org data
//! - Never calls large/strategist model
//! - Never logs AWS secrets
//! - Does not run in normal CI — manual trigger only
//!
//! Run with:
//! ```text
//! BEDROCK_SMOKE_TEST=1 cargo test -p raptorflow-aws --test bedrock_smoke -- --nocapture --test-threads=1
//! ```

use raptorflow_aws::BedrockInferenceClient;
use serde::Deserialize;
use std::env;

const SMOKE_PROMPT: &str = r#"Return exactly this JSON with no extra text:
{"ok":true,"component":"bedrock_smoke"}"#;

const MAX_TOKENS_SMOKE: i32 = 64;

#[derive(Debug, Deserialize)]
struct SmokeResponse {
    ok: bool,
    component: String,
}

fn is_smoke_enabled() -> bool {
    env::var("BEDROCK_SMOKE_TEST")
        .map(|v| v == "1")
        .unwrap_or(false)
}

fn get_region() -> Option<String> {
    env::var("RAPTORFLOW_BEDROCK_REGION").ok()
}

fn get_model_fast() -> Option<String> {
    env::var("RAPTORFLOW_BEDROCK_MODEL_FAST").ok()
}

fn env_info() -> String {
    format!(
        "BEDROCK_SMOKE_TEST={} RAPTORFLOW_BEDROCK_REGION={} RAPTORFLOW_BEDROCK_MODEL_FAST={}",
        env::var("BEDROCK_SMOKE_TEST").unwrap_or_default(),
        env::var("RAPTORFLOW_BEDROCK_REGION").unwrap_or_default(),
        env::var("RAPTORFLOW_BEDROCK_MODEL_FAST").unwrap_or_default(),
    )
}

#[tokio::test]
async fn bedrock_smoke_real_inference() {
    if !is_smoke_enabled() {
        println!("[SMOKE BEDROCK] SKIP: BEDROCK_SMOKE_TEST != 1 — Bedrock smoke test is disabled by default");
        println!("[SMOKE BEDROCK] This is intentional — Bedrock calls are expensive and require AWS credentials.");
        println!("[SMOKE BEDROCK] To run: BEDROCK_SMOKE_TEST=1 cargo test -p raptorflow-aws --test bedrock_smoke");
        return;
    }

    let region = match get_region() {
        Some(r) => {
            println!("[SMOKE BEDROCK] Region: {}", r);
            r
        }
        None => {
            panic!("[SMOKE BEDROCK] FAIL: RAPTORFLOW_BEDROCK_REGION not set (required when BEDROCK_SMOKE_TEST=1)");
        }
    };

    let model_fast = match get_model_fast() {
        Some(m) => {
            println!("[SMOKE BEDROCK] Fast model: {}", m);
            m
        }
        None => {
            panic!("[SMOKE BEDROCK] FAIL: RAPTORFLOW_BEDROCK_MODEL_FAST not set (required when BEDROCK_SMOKE_TEST=1)");
        }
    };

    println!("[SMOKE BEDROCK] Env: {}", env_info());
    println!("[SMOKE BEDROCK] Creating Bedrock client...");

    let client = match BedrockInferenceClient::new(&region).await {
        Ok(c) => {
            println!("[SMOKE BEDROCK] Client created successfully");
            c
        }
        Err(e) => {
            panic!(
                "[SMOKE BEDROCK] FAIL: Could not create Bedrock client: {}",
                e
            );
        }
    };

    println!("[SMOKE BEDROCK] Calling converse_fast with smoke prompt...");
    println!("[SMOKE BEDROCK] Prompt: {}", SMOKE_PROMPT);
    println!("[SMOKE BEDROCK] Model: {}", model_fast);
    println!("[SMOKE BEDROCK] Max tokens: {}", MAX_TOKENS_SMOKE);

    let output = match client
        .converse(&model_fast, SMOKE_PROMPT, MAX_TOKENS_SMOKE)
        .await
    {
        Ok(o) => {
            println!("[SMOKE BEDROCK] Raw response: {:?}", output);
            o
        }
        Err(e) => {
            panic!("[SMOKE BEDROCK] FAIL: Bedrock inference failed: {}", e);
        }
    };

    println!("[SMOKE BEDROCK] Raw output: {:?}", output);

    // Parse JSON response
    let parsed: SmokeResponse = match serde_json::from_str(&output) {
        Ok(p) => {
            println!(
                "[SMOKE BEDROCK] Parsed JSON: ok={}, component={}",
                p.ok, p.component
            );
            p
        }
        Err(e) => {
            panic!(
                "[SMOKE BEDROCK] FAIL: Response was not valid JSON: {}\nRaw response: {}",
                e, output
            );
        }
    };

    // Validate response fields
    if !parsed.ok {
        panic!(
            "[SMOKE BEDROCK] FAIL: Expected {{ok: true}}, got {{ok: false}}\nRaw response: {}",
            output
        );
    }

    if parsed.component != "bedrock_smoke" {
        panic!(
            "[SMOKE BEDROCK] FAIL: Expected {{component: \"bedrock_smoke\"}}, got {{component: \"{}\"}}\nRaw response: {}",
            parsed.component, output
        );
    }

    println!("[SMOKE BEDROCK] ALL CHECKS PASSED");
    println!("[SMOKE BEDROCK] Runtime reality verified: Bedrock inference is functional.");
}
