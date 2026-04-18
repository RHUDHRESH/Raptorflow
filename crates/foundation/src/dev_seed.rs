// ⚠️ DEV SEED — DELETE THIS FILE BEFORE PRODUCTION
// This file is excluded from release builds via Cargo feature gates.
// It allows developers to bypass the 21-screen onboarding flow.

#[cfg(feature = "dev-seed")]
use axum::{
    extract::State,
    http::{header, StatusCode},
    response::IntoResponse,
    Json,
};
#[cfg(feature = "dev-seed")]
use serde_json::json;
#[cfg(feature = "dev-seed")]
use crate::AppState; // Assuming state exists in crate root or similar
#[cfg(feature = "dev-seed")]
use auth::ClerkUser; // Assuming auth middleware provides this
#[cfg(feature = "dev-seed")]
use sqlx::PgPool;

#[cfg(feature = "dev-seed")]
pub async fn seed_foundation_handler(
    State(pool): State<PgPool>,
    user: ClerkUser, // Custom extractor for Clerk JWT
) -> impl IntoResponse {
    let org_id = user.org_id;

    // 1. COMPILATION OF FOUNDATION DATA
    let sections = vec![
        ("url", json!({ "url": "https://verdantnaturals.co.in" })),
        ("scan_results", json!({
            "businessName": "Verdant Naturals",
            "extractedDescription": "A premium D2C organic skincare brand focusing on cold-pressed botanical oils.",
            "categories": ["Skincare", "D2C", "Wellness"]
        })),
        ("stage_team", json!({ "stage": "growing", "teamSize": "5-15" })),
        ("product_details", json!({ "primaryProduct": "Revitalizing Face Serum", "description": "100% organic, cold-pressed serum." })),
        ("customer_problem", json!({ "problem": "Competitors use synthetic 'natural' labels; customers can't verify purity." })),
        ("icp", json!({ "primaryICP": { "name": "The Urban Wellness Buyer", "demographics": "25-35F, Tier 1 cities" } })),
        ("transformation", json!({ "before": "Confused about ingredient labels", "after": "Confidence in pure botanical potency" })),
        ("competitors", json!({ "direct": [{"name": "Mamaearth", "competitor_url": "https://mamaearth.in", "tracking_enabled": true}], "indirect": [{"name": "Plum Goodness", "competitor_url": "https://plumgoodness.com", "tracking_enabled": true}] })),
        ("pricing", json!({ "model": "D2C / E-commerce", "range": "₹800 - ₹2,500" })),
        ("positioning", json!({
            "statement": "For the wellness-conscious professional, Verdant Naturals provides verified botanical potency.",
            "template_components": {
                "for_who": "wellness-conscious professionals",
                "who_problem": "face challenges with ingredient verification",
                "brand": "Verdant Naturals",
                "category": "organic skincare brand",
                "differentiation": "provides verified botanical potency",
                "because": "unlike competitors, we guarantee purity through cold-pressed extraction"
            },
            "quality_score": 0.85,
            "quality_feedback": "Clear value proposition with strong differentiation. Consider adding specific metrics for 'verified potency'.",
            "is_locked": false
        })),
        ("brand_voice_descriptors", json!(["authentic", "educational", "empowering", "natural"])),
        ("writing_samples", json!([
            {
                "prompt": "Describe our serum to a new customer",
                "output": "Our cold-pressed serum delivers the purest botanical extracts directly to your skin, verified for potency and free from synthetic additives."
            },
            {
                "prompt": "Explain why natural ingredients matter",
                "output": "Nature provides the most effective ingredients when extracted properly. We cold-press our botanicals to preserve their natural potency."
            },
            {
                "prompt": "Address a customer concern about price",
                "output": "Quality ingredients and careful extraction come at a premium. We're investing in your skin's long-term health, not short-term marketing."
            }
        ])),
        ("voice_fingerprint", json!([0.1, -0.2, 0.3, 0.4, -0.1, 0.2, -0.3, 0.0, 0.5, -0.4, 0.1, 0.2, -0.3, 0.4, -0.2, 0.3, 0.1, -0.5, 0.2, 0.0, -0.1, 0.3, -0.2, 0.4, 0.1, -0.3, 0.2, 0.0, -0.4, 0.1, 0.2, -0.3, 0.4, -0.1, 0.2, 0.3, -0.4, 0.1, -0.2, 0.3, 0.0, -0.1, 0.4, -0.3, 0.2, 0.1, -0.5, 0.3, -0.2, 0.4, 0.0, -0.1, 0.2, -0.3, 0.4, 0.1, -0.2, 0.3, 0.0, -0.4, 0.2, 0.1, -0.3, 0.4, -0.1])),
        ("brand_personality", json!({ "casual": 70, "playful": 65, "bold": 75, "guardrails": ["No jargon", "No medical claims"] })),
        ("brand_voice_sliders", json!({ "formality": 0.6, "technicality": 0.4, "tone": 0.7, "stance": 0.8, "register": 0.6 })),
        ("keywords", json!({ "primary": ["organic serum india", "cold pressed skincare", "botanical face oil"] })),
        ("content_channels", json!({ "priority": ["Instagram", "Email"], "secondary": ["LinkedIn"] })),
        ("content_history", json!({ "tried": ["Instagram Reels", "Facebook Ads"], "frustration": "High CAC on Meta ads" })),
        ("primary_goal", json!({ 
            "goal": "awareness", 
            "target_90d": "₹50 leads/month target",
            "strategistName": "ARIA",
            "personality": ["Direct", "Challenger", "Data-driven"]
        })),
        ("budget", json!({ "range": "₹50,000 - ₹2,00,000", "allocation": "Ads & Content" })),
        ("existing_assets", json!({ "logos": true, "guidelines": true, "social_handles": ["@verdantnaturals"] })),
        ("frustrations", json!({ "top": ["Creativity block", "Lack of measurement"] })),
        ("analytics", json!({ "tools": ["Google Analytics", "Meta Pixel"] })),
        ("reference_brands", json!({ "admired": ["The Ordinary", "Forest Essentials"] })),
        ("strategist_config", json!({ "name": "ARIA", "voice": "Direct" }))
    ];

    // 2. TRANSACTIONAL UPSERT
    let mut tx = pool.begin().await.map_err(|_| StatusCode::INTERNAL_SERVER_ERROR).unwrap();

    // Update Org Status
    sqlx::query!(
        "UPDATE orgs SET foundation_complete = true WHERE id = $1",
        org_id
    )
    .execute(&mut *tx)
    .await
    .unwrap();

    // Seed Sections
    for (key, data) in sections {
        sqlx::query!(
            "INSERT INTO foundation_sections (org_id, section_id, data) 
             VALUES ($1, $2, $3) 
             ON CONFLICT (org_id, section_id) DO UPDATE SET data = $3",
            org_id,
            key,
            data
        )
        .execute(&mut *tx)
        .await
        .unwrap();
    }

    // 3. AGENT INITIALIZATION
    // Assuming crates/eel provides this via initialization logic
    // we call the standard library init here
    // eel::init_org_agents(&org_id, &mut tx).await.unwrap();

    tx.commit().await.unwrap();

    // 4. RESPONSE WITH COOKIE
    let cookie = "foundation_complete=true; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000";
    
    (
        StatusCode::OK,
        [
            (header::SET_COOKIE, cookie),
            (header::CONTENT_TYPE, "application/json"),
        ],
        Json(json!({
            "ok": true,
            "org_id": org_id,
            "strategist_name": "ARIA"
        })),
    ).into_response()
}

#[cfg(not(feature = "dev-seed"))]
pub async fn seed_foundation_handler() -> impl IntoResponse {
    (StatusCode::NOT_FOUND, "Dev seed feature not enabled").into_response()
}
