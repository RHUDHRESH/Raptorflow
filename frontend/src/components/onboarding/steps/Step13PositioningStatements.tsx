"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Edit2, RefreshCw, Target } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 13: Positioning Statements
   Craft core positioning messages
   ══════════════════════════════════════════════════════════════════════════════ */

interface PositioningStatement { id: string; type: "elevator" | "tagline" | "value-prop"; label: string; template: string; content: string; code: string; }

const INITIAL_STATEMENTS: PositioningStatement[] = [
    { id: "1", type: "elevator", label: "Elevator Pitch", template: "For [target], [product] is the [category] that [key benefit] unlike [alternatives] because [unique differentiator].", content: "For founders scaling their first marketing team, RaptorFlow is the marketing operating system that validates positioning in hours, not months, unlike agencies or DIY approaches because it extracts and validates your positioning from existing evidence.", code: "POS-01" },
    { id: "2", type: "tagline", label: "Tagline", template: "[Outcome], [how].", content: "Marketing. Finally under control.", code: "POS-02" },
    { id: "3", type: "value-prop", label: "Value Proposition", template: "We help [audience] achieve [outcome] by [mechanism].", content: "We help founders build validated positioning by extracting and validating claims from their existing content using AI.", code: "POS-03" },
];

export default function Step13PositioningStatements() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(13)?.data as { statements?: PositioningStatement[]; confirmed?: boolean } | undefined;
    const [statements, setStatements] = useState<PositioningStatement[]>(stepData?.statements || INITIAL_STATEMENTS);
    const [editing, setEditing] = useState<string | null>(null);
    const [editContent, setEditContent] = useState("");
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    }, []);

    const saveData = (stmts: PositioningStatement[]) => { setStatements(stmts); updateStepData(13, { statements: stmts }); };
    const startEdit = (id: string) => { const stmt = statements.find((s) => s.id === id); if (stmt) { setEditing(id); setEditContent(stmt.content); } };
    const saveEdit = () => { if (!editing) return; saveData(statements.map((s) => (s.id === editing ? { ...s, content: editContent } : s))); setEditing(null); };
    const handleConfirm = () => { setConfirmed(true); updateStepData(13, { statements, confirmed: true }); updateStepStatus(13, "complete"); };

    const typeConfig = {
        elevator: { icon: Target, variant: "blueprint" as const, label: "ELEVATOR" },
        tagline: { icon: RefreshCw, variant: "warning" as const, label: "TAGLINE" },
        "value-prop": { icon: Check, variant: "success" as const, label: "VALUE PROP" },
    };

    return (
        <div ref={containerRef} className="space-y-6">
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <p className="text-sm text-[var(--secondary)]">Craft your core positioning statements. These will guide all messaging.</p>
            </BlueprintCard>

            {statements.map((stmt, i) => {
                const config = typeConfig[stmt.type];
                const ConfigIcon = config.icon;
                return (
                    <BlueprintCard key={stmt.id} data-animate figure={`FIG. ${String(i + 1).padStart(2, "0")}`} title={stmt.label} code={stmt.code} showCorners padding="md">
                        <div className="flex items-center gap-2 mb-4"><BlueprintBadge variant={config.variant}>{config.label}</BlueprintBadge>{editing !== stmt.id && <button onClick={() => startEdit(stmt.id)} className="ml-auto p-1.5 text-[var(--muted)] hover:text-[var(--blueprint)] rounded-[var(--radius-xs)] transition-colors"><Edit2 size={12} strokeWidth={1.5} /></button>}</div>
                        <div className="mb-4 p-3 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-dashed border-[var(--border)]"><p className="font-technical text-[var(--muted)] italic">{stmt.template}</p></div>
                        {editing === stmt.id ? (
                            <div className="space-y-3">
                                <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)} className="w-full min-h-[120px] p-4 text-sm font-mono bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]" autoFocus />
                                <div className="flex gap-3"><BlueprintButton size="sm" onClick={saveEdit}>Save</BlueprintButton><SecondaryButton size="sm" onClick={() => setEditing(null)}>Cancel</SecondaryButton></div>
                            </div>
                        ) : (
                            <p className="text-sm text-[var(--ink)] leading-relaxed">"{stmt.content}"</p>
                        )}
                    </BlueprintCard>
                );
            })}

            {!confirmed && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM"><Check size={14} strokeWidth={1.5} />Confirm Positioning Statements</BlueprintButton>
            )}
            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3"><Check size={18} strokeWidth={1.5} className="text-[var(--success)]" /><span className="text-sm font-medium text-[var(--ink)]">Positioning statements confirmed</span><BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge></div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4"><span className="font-technical text-[var(--muted)]">DOCUMENT: POSITIONING | STEP 13/25</span></div>
        </div>
    );
}
