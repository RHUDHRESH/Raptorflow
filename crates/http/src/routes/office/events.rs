use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{RwLock, broadcast};

#[derive(Debug, Clone, serde::Serialize)]
pub struct OfficeEvent {
    pub event_type: String,
    pub org_id: String,
    pub payload: serde_json::Value,
    pub timestamp: String,
}

pub struct EventBus {
    sender: broadcast::Sender<OfficeEvent>,
    subscriptions: Arc<RwLock<HashMap<String, broadcast::Receiver<OfficeEvent>>>>,
}

pub const OFFICE_EVENT_TYPES: &[&str] = &[
    "file_delivery_start",
    "file_delivered_to_maya",
    "file_delivered_to_strategist",
    "brief_reading",
    "brief_accepted",
    "brief_clarification_needed",
    "pager_notification",
    "agent_walk_start",
    "agent_seated_conference",
    "debate_agent_speaking",
    "debate_agent_reacting",
    "synthesis_presenting",
    "conference_break",
    "move_completed_celebration",
    "task_missed_notification",
    "intel_alert_received",
    "morning_meeting_start",
    "speech_bubble",
    "agent_working",
    "council_pager",
    "council_walk",
    "council_debate",
    "council_synthesis",
    "snark_refresh",
    "campaign_task_ready",
    "file_delivery_complete",
    "campaign_created",
    "nudge_created",
    "daily_win_available",
    "replan_triggered",
];

impl EventBus {
    pub fn new() -> Self {
        let (sender, _) = broadcast::channel(1000);
        Self {
            sender,
            subscriptions: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub async fn subscribe(&self, org_id: &str) -> broadcast::Receiver<OfficeEvent> {
        let mut subs = self.subscriptions.write().await;
        if let Some(rx) = subs.get_mut(org_id) {
            rx.resubscribe()
        } else {
            let rx = self.sender.subscribe();
            subs.insert(org_id.to_string(), rx.resubscribe());
            rx
        }
    }

    pub async fn publish(&self, event: OfficeEvent) {
        let _ = self.sender.send(event);
    }

    pub fn publish_sync(&self, event: OfficeEvent) {
        let _ = self.sender.send(event);
    }

    pub async fn get_receiver(&self, org_id: &str) -> Option<broadcast::Receiver<OfficeEvent>> {
        let subs = self.subscriptions.read().await;
        subs.get(org_id).map(|rx| rx.resubscribe())
    }
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}
