"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Shield, AlertTriangle, Zap, X, Plus, Trash2, Edit2, GripVertical } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 17: Messaging Guardrails

   Define do's and don'ts for messaging with full CRUD:
   - Add new guardrails
   - Edit existing guardrails inline
   - Delete guardrails
   ══════════════════════════════════════════════════════════════════════════════ */

interface Guardrail {
    id: string;
    type: "do" | "dont";
    text: string;
    reason?: string;
    code: string;
}

const INITIAL_GUARDRAILS: Guardrail[] = [
    { id: "1", type: "do", text: "Use evidence-based claims with source attribution", reason: "Builds credibility and trust", code: "DO-01" },
    { id: "2", type: "do", text: "Lead with founder pain points, not features", reason: "Founders care about problems, not specs", code: "DO-02" },
    { id: "3", type: "do", text: "Keep messaging calm and confident, not hype", reason: "Matches the RaptorFlow brand tone", code: "DO-03" },
    { id: "4", type: "dont", text: "Make unverifiable claims about results", reason: "Damages credibility when challenged", code: "DNT-01" },
    { id: "5", type: "dont", text: "Use enterprise jargon with startup founders", reason: "Alienates our core ICP", code: "DNT-02" },
    { id: "6", type: "dont", text: "Compare directly to competitors by name", reason: "Gives them free attention", code: "DNT-03" },
];

// Individual guardrail row with inline editing
function GuardrailRow({
    guardrail,
    onUpdate,
    onDelete
}: {
    guardrail: Guardrail;
    onUpdate: (g: Guardrail) => void;
    onDelete: () => void;
}) {
    const [isEditing, setIsEditing] = useState(false);
    const [editText, setEditText] = useState(guardrail.text);
    const [editReason, setEditReason] = useState(guardrail.reason || "");
    const inputRef = useRef<HTMLInputElement>(null);

    const isDo = guardrail.type === "do";

    useEffect(() => {
        if (isEditing && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isEditing]);

    const handleSave = () => {
        if (!editText.trim()) return;
        onUpdate({ ...guardrail, text: editText, reason: editReason });
        setIsEditing(false);
    };

    const handleCancel = () => {
        setEditText(guardrail.text);
        setEditReason(guardrail.reason || "");
        setIsEditing(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") handleSave();
        if (e.key === "Escape") handleCancel();
    };

    if (isEditing) {
        return (
            <div className={`p-4 rounded-lg border-2 ${isDo ? "border-[var(--success)]" : "border-[var(--error)]"} bg-[var(--paper)]`}>
                <div className="space-y-3">
                    <div>
                        <label className="font-technical text-[9px] text-[var(--muted)] block mb-1">GUARDRAIL</label>
                        <input
                            ref={inputRef}
                            type="text"
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            onKeyDown={handleKeyDown}
                            className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-lg text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                            placeholder="What's the rule?"
                        />
                    </div>
                    <div>
                        <label className="font-technical text-[9px] text-[var(--muted)] block mb-1">WHY? (OPTIONAL)</label>
                        <input
                            type="text"
                            value={editReason}
                            onChange={(e) => setEditReason(e.target.value)}
                            onKeyDown={handleKeyDown}
                            className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-lg text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                            placeholder="Why does this matter?"
                        />
                    </div>
                    <div className="flex gap-2">
                        <BlueprintButton size="sm" onClick={handleSave}>Save</BlueprintButton>
                        <SecondaryButton size="sm" onClick={handleCancel}>Cancel</SecondaryButton>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`
            group flex items-start gap-3 p-3 rounded-lg transition-all
            ${isDo ? "bg-[var(--success-light)] border border-[var(--success)]/20 hover:border-[var(--success)]/50" : "bg-[var(--error-light)] border border-[var(--error)]/20 hover:border-[var(--error)]/50"}
        `}>
            <div className={`
                w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
                ${isDo ? "bg-[var(--success)]" : "bg-[var(--error)]"}
            `}>
                {isDo ? <Check size={14} className="text-[var(--paper)]" /> : <X size={14} className="text-[var(--paper)]" />}
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <span className={`font-technical text-[9px] ${isDo ? "text-[var(--success)]" : "text-[var(--error)]"}`}>
                        {guardrail.code}
                    </span>
                </div>
                <p className="text-sm text-[var(--ink)]">{guardrail.text}</p>
                {guardrail.reason && (
                    <p className="text-xs text-[var(--secondary)] mt-1 italic">→ {guardrail.reason}</p>
                )}
            </div>
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                    onClick={() => setIsEditing(true)}
                    className="p-1.5 text-[var(--muted)] hover:text-[var(--blueprint)] hover:bg-[var(--canvas)] rounded-lg transition-all"
                    title="Edit"
                >
                    <Edit2 size={12} strokeWidth={1.5} />
                </button>
                <button
                    onClick={onDelete}
                    className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] hover:bg-[var(--error-light)] rounded-lg transition-all"
                    title="Delete"
                >
                    <Trash2 size={12} strokeWidth={1.5} />
                </button>
            </div>
        </div>
    );
}

export default function Step17MessagingGuardrails() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(17)?.data as { guardrails?: Guardrail[]; confirmed?: boolean } | undefined;

    const [guardrails, setGuardrails] = useState<Guardrail[]>(stepData?.guardrails || INITIAL_GUARDRAILS);
    const [isAdding, setIsAdding] = useState(false);
    const [newType, setNewType] = useState<"do" | "dont">("do");
    const [newText, setNewText] = useState("");
    const [newReason, setNewReason] = useState("");
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    const saveData = (items: Guardrail[]) => {
        setGuardrails(items);
        updateStepData(17, { guardrails: items });
    };

    const handleAdd = () => {
        if (!newText.trim()) return;
        const count = guardrails.filter(g => g.type === newType).length;
        const code = newType === "do" ? `DO-${String(count + 1).padStart(2, "0")}` : `DNT-${String(count + 1).padStart(2, "0")}`;
        const item: Guardrail = {
            id: `g-${Date.now()}`,
            type: newType,
            text: newText,
            reason: newReason || undefined,
            code
        };
        saveData([...guardrails, item]);
        setNewText("");
        setNewReason("");
        setIsAdding(false);
    };

    const handleUpdate = (updated: Guardrail) => {
        saveData(guardrails.map(g => g.id === updated.id ? updated : g));
    };

    const handleDelete = (id: string) => {
        saveData(guardrails.filter(g => g.id !== id));
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(17, { guardrails, confirmed: true });
        updateStepStatus(17, "complete");
    };

    const dos = guardrails.filter((g) => g.type === "do");
    const donts = guardrails.filter((g) => g.type === "dont");

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Header */}
            <div data-animate className="text-center py-4">
                <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">Messaging Guardrails</h2>
                <p className="text-sm text-[var(--secondary)] max-w-lg mx-auto">
                    Define what your messaging should <span className="text-[var(--success)] font-semibold">always do</span> and
                    what it should <span className="text-[var(--error)] font-semibold">never do</span>.
                    These rules keep your team aligned.
                </p>
            </div>

            {/* Summary Stats */}
            <div data-animate className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-[var(--success-light)] border border-[var(--success)]/30 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                        <Check size={20} className="text-[var(--paper)]" />
                    </div>
                    <div>
                        <span className="text-2xl font-serif text-[var(--success)]">{dos.length}</span>
                        <p className="font-technical text-[9px] text-[var(--success)]">ALWAYS DO</p>
                    </div>
                </div>
                <div className="p-4 rounded-xl bg-[var(--error-light)] border border-[var(--error)]/30 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[var(--error)] flex items-center justify-center">
                        <X size={20} className="text-[var(--paper)]" />
                    </div>
                    <div>
                        <span className="text-2xl font-serif text-[var(--error)]">{donts.length}</span>
                        <p className="font-technical text-[9px] text-[var(--error)]">NEVER DO</p>
                    </div>
                </div>
            </div>

            {/* Do's */}
            <BlueprintCard data-animate figure="FIG. 01" title="Always Do" code="DO" showCorners padding="md">
                <div className="space-y-2">
                    {dos.map((g) => (
                        <GuardrailRow
                            key={g.id}
                            guardrail={g}
                            onUpdate={handleUpdate}
                            onDelete={() => handleDelete(g.id)}
                        />
                    ))}
                    {dos.length === 0 && (
                        <p className="text-sm text-[var(--muted)] text-center py-4">No "always do" rules yet</p>
                    )}
                </div>
            </BlueprintCard>

            {/* Don'ts */}
            <BlueprintCard data-animate figure="FIG. 02" title="Never Do" code="DNT" showCorners padding="md">
                <div className="space-y-2">
                    {donts.map((g) => (
                        <GuardrailRow
                            key={g.id}
                            guardrail={g}
                            onUpdate={handleUpdate}
                            onDelete={() => handleDelete(g.id)}
                        />
                    ))}
                    {donts.length === 0 && (
                        <p className="text-sm text-[var(--muted)] text-center py-4">No "never do" rules yet</p>
                    )}
                </div>
            </BlueprintCard>

            {/* Add New */}
            {isAdding ? (
                <BlueprintCard data-animate code="ADD" showCorners padding="md" className="border-[var(--blueprint)]">
                    <h4 className="text-sm font-semibold text-[var(--ink)] mb-4">Add New Guardrail</h4>
                    <div className="flex gap-2 mb-4">
                        <button
                            onClick={() => setNewType("do")}
                            className={`flex-1 px-4 py-3 font-technical text-[10px] rounded-lg transition-all flex items-center justify-center gap-2 ${newType === "do"
                                ? "bg-[var(--success)] text-[var(--paper)]"
                                : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)]"
                                }`}
                        >
                            <Check size={14} />ALWAYS DO
                        </button>
                        <button
                            onClick={() => setNewType("dont")}
                            className={`flex-1 px-4 py-3 font-technical text-[10px] rounded-lg transition-all flex items-center justify-center gap-2 ${newType === "dont"
                                ? "bg-[var(--error)] text-[var(--paper)]"
                                : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)]"
                                }`}
                        >
                            <X size={14} />NEVER DO
                        </button>
                    </div>
                    <div className="space-y-3 mb-4">
                        <div>
                            <label className="font-technical text-[9px] text-[var(--muted)] block mb-1">GUARDRAIL</label>
                            <input
                                type="text"
                                value={newText}
                                onChange={(e) => setNewText(e.target.value)}
                                placeholder="What's the rule?"
                                className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-lg text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                            />
                        </div>
                        <div>
                            <label className="font-technical text-[9px] text-[var(--muted)] block mb-1">WHY? (OPTIONAL)</label>
                            <input
                                type="text"
                                value={newReason}
                                onChange={(e) => setNewReason(e.target.value)}
                                placeholder="Why does this matter?"
                                className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-lg text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                            />
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <BlueprintButton size="sm" onClick={handleAdd}>Add Guardrail</BlueprintButton>
                        <SecondaryButton size="sm" onClick={() => { setIsAdding(false); setNewText(""); setNewReason(""); }}>Cancel</SecondaryButton>
                    </div>
                </BlueprintCard>
            ) : (
                <SecondaryButton data-animate onClick={() => setIsAdding(true)} className="w-full">
                    <Plus size={12} strokeWidth={1.5} />Add Guardrail
                </SecondaryButton>
            )}

            {/* Confirm */}
            {!confirmed && guardrails.length >= 4 && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-LOCK">
                    <Shield size={14} strokeWidth={1.5} />Lock Messaging Guardrails
                </BlueprintButton>
            )}

            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[var(--success)] flex items-center justify-center">
                            <Shield size={20} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="text-base font-serif text-[var(--ink)]">Guardrails Locked</span>
                            <p className="font-technical text-[10px] text-[var(--secondary)]">{dos.length} do's • {donts.length} don'ts</p>
                        </div>
                        <BlueprintBadge variant="success" dot className="ml-auto">LOCKED</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">MESSAGING-RULES • STEP 16/24</span>
            </div>
        </div>
    );
}
