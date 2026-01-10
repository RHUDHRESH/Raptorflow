"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, X, AlertTriangle, Target, Lightbulb, ArrowRight, HelpCircle, Sparkles } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 14: Focus & Sacrifice

   Clearer UX: Guide users through strategic trade-offs with explanations
   "What to double down on" vs "What to consciously NOT do"
   ══════════════════════════════════════════════════════════════════════════════ */

interface FocusItem {
    id: string;
    category: string;
    item: string;
    explanation: string;
    focusImplication: string;
    sacrificeImplication: string;
    decision: "focus" | "sacrifice" | null;
    code: string;
}

const INITIAL_ITEMS: FocusItem[] = [
    {
        id: "1", category: "Audience", item: "Enterprise companies (1000+ employees)",
        explanation: "Large organizations with complex buying processes and bigger budgets",
        focusImplication: "Longer sales cycles, higher ACV, need for enterprise features",
        sacrificeImplication: "Miss out on enterprise budgets, stay nimble and fast-moving",
        decision: null, code: "DEC-01"
    },
    {
        id: "2", category: "Audience", item: "Founders at early-stage startups",
        explanation: "Fast-moving individuals who need quick wins and hate complexity",
        focusImplication: "Product-led growth, self-serve focus, lower price points",
        sacrificeImplication: "Miss early adopters and evangelists, focus on established companies",
        decision: null, code: "DEC-02"
    },
    {
        id: "3", category: "Features", item: "Advanced analytics & reporting",
        explanation: "Deep insights, custom dashboards, data exports",
        focusImplication: "Appeal to data-driven buyers, longer build time",
        sacrificeImplication: "Keep product simple, faster iteration, less enterprise appeal",
        decision: null, code: "DEC-03"
    },
    {
        id: "4", category: "Features", item: "AI-powered automation",
        explanation: "Intelligent recommendations and automated workflows",
        focusImplication: "Strong differentiation, higher dev investment, AI positioning",
        sacrificeImplication: "Manual-first approach, more control for users, faster to market",
        decision: null, code: "DEC-04"
    },
    {
        id: "5", category: "Go-to-Market", item: "Content marketing & SEO",
        explanation: "Blog posts, guides, organic search traffic",
        focusImplication: "Slow burn, compounds over time, lower CAC long-term",
        sacrificeImplication: "Faster paid channels, less content creation overhead",
        decision: null, code: "DEC-05"
    },
    {
        id: "6", category: "Go-to-Market", item: "Outbound sales & partnerships",
        explanation: "Direct outreach, channel partnerships, events",
        focusImplication: "Faster revenue, relationship-driven, higher CAC",
        sacrificeImplication: "Self-serve focus, product-led acquisition",
        decision: null, code: "DEC-06"
    },
];

// Decision Card with clear implications
function DecisionCard({
    item,
    onDecide,
    showHelp,
    onToggleHelp
}: {
    item: FocusItem;
    onDecide: (decision: "focus" | "sacrifice") => void;
    showHelp: boolean;
    onToggleHelp: () => void;
}) {
    return (
        <div className={`
            rounded-[var(--radius-md)] border-2 overflow-hidden transition-all
            ${item.decision === "focus" ? "border-[var(--success)] bg-[var(--success-light)]" :
                item.decision === "sacrifice" ? "border-[var(--error)]/50 bg-[var(--error-light)]" :
                    "border-[var(--border)] bg-[var(--paper)]"}
        `}>
            {/* Main Row */}
            <div className="p-4 flex items-center gap-4">
                {/* Decision Indicator */}
                <div className={`
                    w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
                    ${item.decision === "focus" ? "bg-[var(--success)] text-[var(--paper)]" :
                        item.decision === "sacrifice" ? "bg-[var(--error)] text-[var(--paper)]" :
                            "bg-[var(--canvas)] border border-[var(--border)] text-[var(--muted)]"}
                `}>
                    {item.decision === "focus" && <Check size={18} strokeWidth={2} />}
                    {item.decision === "sacrifice" && <X size={18} strokeWidth={2} />}
                    {!item.decision && <HelpCircle size={18} strokeWidth={1.5} />}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                        <span className="font-technical text-[9px] text-[var(--muted)]">{item.code}</span>
                        <span className="font-technical text-[9px] text-[var(--blueprint)]">{item.category.toUpperCase()}</span>
                    </div>
                    <h4 className="text-sm font-semibold text-[var(--ink)]">{item.item}</h4>
                    <p className="text-xs text-[var(--secondary)]">{item.explanation}</p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                    <button
                        onClick={onToggleHelp}
                        className={`p-2 rounded-lg transition-all ${showHelp ? "bg-[var(--blueprint)] text-[var(--paper)]" : "text-[var(--muted)] hover:text-[var(--blueprint)]"}`}
                        title="Show implications"
                    >
                        <Lightbulb size={14} strokeWidth={1.5} />
                    </button>
                    <button
                        onClick={() => onDecide("focus")}
                        className={`
                            px-4 py-2 rounded-lg font-technical text-[10px] flex items-center gap-1.5 transition-all
                            ${item.decision === "focus"
                                ? "bg-[var(--success)] text-[var(--paper)]"
                                : "bg-[var(--canvas)] text-[var(--ink)] hover:bg-[var(--success)] hover:text-[var(--paper)] border border-[var(--border)]"}
                        `}
                    >
                        <Target size={12} />FOCUS
                    </button>
                    <button
                        onClick={() => onDecide("sacrifice")}
                        className={`
                            px-4 py-2 rounded-lg font-technical text-[10px] flex items-center gap-1.5 transition-all
                            ${item.decision === "sacrifice"
                                ? "bg-[var(--error)] text-[var(--paper)]"
                                : "bg-[var(--canvas)] text-[var(--ink)] hover:bg-[var(--error)] hover:text-[var(--paper)] border border-[var(--border)]"}
                        `}
                    >
                        <X size={12} />SACRIFICE
                    </button>
                </div>
            </div>

            {/* Help Panel - Implications */}
            {showHelp && (
                <div className="px-4 pb-4 pt-0">
                    <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)]">
                        <div>
                            <div className="flex items-center gap-1.5 mb-1">
                                <Check size={10} className="text-[var(--success)]" />
                                <span className="font-technical text-[8px] text-[var(--success)]">IF YOU FOCUS</span>
                            </div>
                            <p className="text-xs text-[var(--secondary)]">{item.focusImplication}</p>
                        </div>
                        <div>
                            <div className="flex items-center gap-1.5 mb-1">
                                <X size={10} className="text-[var(--error)]" />
                                <span className="font-technical text-[8px] text-[var(--error)]">IF YOU SACRIFICE</span>
                            </div>
                            <p className="text-xs text-[var(--secondary)]">{item.sacrificeImplication}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default function Step14FocusSacrifice() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(14)?.data as { items?: FocusItem[]; confirmed?: boolean } | undefined;
    const [items, setItems] = useState<FocusItem[]>(stepData?.items || INITIAL_ITEMS);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [expandedHelp, setExpandedHelp] = useState<string | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    const saveData = (updated: FocusItem[]) => {
        setItems(updated);
        updateStepData(14, { items: updated });
    };

    const setDecision = (id: string, decision: "focus" | "sacrifice") => {
        saveData(items.map((i) => (i.id === id ? { ...i, decision } : i)));
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(14, { items, confirmed: true });
        updateStepStatus(14, "complete");
    };

    const focusCount = items.filter((i) => i.decision === "focus").length;
    const sacrificeCount = items.filter((i) => i.decision === "sacrifice").length;
    const undecided = items.filter((i) => !i.decision).length;

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Header with explanation */}
            <div data-animate className="text-center py-4">
                <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">Focus & Sacrifice</h2>
                <p className="text-sm text-[var(--secondary)] max-w-lg mx-auto">
                    Great strategy means making hard choices. For each item below, decide whether to
                    <span className="text-[var(--success)] font-semibold"> FOCUS</span> (double down) or
                    <span className="text-[var(--error)] font-semibold"> SACRIFICE</span> (consciously not pursue).
                </p>
            </div>

            {/* Visual guide */}
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <div className="flex items-center justify-center gap-8">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-[var(--success)] flex items-center justify-center">
                            <Check size={14} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="font-technical text-[10px] text-[var(--success)] block">FOCUS</span>
                            <span className="text-xs text-[var(--secondary)]">Double down on this</span>
                        </div>
                    </div>
                    <ArrowRight size={18} className="text-[var(--muted)]" />
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-[var(--error)] flex items-center justify-center">
                            <X size={14} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="font-technical text-[10px] text-[var(--error)] block">SACRIFICE</span>
                            <span className="text-xs text-[var(--secondary)]">Consciously NOT pursue</span>
                        </div>
                    </div>
                </div>
                <p className="text-center text-xs text-[var(--muted)] mt-3">
                    💡 Tip: Click the lightbulb icon on any item to see implications of each choice
                </p>
            </BlueprintCard>

            {/* Summary Stats */}
            <div data-animate className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-[var(--success-light)] border border-[var(--success)]/30 text-center">
                    <span className="text-3xl font-serif text-[var(--success)]">{focusCount}</span>
                    <p className="font-technical text-[9px] text-[var(--success)]">FOCUS</p>
                </div>
                <div className="p-4 rounded-xl bg-[var(--error-light)] border border-[var(--error)]/30 text-center">
                    <span className="text-3xl font-serif text-[var(--error)]">{sacrificeCount}</span>
                    <p className="font-technical text-[9px] text-[var(--error)]">SACRIFICE</p>
                </div>
                <div className={`p-4 rounded-xl text-center ${undecided > 0 ? "bg-[var(--warning-light)] border border-[var(--warning)]/30" : "bg-[var(--canvas)] border border-[var(--border)]"}`}>
                    <span className={`text-3xl font-serif ${undecided > 0 ? "text-[var(--warning)]" : "text-[var(--muted)]"}`}>{undecided}</span>
                    <p className={`font-technical text-[9px] ${undecided > 0 ? "text-[var(--warning)]" : "text-[var(--muted)]"}`}>UNDECIDED</p>
                </div>
            </div>

            {/* Decision Cards */}
            <div data-animate className="space-y-3">
                {items.map((item) => (
                    <DecisionCard
                        key={item.id}
                        item={item}
                        onDecide={(decision) => setDecision(item.id, decision)}
                        showHelp={expandedHelp === item.id}
                        onToggleHelp={() => setExpandedHelp(expandedHelp === item.id ? null : item.id)}
                    />
                ))}
            </div>

            {/* Warning for undecided */}
            {undecided > 0 && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--warning)]/30 bg-[var(--warning-light)]">
                    <div className="flex items-center gap-3">
                        <AlertTriangle size={18} strokeWidth={1.5} className="text-[var(--warning)]" />
                        <span className="text-sm text-[var(--ink)]">
                            <strong>{undecided}</strong> decision{undecided > 1 ? "s" : ""} still needed before you can continue
                        </span>
                    </div>
                </BlueprintCard>
            )}

            {/* Confirm */}
            {!confirmed && undecided === 0 && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                    <Sparkles size={14} strokeWidth={1.5} />
                    Lock In Strategic Choices
                </BlueprintButton>
            )}

            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                            <Check size={24} strokeWidth={2} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="text-base font-serif text-[var(--ink)]">Strategic Choices Locked</span>
                            <p className="font-technical text-[10px] text-[var(--secondary)]">
                                {focusCount} focus areas • {sacrificeCount} sacrifices
                            </p>
                        </div>
                        <BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">FOCUS-SACRIFICE • STEP 14/25</span>
            </div>
        </div>
    );
}
