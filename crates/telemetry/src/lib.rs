//! Tracing and Sentry initialisation for RaptorFlow services.
//!
//! This crate wires together:
//! - structured JSON logs via `tracing_subscriber`
//! - Sentry error capture
//! - Sentry log capture for warnings/errors
//!
//! The caller keeps the returned Sentry guard alive for the lifetime of the
//! process so buffered events can flush on shutdown.

use anyhow::Result;
use std::borrow::Cow;
use sentry::ClientInitGuard;
use sentry::integrations::tracing::EventFilter;
use tracing_subscriber::{EnvFilter, fmt, layer::SubscriberExt, util::SubscriberInitExt};

pub fn init(
    service_name: &str,
    sentry_dsn: Option<&str>,
    environment: Option<&str>,
) -> Result<Option<ClientInitGuard>> {
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    let sentry_guard = init_sentry(service_name, sentry_dsn, environment);

    if sentry_guard.is_some() {
        let sentry_layer = sentry::integrations::tracing::layer().event_filter(|metadata| {
            match *metadata.level() {
                tracing::Level::ERROR => EventFilter::Event | EventFilter::Log,
                tracing::Level::WARN => EventFilter::Log,
                tracing::Level::INFO => EventFilter::Log,
                tracing::Level::DEBUG | tracing::Level::TRACE => EventFilter::Ignore,
            }
        });

        tracing_subscriber::registry()
            .with(filter)
            .with(
                fmt::layer()
                    .json()
                    .with_target(true)
                    .with_thread_ids(true)
                    .with_thread_names(true),
            )
            .with(sentry_layer)
            .try_init()?;
    } else {
        tracing_subscriber::registry()
            .with(filter)
            .with(
                fmt::layer()
                    .json()
                    .with_target(true)
                    .with_thread_ids(true)
                    .with_thread_names(true),
            )
            .try_init()?;
    }

    tracing::info!(
        service = service_name,
        sentry_enabled = sentry_guard.is_some(),
        "telemetry initialized"
    );

    Ok(sentry_guard)
}

fn init_sentry(
    service_name: &str,
    sentry_dsn: Option<&str>,
    environment: Option<&str>,
) -> Option<ClientInitGuard> {
    let dsn = sentry_dsn?.trim();
    if dsn.is_empty() {
        return None;
    }

    let guard = sentry::init((
        dsn,
        sentry::ClientOptions {
            release: sentry::release_name!(),
            environment: environment
                .map(|value| Cow::<str>::Owned(value.trim().to_owned()))
                .filter(|value| !value.is_empty()),
            enable_logs: true,
            traces_sample_rate: 1.0,
            sample_rate: 1.0,
            ..Default::default()
        },
    ));

    sentry::configure_scope(|scope| {
        scope.set_tag("service", service_name);
        scope.set_tag("component", "backend");
    });

    Some(guard)
}
