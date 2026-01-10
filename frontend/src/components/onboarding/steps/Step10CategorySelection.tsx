"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Target, Lightbulb, Crown, Sparkles, AlertTriangle, TrendingUp, Users, DollarSign, Clock } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 10: Category Selection
   "Choose your destiny" - Pokémon-style market category selection
   ══════════════════════════════════════════════════════════════════════════════ */

interface CategoryOption {
    id: string;
    type: "traditional" | "twist" | "new";
    name: string;
    tagline: string;
    description: string;
    pros: string[];
    cons: string[];
    stats: {
        marketingEffort: number;  // 1-10
        buyerEducation: number;   // 1-10
        competitionLevel: number; // 1-10
        pricingPower: number;     // 1-10
    };
    implications: {
        competitors: string;
        buyers: string;
        marketing: string;
    };
    code: string;
}

const CATEGORY_OPTIONS: CategoryOption[] = [
    {
        id: "1",
        type: "traditional",
        name: "Established Category",
        tagline: "Join an existing market",
        description: "Position yourself within a well-defined, existing category. Buyers already know what this is and where to find it.",
        pros: ["Instant recognition", "Clear buyer path", "Established demand", "Easier SEO"],
        cons: ["Crowded market", "Feature comparison trap", "Price pressure", "Hard to stand out"],
        stats: { marketingEffort: 5, buyerEducation: 2, competitionLevel: 9, pricingPower: 4 },
        implications: {
            competitors: "You'll be compared directly to established players. Every feature gets benchmarked.",
            buyers: "Buyers know what to expect. They'll evaluate you on familiar criteria.",
            marketing: "Focus on differentiation. Why are you better than the alternatives?"
        },
        code: "CAT-01"
    },
    {
        id: "2",
        type: "twist",
        name: "Category with a Twist",
        tagline: "Familiar but different",
        description: "Take an existing category and add a compelling differentiator. Best of both worlds: recognition + differentiation.",
        pros: ["Familiar yet fresh", "Trend-aligned", "Premium positioning", "Clear comparison point"],
        cons: ["Must prove the twist matters", "Competitors can copy", "Messaging complexity"],
        stats: { marketingEffort: 6, buyerEducation: 4, competitionLevel: 6, pricingPower: 7 },
        implications: {
            competitors: "You'll reframe the competition. 'Like X, but with Y' becomes your positioning.",
            buyers: "Buyers get a reference point but understand you're different. Easier to justify premium.",
            marketing: "Lead with the twist. Make the differentiator the hero of every message."
        },
        code: "CAT-02"
    },
    {
        id: "3",
        type: "new",
        name: "New Category",
        tagline: "Create your own market",
        description: "Define an entirely new category. Highest risk, highest reward. If successful, you become the category leader.",
        pros: ["Category king potential", "No direct competition", "Premium pricing", "Thought leadership"],
        cons: ["Heavy education burden", "Longer sales cycle", "Market creation cost", "Timing risk"],
        stats: { marketingEffort: 10, buyerEducation: 10, competitionLevel: 1, pricingPower: 10 },
        implications: {
            competitors: "You have no direct competitors... yet. But you're competing against the status quo.",
            buyers: "Buyers need to be taught why this category matters before they look for solutions.",
            marketing: "Content-heavy, evangelist-driven. You're not selling a product—you're selling a movement."
        },
        code: "CAT-03"
    },
];

// Stat bar component
function StatBar({ label, value, icon: Icon, color }: { label: string; value: number; icon: React.ElementType; color: string }) {
    return (
        <div className="flex items-center gap-2">
            <Icon size={12} strokeWidth={1.5} className={color} />
            <span className="font-technical text-[8px] text-[var(--muted)] w-20">{label}</span>
            <div className="flex-1 h-2 bg-[var(--border)] rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-500 ${color.replace('text-', 'bg-')}`}
                    style={{ width: `${value * 10}%` }}
                />
            </div>
            <span className="font-technical text-[10px] text-[var(--ink)] w-4">{value}</span>
        </div>
    );
}

export default function Step10CategorySelection() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(10)?.data as { selectedCategory?: string; rationale?: string; confirmed?: boolean } | undefined;

    const [selectedCategory, setSelectedCategory] = useState(stepData?.selectedCategory || "");
    const [rationale, setRationale] = useState(stepData?.rationale || "");
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [showImplications, setShowImplications] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const cardsRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    // Animate card selection
    const handleSelect = (id: string) => {
        setSelectedCategory(id);
        updateStepData(10, { selectedCategory: id, rationale });

        // Animate selected card
        if (cardsRef.current) {
            const cards = cardsRef.current.querySelectorAll("[data-card]");
            cards.forEach((card, i) => {
                const cardId = CATEGORY_OPTIONS[i].id;
                if (cardId === id) {
                    gsap.fromTo(card,
                        { scale: 1 },
                        { scale: 1.02, duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out" }
                    );
                }
            });
        }

        // Show implications after a brief delay
        setTimeout(() => setShowImplications(true), 300);
    };

    const handleConfirm = () => {
        if (!selectedCategory || !rationale.trim()) return;
        setConfirmed(true);
        updateStepData(10, { selectedCategory, rationale, confirmed: true });
        updateStepStatus(10, "complete");
    };

    const selected = CATEGORY_OPTIONS.find((o) => o.id === selectedCategory);

    const typeConfig = {
        traditional: {
            icon: Target,
            color: "text-[var(--muted)]",
            bg: "bg-[var(--canvas)]",
            border: "border-[var(--border)]",
            glow: "shadow-none",
            label: "THE SAFE PATH"
        },
        twist: {
            icon: Lightbulb,
            color: "text-[var(--blueprint)]",
            bg: "bg-[var(--blueprint-light)]",
            border: "border-[var(--blueprint)]",
            glow: "shadow-[0_0_20px_rgba(var(--blueprint-rgb),0.2)]",
            label: "THE CLEVER PLAY"
        },
        new: {
            icon: Crown,
            color: "text-[var(--warning)]",
            bg: "bg-[var(--warning-light)]",
            border: "border-[var(--warning)]",
            glow: "shadow-[0_0_20px_rgba(var(--warning-rgb),0.3)]",
            label: "THE BOLD MOVE"
        },
    };

    return (
        <div ref={containerRef} className="space-y-8">
            {/* Hero intro */}
            <div data-animate className="text-center py-4">
                <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">Choose Your Category Strategy</h2>
                <p className="text-sm text-[var(--secondary)] max-w-lg mx-auto">
                    This decision shapes how buyers discover you, how competitors respond, and how you'll price your offering. Choose wisely.
                </p>
            </div>

            {/* Category Cards - Trading Card Layout */}
            <div ref={cardsRef} data-animate className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {CATEGORY_OPTIONS.map((option) => {
                    const config = typeConfig[option.type];
                    const ConfigIcon = config.icon;
                    const isSelected = selectedCategory === option.id;

                    return (
                        <div
                            key={option.id}
                            data-card
                            onClick={() => handleSelect(option.id)}
                            className={`relative cursor-pointer transition-all duration-300 ${isSelected ? config.glow : ""}`}
                        >
                            {/* Card Frame */}
                            <div className={`
                                relative rounded-[var(--radius-md)] overflow-hidden
                                border-2 transition-all duration-300
                                ${isSelected ? config.border : "border-[var(--border)] hover:border-[var(--blueprint)]"}
                                ${isSelected ? "ring-2 ring-offset-2 ring-offset-[var(--paper)]" : ""}
                                ${isSelected ? (option.type === "new" ? "ring-[var(--warning)]" : option.type === "twist" ? "ring-[var(--blueprint)]" : "ring-[var(--muted)]") : "ring-transparent"}
                            `}>
                                {/* Card Header */}
                                <div className={`p-4 ${isSelected ? config.bg : "bg-[var(--canvas)]"} border-b border-[var(--border-subtle)]`}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className={`font-technical text-[9px] ${config.color}`}>{config.label}</span>
                                        <span className="font-technical text-[9px] text-[var(--muted)]">{option.code}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className={`w-12 h-12 rounded-[var(--radius-sm)] ${config.bg} border ${config.border} flex items-center justify-center`}>
                                            <ConfigIcon size={24} strokeWidth={1.5} className={config.color} />
                                        </div>
                                        <div>
                                            <h3 className="text-base font-semibold text-[var(--ink)]">{option.name}</h3>
                                            <p className="text-xs text-[var(--secondary)]">{option.tagline}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Card Body */}
                                <div className="p-4 bg-[var(--paper)]">
                                    <p className="text-xs text-[var(--secondary)] mb-4 min-h-[3em]">{option.description}</p>

                                    {/* Stats */}
                                    <div className="space-y-2 mb-4">
                                        <StatBar label="EFFORT" value={option.stats.marketingEffort} icon={TrendingUp} color="text-[var(--error)]" />
                                        <StatBar label="EDUCATION" value={option.stats.buyerEducation} icon={Users} color="text-[var(--warning)]" />
                                        <StatBar label="COMPETITION" value={option.stats.competitionLevel} icon={Target} color="text-[var(--blueprint)]" />
                                        <StatBar label="PRICING" value={option.stats.pricingPower} icon={DollarSign} color="text-[var(--success)]" />
                                    </div>

                                    {/* Pros/Cons condensed */}
                                    <div className="grid grid-cols-2 gap-2 pt-3 border-t border-[var(--border-subtle)]">
                                        <div>
                                            <span className="font-technical text-[8px] text-[var(--success)] block mb-1">PROS</span>
                                            {option.pros.slice(0, 2).map((p, i) => (
                                                <p key={i} className="text-[10px] text-[var(--secondary)] flex items-start gap-1">
                                                    <Check size={8} strokeWidth={1.5} className="text-[var(--success)] mt-0.5 flex-shrink-0" />{p}
                                                </p>
                                            ))}
                                        </div>
                                        <div>
                                            <span className="font-technical text-[8px] text-[var(--warning)] block mb-1">CONS</span>
                                            {option.cons.slice(0, 2).map((c, i) => (
                                                <p key={i} className="text-[10px] text-[var(--secondary)] flex items-start gap-1">
                                                    <AlertTriangle size={8} strokeWidth={1.5} className="text-[var(--warning)] mt-0.5 flex-shrink-0" />{c}
                                                </p>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* Selection indicator */}
                                {isSelected && (
                                    <div className="absolute top-3 right-3">
                                        <div className={`w-8 h-8 rounded-full ${option.type === "new" ? "bg-[var(--warning)]" : option.type === "twist" ? "bg-[var(--blueprint)]" : "bg-[var(--ink)]"} flex items-center justify-center animate-pulse`}>
                                            <Check size={16} strokeWidth={2} className="text-[var(--paper)]" />
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Implications - What this means for you */}
            {selected && showImplications && (
                <BlueprintCard data-animate figure="FIG. 01" title="What This Means For You" code="IMPL" showCorners padding="md">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-3 rounded-[var(--radius-sm)] bg-[var(--error-light)] border border-[var(--error)]/20">
                            <span className="font-technical text-[9px] text-[var(--error)] block mb-2">COMPETITORS</span>
                            <p className="text-xs text-[var(--ink)]">{selected.implications.competitors}</p>
                        </div>
                        <div className="p-3 rounded-[var(--radius-sm)] bg-[var(--blueprint-light)] border border-[var(--blueprint)]/20">
                            <span className="font-technical text-[9px] text-[var(--blueprint)] block mb-2">BUYERS</span>
                            <p className="text-xs text-[var(--ink)]">{selected.implications.buyers}</p>
                        </div>
                        <div className="p-3 rounded-[var(--radius-sm)] bg-[var(--success-light)] border border-[var(--success)]/20">
                            <span className="font-technical text-[9px] text-[var(--success)] block mb-2">MARKETING</span>
                            <p className="text-xs text-[var(--ink)]">{selected.implications.marketing}</p>
                        </div>
                    </div>
                </BlueprintCard>
            )}

            {/* Rationale */}
            {selectedCategory && (
                <BlueprintCard data-animate figure="FIG. 02" title="Your Rationale" code="WHY" showCorners padding="md">
                    <p className="text-xs text-[var(--secondary)] mb-3">
                        Explain why this category strategy fits your business. This helps ensure alignment across your team.
                    </p>
                    <textarea
                        value={rationale}
                        onChange={(e) => {
                            setRationale(e.target.value);
                            updateStepData(10, { selectedCategory, rationale: e.target.value });
                        }}
                        placeholder="We're choosing this category because..."
                        className="w-full min-h-[100px] p-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                    />
                </BlueprintCard>
            )}

            {/* Confirm */}
            {!confirmed && selectedCategory && rationale.trim() && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                    <Sparkles size={14} strokeWidth={1.5} />Lock In Category Strategy
                </BlueprintButton>
            )}

            {confirmed && selected && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-[var(--success)] flex items-center justify-center">
                            <Check size={24} strokeWidth={2} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="text-base font-serif text-[var(--ink)]">{selected.name}</span>
                            <p className="font-technical text-[var(--success)]">CATEGORY STRATEGY LOCKED</p>
                        </div>
                        <BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">CATEGORY-SELECTION • STEP 10/25</span>
            </div>
        </div>
    );
}
