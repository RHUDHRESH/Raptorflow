#!/usr/bin/env node
/**
 * scripts/mock-office-server.ts
 *
 * A lightweight WebSocket server that replays canned office events on a timer.
 * Used for offline development when NEXT_PUBLIC_OFFLINE_MODE=true.
 *
 * Usage:
 *   npx tsx scripts/mock-office-server.ts
 *
 * Runs on ws://localhost:3001 by default.
 */

import { WebSocketServer, type WebSocket } from "ws";

const PORT = Number(process.env["WS_PORT"] ?? 3001);
const EVENT_INTERVAL_MS = Number(process.env["EVENT_INTERVAL_MS"] ?? 3500);

const ORG_ID = "dev-org-0000-0000-0000-000000000000";

interface OfficeEvent {
  orgId: string;
  type: "office.event";
  eventType: string;
  payload: Record<string, unknown>;
}

const eventSequence: OfficeEvent[] = [
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "morning_meeting_start",
    payload: { room: "conference-room", speaker: "Strategist" },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "speech_bubble",
    payload: { agent: "ogilvy", content: "The brief is not a suggestion." },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "brief_reading",
    payload: { agent: "strategist", content: "Reading campaign brief for Q2 Growth Push..." },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "agent_walk_start",
    payload: { agent: "sharp", destination: "research-station" },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "agent_seated_conference",
    payload: { agent: "cialdini", zone: "conference-room" },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "intel_alert_received",
    payload: { zone: "debug-nook", severity: "major", message: "Competitor launched new campaign" },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "debate_agent_speaking",
    payload: { agent: "ogilvy", round: 1, content: "The differentiation needs to be sharper." },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "debate_agent_reacting",
    payload: { agent: "patel", round: 1, content: "The data doesn't support that claim." },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "synthesis_presenting",
    payload: { speaker: "strategist", content: "Recommendation: shift 40% budget to LinkedIn." },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "move_completed_celebration",
    payload: { moveType: "awareness", campaignId: "campaign-001" },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "campaign_task_ready",
    payload: { taskId: "task-042", campaignId: "campaign-001", title: "Draft LinkedIn post" },
  },
  {
    orgId: ORG_ID,
    type: "office.event",
    eventType: "snark_refresh",
    payload: { speaker: "qa-director", content: "Everything looks stable. For now." },
  },
];

const wss = new WebSocketServer({ port: PORT });

let eventIndex = 0;

wss.on("connection", (ws: WebSocket) => {
  console.log(`[mock-office] Client connected. Streaming ${eventSequence.length} events...`);

  let interval: NodeJS.Timeout | null = null;

  const sendNext = () => {
    if (eventIndex < eventSequence.length) {
      const event = eventSequence[eventIndex++];
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(event));
      }
    } else {
      if (interval) clearInterval(interval);
      eventIndex = 0;
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({
            orgId: ORG_ID,
            type: "office.event",
            eventType: "conference_break",
            payload: { reason: "Sequence complete — looping back" },
          }),
        );
      }
      interval = setInterval(sendNext, EVENT_INTERVAL_MS);
    }
  };

  interval = setInterval(sendNext, EVENT_INTERVAL_MS);

  ws.on("close", () => {
    if (interval) clearInterval(interval);
    console.log(`[mock-office] Client disconnected.`);
  });

  ws.on("error", (err) => {
    console.error(`[mock-office] WebSocket error:`, err.message);
  });
});

wss.on("listening", () => {
  console.log(`[mock-office] Mock office WebSocket server running on ws://localhost:${PORT}`);
  console.log(`[mock-office] Event interval: ${EVENT_INTERVAL_MS}ms`);
  console.log(`[mock-office] Events: ${eventSequence.length}`);
});

wss.on("error", (err) => {
  console.error(`[mock-office] Server error:`, err.message);
});
