use axum::{
    body::Body,
    extract::Extension,
    http::{Request, StatusCode},
    routing::post,
    Json, Router,
};
use raptorflow_auth::{ClerkClient, ClerkWebhookEvent};
use raptorflow_auth::clerk::{ClerkUserData, ClerkMembershipData, ClerkOrgData};
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
    let signature = request
        .headers()
        .get("clerk-webhook-signature")
        .and_then(|v| v.to_str().ok())
        .unwrap_or_default()
        .to_string();

    let body = axum::body::to_bytes(request.into_body(), 10 * 1024 * 1024)
        .await
        .map_err(|_| StatusCode::BAD_REQUEST)?;

    let clerk_webhook_secret = state
        .settings
        .clerk_webhook_secret
        .clone()
        .ok_or_else(|| {
            tracing::error!("Missing Clerk webhook secret in settings");
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    let clerk_client = ClerkClient::new(clerk_webhook_secret);

    if let Err(e) = clerk_client.verify_webhook_signature(&body, &signature) {
        tracing::warn!(error = %e, "Clerk webhook signature verification failed");
        return Err(StatusCode::UNAUTHORIZED);
    }

    let event: ClerkWebhookEvent = clerk_client
        .parse_webhook_event(&body)
        .map_err(|e| {
            tracing::warn!(error = %e, "Failed to parse webhook event");
            StatusCode::BAD_REQUEST
        })?;

    // # FIXED: Clerk webhook replay protection - check event_id before processing
    if let Some(ref cache_service) = state.cache_service {
        let cache_key = format!("clerk:events:{}", event.id);
        match cache_service.exists(&cache_key).await {
            Ok(true) => {
                tracing::info!(event_id = %event.id, "Clerk webhook event already processed (replay), skipping");
                return Ok(Json(WebhookResponse {
                    received: true,
                    processed: true,
                    message: "Event already processed".to_string(),
                }));
            }
            Ok(false) => {
                // Event not seen before, mark it as processed with 24h TTL
                if let Err(e) = cache_service.set_with_ttl(&cache_key, &true, 86400).await {
                    tracing::error!(error = %e, "Failed to set replay protection cache key");
                    // Don't fail the request, just log the error
                }
            }
            Err(e) => {
                tracing::error!(error = %e, "Failed to check replay protection cache");
                // Don't fail the request, continue without replay protection
            }
        }
    }

    tracing::info!(event_type = %event.event_type, "Processing Clerk webhook");

    if let Some(ref pool) = state.db_pool {
        match event.event_type.as_str() {
            "user.created" | "user.updated" => {
                if let Err(e) = upsert_user(pool, &event).await {
                    tracing::error!(error = %e, "Failed to upsert user");
                    return Ok(Json(WebhookResponse {
                        received: true,
                        processed: false,
                        message: format!("Failed to process user: {}", e),
                    }));
                }
            }
            "organization_membership.created" | "organization_membership.updated" => {
                if let Err(e) = upsert_membership(pool, &event).await {
                    tracing::error!(error = %e, "Failed to upsert membership");
                    return Ok(Json(WebhookResponse {
                        received: true,
                        processed: false,
                        message: format!("Failed to process membership: {}", e),
                    }));
                }
            }
            "organization.created" => {
                if let Err(e) = handle_org_created(pool, &event).await {
                    tracing::error!(error = %e, "Failed to create organization");
                    return Ok(Json(WebhookResponse {
                        received: true,
                        processed: false,
                        message: format!("Failed to process org: {}", e),
                    }));
                }
            }
            _ => {
                tracing::debug!(event_type = %event.event_type, "Unhandled webhook event type");
            }
        }
    }

    Ok(Json(WebhookResponse {
        received: true,
        processed: true,
        message: "Event processed successfully".to_string(),
    }))
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

    // # FIXED: implement user upsert using raw sqlx query
    // Upsert into users table: INSERT ... ON CONFLICT DO UPDATE
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

    let org_id = data
        .organization
        .as_ref()
        .ok_or("No organization in membership")?
        .id
        .as_str();

    let org_id = Uuid::parse_str(org_id).map_err(|e| format!("Invalid org_id: {}", e))?;

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

    let org_id = Uuid::parse_str(&data.id).map_err(|e| format!("Invalid org_id: {}", e))?;
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
    if lower.contains("admin") || lower.contains("owner") || lower.contains("billing_admin") {
        "admin"
    } else if lower.contains("member") {
        "member"
    } else if lower.contains("guest") || lower.contains("restricted") {
        "guest"
    } else {
        "member"
    }
}
