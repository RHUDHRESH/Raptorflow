"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Map, Grid, Flame, ArrowRight, ChevronRight } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

import { PerceptualMapCanvas, type BrandBubbleData } from "@/components/positioning/PerceptualMap";
import { PositioningGrid, type PositioningGridData } from "@/components/positioning/PositioningGrid";
import { CompetitiveHeatmap, type CompetitorDot } from "@/components/positioning/CompetitiveHeatmap";

/* ══════════════════════════════════════════════════════════════════════════════
   POSITIONING EXPLORER — Step for visualizing brand positioning

   Three visualization modes:
   1. Perceptual Map — 2-axis scatter plot
   2. Four-Coordinate Grid — Market/Category/Tribe/Story
   3. Competitive Heatmap — Blue Ocean/Red Ocean
   ══════════════════════════════════════════════════════════════════════════════ */

interface PositioningData {
    activeView: "map" | "grid" | "heatmap";
    perceptualMap: {
        brands: BrandBubbleData[];
        xAxis: string;
        yAxis: string;
    };
    positioningGrid: PositioningGridData | null;
    confirmed: boolean;
}

// Mock competitor data (would come from Step 8/9 in real flow)
const MOCK_BRANDS: BrandBubbleData[] = [
    { id: "you", name: "Your Brand", x: 50, y: 60, size: 30, isYou: true },
    { id: "comp1", name: "Competitor A", x: 70, y: 80, size: 60 },
    { id: "comp2", name: "Competitor B", x: 30, y: 40, size: 45 },
    { id: "comp3", name: "Competitor C", x: 80, y: 30, size: 55 },
    { id: "comp4", name: "Budget Option", x: 20, y: 20, size: 25 },
    { id: "comp5", name: "Enterprise", x: 85, y: 90, size: 70 },
];

const MOCK_COMPETITORS: CompetitorDot[] = [
    { id: "c1", name: "Competitor A", x: 70, y: 80, size: 60, type: "direct" },
    { id: "c2", name: "Competitor B", x: 30, y: 40, size: 45, type: "direct" },
    { id: "c3", name: "Competitor C", x: 80, y: 30, size: 55, type: "indirect" },
    { id: "c4", name: "Budget Option", x: 20, y: 20, size: 25, type: "alternative" },
    { id: "c5", name: "Enterprise", x: 85, y: 90, size: 70, type: "direct" },
    { id: "c6", name: "New Player", x: 45, y: 55, size: 20, type: "indirect" },
    { id: "c7", name: "Legacy Tool", x: 60, y: 25, size: 40, type: "alternative" },
];

const VIEW_OPTIONS = [
    { id: "map", label: "Perceptual Map", icon: Map, description: "2-axis scatter plot positioning" },
    { id: "grid", label: "Positioning Grid", icon: Grid, description: "Market / Category / Tribe / Story" },
    { id: "heatmap", label: "Competitive Heatmap", icon: Flame, description: "Blue Ocean / Red Ocean analysis" },
] as const;

export default function StepPositioningExplorer() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(12)?.data as PositioningData | undefined;

    const [activeView, setActiveView] = useState<"map" | "grid" | "heatmap">(stepData?.activeView || "map");
    const [brands, setBrands] = useState<BrandBubbleData[]>(stepData?.perceptualMap?.brands || MOCK_BRANDS);
    const [xAxis, setXAxis] = useState(stepData?.perceptualMap?.xAxis || "price");
    const [yAxis, setYAxis] = useState(stepData?.perceptualMap?.yAxis || "features");
    const [gridData, setGridData] = useState<PositioningGridData | null>(stepData?.positioningGrid || null);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    }, []);

    // Save data on changes
    useEffect(() => {
        const data = {
            activeView,
            perceptualMap: { brands, xAxis, yAxis },
            positioningGrid: gridData,
            confirmed,
        };
        updateStepData(12, data as Record<string, unknown>);
    }, [activeView, brands, xAxis, yAxis, gridData, confirmed, updateStepData]);

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepStatus(12, "complete");
    };

    const yourPosition = brands.find(b => b.isYou);

    return (
        <div ref={containerRef} className="space-y-8">
            {/* Header */}
            <div data-animate className="text-center">
                <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">Positioning Explorer</h2>
                <p className="text-[var(--secondary)]">Visualize where you stand in the competitive landscape</p>
            </div>

            {/* View Selector */}
            <div data-animate className="flex gap-3 justify-center">
                {VIEW_OPTIONS.map((view) => {
                    const Icon = view.icon;
                    const isActive = activeView === view.id;
                    return (
                        <button
                            key={view.id}
                            onClick={() => setActiveView(view.id)}
                            className={`
                                flex items-center gap-3 px-5 py-3 rounded-xl transition-all
                                ${isActive
                                    ? "bg-[var(--ink)] text-[var(--paper)] shadow-lg"
                                    : "bg-[var(--canvas)] text-[var(--ink)] hover:bg-[var(--canvas)]/80"}
                            `}
                        >
                            <Icon size={18} />
                            <div className="text-left">
                                <span className="font-medium block">{view.label}</span>
                                <span className={`text-[10px] ${isActive ? "opacity-70" : "text-[var(--muted)]"}`}>{view.description}</span>
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* Active View */}
            <div data-animate>
                {activeView === "map" && (
                    <BlueprintCard figure="FIG. 01" title="Perceptual Map" code="PMAP" showCorners padding="lg">
                        <p className="text-sm text-[var(--secondary)] mb-6">
                            Drag your brand and competitors to visualize positioning. Change axes to explore different dimensions.
                        </p>
                        <PerceptualMapCanvas
                            brands={brands}
                            onBrandsChange={setBrands}
                            xAxis={xAxis}
                            yAxis={yAxis}
                            onXAxisChange={setXAxis}
                            onYAxisChange={setYAxis}
                        />
                    </BlueprintCard>
                )}

                {activeView === "grid" && (
                    <BlueprintCard figure="FIG. 02" title="Four-Coordinate Grid" code="GRID" showCorners padding="lg">
                        <p className="text-sm text-[var(--secondary)] mb-6">
                            Define your positioning across four dimensions: who you serve, what you are, your community, and your narrative.
                        </p>
                        <PositioningGrid
                            data={gridData || undefined}
                            onChange={setGridData}
                        />
                    </BlueprintCard>
                )}

                {activeView === "heatmap" && (
                    <BlueprintCard figure="FIG. 03" title="Competitive Heatmap" code="HEAT" showCorners padding="lg">
                        <p className="text-sm text-[var(--secondary)] mb-6">
                            Identify market gaps and crowded zones. Opportunity zones highlight where competition is low.
                        </p>
                        <CompetitiveHeatmap
                            competitors={MOCK_COMPETITORS}
                            yourPosition={yourPosition ? { x: yourPosition.x, y: yourPosition.y } : undefined}
                        />
                    </BlueprintCard>
                )}
            </div>

            {/* Progress Indicator */}
            <div data-animate className="flex items-center justify-center gap-4">
                {VIEW_OPTIONS.map((view, i) => (
                    <div key={view.id} className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${activeView === view.id ? "bg-[var(--ink)] text-[var(--paper)]" : "bg-[var(--canvas)] text-[var(--muted)]"}`}>
                            {i + 1}
                        </div>
                        {i < VIEW_OPTIONS.length - 1 && <ChevronRight size={16} className="text-[var(--muted)]" />}
                    </div>
                ))}
            </div>

            {/* Confirm */}
            {!confirmed && (
                <div data-animate className="flex justify-center">
                    <BlueprintButton size="lg" onClick={handleConfirm}>
                        <Check size={14} />Confirm Positioning
                    </BlueprintButton>
                </div>
            )}

            {confirmed && (
                <BlueprintCard data-animate showCorners padding="lg" className="border-[var(--success)] bg-[var(--success-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-xl bg-[var(--success)] flex items-center justify-center">
                            <Check size={24} className="text-[var(--paper)]" />
                        </div>
                        <div>
                            <span className="font-serif text-lg text-[var(--ink)]">Positioning Confirmed</span>
                            <p className="font-technical text-[10px] text-[var(--secondary)]">Your competitive position has been locked</p>
                        </div>
                        <BlueprintBadge variant="success" dot className="ml-auto">COMPLETE</BlueprintBadge>
                    </div>
                </BlueprintCard>
            )}

            {/* Footer */}
            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">POSITIONING-EXPLORER • STEP 12/25</span>
            </div>
        </div>
    );
}
