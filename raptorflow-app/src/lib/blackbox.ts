'use client';

import {
    BlackboxState,
    Experiment,

    LearningArtifact
} from './blackbox-types';
import { supabase } from './supabase';

/**
 * Black Box Z — Persistence Layer (localStorage)
 */

const STORAGE_KEY = 'raptorflow_blackbox';

const defaultState: BlackboxState = {
    experiments: [],
    learnings: [],
    skill_weights: {},
};

export function saveBlackboxState(state: BlackboxState): void {
    if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }
}

export function loadBlackboxState(): BlackboxState {
    if (typeof window !== 'undefined') {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                return JSON.parse(stored) as BlackboxState;
            } catch (e) {
                console.error('Failed to load Black Box state', e);
                return defaultState;
            }
        }
    }
    return defaultState;
}

export function clearBlackboxState(): void {
    if (typeof window !== 'undefined') {
        localStorage.removeItem(STORAGE_KEY);
    }
}

// =====================================
// Experiment CRUD (Supabase)
// =====================================

async function getTenantId(): Promise<string> {
    try {
        const { data: { user } } = await supabase.auth.getUser();
        return user?.id || '00000000-0000-0000-0000-000000000000';
    } catch {
        return '00000000-0000-0000-0000-000000000000';
    }
}

export async function getExperimentsDB(): Promise<Experiment[]> {
    const tenantId = await getTenantId();
    const { data, error } = await supabase
        .from('experiments')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('created_at', { ascending: false });


    if (error) {
        console.error('Error fetching experiments:', error);
        return [];
    }

    return data ? data.map(mapDBExperimentToFrontend) : [];
}
export async function createExperimentDB(experiment: Experiment): Promise<void> {
    const tenantId = await getTenantId();
    const dbExp = { ...mapFrontendExperimentToDB(experiment), tenant_id: tenantId };
    const { error } = await supabase
        .from('experiments')
        .insert(dbExp);


    if (error) {
        console.error('Error creating experiment:', error);
        throw error;
    }
}

export async function updateExperimentDB(experiment: Experiment): Promise<void> {
    const dbExp = mapFrontendExperimentToDB(experiment);
    const { error } = await supabase
        .from('experiments')
        .update(dbExp)
        .eq('id', experiment.id);

    if (error) {
        console.error('Error updating experiment:', error);
        throw error;
    }
}

export async function deleteExperimentDB(id: string): Promise<void> {
    const { error } = await supabase
        .from('experiments')
        .delete()
        .eq('id', id);

    if (error) {
        console.error('Error deleting experiment:', error);
        throw error;
    }
}

function mapDBExperimentToFrontend(db: any): Experiment {
    return {
        id: db.id,
        goal: db.goal,
        risk_level: db.risk_level,
        channel: db.channel,
        title: db.title,
        bet: db.bet,
        why: db.why || '',
        principle: db.principle,

        // Actionable details
        hypothesis: db.hypothesis || '',
        control: db.control || '',
        variant: db.variant || '',
        success_metric: db.success_metric || '',
        sample_size: db.sample_size || 'N/A',
        duration_days: db.duration_days || 7,
        action_steps: db.action_steps || [],

        effort: db.effort || '30m',
        time_to_signal: db.time_to_signal || '48h',
        skill_stack: db.skill_stack || [],
        asset_ids: db.asset_ids || [],
        status: db.status,
        created_at: db.created_at,
        launched_at: db.launched_at,
        self_report: db.self_report
    };
}

function mapFrontendExperimentToDB(e: Experiment): any {
    return {
        id: e.id,
        goal: e.goal,
        risk_level: e.risk_level,
        channel: e.channel,
        title: e.title,
        bet: e.bet,
        why: e.why,
        principle: e.principle,

        hypothesis: e.hypothesis,
        control: e.control,
        variant: e.variant,
        success_metric: e.success_metric,
        sample_size: e.sample_size,
        duration_days: e.duration_days,
        action_steps: e.action_steps,

        effort: e.effort,
        time_to_signal: e.time_to_signal,
        status: e.status,
        launched_at: e.launched_at,
        self_report: e.self_report,
        asset_ids: e.asset_ids,
        skill_stack: e.skill_stack
    };
}

// =====================================
// Backend Persistence (Supabase)
// =====================================


export async function saveOutcome(outcome: {
    source: string,
    value: number,
    confidence: number,
    campaign_id?: string,
    move_id?: string
}) {
    const { error } = await supabase
        .from('blackbox_outcomes_industrial')
        .insert(outcome);

    if (error) {
        console.error('Error saving outcome:', error);
        throw error;
    }
}

export async function saveLearning(learning: {
    content: string,
    learning_type: 'tactical' | 'strategic' | 'content',
    source_ids?: string[]
}) {
    const { error } = await supabase
        .from('blackbox_learnings_industrial')
        .insert(learning);

    if (error) {
        console.error('Error saving learning:', error);
        throw error;
    }
}

export async function getOutcomesByCampaign(campaignId: string) {
    const { data, error } = await supabase
        .from('blackbox_outcomes_industrial')
        .select('*')
        .eq('campaign_id', campaignId)
        .order('timestamp', { ascending: false });

    if (error) {
        console.error('Error fetching outcomes for campaign:', error);
        return [];
    }
    return data;
}

export async function getOutcomesByMove(moveId: string) {
    const { data, error } = await supabase
        .from('blackbox_outcomes_industrial')
        .select('*')
        .eq('move_id', moveId)
        .order('timestamp', { ascending: false });

    if (error) {
        console.error('Error fetching outcomes for move:', error);
        return [];
    }
    return data;
}

export async function getEvidencePackage(learningId: string) {
    // 1. Fetch learning to get source_ids
    const { data: learning, error: lError } = await supabase
        .from('blackbox_learnings_industrial')
        .select('source_ids')
        .eq('id', learningId)
        .single();

    if (lError || !learning?.source_ids) {
        console.error('Error fetching learning source IDs:', lError);
        return [];
    }

    // 2. Fetch all telemetry for these IDs
    const { data, error } = await supabase
        .from('blackbox_telemetry_industrial')
        .select('*')
        .in('id', learning.source_ids);

    if (error) {
        console.error('Error fetching evidence package:', error);
        return [];
    }
    return data;
}

export async function getTelemetryByMove(moveId: string) {
    const { data, error } = await supabase
        .from('blackbox_telemetry_industrial')
        .select('*')
        .eq('move_id', moveId)
        .order('timestamp', { ascending: false });

    if (error) {
        console.error('Error fetching telemetry for move:', error);
        return [];
    }
    return data;
}

export async function getLearningsByMove(moveId: string) {
    const { data, error } = await supabase
        .from('blackbox_learnings_industrial')
        .select('*')
        .contains('source_ids', [moveId]);

    if (error) {
        console.error('Error fetching learnings for move:', error);
        return [];
    }
    return data;
}

// =====================================
// Agentic Triggers (API)
// =====================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getLearningFeed(limit: number = 10) {
    // Always return mock data for now - backend is not running
    console.log('Returning mock learning feed data');
    return getMockLearningFeed();

    // Original API call code (commented out until backend is available)
    /*
    // Check if we're in a browser environment
    if (typeof window === 'undefined') {
        console.warn('getLearningFeed called in server environment, returning mock data');
        return getMockLearningFeed();
    }

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        const response = await fetch(`${API_URL}/v1/blackbox/learning/feed?limit=${limit}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            // If server is not available, return mock data
            if (response.status === 0 || response.type === 'error') {
                console.warn('Backend server not available, returning mock data');
                return getMockLearningFeed();
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (err) {
        console.error('Error fetching learning feed:', err);
        // Return mock data as fallback
        return getMockLearningFeed();
    }
    */
}

// Mock data fallback
function getMockLearningFeed() {
    return [
        {
            id: '1',
            title: 'Understanding Customer Churn Patterns',
            content: 'Recent analysis shows that customers who engage with onboarding materials are 3x more likely to stay...',
            timestamp: new Date().toISOString(),
            category: 'retention',
            priority: 'high'
        },
        {
            id: '2',
            title: 'Optimal Pricing Strategy for SaaS',
            content: 'Based on market analysis, tiered pricing with a free trial increases conversion rates by 25%...',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            category: 'pricing',
            priority: 'medium'
        },
        {
            id: '3',
            title: 'Feature Adoption Best Practices',
            content: 'Features introduced with interactive tutorials see 40% higher adoption rates...',
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            category: 'product',
            priority: 'low'
        }
    ];
}

export async function triggerLearningCycle(moveId: string) {
    try {
        const response = await fetch(`${API_URL}/v1/blackbox/learning/cycle/${moveId}`, {
            method: 'POST'
        });
        return await response.json();
    } catch (err) {
        console.error('Failed to trigger learning cycle:', err);
        return { status: 'error', message: String(err) };
    }
}

export async function runSpecialistAgent(agentId: string, moveId: string, stateOverride?: any) {
    try {
        const response = await fetch(`${API_URL}/v1/blackbox/specialist/run/${agentId}/${moveId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(stateOverride || {})
        });
        return await response.json();
    } catch (err) {
        console.error('Failed to run specialist agent:', err);
        return { status: 'error', message: String(err) };
    }
}
