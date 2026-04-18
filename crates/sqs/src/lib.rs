//! AWS SQS job queue client for RaptorFlow.
//!
//! Provides a typed SQS client for enqueuing and dequeuing background jobs.
//! Two job queues are defined:
//!
//! ## Queues
//!
//! | Queue | URL env var | Purpose |
//! |---|---|---|
//! | Embedding | `RAPTORFLOW_SQS_EMBEDDING_QUEUE` | Ripple text → vector embedding |
//! | Content generation | `RAPTORFLOW_SQS_CONTENT_QUEUE` | AI content generation tasks |
//!
//! ## Key types
//!
//! - [`SqsClient`] — low-level send/receive/delete
//! - [`SqsJobQueue`] — high-level job enqueue/dequeue/acknowledge
//! - [`JobPayload`] — enum over embedding and content-generation job variants
//!
//! ## SQS base URL
//!
//! The SQS base URL is read from `RAPTORFLOW_SQS_BASE_URL` (defaults to
//! `https://sqs.ap-south-1.amazonaws.com`). Pass it via `SqsClient::new`.

use reqwest::Client;
use serde::Deserialize;

#[derive(Clone)]
pub struct SqsClient {
    client: Client,
    account_id: String,
    base_url: String,
}

impl SqsClient {
    pub fn new(account_id: String, base_url: String) -> Self {
        Self {
            client: Client::new(),
            account_id,
            base_url,
        }
    }

    pub async fn send_message(
        &self,
        queue_url: &str,
        message_body: &str,
        delay_seconds: Option<u32>,
    ) -> Result<SendMessageResponse, SqsError> {
        let full_queue_url = if queue_url.starts_with("https://") {
            queue_url.to_string()
        } else {
            format!("{}/{}/{}", self.base_url, self.account_id, queue_url)
        };

        let mut params = vec![
            ("Action".to_string(), "SendMessage".to_string()),
            ("Version".to_string(), "2012-11-05".to_string()),
            ("MessageBody".to_string(), message_body.to_string()),
        ];

        if let Some(delay) = delay_seconds {
            params.push(("DelaySeconds".to_string(), delay.to_string()));
        }

        let body = params
            .iter()
            .map(|(k, v)| format!("{}={}", k, percent_encoding::encode(v)))
            .collect::<Vec<_>>()
            .join("&");

        let response = self
            .client
            .post(&full_queue_url)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .await
            .map_err(|e| SqsError::Network(e.to_string()))?;

        if response.status().is_success() {
            let body = response
                .text()
                .await
                .map_err(|e| SqsError::Parse(e.to_string()))?;
            let parsed: SendMessageResult =
                serde_xml_rs::de::from_str(&body).map_err(|e| SqsError::Parse(e.to_string()))?;
            Ok(SendMessageResponse {
                message_id: parsed.message_id,
                md5_of_message_body: parsed.md5_of_message_body,
            })
        } else {
            Err(SqsError::Api(response.status().as_u16()))
        }
    }

    pub async fn receive_messages(
        &self,
        queue_url: &str,
        max_messages: Option<i32>,
        wait_time_seconds: Option<i32>,
    ) -> Result<Vec<SqsMessage>, SqsError> {
        let full_queue_url = if queue_url.starts_with("https://") {
            queue_url.to_string()
        } else {
            format!("{}/{}/{}", self.base_url, self.account_id, queue_url)
        };

        let mut params = vec![
            ("Action".to_string(), "ReceiveMessage".to_string()),
            ("Version".to_string(), "2012-11-05".to_string()),
        ];

        if let Some(max) = max_messages {
            params.push(("MaxNumberOfMessages".to_string(), max.to_string()));
        }

        if let Some(wait) = wait_time_seconds {
            params.push(("WaitTimeSeconds".to_string(), wait.to_string()));
        }

        let body = params
            .iter()
            .map(|(k, v)| format!("{}={}", k, percent_encoding::encode(v)))
            .collect::<Vec<_>>()
            .join("&");

        let response = self
            .client
            .post(&full_queue_url)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .await
            .map_err(|e| SqsError::Network(e.to_string()))?;

        if response.status().is_success() {
            let body = response
                .text()
                .await
                .map_err(|e| SqsError::Parse(e.to_string()))?;
            let parsed: ReceiveMessageResult =
                serde_xml_rs::de::from_str(&body).map_err(|e| SqsError::Parse(e.to_string()))?;
            Ok(parsed.messages.unwrap_or_default())
        } else {
            Err(SqsError::Api(response.status().as_u16()))
        }
    }

    pub async fn delete_message(
        &self,
        queue_url: &str,
        receipt_handle: &str,
    ) -> Result<(), SqsError> {
        let full_queue_url = if queue_url.starts_with("https://") {
            queue_url.to_string()
        } else {
            format!("{}/{}/{}", self.base_url, self.account_id, queue_url)
        };

        let body = format!(
            "Action=DeleteMessage&Version=2012-11-05&ReceiptHandle={}",
            percent_encoding::encode(receipt_handle)
        );

        let response = self
            .client
            .post(&full_queue_url)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .await
            .map_err(|e| SqsError::Network(e.to_string()))?;

        if response.status().is_success() {
            Ok(())
        } else {
            Err(SqsError::Api(response.status().as_u16()))
        }
    }
}

#[derive(Debug, Deserialize)]
struct SendMessageResult {
    #[serde(rename = "MessageId")]
    message_id: String,
    #[serde(rename = "MD5OfMessageBody")]
    md5_of_message_body: String,
}

#[derive(Debug, Deserialize)]
struct ReceiveMessageResult {
    #[serde(rename = "Message")]
    messages: Option<Vec<SqsMessage>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SqsMessage {
    #[serde(rename = "MessageId")]
    pub message_id: String,
    #[serde(rename = "ReceiptHandle")]
    pub receipt_handle: String,
    #[serde(rename = "MD5OfBody")]
    pub md5_of_body: String,
    #[serde(rename = "Body")]
    pub body: String,
    #[serde(rename = "Attribute")]
    pub attributes: Option<std::collections::HashMap<String, String>>,
}

#[derive(Debug, Deserialize)]
pub struct SendMessageResponse {
    pub message_id: String,
    pub md5_of_message_body: String,
}

#[derive(Debug, thiserror::Error)]
pub enum SqsError {
    #[error("Network error: {0}")]
    Network(String),

    #[error("Parse error: {0}")]
    Parse(String),

    #[error("API error: {0}")]
    Api(u16),
}

pub struct SqsJobQueue {
    client: SqsClient,
}

impl SqsJobQueue {
    pub fn new(client: SqsClient) -> Self {
        Self { client }
    }

    pub async fn enqueue_embedding_job(
        &self,
        queue_url: &str,
        org_id: &str,
        ripple_id: &str,
        text: &str,
    ) -> Result<String, SqsError> {
        let job = serde_json::json!({
            "job_type": "embedding",
            "org_id": org_id,
            "ripple_id": ripple_id,
            "text": text
        });

        let body = job.to_string();
        let response = self.client.send_message(queue_url, &body, None).await?;
        Ok(response.message_id)
    }

    pub async fn enqueue_content_generation_job(
        &self,
        queue_url: &str,
        org_id: &str,
        task_id: &str,
        prompt: &str,
    ) -> Result<String, SqsError> {
        let job = serde_json::json!({
            "job_type": "content_generation",
            "org_id": org_id,
            "task_id": task_id,
            "prompt": prompt
        });

        let body = job.to_string();
        let response = self.client.send_message(queue_url, &body, None).await?;
        Ok(response.message_id)
    }

    pub async fn dequeue_jobs(&self, queue_url: &str) -> Result<Vec<JobMessage>, SqsError> {
        let messages = self
            .client
            .receive_messages(queue_url, Some(10), Some(20))
            .await?;

        let mut jobs = Vec::new();
        for msg in messages {
            if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(&msg.body) {
                let job_type = parsed
                    .get("job_type")
                    .and_then(|v| v.as_str())
                    .unwrap_or("unknown");

                let payload = match job_type {
                    "embedding" => JobPayload::Embedding(EmbeddingJob {
                        org_id: parsed
                            .get("org_id")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        ripple_id: parsed
                            .get("ripple_id")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        text: parsed
                            .get("text")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                    }),
                    "content_generation" => JobPayload::ContentGeneration(ContentGenerationJob {
                        org_id: parsed
                            .get("org_id")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        task_id: parsed
                            .get("task_id")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        prompt: parsed
                            .get("prompt")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                    }),
                    _ => continue,
                };

                jobs.push(JobMessage {
                    message_id: msg.message_id,
                    receipt_handle: msg.receipt_handle,
                    payload,
                });
            }
        }

        Ok(jobs)
    }

    pub async fn acknowledge_job(
        &self,
        queue_url: &str,
        receipt_handle: &str,
    ) -> Result<(), SqsError> {
        self.client.delete_message(queue_url, receipt_handle).await
    }
}

#[derive(Debug, Clone)]
pub enum JobPayload {
    Embedding(EmbeddingJob),
    ContentGeneration(ContentGenerationJob),
}

#[derive(Debug, Clone)]
pub struct EmbeddingJob {
    pub org_id: String,
    pub ripple_id: String,
    pub text: String,
}

#[derive(Debug, Clone)]
pub struct ContentGenerationJob {
    pub org_id: String,
    pub task_id: String,
    pub prompt: String,
}

pub struct JobMessage {
    pub message_id: String,
    pub receipt_handle: String,
    pub payload: JobPayload,
}

mod percent_encoding {
    pub fn encode(input: &str) -> String {
        let mut result = String::new();
        for byte in input.bytes() {
            match byte {
                b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                    result.push(byte as char);
                }
                _ => {
                    result.push_str(&format!("%{:02X}", byte));
                }
            }
        }
        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_url_encoding() {
        assert_eq!(percent_encoding::encode("hello world"), "hello%20world");
        assert_eq!(percent_encoding::encode("key=value"), "key%3Dvalue");
    }
}
