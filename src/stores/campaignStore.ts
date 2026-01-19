/* ══════════════════════════════════════════════════════════════════════════════
   CAMPAIGN STORE
   Global state for Campaign Command Center 2.0
   Manages campaigns, moves, and kanban state
   ══════════════════════════════════════════════════════════════════════════════ */

import { create } from "zustand";
import { persist } from "zustand/middleware";

// --- Types ---

export type CampaignStatus = "Active" | "Planned" | "Completed" | "Paused";
export type MoveStatus = "Planned" | "Active" | "Completed";

export interface CampaignMove {
    id: string;
    title: string;
    type: string; // e.g. "Positioning", "Proof", "Outreach"
    status: MoveStatus;
    start: string;
    end: string;
    items_done: number;
    items_total: number;
    desc: string;
}

export interface Campaign {
    id: string;
    name: string;
    status: CampaignStatus;
    progress: number;
    goal: string;
    moves: CampaignMove[];
}

export interface CampaignStore {
    campaigns: Campaign[];
    activeCampaignId: string | null;
    view: "LIST" | "DETAIL" | "WIZARD";
    isLoading: boolean;
    error: string | null;

    // Actions
    setActiveCampaign: (id: string | null) => void;
    setView: (view: "LIST" | "DETAIL" | "WIZARD") => void;
    fetchCampaigns: (workspaceId: string) => Promise<void>;
    addCampaign: (campaign: Campaign) => void;
    updateCampaignMoveStatus: (campaignId: string, moveId: string, newStatus: MoveStatus) => void;

    // Getters
    getActiveCampaign: () => Campaign | undefined;
}

// --- Initial Data (Stub from Enterprise Definition) ---
const INITIAL_CAMPAIGNS: Campaign[] = [
    {
        id: "CMP-001",
        name: "Q1 Market Entry",
        status: "Active",
        progress: 35,
        goal: "Establish Category Dominance",
        moves: [
            { id: "M-101", title: "The Manifesto", type: "Positioning", status: "Completed", start: "Jan 1", end: "Jan 14", items_done: 2, items_total: 2, desc: "Define core enemy and value prop." },
            { id: "M-102", title: "Evidence Stack", type: "Proof", status: "Active", start: "Jan 15", end: "Jan 30", items_done: 3, items_total: 5, desc: "Gather case studies and data points." },
            { id: "M-105", title: "Beta User Outreach", type: "Outreach", status: "Active", start: "Jan 20", end: "Feb 5", items_done: 12, items_total: 50, desc: "Direct outreach to top 50 ICPs." },
            { id: "M-103", title: "Content Flood", type: "Volume", status: "Planned", start: "Feb 1", end: "Feb 14", items_done: 0, items_total: 20, desc: "High volume content distribution." },
            { id: "M-104", title: "Velvet Rope", type: "Friction", status: "Planned", start: "Feb 15", end: "Feb 28", items_done: 0, items_total: 1, desc: "Launch waitlist page." }
        ]
    }
];

export const useCampaignStore = create<CampaignStore>()(
    persist(
        (set, get) => ({
            campaigns: [],
            activeCampaignId: null,
            view: "LIST",
            isLoading: false,
            error: null,

            setActiveCampaign: (id) => set({ activeCampaignId: id }),

            setView: (view) => set({ view }),

            fetchCampaigns: async (workspaceId) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/?workspace_id=${workspaceId}`);
                    if (!response.ok) throw new Error("Failed to fetch campaigns");

                    const data = await response.json();

                    // Map backend data to frontend interface
                    const mappedCampaigns: Campaign[] = data.campaigns.map((c: any) => ({
                        id: c.id,
                        name: c.name,
                        status: c.status === "planning" ? "Planned" : c.status === "active" ? "Active" : c.status === "completed" ? "Completed" : "Paused",
                        progress: c.progress || 0, // Backend might calculate this
                        goal: c.description || "Goal not defined", // Mapping description to goal if goal missing
                        moves: (c.moves || []).map((m: any) => ({
                            id: m.id,
                            title: m.name,
                            type: m.category || "General",
                            status: m.status === "completed" ? "Completed" : m.status === "active" ? "Active" : "Planned",
                            start: m.start_date || "TBD",
                            end: m.end_date || "TBD",
                            items_done: 0,
                            items_total: (m.execution || []).length,
                            desc: m.description || ""
                        }))
                    }));

                    set({ campaigns: mappedCampaigns, isLoading: false });
                } catch (e: any) {
                    console.error("Error fetching campaigns:", e);
                    set({ error: e.message, isLoading: false, campaigns: [] });
                    // Fallback to empty instead of initial stub to avoid confusion
                }
            },

            addCampaign: (campaign) => set((state) => ({
                campaigns: [...state.campaigns, campaign]
            })),

            updateCampaignMoveStatus: (campaignId, moveId, newStatus) => {
                set((state) => ({
                    campaigns: state.campaigns.map(c => {
                        if (c.id !== campaignId) return c;

                        const updatedMoves = c.moves.map(m =>
                            m.id === moveId ? { ...m, status: newStatus } : m
                        );

                        const totalMoves = updatedMoves.length;
                        const completedMoves = updatedMoves.filter(m => m.status === "Completed").length;
                        const progress = totalMoves > 0 ? Math.round((completedMoves / totalMoves) * 100) : 0;

                        return {
                            ...c,
                            moves: updatedMoves,
                            progress
                        };
                    })
                }));
            },

            getActiveCampaign: () => {
                const { campaigns, activeCampaignId } = get();
                return campaigns.find(c => c.id === activeCampaignId);
            }
        }),
        {
            name: "raptorflow-campaign-storage",
            partialize: (state) => ({ campaigns: state.campaigns }),
        }
    )
);
