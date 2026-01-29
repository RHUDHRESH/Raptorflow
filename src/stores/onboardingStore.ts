"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { ONBOARDING_STEPS, type StepStatus, type StepState } from "@/lib/onboarding-tokens";
import { supabase } from "@/lib/supabaseClient";
import { useBcmStore } from "./bcmStore";

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
    hasHydrated: boolean;

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
    completeStep: (stepId: number) => Promise<void>;
    updateStep: (stepId: number, data: Record<string, unknown>) => Promise<void>;
    setHasHydrated: (hydrated: boolean) => void;

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
            hasHydrated: false,
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
                    hasHydrated: true,
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
                const { steps } = get();
                const previousStatus = steps.find((s) => s.id === stepId)?.status;

                set((state) => ({
                    steps: state.steps.map((s) =>
                        s.id === stepId ? { ...s, status } : s
                    ),
                }));

                if (status === "complete" && previousStatus !== "complete") {
                    void get().completeStep(stepId);
                }
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

                    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                    const response = await fetch(`${apiUrl}/api/v1/onboarding/${session.sessionId}/steps/${stepId}`, {
                        method: "POST",
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

            completeStep: async (stepId: number) => {
                set({ saveStatus: "saving" });
                try {
                    const { session } = get();
                    if (!session?.sessionId) {
                        set({ saveStatus: "saved", lastSyncedAt: new Date() });
                        return;
                    }

                    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                    const response = await fetch(
                        `${apiUrl}/api/v1/onboarding/${session.sessionId}/steps/${stepId}/complete`,
                        {
                            method: "POST",
                        }
                    );

                    if (!response.ok) {
                        throw new Error(`Backend sync failed: ${response.statusText}`);
                    }

                    await useBcmStore.getState().rebuild(session.sessionId);

                    set({ saveStatus: "saved", lastSyncedAt: new Date() });
                } catch (error) {
                    console.error("Failed to sync step to backend:", error);
                    set({ saveStatus: "error" });
                }
            },

            updateStep: async (stepId: number, data: Record<string, unknown>) => {
                set({ saveStatus: "saving" });
                try {
                    const { session } = get();
                    if (!session?.sessionId) {
                        set({ saveStatus: "saved", lastSyncedAt: new Date() });
                        return;
                    }

                    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                    const response = await fetch(`${apiUrl}/api/v1/onboarding/${session.sessionId}/steps/${stepId}`, {
                        method: "PATCH",
                        body: JSON.stringify(data),
                        headers: { "Content-Type": "application/json" },
                    });

                    if (!response.ok) {
                        throw new Error(`Backend sync failed: ${response.statusText}`);
                    }

                    await useBcmStore.getState().rebuild(session.sessionId);

                    set({ saveStatus: "saved", lastSyncedAt: new Date() });
                } catch (error) {
                    console.error("Failed to sync step to backend:", error);
                    set({ saveStatus: "error" });
                }
            },

            setSaveStatus: (status) => set({ saveStatus: status }),

            setHasHydrated: (hydrated) => set({ hasHydrated: hydrated }),

            // Computed
            getStepById: (stepId) => get().steps.find((s) => s.id === stepId),

            canProceedToStep: (stepId) => {
                const { steps, currentStep } = get();
                const stepConfig = ONBOARDING_STEPS.find((s) => s.id === stepId);
                if (!stepConfig) return false;

                // Can always go back to previous steps
                if (stepId < currentStep) return true;

                // Current step - always allowed
                if (stepId === currentStep) return true;

                // Forward navigation requires all previous required steps to be complete
                const previousRequiredSteps = ONBOARDING_STEPS.filter((s) => s.id < stepId && s.required);
                const allRequiredComplete = previousRequiredSteps.every((ps) => {
                    const stepState = steps.find((s) => s.id === ps.id);
                    return stepState?.status === "complete";
                });

                // If all required steps complete, allow forward navigation
                if (allRequiredComplete) return true;

                // For non-required steps, allow if all prior required steps are complete
                if (!stepConfig.required) {
                    const priorRequired = ONBOARDING_STEPS.filter((s) => s.id < stepId && s.required);
                    return priorRequired.every((ps) => {
                        const stepState = steps.find((s) => s.id === ps.id);
                        return stepState?.status === "complete";
                    });
                }

                return false;
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
            onRehydrateStorage: () => (state) => {
                state?.setHasHydrated(true);
            },
        }
    )
);
