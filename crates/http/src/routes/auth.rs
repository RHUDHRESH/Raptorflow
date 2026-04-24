use axum::{
    Json, Router,
    body::Body,
    extract::Extension,
    http::{Request, StatusCode},
    routing::post,
};
use raptorflow_auth::clerk::{ClerkMembershipData, ClerkOrgData, ClerkUserData};
use raptorflow_auth::{derive_internal_org_id, ClerkClient, ClerkWebhookEvent};
use raptorflow_db::queries;
use serde::Serialize;
use std::sync::Arc;
use uuid::Uuid;

use crate::middleware::AppState;

#[derive(Debug, Serialize)]
pub struct WebhookResponse {
    pub received: bool,
    pub processed: bool,
    pub message: String,
}

pub fn router() -> Router {
    Router::new().route("/webhooks/clerk", post(clerk_webhook))
}

pub async fn clerk_webhook(
    Extension(state): Extension<Arc<AppState>>,
    request: Request<Body>,
) -> Result<Json<WebhookResponse>, StatusCode> {
    let message_id = request
        .headers()
        .get("svix-id")
        .and_then(|v| v.to_str().ok())
        .unwrap_or_default()
        .to_string();
    let timestamp = request
        .headers()
        .get("svix-timestamp")
        .and_then(|v| v.to_str().ok())
        .unwrap_or_default()
        .to_string();
    let signature = request
        .headers()
        .get("svix-signature")
        .and_then(|v| v.to_str().ok())
        .unwrap_or_default()
        .to_string();

    let body = axum::body::to_bytes(request.into_body(), 10 * 1024 * 1024)
        .await
        .map_err(|_| StatusCode::BAD_REQUEST)?;

    let clerk_webhook_secret = state.settings.clerk_webhook_secret.clone().ok_or_else(|| {
        tracing::error!("Missing Clerk webhook secret in settings");
        StatusCode::INTERNAL_SERVER_ERROR
    })?;

    let clerk_client = ClerkClient::new(clerk_webhook_secret);

    if let Err(e) = clerk_client.verify_webhook_signature(
        &body,
        &message_id,
        &timestamp,
        &signature,
        state.settings.webhook_timestamp_tolerance_seconds,
    ) {
        tracing::warn!(error = %e, "Clerk webhook signature verification failed");
        return Err(StatusCode::UNAUTHORIZED);
    }

    let event: ClerkWebhookEvent = clerk_client.parse_webhook_event(&body).map_err(|e| {
        tracing::warn!(error = %e, "Failed to parse webhook event");
        StatusCode::BAD_REQUEST
    })?;

    if message_id.trim().is_empty() {
        tracing::warn!("Clerk webhook missing svix-id header");
        return Err(StatusCode::BAD_REQUEST);
    }

    tracing::info!(
        event_id = %message_id,
        event_type = %event.event_type,
        "Processing Clerk webhook"
    );

    if let Some(ref pool) = state.db_pool {
        match begin_clerk_event(pool, &message_id, &event).await {
            Ok(true) => {}
            Ok(false) => {
                tracing::info!(
                    event_id = %message_id,
                    event_type = %event.event_type,
                    "Skipping duplicate Clerk webhook"
                );
                return Ok(Json(WebhookResponse {
                    received: true,
                    processed: false,
                    message: "Duplicate event skipped".to_string(),
                }));
            }
            Err(e) => {
                tracing::error!(error = %e, "Failed to record Clerk webhook event");
                return Err(StatusCode::INTERNAL_SERVER_ERROR);
            }
        }

        let processing_result: Result<(), String> = async {
        match event.event_type.as_str() {
            "user.created" | "user.updated" => {
                upsert_user(pool, &event).await?;
            }
            "organization_membership.created" | "organization_membership.updated" => {
                upsert_membership(pool, &event).await?;
            }
            "organization.created" => {
                handle_org_created(pool, &event).await?;
            }
            _ => {
                tracing::debug!(event_type = %event.event_type, "Unhandled webhook event type");
            }
        }

            Ok(())
        }
        .await;

        match processing_result {
            Ok(()) => {
                if let Err(e) = mark_clerk_event_processed(pool, &message_id).await {
                    tracing::error!(error = %e, "Failed to mark Clerk webhook processed");
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            }
            Err(e) => {
                let _ = mark_clerk_event_failed(pool, &message_id, &e).await;
                tracing::error!(error = %e, "Failed to process Clerk webhook");
                return Ok(Json(WebhookResponse {
                    received: true,
                    processed: false,
                    message: format!("Failed to process event: {}", e),
                }));
            }
        }
    }

    Ok(Json(WebhookResponse {
        received: true,
        processed: true,
        message: "Event processed successfully".to_string(),
    }))
}

async fn begin_clerk_event(
    pool: &sqlx::PgPool,
    event_id: &str,
    event: &ClerkWebhookEvent,
) -> Result<bool, sqlx::Error> {
    let result = sqlx::query(
        r#"
        INSERT INTO clerk_processed_events (event_id, event_type, payload)
        VALUES ($1, $2, $3)
        ON CONFLICT (event_id) DO NOTHING
        "#,
    )
    .bind(event_id)
    .bind(&event.event_type)
    .bind(&event.data)
    .execute(pool)
    .await?;

    Ok(result.rows_affected() == 1)
}

async fn mark_clerk_event_processed(
    pool: &sqlx::PgPool,
    event_id: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE clerk_processed_events
        SET processed = true, processed_at = NOW(), error = NULL
        WHERE event_id = $1
        "#,
    )
    .bind(event_id)
    .execute(pool)
    .await?;
    Ok(())
}

async fn mark_clerk_event_failed(
    pool: &sqlx::PgPool,
    event_id: &str,
    error: &str,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE clerk_processed_events
        SET processed = false, error = $2
        WHERE event_id = $1
        "#,
    )
    .bind(event_id)
    .bind(error)
    .execute(pool)
    .await?;
    Ok(())
}

async fn upsert_user(pool: &sqlx::PgPool, event: &ClerkWebhookEvent) -> Result<(), String> {
    let data: ClerkUserData = serde_json::from_value(event.data.clone())
        .map_err(|e| format!("Failed to parse user data: {}", e))?;

    let user_id = &data.id;
    let email = data
        .email_addresses
        .first()
        .map(|e| e.email_address.as_str())
        .unwrap_or("unknown@example.com");

    let first_name = data.first_name.as_deref().unwrap_or("Unknown");
    let last_name = data.last_name.as_deref();
    tracing::info!(
        user_id = %user_id,
        email = %email,
        first_name = %first_name,
        "Upserting user from webhook"
    );

    sqlx::query(
        r#"
        INSERT INTO users (clerk_user_id, email, first_name, last_name, updated_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (clerk_user_id) DO UPDATE SET
            email = EXCLUDED.email,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            updated_at = EXCLUDED.updated_at
        "#,
    )
    .bind(user_id)
    .bind(email)
    .bind(first_name)
    .bind(last_name)
    .execute(pool)
    .await
    .map_err(|e| format!("Failed to upsert user: {}", e))?;

    Ok(())
}

async fn upsert_membership(pool: &sqlx::PgPool, event: &ClerkWebhookEvent) -> Result<(), String> {
    let data: ClerkMembershipData = serde_json::from_value(event.data.clone())
        .map_err(|e| format!("Failed to parse membership data: {}", e))?;

    let clerk_org_id = data
        .organization
        .as_ref()
        .ok_or("No organization in membership")?
        .id
        .as_str();

    let org_id = derive_internal_org_id(clerk_org_id);

    let user_id = data
        .public_user_data
        .as_ref()
        .ok_or("No user data in membership")?
        .user_id
        .as_str();

    let email = data
        .public_user_data
        .as_ref()
        .and_then(|d| d.email_addresses.first())
        .map(|e| e.email_address.as_str())
        .unwrap_or("unknown@example.com");

    let role = normalize_clerk_role(&data.role);

    tracing::info!(
        org_id = %org_id,
        user_id = %user_id,
        email = %email,
        role = %role,
        "Upserting org membership"
    );

    queries::create_org_user(pool, Uuid::new_v4(), org_id, user_id, email, role)
        .await
        .map_err(|e| format!("Database error: {}", e))?;

    Ok(())
}

async fn handle_org_created(pool: &sqlx::PgPool, event: &ClerkWebhookEvent) -> Result<(), String> {
    let data: ClerkOrgData = serde_json::from_value(event.data.clone())
        .map_err(|e| format!("Failed to parse org data: {}", e))?;

    let org_id = derive_internal_org_id(&data.id);
    let name = data.name.as_str();

    tracing::info!(
        org_id = %org_id,
        name = %name,
        "Creating organization from webhook"
    );

    queries::create_organization(pool, org_id, name)
        .await
        .map_err(|e| format!("Database error: {}", e))?;

    Ok(())
}

fn normalize_clerk_role(clerk_role: &str) -> &'static str {
    let lower = clerk_role.to_lowercase();
    if lower.contains("admin") || lower.contains("owner") {
        "admin"
    } else if lower.contains("member") {
        "member"
    } else if lower.contains("guest") || lower.contains("restricted") {
        "viewer"
    } else {
        "member"
    }
}
