import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
    RICP,
    CoreMessaging,
    Channel,
    FoundationState,
    MarketSophisticationStage
} from '@/types/foundation';
import { api } from '@/lib/api/client';

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   FOUNDATION STORE ΓÇö RICP & Messaging State Management
   Persisted to localStorage for demo purposes
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

// Sample RICP: "Ambitious SaaS Founder" (Sarah)
const SAMPLE_RICP: RICP = {
    id: 'ricp-001',
    name: 'Ambitious SaaS Founder',
    personaName: 'Sarah',
    avatar: '≡ƒæ⌐ΓÇì≡ƒÆ╗',
    demographics: {
        ageRange: '32-45 years old',
        income: '$150,000 - $400,000',
        location: 'Urban tech hubs (SF, NYC, Austin)',
        role: 'Founder/CEO of B2B SaaS',
        stage: 'Seed to Series A',
    },
    psychographics: {
        beliefs: 'Marketing should be measurable and strategic, not just "post more"',
        identity: 'A builder who is technical but knows marketing is the bottleneck',
        becoming: 'A CEO who understands go-to-market as well as product',
        fears: 'Wasting money on agencies that don\'t understand their business',
        values: ['Speed', 'Clarity', 'Data-driven decisions'],
        hangouts: ['Twitter/X', 'Marketing & founder threads', 'YC forums', 'Indie Hacker communities'],
        contentConsumed: ['Lenny\'s Podcast', 'My First Million', 'How I Write', 'SaaS newsletters'],
        whoTheyFollow: ['Successful founders', 'Marketing operators', 'Not gurus'],
        language: ['CAC', 'LTV', 'PMF', 'growth loops', 'positioning'],
        timing: ['Sunday evenings (planning weeks)', 'Wednesday mornings'],
        triggers: ['Plateaued growth', 'Raising funding', 'Hiring first marketer'],
    },
    marketSophistication: 3,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    confidence: 85,
};

// Sample Core Messaging
const SAMPLE_MESSAGING: CoreMessaging = {
    id: 'msg-001',
    oneLiner: 'RaptorFlow is the marketing operating system for founders who want control, not chaos.',
    positioningStatement: {
        target: 'B2B SaaS founders',
        situation: 'who struggle with inconsistent marketing',
        product: 'RaptorFlow',
        category: 'Marketing Operating System',
        keyBenefit: 'converts chaos into clarity',
        alternatives: 'random posting and agency guesswork',
        differentiator: "it's built by founders, for founders",
    },
    valueProps: [
        { title: 'Clarity', description: 'Know exactly what to say and who to say it to', proof: '92% positioning confidence score' },
        { title: 'Speed', description: 'From zero to execution this week', proof: 'Average 3-day setup time' },
        { title: 'Control', description: 'One system, one source of truth', proof: 'Replace 5+ tools with one' },
    ],
    brandVoice: {
        tone: ['Calm', 'Precise', 'Confident', 'Surgical'],
        doList: ['Short sentences', 'Strong verbs', 'Data-backed claims', 'Specific outcomes'],
        dontList: ['Emojis in product UI', 'Hype words without proof', 'Generic marketing speak', 'Unnecessary jargon'],
    },
    storyBrand: {
        character: 'Sarah, the ambitious SaaS founder',
        problemExternal: 'Plateaued growth despite a great product',
        problemInternal: 'Feeling overwhelmed and out of control with marketing',
        problemPhilosophical: 'Marketing shouldn\'t be this hard for smart people',
        guide: 'RaptorFlow ΓÇö the calm, surgical marketing operating system',
        plan: ['Define your Foundation', 'Create tactical Moves', 'Execute with the calendar', 'Track and iterate'],
        callToAction: 'Start your first Move',
        transitionalCTA: 'See how it works',
        avoidFailure: ['Continued random posting', 'Wasted ad spend', 'Founder burnout', 'Hiring the wrong agency'],
        success: ['Marketing finally under control', 'Predictable growth', 'More time for product', 'Confidence in GTM'],
    },
    updatedAt: Date.now(),
    confidence: 78,
};

// Sample Channels
const SAMPLE_CHANNELS: Channel[] = [
    { id: 'ch-001', name: 'LinkedIn', priority: 'primary', status: 'active', notes: 'Thought leadership & founder content' },
    { id: 'ch-002', name: 'Twitter/X', priority: 'primary', status: 'active', notes: 'Real-time engagement & threads' },
    { id: 'ch-003', name: 'Email Newsletter', priority: 'secondary', status: 'planned', notes: 'Weekly insights for subscribers' },
    { id: 'ch-004', name: 'YouTube', priority: 'experimental', status: 'paused', notes: 'Long-form tutorials' },
];

interface FoundationStore extends FoundationState {
    // RICP Actions
    addRICP: (ricp: RICP) => void;
    updateRICP: (id: string, updates: Partial<RICP>) => void;
    deleteRICP: (id: string) => void;
    getRICPById: (id: string) => RICP | undefined;

    // Messaging Actions
    updateMessaging: (updates: Partial<CoreMessaging>) => void;

    // Channel Actions
    addChannel: (channel: Channel) => void;
    updateChannel: (id: string, updates: Partial<Channel>) => void;
    deleteChannel: (id: string) => void;

    // Data Sync
    fetchFoundation: () => Promise<void>;

    // Utility
    resetToSample: () => void;
}

export const useFoundationStore = create<FoundationStore>()(
    persist(
        (set, get) => ({
            // Initial State
            ricps: [SAMPLE_RICP],
            messaging: SAMPLE_MESSAGING,
            channels: SAMPLE_CHANNELS,
            positioningConfidence: 78,

            // RICP Actions
            addRICP: (ricp) => set((state) => ({
                ricps: [...state.ricps, { ...ricp, createdAt: Date.now(), updatedAt: Date.now() }]
            })),

            updateRICP: (id, updates) => set((state) => ({
                ricps: state.ricps.map((r) =>
                    r.id === id ? { ...r, ...updates, updatedAt: Date.now() } : r
                )
            })),

            deleteRICP: (id) => set((state) => ({
                ricps: state.ricps.filter((r) => r.id !== id)
            })),

            getRICPById: (id) => get().ricps.find((r) => r.id === id),

            // Messaging Actions
            updateMessaging: (updates) => set((state) => ({
                messaging: state.messaging
                    ? { ...state.messaging, ...updates, updatedAt: Date.now() }
                    : null
            })),

            // Channel Actions
            addChannel: (channel) => set((state) => ({
                channels: [...state.channels, channel]
            })),

            updateChannel: (id, updates) => set((state) => ({
                channels: state.channels.map((c) =>
                    c.id === id ? { ...c, ...updates } : c
                )
            })),

            deleteChannel: (id) => set((state) => ({
                channels: state.channels.filter((c) => c.id !== id)
            })),

            // Data Sync
            fetchFoundation: async () => {
                try {
                    const response = await api.get('/foundation/');
                    const data = response.data as any;
                    
                    set({
                        ricps: data.ricps || [],
                        messaging: data.messaging || null,
                        positioningConfidence: data.messaging?.confidence || 0,
                    });
                } catch (error) {
                    console.error("Failed to fetch foundation:", error);
                }
            },

            // Utility
            resetToSample: () => set({
                ricps: [SAMPLE_RICP],
                messaging: SAMPLE_MESSAGING,
                channels: SAMPLE_CHANNELS,
                positioningConfidence: 78,
            }),
        }),
        {
            name: 'raptorflow-foundation',
        }
    )
);

export type { RICP, CoreMessaging, Channel, MarketSophisticationStage };
