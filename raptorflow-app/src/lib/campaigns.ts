'use client';

/**
 * Campaigns & Moves — Persistence Layer
 * API-ready repository with localStorage backing
 */

import {
    Campaign,
    Move,
    CampaignsState,
    OverrideReason,
    CampaignObjective,
    ChecklistItem,
    MoveGoal,
    ChannelType,
    MoveDuration,
} from './campaigns-types';

// =====================================
// Storage Keys
// =====================================

const STORAGE_KEY = 'raptorflow_campaigns';

// =====================================
// Default State
// =====================================

const emptyState: CampaignsState = {
    campaigns: [],
    moves: [],
    activeMoveId: null,
};

// =====================================
// Core CRUD Operations
// =====================================

export function loadCampaignsState(): CampaignsState {
    if (typeof window !== 'undefined') {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                return JSON.parse(stored) as CampaignsState;
            } catch {
                return emptyState;
            }
        }
    }
    return emptyState;
}

export function saveCampaignsState(state: CampaignsState): void {
    if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }
}

export function clearCampaignsState(): void {
    if (typeof window !== 'undefined') {
        localStorage.removeItem(STORAGE_KEY);
    }
}

// =====================================
// Campaign Operations
// =====================================

export function createCampaign(campaign: Campaign): void {
    const state = loadCampaignsState();
    state.campaigns = [campaign, ...state.campaigns];
    saveCampaignsState(state);
}

export function updateCampaign(campaign: Campaign): void {
    const state = loadCampaignsState();
    state.campaigns = state.campaigns.map(c =>
        c.id === campaign.id ? campaign : c
    );
    saveCampaignsState(state);
}

export function deleteCampaign(campaignId: string): void {
    const state = loadCampaignsState();
    state.campaigns = state.campaigns.filter(c => c.id !== campaignId);
    // Also delete associated moves
    state.moves = state.moves.filter(m => m.campaignId !== campaignId);
    saveCampaignsState(state);
}

export function getCampaign(campaignId: string): Campaign | undefined {
    const state = loadCampaignsState();
    return state.campaigns.find(c => c.id === campaignId);
}

export function getCampaigns(): Campaign[] {
    return loadCampaignsState().campaigns;
}

// =====================================
// Move Operations
// =====================================

export function createMove(move: Move): void {
    const state = loadCampaignsState();
    state.moves = [move, ...state.moves];
    saveCampaignsState(state);
}

export function updateMove(move: Move): void {
    const state = loadCampaignsState();
    state.moves = state.moves.map(m =>
        m.id === move.id ? move : m
    );
    // Update active move ID if this move is now active
    if (move.status === 'active') {
        state.activeMoveId = move.id;
    } else if (state.activeMoveId === move.id && move.status !== 'active') {
        state.activeMoveId = null;
    }
    saveCampaignsState(state);
}

export function deleteMove(moveId: string): void {
    const state = loadCampaignsState();
    state.moves = state.moves.filter(m => m.id !== moveId);
    if (state.activeMoveId === moveId) {
        state.activeMoveId = null;
    }
    saveCampaignsState(state);
}

export function getMove(moveId: string): Move | undefined {
    const state = loadCampaignsState();
    return state.moves.find(m => m.id === moveId);
}

export function getMoves(): Move[] {
    return loadCampaignsState().moves;
}

export function getMovesByCampaign(campaignId: string): Move[] {
    const state = loadCampaignsState();
    return state.moves.filter(m => m.campaignId === campaignId);
}

export function getActiveMove(): Move | null {
    const state = loadCampaignsState();
    if (!state.activeMoveId) return null;
    return state.moves.find(m => m.id === state.activeMoveId) || null;
}

export function setActiveMove(moveId: string | null): void {
    const state = loadCampaignsState();
    // Deactivate current active move if exists
    if (state.activeMoveId && state.activeMoveId !== moveId) {
        state.moves = state.moves.map(m =>
            m.id === state.activeMoveId
                ? { ...m, status: 'queued' as const }
                : m
        );
    }
    // Activate new move
    if (moveId) {
        state.moves = state.moves.map(m =>
            m.id === moveId
                ? { ...m, status: 'active' as const, startedAt: m.startedAt || new Date().toISOString() }
                : m
        );
    }
    state.activeMoveId = moveId;
    saveCampaignsState(state);
}

// =====================================
// Move Checklist Operations
// =====================================

export function toggleChecklistItem(moveId: string, itemId: string): void {
    const state = loadCampaignsState();
    state.moves = state.moves.map(move => {
        if (move.id !== moveId) return move;
        return {
            ...move,
            checklist: move.checklist.map(item =>
                item.id === itemId
                    ? { ...item, completed: !item.completed }
                    : item
            ),
        };
    });
    saveCampaignsState(state);
}

// =====================================
// Move Due Date Helpers
// =====================================

export function isMoveOverdue(move: Move): boolean {
    if (!move.dueDate || move.status !== 'active') return false;
    return new Date(move.dueDate) < new Date();
}

export function extendMove(moveId: string, days: number = 3): void {
    const state = loadCampaignsState();
    state.moves = state.moves.map(move => {
        if (move.id !== moveId) return move;
        const currentDue = move.dueDate ? new Date(move.dueDate) : new Date();
        currentDue.setDate(currentDue.getDate() + days);
        return { ...move, dueDate: currentDue.toISOString() };
    });
    saveCampaignsState(state);
}

// =====================================
// Override Logging (connects to Blackbox)
// =====================================

export interface MoveOverrideLog {
    moveId: string;
    moveName: string;
    campaignId: string;
    campaignName: string;
    originalObjective: CampaignObjective;
    moveGoal: MoveGoal;
    reason: OverrideReason;
    loggedAt: string;
}

const OVERRIDE_LOG_KEY = 'raptorflow_move_overrides';

export function logMoveOverride(
    move: Move,
    campaign: Campaign,
    reason: OverrideReason
): void {
    if (typeof window === 'undefined') return;

    const log: MoveOverrideLog = {
        moveId: move.id,
        moveName: move.name,
        campaignId: campaign.id,
        campaignName: campaign.name,
        originalObjective: campaign.objective,
        moveGoal: move.goal,
        reason,
        loggedAt: new Date().toISOString(),
    };

    const existing = localStorage.getItem(OVERRIDE_LOG_KEY);
    const logs: MoveOverrideLog[] = existing ? JSON.parse(existing) : [];
    logs.unshift(log);
    localStorage.setItem(OVERRIDE_LOG_KEY, JSON.stringify(logs));
}

export function getOverrideLogs(): MoveOverrideLog[] {
    if (typeof window === 'undefined') return [];
    const existing = localStorage.getItem(OVERRIDE_LOG_KEY);
    return existing ? JSON.parse(existing) : [];
}

// =====================================
// ID Generation
// =====================================

export function generateCampaignId(): string {
    return `camp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function generateMoveId(): string {
    return `move-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function generateChecklistItemId(): string {
    return `check-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// =====================================
// Default Checklist Generator
// =====================================

export function generateDefaultChecklist(
    goal: MoveGoal,
    channel: ChannelType,
    duration: MoveDuration
): ChecklistItem[] {
    const items: ChecklistItem[] = [];

    // Setup tasks
    items.push({
        id: generateChecklistItemId(),
        label: 'Review campaign context and objectives',
        completed: false,
        group: 'setup',
    });

    if (channel === 'linkedin' || channel === 'cold_dms') {
        items.push({
            id: generateChecklistItemId(),
            label: 'Identify target list (20-50 prospects)',
            completed: false,
            group: 'setup',
        });
    }

    // Create tasks based on goal
    if (goal === 'leads' || goal === 'calls') {
        items.push({
            id: generateChecklistItemId(),
            label: 'Draft outreach script',
            completed: false,
            group: 'create',
        });
        items.push({
            id: generateChecklistItemId(),
            label: 'Create follow-up sequence',
            completed: false,
            group: 'create',
        });
    }

    if (goal === 'distribution') {
        items.push({
            id: generateChecklistItemId(),
            label: 'Create 3-5 content pieces',
            completed: false,
            group: 'create',
        });
    }

    if (goal === 'proof') {
        items.push({
            id: generateChecklistItemId(),
            label: 'Identify 3 customers to contact',
            completed: false,
            group: 'create',
        });
        items.push({
            id: generateChecklistItemId(),
            label: 'Draft testimonial request template',
            completed: false,
            group: 'create',
        });
    }

    // Publish tasks
    if (channel === 'linkedin') {
        items.push({
            id: generateChecklistItemId(),
            label: `Post ${duration === 7 ? '3' : duration === 14 ? '5' : '10'} times`,
            completed: false,
            group: 'publish',
        });
    }

    if (channel === 'email') {
        items.push({
            id: generateChecklistItemId(),
            label: 'Send first batch of emails',
            completed: false,
            group: 'publish',
        });
    }

    if (channel === 'cold_dms') {
        items.push({
            id: generateChecklistItemId(),
            label: 'Send 20 DMs per day',
            completed: false,
            group: 'publish',
        });
    }

    // Follow-up tasks
    items.push({
        id: generateChecklistItemId(),
        label: 'Track responses and engagement',
        completed: false,
        group: 'followup',
    });
    items.push({
        id: generateChecklistItemId(),
        label: 'Follow up with warm leads',
        completed: false,
        group: 'followup',
    });

    return items;
}

// =====================================
// Campaign Progress Helpers
// =====================================

export function getCampaignProgress(campaignId: string): {
    totalMoves: number;
    completedMoves: number;
    weekNumber: number;
    totalWeeks: number;
} {
    const campaign = getCampaign(campaignId);
    const moves = getMovesByCampaign(campaignId);

    if (!campaign) {
        return { totalMoves: 0, completedMoves: 0, weekNumber: 0, totalWeeks: 0 };
    }

    const completedMoves = moves.filter(m =>
        m.status === 'completed' || m.status === 'abandoned'
    ).length;

    const totalWeeks = Math.ceil(campaign.duration / 7);
    const startDate = campaign.startedAt ? new Date(campaign.startedAt) : new Date();
    const now = new Date();
    const weekNumber = Math.min(
        Math.ceil((now.getTime() - startDate.getTime()) / (7 * 24 * 60 * 60 * 1000)),
        totalWeeks
    );

    return {
        totalMoves: moves.length,
        completedMoves,
        weekNumber: Math.max(1, weekNumber),
        totalWeeks,
    };
}
