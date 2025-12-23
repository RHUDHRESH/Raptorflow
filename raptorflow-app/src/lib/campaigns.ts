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

function mapDBCampaignToFrontend(db: any): Campaign {
    return {
        id: db.id,
        name: db.title,
        objective: db.objective as CampaignObjective,
        status: db.status,
        createdAt: db.created_at,
        startedAt: db.start_date,
        duration: 90, 
        moveLength: 14,
        dailyEffort: 30,
        offer: 'other',
        channels: [],
    };
}

function mapFrontendCampaignToDB(c: Campaign): any {
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

function mapDBMoveToFrontend(db: any): Move {
    return {
        id: db.id,
        name: db.title,
        goal: 'distribution', 
        channel: 'linkedin', 
        duration: 7,
        dailyEffort: 30,
        status: db.status,
        createdAt: db.created_at,
        campaignId: db.campaign_id,
        checklist: [],
        assetIds: [],
    };
}

function mapFrontendMoveToDB(m: Move): any {
    return {
        id: m.id,
        campaign_id: m.campaignId,
        title: m.name,
        description: m.outcomeTarget,
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
    goal: MoveGoal,
    channel: ChannelType,
    duration: MoveDuration
): ChecklistItem[] {
    return []; 
}

export async function triggerCampaignInference(campaignId: string): Promise<any> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/v1/campaigns/generate-arc/${campaignId}`, {
        method: 'POST',
    });
    return response.ok ? await response.json() : null;
}