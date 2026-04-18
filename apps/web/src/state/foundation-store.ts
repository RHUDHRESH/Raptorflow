import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { useEffect, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";

/**
 * Valid Foundation Section IDs — 21 screens mapped to Rust model fields
 * 
 * Screen → Backend Field Mapping:
 *  1. url              → company_url
 *  2. company_info     → company_info (name, legal_name, year_founded, etc.)
 *  3. company_stage    → company_stage
 *  4. product_catalog  → product_catalog (products, pricing_model)
 *  5. problem_statement → problem_statement
 *  6. icp              → target_audience (primary ICP)
 *  7. secondary_icps   → secondary_icps (additional ICPs)
 *  8. competitors      → competitors (direct + indirect)
 *  9. differentiation  → differentiation (list of differentiators)
 * 10. positioning      → positioning (tagline, mission, UVP)
 * 11. brand_personality → brand_personality (traits, tone, archetype)
 * 12. voice_practice   → voice_practice (5 sliders, writing samples)
 * 13. content_territories → content_territories
 * 14. channels         → channels (primary + secondary)
 * 15. goals            → goals (primary_goal, kpis, budget)
 * 16. seo_keywords     → seo_keywords
 * 17. asset_inventory  → asset_inventory
 * 18. frustrations     → frustrations (pain points, analytics)
 * 19. tools            → tools (CRM, marketing, analytics, design)
 * 20. reference_brands → reference_brands
 * 21. strategist       → strategist (name + personality calibration)
 */
export type FoundationSectionId =
  | "url"
  | "scan_results"
  | "business_stage"
  | "primary_product"
  | "customer_problem"
  | "icp"
  | "transformation"
  | "pricing_model"
  | "keywords"
  | "content_channels"
  | "content_history"
  | "primary_goal"
  | "budget"
  | "existing_assets"
  | "analytics_tracking"
  | "company_url"
  | "company_info"
  | "company_stage"
  | "product_catalog"
  | "problem_statement"
  | "target_audience"
  | "secondary_icps"
  | "competitors"
  | "differentiation"
  | "positioning"
  | "brand_personality"
  | "voice_practice"
  | "content_territories"
  | "channels"
  | "goals"
  | "seo_keywords"
  | "asset_inventory"
  | "frustrations"
  | "tools"
  | "reference_brands"
  | "strategist";

// Legacy aliases for backwards compat with existing frontend code
export type LegacySectionId =
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

// Mapping from legacy IDs to new standardized IDs
export const LEGACY_SECTION_MAP: Record<LegacySectionId, FoundationSectionId> = {
  url: "company_url",
  scan_results: "company_url", // scan results populate company_url
  business_stage: "company_stage",
  primary_product: "product_catalog",
  customer_problem: "problem_statement",
  icp: "target_audience",
  transformation: "secondary_icps",
  competitors: "competitors",
  pricing_model: "product_catalog", // part of product_catalog
  positioning: "positioning",
  brand_personality: "brand_personality",
  keywords: "seo_keywords",
  content_channels: "channels",
  content_history: "channels", // part of channels
  primary_goal: "goals",
  budget: "goals", // part of goals
  existing_assets: "asset_inventory",
  frustrations: "frustrations",
  analytics_tracking: "frustrations", // part of frustrations
  reference_brands: "reference_brands",
  strategist: "strategist",
};

interface FoundationState {
  currentStep: number;
  totalSteps: number;
  completedSteps: number[];
  sectionData: Record<FoundationSectionId, any>;
  scanData: any | null;
  isAutoSaving: boolean;
  status: "initial" | "scanning" | "scanned" | "completing" | "ready" | "incomplete" | "complete";

  // Actions
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setStatus: (status: FoundationState["status"]) => void;
  setSectionData: (section: FoundationSectionId, data: any) => void;
  setSectionDataByLegacy: (legacySection: LegacySectionId, data: any) => void;
  markStepComplete: (step: number) => void;
  setScanData: (data: any) => void;
  setIsAutoSaving: (status: boolean) => void;
  getSectionData: (section: FoundationSectionId) => any;
  isStepComplete: (step: number) => boolean;
  getProgress: () => { completed: number; total: number; percentage: number };
  reset: () => void;
}

// All 21 screens in order
export const FOUNDATION_STEPS: { step: number; section: FoundationSectionId; label: string }[] = [
  { step: 1, section: "company_url", label: "Website" },
  { step: 2, section: "company_info", label: "Identity" },
  { step: 3, section: "company_stage", label: "Stage" },
  { step: 4, section: "product_catalog", label: "Products" },
  { step: 5, section: "problem_statement", label: "Problem" },
  { step: 6, section: "target_audience", label: "ICP" },
  { step: 7, section: "secondary_icps", label: "Secondary ICP" },
  { step: 8, section: "competitors", label: "Competitors" },
  { step: 9, section: "differentiation", label: "Differentiation" },
  { step: 10, section: "positioning", label: "Positioning" },
  { step: 11, section: "brand_personality", label: "Brand Personality" },
  { step: 12, section: "voice_practice", label: "Voice Practice" },
  { step: 13, section: "content_territories", label: "Content Territories" },
  { step: 14, section: "channels", label: "Channels" },
  { step: 15, section: "goals", label: "Goals & KPIs" },
  { step: 16, section: "seo_keywords", label: "Keywords / SEO" },
  { step: 17, section: "asset_inventory", label: "Assets" },
  { step: 18, section: "frustrations", label: "Frustrations" },
  { step: 19, section: "tools", label: "Tools" },
  { step: 20, section: "reference_brands", label: "Reference Brands" },
  { step: 21, section: "strategist", label: "Strategist" },
];

/**
 * useFoundationStore
 * Central state for the 21-screen onboarding.
 * Persists to localStorage to prevent data loss on refresh.
 */
export const useFoundationStore = create<FoundationState>()(
  persist(
    (set, get) => ({
      currentStep: 1,
      totalSteps: 21,
      completedSteps: [],
      sectionData: {} as Record<FoundationSectionId, any>,
      scanData: null,
      isAutoSaving: false,
      status: "initial",

      setStep: (step) => set({ currentStep: Math.max(1, Math.min(step, 21)) }),
      
      nextStep: () => set((state) => ({
        currentStep: Math.min(state.currentStep + 1, 21)
      })),
      
      prevStep: () => set((state) => ({
        currentStep: Math.max(state.currentStep - 1, 1)
      })),

      setStatus: (status) => set({ status }),

      setSectionData: (section, data) => set((state) => ({
        sectionData: {
          ...state.sectionData,
          [section]: {
            ...state.sectionData[section],
            ...data,
            _updatedAt: new Date().toISOString(),
          },
        },
      })),

      setSectionDataByLegacy: (legacySection, data) => {
        const section = LEGACY_SECTION_MAP[legacySection];
        get().setSectionData(section, data);
      },

      markStepComplete: (step) => set((state) => ({
        completedSteps: state.completedSteps.includes(step)
          ? state.completedSteps
          : [...state.completedSteps, step],
      })),

      setScanData: (data) => set({ scanData: data, status: "scanned" }),

      setIsAutoSaving: (status) => set({ isAutoSaving: status }),

      getSectionData: (section) => get().sectionData[section] ?? null,

      isStepComplete: (step) => get().completedSteps.includes(step),

      getProgress: () => {
        const state = get();
        const completed = state.completedSteps.length;
        const total = state.totalSteps;
        return {
          completed,
          total,
          percentage: Math.round((completed / total) * 100),
        };
      },

      reset: () => set({
        currentStep: 1,
        completedSteps: [],
        sectionData: {} as Record<FoundationSectionId, any>,
        scanData: null,
        isAutoSaving: false,
        status: "initial",
      }),
    }),
    {
      name: "raptorflow-foundation-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        currentStep: state.currentStep,
        completedSteps: state.completedSteps,
        sectionData: state.sectionData,
        status: state.status,
      }),
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
  const currentStep = useFoundationStore((s) => s.currentStep);
  const markStepComplete = useFoundationStore((s) => s.markStepComplete);

  const performSave = useCallback(async () => {
    if (!data) return;

    try {
      setIsAutoSaving(true);
      const token = await getToken();
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/${sectionId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ data }),
        }
      );

      if (!response.ok) {
        console.error(`[FoundationAutoSave] Failed to save section ${sectionId}`);
        return;
      }

      // Mark current step as complete on successful save
      const stepForSection = FOUNDATION_STEPS.find(s => s.section === sectionId)?.step;
      if (stepForSection) {
        markStepComplete(stepForSection);
      }
    } catch (err) {
      console.error(`[FoundationAutoSave] Error saving section ${sectionId}:`, err);
    } finally {
      setIsAutoSaving(false);
    }
  }, [sectionId, data, getToken, setIsAutoSaving, markStepComplete]);

  useEffect(() => {
    // 800ms debounce
    const timeout = setTimeout(() => {
      performSave();
    }, 800);

    return () => clearTimeout(timeout);
  }, [performSave]);
}

/**
 * useFoundationProgress
 * Hook to get real-time progress of foundation completion
 */
export function useFoundationProgress() {
  const completedSteps = useFoundationStore((s) => s.completedSteps);
  const totalSteps = useFoundationStore((s) => s.totalSteps);
  const currentStep = useFoundationStore((s) => s.currentStep);
  const status = useFoundationStore((s) => s.status);

  const progress = useFoundationStore.getState().getProgress();

  return {
    completedSteps,
    totalSteps,
    currentStep,
    status,
    progress,
    isComplete: completedSteps.length === totalSteps,
    remainingSteps: totalSteps - completedSteps.length,
  };
}

/**
 * getSectionForStep
 * Get the section ID for a given step number
 */
export function getSectionForStep(step: number): FoundationSectionId {
  const stepInfo = FOUNDATION_STEPS.find(s => s.step === step);
  return stepInfo?.section ?? "company_url";
}

/**
 * getStepForSection
 * Get the step number for a given section ID
 */
export function getStepForSection(section: FoundationSectionId): number {
  const stepInfo = FOUNDATION_STEPS.find(s => s.section === section);
  return stepInfo?.step ?? 1;
}
