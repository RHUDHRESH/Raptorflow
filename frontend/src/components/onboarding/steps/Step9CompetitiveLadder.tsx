"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import { Check, ArrowUp, ArrowDown, GripVertical, Plus, Trash2, Play, Target, RefreshCw } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { StepLoadingState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 9: Competitive Ladder & Attack Angles

   PURPOSE: Position yourself in the market hierarchy and find attack angles
   - Arrange competitors from premium to budget
   - Identify market leader vs challenger positions
   - Find underserved segments or value gaps
   - Generate possible differentiation themes
   ══════════════════════════════════════════════════════════════════════════════ */

// Types
interface LadderItem {
    id: string;
    name: string;
    position: number;
    isYou: boolean;
    tier: "premium" | "mid-market" | "budget" | "free";
    notes?: string;
    code: string;
}

interface AttackAngle {
    id: string;
    title: string;
    description: string;
    targetGap: string;
    viability: "high" | "medium" | "low";
}

interface LadderResult {
    ladder: LadderItem[];
    attackAngles: AttackAngle[];
    confirmed: boolean;
}

export default function Step9CompetitiveLadder() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const step8Data = getStepById(8)?.data as { alternatives?: any[] } | undefined;
    const stepData = getStepById(9)?.data as LadderResult | undefined;

    const [isGenerating, setIsGenerating] = useState(false);
    const [ladder, setLadder] = useState<LadderItem[]>(stepData?.ladder || []);
    const [attackAngles, setAttackAngles] = useState<AttackAngle[]>(stepData?.attackAngles || []);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    const hasData = ladder.length > 0;

    // Initialize from Step 8 if available
    useEffect(() => {
        if (ladder.length === 0 && step8Data?.alternatives) {
            const converted: LadderItem[] = step8Data.alternatives
                .filter((a: any) => a.type === "direct")
                .map((a: any, i: number) => ({
                    id: a.id || `ladder-${i}`,
                    name: a.name,
                    position: i + 1,
                    isYou: false,
                    tier: "mid-market" as const,
                    code: a.code || `LAD-${String(i + 1).padStart(2, "0")}`,
                }));
            // Add "You" in the middle
            const youItem: LadderItem = {
                id: "you",
                name: "Your Product",
                position: Math.ceil(converted.length / 2) + 1,
                isYou: true,
                tier: "mid-market",
                code: "YOU",
            };
            const withYou = [...converted.slice(0, Math.ceil(converted.length / 2)), youItem, ...converted.slice(Math.ceil(converted.length / 2))];
            const reindexed = withYou.map((item, i) => ({ ...item, position: i + 1 }));
            setLadder(reindexed);
            updateStepData(9, { ladder: reindexed });
        }
    }, [step8Data, ladder.length, updateStepData]);

    // Animation
    useEffect(() => {
        if (!containerRef.current || isGenerating) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, [hasData, isGenerating]);

    // Generate attack angles
    const generateAttackAngles = useCallback(async () => {
        if (!session?.sessionId) return;
        setIsGenerating(true);

        try {
            const { data: authData } = await supabase.auth.getSession();
            const token = authData.session?.access_token;

            const res = await fetch(
                `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/9/run`,
                {
                    method: "POST",
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            );

            if (res.ok) {
                const pollInterval = setInterval(async () => {
                    const statusRes = await fetch(
                        `http://localhost:8000/api/v1/onboarding/${session.sessionId}/steps/9`,
                        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
                    );
                    if (statusRes.ok) {
                        const data = await statusRes.json();
                        if (data?.data?.attackAngles) {
                            clearInterval(pollInterval);
                            setAttackAngles(data.data.attackAngles);
                            updateStepData(9, { ladder, attackAngles: data.data.attackAngles });
                            setIsGenerating(false);
                        }
                    }
                }, 2000);

                setTimeout(() => {
                    clearInterval(pollInterval);
                    if (isGenerating) {
                        const mock = generateMockAttackAngles();
                        setAttackAngles(mock);
                        updateStepData(9, { ladder, attackAngles: mock });
                        setIsGenerating(false);
                    }
                }, 20000);
            }
        } catch (error) {
            console.error("Generation error:", error);
            const mock = generateMockAttackAngles();
            setAttackAngles(mock);
            updateStepData(9, { ladder, attackAngles: mock });
            setIsGenerating(false);
        }
    }, [session, updateStepData, ladder, isGenerating]);

    const generateMockAttackAngles = (): AttackAngle[] => [
        { id: "1", title: "Speed-to-Value Attack", description: "Position against enterprise tools by emphasizing quick setup and immediate results", targetGap: "Complex onboarding of HubSpot/Marketo", viability: "high" },
        { id: "2", title: "Price Disruption", description: "Offer enterprise features at SMB pricing", targetGap: "Enterprise pricing excludes growing startups", viability: "medium" },
        { id: "3", title: "Guidance Over Features", description: "Differentiate by providing strategic direction, not just tools", targetGap: "Existing tools don't tell you WHAT to do", viability: "high" },
        { id: "4", title: "Founder-First Design", description: "Built specifically for non-marketers running their own marketing", targetGap: "Most tools assume marketing expertise", viability: "high" },
    ];

    const moveItem = (id: string, direction: "up" | "down") => {
        const idx = ladder.findIndex((l) => l.id === id);
        if (idx === -1) return;
        if (direction === "up" && idx === 0) return;
        if (direction === "down" && idx === ladder.length - 1) return;

        const newLadder = [...ladder];
        const swapIdx = direction === "up" ? idx - 1 : idx + 1;
        [newLadder[idx], newLadder[swapIdx]] = [newLadder[swapIdx], newLadder[idx]];
        const reindexed = newLadder.map((item, i) => ({ ...item, position: i + 1 }));
        setLadder(reindexed);
        updateStepData(9, { ladder: reindexed, attackAngles });
    };

    const updateTier = (id: string, tier: LadderItem["tier"]) => {
        const updated = ladder.map(l => l.id === id ? { ...l, tier } : l);
        setLadder(updated);
        updateStepData(9, { ladder: updated, attackAngles });
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(9, { ladder, attackAngles, confirmed: true });
        updateStepStatus(9, "complete");
    };

    const yourPosition = ladder.find((l) => l.isYou)?.position || 0;

    const tierColors = {
        premium: "text-[var(--success)] bg-[var(--success-light)]",
        "mid-market": "text-[var(--blueprint)] bg-[var(--blueprint-light)]",
        budget: "text-[var(--warning)] bg-[var(--warning-light)]",
        free: "text-[var(--muted)] bg-[var(--canvas)]",
    };

    if (isGenerating) {
        return (
            <StepLoadingState
                title="Analyzing Market Position"
                message="Identifying attack angles and differentiation opportunities..."
                stage="Evaluating competitive gaps..."
            />
        );
    }

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Description */}
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <p className="text-sm text-[var(--secondary)]">
                    Arrange competitors on a ladder from premium (top) to budget (bottom).
                    Position yourself where you want to compete, then identify attack angles.
                </p>
            </BlueprintCard>

            {/* Ladder */}
            <BlueprintCard data-animate figure="FIG. 01" title="Competitive Ladder" code="LADDER" showCorners padding="md">
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-[var(--border-subtle)]">
                    <span className="font-technical text-[var(--muted)]">USE ARROWS TO REORDER</span>
                    <BlueprintBadge variant="blueprint">YOUR POSITION: #{yourPosition}</BlueprintBadge>
                </div>

                <div className="space-y-2">
                    {ladder.map((item, idx) => (
                        <div
                            key={item.id}
                            className={`flex items-center gap-3 p-4 rounded-[var(--radius-sm)] border transition-all ${item.isYou
                                ? "bg-[var(--blueprint-light)] border-[var(--blueprint)]"
                                : "bg-[var(--canvas)] border-[var(--border-subtle)]"
                                }`}
                        >
                            <GripVertical size={14} strokeWidth={1.5} className="text-[var(--muted)] cursor-grab" />
                            <span className="font-technical text-[var(--blueprint)] w-10">{item.code}</span>
                            <div className={`w-8 h-8 rounded-[var(--radius-xs)] flex items-center justify-center font-technical ${item.isYou ? "bg-[var(--blueprint)] text-[var(--paper)]" : "bg-[var(--paper)] border border-[var(--border)] text-[var(--ink)]"
                                }`}>
                                {String(item.position).padStart(2, "0")}
                            </div>
                            <div className="flex-1">
                                <span className={`text-sm font-medium ${item.isYou ? "text-[var(--ink)]" : "text-[var(--secondary)]"}`}>
                                    {item.name}
                                </span>
                                {item.isYou && <BlueprintBadge variant="blueprint" className="ml-2">YOU</BlueprintBadge>}
                            </div>

                            {/* Tier Selector */}
                            <div className="flex gap-1">
                                {(["premium", "mid-market", "budget", "free"] as const).map((tier) => (
                                    <button
                                        key={tier}
                                        onClick={() => updateTier(item.id, tier)}
                                        className={`px-2 py-1 font-technical text-[8px] rounded-[var(--radius-xs)] transition-all ${item.tier === tier ? tierColors[tier] : "text-[var(--muted)] hover:bg-[var(--canvas)]"
                                            }`}
                                    >
                                        {tier.toUpperCase()}
                                    </button>
                                ))}
                            </div>

                            {/* Move Buttons */}
                            <div className="flex gap-1">
                                <button
                                    onClick={() => moveItem(item.id, "up")}
                                    disabled={idx === 0}
                                    className="p-1.5 rounded-[var(--radius-xs)] text-[var(--muted)] hover:bg-[var(--paper)] hover:text-[var(--blueprint)] disabled:opacity-30 transition-all"
                                >
                                    <ArrowUp size={12} strokeWidth={1.5} />
                                </button>
                                <button
                                    onClick={() => moveItem(item.id, "down")}
                                    disabled={idx === ladder.length - 1}
                                    className="p-1.5 rounded-[var(--radius-xs)] text-[var(--muted)] hover:bg-[var(--paper)] hover:text-[var(--blueprint)] disabled:opacity-30 transition-all"
                                >
                                    <ArrowDown size={12} strokeWidth={1.5} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Visual Scale */}
                <div className="mt-4 flex justify-between font-technical text-[var(--muted)]">
                    <span>↑ PREMIUM</span>
                    <span>BUDGET ↓</span>
                </div>
            </BlueprintCard>

            {/* Attack Angles */}
            <BlueprintCard data-animate figure="FIG. 02" title="Attack Angles" code="ATTACK" showCorners padding="md">
                {attackAngles.length === 0 ? (
                    <div className="text-center py-8">
                        <Target size={24} strokeWidth={1.5} className="mx-auto mb-3 text-[var(--muted)]" />
                        <p className="text-sm text-[var(--secondary)] mb-4">Generate differentiation strategies based on competitive gaps</p>
                        <BlueprintButton size="sm" onClick={generateAttackAngles}>
                            <Play size={12} strokeWidth={1.5} fill="currentColor" />
                            Generate Attack Angles
                        </BlueprintButton>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {attackAngles.map((angle) => {
                                const viabilityConfig = {
                                    high: { label: "HIGH VIABILITY", color: "bg-[var(--success)]", barWidth: "w-full" },
                                    medium: { label: "MEDIUM", color: "bg-[var(--warning)]", barWidth: "w-2/3" },
                                    low: { label: "LOW", color: "bg-[var(--muted)]", barWidth: "w-1/3" },
                                };
                                const config = viabilityConfig[angle.viability];
                                return (
                                    <div
                                        key={angle.id}
                                        className="relative p-4 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)] hover:border-[var(--blueprint)] transition-all group"
                                    >
                                        {/* Viability indicator bar at top */}
                                        <div className="absolute top-0 left-0 right-0 h-1 rounded-t-[var(--radius-sm)] overflow-hidden bg-[var(--border-subtle)]">
                                            <div className={`h-full ${config.color} ${config.barWidth} transition-all`} />
                                        </div>

                                        <div className="pt-2">
                                            <div className="flex items-start justify-between mb-2">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-8 h-8 rounded-[var(--radius-xs)] bg-[var(--blueprint-light)] flex items-center justify-center">
                                                        <Target size={14} strokeWidth={1.5} className="text-[var(--blueprint)]" />
                                                    </div>
                                                    <h4 className="text-sm font-semibold text-[var(--ink)]">{angle.title}</h4>
                                                </div>
                                                <span className={`font-technical text-[8px] px-2 py-0.5 rounded-full ${angle.viability === "high" ? "bg-[var(--success-light)] text-[var(--success)]" :
                                                    angle.viability === "medium" ? "bg-[var(--warning-light)] text-[var(--warning)]" :
                                                        "bg-[var(--canvas)] text-[var(--muted)]"
                                                    }`}>
                                                    {config.label}
                                                </span>
                                            </div>
                                            <p className="text-xs text-[var(--secondary)] mb-3">{angle.description}</p>
                                            <div className="p-2 rounded-[var(--radius-xs)] bg-[var(--paper)] border border-[var(--border-subtle)]">
                                                <span className="font-technical text-[8px] text-[var(--muted)] block mb-1">TARGET GAP</span>
                                                <span className="text-xs text-[var(--ink)]">{angle.targetGap}</span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                        <SecondaryButton size="sm" onClick={generateAttackAngles} className="w-full">
                            <RefreshCw size={10} strokeWidth={1.5} />
                            Regenerate Angles
                        </SecondaryButton>
                    </div>
                )}
            </BlueprintCard>

            {/* Confirm */}
            {!confirmed && ladder.length > 0 && attackAngles.length > 0 ? (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                    <Check size={14} strokeWidth={1.5} />
                    Confirm Ladder Position
                </BlueprintButton>
            ) : null}

            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3">
                        <Check size={18} strokeWidth={1.5} className="text-[var(--success)]" />
                        <span className="text-sm font-medium text-[var(--ink)]">Positioned at #{yourPosition} • {attackAngles.length} attack angles identified</span>
                        <BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">
                    HOW-YOU-COMPARE • STEP 08/24
                </span>
            </div>
        </div>
    );
}
