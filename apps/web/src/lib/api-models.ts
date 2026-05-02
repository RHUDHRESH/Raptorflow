export interface UpdateAvatarSoulRequest {
  identity_kernel?: Record<string, unknown>;
  worldview?: string[];
  obsessions?: string[];
  reflexes?: string[];
  taboos?: string[];
  debate_style?: Record<string, unknown>;
  embodiment_level?: string;
  operating_principles?: string[];
  evaluation_bias?: Record<string, unknown>;
  is_active?: boolean;
}

export interface CreateMemoryEdgeRequest {
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy?: string;
  use_when: string;
}

export interface CreateInstinctFrameRequest {
  avatar_id: string;
  harness_run_id?: string;
  capability_run_id?: string;
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: Record<string, unknown>;
  recommended_posture: string;
  visible_summary: string;
  private_notes?: Record<string, unknown>;
}

export interface UpsertPresenceStateRequest {
  avatar_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  confidence: number;
  visible_summary: string;
  last_event_id?: string;
}

export interface CreateDebateEventRequest {
  speaker_avatar_id?: string;
  target_avatar_id?: string;
  event_type: string;
  stance?: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface CreateContextPackRequest {
  avatar_id?: string;
  capability_id?: string;
  capability_key?: string;
  campaign_id?: string;
  token_budget?: number;
}

export interface CreateCapabilityRunRequest {
  avatar_id: string;
  capability_key: string;
  campaign_id?: string;
  input: Record<string, unknown>;
  mode?: "draft" | "dry_run";
}

export interface GrantCapabilityRequest {
  capability_id: string;
  grant_scope?: string;
  constraints?: Record<string, unknown>;
}

export interface CreateArtifactVersionRequest {
  body: Record<string, unknown>;
  change_reason?: string;
}

// ─── TYPES ───────────────────────────────────────────────────────────────────

export interface DailyWin {
  win_id: string;
  generated_at: string;
  strategist_name: string;
  lead: { text: string; significance: string };
  context: Array<{ text: string; source: string }>;
  todays_focus: {
    action: string;
    rationale: string;
    action_type: "approve_content" | "review_campaign" | "respond_to_intel" | "strategic_review";
    action_data: { task_id?: string; campaign_id?: string };
  };
  viewed_at: string | null;
  status?: "not_started";
  message?: string;
}
export interface BackendDailyWin {
  briefing_id: string;
  briefing_date: string;
  generated_at: string;
  lead_summary: string;
  full_briefing: string;
  recommended_action: string;
  recommended_action_type: string;
  recommended_action_data: Record<string, unknown>;
  viewed_at: string | null;
  acted_on_at?: string | null;
  action_outcome?: string | null;
}

export interface FoundationResponse {
  orgId: string;
  version: number;
  sections: Record<string, any>;
  updatedAt: string;
}

export interface FoundationSnapshot {
  id: string;
  orgId: string;
  foundationVersion: number;
  sections: Record<string, any>;
  createdAt: string;
}

export interface SnapshotFullResponse {
  status: "not_started" | "in_progress" | "complete";
  completed_sections: string[];
  missing_sections: string[];
  last_updated_section?: string;
  version: number;
  sections: Record<string, any>;
}

export interface ScanJob {
  scan_id: string;
  status: "queued" | "running" | "completed" | "failed";
  progress?: number;
}

export interface QuickScanResult {
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  positioning_score: number;
  summary: string;
}

export interface Campaign {
  campaignId: string;
  campaign_id?: string; // Legacy/API compatibility
  orgId: string;
  name: string;
  status: "draft" | "pending_approval" | "active" | "paused" | "completed" | "archived";
  goal?: string;
  timeline?: string;
  channels?: string[];
  createdAt: string;
  updatedAt: string;
  goal_type: "awareness" | "leads" | "conversion" | "retention" | "re_engagement" | any;
  tasks_due_today?: number;
  tasks_completed?: number;
  tasks_total?: number;
  progress_pct: number;
  current_move_name?: string;
  start_date: string;
  end_date: string;
}

export interface CampaignDetail extends Campaign {
  council_rationale: { synthesis: string; participating_agents: string[] };
  outcome_projection: string;
  current_move?: {
    move_id: string;
    name: string;
    type: string;
    sub_goal: string;
    day_number: number;
    total_days: number;
    tasks_completed: number;
    tasks_total: number;
  };
}

export interface Move {
  move_id: string;
  move_number: number;
  name: string;
  type: string;
  sub_goal: string;
  start_date: string;
  end_date: string;
  status: "upcoming" | "active" | "completed" | "overdue";
  tasks_completed: number;
  tasks_total: number;
}

export interface Task {
  task_id: string;
  title: string;
  task_type:
    | "publish_content"
    | "review_performance"
    | "execute_ad"
    | "approve_content"
    | "research"
    | "setup";
  channel: string;
  status:
    | "pending"
    | "due"
    | "ready_for_review"
    | "approved"
    | "completed"
    | "missed"
    | "processing";
  content_ready: boolean;
  assigned_agent_key: string;
  assigned_agent_name: string;
  scheduled_date: string;
  move_name: string;
  priority?: "normal" | "high" | "critical";
}

export interface TaskDetail extends Task {
  description: string;
  campaign_name: string;
  content: {
    content_id: string;
    body: string;
    headline: string | null;
    hashtags: string[] | null;
    image_direction: string | null;
    posting_time: string | null;
    format: "social_post" | "email" | "ad_copy" | "long_form";
  } | null;
  performance_summary?: {
    metrics: Array<{
      label: string;
      value: string;
      vs_target: "above" | "on" | "below";
      trend: string;
    }>;
    recommendation: string;
  };
  ad_instruction?: string;
  ad_reasoning?: string;
}

export interface CreateCampaignRequest {
  name: string;
  goal?: string;
  timeline?: string;
  channels?: string[];
  goal_type?: string;
  start_date?: string;
  end_date?: string;
}
export interface CreateMoveRequest {
  name: string;
  type: string;
  sub_goal: string;
  start_date: string;
  end_date: string;
}
export interface CreateTaskRequest {
  title: string;
  task_type: Task["task_type"];
  channel: string;
  scheduled_date: string;
  assigned_agent_key?: string;
  move_id?: string;
}
export interface CreateBriefRequest {
  content: string;
  goal?: string;
}
export interface CampaignBrief {
  brief_id: string;
  campaign_id: string;
  content: string;
  status: "draft" | "approved" | "rejected";
  created_at: string;
}

export interface StartCouncilRequest {
  campaignId?: string;
  sessionType?: string;
  question?: string;
  agentRoster?: string[];
}
export interface CouncilSession {
  sessionId: string;
  orgId: string;
  campaignId: string;
  sessionType: string;
  status: string;
  createdAt: string;
  agentCount?: number;
  duration?: string;
}

export interface CouncilMessage {
  messageId: string;
  sessionId: string;
  content: string;
  createdAt: string;
}
export interface BackendCouncilPosition {
  position_id: string;
  avatar_key: string;
  round_number: number;
  content: string;
  extracted_ripple_data?: {
    key_risks?: string[];
    recommended_next_move?: string;
    ripple_candidates?: Array<{
      summary: string;
      salience: number;
      type: string;
    }>;
  };
  created_at: string;
}

export interface CouncilPollSessionResponse {
  session: BackendCouncilSession;
  positions?: BackendCouncilPosition[];
  status: string;
}

export interface CouncilPollMessagesResponse {
  session_id: string;
  positions: BackendCouncilPosition[];
  status: string;
}
export interface BackendCouncilSession {
  session_id: string;
  org_id: string;
  campaign_id?: string | null;
  session_type: string;
  status: string;
  question?: string;
  total_cost_usd?: number;
  created_at: string;
}

export interface MuseConversation {
  conversationId: string;
  orgId: string;
  route: string;
  lastMessageAt: string;
  messageCount: number;
  preview?: string;
  id?: string; // Some parts of the code use .id
  updated_at?: string;
}

export interface MusePromptRequest {
  conversationId?: string;
  route: string;
  message: string;
}
export interface MuseResponse {
  conversationId: string;
  message: { messageId: string; content: string };
  assistantMessageId?: string;
}
export interface BackendMuseConversation {
  conversation_id: string;
  route: string;
  created_at: string;
}
export interface BackendMuseMessage {
  message_id: string;
  role: string;
  body: string;
  created_at: string;
}

export interface Ripple {
  rippleId: string;
  orgId: string;
  agentId?: string;
  summaryText: string;
  rawText?: string;
  triggerText?: string;
  prediction?: string;
  sourceAgent?: string;
  confidence: number;
  salience?: number;
  hierarchyLevel: 1 | 2 | 3 | 4;
  importanceBand: "critical" | "strong" | "normal" | "disposable";
  retentionBand?: "hot" | "warm" | "cold" | "archived";
  memoryClass?: "episodic" | "semantic" | "procedural" | "identity" | "affective" | "preference";
  eventType?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface IntelSignal {
  signalId: string;
  competitorId: string;
  competitorName: string;
  category: "website" | "social" | "ads" | "seo" | "system" | string;
  title: string;
  description: string;
  extractedAt: string;
  significance: "low" | "medium" | "high" | "critical";
  implication?: string;
}

export interface IntelOverview {
  monitored_count: number;
  signals_24h: number;
  high_priority_count: number;
  latest_signals: IntelSignal[];
}

export interface ResearchRun {
  run_id: string;
  title: string;
  status: "running" | "completed" | "failed";
  progress: number;
  created_at: string;
}

export interface IntelDocument {
  document_id: string;
  title: string;
  source_type: string;
  content_preview: string;
  created_at: string;
}

export interface Competitor {
  id: string;
  name: string;
  websiteUrl?: string;
  monitors: string[];
  lastSeenAt: string;
}

export interface IntelStats {
  monitoredCount: number;
  signalsTwentyFourHours: number;
  highPriorityCount: number;
  categoryBreakdown: Record<string, number>;
}

export interface Essence {
  essenceId: string;
  orgId: string;
  avatarKey: string;
  content: string;
  category: string;
  createdAt: string;
}

export interface CreateRippleRequest {
  summaryText: string;
  rawText: string;
  sourceAgent?: string;
  confidence: number;
  importanceBand: Ripple["importanceBand"];
}
export interface UpdateRippleRequest {
  summaryText?: string;
  rawText?: string;
  importanceBand?: Ripple["importanceBand"];
}
export interface CreateEdgeRequest {
  targetId: string;
  edgeType: string;
}
export interface CreateEssenceRequest {
  avatarKey: string;
  content: string;
  category: string;
}
export interface UpdateEssenceRequest {
  content?: string;
  category?: string;
}

export interface GeneratedContentRecord {
  contentId: string;
  orgId: string;
  campaignId?: string;
  taskId?: string;
  contentType: string;
  status: string;
  body: Record<string, unknown>;
  createdAt: string;
}

export interface OfficeStateSnapshot {
  activeCampaigns: number;
  activeCouncilSessions: number;
  openNudges: number;
  recentMuseConversations: number;
  eventTypes: string[];
}

export interface BackendCampaign {
  campaign_id: string;
  org_id: string;
  name: string;
  goal: string;
  status: string;
  active_move_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BackendMove {
  move_id: string;
  campaign_id: string;
  move_type: string;
  sequence_number: number;
  status: string;
  created_at: string;
}

export interface BackendTask {
  task_id: string;
  move_id: string;
  campaign_id: string;
  title: string;
  status: string;
  scheduled_date?: string | null;
  created_at: string;
}

export interface BackendBrief {
  brief_id: string;
  campaign_id?: string | null;
  status: "draft" | "submitted" | "approved" | "rejected";
  original_text: string;
  created_at: string;
}

export interface BackendGeneratedContent {
  content_id: string;
  org_id: string;
  campaign_id?: string | null;
  task_id?: string | null;
  content_type: string;
  status: string;
  body: Record<string, unknown>;
  created_at: string;
}

export function normalizeDailyWin(win: BackendDailyWin): DailyWin {
  return {
    win_id: win.briefing_id,
    generated_at: win.generated_at,
    strategist_name: "Strategist",
    lead: {
      text: win.lead_summary,
      significance: "Grounded in the latest available product state.",
    },
    context: win.full_briefing ? [{ text: win.full_briefing, source: "daily_briefing" }] : [],
    todays_focus: {
      action: win.recommended_action,
      rationale: "Recommended from the current daily briefing.",
      action_type:
        (win.recommended_action_type as DailyWin["todays_focus"]["action_type"]) ??
        "strategic_review",
      action_data:
        (win.recommended_action_data as { task_id?: string; campaign_id?: string }) ?? {},
    },
    viewed_at: win.viewed_at,
  };
}

export function normalizeCampaign(campaign: BackendCampaign): Campaign {
  return {
    campaignId: campaign.campaign_id,
    campaign_id: campaign.campaign_id,
    orgId: campaign.org_id,
    name: campaign.name,
    status: campaign.status as Campaign["status"],
    goal: campaign.goal,
    goal_type: "awareness",
    progress_pct: 0,
    start_date: campaign.created_at,
    end_date: campaign.updated_at,
    createdAt: campaign.created_at,
    updatedAt: campaign.updated_at,
    timeline: `${campaign.created_at} → ${campaign.updated_at}`,
    channels: [],
    current_move_name: campaign.active_move_id ?? undefined,
    tasks_completed: 0,
    tasks_due_today: 0,
    tasks_total: 0,
  };
}

export function normalizeMove(move: BackendMove): Move {
  return {
    move_id: move.move_id,
    move_number: move.sequence_number,
    name: `${move.move_type} move`,
    type: move.move_type,
    sub_goal: move.move_type,
    start_date: move.created_at,
    end_date: move.created_at,
    status: move.status === "planned" ? "upcoming" : (move.status as Move["status"]),
    tasks_completed: 0,
    tasks_total: 0,
  };
}

export function normalizeTask(task: BackendTask): Task {
  return {
    task_id: task.task_id,
    title: task.title,
    task_type: "setup",
    channel: "general",
    status: task.status as Task["status"],
    content_ready: false,
    assigned_agent_key: "strategist",
    assigned_agent_name: "Strategist",
    scheduled_date: task.scheduled_date ?? task.created_at,
    move_name: task.move_id,
  };
}

export function normalizeCampaignDetail(
  campaign: BackendCampaign,
  moves: Move[],
  tasks: Task[],
): CampaignDetail {
  const currentMove = moves[0];
  return {
    ...normalizeCampaign(campaign),
    council_rationale: {
      synthesis: "Campaign detail is grounded in persisted backend campaign state.",
      participating_agents: [],
    },
    outcome_projection: "Projection will become richer as campaign performance data is populated.",
    current_move: currentMove
      ? {
          move_id: currentMove.move_id,
          name: currentMove.name,
          type: currentMove.type,
          sub_goal: currentMove.sub_goal,
          day_number: currentMove.move_number,
          total_days: moves.length,
          tasks_completed: tasks.filter((task) => task.status === "completed").length,
          tasks_total: tasks.length,
        }
      : undefined,
  };
}

export function normalizeBrief(brief: BackendBrief): CampaignBrief {
  return {
    brief_id: brief.brief_id,
    campaign_id: brief.campaign_id ?? "",
    content: brief.original_text,
    status: brief.status === "submitted" ? "draft" : (brief.status as CampaignBrief["status"]),
    created_at: brief.created_at,
  };
}

export function normalizeCouncilSession(session: BackendCouncilSession): CouncilSession {
  return {
    sessionId: session.session_id,
    orgId: session.org_id,
    campaignId: session.campaign_id ?? "",
    sessionType: session.session_type,
    status: session.status,
    createdAt: session.created_at,
    agentCount: 0,
  };
}

export function normalizeCouncilMessage(position: BackendCouncilPosition): CouncilMessage {
  return {
    messageId: position.position_id,
    sessionId: "",
    content: position.content,
    createdAt: position.created_at,
  };
}

export function normalizeMuseConversation(conversation: BackendMuseConversation): MuseConversation {
  return {
    conversationId: conversation.conversation_id,
    orgId: "",
    route: conversation.route,
    lastMessageAt: conversation.created_at,
    messageCount: 0,
    id: conversation.conversation_id,
    preview: conversation.route,
    updated_at: conversation.created_at,
  };
}

export function normalizeMuseMessage(message: BackendMuseMessage) {
  return {
    id: message.message_id,
    role: message.role,
    content: message.body,
    createdAt: message.created_at,
  };
}

export function normalizeGeneratedContent(
  content: BackendGeneratedContent,
): GeneratedContentRecord {
  return {
    contentId: content.content_id,
    orgId: content.org_id,
    campaignId: content.campaign_id ?? undefined,
    taskId: content.task_id ?? undefined,
    contentType: content.content_type,
    status: content.status,
    body: content.body,
    createdAt: content.created_at,
  };
}

export interface Avatar {
  avatarId: string;
  avatarKey: string;
  displayName: string;
  role: string;
  archetype: string;
  personality: Record<string, unknown>;
  systemPrompt: string;
  toolPermissions: Record<string, unknown>;
  memoryScope: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface BackendAvatar {
  avatar_id: string;
  avatar_key: string;
  display_name: string;
  role: string;
  archetype: string;
  personality: Record<string, unknown>;
  system_prompt: string;
  tool_permissions: Record<string, unknown>;
  memory_scope: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateAvatarRequest {
  avatar_key: string;
  display_name: string;
  role: string;
  archetype: string;
  personality?: Record<string, unknown>;
  system_prompt?: string;
  tool_permissions?: Record<string, unknown>;
  memory_scope?: string;
}

export interface UpdateAvatarRequest {
  display_name?: string;
  personality?: Record<string, unknown>;
  system_prompt?: string;
  tool_permissions?: Record<string, unknown>;
  is_active?: boolean;
}

export interface HarnessRun {
  runId: string;
  runType: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  errorMessage: string | null;
  createdBy: string | null;
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface BackendHarnessRun {
  run_id: string;
  run_type: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  error_message: string | null;
  created_by: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface HarnessStep {
  stepId: string;
  runId: string;
  avatarId: string | null;
  stepType: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  errorMessage: string | null;
  sequenceNumber: number;
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface BackendHarnessStep {
  step_id: string;
  run_id: string;
  avatar_id: string | null;
  step_type: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  error_message: string | null;
  sequence_number: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateHarnessRunRequest {
  run_type: string;
  input: Record<string, unknown>;
  avatar_keys?: string[];
  execute_now?: boolean;
}

export interface BackendCapabilityDefinition {
  capability_id: string;
  capability_key: string;
  name: string;
  domain: string;
  description: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  required_context: Record<string, unknown>;
  allowed_tools: Record<string, unknown>;
  artifact_type: string;
  evaluator_key: string;
  ripple_policy: Record<string, unknown>;
  risk_level: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BackendCapabilityRun {
  capability_run_id: string;
  org_id: string;
  avatar_id: string | null;
  capability_id: string;
  capability_key: string | null;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  error_message: string | null;
  model_id: string | null;
  token_usage: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BackendCapabilityArtifact {
  artifact_id: string;
  org_id: string;
  capability_run_id: string | null;
  avatar_id: string | null;
  capability_id: string | null;
  artifact_type: string;
  title: string;
  body: Record<string, unknown>;
  status: string;
  version: number;
  evaluation: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export function normalizeAvatar(a: BackendAvatar): Avatar {
  return {
    avatarId: a.avatar_id,
    avatarKey: a.avatar_key,
    displayName: a.display_name,
    role: a.role,
    archetype: a.archetype,
    personality: a.personality,
    systemPrompt: a.system_prompt,
    toolPermissions: a.tool_permissions,
    memoryScope: a.memory_scope,
    isActive: a.is_active,
    createdAt: a.created_at,
    updatedAt: a.updated_at,
  };
}

export function normalizeHarnessRun(r: BackendHarnessRun): HarnessRun {
  return {
    runId: r.run_id,
    runType: r.run_type,
    status: r.status,
    input: r.input,
    output: r.output,
    errorMessage: r.error_message,
    createdBy: r.created_by,
    startedAt: r.started_at,
    completedAt: r.completed_at,
    createdAt: r.created_at,
    updatedAt: r.updated_at,
  };
}

export function normalizeHarnessStep(s: BackendHarnessStep): HarnessStep {
  return {
    stepId: s.step_id,
    runId: s.run_id,
    avatarId: s.avatar_id,
    stepType: s.step_type,
    status: s.status,
    input: s.input,
    output: s.output,
    errorMessage: s.error_message,
    sequenceNumber: s.sequence_number,
    startedAt: s.started_at,
    completedAt: s.completed_at,
    createdAt: s.created_at,
    updatedAt: s.updated_at,
  };
}

export interface BackendAvatarSoul {
  soul_id: string;
  avatar_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: unknown;
  obsessions: unknown;
  reflexes: unknown;
  taboos: unknown;
  debate_style: Record<string, unknown>;
  embodiment_level: string;
  operating_principles: unknown;
  evaluation_bias: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BackendAvatarMemoryEdge {
  memory_edge_id: string;
  avatar_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface BackendAvatarInstinctFrame {
  instinct_frame_id: string;
  avatar_id: string;
  harness_run_id: string | null;
  capability_run_id: string | null;
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: Record<string, unknown>;
  recommended_posture: string;
  visible_summary: string;
  created_at: string;
}

export interface BackendAvatarPresenceState {
  presence_id: string;
  avatar_id: string;
  harness_run_id: string | null;
  state: string;
  current_focus: string;
  current_concern: string;
  confidence: number;
  visible_summary: string;
  last_event_id: string | null;
  updated_at: string;
}

export interface BackendAvatarDebateEvent {
  debate_event_id: string;
  harness_run_id: string;
  speaker_avatar_id: string | null;
  target_avatar_id: string | null;
  event_type: string;
  stance: string | null;
  content: Record<string, unknown>;
  confidence: number;
  created_at: string;
}

export interface BackendAvatarArtifactTrail {
  trail_id: string;
  avatar_id: string;
  artifact_id: string;
  harness_run_id: string | null;
  contribution_type: string;
  summary: string;
  created_at: string;
}

export interface AvatarSoul {
  soulId: string;
  avatarId: string;
  identityKernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  debateStyle: Record<string, unknown>;
  embodimentLevel: string;
  operatingPrinciples: string[];
  evaluationBias: Record<string, unknown>;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AvatarMemoryEdge {
  memoryEdgeId: string;
  avatarId: string;
  rippleId: string;
  relationshipType: string;
  salience: number;
  decayPolicy: string;
  useWhen: string;
  lastUsedAt: string | null;
  createdAt: string;
}

export interface AvatarPresenceState {
  presenceId: string;
  avatarId: string;
  harnessRunId: string | null;
  state: string;
  currentFocus: string;
  currentConcern: string;
  confidence: number;
  visibleSummary: string;
  lastEventId: string | null;
  updatedAt: string;
}

export interface AvatarDebateEvent {
  debateEventId: string;
  harnessRunId: string;
  speakerAvatarId: string | null;
  targetAvatarId: string | null;
  eventType: string;
  stance: string | null;
  content: Record<string, unknown>;
  confidence: number;
  createdAt: string;
}

export interface AvatarArtifactTrail {
  trailId: string;
  avatarId: string;
  artifactId: string;
  harnessRunId: string | null;
  contributionType: string;
  summary: string;
  createdAt: string;
}

export function normalizeAvatarSoul(s: BackendAvatarSoul): AvatarSoul {
  return {
    soulId: s.soul_id,
    avatarId: s.avatar_id,
    identityKernel: s.identity_kernel,
    worldview: Array.isArray(s.worldview) ? (s.worldview as string[]) : [],
    obsessions: Array.isArray(s.obsessions) ? (s.obsessions as string[]) : [],
    reflexes: Array.isArray(s.reflexes) ? (s.reflexes as string[]) : [],
    taboos: Array.isArray(s.taboos) ? (s.taboos as string[]) : [],
    debateStyle: s.debate_style,
    embodimentLevel: s.embodiment_level,
    operatingPrinciples: Array.isArray(s.operating_principles)
      ? (s.operating_principles as string[])
      : [],
    evaluationBias: s.evaluation_bias,
    isActive: s.is_active,
    createdAt: s.created_at,
    updatedAt: s.updated_at,
  };
}

export function normalizeAvatarMemoryEdge(e: BackendAvatarMemoryEdge): AvatarMemoryEdge {
  return {
    memoryEdgeId: e.memory_edge_id,
    avatarId: e.avatar_id,
    rippleId: e.ripple_id,
    relationshipType: e.relationship_type,
    salience: e.salience,
    decayPolicy: e.decay_policy,
    useWhen: e.use_when,
    lastUsedAt: e.last_used_at,
    createdAt: e.created_at,
  };
}

export function normalizeAvatarPresenceState(p: BackendAvatarPresenceState): AvatarPresenceState {
  return {
    presenceId: p.presence_id,
    avatarId: p.avatar_id,
    harnessRunId: p.harness_run_id,
    state: p.state,
    currentFocus: p.current_focus,
    currentConcern: p.current_concern,
    confidence: p.confidence,
    visibleSummary: p.visible_summary,
    lastEventId: p.last_event_id,
    updatedAt: p.updated_at,
  };
}

export function normalizeAvatarDebateEvent(e: BackendAvatarDebateEvent): AvatarDebateEvent {
  return {
    debateEventId: e.debate_event_id,
    harnessRunId: e.harness_run_id,
    speakerAvatarId: e.speaker_avatar_id,
    targetAvatarId: e.target_avatar_id,
    eventType: e.event_type,
    stance: e.stance,
    content: e.content,
    confidence: e.confidence,
    createdAt: e.created_at,
  };
}

export function normalizeAvatarArtifactTrail(t: BackendAvatarArtifactTrail): AvatarArtifactTrail {
  return {
    trailId: t.trail_id,
    avatarId: t.avatar_id,
    artifactId: t.artifact_id,
    harnessRunId: t.harness_run_id,
    contributionType: t.contribution_type,
    summary: t.summary,
    createdAt: t.created_at,
  };
}
