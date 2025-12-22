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
