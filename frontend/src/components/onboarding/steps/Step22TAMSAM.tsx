"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, TrendingUp } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 22: TAM/SAM/SOM
   Define market sizing pyramid
   ══════════════════════════════════════════════════════════════════════════════ */

interface MarketSize { tam: { value: string; description: string }; sam: { value: string; description: string }; som: { value: string; description: string }; }

const INITIAL_SIZE: MarketSize = {
    tam: { value: "$45B", description: "Total marketing software market globally" },
    sam: { value: "$8B", description: "B2B SaaS marketing tools in US/EU" },
    som: { value: "$150M", description: "Founder-led companies, 10-50 employees, needing positioning help" },
};

export default function Step22TAMSAM() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(22)?.data as { sizes?: MarketSize; confirmed?: boolean } | undefined;
    const [sizes, setSizes] = useState<MarketSize>(stepData?.sizes || INITIAL_SIZE);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    }, []);

    const handleChange = (tier: "tam" | "sam" | "som", field: "value" | "description", value: string) => { const updated = { ...sizes, [tier]: { ...sizes[tier], [field]: value } }; setSizes(updated); updateStepData(22, { sizes: updated }); };
    const handleConfirm = () => { setConfirmed(true); updateStepData(22, { sizes, confirmed: true }); updateStepStatus(22, "complete"); };

    const tierConfig = {
        tam: { label: "TAM", full: "Total Addressable Market", color: "text-[var(--blueprint)]", bg: "bg-[var(--blueprint-light)]", size: "w-full", code: "MKT-01" },
        sam: { label: "SAM", full: "Serviceable Addressable Market", color: "text-[var(--warning)]", bg: "bg-[var(--warning-light)]", size: "w-3/4", code: "MKT-02" },
        som: { label: "SOM", full: "Serviceable Obtainable Market", color: "text-[var(--success)]", bg: "bg-[var(--success-light)]", size: "w-1/2", code: "MKT-03" },
    };

    return (
        <div ref={containerRef} className="space-y-6">
            <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                <p className="text-sm text-[var(--secondary)]">Define your market size pyramid: Total, Serviceable, and Obtainable market.</p>
            </BlueprintCard>

            <BlueprintCard data-animate figure="FIG. 01" title="Market Pyramid" code="PYR" showCorners padding="lg">
                <div className="flex flex-col items-center">
                    {(["tam", "sam", "som"] as const).map((tier) => {
                        const config = tierConfig[tier];
                        return (
                            <div key={tier} className={`flex flex-col items-center w-full z-10`} style={{ width: config.size }}>
                                <div className={`${config.bg} p-4 w-full rounded-[var(--radius-md)] text-center border-2 border-[var(--paper)] shadow-sm hover:scale-[1.02] transition-transform duration-300`}>
                                    <span className={`text-xl font-bold ${config.color}`}>{sizes[tier].value}</span>
                                    <span className={`font-technical ${config.color} ml-2`}>{config.label}</span>
                                </div>
                            </div>
                        );
                    })}
                    <div className="flex items-center gap-2 mt-4"><TrendingUp size={12} strokeWidth={1.5} className="text-[var(--muted)]" /><span className="font-technical text-[var(--muted)]">YOUR GROWTH TRAJECTORY</span></div>
                </div>
            </BlueprintCard>

            {(["tam", "sam", "som"] as const).map((tier, i) => {
                const config = tierConfig[tier];
                return (
                    <BlueprintCard key={tier} data-animate figure={`FIG. ${String(i + 2).padStart(2, "0")}`} title={config.full} code={config.code} showCorners padding="md">
                        <div className="flex items-center gap-2 mb-4"><BlueprintBadge variant={tier === "tam" ? "blueprint" : tier === "sam" ? "warning" : "success"}>{config.label}</BlueprintBadge></div>
                        <div className="grid grid-cols-3 gap-4">
                            <input type="text" value={sizes[tier].value} onChange={(e) => handleChange(tier, "value", e.target.value)} placeholder="$XXB" className="h-10 px-4 text-center font-mono font-bold text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] placeholder:font-sans placeholder:font-normal" />
                            <input type="text" value={sizes[tier].description} onChange={(e) => handleChange(tier, "description", e.target.value)} placeholder="Description" className="col-span-2 h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]" />
                        </div>
                    </BlueprintCard>
                );
            })}

            {!confirmed && (
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM"><Check size={14} strokeWidth={1.5} />Confirm Market Sizing</BlueprintButton>
            )}
            {confirmed && (
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                    <div className="flex items-center gap-3"><Check size={18} strokeWidth={1.5} className="text-[var(--success)]" /><span className="text-sm font-medium text-[var(--ink)]">Market sizing confirmed</span><BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge></div>
                </BlueprintCard>
            )}

            <div className="flex justify-center pt-4"><span className="font-technical text-[var(--muted)]">DOCUMENT: TAM-SAM-SOM | STEP 22/25</span></div>
        </div>
    );
}
