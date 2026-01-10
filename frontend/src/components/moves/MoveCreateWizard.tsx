"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { MoveCategory, MoveBriefData, ExecutionDay, MOVE_CATEGORIES } from "./types";
import { ExecutionGrid } from "./ExecutionGrid";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { Loader2, ArrowRight, ArrowLeft, Check, X, Sparkles } from "lucide-react";
import { generateMockBrief, generateMockExecution } from "./mockMoves";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE CREATE WIZARD — ULTRA COMPACT (No Scrolling!)
   Everything fits on screen at once. No vertical scrolling required.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MoveCreateWizardProps {
    isOpen: boolean;
    onClose: () => void;
    onComplete: (move: { category: MoveCategory; context: string; brief: MoveBriefData; execution: ExecutionDay[] }) => void;
}

type WizardStep = 'objective' | 'context' | 'clarify' | 'preview';

const CLARIFICATION_QUESTIONS = [
    { id: 'pricing', question: 'Pricing approach?', options: ['Increasing', 'Keep current', 'Other'] },
    { id: 'audience', question: 'Target audience?', options: ['SaaS founders', 'E-commerce', 'Other'] },
    { id: 'timeline', question: 'Timeline?', options: ['This week', 'This month', 'This quarter'] },
];

import { createPortal } from "react-dom";

export function MoveCreateWizard({ isOpen, onClose, onComplete }: MoveCreateWizardProps) {
    const [step, setStep] = useState<WizardStep>('objective');
    const [category, setCategory] = useState<MoveCategory | null>(null);
    const [contextDesc, setContextDesc] = useState('');
    const [timeCommitment, setTimeCommitment] = useState<string | null>(null);
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [customAnswer, setCustomAnswer] = useState('');
    const [brief, setBrief] = useState<MoveBriefData | null>(null);
    const [execution, setExecution] = useState<ExecutionDay[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (isOpen) {
            setStep('objective');
            setCategory(null);
            setContextDesc('');
            setTimeCommitment(null);
            setCurrentQ(0);
            setAnswers({});
            setCustomAnswer('');
            setBrief(null);
            setExecution([]);
            setIsLoading(false);
            // Lock body scroll
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => { document.body.style.overflow = ''; };
    }, [isOpen]);

    const handleNext = async () => {
        if (step === 'objective' && category) {
            setStep('context');
        } else if (step === 'context' && contextDesc.trim() && timeCommitment) {
            setStep('clarify');
        } else if (step === 'clarify') {
            const q = CLARIFICATION_QUESTIONS[currentQ];
            const ans = answers[q.id] || customAnswer;
            if (!ans) return;

            if (currentQ < CLARIFICATION_QUESTIONS.length - 1) {
                setCurrentQ(prev => prev + 1);
                setCustomAnswer('');
            } else {
                setIsLoading(true);
                await new Promise(r => setTimeout(r, 1000));
                const b = generateMockBrief(category!, contextDesc);
                setBrief(b);
                setExecution(generateMockExecution(b));
                setIsLoading(false);
                setStep('preview');
            }
        } else if (step === 'preview') {
            onComplete({ category: category!, context: contextDesc, brief: brief!, execution });
        }
    };

    const handleBack = () => {
        if (step === 'context') setStep('objective');
        else if (step === 'clarify') {
            if (currentQ > 0) { setCurrentQ(p => p - 1); setCustomAnswer(''); }
            else setStep('context');
        }
        else if (step === 'preview') { setCurrentQ(CLARIFICATION_QUESTIONS.length - 1); setStep('clarify'); }
    };

    const canProceed = () => {
        if (step === 'objective') return !!category;
        if (step === 'context') return contextDesc.trim().length > 3 && !!timeCommitment;
        if (step === 'clarify') return !!answers[CLARIFICATION_QUESTIONS[currentQ].id] || customAnswer.length > 0;
        return step === 'preview' && execution.length > 0;
    };

    const progress = step === 'objective' ? 20 : step === 'context' ? 40 : step === 'clarify' ? 60 + (currentQ * 10) : 100;

    if (!isOpen || !mounted) return null;

    const cats = Object.keys(MOVE_CATEGORIES) as MoveCategory[];

    return createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-8">
            {/* Backdrop with blur */}
            <div
                className="absolute inset-0 bg-[var(--ink)]/40 backdrop-blur-md animate-in fade-in duration-200"
                onClick={onClose}
            />

            {/* MODAL - Premium design */}
            <div className="relative w-full max-w-md bg-[var(--paper)] rounded-[var(--radius-lg)] border border-[var(--border)] shadow-2xl animate-in zoom-in-95 fade-in slide-in-from-bottom-4 duration-300">
                {/* Registration marks */}
                <div className="absolute -top-1 -left-1 w-5 h-5 border-t-2 border-l-2 border-[var(--blueprint)] rounded-tl-lg" />
                <div className="absolute -top-1 -right-1 w-5 h-5 border-t-2 border-r-2 border-[var(--blueprint)] rounded-tr-lg" />
                <div className="absolute -bottom-1 -left-1 w-5 h-5 border-b-2 border-l-2 border-[var(--blueprint)] rounded-bl-lg" />
                <div className="absolute -bottom-1 -right-1 w-5 h-5 border-b-2 border-r-2 border-[var(--blueprint)] rounded-br-lg" />

                {/* Progress bar - Gradient */}
                <div className="h-1.5 bg-[var(--surface)] rounded-t-[var(--radius-lg)] overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-[var(--blueprint)] to-[var(--success)] transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                    />
                </div>

                {/* Header */}
                <div className="flex items-center justify-between px-5 py-3 border-b border-[var(--border)]">
                    <span className="font-semibold text-sm text-[var(--ink)]">
                        {step === 'objective' && 'Choose Objective'}
                        {step === 'context' && 'Details'}
                        {step === 'clarify' && `Question ${currentQ + 1}/3`}
                        {step === 'preview' && 'Ready!'}
                    </span>
                    <button
                        onClick={onClose}
                        className="p-1.5 hover:bg-[var(--surface)] rounded-lg transition-colors text-[var(--muted)] hover:text-[var(--ink)]"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* CONTENT - All steps fit without scrolling */}
                <div className="p-4">

                    {/* STEP 1: Objectives - 2x3 Grid, ultra compact */}
                    {step === 'objective' && (
                        <div className="grid grid-cols-2 gap-2">
                            {cats.map((cat) => {
                                const info = MOVE_CATEGORIES[cat];
                                const sel = category === cat;
                                return (
                                    <button
                                        key={cat}
                                        onClick={() => setCategory(cat)}
                                        className={cn(
                                            "flex items-center gap-2 p-2 rounded-lg border text-left text-xs transition-all",
                                            sel ? "bg-[var(--ink)] border-[var(--ink)] text-white" : "border-[var(--border)] hover:border-[var(--ink)]"
                                        )}
                                    >
                                        <span>{info.emoji}</span>
                                        <span className="font-medium truncate">{info.name}</span>
                                        {sel && <Check size={12} />}
                                    </button>
                                );
                            })}
                        </div>
                    )}

                    {/* STEP 2: Context - Compact */}
                    {step === 'context' && (
                        <div className="space-y-3">
                            <div>
                                <label className="text-xs font-medium text-[var(--ink)] mb-1 block">What's your goal?</label>
                                <textarea
                                    autoFocus
                                    className="w-full h-16 p-2 bg-[var(--surface)] border rounded-lg text-xs resize-none focus:ring-1 focus:ring-[var(--ink)] focus:outline-none"
                                    placeholder="E.g., Launch product and get 500 signups..."
                                    value={contextDesc}
                                    onChange={(e) => setContextDesc(e.target.value)}
                                />
                            </div>
                            <div>
                                <label className="text-xs font-medium text-[var(--ink)] mb-1 block">Daily time</label>
                                <div className="grid grid-cols-3 gap-2">
                                    {[{ id: 'light', l: '<30m' }, { id: 'std', l: '1-2h' }, { id: 'int', l: '2h+' }].map(t => (
                                        <button
                                            key={t.id}
                                            onClick={() => setTimeCommitment(t.id)}
                                            className={cn(
                                                "py-1.5 rounded-lg border text-xs font-medium transition-all",
                                                timeCommitment === t.id ? "bg-[var(--ink)] border-[var(--ink)] text-white" : "border-[var(--border)] hover:border-[var(--ink)]"
                                            )}
                                        >
                                            {t.l}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: Questions - One at a time, compact */}
                    {step === 'clarify' && (
                        <div>
                            {isLoading ? (
                                <div className="py-8 text-center">
                                    <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[var(--ink)]" />
                                    <p className="text-xs text-[var(--muted)]">Building plan...</p>
                                </div>
                            ) : (
                                <>
                                    <p className="text-sm text-[var(--ink)] text-center mb-3">
                                        {CLARIFICATION_QUESTIONS[currentQ].question}
                                    </p>
                                    <div className="grid grid-cols-3 gap-2">
                                        {CLARIFICATION_QUESTIONS[currentQ].options.map((opt, i) => {
                                            const qId = CLARIFICATION_QUESTIONS[currentQ].id;
                                            const isOther = opt === 'Other';
                                            const sel = answers[qId] === opt;
                                            return (
                                                <button
                                                    key={i}
                                                    onClick={() => {
                                                        setAnswers(p => ({ ...p, [qId]: opt }));
                                                        if (!isOther) setCustomAnswer('');
                                                    }}
                                                    className={cn(
                                                        "py-2 rounded-lg border text-xs font-medium transition-all",
                                                        sel ? "bg-[var(--ink)] border-[var(--ink)] text-white" : "border-[var(--border)] hover:border-[var(--ink)]"
                                                    )}
                                                >
                                                    {opt}
                                                </button>
                                            );
                                        })}
                                    </div>
                                    {answers[CLARIFICATION_QUESTIONS[currentQ].id] === 'Other' && (
                                        <input
                                            type="text"
                                            autoFocus
                                            placeholder="Type answer..."
                                            value={customAnswer}
                                            onChange={(e) => setCustomAnswer(e.target.value)}
                                            className="w-full mt-2 p-2 bg-[var(--surface)] border rounded-lg text-xs focus:ring-1 focus:ring-[var(--ink)] focus:outline-none"
                                        />
                                    )}
                                </>
                            )}
                        </div>
                    )}

                    {/* STEP 4: Preview - Compact summary only */}
                    {step === 'preview' && brief && (
                        <div className="text-center py-2">
                            <Sparkles className="mx-auto mb-2 text-[var(--success)]" size={28} />
                            <h3 className="font-semibold text-[var(--ink)]">{brief.name}</h3>
                            <p className="text-xs text-[var(--muted)] mb-3">{brief.duration} days • {MOVE_CATEGORIES[category!].name}</p>
                            <div className="bg-[var(--surface)] rounded-lg p-2 text-left text-xs text-[var(--ink-secondary)]">
                                <p className="line-clamp-2">{brief.goal}</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-4 py-2 border-t flex justify-between items-center">
                    {step !== 'objective' && !isLoading ? (
                        <button onClick={handleBack} className="text-xs text-[var(--muted)] hover:text-[var(--ink)] flex items-center gap-1">
                            <ArrowLeft size={12} /> Back
                        </button>
                    ) : <div />}

                    <BlueprintButton onClick={handleNext} disabled={!canProceed() || isLoading} className="text-xs py-1.5 px-3">
                        {isLoading ? <Loader2 size={12} className="animate-spin" /> :
                            step === 'preview' ? <><Check size={12} /> Create</> :
                                <>Next <ArrowRight size={12} /></>}
                    </BlueprintButton>
                </div>
            </div>
        </div>,
        document.body
    );
}

export default MoveCreateWizard;
