"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Check, Lock, AlertTriangle, ChevronDown, ChevronUp, Edit2, ExternalLink,
    Shield, FileText, HelpCircle, Unlock, History, Download
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { supabase } from "@/lib/supabaseClient";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { StepEmptyState } from "../StepStates";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 4: Validate Truth Sheet

   PURPOSE: Review and lock validated facts as the "Business Truth Sheet v1"
   - Present validated facts from Step 2/3 in an editable format
   - Allow confirm/edit/unknown marking per item
   - Create immutable version when locked
   - Handle stakeholder disagreements
   ══════════════════════════════════════════════════════════════════════════════ */

// Types
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

    const handleMarkUnknown = () => {
        onMarkUnknown(item.id, notes);
        setShowNotes(false);
    };

    const statusConfig = {
        confirmed: { label: "CONFIRMED", variant: "success" as const, color: "text-[var(--success)]" },
        "needs-review": { label: "REVIEW", variant: "warning" as const, color: "text-[var(--warning)]" },
        edited: { label: "EDITED", variant: "blueprint" as const, color: "text-[var(--blueprint)]" },
        unknown: { label: "UNKNOWN", variant: "error" as const, color: "text-[var(--error)]" },
    };

    return (
        <div className={`flex flex-col gap-2 py-3 border-b border-[var(--border-subtle)] last:border-0 ${isLocked ? "opacity-75" : ""}`}>
            <div className="flex items-center gap-4">
                <span className="font-technical text-[var(--blueprint)] w-16 flex-shrink-0">{item.code}</span>
                <div className="w-36 flex-shrink-0">
                    <span className="text-sm font-medium text-[var(--secondary)]">{item.label}</span>
                </div>
                <div className="flex-1">
                    {isEditing && !isLocked ? (
                        <div className="flex flex-col gap-2">
                            <input
                                type="text"
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                className="w-full h-8 px-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                autoFocus
                            />
                            <div className="flex gap-2">
                                <BlueprintButton size="sm" onClick={handleSave}>Save</BlueprintButton>
                                <SecondaryButton size="sm" onClick={() => setIsEditing(false)}>Cancel</SecondaryButton>
                            </div>
                        </div>
                    ) : (
                        <span className={`text-sm ${item.status === "unknown" ? "text-[var(--muted)] italic" : "text-[var(--ink)]"}`}>
                            {item.value}
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    <BlueprintBadge variant={statusConfig[item.status].variant} dot>
                        {statusConfig[item.status].label}
                    </BlueprintBadge>
                    {item.proofLinked && (
                        <span className="flex items-center gap-1 font-technical text-[var(--success)]">
                            <ExternalLink size={8} />PROOF
                        </span>
                    )}
                    {!isLocked && !isEditing && (
                        <>
                            <button
                                onClick={() => setIsEditing(true)}
                                className="p-1.5 text-[var(--muted)] hover:text-[var(--blueprint)] rounded-[var(--radius-xs)] transition-colors"
                                title="Edit"
                            >
                                <Edit2 size={12} strokeWidth={1.5} />
                            </button>
                            {item.status !== "confirmed" && (
                                <button
                                    onClick={() => onConfirm(item.id)}
                                    className="p-1.5 text-[var(--success)] hover:bg-[var(--success-light)] rounded-[var(--radius-xs)] transition-colors"
                                    title="Confirm"
                                >
                                    <Check size={12} strokeWidth={1.5} />
                                </button>
                            )}
                            <button
                                onClick={() => setShowNotes(!showNotes)}
                                className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] rounded-[var(--radius-xs)] transition-colors"
                                title="Mark as unknown or add notes"
                            >
                                <HelpCircle size={12} strokeWidth={1.5} />
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* Stakeholder Notes / Unknown Input */}
            {showNotes && !isLocked && (
                <div className="ml-20 p-3 bg-[var(--canvas)] rounded-[var(--radius-sm)] border border-[var(--border-subtle)]">
                    <span className="font-technical text-[var(--muted)] block mb-2">STAKEHOLDER NOTES / RESOLUTION</span>
                    <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Add notes about disagreements or mark why this is unknown..."
                        className="w-full min-h-[60px] p-2 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                    />
                    <div className="flex gap-2 mt-2">
                        <SecondaryButton size="sm" onClick={handleMarkUnknown}>
                            <HelpCircle size={10} strokeWidth={1.5} />
                            Mark Unknown
                        </SecondaryButton>
                        <SecondaryButton size="sm" onClick={() => setShowNotes(false)}>Cancel</SecondaryButton>
                    </div>
                </div>
            )}

            {item.stakeholderNotes && (
                <div className="ml-20 p-2 bg-[var(--warning-light)] rounded-[var(--radius-xs)] border border-[var(--warning)]/20">
                    <span className="font-technical text-[var(--warning)] text-[10px]">NOTE: </span>
                    <span className="text-xs text-[var(--secondary)]">{item.stakeholderNotes}</span>
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

    return (
        <BlueprintCard code={category.slice(0, 3).toUpperCase()} showCorners padding="none">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between p-4 hover:bg-[var(--canvas)] transition-colors"
            >
                <div className="flex items-center gap-3">
                    <h3 className="text-sm font-semibold text-[var(--ink)]">{category}</h3>
                    <span className="font-technical text-[var(--muted)]">{confirmedCount}/{items.length} CONFIRMED</span>
                </div>
                {isExpanded ? <ChevronUp size={14} strokeWidth={1.5} /> : <ChevronDown size={14} strokeWidth={1.5} />}
            </button>
            {isExpanded && (
                <div className="px-4 pb-4">
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
        </BlueprintCard>
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
    const containerRef = useRef<HTMLDivElement>(null);

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
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
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

        // Sync to backend
        if (session?.sessionId) {
            try {
                const { data: authData } = await supabase.auth.getSession();
                const token = authData.session?.access_token;

                await fetch(
                    `http://localhost:8000/api/v1/onboarding/${session.sessionId}/truth-sheet/lock`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            ...(token ? { Authorization: `Bearer ${token}` } : {}),
                        },
                        body: JSON.stringify({ items, version: newVersion.version }),
                    }
                );
            } catch (error) {
                console.error("Failed to sync lock to backend:", error);
            }
        }
    };

    const handleUnlock = () => {
        setIsLocked(false);
        updateStepData(4, { truthSheet: items, locked: false, versions });
        updateStepStatus(4, "in-progress");
    };

    // Group items by category
    const grouped = items.reduce((acc, item) => {
        if (!acc[item.category]) acc[item.category] = [];
        acc[item.category].push(item);
        return acc;
    }, {} as Record<string, TruthItem[]>);

    const allConfirmed = items.every(i => i.status === "confirmed" || i.status === "edited");
    const needsReviewCount = items.filter(i => i.status === "needs-review").length;
    const unknownCount = items.filter(i => i.status === "unknown").length;
    const confirmedCount = items.filter(i => i.status === "confirmed" || i.status === "edited").length;

    // No data state
    if (items.length === 0) {
        return (
            <StepEmptyState
                title="No Facts to Validate"
                description="Please complete Step 2 (Auto-Extraction) to generate facts for validation."
                icon={FileText}
            />
        );
    }

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Status Card */}
            {isLocked ? (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--success)] flex items-center justify-center ink-bleed-xs">
                            <Lock size={18} strokeWidth={1.5} className="text-[var(--paper)]" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-sm font-semibold text-[var(--ink)]">Truth Sheet Locked</h3>
                            <p className="font-technical text-[var(--muted)]">
                                VERSION {versions[versions.length - 1]?.version || "1.0"} CREATED
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <SecondaryButton size="sm" onClick={() => setShowVersionHistory(true)}>
                                <History size={10} strokeWidth={1.5} />
                                History
                            </SecondaryButton>
                            <SecondaryButton size="sm" onClick={handleUnlock}>
                                <Unlock size={10} strokeWidth={1.5} />
                                Unlock
                            </SecondaryButton>
                        </div>
                        <BlueprintBadge variant="success" dot>LOCKED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            ) : (
                <BlueprintCard
                    data-animate
                    showCorners
                    padding="md"
                    className={allConfirmed ? "border-[var(--success)]/30 bg-[var(--success-light)]" : "border-[var(--warning)]/30 bg-[var(--warning-light)]"}
                >
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-[var(--radius-sm)] flex items-center justify-center ${allConfirmed ? "bg-[var(--success)]" : "bg-[var(--warning)]"
                                }`}>
                                {allConfirmed
                                    ? <Check size={18} strokeWidth={1.5} className="text-[var(--paper)]" />
                                    : <AlertTriangle size={18} strokeWidth={1.5} className="text-[var(--paper)]" />
                                }
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-[var(--ink)]">
                                    {allConfirmed ? "Ready to lock" : `${needsReviewCount} items need review`}
                                </h3>
                                <p className="font-technical text-[var(--muted)]">
                                    {confirmedCount}/{items.length} CONFIRMED
                                    {unknownCount > 0 && ` • ${unknownCount} UNKNOWN`}
                                </p>
                            </div>
                        </div>
                        <BlueprintButton
                            size="sm"
                            onClick={() => setShowLockConfirm(true)}
                            disabled={needsReviewCount > 0}
                        >
                            <Lock size={12} strokeWidth={1.5} />
                            Lock Truth Sheet
                        </BlueprintButton>
                    </div>
                </BlueprintCard>
            )}

            {/* Categories */}
            <div data-animate className="space-y-4">
                {Object.entries(grouped).map(([category, categoryItems], i) => (
                    <div key={category}>
                        <div className="flex items-center gap-3 mb-3">
                            <span className="font-technical text-[var(--blueprint)]">FIG. {String(i + 1).padStart(2, "0")}</span>
                            <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                        </div>
                        <CategorySection
                            category={category}
                            items={categoryItems}
                            onConfirm={handleConfirm}
                            onEdit={handleEdit}
                            onMarkUnknown={handleMarkUnknown}
                            isLocked={isLocked}
                        />
                    </div>
                ))}
            </div>

            {/* Stats Summary */}
            <BlueprintCard data-animate code="STATS" showCorners padding="md">
                <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                        <span className="block font-serif text-2xl text-[var(--ink)]">{items.length}</span>
                        <span className="font-technical text-[var(--muted)]">TOTAL</span>
                    </div>
                    <div>
                        <span className="block font-serif text-2xl text-[var(--success)]">{confirmedCount}</span>
                        <span className="font-technical text-[var(--muted)]">CONFIRMED</span>
                    </div>
                    <div>
                        <span className="block font-serif text-2xl text-[var(--warning)]">{needsReviewCount}</span>
                        <span className="font-technical text-[var(--muted)]">PENDING</span>
                    </div>
                    <div>
                        <span className="block font-serif text-2xl text-[var(--error)]">{unknownCount}</span>
                        <span className="font-technical text-[var(--muted)]">UNKNOWN</span>
                    </div>
                </div>
            </BlueprintCard>

            {/* Lock Confirmation Modal */}
            <BlueprintModal
                isOpen={showLockConfirm}
                onClose={() => setShowLockConfirm(false)}
                title="Lock Truth Sheet?"
            >
                <div className="space-y-4">
                    <p className="text-sm text-[var(--secondary)]">
                        Locking creates an immutable Version {versions.length + 1}.0 of your Truth Sheet.
                        This becomes the foundation for all positioning and messaging work.
                    </p>
                    {unknownCount > 0 && (
                        <BlueprintCard padding="sm" className="border-[var(--warning)]/30 bg-[var(--warning-light)]">
                            <div className="flex items-center gap-2">
                                <AlertTriangle size={14} className="text-[var(--warning)]" />
                                <span className="text-sm text-[var(--secondary)]">
                                    {unknownCount} item{unknownCount > 1 ? "s are" : " is"} marked as unknown
                                </span>
                            </div>
                        </BlueprintCard>
                    )}
                    <div className="flex gap-3 justify-end">
                        <SecondaryButton onClick={() => setShowLockConfirm(false)}>Cancel</SecondaryButton>
                        <BlueprintButton onClick={handleLock}>
                            <Lock size={12} strokeWidth={1.5} />
                            Lock & Create v{versions.length + 1}.0
                        </BlueprintButton>
                    </div>
                </div>
            </BlueprintModal>

            {/* Version History Modal */}
            <BlueprintModal
                isOpen={showVersionHistory}
                onClose={() => setShowVersionHistory(false)}
                title="Version History"
            >
                <div className="space-y-3">
                    {versions.length === 0 ? (
                        <p className="text-sm text-[var(--muted)]">No versions created yet.</p>
                    ) : (
                        versions.map((v, i) => (
                            <div key={i} className="flex items-center justify-between p-3 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border-subtle)]">
                                <div>
                                    <span className="font-technical text-[var(--blueprint)]">{v.version}</span>
                                    <p className="text-xs text-[var(--muted)]">
                                        {new Date(v.createdAt).toLocaleDateString()} • {v.itemCount} items
                                    </p>
                                </div>
                                <SecondaryButton size="sm">
                                    <Download size={10} strokeWidth={1.5} />
                                    Export
                                </SecondaryButton>
                            </div>
                        ))
                    )}
                </div>
            </BlueprintModal>

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">
                    DOCUMENT: TRUTH-SHEET | STEP 04/25 | {isLocked ? "LOCKED" : "DRAFT"}
                </span>
            </div>
        </div>
    );
}
