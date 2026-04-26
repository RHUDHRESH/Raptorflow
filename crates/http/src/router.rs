use axum::{
    Router,
    extract::Extension,
    routing::{delete, get, patch, post, put},
};
use std::sync::Arc;
use tower_http::cors::{Any, CorsLayer};

use crate::middleware::{
    AppState,
    auth::auth_middleware,
    rate_limit::{RateLimitConfig, RateLimitLayer, RateLimitState},
};
use crate::routes::{
    analyst_soul, auth, avatar_soul, avatars, billing, campaigns, capabilities, content,
    copywriter_soul, council, council_orchestration, creative_director_soul, daily_wins,
    foundation, growth_operator_soul, harness, health, intel, jobs, muse, nudges, office, prl,
    proof_collector_soul, replan, researcher_soul, strategist_soul,
};

fn cors_layer(state: &AppState) -> CorsLayer {
    let layer = CorsLayer::new()
        .allow_methods(Any)
        .allow_headers(Any)
        .max_age(std::time::Duration::from_secs(86400));

    if state.settings.app_env == "prod" {
        // # FIXED: handle invalid frontend_url gracefully instead of unwrap
        match state
            .settings
            .frontend_url
            .as_str()
            .parse::<axum::http::HeaderValue>()
        {
            Ok(origin) => layer.allow_origin(origin),
            Err(_) => {
                tracing::warn!(
                    "Invalid RAPTORFLOW_FRONTEND_URL '{}', falling back to Any",
                    state.settings.frontend_url
                );
                layer.allow_origin(Any)
            }
        }
    } else {
        layer.allow_origin(Any)
    }
}

fn public_router(_state: &AppState) -> Router {
    // # FIXED: underscore prefix since state is unused but may be needed later for config
    // # FIXED: apply RateLimitLayer::per_ip() to public webhook endpoints
    let rate_limit_state = RateLimitState::new(
        RateLimitConfig::strict(), // 30 requests per minute, burst size 5
    );

    Router::new()
        .route("/health", get(health::liveness))
        .route("/health/live", get(health::liveness))
        .route("/health/ready", get(health::readiness))
        .route("/api/v1/webhooks/clerk", post(auth::clerk_webhook))
        .route("/api/v1/webhooks/razorpay", post(billing::razorpay_webhook))
        .layer(RateLimitLayer::per_ip(rate_limit_state))
}

fn protected_router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/api/v1/foundation", get(foundation::get_foundation))
        .route("/api/v1/foundation", post(foundation::create_foundation))
        .route(
            "/api/v1/foundation/scan/start",
            post(foundation::start_scan),
        )
        .route(
            "/api/v1/foundation/scan/quick",
            post(foundation::start_quick_scan),
        )
        .route(
            "/api/v1/foundation/scan/deep",
            post(foundation::start_deep_scan),
        )
        .route(
            "/api/v1/foundation/scan/status",
            get(foundation::get_scan_status),
        )
        .route(
            "/api/v1/foundation/scan/update",
            post(foundation::update_scan),
        )
        .route(
            "/api/v1/foundation/scan/{scan_id}",
            get(foundation::get_scan_by_id),
        )
        .route(
            "/api/v1/foundation/competitor-snapshots",
            post(foundation::create_competitor_snapshot),
        )
        .route(
            "/api/v1/foundation/competitor-snapshots/{snapshot_id}",
            put(foundation::update_competitor_snapshot),
        )
        .route(
            "/api/v1/foundation/competitor-snapshots",
            get(foundation::get_latest_competitor_snapshot),
        )
        .route(
            "/api/v1/foundation/content/strategy",
            get(foundation::content_strategy_get),
        )
        .route(
            "/api/v1/foundation/content/strategy",
            put(foundation::content_strategy_create),
        )
        .route(
            "/api/v1/foundation/content/territories",
            post(foundation::content_strategy_update_territories),
        )
        .route(
            "/api/v1/foundation/content/territories",
            get(foundation::content_strategy_get),
        )
        .route(
            "/api/v1/foundation/content/calendar",
            get(foundation::content_strategy_generate_calendar),
        )
        .route(
            "/api/v1/foundation/icp/secondary",
            post(foundation::add_secondary_icp),
        )
        .route(
            "/api/v1/foundation/icp/secondary/{index}",
            put(foundation::update_secondary_icp),
        )
        .route(
            "/api/v1/foundation/icp/secondary/{index}",
            delete(foundation::delete_secondary_icp),
        )
        .route(
            "/api/v1/foundation/positioning/draft",
            post(foundation::generate_positioning_draft),
        )
        .route(
            "/api/v1/foundation/positioning/lock",
            post(foundation::lock_positioning),
        )
        .route(
            "/api/v1/foundation/section/{section}",
            patch(foundation::update_section),
        )
        .route(
            "/api/v1/foundation/snapshot",
            get(foundation::get_snapshot_full),
        )
        .route(
            "/api/v1/foundation/complete",
            post(foundation::complete_foundation),
        )
        .route(
            "/api/v1/foundation/snapshots",
            get(foundation::list_snapshots),
        )
        .route(
            "/api/v1/foundation/versions",
            get(foundation::list_foundation_versions),
        )
        .route(
            "/api/v1/foundation/snapshots",
            post(foundation::create_snapshot),
        )
        .route(
            "/api/v1/foundation/snapshots/{id}/restore",
            post(foundation::restore_snapshot),
        )
        .route(
            "/api/v1/foundation/snapshots/{id}",
            get(foundation::get_snapshot),
        )
        .route("/api/v1/prl/ripples", get(prl::list_ripples))
        .route("/api/v1/prl/ripples", post(prl::create_ripple))
        .route("/api/v1/prl/ripples/{id}", get(prl::get_ripple))
        .route("/api/v1/prl/ripples/{id}", put(prl::update_ripple))
        .route("/api/v1/prl/ripples/{id}", delete(prl::delete_ripple))
        .route("/api/v1/prl/ripples/{id}/edges", get(prl::get_ripple_edges))
        .route(
            "/api/v1/prl/ripples/{id}/edges",
            post(prl::create_ripple_edge),
        )
        .route(
            "/api/v1/prl/ripples/edges/{edge_id}",
            delete(prl::delete_ripple_edge),
        )
        .route("/api/v1/prl/essences", get(prl::list_essences))
        .route("/api/v1/prl/essences", post(prl::create_essence))
        .route("/api/v1/prl/essences/{id}", get(prl::get_essence))
        .route("/api/v1/prl/essences/{id}", put(prl::update_essence))
        .route("/api/v1/prl/decay", post(prl::run_decay))
        .route("/api/v1/intel", get(intel::list_intel_overview))
        .route("/api/v1/intel/runs", get(intel::list_research_runs))
        .route("/api/v1/intel/documents", get(intel::list_documents))
        .route("/api/v1/intel/signals", get(intel::list_signals))
        .route(
            "/api/v1/intel/signals/{id}",
            get(intel::get_signal).patch(intel::update_signal),
        )
        .route(
            "/api/v1/intel/competitors",
            get(intel::list_competitor_snapshots).post(intel::create_competitor_snapshot),
        )
        .route(
            "/api/v1/campaigns",
            get(campaigns::list_campaigns).post(campaigns::create_campaign),
        )
        .route("/api/v1/campaigns/{id}", get(campaigns::get_campaign))
        .route(
            "/api/v1/campaigns/{id}/status",
            patch(campaigns::update_campaign_status),
        )
        .route(
            "/api/v1/campaigns/{id}/moves",
            get(campaigns::list_moves).post(campaigns::create_move),
        )
        .route(
            "/api/v1/campaigns/{id}/moves/{move_id}/status",
            patch(campaigns::update_move_status),
        )
        .route(
            "/api/v1/campaigns/{id}/tasks",
            get(campaigns::list_tasks).post(campaigns::create_task),
        )
        .route(
            "/api/v1/campaigns/{id}/tasks/{task_id}/status",
            patch(campaigns::update_task_status),
        )
        .route(
            "/api/v1/campaigns/{id}/brief",
            get(campaigns::get_brief).post(campaigns::create_brief),
        )
        .route(
            "/api/v1/campaigns/{id}/brief/status",
            patch(campaigns::update_brief_status),
        )
        .route(
            "/api/v1/campaigns/{id}/evaluate",
            post(campaigns::evaluate_campaign),
        )
        .route(
            "/api/v1/campaigns/{id}/moves/generate",
            post(campaigns::generate_campaign_moves),
        )
        .route(
            "/api/v1/campaigns/{id}/replan",
            get(replan::list_replans).post(replan::trigger_replan),
        )
        .route(
            "/api/v1/content",
            get(content::list_content).post(content::create_content),
        )
        .route("/api/v1/content/{id}", get(content::get_content))
        .route("/api/v1/jobs/research", post(jobs::accept_research_request))
        .route(
            "/api/v1/jobs/tool-gateway",
            post(jobs::accept_tool_gateway_request),
        )
        .route(
            "/api/v1/nudges",
            get(nudges::list_nudges).post(nudges::create_nudge),
        )
        .route("/api/v1/nudges/{id}", get(nudges::get_nudge))
        .route("/api/v1/nudges/{id}/viewed", post(nudges::mark_viewed))
        .route(
            "/api/v1/nudges/{id}/dismissed",
            post(nudges::mark_dismissed),
        )
        .route(
            "/api/v1/daily-wins",
            get(daily_wins::list_daily_wins).post(daily_wins::create_daily_win),
        )
        .route(
            "/api/v1/daily-wins/today",
            get(daily_wins::get_today_daily_win),
        )
        .route(
            "/api/v1/daily-wins/{id}/viewed",
            post(daily_wins::mark_viewed),
        )
        .route(
            "/api/v1/daily-wins/{id}/acted",
            post(daily_wins::mark_acted),
        )
        .route(
            "/api/v1/council",
            post(council::start_session).get(council::list_sessions),
        )
        .route("/api/v1/council/{session_id}", get(council::get_session))
        .route(
            "/api/v1/council/{session_id}/messages",
            get(council::get_session_messages),
        )
        .route(
            "/api/v1/council/{session_id}/start",
            post(council::start_council_session),
        )
        .route(
            "/api/v1/council/{session_id}/stream",
            get(council::stream_council_session),
        )
        .route(
            "/api/v1/council/{session_id}/synthesize",
            post(council::synthesize_council_session),
        )
        .route(
            "/api/v1/council/orchestrations",
            post(council_orchestration::create_orchestration)
                .get(council_orchestration::list_orchestrations),
        )
        .route(
            "/api/v1/council/orchestrations/{id}",
            get(council_orchestration::get_orchestration),
        )
        .route(
            "/api/v1/council/orchestrations/{id}/turns",
            get(council_orchestration::list_orchestration_turns),
        )
        .route(
            "/api/v1/council/orchestrations/{id}/presence",
            get(council_orchestration::list_orchestration_presence),
        )
        .route(
            "/api/v1/council/orchestrations/{id}/debate-events",
            get(council_orchestration::list_orchestration_debate_events),
        )
        .route(
            "/api/v1/muse",
            post(muse::submit_prompt).get(muse::list_conversations),
        )
        .route(
            "/api/v1/muse/{conversation_id}",
            get(muse::get_conversation),
        )
        .route(
            "/api/v1/muse/{conversation_id}/messages",
            get(muse::get_messages),
        )
        .route("/api/v1/office", get(office::get_office_state))
        .route("/api/v1/office/ws", get(office::ws_office))
        .route(
            "/api/v1/avatars",
            get(avatars::list_avatars).post(avatars::create_avatar),
        )
        .route("/api/v1/avatars/defaults", post(avatars::ensure_defaults))
        .route(
            "/api/v1/avatars/{id}",
            get(avatars::get_avatar)
                .patch(avatars::update_avatar)
                .delete(avatars::delete_avatar),
        )
        .route(
            "/api/v1/avatars/{id}/soul",
            get(avatar_soul::get_avatar_soul).put(avatar_soul::update_avatar_soul),
        )
        .route(
            "/api/v1/avatars/{id}/memory/edges",
            get(avatar_soul::list_memory_edges).post(avatar_soul::create_memory_edge),
        )
        .route(
            "/api/v1/avatars/{id}/memory/edges/{edge_id}",
            delete(avatar_soul::delete_memory_edge),
        )
        .route(
            "/api/v1/avatars/{id}/instinct-frame",
            post(avatar_soul::create_instinct_frame),
        )
        .route(
            "/api/v1/harness/runs/{id}/presence",
            get(avatar_soul::list_presence_states).post(avatar_soul::upsert_presence_state),
        )
        .route(
            "/api/v1/harness/runs/{id}/debate-events",
            get(avatar_soul::list_debate_events).post(avatar_soul::create_debate_event),
        )
        .route(
            "/api/v1/avatars/{id}/artifact-trail",
            get(avatar_soul::get_artifact_trail),
        )
        .route(
            "/api/v1/avatars/strategist/default",
            post(strategist_soul::ensure_strategist_default),
        )
        .route(
            "/api/v1/avatars/strategist/dry-run",
            post(strategist_soul::run_strategist_dry_run),
        )
        .route(
            "/api/v1/avatars/researcher/default",
            post(researcher_soul::ensure_researcher_default),
        )
        .route(
            "/api/v1/avatars/researcher/dry-run",
            post(researcher_soul::run_researcher_dry_run),
        )
        .route(
            "/api/v1/avatars/copywriter/default",
            post(copywriter_soul::ensure_copywriter_default),
        )
        .route(
            "/api/v1/avatars/copywriter/dry-run",
            post(copywriter_soul::run_copywriter_dry_run),
        )
        .route(
            "/api/v1/avatars/growth-operator/default",
            post(growth_operator_soul::ensure_growth_operator_default),
        )
        .route(
            "/api/v1/avatars/growth-operator/dry-run",
            post(growth_operator_soul::run_growth_operator_dry_run),
        )
        .route(
            "/api/v1/avatars/analyst/default",
            post(analyst_soul::ensure_analyst_default),
        )
        .route(
            "/api/v1/avatars/analyst/dry-run",
            post(analyst_soul::run_analyst_dry_run),
        )
        .route(
            "/api/v1/avatars/creative-director/default",
            post(creative_director_soul::ensure_creative_director_default),
        )
        .route(
            "/api/v1/avatars/creative-director/dry-run",
            post(creative_director_soul::run_creative_director_dry_run),
        )
        .route(
            "/api/v1/avatars/proof-collector/default",
            post(proof_collector_soul::ensure_proof_collector_default),
        )
        .route(
            "/api/v1/avatars/proof-collector/dry-run",
            post(proof_collector_soul::run_proof_collector_dry_run),
        )
        .route(
            "/api/v1/harness/runs",
            get(harness::list_runs).post(harness::create_run),
        )
        .route("/api/v1/harness/runs/{id}", get(harness::get_run))
        .route(
            "/api/v1/harness/runs/{id}/cancel",
            post(harness::cancel_run),
        )
        .route("/api/v1/harness/runs/{id}/steps", get(harness::list_steps))
        .route("/api/v1/capabilities", get(capabilities::list_capabilities))
        .route(
            "/api/v1/capabilities/defaults",
            post(capabilities::ensure_default_capabilities),
        )
        .route(
            "/api/v1/capabilities/{id}",
            get(capabilities::get_capability),
        )
        .route(
            "/api/v1/capabilities/key/{key}",
            get(capabilities::get_capability_by_key),
        )
        .route(
            "/api/v1/avatars/{id}/capabilities",
            get(capabilities::list_avatar_capabilities),
        )
        .route(
            "/api/v1/avatars/{id}/capabilities",
            post(capabilities::grant_capability_to_avatar),
        )
        .route(
            "/api/v1/avatars/{id}/capabilities/{capability_id}",
            delete(capabilities::revoke_capability_from_avatar),
        )
        .route(
            "/api/v1/harness/context-packs",
            post(capabilities::create_context_pack),
        )
        .route(
            "/api/v1/harness/context-packs/{id}",
            get(capabilities::get_context_pack),
        )
        .route(
            "/api/v1/capability-runs",
            get(capabilities::list_capability_runs).post(capabilities::create_capability_run),
        )
        .route(
            "/api/v1/capability-runs/{id}",
            get(capabilities::get_capability_run),
        )
        .route("/api/v1/artifacts", get(capabilities::list_artifacts))
        .route("/api/v1/artifacts/{id}", get(capabilities::get_artifact))
        .route(
            "/api/v1/artifacts/{id}/versions",
            post(capabilities::create_artifact_version),
        )
        .route("/api/v1/health", get(health::api_health))
        .layer(axum::middleware::from_fn_with_state(state, auth_middleware))
}

pub fn create_router(state: AppState) -> Router {
    let shared_state = Arc::new(state);
    let public = public_router(shared_state.as_ref()); // # FIXED: pass state to public_router for rate limiting
    let protected = protected_router(shared_state.clone());

    let mut app = Router::new()
        .layer(Extension(shared_state.settings.clone()))
        .layer(Extension(shared_state.clone()))
        .merge(public)
        .merge(protected);

    if let Some(pool) = shared_state.db_pool.clone() {
        app = app.layer(Extension(pool));
    }

    if let Some(ref tenant_pool) = shared_state.tenant_pool {
        app = app.layer(Extension(tenant_pool.clone()));
    }

    app.layer(cors_layer(shared_state.as_ref()))
}
