import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { useEffect, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";

/**
 * Valid Foundation Section IDs
 */
export type FoundationSectionId =
  | "url"
  | "scan_results"
  | "business_stage"
  | "primary_product"
  | "customer_problem"
  | "icp"
  | "transformation"
  | "competitors"
  | "pricing_model"
  | "positioning"
  | "brand_personality"
  | "keywords"
  | "content_channels"
  | "content_history"
  | "primary_goal"
  | "budget"
  | "existing_assets"
  | "frustrations"
  | "analytics_tracking"
  | "reference_brands"
  | "strategist";

interface FoundationState {
  currentStep: number;
  completedSteps: number[];
  sectionData: Record<string, any>;
  scanData: any | null;
  isAutoSaving: boolean;

  // Actions
  setStep: (step: number) => void;
  setSectionData: (section: FoundationSectionId, data: any) => void;
  markStepComplete: (step: number) => void;
  setScanData: (data: any) => void;
  setIsAutoSaving: (status: boolean) => void;
  reset: () => void;
}

/**
 * useFoundationStore
 * Central state for the 21-screen onboarding.
 * Persists to localStorage to prevent data loss on refresh.
 */
export const useFoundationStore = create<FoundationState>()(
  persist(
    (set) => ({
      currentStep: 1,
      completedSteps: [],
      sectionData: {},
      scanData: null,
      isAutoSaving: false,

      setStep: (step) => set({ currentStep: step }),
      
      setSectionData: (section, data) => 
        set((state) => ({
          sectionData: {
            ...state.sectionData,
            [section]: data,
          },
        })),

      markStepComplete: (step) =>
        set((state) => ({
          completedSteps: state.completedSteps.includes(step)
            ? state.completedSteps
            : [...state.completedSteps, step],
        })),

      setScanData: (data) => set({ scanData: data }),
      
      setIsAutoSaving: (status) => set({ isAutoSaving: status }),

      reset: () => set({
        currentStep: 1,
        completedSteps: [],
        sectionData: {},
        scanData: null,
        isAutoSaving: false,
      }),
    }),
    {
      name: "raptorflow-foundation-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);

/**
 * useFoundationAutoSave
 * Custom hook to debounce and save section data to the backend.
 * Fires a PATCH to /api/v1/foundation/section/:sectionId
 */
export function useFoundationAutoSave(sectionId: FoundationSectionId, data: any) {
  const { getToken } = useAuth();
  const setIsAutoSaving = useFoundationStore((s) => s.setIsAutoSaving);

  const performSave = useCallback(async () => {
    if (!data) return;

    try {
      setIsAutoSaving(true);
      const token = await getToken();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/${sectionId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        console.error(`[FoundationAutoSave] Failed to save section ${sectionId}`);
      }
    } catch (err) {
      console.error(`[FoundationAutoSave] Error saving section ${sectionId}:`, err);
    } finally {
      setIsAutoSaving(false);
    }
  }, [sectionId, data, getToken, setIsAutoSaving]);

  useEffect(() => {
    // 800ms debounce
    const timeout = setTimeout(() => {
      performSave();
    }, 800);

    return () => clearTimeout(timeout);
  }, [performSave]);
}
