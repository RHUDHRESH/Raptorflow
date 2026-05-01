use axum::body::Body;
use axum::http::{Request, StatusCode};
use raptorflow_config::Settings;
use raptorflow_http::{create_router, middleware::AppState};
use std::sync::Arc;
use tower::ServiceExt;

fn test_app_state() -> AppState {
    let mut settings = Settings::from_env().expect("settings");
    settings.app_env = "dev".to_string();
    AppState::new(None, None, None, Arc::new(settings))
}

fn auth_header(org_id: &str, user_id: &str) -> String {
    let claims = serde_json::json!({
        "org_id": org_id,
        "user_id": user_id,
        "role": "admin",
        "iss": "https://example.clerk.accounts.dev",
        "sub": user_id
    });
    let header = format!(
        "Bearer {}",
        jsonwebtoken::encode(
            &jsonwebtoken::Header::default(),
            &claims,
            &jsonwebtoken::EncodingKey::from_secret(b"test-secret"),
        )
        .unwrap()
    );
    header
}

#[tokio::test]
async fn council_list_requires_auth() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/council")
                .method("GET")
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn council_start_requires_auth() {
    let app = create_router(test_app_state());

    let body = serde_json::json!({
        "question": "What should our Q2 campaign focus on?",
        "agent_roster": ["strategist", "market_research_lead"]
    });

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/council")
                .method("POST")
                .header(
                    "Authorization",
                    auth_header("00000000-0000-0000-0000-000000000001", "user_001"),
                )
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&body).unwrap()))
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::SERVICE_UNAVAILABLE);
}

#[tokio::test]
async fn council_start_rejects_empty_question() {
    let app = create_router(test_app_state());

    let body = serde_json::json!({
        "question": ""
    });

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/council")
                .method("POST")
                .header(
                    "Authorization",
                    auth_header("00000000-0000-0000-0000-000000000002", "user_002"),
                )
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&body).unwrap()))
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::BAD_REQUEST);

    let body_bytes = axum::body::to_bytes(response.into_body(), 256 * 1024)
        .await
        .expect("body");
    let json: serde_json::Value = serde_json::from_slice(&body_bytes).expect("json");
    assert_eq!(json["error"], "question_required");
}

#[tokio::test]
async fn council_get_returns_404_for_nonexistent() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/council/nonexistent-session")
                .method("GET")
                .header(
                    "Authorization",
                    auth_header("00000000-0000-0000-0000-000000000003", "user_003"),
                )
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn council_messages_returns_404_for_nonexistent() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/council/nonexistent-session/messages")
                .method("GET")
                .header(
                    "Authorization",
                    auth_header("00000000-0000-0000-0000-000000000004", "user_004"),
                )
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}
