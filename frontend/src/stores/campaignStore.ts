/* ══════════════════════════════════════════════════════════════════════════════
   CAMPAIGN STORE
   Global state for Campaign Command Center 2.0
   Manages campaigns, moves, and kanban state
   ══════════════════════════════════════════════════════════════════════════════ */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "@/lib/api/client";

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

export interface CampaignStoreState {
    campaigns: Campaign[];
    activeCampaignId: string | null;
    view: "LIST" | "DETAIL" | "WIZARD";

    // Actions
    setActiveCampaign: (id: string | null) => void;
    setView: (view: "LIST" | "DETAIL" | "WIZARD") => void;
    addCampaign: (campaign: any) => Promise<void>;
    updateCampaignMoveStatus: (campaignId: string, moveId: string, newStatus: MoveStatus) => Promise<void>;
    fetchCampaigns: () => Promise<void>;
    fetchCalendar: () => Promise<any>;

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

export const useCampaignStore = create<CampaignStoreState>()(
    persist(
        (set, get) => ({
            campaigns: INITIAL_CAMPAIGNS,
            activeCampaignId: null,
            view: "LIST",

            setActiveCampaign: (id) => set({ activeCampaignId: id }),

            setView: (view) => set({ view }),

            fetchCampaigns: async () => {
                try {
                    const response = await apiClient.listCampaigns() as any;
                    set({ campaigns: response.campaigns || [] });
                } catch (error) {
                    console.error("Fetch campaigns failed:", error);
                }
            },

            fetchCalendar: async () => {
                try {
                    const response = await apiClient.getCampaignCalendar();
                    return response;
                } catch (error) {
                    console.error("Fetch campaign calendar failed:", error);
                    return { campaigns: [], moves: [] };
                }
            },

            addCampaign: async (campaign) => {
                try {
                    const response = await apiClient.createCampaign({
                        name: campaign.name,
                        description: campaign.goal,
                        start_date: campaign.start_date,
                        end_date: campaign.end_date
                    }) as any;
                    set((state) => ({
                        campaigns: [...state.campaigns, response]
                    }));
                } catch (error) {
                    console.error("Add campaign failed:", error);
                }
            },

            updateCampaignMoveStatus: async (campaignId, moveId, newStatus) => {
                try {
                    await apiClient.updateMove(moveId, { status: newStatus.toLowerCase() });
                    await get().fetchCampaigns();
                } catch (error) {
                    console.error("Update move status failed:", error);
                }
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
