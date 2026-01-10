"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Plus, Trash2, Sparkles } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 11: Differentiated Capabilities
   Map product capabilities and uniqueness
   ══════════════════════════════════════════════════════════════════════════════ */

interface Capability { id: string; name: string; description: string; uniqueness: "unique" | "better" | "parity"; code: string; }

const INITIAL_CAPABILITIES: Capability[] = [
    { id: "1", name: "AI-Powered Extraction", description: "Automatically extract positioning from your existing content", uniqueness: "unique", code: "CAP-01" },
    { id: "2", name: "Evidence-Based Validation", description: "Every claim backed by source attribution", uniqueness: "unique", code: "CAP-02" },
    { id: "3", name: "90-Day Execution System", description: "Campaign planning with weekly moves", uniqueness: "better", code: "CAP-03" },
];

export default function Step11DifferentiatedCapabilities() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(11)?.data as { capabilities?: Capability[]; confirmed?: boolean } | undefined;
    const [capabilities, setCapabilities] = useState<Capability[]>(stepData?.capabilities || INITIAL_CAPABILITIES);
    const [isAdding, setIsAdding] = useState(false);
    const [newCap, setNewCap] = useState<{ name: string; description: string; uniqueness: Capability["uniqueness"] }>({ name: "", description: "", uniqueness: "better" });
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    }, []);

    const saveData = (caps: Capability[]) => { setCapabilities(caps); updateStepData(11, { capabilities: caps }); };
    const addCapability = () => { if (!newCap.name.trim()) return; const cap: Capability = { id: `cap-${Date.now()}`, code: `CAP-${String(capabilities.length + 1).padStart(2, "0")}`, ...newCap }; saveData([...capabilities, cap]); setNewCap({ name: "", description: "", uniqueness: "better" }); setIsAdding(false); };
    const removeCapability = (id: string) => saveData(capabilities.filter((c) => c.id !== id));
    const updateUniqueness = (id: string, uniqueness: Capability["uniqueness"]) => saveData(capabilities.map((c) => (c.id === id ? { ...c, uniqueness } : c)));
    const handleConfirm = () => { setConfirmed(true); updateStepData(11, { capabilities, confirmed: true }); updateStepStatus(11, "complete"); };

    const uniquenessConfig = {
        unique: { label: "ONLY YOU", variant: "blueprint" as const },
        better: { label: "BETTER THAN", variant: "success" as const },
        parity: { label: "TABLE STAKES", variant: "default" as const },
    };

    return (
        <div ref={containerRef} className="space-y-6">
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <p className="text-sm text-[var(--secondary)]">List your product capabilities and rate each: Only You (unique), Better Than (superior), or Table Stakes (expected).</p>
            </BlueprintCard>

            <div data-animate className="space-y-3">
                {capabilities.map((cap) => (
                    <BlueprintCard key={cap.id} code={cap.code} showCorners padding="md">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--blueprint-light)] flex items-center justify-center flex-shrink-0">
                                <Sparkles size={18} strokeWidth={1.5} className="text-[var(--blueprint)]" />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-sm font-semibold text-[var(--ink)] mb-1">{cap.name}</h3>
                                <p className="text-xs text-[var(--secondary)] mb-3">{cap.description}</p>
                                <div className="flex gap-2">
                                    {(["unique", "better", "parity"] as const).map((u) => (
                                        <button key={u} onClick={() => updateUniqueness(cap.id, u)} className={`px-3 py-1.5 font-technical rounded-[var(--radius-sm)] transition-all ${cap.uniqueness === u ? `bg-[var(--${u === "unique" ? "blueprint" : u === "better" ? "success" : "muted"})] text-[var(--paper)]` : "bg-[var(--canvas)] text-[var(--muted)]"}`}>{uniquenessConfig[u].label}</button>
                                    ))}
                                </div>
                            </div>
                            <button onClick={() => removeCapability(cap.id)} className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] hover:bg-[var(--error-light)] rounded-[var(--radius-xs)] transition-all"><Trash2 size={12} strokeWidth={1.5} /></button>
                        </div>
                    </BlueprintCard>
                ))}
            </div>

            {isAdding ? (
                <BlueprintCard data-animate code="NEW" showCorners padding="md">
                    <div className="space-y-4">
                        <input type="text" value={newCap.name} onChange={(e) => setNewCap({ ...newCap, name: e.target.value })} placeholder="Capability name" className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]" autoFocus />
                        <textarea value={newCap.description} onChange={(e) => setNewCap({ ...newCap, description: e.target.value })} placeholder="Brief description" className="w-full min-h-[60px] p-3 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]" />
                        <div className="flex gap-2"><BlueprintButton size="sm" onClick={addCapability}>Add</BlueprintButton><SecondaryButton size="sm" onClick={() => setIsAdding(false)}>Cancel</SecondaryButton></div>
                    </div>
                </BlueprintCard>
            ) : (
                <SecondaryButton data-animate onClick={() => setIsAdding(true)} className="w-full"><Plus size={12} strokeWidth={1.5} />Add Capability</SecondaryButton>
            )}

            <BlueprintCard data-animate figure="FIG. 01" title="Summary" code="SUM" showCorners padding="md">
                <KPIGrid columns={3}>
                    <BlueprintKPI label="Only You" value={String(capabilities.filter((c) => c.uniqueness === "unique").length)} code="U" />
                    <BlueprintKPI label="Better Than" value={String(capabilities.filter((c) => c.uniqueness === "better").length)} code="B" trend="up" />
                    <BlueprintKPI label="Table Stakes" value={String(capabilities.filter((c) => c.uniqueness === "parity").length)} code="P" />
                </KPIGrid>
            </BlueprintCard>

            {!confirmed && capabilities.length >= 3 && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM"><Check size={14} strokeWidth={1.5} />Confirm Capabilities</BlueprintButton>
            )}
            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3"><Check size={18} strokeWidth={1.5} className="text-[var(--success)]" /><span className="text-sm font-medium text-[var(--ink)]">{capabilities.length} capabilities mapped</span><BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge></div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4"><span className="font-technical text-[var(--muted)]">DOCUMENT: CAPABILITIES | STEP 11/25</span></div>
        </div>
    );
}
