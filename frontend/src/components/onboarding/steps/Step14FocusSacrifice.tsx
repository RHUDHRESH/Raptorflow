"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, X, Sparkles, CheckCircle, Lock, Info, Lightbulb, Loader2 } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 14: Focus & Sacrifice (Smart Logic)
   
   PURPOSE: "No Scroll" Decision Grid with STRATEGIC LOGIC.
   - Forces choices based on Step 9 (Category Path).
   - "David vs Goliath" -> MUST Focus on 'Early Stage', MUST Sacrifice 'Enterprise'.
   - Shows "Why" (Contextual Help).
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface FocusItem {
    id: string;
    category: string;
    item: string;
    decision: "focus" | "sacrifice" | null;
    forcedDecision?: "focus" | "sacrifice"; // If set, user cannot change
    reason?: string; // Why it's forced
}

const BASE_ITEMS: FocusItem[] = [
    { id: "1", category: "Audience", item: "Enterprise (1000+)", decision: null },
    { id: "2", category: "Audience", item: "Early-Stage Founders", decision: null },
    { id: "3", category: "Product", item: "Custom Reporting", decision: null },
    { id: "4", category: "Product", item: "Speed / Automation", decision: null },
    { id: "5", category: "Channels", item: "Content / SEO", decision: null },
    { id: "6", category: "Channels", item: "Outbound Sales", decision: null },
];

function DecisionTile({
    item,
    onDecide
}: {
    item: FocusItem;
    onDecide: (decision: "focus" | "sacrifice") => void;
}) {
    const isFocus = item.decision === "focus";
    const isSacrifice = item.decision === "sacrifice";
    const isForced = !!item.forcedDecision;

    return (
        <div className={cn(
            "relative p-4 rounded border transition-all duration-300 flex flex-col items-center justify-between text-center group h-full select-none",
            isFocus ? "bg-[var(--success)]/5 border-[var(--success)]" :
                isSacrifice ? "bg-[var(--error)]/5 border-[var(--error)]" :
                    "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)] hover:shadow-md"
        )}>
            {/* Forced Lock Indicator */}
            {isForced && (
                <div className="absolute top-2 right-2 text-[var(--muted)]" title="Strategic Constraint">
                    <Lock size={12} />
                </div>
            )}

            <div className="flex-1 w-full flex flex-col items-center justify-center space-y-2 mb-4">
                <span className="font-technical text-[9px] uppercase tracking-wider text-[var(--muted)]">{item.category}</span>
                <h4 className="font-serif text-lg leading-tight text-[var(--ink)]">{item.item}</h4>

                {/* Status Indicator */}
                {isFocus && <span className="font-technical text-[9px] text-[var(--success)] bg-[var(--success)]/10 px-2 py-0.5 rounded">FOCUSED</span>}
                {isSacrifice && <span className="font-technical text-[9px] text-[var(--error)] bg-[var(--error)]/10 px-2 py-0.5 rounded">SACRIFICED</span>}

                {/* Forced Reason */}
                {isForced && (
                    <div className="mt-2 text-[10px] text-[var(--secondary)] italic max-w-[90%] bg-[var(--canvas)] p-1.5 rounded border border-[var(--border-subtle)] flex items-start gap-1">
                        <Info size={10} className="shrink-0 mt-0.5" />
                        "{item.reason}"
                    </div>
                )}
            </div>

            {/* Actions */}
            <div className="flex w-full gap-2 opacity-100 transition-opacity">
                <button
                    onClick={() => onDecide("focus")}
                    disabled={isForced && item.forcedDecision !== "focus" || isFocus}
                    className={cn(
                        "flex-1 py-1.5 rounded text-[10px] uppercase font-bold tracking-wider transition-all border",
                        isFocus
                            ? "bg-[var(--success)] text-[var(--paper)] border-[var(--success)] cursor-default"
                            : (isForced && item.forcedDecision !== "focus")
                                ? "bg-[var(--canvas)] text-[var(--placeholder)] border-[var(--border-subtle)] cursor-not-allowed opacity-50"
                                : "bg-[var(--canvas)] text-[var(--ink)] border-[var(--border)] hover:bg-[var(--success)] hover:text-[var(--paper)] hover:border-[var(--success)]"
                    )}
                >
                    Focus
                </button>
                <button
                    onClick={() => onDecide("sacrifice")}
                    disabled={isForced && item.forcedDecision !== "sacrifice" || isSacrifice}
                    className={cn(
                        "flex-1 py-1.5 rounded text-[10px] uppercase font-bold tracking-wider transition-all border",
                        isSacrifice
                            ? "bg-[var(--error)] text-[var(--paper)] border-[var(--error)] cursor-default"
                            : (isForced && item.forcedDecision !== "sacrifice")
                                ? "bg-[var(--canvas)] text-[var(--placeholder)] border-[var(--border-subtle)] cursor-not-allowed opacity-50"
                                : "bg-[var(--canvas)] text-[var(--ink)] border-[var(--border)] hover:bg-[var(--error)] hover:text-[var(--paper)] hover:border-[var(--error)]"
                    )}
                >
                    Cut
                </button>
            </div>
        </div>
    );
}

interface AIInsight {
    icon: string;
    title: string;
    insight: string;
    source: string;
}

export default function Step14FocusSacrifice() {
    const { updateStepData, updateStepStatus, getStepById, session } = useOnboardingStore();

    // Get Strategy Source (Step 9)
    const step9Data = getStepById(9)?.data as any; // { selectedPath: 'safe' | 'clever' | 'bold' ... }
    const strategy = step9Data?.selectedPath || "bold"; // usage fallback

    const stepData = getStepById(14)?.data as any;

    const [items, setItems] = useState<FocusItem[]>([]);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
    const [isLoadingInsights, setIsLoadingInsights] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Fetch AI insights on mount
    useEffect(() => {
        const fetchAIInsights = async () => {
            setIsLoadingInsights(true);
            try {
                const response = await fetch('/api/onboarding/focus-sacrifice', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: session?.sessionId || 'demo',
                        company_info: getStepById(4)?.data || {},
                        icp_data: getStepById(15)?.data || {},
                        capabilities: getStepById(10)?.data?.capabilities || [],
                        positioning: getStepById(9)?.data || {}
                    })
                });
                
                const data = await response.json();
                if (data.success && data.focus_sacrifice?.lightbulb_insights) {
                    setAiInsights(data.focus_sacrifice.lightbulb_insights);
                }
            } catch (err) {
                console.error('Failed to fetch AI insights:', err);
            } finally {
                setIsLoadingInsights(false);
            }
        };
        
        fetchAIInsights();
    }, [session?.sessionId]);

    // Initialize Items with Logic
    useEffect(() => {
        if (items.length > 0) return; // Prevent re-init if state exists

        let smartItems = [...BASE_ITEMS];

        if (strategy === "bold") { // "The Category Creator" / "David"
            smartItems = smartItems.map(i => {
                if (i.item.includes("Enterprise")) return { ...i, decision: "sacrifice", forcedDecision: "sacrifice", reason: "Category creators can't survive long sales cycles." };
                if (i.item.includes("Early-Stage")) return { ...i, decision: "focus", forcedDecision: "focus", reason: "You need agile adopters who tolerate risk." };
                if (i.item.includes("Custom Reporting")) return { ...i, decision: "sacrifice", forcedDecision: "sacrifice", reason: "Too much engineering debt for now." };
                return i;
            });
        } else if (strategy === "safe") { // "The Better Option" / "Goliath"
            smartItems = smartItems.map(i => {
                if (i.item.includes("Enterprise")) return { ...i, decision: "focus", forcedDecision: "focus", reason: "Better Options win on specs for big buyers." };
                if (i.item.includes("Early-Stage")) return { ...i, decision: "sacrifice", forcedDecision: "sacrifice", reason: "Startups can't afford 'Better', they need 'Different'." };
                return i;
            });
        }

        // Merge with existing data if any (preserve manual choices)
        if (stepData?.items) {
            // We prioritize the smart logic for *forced* items, but respect saved manual choices for others
            const merged = smartItems.map(smart => {
                const saved = stepData.items.find((s: FocusItem) => s.id === smart.id);
                if (saved && !smart.forcedDecision) return saved;
                return smart;
            });
            setItems(merged);
        } else {
            setItems(smartItems);
        }

    }, [strategy, stepData?.items]); // Runs once effectively

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll(".animate-in"),
            { opacity: 0, scale: 0.95 },
            { opacity: 1, scale: 1, duration: 0.4, stagger: 0.05, ease: "back.out(1.2)" }
        );
    }, [items]); // Anim on items load

    const handleDecide = (id: string, decision: "focus" | "sacrifice") => {
        const item = items.find(i => i.id === id);
        if (item?.forcedDecision) return; // double check

        const updated = items.map(i => i.id === id ? { ...i, decision } : i);
        setItems(updated);
        // Auto-update store on interaction? No, wait for confirmation or distinct save.
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(14, { items, confirmed: true });
        updateStepStatus(14, "complete");
    };

    const undecidedCount = items.filter(i => !i.decision).length;
    const focusCount = items.filter(i => i.decision === "focus").length;
    const sacrificeCount = items.filter(i => i.decision === "sacrifice").length;

    if (items.length === 0) return null; // Loading...

    return (
        <div ref={containerRef} className="h-full flex flex-col pb-6">

            {/* Header */}
            <div className="text-center space-y-2 mb-8 shrink-0">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 14 / 24</span>
                <h2 className="font-serif text-2xl text-[var(--ink)]">Focus & Sacrifice</h2>
                <div className="flex justify-center gap-6 text-xs text-[var(--secondary)] font-serif italic">
                    <span className={cn(focusCount > 0 && "text-[var(--success)]")}>Focused: {focusCount}</span>
                    <span className="w-px h-4 bg-[var(--border)]" />
                    <span className={cn(sacrificeCount > 0 && "text-[var(--error)]")}>Sacrificed: {sacrificeCount}</span>
                </div>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 auto-rows-fr">
                {items.map((item) => (
                    <div key={item.id} className="animate-in h-40">
                        <DecisionTile item={item} onDecide={(d) => handleDecide(item.id, d)} />
                    </div>
                ))}
            </div>

            {/* Footer Action */}
            <div className="mt-auto pt-6 flex justify-center h-16 shrink-0">
                {undecidedCount === 0 && !confirmed && (
                    <div className="animate-in zoom-in">
                        <BlueprintButton onClick={handleConfirm} size="lg" className="px-12">
                            <Sparkles size={14} /> Lock Strategic Focus
                        </BlueprintButton>
                    </div>
                )}
                {confirmed && (
                    <div className="flex items-center gap-2 text-[var(--success)] animate-in">
                        <CheckCircle size={20} /> <span className="font-medium">Strategy Locked</span>
                    </div>
                )}
            </div>

        </div>
    );
}
