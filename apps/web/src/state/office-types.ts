import type { OfficeEventMessage } from "@raptorflow/contracts";

export type OfficeMode = "passive" | "active" | "debug";

export type OfficeSurface = "floor_plan" | "conference_room" | "snark" | "roster" | "debug";

export interface OfficeZone {
  id: string;
  label: string;
  kind: "entry" | "workspace" | "meeting" | "research" | "debug";
  capacity: string;
  status: "quiet" | "active" | "paused" | "instrumented";
  note: string;
}

export interface OfficeAgent {
  agentKey: string;
  displayName: string;
  role: string;
  zoneId: string;
  posture: string;
  status: "idle" | "working" | "speaking" | "researching";
}

export interface OfficeSnarkLine {
  id: string;
  speaker: string;
  body: string;
  tone: "dry" | "warm" | "observant" | "needle";
}

export interface OfficeDebugSurface {
  id: string;
  label: string;
  value: string;
  hint: string;
}

export const officeEventTypes = [
  "file_delivery_start",
  "file_delivery_complete",
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
] as const;

export const officeFloorPlan: OfficeZone[] = [
  {
    id: "lobby",
    label: "Lobby",
    kind: "entry",
    capacity: "1-2 visitors",
    status: "quiet",
    note: "Intake and entry-state coordination.",
  },
  {
    id: "strategist-office",
    label: "Strategist Office",
    kind: "workspace",
    capacity: "1 strategist",
    status: "active",
    note: "Foundation-aware synthesis and daily routing.",
  },
  {
    id: "conference-room",
    label: "Conference Room",
    kind: "meeting",
    capacity: "4-8 agents",
    status: "instrumented",
    note: "Council debates, walk-backs, and synthesis playback.",
  },
  {
    id: "research-station",
    label: "Research Station",
    kind: "research",
    capacity: "2 interns",
    status: "active",
    note: "Blocking and background research requests.",
  },
  {
    id: "creative-pod",
    label: "Creative Pod",
    kind: "workspace",
    capacity: "Copy and content",
    status: "paused",
    note: "Campaign content prep and snark generation.",
  },
  {
    id: "digital-pod",
    label: "Digital Pod",
    kind: "workspace",
    capacity: "Performance and paid",
    status: "quiet",
    note: "Channel-specific execution and adjustments.",
  },
  {
    id: "debug-nook",
    label: "Debug Nook",
    kind: "debug",
    capacity: "Operators only",
    status: "instrumented",
    note: "Transport, cache, and contract inspection.",
  },
  {
    id: "intern-bay",
    label: "Intern Bay",
    kind: "workspace",
    capacity: "Rotating interns",
    status: "active",
    note: "Task delegation and return-path tracking.",
  },
];

export const officeRoster: OfficeAgent[] = [
  {
    agentKey: "strategist",
    displayName: "Strategist",
    role: "Session orchestrator",
    zoneId: "strategist-office",
    posture: "reading Foundation",
    status: "working",
  },
  {
    agentKey: "ogilvy",
    displayName: "Ogilvy",
    role: "Copy and positioning",
    zoneId: "creative-pod",
    posture: "reviewing copy",
    status: "speaking",
  },
  {
    agentKey: "patel",
    displayName: "Patel",
    role: "Analytics and pressure testing",
    zoneId: "digital-pod",
    posture: "checking measurements",
    status: "working",
  },
  {
    agentKey: "sharp",
    displayName: "Sharp",
    role: "Research and evidence",
    zoneId: "research-station",
    posture: "cross-checking sources",
    status: "researching",
  },
  {
    agentKey: "cialdini",
    displayName: "Cialdini",
    role: "Behavior and persuasion",
    zoneId: "conference-room",
    posture: "listening for cues",
    status: "idle",
  },
  {
    agentKey: "qa-director",
    displayName: "QA Director",
    role: "Quality gate and review",
    zoneId: "debug-nook",
    posture: "watching for regressions",
    status: "idle",
  },
];

export const officeSnarkLines: OfficeSnarkLine[] = [
  {
    id: "snark-1",
    speaker: "QA Director",
    body: "If the office says it's moving, I expect the camera to agree.",
    tone: "needle",
  },
  {
    id: "snark-2",
    speaker: "Ogilvy",
    body: "Nobody touches the brief until the evidence is in the room.",
    tone: "dry",
  },
  {
    id: "snark-3",
    speaker: "Cialdini",
    body: "The room looks calmer when the snark is in the right channel.",
    tone: "warm",
  },
];

export const officeDebugSurfaces: OfficeDebugSurface[] = [
  {
    id: "transport",
    label: "Transport",
    value: "WebSocket scaffold active",
    hint: "Session and council streams remain separate surfaces.",
  },
  {
    id: "cache",
    label: "Cache",
    value: "Foundation cache reserved",
    hint: "Invalidation hooks will hang off this surface.",
  },
  {
    id: "contracts",
    label: "Contracts",
    value: "Office event schema expanded",
    hint: "Payloads are still stubbed by design.",
  },
];

export const officeSeedEvents: OfficeEventMessage[] = [
  {
    orgId: "00000000-0000-0000-0000-000000000000",
    type: "office.event",
    eventType: "morning_meeting_start",
    payload: {
      room: "conference-room",
      speaker: "Strategist",
    },
  },
  {
    orgId: "00000000-0000-0000-0000-000000000000",
    type: "office.event",
    eventType: "speech_bubble",
    payload: {
      agent: "ogilvy",
      content: "The brief is not a suggestion.",
    },
  },
  {
    orgId: "00000000-0000-0000-0000-000000000000",
    type: "office.event",
    eventType: "intel_alert_received",
    payload: {
      zone: "debug-nook",
      severity: "major",
    },
  },
];
