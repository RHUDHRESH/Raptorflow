use axum::body::Body;
use axum::http::{Request, StatusCode};
use raptorflow_config::Settings;
use raptorflow_http::{create_router, middleware::AppState};
use std::collections::BTreeSet;
use std::sync::Arc;
use tower::ServiceExt;

fn app_state_without_dependencies() -> AppState {
    let mut settings = Settings::from_env().expect("settings");
    settings.app_env = "dev".to_string();
    AppState::new(
        None,
        "example.clerk.accounts.dev".to_string(),
        Arc::new(settings),
    )
}

#[tokio::test]
async fn readiness_returns_503_when_dependencies_missing() {
    let app = create_router(app_state_without_dependencies());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/health/ready")
                .method("GET")
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::SERVICE_UNAVAILABLE);
}

#[test]
fn openapi_paths_match_mounted_routes() {
    let router_source = include_str!("../src/router.rs");
    let openapi_source = include_str!("../../../schemas/openapi/api-v1.yaml");

    let mounted_paths: BTreeSet<String> = router_source
        .lines()
        .filter_map(|line| {
            let marker = ".route(\"";
            let start = line.find(marker)?;
            let remaining = &line[start + marker.len()..];
            let end = remaining.find('"')?;
            Some(remaining[..end].to_string())
        })
        .collect();

    let documented_paths: BTreeSet<String> = openapi_source
        .lines()
        .filter_map(|line| {
            let trimmed = line.trim_start();
            if !trimmed.starts_with('/') || !trimmed.ends_with(':') {
                return None;
            }
            Some(trimmed.trim_end_matches(':').to_string())
        })
        .collect();

    assert_eq!(mounted_paths, documented_paths);
}
