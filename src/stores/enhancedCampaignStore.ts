/* ══════════════════════════════════════════════════════════════════════════════
   ENHANCED CAMPAIGN STORE
   Comprehensive state management for Moves & Campaigns system
   ═════════════════════════════════════════════════════════════════════════════ */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  Campaign,
  Move,
  Play,
  CampaignStatus,
  MoveStatus,
  CampaignAnalytics,
  CreateCampaignRequest,
  UpdateCampaignRequest,
  createCampaignId,
  createMoveId
} from '@/types/campaign';

interface EnhancedCampaignStoreState {
  // State
  campaigns: Record<string, Campaign>;
  moves: Record<string, Move>;
  plays: Record<string, Play>;
  activeCampaign: string | null;
  loading: boolean;
  error: string | null;

  // Campaign Actions
  createCampaign: (request: CreateCampaignRequest) => Promise<string>;
  updateCampaign: (request: UpdateCampaignRequest) => Promise<void>;
  deleteCampaign: (id: string) => Promise<void>;
  duplicateCampaign: (id: string, name?: string) => Promise<string>;
  setActiveCampaign: (id: string | null) => void;

  // Move Actions
  createMove: (campaignId: string, move: Omit<Move, 'id' | 'createdAt' | 'updatedAt'>) => Promise<string>;
  updateMove: (moveId: string, updates: Partial<Move>) => Promise<void>;
  deleteMove: (moveId: string) => Promise<void>;
  executeMove: (moveId: string) => Promise<void>;
  pauseMove: (moveId: string) => Promise<void>;
  resumeMove: (moveId: string) => Promise<void>;

  // Play Actions
  createPlay: (play: Omit<Play, 'id' | 'createdAt' | 'updatedAt'>) => Promise<string>;
  updatePlay: (playId: string, updates: Partial<Play>) => Promise<void>;
  deletePlay: (playId: string) => Promise<void>;
  executePlay: (playId: string) => Promise<void>;
  pausePlay: (playId: string) => Promise<void>;
  resumePlay: (playId: string) => Promise<void>;

  // Analytics
  updateCampaignAnalytics: (campaignId: string, analytics: Partial<CampaignAnalytics>) => void;
  refreshAnalytics: (campaignId: string) => Promise<void>;

  // Bulk Actions
  bulkUpdateStatus: (campaignIds: string[], status: CampaignStatus) => Promise<void>;
  bulkDelete: (campaignIds: string[]) => Promise<void>;
}

export const useEnhancedCampaignStore = create<EnhancedCampaignStoreState>()(
  devtools(
    (set, get) => ({
      // Initial State
      campaigns: {},
      moves: {},
      plays: {},
      activeCampaign: null,
      loading: false,
      error: null,

      // Campaign Actions
      createCampaign: async (request) => {
        set({ loading: true, error: null });

        try {
          const id = createCampaignId();
          const now = new Date();

          const campaign: Campaign = {
            id,
            name: request.name,
            description: request.description,
            objective: request.objective,
            status: CampaignStatus.DRAFT,
            targetAudience: {
              id: `aud_${Date.now()}`,
              name: request.targetAudience.name || 'Default Audience',
              criteria: request.targetAudience.criteria || {},
              size: 0,
              estimatedReach: 0,
              customProperties: {}
            },
            budget: {
              total: request.budget.total || 0,
              currency: request.budget.currency || 'USD',
              allocated: {},
              spent: 0,
              remaining: request.budget.total || 0
            },
            timeline: {
              startDate: request.timeline.startDate || now,
              endDate: request.timeline.endDate || new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000),
              phases: [],
              milestones: []
            },
            moves: [],
            plays: [],
            analytics: {
              overview: {
                totalReach: 0,
                totalEngagement: 0,
                totalConversions: 0,
                totalRevenue: 0,
                totalCost: 0,
                roi: 0
              },
              funnel: {
                stages: [],
                conversionRates: {}
              },
              engagement: {
                byChannel: {},
                byContentType: {},
                byTimeframe: {}
              },
              roi: {
                spend: 0,
                revenue: 0,
                profit: 0,
                roi: 0,
                roas: 0,
                cac: 0,
                ltv: 0
              },
              performance: {
                kpis: [],
                benchmarks: [],
                trends: []
              }
            },
            team: {
              ownerId: 'current_user',
              members: [],
              roles: {},
              permissions: []
            },
            settings: {
              autoOptimization: false,
              abTesting: false,
              notifications: {
                email: true,
                push: false,
                slack: false,
                frequency: 'daily',
                events: []
              },
              integrations: {},
              branding: {
                colors: {
                  primary: '#000000',
                  secondary: '#666666'
                },
                fonts: {
                  heading: 'Inter',
                  body: 'Inter'
                },
                voice: {
                  tone: 'professional',
                  style: 'direct'
                }
              }
            },
            createdAt: now,
            updatedAt: now,
            createdBy: 'current_user',
            tags: []
          };

          set(state => ({
            campaigns: { ...state.campaigns, [id]: campaign },
            loading: false
          }));

          return id;
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to create campaign', loading: false });
          throw error;
        }
      },

      updateCampaign: async (request) => {
        set({ loading: true, error: null });

        try {
          const { campaigns } = get();
          const campaign = campaigns[request.id];

          if (!campaign) {
            throw new Error('Campaign not found');
          }

          const updated = {
            ...campaign,
            ...request,
            targetAudience: request.targetAudience ? {
              ...campaign.targetAudience,
              ...request.targetAudience
            } : campaign.targetAudience,
            budget: request.budget ? {
              ...campaign.budget,
              ...request.budget
            } : campaign.budget,
            timeline: request.timeline ? {
              ...campaign.timeline,
              ...request.timeline
            } : campaign.timeline,
            settings: request.settings ? {
              ...campaign.settings,
              ...request.settings
            } : campaign.settings,
            updatedAt: new Date()
          };

          set(state => ({
            campaigns: { ...state.campaigns, [request.id]: updated },
            loading: false
          }));
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to update campaign', loading: false });
          throw error;
        }
      },

      deleteCampaign: async (id) => {
        set({ loading: true, error: null });

        try {
          const { campaigns, moves, activeCampaign } = get();

          // Delete associated moves
          const campaignMoves = campaigns[id]?.moves || [];
          const newMoves = { ...moves };
          campaignMoves.forEach(moveId => {
            delete newMoves[moveId];
          });

          // Delete campaign
          const newCampaigns = { ...campaigns };
          delete newCampaigns[id];

          set({
            campaigns: newCampaigns,
            moves: newMoves,
            activeCampaign: activeCampaign === id ? null : activeCampaign,
            loading: false
          });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to delete campaign', loading: false });
          throw error;
        }
      },

      duplicateCampaign: async (id, name) => {
        set({ loading: true, error: null });

        try {
          const { campaigns } = get();
          const original = campaigns[id];

          if (!original) {
            throw new Error('Campaign not found');
          }

          const newId = createCampaignId();
          const now = new Date();

          const duplicate: Campaign = {
            ...original,
            id: newId,
            name: name || `${original.name} (Copy)`,
            status: CampaignStatus.DRAFT,
            moves: [],
            plays: [],
            analytics: {
              overview: {
                totalReach: 0,
                totalEngagement: 0,
                totalConversions: 0,
                totalRevenue: 0,
                totalCost: 0,
                roi: 0
              },
              funnel: {
                stages: [],
                conversionRates: {}
              },
              engagement: {
                byChannel: {},
                byContentType: {},
                byTimeframe: {}
              },
              roi: {
                spend: 0,
                revenue: 0,
                profit: 0,
                roi: 0,
                roas: 0,
                cac: 0,
                ltv: 0
              },
              performance: {
                kpis: [],
                benchmarks: [],
                trends: []
              }
            },
            createdAt: now,
            updatedAt: now,
            createdBy: 'current_user'
          };

          set(state => ({
            campaigns: { ...state.campaigns, [newId]: duplicate },
            loading: false
          }));

          return newId;
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to duplicate campaign', loading: false });
          throw error;
        }
      },

      setActiveCampaign: (id) => {
        set({ activeCampaign: id });
      },

      // Move Actions
      createMove: async (campaignId, move) => {
        set({ loading: true, error: null });

        try {
          const id = createMoveId();
          const now = new Date();

          const newMove: Move = {
            ...move,
            id,
            status: MoveStatus.DRAFT,
            execution: {
              attempts: 0,
              logs: [],
              results: {
                success: false,
                metrics: {}
              }
            },
            analytics: {},
            createdAt: now,
            updatedAt: now
          };

          set(state => ({
            moves: { ...state.moves, [id]: newMove },
            campaigns: {
              ...state.campaigns,
              [campaignId]: {
                ...state.campaigns[campaignId],
                moves: [...state.campaigns[campaignId].moves, id],
                updatedAt: now
              }
            },
            loading: false
          }));

          return id;
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to create move', loading: false });
          throw error;
        }
      },

      updateMove: async (moveId, updates) => {
        set({ loading: true, error: null });

        try {
          const { moves } = get();
          const move = moves[moveId];

          if (!move) {
            throw new Error('Move not found');
          }

          const updated = {
            ...move,
            ...updates,
            updatedAt: new Date()
          };

          set(state => ({
            moves: { ...state.moves, [moveId]: updated },
            loading: false
          }));
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to update move', loading: false });
          throw error;
        }
      },

      deleteMove: async (moveId) => {
        set({ loading: true, error: null });

        try {
          const { campaigns, moves } = get();

          // Remove move from campaigns
          const newCampaigns = { ...campaigns };
          Object.values(newCampaigns).forEach(campaign => {
            campaign.moves = campaign.moves.filter(id => id !== moveId);
          });

          // Delete move
          const newMoves = { ...moves };
          delete newMoves[moveId];

          set({
            campaigns: newCampaigns,
            moves: newMoves,
            loading: false
          });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to delete move', loading: false });
          throw error;
        }
      },

      executeMove: async (moveId) => {
        set({ loading: true, error: null });

        try {
          await get().updateMove(moveId, {
            status: MoveStatus.RUNNING,
            execution: {
              ...get().moves[moveId].execution,
              startedAt: new Date()
            }
          });

          // Simulate execution
          setTimeout(async () => {
            await get().updateMove(moveId, {
              status: MoveStatus.COMPLETED,
              execution: {
                ...get().moves[moveId].execution,
                completedAt: new Date(),
                results: {
                  success: true,
                  metrics: {
                    sent: 1000,
                    delivered: 950,
                    opened: 400,
                    clicked: 80
                  }
                }
              }
            });
          }, 2000);

          set({ loading: false });
        } catch (error) {
          await get().updateMove(moveId, {
            status: MoveStatus.FAILED,
            execution: {
              ...get().moves[moveId].execution,
              lastError: error instanceof Error ? error.message : 'Execution failed'
            }
          });
          set({ error: error instanceof Error ? error.message : 'Failed to execute move', loading: false });
          throw error;
        }
      },

      pauseMove: async (moveId) => {
        await get().updateMove(moveId, { status: MoveStatus.CANCELLED });
      },

      resumeMove: async (moveId) => {
        await get().updateMove(moveId, { status: MoveStatus.SCHEDULED });
      },

      // Play Actions
      createPlay: async (play) => {
        set({ loading: true, error: null });

        try {
          const id = `play_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          const now = new Date();

          const newPlay: Play = {
            ...play,
            id,
            isActive: false,
            createdAt: now,
            updatedAt: now
          };

          set(state => ({
            plays: { ...state.plays, [id]: newPlay },
            loading: false
          }));

          return id;
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to create play', loading: false });
          throw error;
        }
      },

      updatePlay: async (playId, updates) => {
        set({ loading: true, error: null });

        try {
          const { plays } = get();
          const play = plays[playId];

          if (!play) {
            throw new Error('Play not found');
          }

          const updated = {
            ...play,
            ...updates,
            updatedAt: new Date()
          };

          set(state => ({
            plays: { ...state.plays, [playId]: updated },
            loading: false
          }));
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to update play', loading: false });
          throw error;
        }
      },

      deletePlay: async (playId) => {
        set({ loading: true, error: null });

        try {
          const { plays } = get();
          const newPlays = { ...plays };
          delete newPlays[playId];

          set({ plays: newPlays, loading: false });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to delete play', loading: false });
          throw error;
        }
      },

      executePlay: async (playId) => {
        set({ loading: true, error: null });

        try {
          const play = get().plays[playId];
          if (!play) throw new Error('Play not found');

          // Execute all moves in the play
          for (const moveId of play.moves) {
            await get().executeMove(moveId);
          }

          await get().updatePlay(playId, { isActive: true });
          set({ loading: false });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to execute play', loading: false });
          throw error;
        }
      },

      pausePlay: async (playId) => {
        set({ loading: true, error: null });
        try {
          await get().updatePlay(playId, { isActive: false });
          set({ loading: false });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to pause play', loading: false });
          throw error;
        }
      },

      resumePlay: async (playId) => {
        set({ loading: true, error: null });
        try {
          await get().updatePlay(playId, { isActive: true });
          set({ loading: false });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to resume play', loading: false });
          throw error;
        }
      },

      // Analytics
      updateCampaignAnalytics: (campaignId, analytics) => {
        const { campaigns } = get();
        const campaign = campaigns[campaignId];

        if (campaign) {
          set(state => ({
            campaigns: {
              ...state.campaigns,
              [campaignId]: {
                ...campaign,
                analytics: {
                  ...campaign.analytics,
                  ...analytics
                },
                updatedAt: new Date()
              }
            }
          }));
        }
      },

      refreshAnalytics: async (campaignId) => {
        set({ loading: true, error: null });

        try {
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 1000));

          // Mock updated analytics
          const mockAnalytics = {
            overview: {
              totalReach: Math.floor(Math.random() * 10000),
              totalEngagement: Math.floor(Math.random() * 1000),
              totalConversions: Math.floor(Math.random() * 100),
              totalRevenue: Math.floor(Math.random() * 10000),
              totalCost: Math.floor(Math.random() * 1000),
              roi: Math.floor(Math.random() * 200)
            }
          };

          get().updateCampaignAnalytics(campaignId, mockAnalytics);
          set({ loading: false });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to refresh analytics', loading: false });
          throw error;
        }
      },

      // Bulk Actions
      bulkUpdateStatus: async (campaignIds, status) => {
        set({ loading: true, error: null });

        try {
          const { campaigns } = get();
          const newCampaigns = { ...campaigns };

          campaignIds.forEach(id => {
            if (newCampaigns[id]) {
              newCampaigns[id] = {
                ...newCampaigns[id],
                status,
                updatedAt: new Date()
              };
            }
          });

          set({ campaigns: newCampaigns, loading: false });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to bulk update', loading: false });
          throw error;
        }
      },

      bulkDelete: async (campaignIds) => {
        set({ loading: true, error: null });

        try {
          const { campaigns, moves, activeCampaign } = get();
          const newCampaigns = { ...campaigns };
          const newMoves = { ...moves };

          campaignIds.forEach(id => {
            // Delete associated moves
            const campaignMoves = campaigns[id]?.moves || [];
            campaignMoves.forEach(moveId => {
              delete newMoves[moveId];
            });

            // Delete campaign
            delete newCampaigns[id];
          });

          set({
            campaigns: newCampaigns,
            moves: newMoves,
            activeCampaign: campaignIds.includes(activeCampaign || '') ? null : activeCampaign,
            loading: false
          });
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to bulk delete', loading: false });
          throw error;
        }
      }
    }),
    {
      name: 'enhanced-campaign-store'
    }
  )
);

// Selectors
export const useCampaign = (id: string) => {
  return useEnhancedCampaignStore(state => state.campaigns[id]);
};

export const useCampaigns = () => {
  return useEnhancedCampaignStore(state => Object.values(state.campaigns));
};

export const useActiveCampaign = () => {
  const activeId = useEnhancedCampaignStore(state => state.activeCampaign);
  const campaigns = useEnhancedCampaignStore(state => state.campaigns);
  return activeId ? campaigns[activeId] : null;
};

export const useCampaignMoves = (campaignId: string) => {
  const campaigns = useEnhancedCampaignStore(state => state.campaigns);
  const moves = useEnhancedCampaignStore(state => state.moves);
  const campaign = campaigns[campaignId];

  if (!campaign) return [];

  return campaign.moves.map(moveId => moves[moveId]).filter(Boolean);
};

export const usePlays = () => {
  return useEnhancedCampaignStore(state => Object.values(state.plays));
};
