"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Target, Users, MessageSquare, Sparkles, Shield, FileText, Trophy, Rocket, Download, ArrowRight, Star, Zap } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { useRouter } from "next/navigation";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 24: Final Synthesis

   CELEBRATION REDESIGN: A moment of achievement
   The user has completed their foundation—make them feel it
   ══════════════════════════════════════════════════════════════════════════════ */

interface SynthesisSection {
    id: string;
    icon: React.ElementType;
    title: string;
    content: string;
    code: string;
}

export default function Step24FinalSynthesis() {
    const { updateStepData, updateStepStatus, getStepById, getProgress } = useOnboardingStore();
    const stepData = getStepById(24)?.data as { finalized?: boolean } | undefined;
    const router = useRouter();

    const [finalized, setFinalized] = useState(stepData?.finalized || false);
    const [showConfetti, setShowConfetti] = useState(false);
    const progress = getProgress();
    const containerRef = useRef<HTMLDivElement>(null);
    const celebrationRef = useRef<HTMLDivElement>(null);

    // Get data from previous steps
    const step10Data = getStepById(10)?.data as { selectedCategory?: string } | undefined;
    const step15Data = getStepById(15)?.data as { primaryICP?: string; profiles?: any[] } | undefined;
    const step17Data = getStepById(17)?.data as { guardrails?: any[] } | undefined;
    const step18Data = getStepById(18)?.data as { soundbites?: any[] } | undefined;

    const primaryICP = step15Data?.profiles?.find(p => p.id === step15Data?.primaryICP);
    const guardrailCount = step17Data?.guardrails?.length || 0;
    const soundbiteCount = step18Data?.soundbites?.length || 0;

    // Build synthesis from actual data
    const synthesis: SynthesisSection[] = [
        {
            id: "1",
            icon: Target,
            title: "Category Strategy",
            content: step10Data?.selectedCategory ? "Category strategy selected and locked" : "Category selection pending",
            code: "CAT"
        },
        {
            id: "2",
            icon: Users,
            title: "Primary ICP",
            content: primaryICP?.name || "ICP selection pending",
            code: "ICP"
        },
        {
            id: "3",
            icon: Shield,
            title: "Messaging Guardrails",
            content: `${guardrailCount} guardrails defined`,
            code: "GRD"
        },
        {
            id: "4",
            icon: MessageSquare,
            title: "Soundbites Library",
            content: `${soundbiteCount} soundbites approved`,
            code: "SND"
        },
    ];

    // Achievement stats
    const achievements = [
        { label: "Steps Completed", value: progress.completed, total: progress.total, icon: Check },
        { label: "Foundation Score", value: Math.round((progress.completed / progress.total) * 100), unit: "%", icon: Star },
    ];

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "back.out(1.2)" }
        );
    }, []);

    // Celebration animation on finalize
    const handleFinalize = () => {
        setFinalized(true);
        setShowConfetti(true);
        updateStepData(24, { finalized: true });
        updateStepStatus(24, "complete");

        // Animate celebration
        if (celebrationRef.current) {
            gsap.fromTo(celebrationRef.current,
                { scale: 0.8, opacity: 0 },
                { scale: 1, opacity: 1, duration: 0.6, ease: "elastic.out(1, 0.5)" }
            );
        }

        // Hide confetti after a bit
        setTimeout(() => setShowConfetti(false), 3000);
    };

    const goToExport = () => {
        router.push("/onboarding?step=25");
    };

    return (
        <div ref={containerRef} className="space-y-8">
            {/* Confetti Effect (CSS-based) */}
            {showConfetti && (
                <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
                    {Array.from({ length: 50 }).map((_, i) => (
                        <div
                            key={i}
                            className="absolute animate-confetti"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: "-10px",
                                width: "10px",
                                height: "10px",
                                backgroundColor: ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"][i % 5],
                                borderRadius: Math.random() > 0.5 ? "50%" : "0",
                                animationDelay: `${Math.random() * 2}s`,
                                animationDuration: `${2 + Math.random() * 2}s`,
                            }}
                        />
                    ))}
                </div>
            )}

            {/* Hero Header */}
            <div data-animate className="text-center py-8">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-[var(--blueprint)] to-[var(--blueprint)]/60 shadow-xl mb-4">
                    <Trophy size={40} className="text-[var(--paper)]" />
                </div>
                <h1 className="text-3xl font-serif text-[var(--ink)] mb-2">
                    {finalized ? "Foundation Complete!" : "Your Foundation Awaits"}
                </h1>
                <p className="text-sm text-[var(--secondary)] max-w-md mx-auto">
                    {finalized
                        ? "You've built a solid marketing foundation. Time to put it into action."
                        : "Review your progress and lock in your marketing foundation."
                    }
                </p>
            </div>

            {/* Progress Ring */}
            <div data-animate className="flex justify-center">
                <div className="relative w-40 h-40">
                    <svg className="w-full h-full transform -rotate-90">
                        <circle
                            cx="80"
                            cy="80"
                            r="70"
                            stroke="var(--border)"
                            strokeWidth="8"
                            fill="none"
                        />
                        <circle
                            cx="80"
                            cy="80"
                            r="70"
                            stroke="var(--blueprint)"
                            strokeWidth="8"
                            fill="none"
                            strokeLinecap="round"
                            strokeDasharray={`${2 * Math.PI * 70}`}
                            strokeDashoffset={`${2 * Math.PI * 70 * (1 - progress.percentage / 100)}`}
                            className="transition-all duration-1000"
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-4xl font-serif text-[var(--ink)]">{Math.round(progress.percentage)}%</span>
                        <span className="font-technical text-[9px] text-[var(--muted)]">COMPLETE</span>
                    </div>
                </div>
            </div>

            {/* Achievement Stats */}
            <div data-animate className="grid grid-cols-2 gap-4">
                {achievements.map((stat, i) => (
                    <div key={i} className="p-5 rounded-2xl bg-[var(--canvas)] border border-[var(--border)] text-center">
                        <stat.icon size={20} className="mx-auto mb-2 text-[var(--blueprint)]" />
                        <div className="text-3xl font-serif text-[var(--ink)]">
                            {stat.value}{stat.unit || ""}{stat.total && <span className="text-lg text-[var(--muted)]">/{stat.total}</span>}
                        </div>
                        <p className="font-technical text-[9px] text-[var(--muted)]">{stat.label}</p>
                    </div>
                ))}
            </div>

            {/* What You've Built */}
            <BlueprintCard data-animate figure="FIG. 01" title="What You've Built" code="FOUNDATION" showCorners padding="md">
                <div className="grid grid-cols-2 gap-4">
                    {synthesis.map((section) => (
                        <div
                            key={section.id}
                            className="p-4 rounded-xl bg-[var(--paper)] border border-[var(--border-subtle)] flex items-start gap-3"
                        >
                            <div className="w-10 h-10 rounded-lg bg-[var(--blueprint-light)] flex items-center justify-center flex-shrink-0">
                                <section.icon size={16} className="text-[var(--blueprint)]" />
                            </div>
                            <div>
                                <h4 className="text-sm font-semibold text-[var(--ink)]">{section.title}</h4>
                                <p className="text-xs text-[var(--secondary)]">{section.content}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </BlueprintCard>

            {/* Next Steps Preview */}
            <BlueprintCard data-animate figure="FIG. 02" title="What's Next" code="NEXT" showCorners padding="md">
                <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)]">
                        <div className="w-8 h-8 rounded-lg bg-[var(--success)] flex items-center justify-center">
                            <Download size={14} className="text-[var(--paper)]" />
                        </div>
                        <div className="flex-1">
                            <span className="text-sm font-medium text-[var(--ink)]">Export Your Assets</span>
                            <p className="text-xs text-[var(--secondary)]">Download your positioning docs, messaging guide, and more</p>
                        </div>
                        <ArrowRight size={14} className="text-[var(--muted)]" />
                    </div>
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)]">
                        <div className="w-8 h-8 rounded-lg bg-[var(--blueprint)] flex items-center justify-center">
                            <Rocket size={14} className="text-[var(--paper)]" />
                        </div>
                        <div className="flex-1">
                            <span className="text-sm font-medium text-[var(--ink)]">Launch Your Campaigns</span>
                            <p className="text-xs text-[var(--secondary)]">Use your foundation to build 90-day marketing campaigns</p>
                        </div>
                        <ArrowRight size={14} className="text-[var(--muted)]" />
                    </div>
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-[var(--canvas)] border border-[var(--border-subtle)]">
                        <div className="w-8 h-8 rounded-lg bg-[var(--warning)] flex items-center justify-center">
                            <Zap size={14} className="text-[var(--paper)]" />
                        </div>
                        <div className="flex-1">
                            <span className="text-sm font-medium text-[var(--ink)]">Execute Weekly Moves</span>
                            <p className="text-xs text-[var(--secondary)]">Turn strategy into action with guided weekly execution</p>
                        </div>
                        <ArrowRight size={14} className="text-[var(--muted)]" />
                    </div>
                </div>
            </BlueprintCard>

            {/* Finalize / Celebration */}
            {!finalized ? (
                <BlueprintButton data-animate size="lg" onClick={handleFinalize} className="w-full" label="BTN-FINAL">
                    <Sparkles size={18} strokeWidth={1.5} />Lock In My Foundation
                </BlueprintButton>
            ) : (
                <div ref={celebrationRef}>
                    <BlueprintCard showCorners variant="elevated" padding="lg" className="border-[var(--success)] bg-gradient-to-br from-[var(--success-light)] to-[var(--paper)]">
                        <div className="text-center py-4">
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[var(--success)] shadow-lg mb-4">
                                <Trophy size={32} className="text-[var(--paper)]" />
                            </div>
                            <h3 className="text-xl font-serif text-[var(--ink)] mb-2">🎉 Congratulations!</h3>
                            <p className="text-sm text-[var(--secondary)] mb-4">
                                Your marketing foundation is locked and ready. You've done the hard work—now it's time to execute.
                            </p>
                            <BlueprintButton size="lg" onClick={goToExport}>
                                <Download size={14} strokeWidth={1.5} />Export My Assets
                            </BlueprintButton>
                        </div>
                    </BlueprintCard>
                </div>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">FINAL-SYNTHESIS • STEP 24/25</span>
            </div>

            {/* Confetti Animation Styles */}
            <style jsx>{`
                @keyframes confetti-fall {
                    0% {
                        transform: translateY(0) rotate(0deg);
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(100vh) rotate(720deg);
                        opacity: 0;
                    }
                }
                .animate-confetti {
                    animation: confetti-fall 3s ease-in-out forwards;
                }
            `}</style>
        </div>
    );
}
