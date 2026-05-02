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
    format!(
        "Bearer {}",
        jsonwebtoken::encode(
            &jsonwebtoken::Header::default(),
            &claims,
            &jsonwebtoken::EncodingKey::from_secret(b"test-secret"),
        )
        .unwrap()
    )
}

#[tokio::test]
async fn nudges_list_requires_auth() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/nudges")
                .method("GET")
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn nudges_create_requires_auth() {
    let app = create_router(test_app_state());

    let body = serde_json::json!({
        "user_id": "00000000-0000-0000-0000-000000000001",
        "nudge_type": "campaign_deadline",
        "priority": "high",
        "title": "Campaign deadline approaching",
        "body": "Your Q2 campaign ends in 3 days",
        "source_type": "campaign",
        "source_id": "campaign_123"
    });

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/nudges")
                .method("POST")
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&body).unwrap()))
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::SERVICE_UNAVAILABLE);
}

#[tokio::test]
async fn nudges_create_rejects_empty_title() {
    let app = create_router(test_app_state());

    let body = serde_json::json!({
        "user_id": "00000000-0000-0000-0000-000000000001",
        "nudge_type": "campaign_deadline",
        "priority": "high",
        "title": "",
        "body": "Some body",
        "source_type": "campaign",
        "source_id": "campaign_123"
    });

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/nudges")
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

    assert_eq!(response.status(), StatusCode::BAD_REQUEST);

    let body_bytes = axum::body::to_bytes(response.into_body(), 256 * 1024)
        .await
        .expect("body");
    let json: serde_json::Value = serde_json::from_slice(&body_bytes).expect("json");
    assert_eq!(json["error"], "title_required");
}

#[tokio::test]
async fn nudges_get_returns_404_for_nonexistent() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/nudges/nonexistent-nudge")
                .method("GET")
                .header(
                    "Authorization",
                    auth_header("00000000-0000-0000-0000-000000000002", "user_002"),
                )
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn daily_wins_list_requires_auth() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/daily-wins")
                .method("GET")
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn daily_wins_today_requires_auth() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/daily-wins/today")
                .method("GET")
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn daily_wins_create_requires_auth() {
    let app = create_router(test_app_state());

    let body = serde_json::json!({
        "briefing_date": "2026-04-16",
        "lead_summary": "Campaign progressing well",
        "full_briefing": "Details here",
        "recommended_action": "Review task list",
        "recommended_action_type": "review"
    });

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/daily-wins")
                .method("POST")
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&body).unwrap()))
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::SERVICE_UNAVAILABLE);
}
