"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
    Check, Box, Users, BookOpen, Target, CheckCircle, Search, ShieldAlert,
    BarChart3, ArrowRight, MousePointerClick
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 13: The Strategic Grid (Compact)

   PURPOSE: "No Scroll" Strategic Dashboard.
   - Top: 4-Column Summary (Mini).
   - Middle: 3-Column AI Options (Selectable).
   - Bottom: 2-Column Gap Analysis (Compact).
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface PositioningOption {
    id: string;
    name: string;
    description: string;
    strategy: string;
    confidence: number;
    advantages: string[];
}

function MiniGridCell({ label, value, icon: Icon }: { label: string, value: string, icon: any }) {
    return (
        <div className="p-3 bg-[var(--paper)] border-r border-[var(--border-subtle)] last:border-0 flex items-center gap-3">
            <div className="p-1.5 rounded bg-[var(--canvas)] text-[var(--muted)]">
                <Icon size={14} />
            </div>
            <div className="min-w-0">
                <span className="font-technical text-[8px] uppercase tracking-wider text-[var(--muted)] block">{label}</span>
                <span className="font-serif text-sm text-[var(--ink)] truncate block">{value}</span>
            </div>
        </div>
    );
}

function CompactThreatCard({ type, items }: { type: "threat" | "opportunity", items: string[] }) {
    const isThreat = type === "threat";
    return (
        <div className={cn("p-4 rounded border h-full", isThreat ? "bg-[var(--error)]/5 border-[var(--error)]/20" : "bg-[var(--success)]/5 border-[var(--success)]/20")}>
            <div className="flex items-center gap-2 mb-2">
                {isThreat ? <ShieldAlert size={12} className="text-[var(--error)]" /> : <Target size={12} className="text-[var(--success)]" />}
                <span className={cn("font-technical text-[9px] uppercase tracking-widest", isThreat ? "text-[var(--error)]" : "text-[var(--success)]")}>
                    {isThreat ? "Threats" : "Opportunities"}
                </span>
            </div>
            <ul className="space-y-1">
                {items.map((item, i) => (
                    <li key={i} className="flex items-start gap-1.5 text-xs text-[var(--ink)]">
                        <span className="mt-1 w-0.5 h-0.5 rounded-full bg-[var(--ink)] shrink-0" />
                        {item}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default function Step12CapabilityMatrix() { // Maps to Step 13
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(12)?.data as any;

    const [selectedOption, setSelectedOption] = useState<string | null>(stepData?.selectedOption || null);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Mock Options
    const options: PositioningOption[] = [
        { id: 'POS-1', name: 'Innovation Leader', description: 'First-mover advantage in a new category.', strategy: 'innovation', confidence: 0.85, advantages: ['Premium pricing', 'Brand authority'] },
        { id: 'POS-2', name: 'Niche Specialist', description: 'Deep expertise for a specific vertical.', strategy: 'niche', confidence: 0.92, advantages: ['Low competition', 'High loyalty'] },
        { id: 'POS-3', name: 'Service Partner', description: 'High-touch implementation & support.', strategy: 'service', confidence: 0.78, advantages: ['Retention', 'Upsell potential'] },
    ];

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll(".animate-in"),
            { opacity: 0, y: 10 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.1 }
        );
    }, []);

    const handleConfirm = () => {
        if (!selectedOption) return;
        setConfirmed(true);
        updateStepData(12, { selectedOption, confirmed: true });
        updateStepStatus(12, "complete"); // Maps to actual Step 13 in store
    };

    return (
        <div ref={containerRef} className="h-full flex flex-col pb-4">

            {/* Header (Tiny) */}
            <div className="flex justify-between items-end mb-6 shrink-0 border-b border-[var(--border-subtle)] pb-4">
                <div>
                    <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 13 / 24</span>
                    <h2 className="font-serif text-2xl text-[var(--ink)]">The Strategic Grid</h2>
                </div>
                {!confirmed && selectedOption && (
                    <BlueprintButton size="sm" onClick={handleConfirm}>
                        <span>Lock Strategy</span> <Check size={14} />
                    </BlueprintButton>
                )}
                {confirmed && <div className="text-[var(--success)] text-xs font-medium flex items-center gap-1"><CheckCircle size={14} /> Locked</div>}
            </div>

            {/* 1. Summary Strip (Compact) */}
            <div className="animate-in grid grid-cols-4 border border-[var(--border-subtle)] rounded overflow-hidden mb-6 shrink-0">
                <MiniGridCell label="Market" value="Enterprise B2B" icon={Box} />
                <MiniGridCell label="Category" value="Visual Collab" icon={Search} />
                <MiniGridCell label="Tribe" value="Product Managers" icon={Users} />
                <MiniGridCell label="Narrative" value="Speed vs Bloat" icon={BookOpen} />
            </div>

            {/* 2. Main Content Grid */}
            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in">

                {/* Left: AI Options (2/3 width) */}
                <div className="lg:col-span-2 flex flex-col gap-4">
                    <h3 className="font-technical text-[10px] uppercase text-[var(--muted)] tracking-wider">SELECT STRATEGIC POSITION</h3>
                    <div className="grid grid-cols-1 gap-3 overflow-y-auto pr-1">
                        {options.map((opt) => (
                            <div
                                key={opt.id}
                                onClick={() => !confirmed && setSelectedOption(opt.id)}
                                className={cn(
                                    "p-4 border rounded transition-all cursor-pointer flex items-center justify-between group",
                                    selectedOption === opt.id
                                        ? "bg-[var(--ink)] border-[var(--ink)] text-[var(--paper)] shadow-md"
                                        : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)] text-[var(--ink)]"
                                )}
                            >
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <h4 className="font-serif text-lg leading-none">{opt.name}</h4>
                                        <span className={cn("text-[9px] font-technical px-1.5 py-0.5 rounded", selectedOption === opt.id ? "bg-[var(--paper)]/20 text-[var(--paper)]" : "bg-[var(--canvas)] text-[var(--muted)]")}>
                                            {Math.round(opt.confidence * 100)}% MATCH
                                        </span>
                                    </div>
                                    <p className={cn("text-xs", selectedOption === opt.id ? "text-[var(--paper)]/80" : "text-[var(--secondary)]")}>
                                        {opt.description}
                                    </p>
                                </div>
                                {selectedOption === opt.id ? <CheckCircle size={20} className="text-[var(--success)]" /> : <MousePointerClick size={16} className="text-[var(--border)] group-hover:text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-opacity" />}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right: Gap Analysis (1/3 width) */}
                <div className="flex flex-col gap-4 h-full">
                    <h3 className="font-technical text-[10px] uppercase text-[var(--muted)] tracking-wider">GAP ANALYSIS</h3>
                    <div className="flex-1 flex flex-col gap-3 min-h-0">
                        <CompactThreatCard type="threat" items={["Incumbents bundling free", "Market fatigue"]} />
                        <CompactThreatCard type="opportunity" items={["'Simple' niche vacant", "Faster implementation"]} />
                    </div>
                </div>

            </div>
        </div>
    );
}
