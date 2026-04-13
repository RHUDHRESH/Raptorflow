use axum::{
    extract::{Extension, Path, Query},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use raptorflow_aws::{ExportManager, S3Service, ScreenshotManager, UploadManager};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::middleware::{AppState, auth::AuthContext};

#[derive(Debug, Serialize)]
pub struct UploadUrlResponse {
    pub upload_url: String,
    pub key: String,
    pub expires_in: u32,
}

#[derive(Debug, Serialize)]
pub struct DownloadUrlResponse {
    pub download_url: String,
    pub expires_in: u32,
}

#[derive(Debug, Serialize)]
pub struct DeleteResponse {
    deleted: bool,
}

#[derive(Debug, Serialize)]
pub struct ExportUrlResponse {
    pub upload_url: String,
    pub expires_in: u32,
}

#[derive(Debug, Serialize)]
pub struct UploadError {
    pub error: String,
}

impl IntoResponse for UploadError {
    fn into_response(self) -> axum::response::Response {
        (StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({ "error": self.error }))).into_response()
    }
}

impl From<raptorflow_aws::S3Error> for UploadError {
    fn from(e: raptorflow_aws::S3Error) -> Self {
        Self { error: e.to_string() }
    }
}

#[derive(Debug, Deserialize)]
pub struct GenerateUploadUrlRequest {
    pub filename: String,
    pub content_type: String,
}

pub async fn generate_upload_url(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(req): Json<GenerateUploadUrlRequest>,
) -> Result<Json<UploadUrlResponse>, UploadError> {
    let s3 = S3Service::from_settings(&state.settings).await;
    let upload_manager = UploadManager::new(s3);

    let url = upload_manager
        .generate_upload_url(&state.settings.s3_bucket, &req.filename, &req.content_type)
        .await
        .map_err(UploadError::from)?;

    Ok(Json(UploadUrlResponse {
        upload_url: url.upload_url,
        key: url.key,
        expires_in: url.expires_in,
    }))
}

#[derive(Debug, Deserialize)]
pub struct DownloadQuery {
    pub key: String,
}

pub async fn generate_download_url(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Query(params): Query<DownloadQuery>,
) -> Result<Json<DownloadUrlResponse>, UploadError> {
    let s3 = S3Service::from_settings(&state.settings).await;
    let upload_manager = UploadManager::new(s3);

    let url = upload_manager.generate_download_url(&params.key).await.map_err(UploadError::from)?;

    Ok(Json(DownloadUrlResponse {
        download_url: url,
        expires_in: 3600,
    }))
}

pub async fn delete_upload(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(key): Path<String>,
) -> Result<Json<DeleteResponse>, UploadError> {
    let s3 = S3Service::from_settings(&state.settings).await;
    let upload_manager = UploadManager::new(s3);

    upload_manager.delete_upload(&key).await.map_err(UploadError::from)?;

    Ok(Json(DeleteResponse { deleted: true }))
}

#[derive(Debug, Deserialize)]
pub struct GenerateScreenshotUploadUrlRequest {
    pub campaign_id: String,
    pub filename: String,
}

pub async fn generate_screenshot_upload_url(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(req): Json<GenerateScreenshotUploadUrlRequest>,
) -> Result<Json<UploadUrlResponse>, UploadError> {
    let s3 = S3Service::from_settings(&state.settings).await;
    let screenshot_manager = ScreenshotManager::new(s3);

    let url = screenshot_manager
        .generate_upload_url(&state.settings.s3_bucket, &req.campaign_id, &req.filename)
        .await
        .map_err(UploadError::from)?;

    Ok(Json(UploadUrlResponse {
        upload_url: url.upload_url,
        key: url.key,
        expires_in: url.expires_in,
    }))
}

#[derive(Debug, Deserialize)]
pub struct GenerateExportUrlRequest {
    pub export_type: String,
    pub filename: String,
}

pub async fn generate_export_url(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(req): Json<GenerateExportUrlRequest>,
) -> Result<Json<ExportUrlResponse>, UploadError> {
    let s3 = S3Service::from_settings(&state.settings).await;
    let export_manager = ExportManager::new(s3);

    let url = export_manager
        .generate_export_url(&state.settings.s3_bucket, &req.export_type, &req.filename)
        .await
        .map_err(UploadError::from)?;

    Ok(Json(ExportUrlResponse {
        upload_url: url,
        expires_in: 86400,
    }))
}

#[derive(Debug, Deserialize)]
pub struct ExportDownloadQuery {
    pub key: String,
}

pub async fn generate_export_download_url(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Query(params): Query<ExportDownloadQuery>,
) -> Result<Json<DownloadUrlResponse>, UploadError> {
    let s3 = S3Service::from_settings(&state.settings).await;
    let export_manager = ExportManager::new(s3);

    let url = export_manager.generate_download_url(&params.key).await.map_err(UploadError::from)?;

    Ok(Json(DownloadUrlResponse {
        download_url: url,
        expires_in: 86400,
    }))
}