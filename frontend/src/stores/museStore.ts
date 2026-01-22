/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   MUSE STORE
   Global state for Content Generation artifacts
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "@/lib/api/client";

export interface MuseAsset {
    id: string;
    title: string;
    content: string;
    type: "Email" | "LinkedIn" | "Blog" | "Campaign" | "Tweet" | "Other" | "Social" | "Script";
    tags: string[];
    createdAt: string;
    source?: "BlackBox" | "Manual" | "Muse" | "Template";
    metadata?: Record<string, unknown>;
}

interface MuseStoreState {
    assets: MuseAsset[];
    addAsset: (asset: Omit<MuseAsset, "id" | "createdAt">) => void;
    updateAsset: (id: string, updates: Partial<Pick<MuseAsset, "title" | "content" | "tags" | "type" | "metadata">>) => void;
    deleteAsset: (id: string) => void;
    getAssetsByTag: (tag: string) => MuseAsset[];
}

export const useMuseStore = create<MuseStoreState>()(
    persist(
        (set, get) => ({
            assets: [
                {
                    id: "GEN-001",
                    title: "Q1 Launch Announcement",
                    content: "Subject: It's time to stop guessing.\n\nMost founders marketing is purely vibes. That ends today...",
                    type: "Email",
                    tags: ["Launch", "Q1"],
                    createdAt: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
                    source: "Manual"
                },
                {
                    id: "GEN-002",
                    title: "Why Founder Marketing Fails",
                    content: "Hot Take: You don't need a personal brand. You need a narrative weapon.",
                    type: "LinkedIn",
                    tags: ["Thought Leadership"],
                    createdAt: new Date(Date.now() - 86400000).toISOString(), // Yesterday
                    source: "Manual"
                }
            ],

            addAsset: async (asset) => {
                try {
                    const response = await apiClient.generateMuseAsset({
                        task: asset.title,
                        content_type: asset.type.toLowerCase(),
                        context: { source: asset.source }
                    }) as any;

                    set((state) => ({
                        assets: [
                            {
                                ...asset,
                                id: (response.metadata?.asset_id as string) || `GEN-${Date.now()}`,
                                content: (response.content as string) || asset.content,
                                createdAt: new Date().toISOString()
                            },
                            ...state.assets
                        ]
                    }));
                } catch (error) {
                    console.error("Muse persistence failed:", error);
                    // Fallback to local
                    set((state) => ({
                        assets: [
                            {
                                ...asset,
                                id: `GEN-${Date.now()}`,
                                createdAt: new Date().toISOString()
                            },
                            ...state.assets
                        ]
                    }));
                }
            },

            updateAsset: (id, updates) => set((state) => ({
                assets: state.assets.map((asset) =>
                    asset.id === id ? { ...asset, ...updates } : asset
                )
            })),

            deleteAsset: (id) => set((state) => ({
                assets: state.assets.filter(a => a.id !== id)
            })),

            getAssetsByTag: (tag) => {
                return get().assets.filter(a => a.tags.includes(tag));
            }
        }),
        {
            name: "raptorflow-muse-storage"
        }
    )
);
