"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { ONBOARDING_STEPS, type StepStatus, type StepState } from "@/lib/onboarding-tokens";
import { supabase } from "@/lib/supabaseClient";

// --- Types ---
export interface OnboardingSession {
    sessionId: string;
    clientName: string;
    createdAt: Date;
    updatedAt: Date;
}

export interface OnboardingState {
    // Session
    session: OnboardingSession | null;
    currentStep: number;

    // Steps
    steps: StepState[];

    // Save status
    saveStatus: "idle" | "saving" | "saved" | "error";
    lastSyncedAt: Date | null;

    // Actions
    initSession: (sessionId: string, clientName?: string) => void;
    setCurrentStep: (stepId: number) => void;
    updateStepStatus: (stepId: number, status: StepStatus) => void;
    updateStepData: (stepId: number, data: Record<string, unknown>) => void;
    setSaveStatus: (status: "idle" | "saving" | "saved" | "error") => void;

    // Computed
    getStepById: (stepId: number) => StepState | undefined;
    canProceedToStep: (stepId: number) => boolean;
    getProgress: () => { completed: number; total: number; percentage: number };
}

// --- Initial Steps ---
const createInitialSteps = (): StepState[] =>
    ONBOARDING_STEPS.map((step) => ({
        id: step.id,
        status: step.id === 1 ? "in-progress" : "pending",
        data: {},
        savedAt: null,
    }));

// --- Store ---
export const useOnboardingStore = create<OnboardingState>()(
    persist(
        (set, get) => ({
            // Initial state
            session: null,
            currentStep: 1,
            steps: createInitialSteps(),
            saveStatus: "idle",
            lastSyncedAt: null,

            // Actions
            initSession: (sessionId, clientName = "New Client") => {
                set({
                    session: {
                        sessionId,
                        clientName,
                        createdAt: new Date(),
                        updatedAt: new Date(),
                    },
                    currentStep: 1,
                    steps: createInitialSteps(),
                    saveStatus: "idle",
                    lastSyncedAt: null,
                });
            },

            setCurrentStep: (stepId) => {
                const { steps } = get();
                const step = steps.find((s) => s.id === stepId);
                if (!step) return;

                // Mark current step as in-progress
                set({
                    currentStep: stepId,
                    steps: steps.map((s) =>
                        s.id === stepId && s.status === "pending"
                            ? { ...s, status: "in-progress" as StepStatus }
                            : s
                    ),
                });
            },

            updateStepStatus: (stepId, status) => {
                set((state) => ({
                    steps: state.steps.map((s) =>
                        s.id === stepId ? { ...s, status } : s
                    ),
                }));
            },

            updateStepData: async (stepId, data) => {
                const { session } = get();

                // 1. Optimistic Update
                set((state) => ({
                    steps: state.steps.map((s) =>
                        s.id === stepId
                            ? { ...s, data: { ...s.data, ...data }, savedAt: new Date() }
                            : s
                    ),
                    saveStatus: "saving",
                }));


                // 2. Sync to Backend
                if (!session?.sessionId) {
                    // No session yet (or local demo), just finish
                    set({ saveStatus: "saved", lastSyncedAt: new Date() });
                    return;
                }

                try {
                    // Get real auth token
                    const { data: authData } = await supabase.auth.getSession();
                    const token = authData.session?.access_token;

                    const headers: Record<string, string> = {
                        "Content-Type": "application/json",
                    };

                    if (token) {
                        headers["Authorization"] = `Bearer ${token}`;
                    }

                    const response = await fetch(`http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/${stepId}`, {
                        method: "PATCH",
                        headers,
                        body: JSON.stringify({
                            data: { ...get().steps.find(s => s.id === stepId)?.data, ...data }, // Merge with existing to be safe
                            version: 1 // Simple versioning for now
                        }),
                    });

                    if (!response.ok) {
                        throw new Error(`Backend sync failed: ${response.statusText}`);
                    }

                    // Success
                    set({ saveStatus: "saved", lastSyncedAt: new Date() });
                } catch (error) {
                    console.error("Failed to sync step to backend:", error);
                    set({ saveStatus: "error" });
                }
            },

            setSaveStatus: (status) => set({ saveStatus: status }),

            // Computed
            getStepById: (stepId) => get().steps.find((s) => s.id === stepId),

            canProceedToStep: (stepId) => {
                const { steps, currentStep } = get();
                const stepConfig = ONBOARDING_STEPS.find((s) => s.id === stepId);
                if (!stepConfig) return false;

                // Can always go back
                if (stepId < currentStep) return true;

                // Going to next step (stepId = currentStep + 1)
                if (stepId === currentStep + 1) {
                    const currentStepState = steps.find((s) => s.id === currentStep);
                    const currentStepConfig = ONBOARDING_STEPS.find((s) => s.id === currentStep);

                    // If current step is complete, can proceed
                    if (currentStepState?.status === "complete") return true;

                    // If current step is not required, can skip
                    if (!currentStepConfig?.required) return true;

                    // If current step has any data, allow proceed (user engaged)
                    if (currentStepState?.data && Object.keys(currentStepState.data).length > 0) return true;
                }

                // For jumps of more than 1 step, check required previous steps
                const previousRequiredSteps = ONBOARDING_STEPS.filter((s) => s.id < stepId && s.required);
                return previousRequiredSteps.every((ps) => {
                    const stepState = steps.find((s) => s.id === ps.id);
                    return stepState?.status === "complete";
                });
            },

            getProgress: () => {
                const { steps } = get();
                const completed = steps.filter((s) => s.status === "complete").length;
                const total = steps.length;
                return { completed, total, percentage: Math.round((completed / total) * 100) };
            },
        }),
        {
            name: "raptorflow-onboarding",
        }
    )
);
