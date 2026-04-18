//! AWS service integrations for RaptorFlow.
//!
//! Provides S3 presigned-URL generation for file uploads, downloads,
//! screenshots, and exports. All operations go through presigned URLs so
//! the API never handles raw file bytes — clients talk directly to S3.
//!
//! ## Managers
//!
//! - [`S3Service`] — low-level S3 client with presigned GET/PUT, head, delete
//! - [`UploadManager`] — org-scoped upload URL generation (`uploads/{org_id}/{filename}`)
//! - [`ScreenshotManager`] — screenshot upload URL generation (`screenshots/{org_id}/{campaign_id}/{filename}`)
//! - [`ExportManager`] — export file URL generation (`exports/{org_id}/{type}/{filename}`)
//!
//! ## S3 key layout
//!
//! | Prefix | Path pattern |
//! |---|---|
//! | uploads | `uploads/{org_id}/{filename}` |
//! | screenshots | `screenshots/{org_id}/{campaign_id}/{filename}` |
//! | exports | `exports/{org_id}/{export_type}/{filename}` |
//!
//! ## Errors
//!
//! All errors are typed ([`S3Error`]) with variants for config, presigning, and API failures.

use aws_config::BehaviorVersion;
use aws_sdk_s3::config::Credentials;
use aws_sdk_s3::presigning::PresigningConfig;
use aws_sdk_s3::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Clone)]
pub struct S3Service {
    client: Client,
    bucket: String,
}

impl S3Service {
    pub async fn new(
        bucket: String,
        region: String,
        access_key_id: String,
        secret_access_key: String,
    ) -> Self {
        let credentials = Credentials::new(access_key_id, secret_access_key, None, None, "static");

        let config = aws_config::ConfigLoader::default()
            .behavior_version(BehaviorVersion::latest())
            .region(aws_config::Region::new(region))
            .credentials_provider(credentials)
            .load()
            .await;

        let client = Client::new(&config);

        Self { client, bucket }
    }

    pub async fn from_settings(settings: &raptorflow_config::Settings) -> Self {
        let bucket = settings.s3_bucket.clone();
        let region = settings.aws_region.clone();

        let config = aws_config::ConfigLoader::default()
            .behavior_version(BehaviorVersion::latest())
            .region(aws_config::Region::new(region))
            .load()
            .await;

        let client = Client::new(&config);

        Self { client, bucket }
    }

    pub fn bucket(&self) -> &str {
        &self.bucket
    }

    pub async fn generate_presigned_put_url(
        &self,
        key: &str,
        content_type: Option<&str>,
        expires_in: u32,
    ) -> Result<String, S3Error> {
        let presigning_config = PresigningConfig::builder()
            .expires_in(Duration::from_secs(expires_in as u64))
            .build()
            .map_err(|e| S3Error::Config(e.to_string()))?;

        let builder = self
            .client
            .put_object()
            .bucket(&self.bucket)
            .key(key)
            .content_type(content_type.unwrap_or("application/octet-stream"));

        let presigned = builder
            .presigned(presigning_config)
            .await
            .map_err(|e| S3Error::Presigning(e.to_string()))?;

        Ok(presigned.uri().to_string())
    }

    pub async fn generate_presigned_get_url(
        &self,
        key: &str,
        expires_in: u32,
    ) -> Result<String, S3Error> {
        let presigning_config = PresigningConfig::builder()
            .expires_in(Duration::from_secs(expires_in as u64))
            .build()
            .map_err(|e| S3Error::Config(e.to_string()))?;

        let presigned = self
            .client
            .get_object()
            .bucket(&self.bucket)
            .key(key)
            .presigned(presigning_config)
            .await
            .map_err(|e| S3Error::Presigning(e.to_string()))?;

        Ok(presigned.uri().to_string())
    }

    pub async fn put_object(
        &self,
        key: &str,
        body: Vec<u8>,
        content_type: &str,
    ) -> Result<PutObjectResponse, S3Error> {
        let result = self
            .client
            .put_object()
            .bucket(&self.bucket)
            .key(key)
            .content_type(content_type)
            .body(body.into())
            .send()
            .await
            .map_err(|e| S3Error::Api(e.to_string()))?;

        Ok(PutObjectResponse {
            etag: result.e_tag().map(|s| s.to_string()).unwrap_or_default(),
            version_id: result.version_id().map(|s| s.to_string()),
        })
    }

    pub async fn get_object(&self, key: &str) -> Result<Vec<u8>, S3Error> {
        let result = self
            .client
            .get_object()
            .bucket(&self.bucket)
            .key(key)
            .send()
            .await
            .map_err(|e| S3Error::Api(e.to_string()))?;

        let bytes = result
            .body
            .collect()
            .await
            .map_err(|e| S3Error::Api(e.to_string()))?;

        Ok(bytes.to_vec())
    }

    pub async fn delete_object(&self, key: &str) -> Result<(), S3Error> {
        self.client
            .delete_object()
            .bucket(&self.bucket)
            .key(key)
            .send()
            .await
            .map_err(|e| S3Error::Api(e.to_string()))?;

        Ok(())
    }

    pub async fn head_object(&self, key: &str) -> Result<ObjectMetadata, S3Error> {
        let result = self
            .client
            .head_object()
            .bucket(&self.bucket)
            .key(key)
            .send()
            .await
            .map_err(|e| S3Error::Api(e.to_string()))?;

        Ok(ObjectMetadata {
            content_length: result.content_length.unwrap_or(0),
            content_type: result.content_type().map(|s| s.to_string()),
            etag: result.e_tag().map(|s| s.to_string()),
            last_modified: result.last_modified().map(|t| t.to_string()),
        })
    }

    pub fn object_key(prefix: &str, org_id: &str, filename: &str) -> String {
        format!("{}/{}/{}", prefix, org_id, filename)
    }
}

#[derive(Debug, Clone)]
pub struct ObjectMetadata {
    pub content_length: i64,
    pub content_type: Option<String>,
    pub etag: Option<String>,
    pub last_modified: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct PutObjectResponse {
    pub etag: String,
    #[serde(default)]
    pub version_id: Option<String>,
}

#[derive(Debug, thiserror::Error)]
pub enum S3Error {
    #[error("Config error: {0}")]
    Config(String),

    #[error("Presigning error: {0}")]
    Presigning(String),

    #[error("API error: {0}")]
    Api(String),

    #[error("Not found")]
    NotFound,
}

pub struct UploadManager {
    s3: S3Service,
}

impl UploadManager {
    pub fn new(s3: S3Service) -> Self {
        Self { s3 }
    }

    pub async fn generate_upload_url(
        &self,
        org_id: &str,
        filename: &str,
        content_type: &str,
    ) -> Result<UploadUrl, S3Error> {
        let key = S3Service::object_key("uploads", org_id, filename);
        let url = self
            .s3
            .generate_presigned_put_url(&key, Some(content_type), 3600)
            .await?;

        Ok(UploadUrl {
            upload_url: url,
            key,
            expires_in: 3600,
        })
    }

    pub async fn generate_download_url(&self, key: &str) -> Result<String, S3Error> {
        self.s3.generate_presigned_get_url(key, 3600).await
    }

    pub async fn delete_upload(&self, key: &str) -> Result<(), S3Error> {
        self.s3.delete_object(key).await
    }
}

pub struct ScreenshotManager {
    s3: S3Service,
}

impl ScreenshotManager {
    pub fn new(s3: S3Service) -> Self {
        Self { s3 }
    }

    pub async fn generate_upload_url(
        &self,
        org_id: &str,
        campaign_id: &str,
        filename: &str,
    ) -> Result<UploadUrl, S3Error> {
        let key = format!("screenshots/{}/{}/{}", org_id, campaign_id, filename);
        let url = self
            .s3
            .generate_presigned_put_url(&key, Some("image/png"), 3600)
            .await?;

        Ok(UploadUrl {
            upload_url: url,
            key,
            expires_in: 3600,
        })
    }
}

pub struct ExportManager {
    s3: S3Service,
}

impl ExportManager {
    pub fn new(s3: S3Service) -> Self {
        Self { s3 }
    }

    pub async fn generate_export_url(
        &self,
        org_id: &str,
        export_type: &str,
        filename: &str,
    ) -> Result<String, S3Error> {
        let key = format!("exports/{}/{}/{}", org_id, export_type, filename);
        self.s3
            .generate_presigned_put_url(&key, Some("application/json"), 86400)
            .await
    }

    pub async fn generate_download_url(&self, key: &str) -> Result<String, S3Error> {
        self.s3.generate_presigned_get_url(key, 86400).await
    }
}

#[derive(Debug, Serialize)]
pub struct UploadUrl {
    pub upload_url: String,
    pub key: String,
    pub expires_in: u32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_object_key() {
        let key = S3Service::object_key("uploads", "org-123", "file.pdf");
        assert_eq!(key, "uploads/org-123/file.pdf");
    }
}
