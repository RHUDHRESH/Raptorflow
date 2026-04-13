//! Background job registry and stubs for RaptorFlow.
//!
//! ## Current status
//!
//! All 16 job types are registered in [`registry()`] but handlers return `accepted`
//! without any real processing. Workers are not yet implemented.
//!
//! ## Job roster
//!
//! | Key | Description | Status |
//! |---|---|---|
//! | `swr-consolidation` | Sharp wave ripple consolidation | Stub |
//! | `daily-wins` | Daily briefing generation | Stub |
//! | `intel-scan` | Competitive intelligence scan | Stub |
//! | `campaign-replanning` | Autonomous replanning | Stub |
//! | `embedding-worker` | Ripple embedding generation | Stub |
//! | `prediction-resolution` | Memory prediction updates | Stub |
//! | `foundation-quick-scan` | Quick foundation ingestion | Stub |
//! | `foundation-deep-scan` | Deep crawl + enrichment | Stub |
//! | `foundation-cache-invalidation` | Cache refresh | Stub |
//! | `content-feedback-loop` | Performance routing | Stub |
//! | `monthly-cost-thresholds` | Cost alert evaluation | Stub |
//! | `avatar-registry-sync` | Office roster sync | Stub |
//! | `research-request` | Research triage | Stub |
//! | `tool-gateway` | Tool execution | Stub |
//! | `intern-dispatch` | Intern task envelope | Stub |
//! | `stream-coordinator` | Precheck/routing | Stub |
//! | `event-harvester` | Ripple ingestion | Stub |
//!
//! ## When implementing
//!
//! Jobs should be triggered by SQS messages via `raptorflow_sqs`. Each job type
//! needs a dedicated worker function. See `crates/sqs/` for the queue client.

use axum::{
    Json, Router,
    routing::{get, post},
};
use raptorflow_contracts::{
    EventHarvesterRecord, InternTask, OrgMonthlyCost, ResearchRequest, StreamCoordinatorRequest,
    ToolGatewayRequest,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JobRegistration {
    pub key: &'static str,
    pub description: &'static str,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HarnessSurface {
    pub key: &'static str,
    pub description: &'static str,
}

pub fn registry() -> Vec<JobRegistration> {
    vec![
        JobRegistration {
            key: "swr-consolidation",
            description: "Sharp wave ripple consolidation",
        },
        JobRegistration {
            key: "daily-wins",
            description: "Daily Wins briefing generation",
        },
        JobRegistration {
            key: "intel-scan",
            description: "Competitive intelligence scraping and diffing",
        },
        JobRegistration {
            key: "campaign-replanning",
            description: "Autonomous campaign replanning evaluator",
        },
        JobRegistration {
            key: "embedding-worker",
            description: "Ripple embedding generation worker",
        },
        JobRegistration {
            key: "prediction-resolution",
            description: "Prediction resolution and memory updates",
        },
        JobRegistration {
            key: "foundation-quick-scan",
            description: "Foundation quick-scan ingestion and extraction",
        },
        JobRegistration {
            key: "foundation-deep-scan",
            description: "Foundation deep-scan crawl and enrichment",
        },
        JobRegistration {
            key: "foundation-cache-invalidation",
            description: "Foundation cache invalidation and prompt-cache refresh",
        },
        JobRegistration {
            key: "content-feedback-loop",
            description: "Content performance to EEL and campaign feedback routing",
        },
        JobRegistration {
            key: "monthly-cost-thresholds",
            description: "Org monthly cost threshold checks and alerts",
        },
        JobRegistration {
            key: "avatar-registry-sync",
            description: "Avatar registry projection and office roster synchronization",
        },
        JobRegistration {
            key: "research-request",
            description: "Research request intake and triage",
        },
        JobRegistration {
            key: "tool-gateway",
            description: "Tool gateway execution surface",
        },
        JobRegistration {
            key: "intern-dispatch",
            description: "Intern dispatch orchestration",
        },
        JobRegistration {
            key: "stream-coordinator",
            description: "Stream coordinator precheck and routing",
        },
        JobRegistration {
            key: "event-harvester",
            description: "Event harvesting and ripple ingestion",
        },
    ]
}

pub fn harness_surfaces() -> Vec<HarnessSurface> {
    vec![
        HarnessSurface {
            key: "research-request",
            description: "Accepts structured research_request payloads and returns a dispatch stub.",
        },
        HarnessSurface {
            key: "tool-gateway",
            description: "Receives tool invocations for web search, browser, and other tool classes.",
        },
        HarnessSurface {
            key: "intern-dispatch",
            description: "Receives blocking and background intern task envelopes.",
        },
        HarnessSurface {
            key: "stream-coordinator",
            description: "Accepts stream coordination plans and blocking-research prechecks.",
        },
        HarnessSurface {
            key: "event-harvester",
            description: "Records external or internal events for ripple ingestion.",
        },
    ]
}

pub fn router() -> Router {
    Router::new()
        .route("/", post(trigger_job))
        .route("/surfaces", get(list_surfaces))
        .route("/research", post(accept_research_request))
        .route("/tool-gateway", post(accept_tool_gateway_request))
        .route("/intern-dispatch", post(dispatch_intern_task))
        .route("/stream-coordinator", post(run_stream_coordinator))
        .route("/event-harvester", post(harvest_event))
}

async fn trigger_job() -> Json<Value> {
    let _cost_shape = OrgMonthlyCost {
        org_id: Uuid::nil(),
        month: "2026-04-01".to_string(),
        inference_cost_usd: 0.0,
        scraping_cost_usd: 0.0,
        storage_cost_usd: 0.0,
        session_count: 0,
    };

    Json(json!({
        "status": "accepted",
        "jobs": registry(),
        "surfaces": harness_surfaces(),
    }))
}

async fn list_surfaces() -> Json<Value> {
    Json(json!({
        "status": "stub",
        "surfaces": harness_surfaces(),
    }))
}

async fn accept_research_request(Json(request): Json<ResearchRequest>) -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "surface": "research-request",
        "request_id": request.request_id,
        "task_type": request.request_kind,
    }))
}

async fn accept_tool_gateway_request(Json(request): Json<ToolGatewayRequest>) -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "surface": "tool-gateway",
        "request_id": request.request_id,
        "tool_name": request.tool_name,
    }))
}

async fn dispatch_intern_task(Json(request): Json<InternTask>) -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "surface": "intern-dispatch",
        "task_id": request.task_id,
        "intern_avatar_key": request.intern_avatar_key,
        "task_type": request.task_type,
    }))
}

async fn run_stream_coordinator(Json(request): Json<StreamCoordinatorRequest>) -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "surface": "stream-coordinator",
        "session_id": request.session_id,
        "phase": request.phase,
        "blocking_research_count": request.blocking_research.len(),
        "tool_request_count": request.tool_requests.len(),
    }))
}

async fn harvest_event(Json(request): Json<EventHarvesterRecord>) -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "surface": "event-harvester",
        "event_id": request.event_id,
        "source_type": request.source_type,
        "source_id": request.source_id,
    }))
}
