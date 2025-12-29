'use client';

import {
  Campaign,
  CampaignObjective,
  ChecklistItem,
  Move,
  MoveSelfReport,
  MoveStatus,
  ChannelType,
  MoveGoal,
  MoveDuration,
} from './campaigns-types';
import { apiFetch, getAuthHeaders } from './backend';
import { createMoveFromProposal } from './api';
import foundationMetadata from './foundation_test.json';

const DEFAULT_GOAL: MoveGoal = 'distribution';
const DEFAULT_CHANNEL: ChannelType = 'linkedin';
const DEFAULT_DURATION = 7;
const DEFAULT_DAILY_EFFORT = 30;

function normalizeMoveGoal(raw?: string): MoveGoal {
  const value = (raw || '').toLowerCase();
  if (
    value === 'leads' ||
    value === 'calls' ||
    value === 'sales' ||
    value === 'proof' ||
    value === 'distribution' ||
    value === 'activation'
  ) {
    return value as MoveGoal;
  }
  return DEFAULT_GOAL;
}

function normalizeChannel(raw?: string): ChannelType {
  const value = (raw || '').toLowerCase();
  if (
    value === 'linkedin' ||
    value === 'email' ||
    value === 'instagram' ||
    value === 'whatsapp' ||
    value === 'cold_dms' ||
    value === 'partnerships' ||
    value === 'twitter'
  ) {
    return value as ChannelType;
  }
  return DEFAULT_CHANNEL;
}

function mapChecklist(raw: any[]): ChecklistItem[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((task) => ({
    id: task.id || crypto.randomUUID(),
    label: task.label || task.title || 'Untitled task',
    completed: Boolean(task.completed),
    group: task.group || 'setup',
    assetLink: task.assetLink,
    muse_prompt: task.muse_prompt,
    agent_id: task.agent_id,
  }));
}

function mapBackendCampaign(campaign: any): Campaign {
  return {
    id: campaign.id,
    name: campaign.title || campaign.name || 'Campaign',
    objective: (campaign.objective || 'launch') as CampaignObjective,
    status: campaign.status || 'draft',
    createdAt: campaign.created_at || new Date().toISOString(),
    startedAt: campaign.start_date || campaign.started_at,
    completedAt: campaign.end_date || campaign.completed_at,
    duration: 90,
    moveLength: 14,
    dailyEffort: 30,
    offer: 'other',
    channels: [],
    strategyArc: campaign.arc_data || campaign.strategy_arc || {},
    auditData: campaign.audit_data?.alignments || [],
    qualityScore: campaign.audit_data?.overall_score,
  } as Campaign;
}

function mapBackendMove(move: any): Move {
  const refinement = move.refinement_data || {};
  return {
    id: move.id,
    name: move.title || 'Move',
    description: move.description || '',
    goal: normalizeMoveGoal(refinement.goal),
    channel: normalizeChannel(refinement.channel || move.move_type),
    duration: refinement.duration || DEFAULT_DURATION,
    dailyEffort: refinement.daily_effort || DEFAULT_DAILY_EFFORT,
    status: (move.status || 'draft') as MoveStatus,
    createdAt: move.created_at || new Date().toISOString(),
    campaignId: move.campaign_id || undefined,
    campaignName: move.campaign_name || undefined,
    checklist: mapChecklist(move.checklist || []),
    assetIds: move.asset_ids || [],
    refinementData: refinement,
    toolRequirements: move.tool_requirements || [],
    confidence: move.confidence || undefined,
    rag: move.rag_status || undefined,
    ragReason: move.rag_reason || undefined,
    dailyMetrics: move.daily_metrics || [],
    startedAt: move.started_at || undefined,
    completedAt: move.completed_at || undefined,
    pausedAt: move.paused_at || undefined,
  } as Move;
}

// =====================================
// Campaign Operations
// =====================================

export async function getCampaigns(): Promise<Campaign[]> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>('/v1/campaigns', { headers });
  const campaigns = response?.data?.campaigns || [];
  return campaigns.map(mapBackendCampaign);
}

export async function createCampaign(campaign: Campaign): Promise<void> {
  const headers = await getAuthHeaders();
  await apiFetch('/v1/campaigns', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      title: campaign.name,
      objective: campaign.objective,
      status: campaign.status || 'draft',
      arc_data: campaign.strategyArc || {},
      phase_order: [],
      milestones: [],
      audit_data: {},
    }),
  });
}

export async function updateCampaign(campaign: Campaign): Promise<void> {
  const headers = await getAuthHeaders();
  await apiFetch(`/v1/campaigns/${campaign.id}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      title: campaign.name,
      objective: campaign.objective,
      status: campaign.status,
      arc_data: campaign.strategyArc || {},
    }),
  });
}

export async function deleteCampaign(campaignId: string): Promise<void> {
  const headers = await getAuthHeaders();
  await apiFetch(`/v1/campaigns/${campaignId}`, {
    method: 'DELETE',
    headers,
  });
}

export async function getCampaign(
  campaignId: string
): Promise<Campaign | undefined> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/campaigns/${campaignId}`, { headers });
  const campaign = response?.data?.campaign;
  return campaign ? mapBackendCampaign(campaign) : undefined;
}

// =====================================
// Move Operations
// =====================================

export async function getMoves(): Promise<Move[]> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>('/v1/moves', { headers });
  const moves = response?.data?.moves || [];
  return moves.map(mapBackendMove);
}

export async function getMovesByCampaign(campaignId: string): Promise<Move[]> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/moves?campaign_id=${campaignId}`, {
    headers,
  });
  const moves = response?.data?.moves || [];
  return moves.map(mapBackendMove);
}

export async function getUncategorizedMoves(): Promise<Move[]> {
  const moves = await getMoves();
  return moves.filter((move) => !move.campaignId);
}

export async function createMove(move: Move): Promise<void> {
  await createMoveFromProposal({
    ...move,
    refinementData: {
      ...(move.refinementData || {}),
      foundation_metadata: foundationMetadata,
    },
  });
}

export async function updateMove(move: Move): Promise<void> {
  const headers = await getAuthHeaders();
  await apiFetch(`/v1/moves/${move.id}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      title: move.name,
      description: move.description,
      status: move.status,
      confidence: move.confidence,
    }),
  });

  await updateMoveStatus(move.id, move.status, move.selfReport);
}

export async function deleteMove(_moveId: string): Promise<void> {
  return;
}

export async function getMove(moveId: string): Promise<Move | undefined> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/moves/${moveId}`, { headers });
  const move = response?.data?.move;
  return move ? mapBackendMove(move) : undefined;
}

export async function getActiveMove(): Promise<Move | null> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>('/v1/moves?status=active', { headers });
  const moves = response?.data?.moves || [];
  if (!moves.length) return null;
  return mapBackendMove(moves[0]);
}

export async function setActiveMove(moveId: string | null): Promise<void> {
  if (!moveId) return;
  const headers = await getAuthHeaders();
  await apiFetch(`/v1/moves/${moveId}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify({ status: 'active' }),
  });
}

// =====================================
// Helpers
// =====================================

export async function getCampaignProgress(campaignId: string) {
  const moves = await getMovesByCampaign(campaignId);
  const completedMoves = moves.filter((m) => m.status === 'completed').length;
  const totalWeeks = Math.ceil(90 / 7);

  return {
    totalMoves: moves.length,
    completedMoves,
    weekNumber: 1,
    totalWeeks,
  };
}

export function generateCampaignId(): string {
  return crypto.randomUUID();
}

export function generateMoveId(): string {
  return crypto.randomUUID();
}

export function generateChecklistItemId(): string {
  return crypto.randomUUID();
}

export function generateDefaultChecklist(
  _goal: MoveGoal,
  _channel: ChannelType,
  _duration: MoveDuration
): ChecklistItem[] {
  return [];
}

export async function triggerCampaignInference(
  campaignId: string
): Promise<Record<string, unknown> | null> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/campaigns/generate-arc/${campaignId}`, {
    method: 'POST',
    headers,
  });
  return response || null;
}

export async function getCampaignGantt(
  campaignId: string
): Promise<Record<string, unknown> | null> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/campaigns/${campaignId}/gantt`, {
    headers,
  });
  return response || null;
}

export async function applyCampaignPivot(
  campaignId: string,
  pivotData: Record<string, unknown>
): Promise<Record<string, unknown> | null> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/campaigns/${campaignId}/pivot`, {
    method: 'POST',
    headers,
    body: JSON.stringify(pivotData),
  });
  return response || null;
}

export async function generateWeeklyMoves(
  campaignId: string
): Promise<Record<string, unknown> | null> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/moves/generate-weekly/${campaignId}`, {
    method: 'POST',
    headers,
  });
  return response || null;
}

export async function getMovesStatus(
  campaignId: string
): Promise<Record<string, unknown> | null> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(
    `/v1/moves/generate-weekly/${campaignId}/status`,
    { headers }
  );
  return response || null;
}

export async function updateMoveStatus(
  moveId: string,
  status: string,
  result?: Record<string, unknown> | MoveSelfReport
): Promise<Record<string, unknown> | null> {
  const headers = await getAuthHeaders();
  const response = await apiFetch<any>(`/v1/moves/${moveId}/status`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ status, result }),
  });
  return response || null;
}

export async function toggleChecklistItem(
  moveId: string,
  itemId: string
): Promise<void> {
  const move = await getMove(moveId);
  if (!move) return;

  const updatedChecklist = move.checklist.map((item) =>
    item.id === itemId ? { ...item, completed: !item.completed } : item
  );

  const headers = await getAuthHeaders();
  const target = updatedChecklist.find((item) => item.id === itemId);
  if (!target) return;

  await apiFetch(`/v1/moves/${moveId}/tasks/${itemId}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify({ completed: target.completed }),
  });
}

export function isMoveOverdue(move: Move): boolean {
  if (!move.dueDate || move.status !== 'active') return false;
  return new Date(move.dueDate) < new Date();
}

export async function extendMove(_moveId: string, _days: number): Promise<void> {
  return;
}

export async function logMoveOverride(
  _move: Move,
  _campaign: Campaign,
  _reason: string
): Promise<void> {
  return;
}
