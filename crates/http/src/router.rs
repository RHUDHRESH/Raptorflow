use axum::{
    extract::Extension,
    routing::{delete, get, post, put},
    Router,
};
use tower_http::cors::{Any, CorsLayer};

use crate::middleware::{AppState, auth::auth_middleware, rate_limit::{RateLimitLayer, RateLimitState, RateLimitConfig}};
use crate::routes::{auth, billing, council, foundation, health, muse, prl, uploads};

fn cors_layer(state: &AppState) -> CorsLayer {
    let layer = CorsLayer::new()
        .allow_methods(Any)
        .allow_headers(Any)
        .max_age(std::time::Duration::from_secs(86400));

    if state.settings.app_env == "prod" {
        // # FIXED: handle invalid frontend_url gracefully instead of unwrap
        match state.settings.frontend_url.as_str().parse::<axum::http::HeaderValue>() {
            Ok(origin) => layer.allow_origin(origin),
            Err(_) => {
                tracing::warn!("Invalid RAPTORFLOW_FRONTEND_URL '{}', falling back to Any", state.settings.frontend_url);
                layer.allow_origin(Any)
            }
        }
    } else {
        layer.allow_origin(Any)
    }
}

fn public_router(_state: &AppState) -> Router { // # FIXED: underscore prefix since state is unused but may be needed later for config
    // # FIXED: apply RateLimitLayer::per_ip() to public webhook endpoints
    let rate_limit_state = RateLimitState::new(
        RateLimitConfig::strict() // 30 requests per minute, burst size 5
    );
    
    Router::new()
        .route("/health", get(health::health_check))
        .route("/api/v1/webhooks/clerk", post(auth::clerk_webhook))
        .route("/api/v1/webhooks/razorpay", post(billing::razorpay_webhook))
        .layer(RateLimitLayer::per_ip(rate_limit_state))
}

fn protected_router() -> Router {
    Router::new()
        .route("/api/v1/billing", get(billing::billing_status))
        .route("/api/v1/billing/orders", post(billing::create_order))
        .route("/api/v1/billing/subscriptions/{id}", get(billing::get_subscription))
        .route("/api/v1/billing/subscriptions/{id}/cancel", post(billing::cancel_subscription))
        .route("/api/v1/uploads", post(uploads::generate_upload_url))
        .route("/api/v1/uploads/download", get(uploads::generate_download_url))
        .route("/api/v1/uploads/{key}", delete(uploads::delete_upload))
        .route("/api/v1/screenshots", post(uploads::generate_screenshot_upload_url))
        .route("/api/v1/exports", post(uploads::generate_export_url))
        .route("/api/v1/exports/download", get(uploads::generate_export_download_url))
        .route("/api/v1/council", post(council::start_session))
        .route("/api/v1/council/history", get(council::list_sessions))
        .route("/api/v1/council/{session_id}", get(council::get_session))
        .route("/api/v1/council/{session_id}/messages", get(council::get_session_messages))
        .route("/api/v1/muse", post(muse::submit_prompt))
        .route("/api/v1/muse/history", get(muse::list_conversations))
        .route("/api/v1/muse/{conversation_id}", get(muse::get_conversation))
        .route("/api/v1/muse/{conversation_id}/messages", get(muse::get_messages))
        .route("/api/v1/foundation", get(foundation::get_foundation))
        .route("/api/v1/foundation", post(foundation::create_foundation))
        .route("/api/v1/foundation/sections/{section}", put(foundation::update_section))
        .route("/api/v1/foundation/snapshots", get(foundation::list_snapshots))
        .route("/api/v1/foundation/snapshots", post(foundation::create_snapshot))
        .route("/api/v1/foundation/snapshots/{id}/restore", post(foundation::restore_snapshot))
        .route("/api/v1/foundation/snapshots/{id}", get(foundation::get_snapshot))
        .route("/api/v1/foundation/scan", post(foundation::trigger_scan))
        .route("/api/v1/foundation/scan/{job_id}", get(foundation::get_scan_status))
        .route("/api/v1/ripples", get(prl::list_ripples))
        .route("/api/v1/ripples", post(prl::create_ripple))
        .route("/api/v1/ripples/{id}", get(prl::get_ripple))
        .route("/api/v1/ripples/{id}", put(prl::update_ripple))
        .route("/api/v1/ripples/{id}", delete(prl::delete_ripple))
        .route("/api/v1/ripples/{id}/realize", post(prl::realize_ripple))
        .route("/api/v1/ripples/{id}/edges", get(prl::get_ripple_edges))
        .route("/api/v1/ripples/{id}/edges", post(prl::create_ripple_edge))
        .route("/api/v1/ripples/edges/{edge_id}", delete(prl::delete_ripple_edge))
        .route("/api/v1/essences", get(prl::list_essences))
        .route("/api/v1/essences", post(prl::create_essence))
        .route("/api/v1/essences/{id}", get(prl::get_essence))
        .route("/api/v1/essences/{id}", put(prl::update_essence))
        .route("/api/v1/prl/decay", post(prl::run_decay))
        .layer(axum::middleware::from_fn(auth_middleware))
}

pub fn create_router(state: AppState) -> Router {
    let public = public_router(&state); // # FIXED: pass state to public_router for rate limiting
    let protected = protected_router();

    Router::new()
        .layer(cors_layer(&state))
        .layer(Extension(state))
        .merge(public)
        .merge(protected)
}
