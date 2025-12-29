import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Icp, IcpMemory } from '@/types/icp-types';
import { FoundationData } from './foundation';
import { generateICPsFromFoundation } from './icp-generator';

interface IcpState {
  icps: Icp[];
  activeIcpId: string | null;
  lastGeneratedAt: string | null;

  // Actions
  createIcp: (icp: Partial<Icp>) => string;
  updateIcp: (id: string, updates: Partial<Icp>) => void;
  deleteIcp: (id: string) => void;
  setActiveIcp: (id: string) => void;
  getPrimaryIcp: () => Icp | undefined;
  getIcpMemory: (id: string) => IcpMemory | null;
  generateFromFoundation: (data: FoundationData) => void;
  clearAll: () => void;
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
    decisionMaker: [],
  },
  painMap: {
    primaryPains: [],
    secondaryPains: [],
    triggerEvents: [],
    urgencyLevel: 'soon',
  },
  psycholinguistics: {
    mindsetTraits: [],
    emotionalTriggers: [],
    tonePreference: [],
    wordsToUse: [],
    wordsToAvoid: [],
    proofPreference: [],
    ctaStyle: [],
  },
  disqualifiers: {
    excludedCompanyTypes: [],
    excludedGeographies: [],
    excludedBehaviors: [],
  },
};

export const useIcpStore = create<IcpState>()(
  persist(
    (set, get) => ({
      icps: [],
      activeIcpId: null,
      lastGeneratedAt: null,

      createIcp: (icpData) => {
        const id = crypto.randomUUID();
        const newIcp: Icp = {
          ...DEFAULT_ICP,
          ...icpData,
          id,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };

        set((state) => ({
          icps: [...state.icps, newIcp],
          activeIcpId: state.activeIcpId || id, // Set active if none exists
        }));

        return id;
      },

      updateIcp: (id, updates) => {
        set((state) => ({
          icps: state.icps.map((icp) =>
            icp.id === id
              ? { ...icp, ...updates, updatedAt: new Date().toISOString() }
              : icp
          ),
        }));
      },

      deleteIcp: (id) => {
        set((state) => ({
          icps: state.icps.filter((icp) => icp.id !== id),
          activeIcpId: state.activeIcpId === id ? null : state.activeIcpId,
        }));
      },

      setActiveIcp: (id) => set({ activeIcpId: id }),

      getPrimaryIcp: () => {
        const state = get();
        return (
          state.icps.find((i) => i.priority === 'primary') || state.icps[0]
        );
      },

      getIcpMemory: (id) => {
        const icp = get().icps.find((i) => i.id === id);
        if (!icp) return null;

        // Transform to Memory Object
        return {
          id: icp.id,
          priority: icp.priority,
          confidence: icp.confidenceScore,
          targeting: {
            who: [
              ...icp.firmographics.companyType,
              ...icp.firmographics.decisionMaker,
            ],
            whoNot: icp.disqualifiers.excludedCompanyTypes,
            budget: icp.firmographics.budgetComfort,
            urgency: icp.painMap.urgencyLevel,
          },
          pains: {
            primary: icp.painMap.primaryPains,
            triggers: icp.painMap.triggerEvents,
          },
          language: {
            tone: icp.psycholinguistics.tonePreference,
            wordsToUse: icp.psycholinguistics.wordsToUse,
            wordsToAvoid: icp.psycholinguistics.wordsToAvoid,
            proofStyle: icp.psycholinguistics.proofPreference,
            ctaStyle: icp.psycholinguistics.ctaStyle,
          },
        };
      },

      generateFromFoundation: (data) => {
        // Clear existing ICPs first
        const generated = generateICPsFromFoundation(data);
        const now = new Date().toISOString();

        const newIcps: Icp[] = generated.map(
          (g, _idx) =>
            ({
              ...DEFAULT_ICP,
              ...g.icp,
              id: crypto.randomUUID(),
              workspaceId: 'default-ws',
              createdAt: now,
              updatedAt: now,
            }) as Icp
        );

        const primaryIcp = newIcps.find((i) => i.priority === 'primary');

        set({
          icps: newIcps,
          activeIcpId: primaryIcp?.id || newIcps[0]?.id || null,
          lastGeneratedAt: now,
        });
      },

      clearAll: () => {
        set({
          icps: [],
          activeIcpId: null,
          lastGeneratedAt: null,
        });
      },
    }),
    {
      name: 'raptorflow-icp-store',
    }
  )
);
