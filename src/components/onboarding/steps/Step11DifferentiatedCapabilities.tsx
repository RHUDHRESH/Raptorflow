"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Target, RefreshCw, CheckCircle, Move, Sparkles } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { StepLoadingState } from "../StepStates";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 11: Perceptual Map (Compact)
   
   PURPOSE: "No Scroll" Map Selector.
   - Maps are smaller (MiniMaps).
   - Layout is strictly horizontal.
   - "Deep Dive" info appears below ONLY when selected, or inside the card.
   ══════════════════════════════════════════════════════════════════════════════ */

interface PositionOption {
    id: string;
    name: string;
    xAxisLabel: string;
    yAxisLabel: string;
    xValue: number;
    yValue: number;
    narrative: string;
    competitors: { name: string, x: number, y: number }[];
}

function MiniMap({
    option,
    isSelected,
    onClick
}: {
    option: PositionOption;
    isSelected: boolean;
    onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "group relative w-full aspect-[4/3] bg-[var(--paper)] border transition-all duration-300 overflow-hidden flex flex-col items-center justify-center p-4",
                isSelected
                    ? "border-[var(--ink)] shadow-xl z-10 scale-[1.02]"
                    : "border-[var(--border-subtle)] hover:border-[var(--blueprint)] hover:shadow-md"
            )}
        >
            {/* Grid */}
            <div className="absolute inset-4 border border-[var(--border-subtle)] opacity-40" />
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-full h-px bg-[var(--border)]" />
                <div className="h-full w-px bg-[var(--border)] absolute" />
            </div>

            {/* Labels (Tiny) */}
            <span className="absolute left-2 top-1/2 -translate-y-1/2 -rotate-90 text-[7px] font-technical uppercase tracking-wider text-[var(--muted)]">{option.yAxisLabel.split('/')[0]}</span>
            <span className="absolute right-2 top-1/2 -translate-y-1/2 rotate-90 text-[7px] font-technical uppercase tracking-wider text-[var(--muted)]">{option.yAxisLabel.split('/')[1]}</span>
            <span className="absolute bottom-2 left-1/2 -translate-x-1/2 text-[7px] font-technical uppercase tracking-wider text-[var(--muted)]">{option.xAxisLabel.split('/')[0]}</span>
            <span className="absolute top-2 left-1/2 -translate-x-1/2 text-[7px] font-technical uppercase tracking-wider text-[var(--muted)]">{option.xAxisLabel.split('/')[1]}</span>

            {/* Dots */}
            {option.competitors.map((comp, i) => (
                <div key={i} className="absolute w-1.5 h-1.5 rounded-full bg-[var(--muted)]/40" style={{ left: `${50 + (comp.x / 2.5)}%`, bottom: `${50 + (comp.y / 2.5)}%` }} />
            ))}
            <div className={cn("absolute w-3 h-3 rounded-full border shadow-sm transition-all", isSelected ? "bg-[var(--ink)] border-white scale-125" : "bg-[var(--blueprint)] border-white")}
                style={{ left: `${50 + (option.xValue / 2.5)}%`, bottom: `${50 + (option.yValue / 2.5)}%` }} />
        </button>
    );
}

export default function Step11DifferentiatedCapabilities() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(11)?.data as any;

    const [isGenerating, setIsGenerating] = useState(false);
    const [options, setOptions] = useState<PositionOption[]>([]);
    const [selectedPosition, setSelectedPosition] = useState<PositionOption | null>(stepData?.selectedPosition || null);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    const generateOptions = () => {
        setIsGenerating(true);
        setTimeout(() => {
            setOptions([
                { id: "opt-1", name: "The Specialist", narrative: "Win on 'Specific Depth' vs 'Broad Utility'.", xAxisLabel: "General / Specific", yAxisLabel: "Complex / Simple", xValue: 80, yValue: 60, competitors: [{ name: "A", x: -50, y: -20 }, { name: "B", x: -30, y: 40 }] },
                { id: "opt-2", name: "The Partner", narrative: "High-touch service in a self-serve world.", xAxisLabel: "Vendor / Partner", yAxisLabel: "DIY / DFY", xValue: 70, yValue: 75, competitors: [{ name: "A", x: -60, y: -60 }, { name: "B", x: -20, y: -40 }] },
                { id: "opt-3", name: "The Speedster", narrative: "The 'Instant' alternative to slow giants.", xAxisLabel: "Slow / Instant", yAxisLabel: "Bloated / Lean", xValue: 90, yValue: 80, competitors: [{ name: "A", x: -40, y: -30 }, { name: "B", x: -50, y: -50 }] }
            ]);
            setIsGenerating(false);
        }, 1500);
    };

    useEffect(() => {
        if (!containerRef.current || isGenerating) return;
        gsap.fromTo(containerRef.current.querySelectorAll(".animate-in"), { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.05 });
    }, [options, isGenerating]);

    const handleConfirm = () => {
        if (!selectedPosition) return;
        setConfirmed(true);
        updateStepData(11, { selectedPosition, confirmed: true });
        updateStepStatus(11, "complete");
    };

    if (isGenerating) return <StepLoadingState title="Calculating Quadrants" message="Mapping open market spaces..." stage="Analyzing..." />;

    if (options.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
                <div className="p-4 rounded-full bg-[var(--paper)] border border-[var(--blueprint)]/30 text-[var(--blueprint)] shadow-lg animate-pulse">
                    <Move size={32} strokeWidth={1} />
                </div>
                <div>
                    <h3 className="font-serif text-2xl text-[var(--ink)] mb-2">Find Your Empty Space</h3>
                    <p className="text-[var(--secondary)] max-w-md mx-auto text-sm">We'll identify 3 strategic quadrants where you have zero direct competition.</p>
                </div>
                <BlueprintButton size="lg" onClick={generateOptions}>
                    <Sparkles size={14} /> Reveal Winning Positions
                </BlueprintButton>
            </div>
        );
    }

    return (
        <div ref={containerRef} className="h-full flex flex-col pb-8">
            <div className="text-center space-y-2 mb-8 shrink-0">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 11 / 24</span>
                <h2 className="font-serif text-2xl text-[var(--ink)]">The Perceptual Map</h2>
                <p className="font-serif text-[var(--secondary)] italic text-sm">"Choose the battleground where you have no equal."</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start px-4">
                {options.map((opt) => (
                    <div key={opt.id} className="animate-in space-y-3">
                        <MiniMap option={opt} isSelected={selectedPosition?.id === opt.id} onClick={() => { if (!confirmed) setSelectedPosition(opt); }} />
                        <div className="text-center px-1">
                            <h3 className={cn("font-serif text-lg transition-colors", selectedPosition?.id === opt.id ? "text-[var(--ink)]" : "text-[var(--secondary)]")}>{opt.name}</h3>
                            <p className="text-[10px] font-serif text-[var(--muted)] leading-tight mt-1 min-h-[2.5em]">{opt.narrative}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex justify-center mt-auto pt-8 shrink-0 h-20">
                {selectedPosition && !confirmed && (
                    <div className="animate-in zoom-in slide-in-from-bottom-2">
                        <BlueprintButton onClick={handleConfirm} size="lg" className="px-10">
                            <span>Claim This Territory</span>
                            <Target size={14} />
                        </BlueprintButton>
                    </div>
                )}
                {selectedPosition && confirmed && (
                    <div className="flex items-center gap-2 text-[var(--success)] animate-in zoom-in">
                        <CheckCircle size={20} /> <span className="font-medium text-sm">Position Secured</span>
                    </div>
                )}
            </div>
        </div>
    );
}
