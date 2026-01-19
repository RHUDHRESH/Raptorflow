"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
    Check, Shield, Zap, Target, ArrowRight, AlertTriangle, CheckCircle, ChevronDown
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 9: Market Category Selection (Compact)
   
   PURPOSE: "No Scroll" Category Strategy.
   - Cards are shorter by default.
   - Details expand smoothly (Accordion style).
   - Horizontal layout optimized for laptop screens.
   ══════════════════════════════════════════════════════════════════════════════ */

type CategoryPathType = "safe" | "clever" | "bold";

interface CategoryPath {
    id: CategoryPathType;
    title: string;
    subtitle: string;
    description: string;
    icon: any;
    // Deep dive details
    effort: "Low" | "Medium" | "High";
    education: "Low" | "Medium" | "High";
    pricing: "Commoditized" | "Premium" | "Luxury";
    pros: string[];
    cons: string[];
}

const CATEGORY_PATHS: CategoryPath[] = [
    {
        id: "safe",
        title: "The Better Option",
        subtitle: "The Safe Path",
        description: "Compete on specs in an existing category. You are 'Better X'.",
        icon: Shield,
        effort: "Low",
        education: "Low",
        pricing: "Commoditized",
        pros: ["Instant market understanding", "Existing budgets"],
        cons: ["Price wars", "Hard to differentiate"]
    },
    {
        id: "clever",
        title: "The Niche Specialist",
        subtitle: "The Clever Path",
        description: "Dominate a sub-segment. You are the expert for a specific tribe.",
        icon: Target,
        effort: "Medium",
        education: "Medium",
        pricing: "Premium",
        pros: ["Higher margins", "Stronger loyalty"],
        cons: ["Smaller TAM", "Scaling limits"]
    },
    {
        id: "bold",
        title: "The Category Creator",
        subtitle: "The Bold Move",
        description: "Redefine the problem. Create a new box. You are 'The First X'.",
        icon: Zap,
        effort: "High",
        education: "High",
        pricing: "Luxury",
        pros: ["Monopoly potential", "Zero competition"],
        cons: ["High education cost", "Risk of rejection"]
    }
];

function PathCard({
    path,
    isSelected,
    onSelect
}: {
    path: CategoryPath;
    isSelected: boolean;
    onSelect: () => void;
}) {
    const Icon = path.icon;

    return (
        <div
            onClick={onSelect}
            className={cn(
                "group relative cursor-pointer border transition-all duration-300 ease-out overflow-hidden flex flex-col items-stretch",
                isSelected
                    ? "bg-[var(--ink)] border-[var(--ink)] text-[var(--paper)] shadow-xl z-10"
                    : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)] hover:shadow-md"
            )}
            style={{ height: isSelected ? 'auto' : '280px' }} // Compact height by default
        >
            {/* Header Content */}
            <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                    <div className={cn(
                        "p-2 rounded-full border transition-colors",
                        isSelected
                            ? "bg-[var(--paper)] border-[var(--paper)] text-[var(--ink)]"
                            : "bg-[var(--canvas)] border-[var(--border-subtle)] text-[var(--muted)] group-hover:text-[var(--blueprint)]"
                    )}>
                        <Icon size={20} strokeWidth={1.5} />
                    </div>
                    {isSelected && <CheckCircle size={20} className="text-[var(--paper)] animate-in zoom-in" />}
                </div>

                <div className="space-y-1 mb-3">
                    <span className={cn(
                        "font-technical text-[9px] uppercase tracking-[0.2em] block",
                        isSelected ? "text-[var(--paper)]/60" : "text-[var(--blueprint)]"
                    )}>
                        {path.subtitle}
                    </span>
                    <h3 className={cn(
                        "font-serif text-xl",
                        isSelected ? "text-[var(--paper)]" : "text-[var(--ink)]"
                    )}>
                        {path.title}
                    </h3>
                </div>

                <p className={cn(
                    "text-xs font-serif leading-relaxed italic border-l-2 pl-3 py-1 mb-4",
                    isSelected ? "text-[var(--paper)]/80 border-[var(--paper)]/30" : "text-[var(--secondary)] border-[var(--blueprint)]/30"
                )}>
                    "{path.description}"
                </p>

                {!isSelected && (
                    <div className="w-full flex items-center justify-center pt-2 mt-auto">
                        <ChevronDown size={16} className="text-[var(--border)] group-hover:text-[var(--blueprint)] animate-bounce" />
                    </div>
                )}
            </div>

            {/* Expanded Details (Only visible when selected) */}
            {isSelected && (
                <div className="px-6 py-4 bg-[var(--paper)]/5 border-t border-[var(--paper)]/10 animate-in slide-in-from-top-2 duration-300">
                    <div className="grid grid-cols-2 gap-4 mb-4 text-[10px]">
                        <div>
                            <span className="opacity-50 block mb-1">Effort</span>
                            <span className="font-bold">{path.effort}</span>
                        </div>
                        <div>
                            <span className="opacity-50 block mb-1">Pricing</span>
                            <span className="font-bold">{path.pricing}</span>
                        </div>
                    </div>
                    <div className="space-y-2">
                        <div className="text-[10px]">
                            <span className="text-[var(--success)] block mb-1 uppercase tracking-wider font-bold">Pros</span>
                            <ul className="list-disc pl-3 opacity-90 space-y-0.5">
                                {path.pros.map(p => <li key={p}>{p}</li>)}
                            </ul>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default function Step9CompetitiveLadder() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(9)?.data as any;

    const [selectedPath, setSelectedPath] = useState<CategoryPathType | null>(stepData?.selectedPath || null);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll(".animate-card"),
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" }
        );
    }, []);

    const handleConfirm = () => {
        if (!selectedPath) return;
        setConfirmed(true);
        updateStepData(9, { selectedPath, confirmed: true });
        updateStepStatus(9, "complete");
    };

    return (
        <div ref={containerRef} className="h-full flex flex-col justify-start pb-8">

            <div className="text-center space-y-3 mb-8 shrink-0">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 09 / 24</span>
                <h2 className="font-serif text-3xl text-[var(--ink)]">Select Your Battlefield</h2>
                <p className="font-serif text-[var(--secondary)] italic text-sm">
                    "Strategy is about choice. You cannot be all things to all people."
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start h-full px-4">
                {CATEGORY_PATHS.map((path) => (
                    <div key={path.id} className="animate-card">
                        <PathCard
                            path={path}
                            isSelected={selectedPath === path.id}
                            onSelect={() => setSelectedPath(path.id)}
                        />
                    </div>
                ))}
            </div>

            <div className="flex justify-center mt-8 shrink-0 h-16">
                {selectedPath && !confirmed && (
                    <div className="animate-in fade-in slide-in-from-bottom-4">
                        <BlueprintButton onClick={handleConfirm} size="lg" className="px-12">
                            <span>Confirm {CATEGORY_PATHS.find(p => p.id === selectedPath)?.title}</span>
                            <ArrowRight size={16} />
                        </BlueprintButton>
                    </div>
                )}
            </div>
        </div>
    );
}
