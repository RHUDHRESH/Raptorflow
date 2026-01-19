"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
    Target, AlertTriangle, TrendingUp, Check,
    ArrowRight, Activity, Percent, Crosshair
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { OnboardingStepLayout } from "../OnboardingStepLayout";

/* ══════════════════════════════════════════════════════════════════════════════
   STEP 13: STRATEGIC GAP ANALYSIS
   (Note: File Step ID is 13, but Positioning was 14 in previous context.
    Strictly following file content here, assuming this is Step 13 in flow logic.)
   
   Theme: "Market Intelligence Report"
   Refactored for Quiet Luxury.
   - Removing all dashboard/SaaS visual noise.
   - Creating a "Report" feel.
   ══════════════════════════════════════════════════════════════════════════════ */

interface GapAnalysisData {
    status: "opportunity" | "crowded" | "neutral";
    density: number;
    gapScore: number; // 0-100
    confirmed: boolean;
}

export default function Step13StrategicGap() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();

    const positioningStep = getStepById(12)?.data as { brands?: any[] } | undefined;
    const currentStepData = getStepById(13)?.data as GapAnalysisData | undefined;

    const [confirmed, setConfirmed] = useState(currentStepData?.confirmed || false);

    // Mock Calculation Logic (Same as before)
    const brands = positioningStep?.brands || [];
    const you = brands.find((b: any) => b.isYou);
    const competitors = brands.filter((b: any) => !b.isYou);
    const density = you ? competitors.filter((c: any) => {
        const dist = Math.sqrt(Math.pow(c.x - you.x, 2) + Math.pow(c.y - you.y, 2));
        return dist < 25;
    }).length : 0;

    const status = density === 0 ? "opportunity" : density < 3 ? "neutral" : "crowded";
    const score = Math.max(0, 100 - (density * 20));

    useEffect(() => {
        if (!currentStepData?.confirmed) {
            updateStepData(13, { status, density, gapScore: score });
        }
    }, [status, density, score, currentStepData?.confirmed, updateStepData]);

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(13, { confirmed: true });
        updateStepStatus(13, "complete");
    };

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" }
        );
    }, []);

    const StatusIcon = status === 'opportunity' ? TrendingUp : status === 'crowded' ? AlertTriangle : Activity;
    const statusColor = status === 'opportunity' ? "text-[var(--success)]" : status === 'crowded' ? "text-[var(--error)]" : "text-[var(--blueprint)]";
    const statusBg = status === 'opportunity' ? "bg-[var(--success)]" : status === 'crowded' ? "bg-[var(--error)]" : "bg-[var(--blueprint)]";

    return (
        <OnboardingStepLayout
            stepId={13}
            moduleLabel="GAP ANALYSIS"
            itemCount={confirmed ? 1 : 0}
        >
            <div ref={containerRef} className="max-w-4xl mx-auto space-y-8">

                {/* Intro */}
                <div data-animate className="flex flex-col md:flex-row justify-between items-end border-b border-[var(--border-subtle)] pb-8">
                    <div>
                        <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Market Intelligence</h2>
                        <p className="text-[var(--secondary)] max-w-lg">
                            An automated analysis of your competitive density based on the positioning map.
                        </p>
                    </div>
                </div>

                {/* Main Report Card */}
                <div data-animate className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-md)] overflow-hidden shadow-sm">
                    {/* Header Strip */}
                    <div className="flex items-center justify-between px-6 py-4 bg-[var(--canvas)] border-b border-[var(--border-subtle)]">
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-full ${statusBg} bg-opacity-10`}>
                                <StatusIcon size={18} className={statusColor} strokeWidth={2} />
                            </div>
                            <div>
                                <h3 className="font-technical text-xs font-bold uppercase tracking-widest text-[var(--ink)]">
                                    {status === 'opportunity' ? "Blue Ocean Detected" : status === 'crowded' ? "Red Ocean Alert" : "Neutral Position"}
                                </h3>
                                <p className="text-[10px] text-[var(--muted)]">Status Code: {status.toUpperCase()}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest">Confidence</p>
                            <p className="font-serif text-lg text-[var(--ink)]">{(score + 20) > 100 ? 99 : score + 20}%</p>
                        </div>
                    </div>

                    <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-12">
                        {/* Left: Metrics */}
                        <div className="space-y-8">
                            <div>
                                <span className="block font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest mb-2">Gap Score</span>
                                <div className="flex items-baseline gap-2">
                                    <span className="font-serif text-6xl text-[var(--ink)]">{score}</span>
                                    <span className="font-technical text-sm text-[var(--secondary)]">/ 100</span>
                                </div>
                                <p className="text-xs text-[var(--secondary)] mt-2 italic border-l-2 border-[var(--border-subtle)] pl-3">
                                    {status === 'opportunity'
                                        ? "Exceptional. Minimal competitive overlap."
                                        : "Caution. High competitive density."}
                                </p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-[var(--canvas)] border border-[var(--border-subtle)] rounded-[var(--radius-sm)]">
                                    <Crosshair size={16} className="text-[var(--blueprint)] mb-2" />
                                    <span className="block font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest">Density</span>
                                    <span className="font-serif text-xl text-[var(--ink)]">{density}</span>
                                    <span className="text-[10px] text-[var(--muted)] ml-1">RIVALS</span>
                                </div>
                                <div className="p-4 bg-[var(--canvas)] border border-[var(--border-subtle)] rounded-[var(--radius-sm)]">
                                    <Percent size={16} className="text-[var(--success)] mb-2" />
                                    <span className="block font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest">Win Prob.</span>
                                    <span className="font-serif text-xl text-[var(--ink)]">{score > 70 ? "High" : "Med"}</span>
                                </div>
                            </div>
                        </div>

                        {/* Right: Narrative */}
                        <div className="flex flex-col justify-center space-y-4">
                            <h4 className="font-serif text-lg text-[var(--ink)]">Strategic Implication</h4>
                            <p className="text-sm text-[var(--ink)] leading-relaxed">
                                {status === 'opportunity'
                                    ? "You have identified a clear gap in the market. Your competitors are clustered elsewhere. The strategy is rapid expansion and category education."
                                    : status === 'crowded'
                                        ? "You are entering a saturated space. To win, you must have disjoint differentiation or a significantly lower cost structure. Direct confrontation is risky."
                                        : "You have a balanced position. There are some competitors, but you have room to maneuver. Focus on your unique capabilities (Step 11) to widen the gap."}
                            </p>
                            <div className="pt-4 mt-4 border-t border-[var(--border-subtle)]">
                                <h5 className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest mb-2">Recommended Action</h5>
                                <div className="flex items-center gap-2">
                                    <ArrowRight size={14} className="text-[var(--blueprint)]" />
                                    <span className="font-medium text-sm text-[var(--blueprint)]">
                                        {status === 'opportunity' ? "Execute Attack Plan Alpha" : "Refine Value Proposition"}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Confirm Footer */}
                <div className="flex justify-end pt-8 border-t border-[var(--border-subtle)]">
                    {!confirmed ? (
                        <BlueprintButton onClick={handleConfirm} size="lg" className="px-8">
                            <span>Confirm Market Intelligence</span>
                        </BlueprintButton>
                    ) : (
                        <div className="flex items-center gap-2 text-[var(--success)]">
                            <Check size={18} />
                            <span className="font-serif italic">Intelligence Logged</span>
                        </div>
                    )}
                </div>

            </div>
        </OnboardingStepLayout>
    );
}
