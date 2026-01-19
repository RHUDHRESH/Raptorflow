"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
    Brain, Target, MessageSquare, Zap, Feather,
    Sparkles, BookOpen, ChevronRight, Check
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 12: Positioning Statements (Compact)
   
   PURPOSE: "No Scroll" Messaging Builder.
   - Using CSS Grid for tight layouts.
   - Collapsible / Side-by-side Input + Preview.
   ══════════════════════════════════════════════════════════════════════════════ */

type MessagingLevel = "positioning" | "uvp" | "oneliner" | "tagline" | "proof";

interface MessagingState {
    level: MessagingLevel;
    data: {
        positioning: { category: string; audience: string; challenge: string; benefit: string; differentiator: string; statement: string };
        uvp: { benefit: string; challenge: string; solution: string; statement: string };
        oneliner: { problem: string; solution: string; result: string; statement: string };
        tagline: { keywords: string[]; selected: string };
        proof: { points: string[] };
    };
}

const NEURO_CONTEXT = {
    positioning: { title: "Strategic North Star", principle: "Cognitive Fluency", icon: Target, desc: "The brain craves categorization. Define your category or the market will define it for you." },
    uvp: { title: "Unique Value Proposition", principle: "Limbic Resonance", icon: Zap, desc: "People buy better versions of themselves. Bridge the gap between pain and future." },
    oneliner: { title: "The One-Liner", principle: "Neural Coupling", icon: MessageSquare, desc: "Storytelling mirrors brain activity. Problem -> Solution -> Result creates a dopamine reward." },
    tagline: { title: "The Tagline", principle: "Pattern Recognition", icon: Feather, desc: "The brain seeks rhythm. Use rhyme, alliteration, or repetition to engineer a sticky phrase." },
    proof: { title: "Supporting Evidence", principle: "Social Proof", icon: BookOpen, desc: "Silence the amygdala (fear) with undeniable facts and authority." }
};

export default function Step12PositioningStatements() {
    const { updateStepStatus } = useOnboardingStore();
    const [level, setLevel] = useState<MessagingLevel>("positioning");

    const [state, setState] = useState<MessagingState>({
        level: "positioning",
        data: {
            positioning: { category: "", audience: "", challenge: "", benefit: "", differentiator: "", statement: "" },
            uvp: { benefit: "", challenge: "", solution: "", statement: "" },
            oneliner: { problem: "", solution: "", result: "", statement: "" },
            tagline: { keywords: [], selected: "" },
            proof: { points: ["", "", ""] }
        }
    });

    const generateDraft = (type: MessagingLevel) => {
        if (type === 'positioning') {
            const { audience, category, benefit, differentiator } = state.data.positioning;
            setState(p => ({ ...p, data: { ...p.data, positioning: { ...p.data.positioning, statement: `For ${audience || '[Audience]'}, ${category || '[Category]'} is the only solution that ${benefit || '[Benefit]'} because ${differentiator || '[Reason]'}.` } } }));
        }
        if (type === 'uvp') {
            const { benefit, challenge, solution } = state.data.uvp;
            setState(p => ({ ...p, data: { ...p.data, uvp: { ...p.data.uvp, statement: `${benefit || 'Get Results'} without ${challenge || 'the pain'}. The ${solution || 'solution'} that works.` } } }));
        }
        if (type === 'oneliner') {
            const { problem, solution, result } = state.data.oneliner;
            setState(p => ({ ...p, data: { ...p.data, oneliner: { ...p.data.oneliner, statement: `${problem || 'Problem'}. ${solution || 'Solution'}. ${result || 'Result'}.` } } }));
        }
    };

    const nextLevel = () => {
        const order: MessagingLevel[] = ["positioning", "uvp", "oneliner", "tagline", "proof"];
        const idx = order.indexOf(level);
        if (idx < order.length - 1) setLevel(order[idx + 1]);
        else updateStepStatus(12, "complete");
    };

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            gsap.fromTo(containerRef.current.querySelectorAll('.animate-section'), { opacity: 0, x: 10 }, { opacity: 1, x: 0, duration: 0.3, clearProps: "all" });
        }
    }, [level]);

    const NeuroIcon = NEURO_CONTEXT[level].icon;

    return (
        <div ref={containerRef} className="h-full flex flex-col overflow-hidden">
            {/* 1. Header (Compact) */}
            <div className="flex items-center justify-between border-b border-[var(--border)] pb-4 mb-6 shrink-0">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-[var(--paper)] border border-[var(--border-subtle)] rounded text-[var(--blueprint)]">
                        <NeuroIcon size={18} />
                    </div>
                    <div>
                        <h2 className="font-serif text-2xl text-[var(--ink)]">{NEURO_CONTEXT[level].title}</h2>
                        <div className="flex items-center gap-2">
                            <span className="text-[10px] font-technical uppercase tracking-wider text-[var(--accent)]">{NEURO_CONTEXT[level].principle}</span>
                            <span className="text-[10px] text-[var(--muted)] truncate max-w-sm hidden md:block border-l border-[var(--border-subtle)] pl-2 ml-2">"{NEURO_CONTEXT[level].desc}"</span>
                        </div>
                    </div>
                </div>

                {/* Level Tabs (Mini) */}
                <div className="flex gap-px bg-[var(--structure)] p-px rounded overflow-hidden">
                    {(["positioning", "uvp", "oneliner", "tagline", "proof"] as MessagingLevel[]).map((tab, i) => (
                        <button key={tab} onClick={() => setLevel(tab)} className={cn("px-3 py-1 text-[10px] font-medium uppercase transition-colors", level === tab ? "bg-[var(--paper)] text-[var(--ink)] shadow-sm" : "bg-[var(--canvas)] text-[var(--muted)] hover:text-[var(--ink-secondary)]")}>
                            {i + 1}
                        </button>
                    ))}
                </div>
            </div>

            {/* 2. Main Content (No Scroll) */}
            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-2 gap-8 animate-section">

                {/* LEFT: Inputs */}
                <div className="flex flex-col gap-5 overflow-y-auto pr-2">
                    {level === "positioning" && (
                        <>
                            <div className="grid grid-cols-2 gap-4">
                                <InputGroup label="Category" placeholder="e.g. CRM for Creators" value={state.data.positioning.category} onChange={v => setState(p => ({ ...p, data: { ...p.data, positioning: { ...p.data.positioning, category: v } } }))} />
                                <InputGroup label="Audience" placeholder="e.g. Freelance Designers" value={state.data.positioning.audience} onChange={v => setState(p => ({ ...p, data: { ...p.data, positioning: { ...p.data.positioning, audience: v } } }))} />
                            </div>
                            <InputGroup label="Core Benefit" placeholder="e.g. Double your leads" value={state.data.positioning.benefit} onChange={v => setState(p => ({ ...p, data: { ...p.data, positioning: { ...p.data.positioning, benefit: v } } }))} />
                            <InputGroup label="Radical Differentiator" placeholder="e.g. AI-Powered Automation" value={state.data.positioning.differentiator} onChange={v => setState(p => ({ ...p, data: { ...p.data, positioning: { ...p.data.positioning, differentiator: v } } }))} />
                        </>
                    )}

                    {level === "uvp" && (
                        <>
                            <InputGroup label="Core Benefit (Lead)" placeholder="e.g. Get rides in minutes" value={state.data.uvp.benefit} onChange={v => setState(p => ({ ...p, data: { ...p.data, uvp: { ...p.data.uvp, benefit: v } } }))} />
                            <InputGroup label="The Challenge" placeholder="e.g. No more waving at taxis" value={state.data.uvp.challenge} onChange={v => setState(p => ({ ...p, data: { ...p.data, uvp: { ...p.data.uvp, challenge: v } } }))} />
                            <InputGroup label="The Solution" placeholder="e.g. Vetted drivers via app" value={state.data.uvp.solution} onChange={v => setState(p => ({ ...p, data: { ...p.data, uvp: { ...p.data.uvp, solution: v } } }))} />
                        </>
                    )}

                    {level === "oneliner" && (
                        <>
                            <InputArea label="The Problem (Hook)" placeholder="Marketing software is too complex..." value={state.data.oneliner.problem} onChange={v => setState(p => ({ ...p, data: { ...p.data, oneliner: { ...p.data.oneliner, problem: v } } }))} />
                            <InputArea label="The Solution (Guide)" placeholder="We built a platform that automates..." value={state.data.oneliner.solution} onChange={v => setState(p => ({ ...p, data: { ...p.data, oneliner: { ...p.data.oneliner, solution: v } } }))} />
                            <InputArea label="The Result (Transformation)" placeholder="So you can punch above your weight..." value={state.data.oneliner.result} onChange={v => setState(p => ({ ...p, data: { ...p.data, oneliner: { ...p.data.oneliner, result: v } } }))} />
                        </>
                    )}

                    {level === "tagline" && (
                        <div className="space-y-3">
                            <p className="text-xs text-[var(--secondary)]">Select a rhythmic pattern:</p>
                            {["Stop Guessing. Start Executing.", "Marketing. Finally Under Control.", "The Operating System for Founders."].map((opt, i) => (
                                <button key={i} onClick={() => setState(p => ({ ...p, data: { ...p.data, tagline: { ...p.data.tagline, selected: opt } } }))}
                                    className={cn("w-full p-4 text-left border rounded transition-all font-serif text-lg flex justify-between items-center group", state.data.tagline.selected === opt ? "bg-[var(--ink)] text-[var(--paper)] border-[var(--ink)]" : "bg-[var(--paper)] border-[var(--border)] text-[var(--ink)] hover:border-[var(--blueprint)]")}>
                                    {opt}
                                    {state.data.tagline.selected === opt && <Check size={16} />}
                                </button>
                            ))}
                        </div>
                    )}

                    {level === "proof" && (
                        <div className="space-y-4">
                            {[0, 1, 2].map(i => (
                                <div key={i} className="flex gap-2 items-center">
                                    <span className="font-mono text-[var(--muted)] text-xs">0{i + 1}</span>
                                    <input className="flex-1 bg-transparent border-b border-[var(--border)] py-2 text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] text-sm"
                                        placeholder="e.g. 'Used by 500+ YC Founders'"
                                        value={state.data.proof.points[i]}
                                        onChange={e => { const n = [...state.data.proof.points]; n[i] = e.target.value; setState(p => ({ ...p, data: { ...p.data, proof: { ...p.data.proof, points: n } } })); }}
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* RIGHT: Preview (Fixed) */}
                <div className="h-full bg-[var(--surface)] border border-[var(--border-subtle)] rounded p-6 flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <span className="text-[10px] font-technical uppercase tracking-widest text-[var(--muted)]">GENERATED DRAFT</span>
                        {level !== 'tagline' && level !== 'proof' && (
                            <button onClick={() => generateDraft(level)} className="text-[var(--blueprint)] hover:text-[var(--ink)] text-xs font-medium flex items-center gap-1 transition-colors">
                                <Sparkles size={12} /> Auto-Generate
                            </button>
                        )}
                    </div>

                    <div className="flex-1 flex items-center justify-center text-center">
                        {level === 'tagline' ? (
                            <h3 className="font-serif text-3xl text-[var(--ink)]">{state.data.tagline.selected || "Select a tagline..."}</h3>
                        ) : level === 'proof' ? (
                            <ul className="text-left space-y-2">
                                {state.data.proof.points.map((p, i) => <li key={i} className="flex gap-2 text-[var(--ink)]"><span className="text-[var(--accent)]">•</span> {p || "..."}</li>)}
                            </ul>
                        ) : (
                            <p className="font-serif text-xl text-[var(--ink)] leading-relaxed italic">
                                {level === 'positioning' && (state.data.positioning.statement || "Fill in the details to draft your strategic statement...")}
                                {level === 'uvp' && (state.data.uvp.statement || "Draft your unique value proposition...")}
                                {level === 'oneliner' && (state.data.oneliner.statement || "Tell your hero's story...")}
                            </p>
                        )}
                    </div>

                    <div className="mt-6 pt-4 border-t border-[var(--border-subtle)]/50">
                        <div className="flex justify-between items-center">
                            <SecondaryButton size="sm" onClick={() => { const ord: MessagingLevel[] = ["positioning", "uvp", "oneliner", "tagline", "proof"]; const i = ord.indexOf(level); if (i > 0) setLevel(ord[i - 1]); }} disabled={level === 'positioning'}>Back</SecondaryButton>
                            <BlueprintButton size="sm" onClick={nextLevel}>{level === 'proof' ? "Finish" : "Next"} <ChevronRight size={14} /></BlueprintButton>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Helpers
function InputGroup({ label, value, onChange, placeholder }: { label: string, value: string, onChange: (v: string) => void, placeholder: string }) {
    return (
        <div className="space-y-1.5">
            <label className="text-[10px] font-medium text-[var(--secondary)] uppercase tracking-wide">{label}</label>
            <input className="w-full bg-[var(--paper)] border border-[var(--border)] rounded px-3 py-2 text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--muted)]/40 transition-all"
                placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)} />
        </div>
    );
}

function InputArea({ label, value, onChange, placeholder }: { label: string, value: string, onChange: (v: string) => void, placeholder: string }) {
    return (
        <div className="space-y-1.5">
            <label className="text-[10px] font-medium text-[var(--secondary)] uppercase tracking-wide">{label}</label>
            <textarea className="w-full bg-[var(--paper)] border border-[var(--border)] rounded px-3 py-2 text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--muted)]/40 h-20 resize-none transition-all"
                placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)} />
        </div>
    );
}
