"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, X, Megaphone, Plus, AlertTriangle, ArrowRight, CheckCircle, Mail, MousePointerClick, Globe, Linkedin, Twitter, Instagram, type Icon } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 20: Channel Mapping (Smart Strategy)

   PURPOSE: "No Scroll" Channel Matrix.
   - 3 Buckets: Primary, Secondary, Tertiary.
   - Pre-filled based on ICP (e.g. LinkedIn for B2B).
   - "Not Recommended" Logic (e.g. TikTok for Enterprise).
   - Own Owned Channels (Newsletter logic).
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface Channel {
    id: string;
    name: string;
    icon?: any;
    tier: "primary" | "secondary" | "tertiary" | "avoid";
    isOwned?: boolean; // Website, Newsletter
}

const ALL_CHANNELS: Channel[] = [
    { id: "linkedin", name: "LinkedIn Personal", tier: "primary" },
    { id: "twitter", name: "Twitter / X", tier: "primary" },
    { id: "newsletter", name: "Newsletter (Owned)", tier: "primary", isOwned: true },
    { id: "seo", name: "SEO / Blog", tier: "secondary", isOwned: true },
    { id: "youtube", name: "YouTube", tier: "secondary" },
    { id: "cold_email", name: "Cold Email", tier: "secondary" },
    { id: "ads", name: "Paid Ads", tier: "avoid" },
    { id: "tiktok", name: "TikTok / Reels", tier: "avoid" },
    { id: "events", name: "Physical Events", tier: "avoid" },
];

export default function Step20ChannelMapping() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(20)?.data as any; // Map to 20
    const step9Data = getStepById(9)?.data as any; // Strategy: 'bold' (Category Creator) vs 'safe'
    const strategy = step9Data?.selectedPath || "bold";

    const [channels, setChannels] = useState<Channel[]>(stepData?.channels || []);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Initial Logic: Filter Channels based on Strategy
    useEffect(() => {
        if (channels.length > 0) return;

        let strategicChannels = [...ALL_CHANNELS];

        if (strategy === "bold") {
            // Category Creators need long-form narrative -> Newsletter/LinkedIn
            // Avoid Ads (too expensive for education)
            strategicChannels = strategicChannels.map(c => {
                if (c.id === 'newsletter') return { ...c, tier: 'primary' };
                if (c.id === 'ads') return { ...c, tier: 'avoid' };
                return c;
            });
        } else {
            // Better Options can use Ads
            strategicChannels = strategicChannels.map(c => {
                if (c.id === 'ads') return { ...c, tier: 'secondary' };
                if (c.id === 'newsletter') return { ...c, tier: 'tertiary' }; // Less need for deep education
                return c;
            });
        }
        setChannels(strategicChannels);
    }, [strategy, channels.length]);


    const handleMove = (id: string, toTier: Channel["tier"]) => {
        const channel = channels.find(c => c.id === id);
        if (!channel) return;

        // Validation Logic
        if (toTier === "primary" && channel.tier === "avoid") {
            toast.warning("Strategic Mismatch", {
                description: `${channel.name} is usually ineffective for this strategy. Proceed with caution.`,
                icon: <AlertTriangle size={16} className="text-[var(--warning)]" />
            });
        }

        setChannels(channels.map(c => c.id === id ? { ...c, tier: toTier } : c));
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(20, { channels, confirmed: true });
        updateStepStatus(20, "complete");
    };

    const categories = [
        { id: "primary", label: "Primary (80% Focus)", color: "var(--blueprint)" },
        { id: "secondary", label: "Secondary (Support)", color: "var(--success)" },
        { id: "tertiary", label: "Tertiary (Experiment)", color: "var(--muted)" },
    ];

    return (
        <div ref={containerRef} className="h-full flex flex-col max-w-6xl mx-auto space-y-6 pb-6">

            {/* Header */}
            <div className="text-center space-y-2 shrink-0">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 20 / 23</span>
                <h2 className="font-serif text-2xl text-[var(--ink)]">Channel Architecture</h2>
                <div className="flex items-center justify-center gap-2 text-[var(--secondary)]">
                    <Megaphone size={14} />
                    <span className="font-serif italic text-sm">"Where will we fight?"</span>
                </div>
            </div>

            {/* Matrix Grid */}
            <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">

                {categories.map((cat) => (
                    <div key={cat.id} className="flex flex-col bg-[var(--canvas)] rounded border border-[var(--border-subtle)] h-full">
                        <div className="p-4 border-b border-[var(--border-subtle)] bg-[var(--paper)]">
                            <div className="font-technical text-[10px] uppercase tracking-widest mb-1" style={{ color: cat.color }}>{cat.label}</div>
                        </div>

                        <div className="flex-1 p-3 space-y-2 overflow-y-auto min-h-[200px]">
                            {channels.filter(c => c.tier === cat.id).map(c => (
                                <div key={c.id} className="p-3 bg-[var(--paper)] rounded shadow-sm border border-[var(--border)] flex items-center justify-between group">
                                    <span className="font-serif text-sm">{c.name}</span>
                                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        {/* Move Buttons */}
                                        {cat.id !== "primary" && <button onClick={() => handleMove(c.id, "primary")} className="p-1 hover:bg-[var(--border-subtle)] rounded text-[var(--blueprint)]" title="Move Up"><ArrowRight className="rotate-[-90deg]" size={12} /></button>}
                                        {cat.id !== "tertiary" && <button onClick={() => handleMove(c.id, "tertiary")} className="p-1 hover:bg-[var(--border-subtle)] rounded text-[var(--muted)]" title="Move Down"><ArrowRight className="rotate-90" size={12} /></button>}
                                        <button onClick={() => handleMove(c.id, "avoid")} className="p-1 hover:bg-[var(--border-subtle)] rounded text-[var(--error)]" title="Remove"><X size={12} /></button>
                                    </div>
                                </div>
                            ))}
                            {channels.filter(c => c.tier === cat.id).length === 0 && (
                                <div className="text-center py-8 text-[var(--muted)] text-xs italic opacity-50">Empty Slot</div>
                            )}
                        </div>
                    </div>
                ))}

            </div>

            {/* Unused / Avoid Bank */}
            <div className="border border-[var(--border)] rounded bg-[var(--paper)] p-4 shrink-0">
                <div className="text-xs font-technical uppercase text-[var(--muted)] mb-3">Available / Not Recommended</div>
                <div className="flex flex-wrap gap-2">
                    {channels.filter(c => c.tier === "avoid").map(c => (
                        <button
                            key={c.id}
                            onClick={() => handleMove(c.id, "secondary")}
                            className="px-3 py-1.5 rounded border border-[var(--border)] text-xs bg-[var(--canvas)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors flex items-center gap-2"
                        >
                            <span>{c.name}</span> <Plus size={10} />
                        </button>
                    ))}
                    <button className="px-3 py-1.5 rounded border border-dashed border-[var(--border)] text-xs text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
                        + Custom Channel
                    </button>
                </div>
            </div>

            {/* Footer */}
            <div className="flex justify-center pt-4 h-16 shrink-0">
                {!confirmed ? (
                    <BlueprintButton onClick={handleConfirm} size="lg" className="px-12">
                        <Check size={14} /> Confirm Channel Mix
                    </BlueprintButton>
                ) : (
                    <div className="flex items-center gap-2 text-[var(--success)]">
                        <CheckCircle size={20} /> <span className="font-medium text-sm">Channels Locked</span>
                    </div>
                )}
            </div>
        </div>
    );
}
