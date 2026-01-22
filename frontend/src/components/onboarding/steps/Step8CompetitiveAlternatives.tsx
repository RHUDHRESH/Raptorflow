"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Check, Plus, Shield, Zap, Target, Trash2, Edit2, ChevronDown, ChevronUp,
    Play, RefreshCw, AlertTriangle, X, Swords, ArrowLeftRight, MoreHorizontal,
    Maximize2, Scale, ArrowUpRight, CheckCircle, Loader2, Sparkles
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { StepLoadingState } from "../StepStates";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 8: Comparative Angle

   PURPOSE: Define the "Upper Hand" against competitors.
   - "Quiet Luxury" Refactor: "Landscape Matrix".
   - Minimalist grid/table for comparison.
   - Focus on "Leverage" (Why we win).
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface Alternative {
    id: string;
    name: string;
    type: "status-quo" | "competitor";
    theirPromise: string;
    theirWeakness: string;
    yourLeverage: string;
}

interface ComparativeResult {
    alternatives: Alternative[];
    confirmed: boolean;
}

function VantagePointCard({
    alt,
    onEdit,
    onDelete
}: {
    alt: Alternative;
    onEdit: (alt: Alternative) => void;
    onDelete: (id: string) => void;
}) {
    return (
        <div className="group relative bg-[var(--paper)] border border-[var(--border-subtle)] hover:border-[var(--ink)] hover:shadow-md transition-all duration-300 p-6 flex flex-col h-full">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className={cn(
                            "w-1.5 h-1.5 rounded-full",
                            alt.type === "status-quo" ? "bg-[var(--muted)]" : "bg-[var(--error)]"
                        )} />
                        <span className="font-technical text-[10px] uppercase tracking-widest text-[var(--muted)]">
                            {alt.type === "status-quo" ? "The Inertia" : "The Rival"}
                        </span>
                    </div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">{alt.name}</h3>
                </div>
                <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button onClick={() => onEdit(alt)} className="p-1.5 hover:bg-[var(--canvas)] rounded text-[var(--muted)] hover:text-[var(--ink)]"><Edit2 size={12} /></button>
                    <button onClick={() => onDelete(alt.id)} className="p-1.5 hover:bg-[var(--error)]/10 rounded text-[var(--muted)] hover:text-[var(--error)]"><Trash2 size={12} /></button>
                </div>
            </div>

            <div className="flex-1 space-y-6">
                <div className="pl-4 border-l border-[var(--border-subtle)] group-hover:border-[var(--muted)] transition-colors">
                    <span className="block font-technical text-[9px] uppercase tracking-widest text-[var(--muted)] mb-1">Their Hook</span>
                    <p className="text-sm font-serif text-[var(--secondary)] italic">"{alt.theirPromise}"</p>
                </div>

                <div className="pl-4 border-l border-[var(--border-subtle)] group-hover:border-[var(--muted)] transition-colors">
                    <span className="block font-technical text-[9px] uppercase tracking-widest text-[var(--muted)] mb-1">The Gap</span>
                    <p className="text-sm font-serif text-[var(--secondary)]">{alt.theirWeakness}</p>
                </div>
            </div>

            <div className="mt-8 pt-4 border-t border-[var(--border-subtle)]">
                <div className="flex items-center gap-2 mb-2">
                    <Zap size={12} className="text-[var(--blueprint)]" fill="currentColor" />
                    <span className="font-technical text-[9px] uppercase tracking-widest text-[var(--blueprint)] font-bold">Your Leverage</span>
                </div>
                <p className="text-base font-serif font-medium text-[var(--ink)] leading-relaxed">
                    {alt.yourLeverage}
                </p>
            </div>
        </div>
    );
}

function EditAngleModal({
    alt,
    onClose,
    onSave
}: {
    alt: Alternative;
    onClose: () => void;
    onSave: (alt: Alternative) => void;
}) {
    const [data, setData] = useState(alt);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[var(--ink)]/20 backdrop-blur-[2px] animate-in fade-in duration-200">
            <div className="w-full max-w-lg bg-[var(--paper)] border border-[var(--border)] shadow-2xl p-8 relative">
                <button onClick={onClose} className="absolute top-4 right-4 text-[var(--muted)] hover:text-[var(--ink)]">
                    <X size={18} />
                </button>

                <h3 className="font-serif text-2xl text-[var(--ink)] mb-1">Define Leverage</h3>
                <p className="text-xs text-[var(--secondary)] mb-8 font-serif italic">How do you beat {data.name}?</p>

                <div className="space-y-6">
                    <div>
                        <label className="block text-[10px] font-technical uppercase tracking-widest text-[var(--muted)] mb-2">Adversary Name</label>
                        <input
                            value={data.name}
                            onChange={e => setData({ ...data, name: e.target.value })}
                            className="w-full border-b border-[var(--border)] bg-transparent py-1 text-lg font-serif text-[var(--ink)] focus:border-[var(--blueprint)] outline-none"
                            placeholder="e.g. Excel Spreadsheets"
                            autoFocus
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-[10px] font-technical uppercase tracking-widest text-[var(--muted)] mb-2">Type</label>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setData({ ...data, type: "status-quo" })}
                                    className={cn("px-2 py-1 text-[10px] uppercase border transition-colors", data.type === "status-quo" ? "border-[var(--ink)] text-[var(--ink)]" : "border-[var(--border)] text-[var(--muted)]")}
                                >
                                    Inertia
                                </button>
                                <button
                                    onClick={() => setData({ ...data, type: "competitor" })}
                                    className={cn("px-2 py-1 text-[10px] uppercase border transition-colors", data.type === "competitor" ? "border-[var(--ink)] text-[var(--ink)]" : "border-[var(--border)] text-[var(--muted)]")}
                                >
                                    Competitor
                                </button>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label className="block text-[10px] font-technical uppercase tracking-widest text-[var(--muted)] mb-2">Their Hook (Why people choose them)</label>
                        <input
                            value={data.theirPromise}
                            onChange={e => setData({ ...data, theirPromise: e.target.value })}
                            className="w-full border-b border-[var(--border)] bg-transparent py-1 text-sm text-[var(--ink)] focus:border-[var(--blueprint)] outline-none"
                            placeholder="e.g. It's free and everyone knows it"
                        />
                    </div>

                    <div>
                        <label className="block text-[10px] font-technical uppercase tracking-widest text-[var(--muted)] mb-2">The Gap (Why they fail)</label>
                        <input
                            value={data.theirWeakness}
                            onChange={e => setData({ ...data, theirWeakness: e.target.value })}
                            className="w-full border-b border-[var(--border)] bg-transparent py-1 text-sm text-[var(--ink)] focus:border-[var(--blueprint)] outline-none"
                            placeholder="e.g. Version control nightmares, data silos"
                        />
                    </div>

                    <div className="pt-2">
                        <label className="block text-[10px] font-technical uppercase tracking-widest text-[var(--blueprint)] mb-2 font-bold">Your Leverage (The Winning Move)</label>
                        <textarea
                            value={data.yourLeverage}
                            onChange={e => setData({ ...data, yourLeverage: e.target.value })}
                            className="w-full h-24 border border-[var(--blueprint)]/30 bg-[var(--blueprint)]/5 p-3 text-sm text-[var(--ink)] focus:border-[var(--blueprint)] outline-none resize-none"
                            placeholder="e.g. Single source of truth with real-time sync."
                        />
                    </div>

                    <div className="pt-4 flex justify-end gap-3">
                        <SecondaryButton size="sm" onClick={onClose}>Cancel</SecondaryButton>
                        <BlueprintButton size="sm" onClick={() => onSave(data)}>Save Strategy</BlueprintButton>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function Step8CompetitiveAlternatives() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(8)?.data as ComparativeResult | undefined;

    const [isGenerating, setIsGenerating] = useState(false);
    const [alternatives, setAlternatives] = useState<Alternative[]>(stepData?.alternatives || []);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [editingAlt, setEditingAlt] = useState<Alternative | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const hasData = alternatives.length > 0;

    // Fetch AI-generated competitor analysis
    const generateCompetitorAnalysis = useCallback(async () => {
        setIsGenerating(true);
        try {
            const step1Data = getStepById(1)?.data as { evidence?: any[] } | undefined;
            const foundationData = getStepById(0)?.data as { company_info?: any } | undefined;

            const response = await fetch('/api/onboarding/competitor-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: session?.sessionId || 'demo',
                    company_info: foundationData?.company_info || {},
                    evidence: step1Data?.evidence || []
                })
            });

            const data = await response.json();
            if (data.success && data.competitor_analysis?.competitors) {
                const newAlternatives: Alternative[] = data.competitor_analysis.competitors.map((comp: any, i: number) => ({
                    id: comp.id || `alt-${i}`,
                    name: comp.name,
                    type: "competitor",
                    theirPromise: comp.strengths?.[0] || "Unknown",
                    theirWeakness: comp.weaknesses?.[0] || "Unknown",
                    yourLeverage: comp.market_gap || "Differentiated approach"
                }));
                setAlternatives(newAlternatives);
                updateStepData(8, { alternatives: newAlternatives, confirmed: false });
            }
        } catch (err) {
            console.error('Failed to generate competitor analysis:', err);
        } finally {
            setIsGenerating(false);
        }
    }, [session?.sessionId, getStepById, updateStepData]);

    useEffect(() => {
        if (!containerRef.current || isGenerating) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power2.out" }
        );
    }, [hasData, isGenerating]);

    const generateAlternatives = useCallback(async () => {
        setIsGenerating(true);
        setTimeout(() => {
            const mock: Alternative[] = [
                {
                    id: "1",
                    name: "Spreadsheets & Docs",
                    type: "status-quo",
                    theirPromise: "Infinite flexibility and zero cost.",
                    theirWeakness: "Manual updates lead to stale data.",
                    yourLeverage: "Automated sync ensures 100% accuracy."
                },
                {
                    id: "2",
                    name: "Traditional Agency",
                    type: "competitor",
                    theirPromise: "Done-for-you service handling everything.",
                    theirWeakness: "Black box process, high retainers, slow speed.",
                    yourLeverage: "Full transparency and 10x faster execution."
                },
            ];
            setAlternatives(mock);
            updateStepData(8, { alternatives: mock });
            setIsGenerating(false);
        }, 1500);
    }, [updateStepData]);

    const handleSave = (alt: Alternative) => {
        const exists = alternatives.find(a => a.id === alt.id);
        const updated = exists ? alternatives.map(a => a.id === alt.id ? alt : a) : [...alternatives, alt];
        setAlternatives(updated);
        updateStepData(8, { alternatives: updated });
        setEditingAlt(null);
    };

    const handleDelete = (id: string) => {
        const updated = alternatives.filter(a => a.id !== id);
        setAlternatives(updated);
        updateStepData(8, { alternatives: updated });
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(8, { alternatives, confirmed: true });
        updateStepStatus(8, "complete");
    };

    const handleAddNew = () => {
        setEditingAlt({
            id: `alt-${Date.now()}`,
            name: "",
            type: "competitor",
            theirPromise: "",
            theirWeakness: "",
            yourLeverage: ""
        });
    };

    // 1. Loading
    if (isGenerating) {
        return (
            <StepLoadingState
                title="Analyzing Landscape"
                message="Mapping strategic vectors and leverage points..."
                stage="Calculating Advantage..."
            />
        );
    }

    // 2. Main
    return (
        <div ref={containerRef} className="max-w-6xl mx-auto space-y-12 pb-24">

            {/* Header */}
            <div data-animate className="flex justify-between items-end border-b border-[var(--border-subtle)] pb-8">
                <div>
                    <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Comparative Angle</h2>
                    <p className="text-[var(--secondary)] max-w-lg font-serif italic text-lg">
                        "Why should they choose you over doing nothing or choosing the other guy?"
                    </p>
                </div>
                {hasData && (
                    <BlueprintButton onClick={handleAddNew} size="sm">
                        <Plus size={12} /> Add Vantage Point
                    </BlueprintButton>
                )}
            </div>

            {/* Empty State */}
            {!hasData && (
                <div className="flex flex-col items-center justify-center min-h-[40vh] space-y-6">
                    <div className="p-6 rounded-full bg-[var(--canvas)] border border-[var(--border)]">
                        <Scale size={32} className="text-[var(--muted)]" strokeWidth={1} />
                    </div>
                    <div className="text-center max-w-md">
                        <h3 className="font-serif text-xl text-[var(--ink)] mb-2">Uncharted Territory</h3>
                        <p className="text-sm text-[var(--secondary)] mb-6">
                            Construct a matrix to visualize your strategic leverage against status quo and direct rivals.
                        </p>
                        <BlueprintButton onClick={generateCompetitorAnalysis} size="lg" className="px-8">
                            <Maximize2 size={14} fill="currentColor" />
                            <span>Map The Landscape</span>
                        </BlueprintButton>
                    </div>
                </div>
            )}

            {/* Matrix Grid */}
            {hasData && (
                <div data-animate className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {alternatives.map(alt => (
                        <VantagePointCard
                            key={alt.id}
                            alt={alt}
                            onEdit={setEditingAlt}
                            onDelete={handleDelete}
                        />
                    ))}

                    {/* Add New Ghost Card */}
                    <button
                        onClick={handleAddNew}
                        className="group flex flex-col items-center justify-center p-6 border border-dashed border-[var(--border)] hover:border-[var(--blueprint)] hover:bg-[var(--canvas)] transition-all min-h-[300px]"
                    >
                        <div className="w-12 h-12 rounded-full bg-[var(--canvas)] border border-[var(--border-subtle)] group-hover:border-[var(--blueprint)] flex items-center justify-center mb-4 transition-colors">
                            <Plus size={20} className="text-[var(--muted)] group-hover:text-[var(--blueprint)]" />
                        </div>
                        <span className="font-serif text-[var(--ink)]">Add Competitor</span>
                    </button>
                </div>
            )}

            {/* Footer */}
            {hasData && (
                <div data-animate className="flex justify-center pt-8 border-t border-[var(--border-subtle)]">
                    {!confirmed ? (
                        <BlueprintButton onClick={handleConfirm} size="lg" className="px-12 py-6">
                            <Swords size={16} />
                            <span>Confirm Leverage</span>
                        </BlueprintButton>
                    ) : (
                        <div className="flex items-center gap-2 text-[var(--success)] animate-in zoom-in-50">
                            <CheckCircle size={24} />
                            <span className="font-serif italic font-medium">Positioning Locked</span>
                        </div>
                    )}
                </div>
            )}

            {editingAlt && (
                <EditAngleModal
                    alt={editingAlt}
                    onClose={() => setEditingAlt(null)}
                    onSave={handleSave}
                />
            )}
        </div>
    );
}
