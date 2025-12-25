"use client";

import { toast } from "sonner";

interface GrowthState {
    experiment_streak: number;
    moves_completed: number;
    last_action_at: string | null;
    total_impact_score: number;
}

const STORAGE_KEY = 'raptorflow_growth_engine';

const defaultState: GrowthState = {
    experiment_streak: 0,
    moves_completed: 0,
    last_action_at: null,
    total_impact_score: 0
};

function getGrowthState(): GrowthState {
    if (typeof window === 'undefined') return defaultState;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : defaultState;
}

function saveGrowthState(state: GrowthState) {
    if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }
}

export const GrowthHooks = {
    trackExperimentCompletion: (impactScore: number = 5) => {
        const state = getGrowthState();
        const now = new Date();

        // Update streak logic (simplified)
        state.experiment_streak += 1;
        state.total_impact_score += impactScore;
        state.last_action_at = now.toISOString();

        saveGrowthState(state);

        // Variable Reward: Milestone Toasts
        if (state.experiment_streak === 1) {
            toast.success("First Experiment Logged!", {
                description: "You've officially started your growth flywheel. +10 Momentum."
            });
        } else if (state.experiment_streak % 3 === 0) {
            toast.success(`${state.experiment_streak} Experiment Streak!`, {
                description: "Consistency is the founder's superpower. Your learning confidence increased."
            });
        } else {
            toast("Experiment Secured", {
                description: "Evidence logged to Black Box. +5 Momentum."
            });
        }
    },

    trackMoveCompletion: () => {
        const state = getGrowthState();
        state.moves_completed += 1;
        saveGrowthState(state);

        // Variable Reward
        const rewards = [
            "Nice work! Your strategic arc is 5% closer to completion.",
            "Move executed. The engine is refining its next recommendation.",
            "Momentum building. Your execution velocity is in the top 10%.",
            "Surgical execution. ROI data will be available in 48h."
        ];
        const randomReward = rewards[Math.floor(Math.random() * rewards.length)];

        toast.success("Move Complete", {
            description: randomReward
        });
    },

    getStreak: () => getGrowthState().experiment_streak,
    getImpact: () => getGrowthState().total_impact_score
};
