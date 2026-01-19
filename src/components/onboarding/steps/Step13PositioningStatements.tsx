"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Edit2, Quote, ArrowRight, FileText, Sparkles, Brain, Loader2 } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 13: Positioning Statements
   
   Theme: "The Manifesto"
   Refactored for Quiet Luxury:
   - "Document" aesthetic (Paper background, serif text).
   - Clear distinction between "Template/Structure" (Tech Mono) and "Content" (Serif).
   - Focus on drafting the core brand message.
   ══════════════════════════════════════════════════════════════════════════════ */

interface PositioningStatement {
    id: string;
    type: "elevator" | "tagline" | "value-prop";
    label: string;
    template: string;
    content: string;
    code: string;
    neuroscienceScore?: number;
    principle?: string;
}

const INITIAL_STATEMENTS: PositioningStatement[] = [
    {
        id: "1",
        type: "elevator",
        label: "Elevator Pitch",
        template: "For [target], [product] is the [category] that [key benefit] unlike [alternatives] because [unique differentiator].",
        content: "For founders scaling their first marketing team, RaptorFlow is the marketing operating system that validates positioning in hours, not months, unlike agencies or DIY approaches because it extracts and validates your positioning from existing evidence.",
        code: "STMT-01"
    },
    {
        id: "2",
        type: "tagline",
        label: "Tagline",
        template: "[Outcome], [how].",
        content: "Marketing. Finally under control.",
        code: "STMT-02"
    },
    {
        id: "3",
        type: "value-prop",
        label: "Value Proposition",
        template: "We help [audience] achieve [outcome] by [mechanism].",
        content: "We help lean teams build validated positioning by automating the extraction and testing of brand claims.",
        code: "STMT-03"
    },
];

export default function Step13PositioningStatements() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(14)?.data as { statements?: PositioningStatement[]; confirmed?: boolean } | undefined;

    const [statements, setStatements] = useState<PositioningStatement[]>(stepData?.statements || INITIAL_STATEMENTS);
    const [editing, setEditing] = useState<string | null>(null);
    const [editContent, setEditContent] = useState("");
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [isGeneratingAI, setIsGeneratingAI] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Generate AI copy using neuroscience principles
    const generateAICopy = async () => {
        setIsGeneratingAI(true);
        try {
            const response = await fetch('/api/onboarding/neuroscience-copy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: session?.sessionId || 'demo',
                    product_info: {
                        name: 'RaptorFlow',
                        key_benefit: 'validated positioning in hours',
                        target_emotion: 'confidence',
                        user_count: 'thousands of founders',
                    },
                    copy_types: ['headline', 'tagline', 'value_proposition'],
                })
            });
            
            const result = await response.json();
            
            // Map AI variants to our statement format
            if (result.variants && result.variants.length > 0) {
                const updatedStatements = statements.map((stmt, idx) => {
                    const variant = result.variants[idx] || result.variants[0];
                    return {
                        ...stmt,
                        content: variant?.text || stmt.content,
                        neuroscienceScore: Math.round((variant?.effectiveness_score || 0.75) * 100),
                        principle: variant?.principle || 'limbic',
                    };
                });
                setStatements(updatedStatements);
                saveData(updatedStatements);
            }
        } catch (error) {
            console.error('AI copy generation error:', error);
        }
        setIsGeneratingAI(false);
    };

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: "power2.out" }
        );
    }, []);

    const saveData = (stmts: PositioningStatement[]) => {
        setStatements(stmts);
        updateStepData(14, { statements: stmts });
    };

    const startEdit = (id: string) => {
        const stmt = statements.find((s) => s.id === id);
        if (stmt) {
            setEditing(id);
            setEditContent(stmt.content);
        }
    };

    const saveEdit = () => {
        if (!editing) return;
        saveData(statements.map((s) => (s.id === editing ? { ...s, content: editContent } : s)));
        setEditing(null);
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(14, { statements, confirmed: true });
        updateStepStatus(14, "complete");
    };

    return (
        <div ref={containerRef} className="max-w-4xl mx-auto space-y-10">
            {/* Header */}
            <div data-animate className="flex items-start justify-between border-b border-[var(--border-subtle)] pb-8">
                <div>
                    <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">The Brand Manifesto</h2>
                    <p className="text-[var(--secondary)] max-w-lg">
                        Codify your positioning into clear, repeatable statements. These are your source of truth for all marketing copy.
                    </p>
                </div>
                {!confirmed && (
                    <SecondaryButton onClick={generateAICopy} disabled={isGeneratingAI} className="shrink-0">
                        {isGeneratingAI ? (
                            <>
                                <Loader2 size={14} className="animate-spin" />
                                <span>Generating...</span>
                            </>
                        ) : (
                            <>
                                <Brain size={14} />
                                <span>AI Rewrite (6 Principles)</span>
                            </>
                        )}
                    </SecondaryButton>
                )}
            </div>

            <div className="space-y-8">
                {statements.map((stmt, i) => (
                    <div
                        key={stmt.id}
                        data-animate
                        className={`group relative transition-all duration-300 ${editing === stmt.id ? "scale-[1.01]" : ""}`}
                    >
                        {/* The logic of the "Document" */}
                        <div className={`
                            relative p-8 rounded-[var(--radius-sm)] border transition-all duration-300 overflow-hidden
                            ${editing === stmt.id
                                ? "bg-[var(--paper)] border-[var(--blueprint)] shadow-lg ring-1 ring-[var(--blueprint)]/20"
                                : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--ink)]"
                            }
                        `}>
                            {/* Label / Type */}
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-full bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                        <Quote size={14} className="text-[var(--ink)]" />
                                    </div>
                                    <span className="font-technical text-[10px] uppercase tracking-widest text-[var(--muted)]">
                                        {stmt.code} • {stmt.label}
                                    </span>
                                    {stmt.neuroscienceScore && (
                                        <div className="flex items-center gap-2 px-2 py-1 bg-[var(--success)]/10 rounded">
                                            <Brain size={10} className="text-[var(--success)]" />
                                            <span className="font-technical text-[9px] text-[var(--success)]">
                                                {stmt.neuroscienceScore}% • {stmt.principle?.toUpperCase()}
                                            </span>
                                        </div>
                                    )}
                                </div>
                                {editing !== stmt.id && !confirmed && (
                                    <button
                                        onClick={() => startEdit(stmt.id)}
                                        className="opacity-0 group-hover:opacity-100 flex items-center gap-2 text-xs font-medium text-[var(--muted)] hover:text-[var(--blueprint)] transition-all"
                                    >
                                        <Edit2 size={12} />
                                        <span>Edit</span>
                                    </button>
                                )}
                            </div>

                            {/* Template Hint */}
                            <div className="mb-6 pl-4 border-l-2 border-[var(--border-subtle)]">
                                <p className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-wider mb-1">Structure</p>
                                <p className="font-technical text-xs text-[var(--secondary)] opacity-70 leading-relaxed font-normal">
                                    {stmt.template}
                                </p>
                            </div>

                            {/* Content Editor vs Display */}
                            {editing === stmt.id ? (
                                <div className="space-y-4 animate-in fade-in duration-300">
                                    <textarea
                                        value={editContent}
                                        onChange={(e) => setEditContent(e.target.value)}
                                        className="w-full min-h-[120px] p-4 text-base font-serif text-[var(--ink)] bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:border-[var(--blueprint)] focus:ring-1 focus:ring-[var(--blueprint)]/10 resize-none leading-relaxed"
                                        autoFocus
                                        placeholder="Draft your statement here..."
                                    />
                                    <div className="flex justify-end gap-3">
                                        <SecondaryButton size="sm" onClick={() => setEditing(null)}>Cancel</SecondaryButton>
                                        <BlueprintButton size="sm" onClick={saveEdit}>Save Draft</BlueprintButton>
                                    </div>
                                </div>
                            ) : (
                                <div className="relative">
                                    <p className="font-serif text-lg md:text-xl text-[var(--ink)] leading-relaxed">
                                        {stmt.content}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Confirmation Footer */}
            <div className="flex justify-between items-center pt-8 border-t border-[var(--border-subtle)]">
                <div className="flex items-center gap-2">
                    <FileText size={14} className="text-[var(--muted)]" />
                    <span className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest">
                        Draft Status: {confirmed ? "LOCKED" : "IN PROGRESS"}
                    </span>
                </div>

                {!confirmed ? (
                    <BlueprintButton onClick={handleConfirm} size="lg" className="px-8">
                        <span>Ratify Manifesto</span>
                        <ArrowRight size={14} />
                    </BlueprintButton>
                ) : (
                    <div className="flex items-center gap-2 text-[var(--success)]">
                        <Check size={18} />
                        <span className="font-serif italic">Manifesto Ratified</span>
                    </div>
                )}
            </div>
        </div>
    );
}
