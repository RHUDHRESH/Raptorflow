"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Check, Lock, AlertTriangle, ChevronDown, ChevronUp, Edit2, ExternalLink,
    HelpCircle, Unlock, History, FileText, ShieldCheck, Loader2, Sparkles
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { StepEmptyState } from "../StepStates";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 4: Validate Truth Sheet

   PURPOSE: Review and lock validated facts as the "Business Truth Sheet v1"
   - "Quiet Luxury" Refactor: Looks like a legal/financial document.
   - High contrast, serif typography for document feel.
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface TruthItem {
    id: string;
    category: string;
    label: string;
    value: string;
    status: "confirmed" | "needs-review" | "edited" | "unknown";
    proofLinked: boolean;
    source?: string;
    code: string;
    stakeholderNotes?: string;
}

interface TruthSheetVersion {
    version: string;
    createdAt: Date;
    itemCount: number;
}

function TruthItemRow({
    item,
    onConfirm,
    onEdit,
    onMarkUnknown,
    isLocked
}: {
    item: TruthItem;
    onConfirm: (id: string) => void;
    onEdit: (id: string, value: string, notes?: string) => void;
    onMarkUnknown: (id: string, notes: string) => void;
    isLocked: boolean;
}) {
    const [isEditing, setIsEditing] = useState(false);
    const [editValue, setEditValue] = useState(item.value);
    const [showNotes, setShowNotes] = useState(false);
    const [notes, setNotes] = useState(item.stakeholderNotes || "");

    const handleSave = () => {
        onEdit(item.id, editValue, notes);
        setIsEditing(false);
    };

    const isConfirmed = item.status === "confirmed" || item.status === "edited";

    return (
        <div className={`group relative py-4 border-b border-[var(--border-subtle)] last:border-0 hover:bg-[var(--canvas)] transition-colors ${isLocked ? "opacity-80" : ""}`}>

            <div className="flex items-start gap-6 px-4">
                {/* Status Indicator (Left Gutter) */}
                <div className="pt-1">
                    {isConfirmed ? (
                        <div className="w-4 h-4 rounded-full border border-[var(--success)] flex items-center justify-center">
                            <Check size={8} className="text-[var(--success)]" />
                        </div>
                    ) : item.status === "unknown" ? (
                        <div className="w-4 h-4 rounded-full border border-[var(--muted)] flex items-center justify-center">
                            <HelpCircle size={8} className="text-[var(--muted)]" />
                        </div>
                    ) : (
                        <div className="w-4 h-4 rounded-full border border-[var(--warning)] bg-[var(--warning)]/10" />
                    )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-baseline justify-between mb-1">
                        <span className="font-technical text-[10px] tracking-widest text-[var(--muted)] uppercase">{item.label}</span>
                        <span className="font-technical text-[10px] text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-opacity">{item.code}</span>
                    </div>

                    {isEditing && !isLocked ? (
                        <div className="mt-2 space-y-3">
                            <input
                                type="text"
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                className="w-full p-2 text-base font-serif bg-[var(--paper)] border-b border-[var(--blueprint)] text-[var(--ink)] focus:outline-none"
                                autoFocus
                            />
                            <div className="flex gap-2">
                                <BlueprintButton size="sm" onClick={handleSave}>Save Change</BlueprintButton>
                                <SecondaryButton size="sm" onClick={() => setIsEditing(false)}>Cancel</SecondaryButton>
                            </div>
                        </div>
                    ) : (
                        <p className={`text-base font-serif leading-relaxed ${item.status === "unknown" ? "text-[var(--muted)] italic" : "text-[var(--ink)]"}`}>
                            {item.value}
                        </p>
                    )}

                    {/* Meta & Actions */}
                    <div className="flex items-center gap-4 mt-2">
                        {item.proofLinked && (
                            <span className="flex items-center gap-1 font-technical text-[10px] text-[var(--secondary)]">
                                <ExternalLink size={8} /> SOURCE LINKED
                            </span>
                        )}

                        {!isLocked && !isEditing && (
                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="text-[10px] uppercase font-technical text-[var(--blueprint)] hover:underline"
                                >
                                    Refine
                                </button>
                                {item.status !== "confirmed" && (
                                    <>
                                        <span className="text-[var(--border)]">ΓÇó</span>
                                        <button
                                            onClick={() => onConfirm(item.id)}
                                            className="text-[10px] uppercase font-technical text-[var(--success)] hover:underline"
                                        >
                                            Confirm
                                        </button>
                                    </>
                                )}
                                <span className="text-[var(--border)]">ΓÇó</span>
                                <button
                                    onClick={() => setShowNotes(!showNotes)}
                                    className="text-[10px] uppercase font-technical text-[var(--muted)] hover:text-[var(--ink)]"
                                >
                                    Flag
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Notes Section */}
            {(showNotes || item.stakeholderNotes) && (
                <div className="ml-14 mr-4 mt-3 p-3 bg-[var(--paper)] border border-[var(--border-subtle)] rounded-[1px]">
                    {showNotes && !isLocked ? (
                        <div className="space-y-2">
                            <textarea
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                                placeholder="Add annotation or mark as unknown..."
                                className="w-full text-xs bg-transparent focus:outline-none text-[var(--ink)] placeholder:text-[var(--muted)]"
                                rows={2}
                            />
                            <div className="flex justify-end gap-2">
                                <button onClick={() => onMarkUnknown(item.id, notes)} className="text-[10px] font-technical uppercase text-[var(--secondary)] hover:text-[var(--ink)]">Mark Unknown</button>
                                <button onClick={() => setShowNotes(false)} className="text-[10px] font-technical uppercase text-[var(--blueprint)]">Done</button>
                            </div>
                        </div>
                    ) : (
                        <p className="text-xs text-[var(--secondary)] italic">
                            <span className="font-technical text-[var(--ink)] not-italic mr-2">NOTE:</span>
                            {item.stakeholderNotes}
                        </p>
                    )}
                </div>
            )}
        </div>
    );
}

function CategorySection({
    category,
    items,
    onConfirm,
    onEdit,
    onMarkUnknown,
    isLocked
}: {
    category: string;
    items: TruthItem[];
    onConfirm: (id: string) => void;
    onEdit: (id: string, value: string, notes?: string) => void;
    onMarkUnknown: (id: string, notes: string) => void;
    isLocked: boolean;
}) {
    const [isExpanded, setIsExpanded] = useState(true);
    const confirmedCount = items.filter(i => i.status === "confirmed" || i.status === "edited").length;
    const isComplete = confirmedCount === items.length;

    return (
        <div className="border border-[var(--border-subtle)] bg-[var(--paper)] mb-6 last:mb-0">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between p-4 bg-[var(--canvas)] hover:bg-[var(--paper)] transition-colors border-b border-[var(--border-subtle)]"
            >
                <div className="flex items-center gap-4">
                    <div className={`w-2 h-2 rounded-full ${isComplete ? 'bg-[var(--ink)]' : 'bg-[var(--warning)]'}`} />
                    <h3 className="font-serif text-lg text-[var(--ink)] tracking-tight">{category}</h3>
                </div>
                <div className="flex items-center gap-4">
                    <span className="font-technical text-[10px] text-[var(--muted)] tracking-widest">
                        {confirmedCount}/{items.length} VERIFIED
                    </span>
                    {isExpanded ? <ChevronUp size={14} className="text-[var(--muted)]" /> : <ChevronDown size={14} className="text-[var(--muted)]" />}
                </div>
            </button>

            {isExpanded && (
                <div>
                    {items.map((item) => (
                        <TruthItemRow
                            key={item.id}
                            item={item}
                            onConfirm={onConfirm}
                            onEdit={onEdit}
                            onMarkUnknown={onMarkUnknown}
                            isLocked={isLocked}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

export default function Step4ValidateTruthSheet() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const step2Data = getStepById(2)?.data as { facts?: any[] } | undefined;
    const stepData = getStepById(4)?.data as {
        truthSheet?: TruthItem[];
        locked?: boolean;
        versions?: TruthSheetVersion[];
    } | undefined;

    const [items, setItems] = useState<TruthItem[]>(stepData?.truthSheet || []);
    const [isLocked, setIsLocked] = useState(stepData?.locked || false);
    const [versions, setVersions] = useState<TruthSheetVersion[]>(stepData?.versions || []);
    const [showLockConfirm, setShowLockConfirm] = useState(false);
    const [showVersionHistory, setShowVersionHistory] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Fetch AI-generated truth sheet
    const generateTruthSheet = useCallback(async () => {
        setIsGenerating(true);
        try {
            const step1Data = getStepById(1)?.data as { evidence?: any[] } | undefined;
            const evidenceList = step1Data?.evidence || [];

            const response = await fetch('/api/onboarding/truth-sheet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: session?.sessionId || 'demo',
                    evidence_list: evidenceList,
                    existing_entries: items.filter(i => i.status === 'edited' || i.status === 'confirmed')
                })
            });

            const data = await response.json();
            if (data.success && data.truth_sheet?.entries) {
                const newItems: TruthItem[] = data.truth_sheet.entries.map((entry: any, i: number) => ({
                    id: entry.id || `truth-${i}`,
                    category: entry.category || "General",
                    label: entry.field_name,
                    value: entry.value,
                    status: entry.verified ? "confirmed" : entry.confidence === "high" ? "needs-review" : "needs-review",
                    proofLinked: !!entry.source,
                    source: entry.source,
                    code: `T-${String(i + 1).padStart(3, "0")}`,
                }));
                setItems(newItems);
                updateStepData(4, { truthSheet: newItems, locked: false });
            }
        } catch (err) {
            console.error('Failed to generate truth sheet:', err);
        } finally {
            setIsGenerating(false);
        }
    }, [session?.sessionId, getStepById, items, updateStepData]);

    // Initialize from Step 2 facts if no items
    useEffect(() => {
        if (items.length === 0 && step2Data?.facts) {
            const truthItems: TruthItem[] = step2Data.facts.map((fact: any, i: number) => ({
                id: fact.id || `truth-${i}`,
                category: fact.category || "General",
                label: fact.label,
                value: fact.value,
                status: fact.status === "verified" ? "confirmed" : "needs-review",
                proofLinked: fact.sources?.length > 0,
                source: fact.sources?.[0]?.name,
                code: `T-${String(i + 1).padStart(3, "0")}`,
            }));
            setItems(truthItems);
            updateStepData(4, { truthSheet: truthItems, locked: false, versions: [] });
        }
    }, [step2Data, items.length, updateStepData]);

    // Animation
    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power2.out" }
        );
    }, []);

    // Handlers
    const handleConfirm = (id: string) => {
        const updated = items.map(i => i.id === id ? { ...i, status: "confirmed" as const } : i);
        setItems(updated);
        updateStepData(4, { truthSheet: updated });
    };

    const handleEdit = (id: string, value: string, notes?: string) => {
        const updated = items.map(i =>
            i.id === id ? { ...i, value, status: "edited" as const, stakeholderNotes: notes } : i
        );
        setItems(updated);
        updateStepData(4, { truthSheet: updated });
    };

    const handleMarkUnknown = (id: string, notes: string) => {
        const updated = items.map(i =>
            i.id === id ? { ...i, status: "unknown" as const, stakeholderNotes: notes } : i
        );
        setItems(updated);
        updateStepData(4, { truthSheet: updated });
    };

    const handleLock = async () => {
        const newVersion: TruthSheetVersion = {
            version: `v${versions.length + 1}.0`,
            createdAt: new Date(),
            itemCount: items.length,
        };
        setIsLocked(true);
        setVersions([...versions, newVersion]);
        setShowLockConfirm(false);
        updateStepData(4, { truthSheet: items, locked: true, versions: [...versions, newVersion] });
        updateStepStatus(4, "complete");

        // Sync to backend logic (mocked here for brevity, assume same fetch as before)
    };

    const handleUnlock = () => {
        setIsLocked(false);
        updateStepData(4, { truthSheet: items, locked: false, versions });
        updateStepStatus(4, "in-progress");
    };

    // Grouping
    const grouped = items.reduce((acc, item) => {
        if (!acc[item.category]) acc[item.category] = [];
        acc[item.category].push(item);
        return acc;
    }, {} as Record<string, TruthItem[]>);

    const allConfirmed = items.every(i => i.status === "confirmed" || i.status === "edited");
    const needsReviewCount = items.filter(i => i.status === "needs-review").length;

    // Empty State
    if (items.length === 0) {
        return (
            <StepEmptyState
                title="Initialize Truth Sheet"
                description="Complete the Auto-Extraction step to populate your initial Truth Sheet."
                icon={FileText}
            />
        );
    }

    return (
        <div ref={containerRef} className="max-w-4xl mx-auto space-y-8">

            {/* Header */}
            <div data-animate className="flex items-center justify-between">
                <div>
                    <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Business Truth Sheet</h2>
                    <p className="text-[var(--secondary)] max-w-lg leading-relaxed">
                        This document serves as the single source of truth for your positioning.
                        Verify each fact before locking.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {isLocked ? (
                        <div className="flex items-center gap-3 px-4 py-2 bg-[var(--canvas)] border border-[var(--border)] rounded-[1px]">
                            <Lock size={14} className="text-[var(--ink)]" />
                            <span className="font-technical text-xs tracking-widest text-[var(--ink)]">LOCKED v{versions[versions.length - 1]?.version}</span>
                            <button onClick={handleUnlock} className="ml-2 text-[var(--muted)] hover:text-[var(--ink)]">
                                <Unlock size={12} />
                            </button>
                        </div>
                    ) : (
                        <BlueprintButton
                            onClick={() => setShowLockConfirm(true)}
                            disabled={needsReviewCount > 0}
                            className="px-6"
                        >
                            <ShieldCheck size={14} />
                            <span>Lock Truth Sheet</span>
                        </BlueprintButton>
                    )}
                </div>
            </div>

            {/* Document Surface */}
            <div data-animate className="bg-[var(--paper)] border border-[var(--border)] shadow-sm min-h-[600px] p-12 relative mx-auto max-w-[900px]">
                {/* Paper Header */}
                <div className="border-b-2 border-[var(--ink)] pb-6 mb-12 flex justify-between items-end">
                    <div>
                        <h1 className="font-serif text-4xl text-[var(--ink)] leading-none mb-2">Fundamental Truths</h1>
                        <p className="font-technical text-xs tracking-[0.2em] text-[var(--muted)] uppercase">Confidential ΓÇó Internal Use Only</p>
                    </div>
                    <div className="text-right">
                        <span className="block font-technical text-xs text-[var(--muted)]">DATE: {new Date().toLocaleDateString()}</span>
                        <span className="block font-technical text-xs text-[var(--muted)]">REF: BTS-{session?.sessionId?.slice(0, 6) || "0000"}</span>
                    </div>
                </div>

                {/* Content */}
                <div className="space-y-8">
                    {Object.entries(grouped).map(([category, categoryItems], i) => (
                        <div key={category}>
                            <h3 className="font-technical text-xs font-bold text-[var(--ink)] uppercase tracking-widest border-b border-[var(--border-subtle)] pb-2 mb-4">
                                Section {String(i + 1).padStart(2, "0")} ΓÇó {category}
                            </h3>
                            <div className="space-y-1">
                                {categoryItems.map((item) => (
                                    <TruthItemRow
                                        key={item.id}
                                        item={item}
                                        onConfirm={handleConfirm}
                                        onEdit={handleEdit}
                                        onMarkUnknown={handleMarkUnknown}
                                        isLocked={isLocked}
                                    />
                                ))}
                            </div>
                            <div className="h-8" /> {/* Spacer */}
                        </div>
                    ))}
                </div>

                {/* Signature Block (Visual Only) */}
                {isLocked && (
                    <div className="mt-24 pt-8 border-t border-[var(--border-subtle)] w-64">
                        <p className="font-serif italic text-xl text-[var(--ink)] mb-2">Verified</p>
                        <p className="font-technical text-[10px] text-[var(--muted)] uppercase tracking-widest">Digital Signature</p>
                    </div>
                )}
            </div>

            {/* Lock Confirmation Modal */}
            <BlueprintModal
                isOpen={showLockConfirm}
                onClose={() => setShowLockConfirm(false)}
                title="Ratify Truth Sheet"
            >
                <div className="space-y-6 p-2">
                    <div className="p-4 bg-[var(--canvas)] border border-[var(--border-subtle)] flex gap-4">
                        <Lock size={24} className="text-[var(--ink)]" />
                        <div className="space-y-2">
                            <h4 className="font-serif text-lg text-[var(--ink)]">Ready to Lock?</h4>
                            <p className="text-sm text-[var(--secondary)]">
                                You are about to create <span className="font-medium text-[var(--ink)]">Version {versions.length + 1}.0</span> of your Business Truth Sheet.
                                This snapshot will be used to generate all downstream positioning assets.
                            </p>
                        </div>
                    </div>
                    <div className="flex justify-end gap-3 pt-4">
                        <SecondaryButton onClick={() => setShowLockConfirm(false)}>Review More</SecondaryButton>
                        <BlueprintButton onClick={handleLock}>
                            <span>Confirm & Lock</span>
                        </BlueprintButton>
                    </div>
                </div>
            </BlueprintModal>

        </div>
    );
}
