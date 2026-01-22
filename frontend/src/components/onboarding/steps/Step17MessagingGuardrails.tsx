"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import { Check, X, Shield, Plus, AlertTriangle, MessageSquare, Trash2, CheckCircle, RotateCcw, Loader2, Sparkles } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { cn } from "@/lib/utils";
import { toast } from "sonner"; // Assuming sonner or generic toast

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 17: Messaging Guardrails (Step 16 in file naming)

   PURPOSE: "No Scroll" Guardrails Editor.
   - 3 Do's, 3 Don'ts (Pre-filled based on Strategy).
   - Validation Mock: "Not Recommended" pop-up.
   - Input fields for custom rules.
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface Guardrail {
    id: string;
    text: string;
    type: "do" | "dont";
    isCustom?: boolean;
}

const DEFAULT_DOS: Guardrail[] = [
    { id: "do-1", text: "Speak like a peer, not a vendor", type: "do" },
    { id: "do-2", text: "Focus on the 'After' state", type: "do" },
    { id: "do-3", text: "Use data to back every claim", type: "do" },
];

const DEFAULT_DONTS: Guardrail[] = [
    { id: "dont-1", text: "Never use 'Best-in-Class' or 'Robust'", type: "dont" },
    { id: "dont-2", text: "Don't promise features you can't ship", type: "dont" },
    { id: "dont-3", text: "Avoid passive voice", type: "dont" },
];

export default function Step16MessagingGuardrails() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(17)?.data as any; // Map to 17

    const [dos, setDos] = useState<Guardrail[]>(stepData?.dos || DEFAULT_DOS);
    const [donts, setDonts] = useState<Guardrail[]>(stepData?.donts || DEFAULT_DONTS);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [newRuleText, setNewRuleText] = useState("");
    const [newRuleType, setNewRuleType] = useState<"do" | "dont">("do");
    const [isGenerating, setIsGenerating] = useState(false);

    const containerRef = useRef<HTMLDivElement>(null);

    // Fetch AI-generated messaging rules
    const generateMessagingRules = useCallback(async () => {
        setIsGenerating(true);
        try {
            const foundationData = getStepById(0)?.data as { company_info?: any } | undefined;
            const positioningData = getStepById(12)?.data as { positioning?: any } | undefined;

            const response = await fetch('/api/onboarding/messaging-rules', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: 'demo',
                    company_info: foundationData?.company_info || {},
                    positioning: positioningData?.positioning || {}
                })
            });

            const data = await response.json();
            if (data.success && data.messaging_rules?.rules) {
                const aiDos = data.messaging_rules.rules
                    .filter((r: any) => r.category === 'tone' || r.category === 'language')
                    .slice(0, 3)
                    .map((r: any, i: number) => ({
                        id: `ai-do-${i}`,
                        text: r.name,
                        type: "do" as const,
                        isCustom: false
                    }));

                const aiDonts = data.messaging_rules.rules
                    .filter((r: any) => r.category === 'claims' || r.category === 'legal')
                    .slice(0, 3)
                    .map((r: any, i: number) => ({
                        id: `ai-dont-${i}`,
                        text: r.name,
                        type: "dont" as const,
                        isCustom: false
                    }));

                setDos([...DEFAULT_DOS, ...aiDos]);
                setDonts([...DEFAULT_DONTS, ...aiDonts]);
                updateStepData(17, { dos: [...DEFAULT_DOS, ...aiDos], donts: [...DEFAULT_DONTS, ...aiDonts], confirmed: false });
            }
        } catch (err) {
            console.error('Failed to generate messaging rules:', err);
        } finally {
            setIsGenerating(false);
        }
    }, [getStepById, updateStepData]);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll(".animate-in"),
            { opacity: 0, y: 12 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.05, ease: "power2.out" }
        );
    }, []);

    // Mock Validation Logic
    const validateRule = (text: string, type: "do" | "dont") => {
        const forbiddenWords = ["synergy", "paradigm", "disrupt", "revolutionary"];
        const hasForbidden = forbiddenWords.some(w => text.toLowerCase().includes(w));

        if (hasForbidden) {
            toast.warning("Not Recommended", {
                description: `Strategic Conflict: The word '${forbiddenWords.find(w => text.toLowerCase().includes(w))}' dilutes your 'No Fluff' position.`,
                icon: <AlertTriangle size={16} className="text-[var(--warning)]" />
            });
            return false; // Proceed anyway? User said "pop-up appears", implies warning.
            // We'll allow it but show warning.
        }
        return true;
    };

    const handleAddRule = () => {
        if (!newRuleText.trim()) return;

        validateRule(newRuleText, newRuleType);

        const newRule: Guardrail = {
            id: `custom-${Date.now()}`,
            text: newRuleText,
            type: newRuleType,
            isCustom: true
        };

        if (newRuleType === "do") setDos([...dos, newRule]);
        else setDonts([...donts, newRule]);

        setNewRuleText("");
    };

    const handleDelete = (id: string, type: "do" | "dont") => {
        if (type === "do") setDos(dos.filter(d => d.id !== id));
        else setDonts(donts.filter(d => d.id !== id));
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(17, { dos, donts, confirmed: true });
        updateStepStatus(17, "complete");
    };

    return (
        <div ref={containerRef} className="h-full flex flex-col max-w-5xl mx-auto space-y-6 pb-6">

            {/* Header */}
            <div className="text-center space-y-2 shrink-0">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 17 / 23</span>
                <h2 className="font-serif text-2xl text-[var(--ink)]">Messaging Guardrails</h2>
                <div className="flex items-center justify-center gap-2 text-[var(--secondary)]">
                    <Shield size={14} />
                    <span className="font-serif italic text-sm">"Define the rules of engagement."</span>
                </div>
                <BlueprintButton
                    onClick={generateMessagingRules}
                    disabled={isGenerating}
                    size="sm"
                    className="mt-2"
                >
                    {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                    {isGenerating ? "Generating..." : "AI Generate Rules"}
                </BlueprintButton>
            </div>

            {/* Main Content: Split Columns */}
            <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch animate-in">

                {/* DO'S Column */}
                <div className="border border-[var(--success)]/20 bg-[var(--success)]/5 rounded-lg p-5 flex flex-col">
                    <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--success)]/20">
                        <div className="flex items-center gap-2 text-[var(--success)]">
                            <CheckCircle size={18} />
                            <span className="font-technical text-sm font-bold tracking-wider">ALWAYS DO THIS</span>
                        </div>
                        <span className="font-serif text-xs italic text-[var(--success)] opacity-70">The Green Zone</span>
                    </div>

                    <div className="space-y-3 flex-1 overflow-y-auto pr-2">
                        {dos.map(item => (
                            <div key={item.id} className="flex items-start gap-3 p-3 bg-[var(--paper)] border border-[var(--border-subtle)] rounded shadow-sm group">
                                <Check size={16} className="text-[var(--success)] mt-0.5 shrink-0" />
                                <span className={cn("text-sm text-[var(--ink)] flex-1", item.isCustom && "italic")}>{item.text}</span>
                                {item.isCustom && (
                                    <button onClick={() => handleDelete(item.id, "do")} className="text-[var(--border)] hover:text-[var(--error)] opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Trash2 size={14} />
                                    </button>
                                )}
                            </div>
                        ))}
                        {/* Empty Ghost for Adding */}
                        <div className="p-3 border border-dashed border-[var(--success)]/30 rounded flex items-center justify-center text-[var(--success)]/50 text-xs">
                            + Add custom rule below
                        </div>
                    </div>
                </div>

                {/* DON'TS Column */}
                <div className="border border-[var(--error)]/20 bg-[var(--error)]/5 rounded-lg p-5 flex flex-col">
                    <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--error)]/20">
                        <div className="flex items-center gap-2 text-[var(--error)]">
                            <AlertTriangle size={18} />
                            <span className="font-technical text-sm font-bold tracking-wider">NEVER DO THIS</span>
                        </div>
                        <span className="font-serif text-xs italic text-[var(--error)] opacity-70">The Red Zone</span>
                    </div>

                    <div className="space-y-3 flex-1 overflow-y-auto pr-2">
                        {donts.map(item => (
                            <div key={item.id} className="flex items-start gap-3 p-3 bg-[var(--paper)] border border-[var(--border-subtle)] rounded shadow-sm group">
                                <X size={16} className="text-[var(--error)] mt-0.5 shrink-0" />
                                <span className={cn("text-sm text-[var(--ink)] flex-1", item.isCustom && "italic")}>{item.text}</span>
                                {item.isCustom && (
                                    <button onClick={() => handleDelete(item.id, "dont")} className="text-[var(--border)] hover:text-[var(--error)] opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Trash2 size={14} />
                                    </button>
                                )}
                            </div>
                        ))}
                        {/* Empty Ghost for Adding */}
                        <div className="p-3 border border-dashed border-[var(--error)]/30 rounded flex items-center justify-center text-[var(--error)]/50 text-xs">
                            + Add custom rule below
                        </div>
                    </div>
                </div>
            </div>

            {/* Input Action Bar */}
            <BlueprintCard padding="sm" className="bg-[var(--canvas)] animate-in">
                <div className="flex items-center gap-3">
                    <select
                        value={newRuleType}
                        onChange={(e) => setNewRuleType(e.target.value as "do" | "dont")}
                        className="h-10 px-3 rounded border border-[var(--border)] bg-[var(--paper)] text-xs font-technical uppercase focus:outline-none focus:border-[var(--blueprint)]"
                    >
                        <option value="do">Add "Do"</option>
                        <option value="dont">Add "Don't"</option>
                    </select>
                    <input
                        type="text"
                        value={newRuleText}
                        onChange={(e) => setNewRuleText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddRule()}
                        placeholder={newRuleType === "do" ? "E.g. Always use active voice..." : "E.g. Never use jargon..."}
                        className="flex-1 h-10 px-4 rounded border border-[var(--border)] bg-[var(--paper)] text-sm focus:outline-none focus:border-[var(--blueprint)]"
                    />
                    <BlueprintButton onClick={handleAddRule} size="sm">
                        <Plus size={14} /> Add Rule
                    </BlueprintButton>
                </div>
            </BlueprintCard>

            {/* Footer */}
            <div data-animate className="flex justify-center shrink-0 h-16">
                {!confirmed ? (
                    <BlueprintButton onClick={handleConfirm} size="lg" className="px-12">
                        <Shield size={14} /> Establish Guardrails
                    </BlueprintButton>
                ) : (
                    <div className="flex items-center gap-2 text-[var(--success)]">
                        <CheckCircle size={20} /> <span className="font-medium text-sm">Rules Locked</span>
                    </div>
                )}
            </div>
        </div>
    );
}
