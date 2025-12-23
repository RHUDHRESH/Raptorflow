'use client';

import {
    BlackboxState,
    Experiment,
    LearningArtifact
} from './blackbox-types';

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
// Helper CRUD Operations
// =====================================

export function addExperiment(experiment: Experiment): void {
    const state = loadBlackboxState();
    state.experiments = [experiment, ...state.experiments];
    saveBlackboxState(state);
}

export function updateExperiment(experiment: Experiment): void {
    const state = loadBlackboxState();
    state.experiments = state.experiments.map(e => e.id === experiment.id ? experiment : e);
    saveBlackboxState(state);
}

export function getExperiments(): Experiment[] {
    return loadBlackboxState().experiments;
}

export function addLearning(learning: LearningArtifact): void {
    const state = loadBlackboxState();
    state.learnings = [learning, ...state.learnings];

    // Also apply skill weight updates
    learning.skill_weight_deltas.forEach(delta => {
        const current = state.skill_weights[delta.skill_id] || 0.5;
        state.skill_weights[delta.skill_id] = Math.max(0, Math.min(1, current + delta.delta));
    });

    saveBlackboxState(state);
}

export function getLearnings(): LearningArtifact[] {
    return loadBlackboxState().learnings;
}

export function getSkillWeights(): Record<string, number> {
    return loadBlackboxState().skill_weights;
}

// =====================================
// Backend Integration (Supabase)
// =====================================
import { supabase } from './supabase';

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
