"use client";

import { useState, useMemo } from "react";
import { MoveCategory, MoveBriefData, ExecutionDay, MOVE_CATEGORIES } from "./types";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { ArrowRight, Check, Sparkles, ChevronRight, Target, Clock, MessageSquare, Lightbulb, Users, User, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api/client";
import { MoveCategoryIcon } from "./MoveCategoryIcon";
import { useBCMStore } from "@/stores/bcmStore";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   MOVE CREATE WIZARD
   Refactored for:
   1. ICP Selection (from Cohorts)
   2. Guaranteed Execution Plan
   3. "Solid + Blur" Visuals
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface MoveCreateWizardProps {
    isOpen: boolean;
    onClose: () => void;
    onComplete: (data: { category: MoveCategory; context: string; brief: MoveBriefData; execution: ExecutionDay[] }) => void;
}

type WizardStep = 'objective' | 'context' | 'clarify' | 'preview';

// Get cohorts from BCM or fallback to mock data
const getCohortsFromBCM = (bcm: any) => {
    if (bcm?.icps && bcm.icps.length > 0) {
        return bcm.icps.map((icp: any, index: number) => ({
            id: icp.id || `COH-${String(index + 1).padStart(2, '0')}`,
            name: icp.name || `ICP ${index + 1}`,
            description: icp.demographics?.role || 'Target audience segment'
        }));
    }
    
    // Fallback mock data
    return [
        { id: "COH-01", name: "Enterprise Decision Makers", description: "C-level at 500+ companies" },
        { id: "COH-02", name: "High-Intent Visitors", description: "Visited pricing 3+ times" },
        { id: "COH-03", name: "SaaS Founders", description: "Series A-B B2B SaaS Founders" },
        { id: "COH-04", name: "Marketing Leaders", description: "CMOs & VPs of Growth" },
        { id: "COH-05", name: "Agency Owners", description: "Service business owners >$500k" },
    ];
};

const CLARIFICATION_QUESTIONS = [
    { id: 'resistance', question: 'Why haven\'t they bought yet?', placeholder: 'e.g. They think it\'s too expensive...' },
    { id: 'offer', question: 'What is the core offer for this move?', placeholder: 'e.g. Free audit call...' },
    { id: 'outcome', question: 'What is the ideal outcome?', placeholder: 'e.g. 10 qualified demos booked...' },
];

export function MoveCreateWizard({ isOpen, onClose, onComplete }: MoveCreateWizardProps) {
    const { bcm } = useBCMStore();
    const [step, setStep] = useState<WizardStep>('objective');
    const [category, setCategory] = useState<MoveCategory | null>(null);
    const [contextDesc, setContextDesc] = useState('');
    const [selectedCohort, setSelectedCohort] = useState<string | null>(null); // For ICP selection
    const [timeCommitment, setTimeCommitment] = useState<string | null>(null);
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [customAnswer, setCustomAnswer] = useState('');
    const [brief, setBrief] = useState<MoveBriefData | null>(null);
    const [execution, setExecution] = useState<ExecutionDay[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Reset state on open
    if (!isOpen && step !== 'objective') {
        setTimeout(() => {
            setStep('objective');
            setCategory(null);
            setContextDesc('');
            setSelectedCohort(null);
            setAnswers({});
            setCurrentQ(0);
        }, 300);
    }

    const handleNext = async () => {
        if (step === 'objective' && category) {
            setStep('context');
        } else if (step === 'context' && contextDesc.trim() && selectedCohort) {
            setStep('clarify');
        } else if (step === 'clarify') {
            const q = CLARIFICATION_QUESTIONS[currentQ];
            const ans = answers[q.id] || customAnswer;
            if (!ans) return;

            setAnswers(prev => ({ ...prev, [q.id]: ans }));
            setCustomAnswer('');

            if (currentQ < CLARIFICATION_QUESTIONS.length - 1) {
                setCurrentQ(prev => prev + 1);
            } else {
                // --- ABSOLUTE INFINITY: CALL REAL STRATEGIC ENGINE ---
                setIsLoading(true);
                try {
                    const goal = `Objective: ${MOVE_CATEGORIES[category!].name}. Context: ${contextDesc}. Answers: ${JSON.stringify(answers)}`;
                    const response = await apiClient.createBlueprint(goal);
                    
                    if (response.data) {
                        setBrief(response.data.brief);
                        setExecution(response.data.execution_plan || []);
                        setStep('preview');
                    }
                } catch (error) {
                    console.error("Blueprint generation failed:", error);
                    // Fallback to mock for UI stability if desired, but here we want it real
                } finally {
                    setIsLoading(false);
                }
            }
        } else if (step === 'preview') {
            onComplete({ category: category!, context: contextDesc, brief: brief!, execution: execution });
            onClose();
        }
    };

    const handleBack = () => {
        if (step === 'context') setStep('objective');
        else if (step === 'clarify') {
            if (currentQ > 0) {
                setCurrentQ(p => p - 1);
                setCustomAnswer(answers[CLARIFICATION_QUESTIONS[currentQ - 1].id] || '');
            } else {
                setStep('context');
            }
        }
        else if (step === 'preview') {
            setStep('clarify');
            setCurrentQ(CLARIFICATION_QUESTIONS.length - 1);
        }
    };

    const isNextDisabled = () => {
        if (step === 'objective') return !category;
        if (step === 'context') return contextDesc.trim().length <= 3 || !selectedCohort;
        if (step === 'clarify') return !customAnswer && !answers[CLARIFICATION_QUESTIONS[currentQ].id];
        return false;
    };

    return (
        <BlueprintModal
            isOpen={isOpen}
            onClose={onClose}
            title={
                step === 'objective' ? 'Select Move Type' :
                    step === 'context' ? 'Target & Context' :
                        step === 'clarify' ? 'Refine Strategy' :
                            'Ready to Launch'
            }
            size="lg"
            className="backdrop-blur-sm" // Restore blur to modal area specifically
            footer={
                <div className="flex items-center justify-between w-full">
                    <div className="flex gap-1">
                        {['objective', 'context', 'clarify', 'preview'].map((s, i) => {
                            const currentIdx = ['objective', 'context', 'clarify', 'preview'].indexOf(step);
                            return (
                                <div
                                    key={s}
                                    className={cn(
                                        "w-2 h-2 rounded-full transition-colors",
                                        i <= currentIdx ? "bg-[var(--ink)]" : "bg-[var(--surface-subtle)]"
                                    )}
                                />
                            );
                        })}
                    </div>

                    <div className="flex gap-3">
                        {step !== 'objective' && (
                            <button
                                onClick={handleBack}
                                className="px-4 py-2 text-sm text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
                            >
                                Back
                            </button>
                        )}
                        <button
                            onClick={handleNext}
                            disabled={isNextDisabled() || isLoading}
                            className={cn(
                                "flex items-center gap-2 px-6 py-2 rounded-[var(--radius)] text-sm font-medium transition-all",
                                isNextDisabled() || isLoading
                                    ? "bg-[var(--surface-subtle)] text-[var(--muted)] cursor-not-allowed"
                                    : "bg-[var(--ink)] text-white hover:bg-[var(--ink)]/90 shadow-md"
                            )}
                        >
                            {isLoading ? (
                                <>Processing...</>
                            ) : step === 'preview' ? (
                                <><Check size={16} /> Launch Move</>
                            ) : (
                                <><span className="mr-1">Next</span> <ArrowRight size={16} /></>
                            )}
                        </button>
                    </div>
                </div>
            }
        >
            <div className="min-h-[400px]">
                {/* STEP 1: OBJECTIVE */}
                {step === 'objective' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {(Object.keys(MOVE_CATEGORIES) as MoveCategory[]).map((catId) => {
                            const cat = MOVE_CATEGORIES[catId];
                            const isSelected = category === catId;
                            return (
                                <div
                                    key={catId}
                                    onClick={() => setCategory(catId)}
                                    className={cn(
                                        "relative p-4 rounded-[var(--radius)] border cursor-pointer transition-all duration-200 group",
                                        isSelected
                                            ? "border-[var(--ink)] bg-[var(--surface-subtle)] ring-1 ring-[var(--ink)]"
                                            : "border-[var(--border)] hover:border-[var(--ink)] hover:shadow-md"
                                    )}
                                >
                                    <div className="flex items-start justify-between mb-2">
                                        <div className="text-2xl"><MoveCategoryIcon category={catId} size={24} /></div>
                                        {isSelected && <Check size={16} className="text-[var(--ink)]" />}
                                    </div>
                                    <h3 className="font-semibold text-[var(--ink)] mb-1">{cat.name}</h3>
                                    <p className="text-xs text-[var(--muted)] mb-3">{cat.tagline}</p>
                                    <div className="flex flex-wrap gap-1.5">
                                        {cat.useFor.slice(0, 2).map((tag, i) => (
                                            <span key={i} className="px-1.5 py-0.5 rounded text-[10px] bg-[var(--paper)] border border-[var(--border)] text-[var(--muted)]">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* STEP 2: CONTEXT & ICP SELECTION */}
                {step === 'context' && (
                    <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                        {/* ICP Selection - Dropdown/Grid */}
                        <div>
                            <label className="block text-sm font-medium text-[var(--ink)] mb-3">
                                Who specifically do you need to reach?
                            </label>
                            <div className="grid grid-cols-1 gap-3 max-h-[160px] overflow-y-auto pr-2 custom-scrollbar">
                                {getCohortsFromBCM(bcm).map((cohort: any) => (
                                    <button
                                        key={cohort.id}
                                        onClick={() => setSelectedCohort(cohort.id)}
                                        className={cn(
                                            "flex items-center justify-between p-3 rounded-[var(--radius)] border text-left transition-all",
                                            selectedCohort === cohort.id
                                                ? "border-[var(--ink)] bg-[var(--surface-subtle)] ring-1 ring-[var(--ink)]"
                                                : "border-[var(--border)] bg-[var(--paper)] hover:border-[var(--blueprint)]"
                                        )}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-[var(--surface)] flex items-center justify-center text-[var(--muted)]">
                                                <Users size={14} />
                                            </div>
                                            <div>
                                                <div className="text-sm font-medium text-[var(--ink)]">{cohort.name}</div>
                                                <div className="text-xs text-[var(--muted)]">{cohort.description}</div>
                                            </div>
                                        </div>
                                        {selectedCohort === cohort.id && <Check size={16} className="text-[var(--ink)]" />}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Situation/Context */}
                        <div>
                            <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                                What's the situation?
                            </label>
                            <textarea
                                value={contextDesc}
                                onChange={(e) => setContextDesc(e.target.value)}
                                placeholder="e.g. We are launching a new feature next week and need to build hype..."
                                className="w-full h-24 p-4 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] focus:outline-none focus:border-[var(--ink)] text-sm resize-none"
                            />
                        </div>

                        {/* Time Commitment */}
                        <div className="flex items-center gap-4 p-4 rounded-[var(--radius)] bg-[var(--surface-subtle)] border border-[var(--border)]">
                            <Clock className="text-[var(--muted)]" />
                            <div>
                                <h4 className="text-sm font-medium text-[var(--ink)]">Time Commitment</h4>
                                <p className="text-xs text-[var(--muted)]">How much time can you dedicate daily?</p>
                            </div>
                            <div className="flex gap-2 ml-auto">
                                {['15m', '30m', '1h+'].map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setTimeCommitment(t)}
                                        className={cn(
                                            "px-3 py-1.5 text-xs font-medium rounded transition-colors",
                                            timeCommitment === t
                                                ? "bg-[var(--ink)] text-white"
                                                : "bg-[var(--paper)] border border-[var(--border)] hover:border-[var(--ink)]"
                                        )}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* STEP 3: CLARIFY */}
                {step === 'clarify' && (
                    <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-[var(--surface-subtle)] flex items-center justify-center shrink-0">
                                <Sparkles size={18} className="text-[var(--ink-secondary)]" />
                            </div>
                            <div className="space-y-4 flex-1">
                                <div className="bg-[var(--surface-subtle)] p-4 rounded-[var(--radius)] rounded-tl-none relative">
                                    <p className="text-sm text-[var(--ink)] font-medium">
                                        {CLARIFICATION_QUESTIONS[currentQ].question}
                                    </p>
                                    <div className="absolute -left-2 top-4 w-2 h-2 bg-[var(--surface-subtle)] [clip-path:polygon(100%_0,0_0,100%_100%)]" />
                                </div>
                                <input
                                    type="text"
                                    value={customAnswer}
                                    onChange={(e) => setCustomAnswer(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && customAnswer && handleNext()}
                                    placeholder={CLARIFICATION_QUESTIONS[currentQ].placeholder}
                                    className="w-full p-3 border-b-2 border-[var(--border)] bg-transparent focus:outline-none focus:border-[var(--ink)] transition-colors"
                                    autoFocus
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* STEP 4: PREVIEW */}
                {step === 'preview' && brief && (
                    <div className="space-y-6 animate-in zoom-in-95 duration-300">
                        <div className="text-center mb-8">
                            <div className="w-16 h-16 rounded-full bg-[var(--success)]/10 flex items-center justify-center mx-auto mb-4 border border-[var(--success)]/20 shadow-lg shadow-[var(--success)]/10">
                                <span className="text-3xl"><MoveCategoryIcon category={brief.category} size={32} /></span>
                            </div>
                            <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">{brief.name}</h2>
                            <p className="text-[var(--muted)] max-w-md mx-auto">{brief.goal}</p>
                        </div>

                        {/* Strategy Card */}
                        <div className="p-4 border border-[var(--border)] rounded-[var(--radius)] bg-[var(--paper)] mb-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Target size={14} className="text-[var(--blueprint)]" />
                                <span className="text-xs font-bold uppercase tracking-wider text-[var(--blueprint)]">Strategy Lock</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="text-sm font-medium text-[var(--ink)]">Targeting {brief.icp}</div>
                                <div className="text-xs text-[var(--muted)]">{brief.duration} Days Execution</div>
                            </div>
                        </div>

                        {/* Plan Preview */}
                        <div className="bg-[var(--surface-subtle)] rounded-[var(--radius)] border border-[var(--border)] overflow-hidden">
                            <div className="px-4 py-3 border-b border-[var(--border)] flex justify-between items-center bg-[var(--surface)]">
                                <div className="text-xs font-medium text-[var(--ink)] uppercase tracking-wider">Execution Plan Generated</div>
                                <div className="text-[10px] text-[var(--success)] font-bold flex items-center gap-1">
                                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)]" />
                                    READY
                                </div>
                            </div>
                            <div className="p-2 space-y-1">
                                {execution.slice(0, 3).map((day, i) => (
                                    <div key={i} className="flex items-center gap-3 p-2 text-xs">
                                        <div className="w-6 text-[var(--muted)] font-medium">Day {day.day}</div>
                                        <div className="flex-1 truncate text-[var(--ink)]">{day.pillarTask.title}</div>
                                    </div>
                                ))}
                                {execution.length > 3 && (
                                    <div className="px-2 py-1 text-[10px] text-[var(--muted)] italic text-center">
                                        + {execution.length - 3} more days planned
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </BlueprintModal>
    );
}

// --- MOCK GENERATORS ---

function generateMockBrief(category: MoveCategory, context: string, icp: string, bcm?: any): MoveBriefData {
    // Use BCM data if available
    const brandVoice = bcm?.messaging?.brand_voice?.tone?.join(', ') || "Professional & Authoritative";
    const valueProps = bcm?.messaging?.value_props || [];
    const company = bcm?.foundation?.company || "Your Company";
    
    return {
        name: `${MOVE_CATEGORIES[category].name} Sprint`,
        category,
        goal: `Execute a high-impact ${category} campaign for ${company} to achieve measurable results.`,
        tone: brandVoice,
        duration: 7,
        icp: icp, // Use selected ICP
        strategy: `Focus on high-leverage ${category} activities to maximize impact. ${valueProps[0] ? `Emphasize: ${valueProps[0]}` : ''}`,
        metrics: ["Engagement Rate", "Conversion Rate", "Lead Quality"]
    };
}

function generateMockExecution(brief: MoveBriefData): ExecutionDay[] {
    // GUARANTEED: Always generate execution days. No partial or empty arrays.
    return Array.from({ length: brief.duration }).map((_, i) => ({
        day: i + 1,
        phase: i < 2 ? 'Analysis' : i < 5 ? 'Execution' : 'Review',
        pillarTask: { id: `p-${i}`, title: `Main Pillar Activity ${i + 1}`, status: 'pending', description: 'Primary focus task for the day.' },
        clusterActions: [{ id: `c-${i}`, title: `Supporting Task ${i + 1}`, status: 'pending', channel: 'linkedin' }],
        networkAction: { id: `n-${i}`, title: `Network Engagement ${i + 1}`, status: 'pending', channel: 'dm' }
    }));
}

export default MoveCreateWizard;
