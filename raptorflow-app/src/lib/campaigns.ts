'use client';

/**
 * Campaigns & Moves — Persistence Layer
 * SOTA Supabase Integration
 */

import { supabase } from './supabase';
import {
    Campaign,
    Move,
    CampaignObjective,
    ChecklistItem,
    MoveGoal,
    ChannelType,
    MoveDuration,
    DBCampaign,
    DBMove,
    MoveStatus,
    CampaignStatus,
    MoveSelfReport,
    OverrideReason,
} from './campaigns-types';

// =====================================
// Campaign Operations
// =====================================

export async function getCampaigns(): Promise<Campaign[]> {
    const { data, error } = await supabase
        .from('campaigns')
        .select('*')
        .order('created_at', { ascending: false });

    if (error) {
        console.error('Error fetching campaigns:', error);
        return [];
    }

    return (data || []).map(mapDBCampaignToFrontend);
}

export async function createCampaign(campaign: Campaign): Promise<void> {
    const dbCampaign = mapFrontendCampaignToDB(campaign);
    const { error } = await supabase
        .from('campaigns')
        .insert(dbCampaign);

    if (error) {
        console.error('Error creating campaign:', error);
        throw error;
    }
}

export async function updateCampaign(campaign: Campaign): Promise<void> {
    const dbCampaign = mapFrontendCampaignToDB(campaign);
    const { error } = await supabase
        .from('campaigns')
        .update(dbCampaign)
        .eq('id', campaign.id);

    if (error) {
        console.error('Error updating campaign:', error);
        throw error;
    }
}

export async function deleteCampaign(campaignId: string): Promise<void> {
    const { error } = await supabase
        .from('campaigns')
        .delete()
        .eq('id', campaignId);

    if (error) {
        console.error('Error deleting campaign:', error);
        throw error;
    }
}

export async function getCampaign(campaignId: string): Promise<Campaign | undefined> {
    const { data, error } = await supabase
        .from('campaigns')
        .select('*')
        .eq('id', campaignId)
        .single();

    if (error) {
        console.error('Error fetching campaign:', error);
        return undefined;
    }

    return mapDBCampaignToFrontend(data);
}

// =====================================
// Move Operations
// =====================================

export async function getMoves(): Promise<Move[]> {
    const { data, error } = await supabase
        .from('moves')
        .select('*')
        .order('created_at', { ascending: false });

    if (error) {
        console.error('Error fetching moves:', error);
        return [];
    }

    return (data || []).map(mapDBMoveToFrontend);
}

export async function getMovesByCampaign(campaignId: string): Promise<Move[]> {
    const { data, error } = await supabase
        .from('moves')
        .select('*')
        .eq('campaign_id', campaignId)
        .order('created_at', { ascending: true });

    if (error) {
        console.error('Error fetching moves by campaign:', error);
        return [];
    }

    return (data || []).map(mapDBMoveToFrontend);
}

export async function createMove(move: Move): Promise<void> {
    const dbMove = mapFrontendMoveToDB(move);
    const { error } = await supabase
        .from('moves')
        .insert(dbMove);

    if (error) {
        console.error('Error creating move:', error);
        throw error;
    }
}

export async function updateMove(move: Move): Promise<void> {
    const dbMove = mapFrontendMoveToDB(move);
    const { error } = await supabase
        .from('moves')
        .update(dbMove)
        .eq('id', move.id);

    if (error) {
        console.error('Error updating move:', error);
        throw error;
    }

    // Task 31: Also notify backend about status change for agentic logic
    await updateMoveStatus(move.id, move.status, move.selfReport);
}

export async function deleteMove(moveId: string): Promise<void> {
    const { error } = await supabase
        .from('moves')
        .delete()
        .eq('id', moveId);

    if (error) {
        console.error('Error deleting move:', error);
        throw error;
    }
}

export async function getActiveMove(): Promise<Move | null> {
    const { data, error } = await supabase
        .from('moves')
        .select('*')
        .eq('status', 'active')
        .limit(1)
        .maybeSingle();

    if (error || !data) {
        return null;
    }

    return mapDBMoveToFrontend(data);
}

export async function setActiveMove(moveId: string | null): Promise<void> {
    // 1. Deactivate current active move
    await supabase
        .from('moves')
        .update({ status: 'queued' })
        .eq('status', 'active');

    // 2. Activate new move
    if (moveId) {
        await supabase
            .from('moves')
            .update({
                status: 'active',
                updated_at: new Date().toISOString()
            })
            .eq('id', moveId);
    }
}

// =====================================
// Mappings (Frontend <-> DB)
// =====================================

function mapDBCampaignToFrontend(db: DBCampaign): Campaign {
    return {
        id: db.id,
        name: db.title,
        objective: db.objective as CampaignObjective,
        status: db.status as CampaignStatus,
        createdAt: db.created_at,
        startedAt: db.start_date,
        duration: 90,
        moveLength: 14,
        dailyEffort: 30,
        offer: 'other',
        channels: [],
        strategyArc: db.arc_data,
        auditData: db.audit_data?.alignments || [],
        qualityScore: db.audit_data?.overall_score,
    };
}

function mapFrontendCampaignToDB(c: Campaign): Partial<DBCampaign> {
    return {
        id: c.id,
        tenant_id: '00000000-0000-0000-0000-000000000000',
        title: c.name,
        objective: c.objective,
        status: c.status,
        start_date: c.startedAt,
        end_date: c.completedAt,
    };
}

function mapDBMoveToFrontend(db: DBMove): Move {
    return {
        id: db.id,
        name: db.title,
        description: db.description,
        owner: db.priority === 1 ? 'AI Agent' : 'Founder',
        goal: (db as any).goal || 'distribution',
        channel: (db as any).channel || 'linkedin',
        duration: (db as any).duration || 7,
        dailyEffort: (db as any).daily_effort || 30,
        status: db.status as MoveStatus,
        createdAt: db.created_at,
        campaignId: db.campaign_id,
        checklist: (db as any).checklist || [],
        assetIds: (db as any).asset_ids || [],
        refinementData: db.refinement_data,
        toolRequirements: db.tool_requirements || [],
    };
}

function mapFrontendMoveToDB(m: Move): Partial<DBMove> {
    return {
        id: m.id,
        campaign_id: m.campaignId,
        title: m.name,
        description: m.outcomeTarget || '',
        status: m.status,
        priority: 1,
    };
}

// =====================================
// Helpers
// =====================================

export async function getCampaignProgress(campaignId: string) {
    const campaign = await getCampaign(campaignId);
    const moves = await getMovesByCampaign(campaignId);

    if (!campaign) return { totalMoves: 0, completedMoves: 0, weekNumber: 0, totalWeeks: 0 };

    const completedMoves = moves.filter(m => m.status === 'completed').length;
    const totalWeeks = Math.ceil(campaign.duration / 7);

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

export async function triggerCampaignInference(campaignId: string): Promise<Record<string, unknown> | null> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/v1/campaigns/generate-arc/${campaignId}`, {
        method: 'POST',
    });
    return response.ok ? await response.json() : null;
}

export async function getCampaignGantt(campaignId: string): Promise<Record<string, unknown> | null> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/v1/campaigns/${campaignId}/gantt`);
    return response.ok ? await response.json() : null;
}

export async function applyCampaignPivot(campaignId: string, pivotData: Record<string, unknown>): Promise<Record<string, unknown> | null> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/v1/campaigns/${campaignId}/pivot`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(pivotData),
    });
    return response.ok ? await response.json() : null;
}

export async function generateWeeklyMoves(campaignId: string): Promise<Record<string, unknown> | null> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/v1/moves/generate-weekly/${campaignId}`, {
        method: 'POST',
    });
    return response.ok ? await response.json() : null;
}

export async function getMovesStatus(campaignId: string): Promise<Record<string, unknown> | null> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/v1/moves/generate-weekly/${campaignId}/status`);
    return response.ok ? await response.json() : null;
}

export async function updateMoveStatus(moveId: string, status: string, result?: Record<string, unknown> | MoveSelfReport): Promise<Record<string, unknown> | null> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/v1/moves/${moveId}/status`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status, result }),
    });
    return response.ok ? await response.json() : null;
}

export async function toggleChecklistItem(moveId: string, itemId: string): Promise<void> {
    const { data: moveData } = await supabase
        .from('moves')
        .select('*')
        .eq('id', moveId)
        .single();

    if (!moveData) return;

    const move = mapDBMoveToFrontend(moveData);
    const updatedChecklist = move.checklist.map(item =>
        item.id === itemId ? { ...item, completed: !item.completed } : item
    );

    await updateMove({ ...move, checklist: updatedChecklist });
}

export function isMoveOverdue(move: Move): boolean {
    if (!move.dueDate || move.status !== 'active') return false;
    return new Date(move.dueDate) < new Date();
}

export async function extendMove(moveId: string, days: number): Promise<void> {
    const { data: moveData } = await supabase
        .from('moves')
        .select('*')
        .eq('id', moveId)
        .single();

    if (!moveData) return;

    // In a real app, this would update the due date in DB.
    // For now, we'll just log it.
}

export async function logMoveOverride(move: Move, campaign: Campaign, reason: OverrideReason): Promise<void> {
    // Audit log placeholder
}
