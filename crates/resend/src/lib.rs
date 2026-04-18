//! Resend email integration for RaptorFlow.
//!
//! Provides transactional email via the Resend API. Three email types are
//! implemented as ready-to-send functions:
//!
//! ## Email templates
//!
//! | Function | Trigger | Template |
//! |---|---|---|
//! | [`send_welcome_email()`] | New user signup | HTML welcome with onboarding steps |
//! | [`send_daily_wins_briefing()`] | Morning job | HTML briefing with insights + recommended action |
//! | [`send_payment_receipt()`] | Razorpay payment | HTML receipt with amount + invoice ID |
//!
//! ## Error handling
//!
//! [`ResendError`] is typed: `Network`, `Parse`, `Api(status, body)`, `Config`.

use reqwest::Client;
use serde::{Deserialize, Serialize};

#[derive(Clone)]
pub struct ResendClient {
    client: Client,
    api_key: String,
    from_email: String,
    base_url: String,
}

#[derive(Debug, Serialize)]
pub struct SendEmailRequest {
    pub from: EmailAddress,
    pub to: Vec<EmailAddress>,
    pub subject: String,
    pub html: Option<String>,
    pub text: Option<String>,
    pub reply_to: Option<EmailAddress>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EmailAddress {
    pub email: String,
    pub name: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct SendEmailResponse {
    pub id: String,
    pub from: EmailAddress,
    pub to: Vec<EmailAddress>,
    pub subject: String,
    pub created_at: bool,
}

#[derive(Debug, Deserialize)]
pub struct ApiError {
    pub message: String,
    pub name: String,
}

impl ResendClient {
    pub fn new(api_key: String, from_email: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
            from_email,
            base_url: "https://api.resend.com".to_string(),
        }
    }

    pub fn from_settings(settings: &raptorflow_config::Settings) -> Self {
        Self::new(
            settings.resend_api_key.clone(),
            settings.resend_from_email.clone(),
        )
    }

    pub async fn send_email(
        &self,
        to: &str,
        subject: &str,
        html: &str,
    ) -> Result<SendEmailResponse, ResendError> {
        let request = SendEmailRequest {
            from: EmailAddress {
                email: self.from_email.clone(),
                name: Some("RaptorFlow".to_string()),
            },
            to: vec![EmailAddress {
                email: to.to_string(),
                name: None,
            }],
            subject: subject.to_string(),
            html: Some(html.to_string()),
            text: None,
            reply_to: None,
        };

        let response = self
            .client
            .post(&format!("{}/emails", self.base_url))
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| ResendError::Network(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| ResendError::Parse(e.to_string()))
        } else {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            tracing::error!(status = %status, body = %text, "Resend API error");
            Err(ResendError::Api(status.as_u16(), text))
        }
    }

    pub async fn send_template(
        &self,
        to: &str,
        template_id: &str,
        variables: serde_json::Value,
    ) -> Result<SendEmailResponse, ResendError> {
        let request = serde_json::json!({
            "from": self.from_email,
            "to": to,
            "template_id": template_id,
            "variables": variables,
        });

        let response = self
            .client
            .post(&format!("{}/email-templates", self.base_url))
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| ResendError::Network(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| ResendError::Parse(e.to_string()))
        } else {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            Err(ResendError::Api(status.as_u16(), text))
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub enum ResendError {
    #[error("Network error: {0}")]
    Network(String),

    #[error("Parse error: {0}")]
    Parse(String),

    #[error("API error ({0}): {1}")]
    Api(u16, String),

    #[error("Configuration error: {0}")]
    Config(String),
}

pub async fn send_welcome_email(
    client: &ResendClient,
    to: &str,
    user_name: &str,
) -> Result<SendEmailResponse, ResendError> {
    let html = format!(
        r#"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to RaptorFlow</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a1a1a;">Welcome to RaptorFlow, {}!</h1>
            <p style="color: #4a4a4a; line-height: 1.6;">
                We're excited to have you on board. RaptorFlow is your AI-powered marketing intelligence platform that helps you create data-driven campaigns faster.
            </p>
            <p style="color: #4a4a4a; line-height: 1.6;">
                Here's what you can do next:
            </p>
            <ul style="color: #4a4a4a; line-height: 1.8;">
                <li>Complete your Foundation (21-screen onboarding)</li>
                <li>Set up your first campaign</li>
                <li>Explore the AI Council for strategic insights</li>
            </ul>
            <p style="color: #4a4a4a; line-height: 1.6;">
                If you have any questions, reply to this email and we'll get back to you within 24 hours.
            </p>
            <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 30px 0;">
            <p style="color: #8a8a8a; font-size: 12px;">
                The RaptorFlow Team
            </p>
        </body>
        </html>
        "#,
        user_name
    );

    client.send_email(to, "Welcome to RaptorFlow", &html).await
}

pub async fn send_daily_wins_briefing(
    client: &ResendClient,
    to: &str,
    org_name: &str,
    briefing: &str,
    recommended_action: &str,
) -> Result<SendEmailResponse, ResendError> {
    let html = format!(
        r#"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your Daily Wins Briefing</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a1a1a;">Your Daily Wins Briefing</h1>
            <p style="color: #4a4a4a;">Good morning, {}!</p>
            
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h2 style="color: #1a1a1a; margin-top: 0;">Today's Insights</h2>
                <p style="color: #4a4a4a; line-height: 1.6;">{}</p>
            </div>
            
            <div style="background: #e8f5e9; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h2 style="color: #2e7d32; margin-top: 0;">Recommended Action</h2>
                <p style="color: #4a4a4a; line-height: 1.6;">{}</p>
            </div>
            
            <p style="color: #4a4a4a; line-height: 1.6;">
                <a href="https://app.raptorflow.ai" style="color: #0066cc; text-decoration: none;">Open RaptorFlow</a> to learn more and take action.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 30px 0;">
            <p style="color: #8a8a8a; font-size: 12px;">
                Powered by RaptorFlow AI
            </p>
        </body>
        </html>
        "#,
        org_name, briefing, recommended_action
    );

    client
        .send_email(to, "Your Daily Wins Briefing", &html)
        .await
}

pub async fn send_payment_receipt(
    client: &ResendClient,
    to: &str,
    amount: &str,
    invoice_id: &str,
) -> Result<SendEmailResponse, ResendError> {
    let html = format!(
        r#"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Payment Receipt</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a1a1a;">Payment Receipt</h1>
            <p style="color: #4a4a4a;">Thank you for your payment!</p>
            
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <p style="margin: 5px 0; color: #4a4a4a;"><strong>Amount:</strong> {}</p>
                <p style="margin: 5px 0; color: #4a4a4a;"><strong>Invoice ID:</strong> {}</p>
                <p style="margin: 5px 0; color: #4a4a4a;"><strong>Date:</strong> {}</p>
            </div>
            
            <p style="color: #4a4a4a; line-height: 1.6;">
                Your subscription is now active. If you have any questions, please contact our support team.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 30px 0;">
            <p style="color: #8a8a8a; font-size: 12px;">
                Powered by RaptorFlow
            </p>
        </body>
        </html>
        "#,
        amount,
        invoice_id,
        chrono::Utc::now().format("%Y-%m-%d")
    );

    client
        .send_email(to, "RaptorFlow Payment Receipt", &html)
        .await
}
