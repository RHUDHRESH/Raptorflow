export const sessionEventTypes = [
  "session.started",
  "session.progress",
  "session.stream",
  "session.completed",
  "session.reconnect"
] as const;

export const foundationEventTypes = [
  "foundation.scan.started",
  "foundation.scan.progress",
  "foundation.scan.completed",
  "foundation.version.created",
  "foundation.version.updated",
  "foundation.section.injected",
  "foundation.snapshot.ready",
  "foundation.reconnect"
] as const;

export const councilEventTypes = [
  "council.started",
  "council.position",
  "council.synthesis",
  "council.reconnect"
] as const;

export const officeEventTypes = [
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
  "file_delivery_complete"
] as const;

export const wsEventTypes = [
  ...sessionEventTypes,
  ...foundationEventTypes,
  ...councilEventTypes,
  "office.event",
  "brief.progress",
  "research.requested",
  "research.completed",
  "tool.requested",
  "tool.completed",
  "harvester.recorded"
] as const;

export type WsEventType = (typeof wsEventTypes)[number];
export type FoundationEventType = (typeof foundationEventTypes)[number];
export type OfficeEventType = (typeof officeEventTypes)[number];
