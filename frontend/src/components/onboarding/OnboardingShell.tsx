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
    1: "5m", 2: "3m", 3: "5m", 4: "2m", 5: "5m", 6: "3m", 7: "3m", 8: "3m", 9: "3m", 10: "4m",
    11: "4m", 12: "5m", 13: "3m", 14: "4m", 15: "3m", 16: "3m", 17: "4m", 18: "4m", 19: "3m", 20: "3m",
    21: "4m", 22: "3m", 23: "5m", 24: "2m",
};

const STEP_UNLOCKS: Record<number, string> = {
    1: "Intel Vault", 2: "Truth Sheet", 3: "Foundation", 4: "Snapshot", 5: "Offer Doc",
    6: "Insights", 7: "Comp Intel", 8: "Angles", 9: "Positioning", 10: "Differentials",
    11: "Value Matrix", 12: "Statements", 13: "Focus Strat", 14: "ICP DNA", 15: "Journeys",
    16: "Guidelines", 17: "Soundbites", 18: "Hierarchy", 19: "Refresh Plan", 20: "Channels",
    21: "Sizing", 22: "Roadmap", 23: "Complete", 24: "Exports",
};

function StepStatusIcon({ status }: { status: StepStatus }) {
    if (status === "complete") return <Check size={14} className="text-[var(--success)]" />;
    if (status === "in-progress") return <div className="w-2 h-2 bg-[var(--blueprint)] rounded-full animate-pulse shadow-[0_0_8px_var(--blueprint)]" />;
    if (status === "error") return <AlertCircle size={14} className="text-[var(--error)]" />;
    if (status === "blocked") return <div className="w-1.5 h-1.5 bg-[var(--border)] rounded-full" />;
    return <div className="w-1.5 h-1.5 bg-[var(--muted)] rounded-full" />;
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

    return (
        <div className="w-64 bg-[var(--paper)] border-r border-[var(--border)] flex flex-col h-full flex-shrink-0 z-20">
            {/* Header */}
            <div className="h-16 flex items-center px-5 border-b border-[var(--border)] bg-[var(--surface-subtle)]">
                <div>
                    <h2 className="font-technical font-bold text-xs text-[var(--ink)] tracking-wider">CALIBRATION INDEX</h2>
                    <div className="flex items-center gap-2 mt-1">
                        <div className="h-1 w-24 bg-[var(--structure)] rounded-full overflow-hidden">
                            <div className="h-full bg-[var(--blueprint)] transition-all duration-500" style={{ width: `${progress.percentage}%` }} />
                        </div>
                        <span className="text-[10px] font-mono text-[var(--muted)]">{progress.percentage}%</span>
                    </div>
                </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto py-2">
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
                                    "w-full flex items-center justify-between px-5 py-3 text-left hover:bg-[var(--surface)] transition-colors group",
                                    isCurrentPhase ? "bg-[var(--surface)]" : ""
                                )}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={cn(
                                        "w-5 h-5 flex items-center justify-center font-mono text-[10px] border rounded-[var(--radius-xs)]",
                                        isCurrentPhase
                                            ? "bg-[var(--blueprint)] border-[var(--blueprint)] text-white"
                                            : completedCount === phase.steps.length
                                                ? "bg-[var(--success)] border-[var(--success)] text-white"
                                                : "bg-[var(--paper)] border-[var(--border)] text-[var(--muted)]"
                                    )}>
                                        {completedCount === phase.steps.length ? <Check size={10} /> : phase.id}
                                    </div>
                                    <span className={cn(
                                        "text-xs font-medium transition-colors",
                                        isCurrentPhase ? "text-[var(--ink)]" : "text-[var(--secondary)]"
                                    )}>
                                        {phase.name}
                                    </span>
                                </div>
                                <ChevronDown
                                    size={12}
                                    className={cn(
                                        "text-[var(--muted)] transition-transform",
                                        isExpanded ? "rotate-180" : ""
                                    )}
                                />
                            </button>

                            {isExpanded && (
                                <div className="bg-[var(--canvas)] pb-2 border-b border-[var(--border-subtle)]">
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
                                                    "w-full flex items-center gap-3 px-5 pl-10 py-2 text-left transition-colors relative",
                                                    isActive
                                                        ? "text-[var(--blueprint)] bg-[var(--blueprint-light)]/20"
                                                        : canClick ? "text-[var(--secondary)] hover:text-[var(--ink)] hover:bg-[var(--surface)]" : "text-[var(--muted)] opacity-60 cursor-not-allowed"
                                                )}
                                            >
                                                {isActive && (
                                                    <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--blueprint)]" />
                                                )}
                                                <StepStatusIcon status={stepState.status} />
                                                <span className="text-[11px] font-medium truncate flex-1">{stepConfig.name}</span>
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
    const contextData: Record<number, { why: string; unlocks: string }> = {
        1: { why: "We need raw material to train your brand voice.", unlocks: "Auto-extraction of claims" },
        // ... (keep brief)
    };
    const context = contextData[stepId] || { why: "Calibration step.", unlocks: "Next Module" };

    return (
        <div className="w-72 bg-[var(--paper)] border-l border-[var(--border)] hidden xl:flex flex-col flex-shrink-0 z-20">
            <div className="h-16 flex items-center px-6 border-b border-[var(--border)] bg-[var(--surface-subtle)]">
                <span className="font-technical font-bold text-xs text-[var(--ink)] tracking-wider">CONTEXT</span>
            </div>
            <div className="p-6">
                <div className="mb-8">
                    <span className="label text-[10px] mb-2 block">OBJECTIVE</span>
                    <p className="text-sm text-[var(--secondary)] leading-relaxed">{context.why}</p>
                </div>

                <BlueprintCard padding="sm" className="bg-[var(--surface)] border-dashed">
                    <div className="flex items-center gap-2 mb-1">
                        <Sparkles size={12} className="text-[var(--blueprint)]" />
                        <span className="font-mono text-[10px] text-[var(--blueprint)]">UNLOCKS</span>
                    </div>
                    <p className="text-xs font-medium text-[var(--ink)]">{context.unlocks}</p>
                </BlueprintCard>

                <div className="mt-8 pt-8 border-t border-[var(--border)]">
                    <button className="flex items-center gap-2 text-xs font-medium text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
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
        if (stepId === 25) {
            router.push('/dashboard');
            return;
        }
        if (stepId < 25 && canProceedToStep(stepId + 1)) {
            const nextPhase = ONBOARDING_PHASES.find(p => p.steps.includes(stepId + 1));
            // Transition logic...
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
                    {/* Paper Texture Overlay */}
                    <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: "url('/textures/paper-grain.png')" }} />

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
                                onClick={() => stepId > 1 && router.push(`/onboarding/session/step/${stepId - 1}`)}
                                disabled={stepId <= 1}
                            >
                                <ChevronLeft size={16} /> Previous
                            </SecondaryButton>

                            <BlueprintButton
                                size="lg"
                                onClick={handleNext}
                                disabled={stepId !== 25 && !canProceedToStep(stepId + 1)}
                                className="shadow-xl"
                                title={stepId !== 25 && !canProceedToStep(stepId + 1) ? "Complete this step first" : undefined}
                            >
                                {stepId === 25 ? "Finish Setup" : "Continue"} <ChevronRight size={16} />
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
                    <BlueprintButton variant="primary" onClick={() => router.push('/dashboard')}>Save & Exit</BlueprintButton>
                </div>
            </BlueprintModal>
        </div>
    );
}
