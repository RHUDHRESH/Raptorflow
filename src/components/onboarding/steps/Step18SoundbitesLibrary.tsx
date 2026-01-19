"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import { Copy, Wand2, Check, RefreshCcw, Save, MessageSquareText, Loader2, Sparkles, CheckCircle } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 18: Soundbites Library (Copy Refinement)
   
   PURPOSE: "No Scroll" Copy Editor.
   - Core Fields: Problem, Agitation, Mechanism, Social Proof, Expertise, Transformation, CTA.
   - Logic: "Approve" or "Improve".
   - Shows previously collected data as a starting point.
   ══════════════════════════════════════════════════════════════════════════════ */

interface Soundbite {
    id: string;
    label: string;
    content: string;
    status: "draft" | "approved";
}

const DEFAULT_SOUNDBITES: Soundbite[] = [
    { id: "problem", label: "Problem Statement", content: "Founders are wasting 20h/week on marketing that doesn't convert.", status: "draft" },
    { id: "agitation", label: "Agitation", content: "That's time stolen from product, hiring, and deep work—essentially bleeding runway.", status: "draft" },
    { id: "mechanism", label: "Unique Mechanism", content: "A 5-Step Narrative Engine that turns raw context into publish-ready assets automatically.", status: "draft" },
    { id: "proof", label: "Social Proof", content: "Trusted by 50+ Series A founders who reclaimed their calendars.", status: "draft" },
    { id: "transformation", label: "Transformation", content: "From 'Guessing & Stressing' to 'Executing with Surgical Precision'.", status: "draft" },
    { id: "cta", label: "Primary CTA", content: "Audit Your Strategy Free", status: "draft" },
];

export default function Step17SoundbitesLibrary() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(18)?.data as any; // Map to 18

    const [soundbites, setSoundbites] = useState<Soundbite[]>(stepData?.soundbites || DEFAULT_SOUNDBITES);
    const [activeId, setActiveId] = useState<string>(DEFAULT_SOUNDBITES[0].id);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [isGenerating, setIsGenerating] = useState(false);

    // For editing
    const activeBite = soundbites.find(s => s.id === activeId)!;
    const [editText, setEditText] = useState(activeBite.content);

    const containerRef = useRef<HTMLDivElement>(null);

    // Fetch AI-generated soundbites
    const generateSoundbites = useCallback(async () => {
        setIsGenerating(true);
        try {
            const foundationData = getStepById(0)?.data as { company_info?: any } | undefined;
            const positioningData = getStepById(12)?.data as { positioning?: any } | undefined;
            const icpData = getStepById(15)?.data as { icp_deep?: any } | undefined;
            
            const response = await fetch('/api/onboarding/soundbites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: 'demo',
                    company_info: foundationData?.company_info || {},
                    positioning: positioningData?.positioning || {},
                    icp_data: icpData?.icp_deep || {}
                })
            });
            
            const data = await response.json();
            if (data.success && data.soundbites?.library) {
                const newSoundbites: Soundbite[] = data.soundbites.library.map((sb: any, i: number) => ({
                    id: sb.id || `sb-${i}`,
                    label: sb.type === 'tagline' ? 'Tagline' : sb.type === 'value_prop' ? 'Value Prop' : sb.type,
                    content: sb.content,
                    status: "draft" as const
                }));
                
                // Merge with default, prioritize AI-generated
                const mergedSoundbites = [...DEFAULT_SOUNDBITES];
                newSoundbites.forEach((aiBite, index) => {
                    if (index < mergedSoundbites.length) {
                        mergedSoundbites[index] = { ...mergedSoundbites[index], content: aiBite.content };
                    }
                });
                
                setSoundbites(mergedSoundbites);
                updateStepData(18, { soundbites: mergedSoundbites, confirmed: false });
            }
        } catch (err) {
            console.error('Failed to generate soundbites:', err);
        } finally {
            setIsGenerating(false);
        }
    }, [getStepById, updateStepData]);

    // Sync input when switching active item
    useEffect(() => {
        setEditText(activeBite.content);
    }, [activeId]);

    const handleSave = () => {
        const updated = soundbites.map(s => s.id === activeId ? { ...s, content: editText, status: "approved" as const } : s);
        setSoundbites(updated);

        // Auto-advance if last one? Maybe.
    };

    const handleImprove = () => {
        // Mock AI improvement
        setEditText(activeBite.content + " (Improved with AI... more punchy keywords added.)");
    };

    const handleFinish = () => {
        setConfirmed(true);
        updateStepData(18, { soundbites, confirmed: true });
        updateStepStatus(18, "complete");
    };

    const approvalProgress = soundbites.filter(s => s.status === "approved").length / soundbites.length;

    return (
        <div ref={containerRef} className="h-full flex flex-col max-w-5xl mx-auto pb-4">

            {/* Header */}
            <div className="flex justify-between items-end mb-6 shrink-0 border-b border-[var(--border-subtle)] pb-4">
                <div>
                    <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 18 / 23</span>
                    <h2 className="font-serif text-2xl text-[var(--ink)]">Soundbites Library</h2>
                </div>
                <div className="flex flex-col items-end gap-2">
                    <BlueprintButton 
                        onClick={generateSoundbites} 
                        disabled={isGenerating}
                        size="sm"
                    >
                        {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                        {isGenerating ? "Generating..." : "AI Generate"}
                    </BlueprintButton>
                    <div className="flex items-center gap-2">
                        <span className="font-technical text-[10px] uppercase text-[var(--muted)]">Library Status</span>
                        <div className="w-24 h-1.5 bg-[var(--border)] rounded-full overflow-hidden">
                            <div className="h-full bg-[var(--blueprint)] transition-all duration-500" style={{ width: `${approvalProgress * 100}%` }} />
                        </div>
                        <span className="text-xs font-medium">{Math.round(approvalProgress * 100)}%</span>
                    </div>
                </div>
            </div>

            {/* Main Content: Layout - Left List / Right Editor */}
            <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Left: Selector List */}
                <div className="md:col-span-1 border-r border-[var(--border-subtle)] pr-4 overflow-y-auto space-y-2">
                    {soundbites.map((bite) => (
                        <button
                            key={bite.id}
                            onClick={() => setActiveId(bite.id)}
                            className={cn(
                                "w-full text-left p-3 rounded text-sm transition-all flex items-center justify-between group",
                                activeId === bite.id
                                    ? "bg-[var(--ink)] text-[var(--paper)]"
                                    : "bg-[var(--paper)] text-[var(--ink)] hover:bg-[var(--canvas)]"
                            )}
                        >
                            <span className="font-medium truncate">{bite.label}</span>
                            {bite.status === "approved" && (
                                <CheckCircle size={14} className={activeId === bite.id ? "text-[var(--success)]" : "text-[var(--success)]"} />
                            )}
                        </button>
                    ))}
                </div>

                {/* Right: Focused Editor */}
                <div className="md:col-span-2 flex flex-col gap-4">
                    <BlueprintCard padding="lg" title={activeBite.label} className="flex-1 flex flex-col">
                        <textarea
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            className="flex-1 w-full bg-[var(--canvas)] border border-[var(--border)] rounded p-4 text-[var(--ink)] font-serif text-lg leading-relaxed focus:outline-none focus:border-[var(--blueprint)] resize-none mb-4"
                            placeholder="Draft your soundbite here..."
                        />

                        <div className="flex justify-between items-center bg-[var(--paper)]">
                            <SecondaryButton onClick={handleImprove} size="sm">
                                <Wand2 size={14} /> AI Improve
                            </SecondaryButton>

                            <div className="flex gap-2">
                                <SecondaryButton onClick={() => setEditText(activeBite.content)} size="sm" title="Revert">
                                    <RefreshCcw size={14} />
                                </SecondaryButton>
                                <BlueprintButton onClick={handleSave} size="sm" className={activeBite.status === "approved" && editText === activeBite.content ? "bg-[var(--success)] border-[var(--success)] text-[var(--paper)]" : ""}>
                                    <Check size={14} /> {activeBite.status === "approved" ? "Updated" : "Approve & Save"}
                                </BlueprintButton>
                            </div>
                        </div>
                    </BlueprintCard>

                    {/* Footer Action (Contextual) */}
                    <div className="flex justify-end pt-2">
                        {approvalProgress === 1 && !confirmed && (
                            <BlueprintButton onClick={handleFinish} className="animate-in">
                                Finalize Library <Save size={14} />
                            </BlueprintButton>
                        )}
                        {confirmed && (
                            <div className="text-[var(--success)] text-sm font-medium flex items-center gap-2">
                                <CheckCircle size={16} /> All Soundbites Locked
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
