import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Icp, IcpMemory } from '@/types/icp-types';

interface IcpState {
    icps: Icp[];
    activeIcpId: string | null;

    // Actions
    createIcp: (icp: Partial<Icp>) => string;
    updateIcp: (id: string, updates: Partial<Icp>) => void;
    deleteIcp: (id: string) => void;
    setActiveIcp: (id: string) => void;
    getPrimaryIcp: () => Icp | undefined;
    getIcpMemory: (id: string) => IcpMemory | null;
}

const DEFAULT_ICP: Icp = {
    id: 'default',
    workspaceId: 'default-ws',
    name: 'Default ICP',
    priority: 'primary',
    status: 'draft',
    confidenceScore: 0.5,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    firmographics: {
        companyType: [],
        geography: [],
        salesMotion: [],
        budgetComfort: [],
        decisionMaker: []
    },
    painMap: {
        primaryPains: [],
        secondaryPains: [],
        triggerEvents: [],
        urgencyLevel: 'soon'
    },
    psycholinguistics: {
        mindsetTraits: [],
        emotionalTriggers: [],
        tonePreference: [],
        wordsToUse: [],
        wordsToAvoid: [],
        proofPreference: [],
        ctaStyle: []
    },
    disqualifiers: {
        excludedCompanyTypes: [],
        excludedGeographies: [],
        excludedBehaviors: []
    }
};

export const useIcpStore = create<IcpState>()(
    persist(
        (set, get) => ({
            icps: [],
            activeIcpId: null,

            createIcp: (icpData) => {
                const id = crypto.randomUUID();
                const newIcp: Icp = {
                    ...DEFAULT_ICP,
                    ...icpData,
                    id,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };

                set((state) => ({
                    icps: [...state.icps, newIcp],
                    activeIcpId: state.activeIcpId || id // Set active if none exists
                }));

                return id;
            },

            updateIcp: (id, updates) => {
                set((state) => ({
                    icps: state.icps.map((icp) =>
                        icp.id === id
                            ? { ...icp, ...updates, updatedAt: new Date().toISOString() }
                            : icp
                    )
                }));
            },

            deleteIcp: (id) => {
                set((state) => ({
                    icps: state.icps.filter((icp) => icp.id !== id),
                    activeIcpId: state.activeIcpId === id ? null : state.activeIcpId
                }));
            },

            setActiveIcp: (id) => set({ activeIcpId: id }),

            getPrimaryIcp: () => {
                const state = get();
                return state.icps.find(i => i.priority === 'primary') || state.icps[0];
            },

            getIcpMemory: (id) => {
                const icp = get().icps.find(i => i.id === id);
                if (!icp) return null;

                // Transform to Memory Object
                return {
                    id: icp.id,
                    priority: icp.priority,
                    confidence: icp.confidenceScore,
                    targeting: {
                        who: [...icp.firmographics.companyType, ...icp.firmographics.decisionMaker],
                        whoNot: icp.disqualifiers.excludedCompanyTypes,
                        budget: icp.firmographics.budgetComfort,
                        urgency: icp.painMap.urgencyLevel
                    },
                    pains: {
                        primary: icp.painMap.primaryPains,
                        triggers: icp.painMap.triggerEvents
                    },
                    language: {
                        tone: icp.psycholinguistics.tonePreference,
                        wordsToUse: icp.psycholinguistics.wordsToUse,
                        wordsToAvoid: icp.psycholinguistics.wordsToAvoid,
                        proofStyle: icp.psycholinguistics.proofPreference,
                        ctaStyle: icp.psycholinguistics.ctaStyle
                    }
                };
            }
        }),
        {
            name: 'raptorflow-icp-store',
        }
    )
);
