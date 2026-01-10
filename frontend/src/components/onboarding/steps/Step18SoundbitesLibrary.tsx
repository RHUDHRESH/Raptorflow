"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, MessageSquare, AlertCircle, ThumbsUp, Zap, ArrowRight, Target, Sparkles, RefreshCw, Lightbulb, Copy, Edit2 } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 18: Soundbites Library

   Approve, edit, and IMPROVE core marketing soundbites
   Now with AI-powered improvement suggestions
   ══════════════════════════════════════════════════════════════════════════════ */

interface Soundbite {
    id: string;
    category: string;
    label: string;
    content: string;
    approved: boolean;
    code: string;
}

interface ImprovementSuggestion {
    id: string;
    improved: string;
    reason: string;
}

const INITIAL_SOUNDBITES: Soundbite[] = [
    { id: "1", category: "Problem", label: "Pain Statement", content: "Founders waste 40% of their time on marketing guesswork instead of building.", approved: false, code: "SND-01" },
    { id: "2", category: "Problem", label: "Agitation", content: "Every week without clear positioning is money left on the table and competitors pulling ahead.", approved: false, code: "SND-02" },
    { id: "3", category: "Solution", label: "Unique Mechanism", content: "RaptorFlow's AI analyzes your existing content to extract and validate your positioning—in hours, not months.", approved: false, code: "SND-03" },
    { id: "4", category: "Proof", label: "Social Proof", content: "Join 500+ founders who transformed their marketing with validated positioning.", approved: false, code: "SND-04" },
    { id: "5", category: "Objection", label: "Handle: Too Expensive", content: "The average founder saves 10+ hours per week. At your hourly rate, RaptorFlow pays for itself in week one.", approved: false, code: "SND-05" },
    { id: "6", category: "Outcome", label: "Transformation", content: "Go from scattered marketing to a focused system that runs itself.", approved: false, code: "SND-06" },
    { id: "7", category: "CTA", label: "Primary CTA", content: "Start your free positioning audit today.", approved: false, code: "SND-07" },
];

const CATEGORIES = ["Problem", "Solution", "Proof", "Objection", "Outcome", "CTA"];

// Mock improvement suggestions based on category
function getMockSuggestions(soundbite: Soundbite): ImprovementSuggestion[] {
    const suggestions: Record<string, ImprovementSuggestion[]> = {
        Problem: [
            { id: "1", improved: `Most founders spend ${soundbite.content.includes("40%") ? "half their week" : "countless hours"} on marketing that doesn't move the needle—while competitors ship and scale.`, reason: "More visceral, competitor pressure added" },
            { id: "2", improved: `You didn't start a company to guess at marketing. Yet here you are, trying tactic after tactic with no clear playbook.`, reason: "Personal, founder-focused language" },
        ],
        Solution: [
            { id: "1", improved: `Give RaptorFlow your existing content—website, docs, decks—and get validated positioning in 24 hours, not 3 months.`, reason: "Specific timeline, input clarity" },
            { id: "2", improved: `Our AI reads what you've already created to find the positioning that's been hiding in plain sight.`, reason: "Reframes as discovery, not creation" },
        ],
        Proof: [
            { id: "1", improved: `"Finally, marketing that makes sense." — 500+ founders who've graduated from guesswork.`, reason: "Quote format adds authenticity" },
            { id: "2", improved: `Trusted by founders at companies you'd recognize—from seed stage to Series C.`, reason: "Stage-spanning credibility" },
        ],
        Objection: [
            { id: "1", improved: `Think about your hourly rate. Now multiply by the 10+ hours you'll save weekly. RaptorFlow costs less than one hour of your time.`, reason: "Math-based, founder-centric ROI" },
            { id: "2", improved: `Expensive compared to what? The consultant you'll hire? The months you'll lose? The customers going to competitors?`, reason: "Reframes the comparison" },
        ],
        Outcome: [
            { id: "1", improved: `From "what should I post today?" to "everything is connected and intentional."`, reason: "Before/after contrast" },
            { id: "2", improved: `Marketing that compounds instead of cycles. Build once, benefit forever.`, reason: "Investment framing" },
        ],
        CTA: [
            { id: "1", improved: `See your positioning in 24 hours—free.`, reason: "Time-bound, no-risk emphasis" },
            { id: "2", improved: `Get your positioning audit before your next team meeting.`, reason: "Time-anchored urgency" },
        ],
    };
    return suggestions[soundbite.category] || [
        { id: "1", improved: soundbite.content + " (Enhanced version)", reason: "Clarity improvement" }
    ];
}

// Soundbite Card with Improve functionality
function SoundbiteCard({
    soundbite,
    onEdit,
    onApprove,
    onUpdate
}: {
    soundbite: Soundbite;
    onEdit: () => void;
    onApprove: () => void;
    onUpdate: (content: string) => void;
}) {
    const [showImprove, setShowImprove] = useState(false);
    const [suggestions, setSuggestions] = useState<ImprovementSuggestion[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);

    const categoryIcons: Record<string, React.ElementType> = {
        Problem: AlertCircle, Solution: Zap, Proof: ThumbsUp,
        Objection: MessageSquare, Outcome: Target, CTA: ArrowRight
    };
    const Icon = categoryIcons[soundbite.category] || MessageSquare;

    const handleImprove = () => {
        setIsGenerating(true);
        setShowImprove(true);

        // Simulate AI generation
        setTimeout(() => {
            setSuggestions(getMockSuggestions(soundbite));
            setIsGenerating(false);
        }, 1000);
    };

    const applySuggestion = (improved: string) => {
        onUpdate(improved);
        setShowImprove(false);
    };

    return (
        <BlueprintCard
            code={soundbite.code}
            showCorners
            padding="md"
            className={soundbite.approved ? "border-[var(--success)]/30 bg-[var(--success-light)]" : ""}
        >
            {/* Header */}
            <div className="flex items-start gap-3 mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${soundbite.approved ? "bg-[var(--success)]" : "bg-[var(--canvas)] border border-[var(--border)]"
                    }`}>
                    <Icon size={16} strokeWidth={1.5} className={soundbite.approved ? "text-[var(--paper)]" : "text-[var(--muted)]"} />
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <BlueprintBadge variant="blueprint">{soundbite.category}</BlueprintBadge>
                        <span className="text-xs text-[var(--secondary)]">{soundbite.label}</span>
                        {soundbite.approved && <BlueprintBadge variant="success" dot>APPROVED</BlueprintBadge>}
                    </div>
                    <p className="text-sm text-[var(--ink)] leading-relaxed">"{soundbite.content}"</p>
                </div>
            </div>

            {/* Improvements Panel */}
            {showImprove && (
                <div className="mb-4 p-4 rounded-lg bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30">
                    <div className="flex items-center gap-2 mb-3">
                        <Sparkles size={14} className="text-[var(--blueprint)]" />
                        <span className="font-technical text-[10px] text-[var(--blueprint)]">AI SUGGESTIONS</span>
                    </div>

                    {isGenerating ? (
                        <div className="flex items-center gap-2 py-4">
                            <RefreshCw size={14} className="animate-spin text-[var(--blueprint)]" />
                            <span className="text-sm text-[var(--secondary)]">Generating improvements...</span>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {suggestions.map((suggestion, i) => (
                                <div key={suggestion.id} className="p-3 rounded-lg bg-[var(--paper)] border border-[var(--border)]">
                                    <div className="flex items-start justify-between gap-2 mb-2">
                                        <p className="text-sm text-[var(--ink)]">"{suggestion.improved}"</p>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-1.5">
                                            <Lightbulb size={10} className="text-[var(--warning)]" />
                                            <span className="text-[10px] text-[var(--secondary)]">{suggestion.reason}</span>
                                        </div>
                                        <button
                                            onClick={() => applySuggestion(suggestion.improved)}
                                            className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-technical bg-[var(--blueprint)] text-[var(--paper)] rounded-lg hover:bg-[var(--blueprint)]/80 transition-all"
                                        >
                                            <Check size={10} />USE THIS
                                        </button>
                                    </div>
                                </div>
                            ))}
                            <button
                                onClick={() => setShowImprove(false)}
                                className="w-full py-2 text-xs text-[var(--muted)] hover:text-[var(--ink)] transition-all"
                            >
                                Keep original
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-3 border-t border-[var(--border-subtle)]">
                <SecondaryButton size="sm" onClick={onEdit} className="flex-1">
                    <Edit2 size={10} strokeWidth={1.5} />Edit
                </SecondaryButton>
                <SecondaryButton size="sm" onClick={handleImprove} className="flex-1">
                    <Sparkles size={10} strokeWidth={1.5} />Improve
                </SecondaryButton>
                <BlueprintButton size="sm" onClick={onApprove} disabled={soundbite.approved} className="flex-1">
                    {soundbite.approved ? <><Check size={10} strokeWidth={1.5} />Approved</> : "Approve"}
                </BlueprintButton>
            </div>
        </BlueprintCard>
    );
}

export default function Step18SoundbitesLibrary() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(18)?.data as { soundbites?: Soundbite[] } | undefined;
    const [soundbites, setSoundbites] = useState<Soundbite[]>(stepData?.soundbites || INITIAL_SOUNDBITES);
    const [activeCategory, setActiveCategory] = useState<string>("all");
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editContent, setEditContent] = useState("");
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    const saveData = (updated: Soundbite[]) => {
        setSoundbites(updated);
        updateStepData(18, { soundbites: updated });
        if (updated.every((s) => s.approved)) updateStepStatus(18, "complete");
    };

    const handleEdit = (id: string, content: string) => saveData(soundbites.map((s) => (s.id === id ? { ...s, content } : s)));
    const handleApprove = (id: string) => saveData(soundbites.map((s) => (s.id === id ? { ...s, approved: true } : s)));
    const approveAll = () => saveData(soundbites.map((s) => ({ ...s, approved: true })));
    const startEdit = (s: Soundbite) => { setEditingId(s.id); setEditContent(s.content); };
    const saveEdit = () => { if (editingId) { handleEdit(editingId, editContent); setEditingId(null); } };

    const filteredSoundbites = activeCategory === "all" ? soundbites : soundbites.filter((s) => s.category === activeCategory);
    const approvedCount = soundbites.filter((s) => s.approved).length;

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Header */}
            <div data-animate className="text-center py-4">
                <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">Soundbites Library</h2>
                <p className="text-sm text-[var(--secondary)] max-w-lg mx-auto">
                    Review, improve, and approve your core marketing messages.
                    Use the <Sparkles size={12} className="inline text-[var(--blueprint)]" /> Improve button for AI-powered suggestions.
                </p>
            </div>

            {/* Progress */}
            <BlueprintCard data-animate figure="FIG. 01" title="Approval Progress" code="PROG" showCorners padding="md">
                <div className="flex items-center justify-between mb-4">
                    <p className="font-technical text-[var(--muted)]">{approvedCount} OF {soundbites.length} APPROVED</p>
                    {approvedCount < soundbites.length && (
                        <SecondaryButton size="sm" onClick={approveAll}>
                            <ThumbsUp size={10} strokeWidth={1.5} />Approve All
                        </SecondaryButton>
                    )}
                </div>
                <BlueprintProgress value={(approvedCount / soundbites.length) * 100} />
            </BlueprintCard>

            {/* Category Filters */}
            <div data-animate className="flex flex-wrap gap-2">
                <button
                    onClick={() => setActiveCategory("all")}
                    className={`px-4 py-2 font-technical text-[10px] rounded-lg transition-all ${activeCategory === "all"
                            ? "bg-[var(--blueprint)] text-[var(--paper)]"
                            : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)] hover:border-[var(--blueprint)]"
                        }`}
                >
                    ALL ({soundbites.length})
                </button>
                {CATEGORIES.map((cat) => (
                    <button
                        key={cat}
                        onClick={() => setActiveCategory(cat)}
                        className={`px-4 py-2 font-technical text-[10px] rounded-lg transition-all ${activeCategory === cat
                                ? "bg-[var(--blueprint)] text-[var(--paper)]"
                                : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)] hover:border-[var(--blueprint)]"
                            }`}
                    >
                        {cat.toUpperCase()} ({soundbites.filter((s) => s.category === cat).length})
                    </button>
                ))}
            </div>

            {/* Soundbites */}
            <div data-animate className="space-y-4">
                {filteredSoundbites.map((soundbite) => (
                    editingId === soundbite.id ? (
                        <BlueprintCard key={soundbite.id} code={soundbite.code} showCorners padding="md" className="border-[var(--blueprint)]">
                            <div className="space-y-3">
                                <div className="flex items-center gap-2">
                                    <BlueprintBadge variant="blueprint">{soundbite.category}</BlueprintBadge>
                                    <span className="text-xs text-[var(--secondary)]">{soundbite.label}</span>
                                </div>
                                <textarea
                                    value={editContent}
                                    onChange={(e) => setEditContent(e.target.value)}
                                    className="w-full min-h-[100px] p-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-lg text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                    autoFocus
                                />
                                <div className="flex gap-2">
                                    <BlueprintButton size="sm" onClick={saveEdit}>Save Changes</BlueprintButton>
                                    <SecondaryButton size="sm" onClick={() => setEditingId(null)}>Cancel</SecondaryButton>
                                </div>
                            </div>
                        </BlueprintCard>
                    ) : (
                        <SoundbiteCard
                            key={soundbite.id}
                            soundbite={soundbite}
                            onEdit={() => startEdit(soundbite)}
                            onApprove={() => handleApprove(soundbite.id)}
                            onUpdate={(content) => handleEdit(soundbite.id, content)}
                        />
                    )
                ))}
            </div>

            {/* Complete State */}
            {approvedCount === soundbites.length && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                            <Check size={24} strokeWidth={2} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="text-base font-serif text-[var(--ink)]">Soundbites Library Complete</span>
                            <p className="font-technical text-[10px] text-[var(--secondary)]">{soundbites.length} soundbites approved</p>
                        </div>
                        <BlueprintBadge variant="success" dot className="ml-auto">COMPLETE</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">SOUNDBITES • STEP 18/25</span>
            </div>
        </div>
    );
}
