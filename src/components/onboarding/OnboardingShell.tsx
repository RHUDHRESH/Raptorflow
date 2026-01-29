"use client";

import { useRef, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { Zap, ChevronLeft, ChevronRight, Check, Circle, AlertCircle, Loader2, X, HelpCircle, BookOpen, Sparkles, ChevronDown, ChevronUp } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { ONBOARDING_PHASES, ONBOARDING_STEPS, type StepStatus } from "@/lib/onboarding-tokens";
import { useCelebration } from "./Celebrations";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — OnboardingShell
   A premium, book-like interface for the calibration process.
   ══════════════════════════════════════════════════════════════════════════════ */

interface OnboardingShellProps { children: React.ReactNode; stepId: number; }

const STEP_TIMES: Record<number, string> = {
    1: "5m", 2: "3m", 3: "5m", 4: "2m", 5: "5m", 6: "4m", 7: "4m", 8: "3m", 9: "4m", 10: "5m",
    11: "6m", 12: "4m", 13: "4m", 14: "5m", 15: "3m", 16: "5m", 17: "3m", 18: "4m", 19: "5m", 20: "4m",
    21: "3m", 22: "4m", 23: "2m"
};

function StepStatusIcon({ status }: { status: StepStatus }) {
    if (status === "complete") return <Check size={14} className="text-[var(--success)]" strokeWidth={3} />;

    // Minimalist Dot - No Animation for Luxury
    if (status === "in-progress") return <div className="w-1.5 h-1.5 bg-[var(--ink)] rounded-full" />;

    if (status === "error") return <AlertCircle size={14} className="text-[var(--error)]" />;
    if (status === "blocked") return <div className="w-1.5 h-1.5 bg-[var(--border)] rounded-full" />;
    return <div className="w-1.5 h-1.5 bg-[var(--structure-subtle)] rounded-full" />;
}

function SaveIndicator() {
    const { saveStatus } = useOnboardingStore();
    return (
        <div className="flex items-center gap-1.5 font-mono text-[10px] text-[var(--muted)] uppercase tracking-wider">
            {saveStatus === "saving" && <><Loader2 size={10} className="animate-spin" />SYNCING</>}
            {saveStatus === "saved" && <><div className="w-1.5 h-1.5 bg-[var(--success)] rounded-full" />SAVED</>}
            {saveStatus === "error" && <><div className="w-1.5 h-1.5 bg-[var(--error)] rounded-full" />ERROR</>}
        </div>
    );
}

function StepSidebar({ currentStepId }: { currentStepId: number }) {
    const { steps, setCurrentStep, canProceedToStep, getProgress } = useOnboardingStore();
    const router = useRouter();
    const [expandedPhases, setExpandedPhases] = useState<number[]>([]);
    const progress = getProgress();

    useEffect(() => {
        const currentPhase = ONBOARDING_PHASES.find(p => p.steps.includes(currentStepId));
        if (currentPhase && !expandedPhases.includes(currentPhase.id)) setExpandedPhases([currentPhase.id]);
    }, [currentStepId]);

    const handleStepClick = (stepId: number) => {
        if (!canProceedToStep(stepId)) return;
        setCurrentStep(stepId);
        router.push(`/onboarding/session/step/${stepId}`);
    };

    const togglePhase = (phaseId: number) => {
        setExpandedPhases(prev => prev.includes(phaseId) ? prev.filter(id => id !== phaseId) : [...prev, phaseId]);
    };

    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Prevent hydration mismatch
    const progressPercentage = mounted ? progress.percentage : 0;

    return (
        <div className="w-64 bg-[var(--paper)] border-r border-[var(--structure)] flex flex-col h-full flex-shrink-0 z-20">
            {/* Header */}
            <div className="h-16 flex items-center px-5 border-b border-[var(--structure)]">
                <div>
                    <h2 className="font-technical font-bold text-[10px] text-[var(--ink)] tracking-[0.15em]">CALIBRATION INDEX</h2>
                    <div className="flex items-center gap-2 mt-1">
                        <div className="h-1.5 w-24 bg-[var(--structure)] rounded-full overflow-hidden">
                            <div className="h-full bg-[var(--blueprint)] transition-all duration-500" style={{ width: `${progressPercentage}%` }} />
                        </div>
                        <span className="font-technical text-[var(--ink-muted)]">{progressPercentage}%</span>
                    </div>
                </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto py-2">
                {/* Section Header */}
                <div className="flex items-center gap-2 px-5 py-2 mb-1">
                    <span className="font-technical text-[var(--ink-muted)]">PHASES</span>
                    <div className="flex-1 h-px bg-[var(--structure-subtle)]" />
                </div>
                {ONBOARDING_PHASES.map((phase) => {
                    const isCurrentPhase = phase.steps.includes(currentStepId);
                    const isExpanded = expandedPhases.includes(phase.id);
                    const phaseSteps = steps.filter(s => phase.steps.includes(s.id));
                    const completedCount = phaseSteps.filter(s => s.status === "complete").length;

                    return (
                        <div key={phase.id} className="mb-px">
                            <button
                                onClick={() => togglePhase(phase.id)}
                                className={cn(
                                    "w-full flex items-center justify-between px-5 py-2.5 text-left hover:bg-[var(--canvas)] transition-colors group",
                                    isCurrentPhase ? "bg-[var(--canvas)]" : ""
                                )}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={cn(
                                        "w-5 h-5 flex items-center justify-center font-technical text-[9px] border rounded-[var(--radius-xs)]",
                                        isCurrentPhase
                                            ? "bg-[var(--ink)] border-[var(--ink)] text-white"
                                            : completedCount === phase.steps.length
                                                ? "bg-[var(--success)] border-[var(--success)] text-white"
                                                : "bg-[var(--paper)] border-[var(--border)] text-[var(--ink-muted)]"
                                    )}>
                                        {completedCount === phase.steps.length ? <Check size={10} /> : phase.id}
                                    </div>
                                    <span className={cn(
                                        "text-xs font-semibold tracking-tight transition-colors",
                                        isCurrentPhase ? "text-[var(--ink)]" : "text-[var(--ink-secondary)]"
                                    )}>
                                        {phase.name.toUpperCase()}
                                    </span>
                                </div>
                                {/* Phase code badge */}
                                <div className="flex items-center gap-2">
                                    <span className={cn(
                                        "font-technical text-[9px] px-1.5 py-0.5 rounded border",
                                        isCurrentPhase
                                            ? "text-[var(--blueprint)] bg-[var(--paper)] border-[var(--blueprint)]/30"
                                            : "text-[var(--ink-muted)] bg-transparent border-transparent"
                                    )}>
                                        {completedCount}/{phase.steps.length}
                                    </span>
                                    <ChevronDown
                                        size={12}
                                        className={cn(
                                            "text-[var(--ink-muted)] transition-transform",
                                            isExpanded ? "rotate-180" : ""
                                        )}
                                    />
                                </div>
                            </button>

                            {isExpanded && (
                                <div className="bg-[var(--canvas)] pb-2 border-b border-[var(--structure-subtle)]">
                                    {phase.steps.map((stepId) => {
                                        const stepConfig = ONBOARDING_STEPS.find(s => s.id === stepId);
                                        const stepState = steps.find(s => s.id === stepId);
                                        if (!stepConfig || !stepState) return null;

                                        const isActive = stepId === currentStepId;
                                        const canClick = canProceedToStep(stepId);

                                        return (
                                            <button
                                                key={stepId}
                                                onClick={() => handleStepClick(stepId)}
                                                disabled={!canClick}
                                                className={cn(
                                                    "w-full flex items-center gap-3 px-5 pl-12 py-2 text-left transition-colors relative",
                                                    isActive
                                                        ? "text-[var(--blueprint)] bg-[var(--blueprint-light)]/20"
                                                        : canClick ? "text-[var(--ink-secondary)] hover:text-[var(--ink)] hover:bg-[var(--canvas)]" : "text-[var(--ink-muted)] opacity-60 cursor-not-allowed"
                                                )}
                                            >
                                                {isActive && (
                                                    <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--blueprint)]" />
                                                )}
                                                <StepStatusIcon status={stepState.status} />
                                                <span className="text-xs font-medium truncate flex-1">{stepConfig.name}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function ContextDrawer({ stepId }: { stepId: number }) {
    const contextData: Record<number, { why: string }> = {
        1: { why: "We need raw material to train your brand voice." },
        // ... (keep brief)
    };
    const context = contextData[stepId] || { why: "Calibration step." };

    return (
        <div className="w-72 bg-[var(--paper)] border-l border-[var(--structure)] hidden xl:flex flex-col flex-shrink-0 z-20">
            <div className="h-16 flex items-center px-6 border-b border-[var(--structure)]">
                <span className="font-technical font-bold text-[10px] text-[var(--ink)] tracking-[0.15em]">CONTEXT</span>
            </div>
            <div className="p-6">
                <div className="mb-8">
                    <span className="font-technical text-[var(--ink-muted)] mb-2 block">OBJECTIVE</span>
                    <p className="text-sm text-[var(--ink-secondary)] leading-relaxed">{context.why}</p>
                </div>

                <div className="mt-8 pt-8 border-t border-[var(--structure-subtle)]">
                    <button className="flex items-center gap-2 text-xs font-medium text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors">
                        <HelpCircle size={14} /> Need assistance?
                    </button>
                </div>
            </div>
        </div>
    );
}

export function OnboardingShell({ children, stepId }: OnboardingShellProps) {
    const router = useRouter();
    const { session, canProceedToStep, setCurrentStep } = useOnboardingStore();
    const [showExit, setShowExit] = useState(false);
    const { triggerPhaseComplete } = useCelebration();
    const mainRef = useRef<HTMLDivElement>(null);

    const stepConfig = ONBOARDING_STEPS.find(s => s.id === stepId);
    const currentPhase = ONBOARDING_PHASES.find(p => p.steps.includes(stepId));

    useEffect(() => {
        if (!mainRef.current) return;
        gsap.fromTo(mainRef.current, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
    }, [stepId]);

    const handleNext = () => {
        const TOTAL_STEPS = 24;
        if (stepId === TOTAL_STEPS) {
            router.push('/dashboard?welcome=true');
            return;
        }
        if (stepId < TOTAL_STEPS && canProceedToStep(stepId + 1)) {
            setCurrentStep(stepId + 1);
            router.push(`/onboarding/session/step/${stepId + 1}`);
        }
    };

    return (
        <div className="h-screen flex flex-col bg-[var(--canvas)] text-[var(--ink)] font-sans overflow-hidden">
            {/* Navbar */}
            <header className="h-14 bg-[var(--paper)] border-b border-[var(--border)] flex items-center justify-between px-4 z-30 shrink-0">
                <div className="flex items-center gap-4">
                    <div className="w-8 h-8 flex items-center justify-center bg-[var(--ink)] rounded-[var(--radius-sm)] text-[var(--paper)]">
                        <Zap size={16} fill="currentColor" />
                    </div>
                    <div className="h-4 w-px bg-[var(--border)]" />
                    <span className="font-mono text-xs text-[var(--muted)] uppercase tracking-wide">
                        {session?.clientName || "NEW WORKSPACE"} // SETUP
                    </span>
                </div>
                <div className="flex items-center gap-4">
                    <SaveIndicator />
                    <button onClick={() => setShowExit(true)} className="p-2 hover:bg-[var(--surface)] rounded-full text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
                        <X size={18} />
                    </button>
                </div>
            </header>

            {/* Main Layout */}
            <div className="flex-1 flex overflow-hidden">
                <StepSidebar currentStepId={stepId} />

                <main className="flex-1 relative flex flex-col min-w-0 bg-[var(--canvas)]">
                    {/* Content Scroll Area */}
                    <div className="flex-1 overflow-y-auto">
                        <div ref={mainRef} className="max-w-3xl mx-auto px-8 py-12 pb-24 relative z-10">
                            {/* Step Header */}
                            <div className="mb-10">
                                <div className="flex items-center gap-3 mb-4">
                                    <BlueprintBadge variant="default">{currentPhase?.name}</BlueprintBadge>
                                    <span className="text-[10px] font-mono text-[var(--muted)]">STEP {String(stepId).padStart(2, '0')}</span>
                                </div>
                                <h1 className="font-serif text-4xl text-[var(--ink)] mb-4">{stepConfig?.name}</h1>
                                <div className="h-px w-full bg-[var(--border)]" />
                            </div>

                            {children}
                        </div>
                    </div>

                    {/* Floating Footer */}
                    <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-[var(--canvas)] via-[var(--canvas)] to-transparent z-20 pointer-events-none">
                        <div className="max-w-3xl mx-auto flex items-center justify-between pointer-events-auto">
                            <SecondaryButton
                                onClick={() => {
                                    if (stepId <= 1) return;
                                    const previousStep = stepId - 1;
                                    setCurrentStep(previousStep);
                                    router.push(`/onboarding/session/step/${previousStep}`);
                                }}
                                disabled={stepId <= 1}
                            >
                                <ChevronLeft size={16} /> Previous
                            </SecondaryButton>

                            <BlueprintButton
                                size="lg"
                                onClick={handleNext}
                                disabled={stepId !== 24 && !canProceedToStep(stepId + 1)}
                                title={stepId !== 24 && !canProceedToStep(stepId + 1) ? "Complete this step first" : undefined}
                            >
                                {stepId === 24 ? "Finish Setup" : "Continue"} <ChevronRight size={16} />
                            </BlueprintButton>
                        </div>
                    </div>
                </main>

                <ContextDrawer stepId={stepId} />
            </div>

            <BlueprintModal isOpen={showExit} onClose={() => setShowExit(false)} title="Pause calibration?" code="EXIT-01">
                <p className="text-sm text-[var(--secondary)] mb-6">Your progress is automatically saved. You can return to this exact step at any time.</p>
                <div className="flex justify-end gap-3">
                    <SecondaryButton onClick={() => setShowExit(false)}>Cancel</SecondaryButton>
                    <BlueprintButton variant="blueprint" onClick={() => router.push('/dashboard')}>Save & Exit</BlueprintButton>
                </div>
            </BlueprintModal>
        </div>
    );
}
