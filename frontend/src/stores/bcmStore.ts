import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface BusinessContext {
  foundation: {
    company: string;
    mission: string;
    value_prop: string;
  };
  icps: Array<{
    id: string;
    name: string;
    demographics: any;
    psychographics: any;
  }>;
  competitive: {
    competitors: string[];
    positioning: string;
    differentiation: string;
  };
  messaging: {
    one_liner: string;
    value_props: string[];
    brand_voice: {
      tone: string[];
      do_list: string[];
      dont_list: string[];
    };
  };
  meta: {
    source: string;
    token_budget: number;
    version: number;
    checksum: string;
    created_at: string;
    updated_at: string;
  };
  evolution?: {
    index: number;
    insights: string[];
    contradictions: any[];
  };
  history?: {
    total_events: number;
    milestones: string[];
  };
  telemetry?: {
    total_interactions: number;
    recent_activity: any[];
  };
}

interface BCMStore {
  bcm: BusinessContext | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setBCM: (bcm: BusinessContext) => void;
  updateBCM: (updates: Partial<BusinessContext>) => void;
  clearBCM: () => void;
  generateFromOnboarding: (onboardingData: any) => Promise<void>;
  validateBCM: (bcm: BusinessContext) => { isValid: boolean; errors: string[] };
  exportBCM: () => string;
  importBCM: (jsonString: string) => { success: boolean; error?: string };
  calculateChecksum: (bcm: Omit<BusinessContext, 'meta'>) => string;
  syncWithEvolution: (ucid: string) => Promise<void>;
  refineBCM: (ucid: string) => Promise<void>;
}

export const useBCMStore = create<BCMStore>()(
  persist(
    (set, get) => ({
      // Initial state
      bcm: null,
      isLoading: false,
      error: null,

      // Set BCM
      setBCM: (bcm) => set({ bcm, error: null }),

      // Update BCM
      updateBCM: (updates) => set((state) => {
        if (!state.bcm) return state;
        
        const updatedBCM = {
          ...state.bcm,
          ...updates,
          meta: {
            ...state.bcm.meta,
            ...updates.meta,
            updated_at: new Date().toISOString(),
            version: state.bcm.meta.version + 1,
          }
        };

        // Recalculate checksum
        const { meta, ...bcmWithoutMeta } = updatedBCM;
        const checksum = get().calculateChecksum(bcmWithoutMeta);
        updatedBCM.meta.checksum = checksum;

        return { bcm: updatedBCM, error: null };
      }),

      // Clear BCM
      clearBCM: () => set({ bcm: null, error: null }),

      // Generate from onboarding data
      generateFromOnboarding: async (onboardingData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch('/api/bcm/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ onboarding_data: onboardingData })
          });

          if (!response.ok) {
            throw new Error('Failed to generate BCM');
          }

          const data = await response.json();
          
          if (data.success && data.bcm) {
            set({ bcm: data.bcm, isLoading: false });
          } else {
            throw new Error(data.error || 'Invalid response');
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to generate BCM',
            isLoading: false 
          });
        }
      },

      // Validate BCM
      validateBCM: (bcm) => {
        const errors: string[] = [];

        // Foundation validation
        if (!bcm.foundation.company) errors.push('Company name is required');
        if (!bcm.foundation.mission) errors.push('Mission statement is required');
        if (!bcm.foundation.value_prop) errors.push('Value proposition is required');

        // ICPs validation
        if (!bcm.icps || bcm.icps.length === 0) {
          errors.push('At least one ICP is required');
        }

        // Messaging validation
        if (!bcm.messaging.one_liner) errors.push('One-liner is required');
        if (!bcm.messaging.value_props || bcm.messaging.value_props.length === 0) {
          errors.push('At least one value proposition is required');
        }

        return {
          isValid: errors.length === 0,
          errors
        };
      },

      // Export BCM
      exportBCM: () => {
        const { bcm } = get();
        if (!bcm) return '';
        
        return JSON.stringify(bcm, null, 2);
      },

      // Import BCM
      importBCM: (jsonString) => {
        try {
          const bcm = JSON.parse(jsonString) as BusinessContext;
          const validation = get().validateBCM(bcm);
          
          if (!validation.isValid) {
            return { 
              success: false, 
              error: `Invalid BCM: ${validation.errors.join(', ')}` 
            };
          }

          set({ bcm, error: null });
          return { success: true };
        } catch (error) {
          return { 
            success: false, 
            error: error instanceof Error ? error.message : 'Invalid JSON' 
          };
        }
      },

      // Calculate checksum
      calculateChecksum: (bcmWithoutMeta) => {
        const manifestStr = JSON.stringify(bcmWithoutMeta, Object.keys(bcmWithoutMeta).sort());
        let hash = 0;
        for (let i = 0; i < manifestStr.length; i++) {
          const char = manifestStr.charCodeAt(i);
          hash = ((hash << 5) - hash) + char;
          hash = hash & hash; // Convert to 32-bit integer
        }
        return hash.toString(16);
      },

      // Sync with Evolution API (Everything state)
      syncWithEvolution: async (ucid) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`/api/v1/evolution/state/${ucid}`);
          if (!response.ok) throw new Error('Failed to fetch evolution state');
          
          const data = await response.json();
          const evolutionState = data.state;

          set((state) => ({
            bcm: {
              ...state.bcm!,
              evolution: {
                index: evolutionState.history.evolution_index,
                insights: evolutionState.evolved_insights,
                contradictions: evolutionState.contradiction_log
              },
              history: {
                total_events: evolutionState.history.total_events,
                milestones: evolutionState.history.significant_milestones
              },
              telemetry: {
                total_interactions: evolutionState.telemetry.total_interactions,
                recent_activity: evolutionState.telemetry.recent_interactions
              }
            },
            isLoading: false
          }));
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Sync failed',
            isLoading: false 
          });
        }
      },

      // Trigger AI Refinement
      refineBCM: async (ucid) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch('/api/v1/evolution/refine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ucid })
          });
          
          if (!response.ok) throw new Error('Refinement failed');
          
          // Re-sync after refinement
          await get().syncWithEvolution(ucid);
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Refinement failed',
            isLoading: false 
          });
        }
      }
    }),
    {
      name: 'raptorflow-bcm',
    }
  )
);
