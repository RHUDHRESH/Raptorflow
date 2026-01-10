"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Palette, Type, Layout, Sparkles } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 20: Brand Augmentation
   Review and plan brand element updates
   ══════════════════════════════════════════════════════════════════════════════ */

interface BrandElement {
    id: string;
    category: string;
    icon: React.ElementType;
    name: string;
    current: string;
    recommendation: string;
    action: "keep" | "update" | "create";
    code: string;
}

const INITIAL_ELEMENTS: BrandElement[] = [
    { id: "1", category: "Visual", icon: Palette, name: "Color Palette", current: "Blue primary, gray secondary", recommendation: "Consider warmer accent for approachability", action: "keep", code: "BRD-01" },
    { id: "2", category: "Visual", icon: Type, name: "Typography", current: "Inter for body, Playfair for headlines", recommendation: "Strong pairing, maintain consistency", action: "keep", code: "BRD-02" },
    { id: "3", category: "Visual", icon: Layout, name: "Logo", current: "Wordmark with icon", recommendation: "Add favicon variant for small sizes", action: "update", code: "BRD-03" },
    { id: "4", category: "Voice", icon: Sparkles, name: "Tone", current: "Professional but friendly", recommendation: "Lean more into confidence, less hedging", action: "update", code: "BRD-04" },
];

export default function Step20BrandAugmentation() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(20)?.data as { elements?: BrandElement[]; confirmed?: boolean } | undefined;

    const [elements, setElements] = useState<BrandElement[]>(stepData?.elements || INITIAL_ELEMENTS);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    }, []);

    const saveData = (items: BrandElement[]) => { setElements(items); updateStepData(20, { elements: items }); };
    const updateAction = (id: string, action: "keep" | "update" | "create") => saveData(elements.map((e) => (e.id === id ? { ...e, action } : e)));
    const handleConfirm = () => { setConfirmed(true); updateStepData(20, { elements, confirmed: true }); updateStepStatus(20, "complete"); };

    const actionConfig = {
        keep: { label: "KEEP", color: "text-[var(--success)]", bg: "bg-[var(--success)]", light: "bg-[var(--success-light)]" },
        update: { label: "UPDATE", color: "text-[var(--warning)]", bg: "bg-[var(--warning)]", light: "bg-[var(--warning-light)]" },
        create: { label: "CREATE", color: "text-[var(--blueprint)]", bg: "bg-[var(--blueprint)]", light: "bg-[var(--blueprint-light)]" },
    };

    return (
        <div ref={containerRef} className="space-y-6">
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <p className="text-sm text-[var(--secondary)]">Review your brand elements and decide what to keep, update, or create.</p>
            </BlueprintCard>

            {/* Elements */}
            {elements.map((el, i) => (
                <BlueprintCard key={el.id} data-animate code={el.code} showCorners padding="md">
                    <div className="flex items-start gap-4 mb-4">
                        <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center">
                            <el.icon size={18} strokeWidth={1.5} className="text-[var(--blueprint)]" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-sm font-semibold text-[var(--ink)]">{el.name}</h3>
                            <p className="font-technical text-[var(--muted)] mb-1">CURRENT: {el.current}</p>
                            <p className="text-xs text-[var(--secondary)]">💡 {el.recommendation}</p>
                        </div>
                        <BlueprintBadge variant={el.action === "keep" ? "success" : el.action === "update" ? "warning" : "blueprint"}>{actionConfig[el.action].label}</BlueprintBadge>
                    </div>
                    <div className="flex gap-2">
                        {(["keep", "update", "create"] as const).map((action) => {
                            const isActive = el.action === action;
                            return (
                                <button key={action} onClick={() => updateAction(el.id, action)} className={`flex-1 px-4 py-2 font-technical rounded-[var(--radius-sm)] transition-all ${isActive ? `${actionConfig[action].bg} text-[var(--paper)]` : "bg-[var(--canvas)] text-[var(--muted)] hover:bg-[var(--paper)]"}`}>
                                    {actionConfig[action].label}
                                </button>
                            );
                        })}
                    </div>
                </BlueprintCard>
            ))}

            {/* Summary */}
            <BlueprintCard data-animate figure="FIG. 01" title="Summary" code="SUM" showCorners padding="md">
                <KPIGrid columns={3}>
                    <BlueprintKPI label="Keep" value={String(elements.filter((e) => e.action === "keep").length)} code="K" />
                    <BlueprintKPI label="Update" value={String(elements.filter((e) => e.action === "update").length)} code="U" trend="up" />
                    <BlueprintKPI label="Create" value={String(elements.filter((e) => e.action === "create").length)} code="C" />
                </KPIGrid>
            </BlueprintCard>

            {/* Confirm */}
            {!confirmed && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM"><Check size={14} strokeWidth={1.5} />Confirm Brand Plan</BlueprintButton>
            )}
            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3"><Check size={18} strokeWidth={1.5} className="text-[var(--success)]" /><span className="text-sm font-medium text-[var(--ink)]">Brand augmentation plan confirmed</span><BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge></div>
                </BlueprintCard>
            )}

            {/* Document Footer */}
            <div className="flex justify-center pt-4"><span className="font-technical text-[var(--muted)]">DOCUMENT: BRAND-AUGMENTATION | STEP 20/25</span></div>
        </div>
    );
}
