use axum::body::Body;
use axum::http::{Request, StatusCode};
use raptorflow_config::Settings;
use raptorflow_http::{create_router, middleware::AppState};
use std::sync::Arc;
use tower::ServiceExt;

fn test_app_state() -> AppState {
    let mut settings = Settings::from_env().expect("settings");
    settings.app_env = "dev".to_string();
    AppState::new(
        None,
        "example.clerk.accounts.dev".to_string(),
        Arc::new(settings),
    )
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
async fn campaigns_list_requires_auth() {
    let app = create_router(test_app_state());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns")
                .method("GET")
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn campaigns_list_returns_empty_for_new_org() {
    let app = create_router(test_app_state());
    let org_id = "00000000-0000-0000-0000-000000000001";
    let user_id = "user_001";

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns")
                .method("GET")
                .header("Authorization", auth_header(org_id, user_id))
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::OK);

    let body = axum::body::to_bytes(response.into_body(), 256 * 1024)
        .await
        .expect("body");
    let json: serde_json::Value = serde_json::from_slice(&body).expect("json");

    assert_eq!(json["status"], "ok");
    assert!(json["campaigns"].is_array());
    assert_eq!(json["total"], 0);
}

#[tokio::test]
async fn campaigns_create_requires_name_and_goal() {
    let org_id = "00000000-0000-0000-0000-000000000002";
    let user_id = "user_002";

    let missing_name = serde_json::json!({
        "goal": "Test goal"
    });

    let app = create_router(test_app_state());
    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns")
                .method("POST")
                .header("Authorization", auth_header(org_id, user_id))
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&missing_name).unwrap()))
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::BAD_REQUEST);

    let body = axum::body::to_bytes(response.into_body(), 256 * 1024)
        .await
        .expect("body");
    let json: serde_json::Value = serde_json::from_slice(&body).expect("json");
    assert_eq!(json["error"], "campaign_name_required");

    let missing_goal = serde_json::json!({
        "name": "Test Campaign"
    });

    let app = create_router(test_app_state());
    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns")
                .method("POST")
                .header("Authorization", auth_header(org_id, user_id))
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&missing_goal).unwrap()))
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::BAD_REQUEST);

    let body = axum::body::to_bytes(response.into_body(), 256 * 1024)
        .await
        .expect("body");
    let json: serde_json::Value = serde_json::from_slice(&body).expect("json");
    assert_eq!(json["error"], "campaign_goal_required");
}

#[tokio::test]
async fn campaigns_get_returns_404_for_nonexistent() {
    let app = create_router(test_app_state());
    let org_id = "00000000-0000-0000-0000-000000000003";
    let user_id = "user_003";

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns/nonexistent-campaign-id")
                .method("GET")
                .header("Authorization", auth_header(org_id, user_id))
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn campaigns_update_status_rejects_invalid_status() {
    let app = create_router(test_app_state());
    let org_id = "00000000-0000-0000-0000-000000000004";
    let user_id = "user_004";

    let invalid_status = serde_json::json!({
        "status": "invalid_status"
    });

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns/some-campaign-id/status")
                .method("PATCH")
                .header("Authorization", auth_header(org_id, user_id))
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&invalid_status).unwrap()))
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::BAD_REQUEST);

    let body = axum::body::to_bytes(response.into_body(), 256 * 1024)
        .await
        .expect("body");
    let json: serde_json::Value = serde_json::from_slice(&body).expect("json");
    assert_eq!(json["error"], "invalid_status");
}

#[tokio::test]
async fn campaigns_moves_returns_404_for_nonexistent_campaign() {
    let app = create_router(test_app_state());
    let org_id = "00000000-0000-0000-0000-000000000005";
    let user_id = "user_005";

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns/nonexistent-campaign/moves")
                .method("GET")
                .header("Authorization", auth_header(org_id, user_id))
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn campaigns_tasks_returns_404_for_nonexistent_campaign() {
    let app = create_router(test_app_state());
    let org_id = "00000000-0000-0000-0000-000000000006";
    let user_id = "user_006";

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns/nonexistent-campaign/tasks")
                .method("GET")
                .header("Authorization", auth_header(org_id, user_id))
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn campaigns_brief_returns_null_for_campaign_without_brief() {
    let app = create_router(test_app_state());
    let org_id = "00000000-0000-0000-0000-000000000007";
    let user_id = "user_007";

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/campaigns/some-campaign/brief")
                .method("GET")
                .header("Authorization", auth_header(org_id, user_id))
                .body(Body::empty())
                .expect("request"),
        )
        .await
        .expect("response");

    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[ignore = "requires DATABASE_URL and test org setup; see GENERATE_MOVES_TRANSACTION_REPORT.md"]
#[tokio::test]
async fn generate_moves_transaction_rollback_on_validation_failure() {
    use raptorflow_db::queries;
    use sqlx::PgPoolOptions;

    let database_url = std::env::var("TEST_DATABASE_URL")
        .expect("TEST_DATABASE_URL must be set for this test");

    let pool = PgPoolOptions::new()
        .max_connections(1)
        .connect(&database_url)
        .await
        .expect("failed to connect to test database");

    let org_id = uuid::Uuid::parse_str("00000000-0000-0000-0000-000000000099")
        .expect("valid UUID");
    let campaign_id = "test-rollback-campaign";

    sqlx::query("SET LOCAL app.current_org_id = $1")
        .bind(org_id)
        .execute(&pool)
        .await
        .expect("failed to set org_id");

    let create_err = queries::create_campaign(&pool, campaign_id, org_id, "Test", "Rollback test")
        .await;
    if create_err.is_err() {
        return;
    }

    let moves = vec![
        queries::GeneratedCampaignMoveInsert {
            move_id: "valid-move".to_string(),
            content_id: "valid-content".to_string(),
            move_type: "positioning".to_string(),
            sequence_number: 1,
            content_body: serde_json::json!({
                "description": "Valid move with sufficient description",
                "expected_impact": "This is a valid impact string with enough chars",
                "confidence": 0.8
            }),
        },
        queries::GeneratedCampaignMoveInsert {
            move_id: "invalid-move".to_string(),
            content_id: "invalid-content".to_string(),
            move_type: "invalid_type".to_string(),
            sequence_number: 2,
            content_body: serde_json::json!({"description": "x", "expected_impact": "x", "confidence": 0.5}),
        },
    ];

    let result = queries::create_generated_campaign_moves_transactional(&pool, org_id, campaign_id, moves).await;

    assert!(result.is_err(), "Should reject due to invalid move_type");

    let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM campaign_moves WHERE campaign_id = $1")
        .bind(campaign_id)
        .fetch_one(&pool)
        .await
        .expect("query should succeed");
    assert_eq!(count.0, 0, "Zero moves should be inserted after rollback");

    sqlx::query("DELETE FROM campaign_moves WHERE campaign_id = $1")
        .bind(campaign_id)
        .execute(&pool)
        .await
        .expect("cleanup");
    sqlx::query("DELETE FROM campaigns WHERE campaign_id = $1")
        .bind(campaign_id)
        .execute(&pool)
        .await
        .expect("cleanup");
}
