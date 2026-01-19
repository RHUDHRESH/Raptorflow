import { create } from 'zustand';
import { supabase } from '@/lib/supabaseClient';
import {
    RICP,
    CoreMessaging,
    Channel,
    FoundationState
} from '@/types/foundation';

/* ══════════════════════════════════════════════════════════════════════════════
   FOUNDATION STORE — Supabase-backed
   Syncs RICPs, Messaging, and Channels to 'business_context_manifests' table.
   ══════════════════════════════════════════════════════════════════════════════ */

interface FoundationStore extends FoundationState {
    isLoading: boolean;
    error: string | null;

    // Actions
    fetchFoundation: (userId: string) => Promise<void>;
    saveFoundation: (userId: string) => Promise<void>;

    // RICP Actions
    addRICP: (ricp: RICP, userId: string) => Promise<void>;
    updateRICP: (id: string, updates: Partial<RICP>, userId: string) => Promise<void>;
    deleteRICP: (id: string, userId: string) => Promise<void>;
    getRICPById: (id: string) => RICP | undefined;

    // Messaging Actions
    updateMessaging: (updates: Partial<CoreMessaging>, userId: string) => Promise<void>;

    // Channel Actions
    addChannel: (channel: Channel, userId: string) => Promise<void>;
    updateChannel: (id: string, updates: Partial<Channel>, userId: string) => Promise<void>;
    deleteChannel: (id: string, userId: string) => Promise<void>;

    // Sync from Onboarding (Migration)
    syncFromOnboarding: (userId: string) => Promise<void>;

    // Utility
    reset: () => void;
}

export const useFoundationStore = create<FoundationStore>((set, get) => ({
    // Initial State
    ricps: [],
    messaging: null,
    channels: [],
    positioningConfidence: 0,
    isLoading: false,
    error: null,

    // Fetch from Supabase
    fetchFoundation: async (userId: string) => {
        set({ isLoading: true, error: null });
        try {
            const { data, error } = await supabase
                .from('business_context_manifests')
                .select('ricps, messaging, channels')
                .eq('user_id', userId)
                .single();

            if (error && error.code !== 'PGRST116') throw error; // PGRST116 is "Row not found"

            if (data) {
                set({
                    ricps: (data.ricps as unknown as RICP[]) || [],
                    messaging: (data.messaging as unknown as CoreMessaging) || null,
                    channels: (data.channels as unknown as Channel[]) || []
                });
            } else {
                // If no data in Supabase, try to sync from Onboarding
                await get().syncFromOnboarding(userId);
            }

        } catch (err: any) {
            console.error('Error fetching foundation:', err);
            set({ error: err.message });
        } finally {
            set({ isLoading: false });
        }
    },

    // Sync from Onboarding (local storage -> Supabase)
    syncFromOnboarding: async (userId: string) => {
        try {
            const stored = localStorage.getItem("raptorflow-onboarding");
            if (!stored) return;

            const parsed = JSON.parse(stored);
            const steps = parsed.state?.steps || [];
            if (!steps.length) return;

            // Extract Data
            const ricpStep = steps.find((s: any) => s.id === 16);
            const positioningStep = steps.find((s: any) => s.id === 14);
            const messagingStep = steps.find((s: any) => s.id === 18);
            const channelStep = steps.find((s: any) => s.id === 20);

            // Map RICPs
            const newRicps: RICP[] = [];
            if (ricpStep?.data?.personas && Array.isArray(ricpStep.data.personas)) {
                // Assuming step data matches RICP structure or mapping needed
                // For now, assume it might need robust mapping or is empty
                // This is a placeholder for actual mapping logic based on step data shape
            }

            // Map Messaging
            let newMessaging: CoreMessaging | null = null;
            if (positioningStep?.data || messagingStep?.data) {
                newMessaging = {
                    id: `msg-${Date.now()}`,
                    oneLiner: (positioningStep?.data?.statement as string) || "RaptorFlow: Marketing Operating System",
                    positioningStatement: {
                        target: (positioningStep?.data?.target as string) || "",
                        situation: (positioningStep?.data?.situation as string) || "",
                        product: (positioningStep?.data?.product as string) || "",
                        category: (positioningStep?.data?.category as string) || "",
                        keyBenefit: (positioningStep?.data?.benefit as string) || "",
                        alternatives: "",
                        differentiator: ""
                    },
                    valueProps: [],
                    brandVoice: { tone: [], doList: [], dontList: [] },
                    storyBrand: { character: '', problemExternal: '', problemInternal: '', problemPhilosophical: '', guide: '', plan: [], callToAction: '', transitionalCTA: '', avoidFailure: [], success: [] },
                    updatedAt: Date.now(),
                    confidence: 50
                };
            }

            // Update State if we found data
            const updates: Partial<FoundationState> = {};
            if (newRicps.length > 0) updates.ricps = newRicps;
            if (newMessaging) updates.messaging = newMessaging;
            // Channels mapping...

            if (Object.keys(updates).length > 0) {
                set((state) => ({ ...state, ...updates }));
                await get().saveFoundation(userId); // Persist to Supabase
                console.log("Synced onboarding data to Supabase");
            }

        } catch (err) {
            console.error("Error syncing onboarding data:", err);
        }
    },

    // Save entire state to Supabase (Upsert)
    saveFoundation: async (userId: string) => {
        const { ricps, messaging, channels } = get();
        try {
            const { error } = await supabase
                .from('business_context_manifests')
                .upsert(
                    { user_id: userId, ricps, messaging, channels },
                    { onConflict: 'user_id' }
                );

            if (error) throw error;
        } catch (err: any) {
            console.error('Error saving foundation:', err);
            set({ error: err.message });
        }
    },

    // RICP Actions
    addRICP: async (ricp, userId) => {
        set((state) => ({
            ricps: [...state.ricps, { ...ricp, createdAt: Date.now(), updatedAt: Date.now() }]
        }));
        await get().saveFoundation(userId);
    },

    updateRICP: async (id, updates, userId) => {
        set((state) => ({
            ricps: state.ricps.map((r) =>
                r.id === id ? { ...r, ...updates, updatedAt: Date.now() } : r
            )
        }));
        await get().saveFoundation(userId);
    },

    deleteRICP: async (id, userId) => {
        set((state) => ({
            ricps: state.ricps.filter((r) => r.id !== id)
        }));
        await get().saveFoundation(userId);
    },

    getRICPById: (id) => get().ricps.find((r) => r.id === id),

    // Messaging Actions
    updateMessaging: async (updates, userId) => {
        set((state) => ({
            messaging: state.messaging
                ? { ...state.messaging, ...updates, updatedAt: Date.now() }
                : {
                    id: `msg-${Date.now()}`,
                    oneLiner: '',
                    positioningStatement: { target: '', situation: '', product: '', category: '', keyBenefit: '', alternatives: '', differentiator: '' },
                    valueProps: [],
                    brandVoice: { tone: [], doList: [], dontList: [] },
                    storyBrand: { character: '', problemExternal: '', problemInternal: '', problemPhilosophical: '', guide: '', plan: [], callToAction: '', transitionalCTA: '', avoidFailure: [], success: [] },
                    updatedAt: Date.now(),
                    confidence: 0,
                    ...updates
                }
        }));
        await get().saveFoundation(userId);
    },

    // Channel Actions
    addChannel: async (channel, userId) => {
        set((state) => ({
            channels: [...state.channels, channel]
        }));
        await get().saveFoundation(userId);
    },

    updateChannel: async (id, updates, userId) => {
        set((state) => ({
            channels: state.channels.map((c) =>
                c.id === id ? { ...c, ...updates } : c
            )
        }));
        await get().saveFoundation(userId);
    },

    deleteChannel: async (id, userId) => {
        set((state) => ({
            channels: state.channels.filter((c) => c.id !== id)
        }));
        await get().saveFoundation(userId);
    },

    // Utility
    reset: () => set({
        ricps: [],
        messaging: null,
        channels: [],
        positioningConfidence: 0,
        error: null
    }),
}));

export type { RICP, CoreMessaging, Channel, MarketSophisticationStage };
