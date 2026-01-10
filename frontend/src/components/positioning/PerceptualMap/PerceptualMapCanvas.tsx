"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { X, ZoomIn, ZoomOut, RotateCcw, Download } from "lucide-react";
import { DraggableItem } from "../shared/DraggableItem";
import { AxisDropdown, DEFAULT_AXIS_OPTIONS } from "../shared/AxisDropdown";
import { PositioningTooltip, usePositioningTooltip } from "../shared/PositioningTooltip";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PERCEPTUAL MAP CANVAS — Interactive 2-axis positioning scatter plot

   Features:
   - Draggable brand bubbles
   - Axis customization
   - Dynamic quadrant labels
   - Comparison mode
   - Tooltips
   ══════════════════════════════════════════════════════════════════════════════ */

export interface BrandBubbleData {
    id: string;
    name: string;
    logo?: string;
    x: number; // 0-100
    y: number; // 0-100
    size?: number; // Market share / revenue indicator
    isYou?: boolean;
    color?: string;
}

interface PerceptualMapCanvasProps {
    brands: BrandBubbleData[];
    onBrandsChange: (brands: BrandBubbleData[]) => void;
    xAxis?: string;
    yAxis?: string;
    onXAxisChange?: (axis: string) => void;
    onYAxisChange?: (axis: string) => void;
    className?: string;
}

// Quadrant label generator based on axis selection
function getQuadrantLabels(xAxis: string, yAxis: string) {
    const xOption = DEFAULT_AXIS_OPTIONS.find(o => o.id === xAxis);
    const yOption = DEFAULT_AXIS_OPTIONS.find(o => o.id === yAxis);

    if (!xOption || !yOption) return { tl: "", tr: "", bl: "", br: "" };

    return {
        tl: `${yOption.highLabel} ${xOption.lowLabel}`,  // Top Left
        tr: `${yOption.highLabel} ${xOption.highLabel}`, // Top Right
        bl: `${yOption.lowLabel} ${xOption.lowLabel}`,   // Bottom Left
        br: `${yOption.lowLabel} ${xOption.highLabel}`,  // Bottom Right
    };
}

// Brand Bubble Component
function BrandBubble({
    brand,
    isSelected,
    isComparing,
    onPositionChange,
    onClick,
    onHover,
    onLeave,
}: {
    brand: BrandBubbleData;
    isSelected: boolean;
    isComparing: boolean;
    onPositionChange: (id: string, x: number, y: number) => void;
    onClick: () => void;
    onHover: (e: React.MouseEvent) => void;
    onLeave: () => void;
}) {
    const size = brand.size || 50;
    const baseSize = 40 + (size / 100) * 30; // 40-70px based on size

    return (
        <DraggableItem
            id={brand.id}
            initialX={brand.x}
            initialY={brand.y}
            onPositionChange={onPositionChange}
            onClick={onClick}
        >
            <div
                onMouseEnter={onHover}
                onMouseLeave={onLeave}
                style={{ width: baseSize, height: baseSize }}
                className={`
                    rounded-full flex items-center justify-center text-center
                    transition-all duration-200 shadow-md
                    ${brand.isYou
                        ? "bg-[var(--ink)] text-[var(--paper)] ring-4 ring-[var(--blueprint)] ring-offset-2"
                        : "bg-[var(--paper)] border-2 border-[var(--border)] text-[var(--ink)]"}
                    ${isSelected ? "ring-4 ring-[var(--blueprint)]" : ""}
                    ${isComparing ? "ring-4 ring-[var(--warning)]" : ""}
                `}
            >
                {brand.logo ? (
                    <img src={brand.logo} alt={brand.name} className="w-3/4 h-3/4 object-contain rounded-full" />
                ) : (
                    <span className="font-technical text-[8px] leading-tight px-1">
                        {brand.name.split(" ").map(w => w[0]).join("").slice(0, 3)}
                    </span>
                )}
            </div>
        </DraggableItem>
    );
}

// Comparison Panel Component
function ComparisonPanel({
    brand1,
    brand2,
    xAxis,
    yAxis,
    onClose,
}: {
    brand1: BrandBubbleData;
    brand2: BrandBubbleData;
    xAxis: string;
    yAxis: string;
    onClose: () => void;
}) {
    const xOption = DEFAULT_AXIS_OPTIONS.find(o => o.id === xAxis);
    const yOption = DEFAULT_AXIS_OPTIONS.find(o => o.id === yAxis);

    return (
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-[var(--paper)] border-l border-[var(--border)] shadow-xl z-50 overflow-y-auto">
            <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="font-serif text-lg text-[var(--ink)]">Compare</h3>
                    <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-[var(--canvas)] text-[var(--muted)]">
                        <X size={16} />
                    </button>
                </div>

                {/* Brand Headers */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                    {[brand1, brand2].map((brand, i) => (
                        <div key={brand.id} className={`p-4 rounded-xl text-center ${brand.isYou ? "bg-[var(--ink)] text-[var(--paper)]" : "bg-[var(--canvas)]"}`}>
                            <div className={`w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center ${brand.isYou ? "bg-[var(--paper)]/20" : "bg-[var(--paper)] border border-[var(--border)]"}`}>
                                <span className="font-technical text-[10px]">{brand.name.slice(0, 2).toUpperCase()}</span>
                            </div>
                            <span className="font-serif text-sm">{brand.name}</span>
                        </div>
                    ))}
                </div>

                {/* Comparison Stats */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--canvas)]">
                        <span className="text-sm text-[var(--secondary)]">{xOption?.label || "X Axis"}</span>
                        <div className="flex items-center gap-4">
                            <span className="font-technical text-sm text-[var(--ink)]">{brand1.x.toFixed(0)}%</span>
                            <span className="text-[var(--muted)]">vs</span>
                            <span className="font-technical text-sm text-[var(--ink)]">{brand2.x.toFixed(0)}%</span>
                        </div>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--canvas)]">
                        <span className="text-sm text-[var(--secondary)]">{yOption?.label || "Y Axis"}</span>
                        <div className="flex items-center gap-4">
                            <span className="font-technical text-sm text-[var(--ink)]">{brand1.y.toFixed(0)}%</span>
                            <span className="text-[var(--muted)]">vs</span>
                            <span className="font-technical text-sm text-[var(--ink)]">{brand2.y.toFixed(0)}%</span>
                        </div>
                    </div>
                    {brand1.size && brand2.size && (
                        <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--canvas)]">
                            <span className="text-sm text-[var(--secondary)]">Market Size</span>
                            <div className="flex items-center gap-4">
                                <span className="font-technical text-sm text-[var(--ink)]">{brand1.size}%</span>
                                <span className="text-[var(--muted)]">vs</span>
                                <span className="font-technical text-sm text-[var(--ink)]">{brand2.size}%</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Distance */}
                <div className="mt-6 p-4 rounded-xl bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30">
                    <span className="font-technical text-[9px] text-[var(--blueprint)] block mb-1">POSITIONING DISTANCE</span>
                    <span className="font-serif text-2xl text-[var(--blueprint)]">
                        {Math.round(Math.sqrt(Math.pow(brand1.x - brand2.x, 2) + Math.pow(brand1.y - brand2.y, 2)))}
                    </span>
                    <span className="text-sm text-[var(--blueprint)]"> points apart</span>
                </div>
            </div>
        </div>
    );
}

export function PerceptualMapCanvas({
    brands,
    onBrandsChange,
    xAxis = "price",
    yAxis = "features",
    onXAxisChange,
    onYAxisChange,
    className = "",
}: PerceptualMapCanvasProps) {
    const canvasRef = useRef<HTMLDivElement>(null);
    const [selectedBrand, setSelectedBrand] = useState<string | null>(null);
    const [comparingBrand, setComparingBrand] = useState<string | null>(null);
    const { tooltip, showTooltip, hideTooltip } = usePositioningTooltip();

    const quadrantLabels = getQuadrantLabels(xAxis, yAxis);
    const xOption = DEFAULT_AXIS_OPTIONS.find(o => o.id === xAxis);
    const yOption = DEFAULT_AXIS_OPTIONS.find(o => o.id === yAxis);

    useEffect(() => {
        if (!canvasRef.current) return;
        gsap.fromTo(canvasRef.current, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.out" });
    }, []);

    const handlePositionChange = (id: string, x: number, y: number) => {
        const updated = brands.map(b => b.id === id ? { ...b, x, y } : b);
        onBrandsChange(updated);
    };

    const handleBubbleClick = (id: string) => {
        if (selectedBrand && selectedBrand !== id) {
            // Second selection → compare mode
            setComparingBrand(id);
        } else if (selectedBrand === id) {
            // Deselect
            setSelectedBrand(null);
            setComparingBrand(null);
        } else {
            // First selection
            setSelectedBrand(id);
            setComparingBrand(null);
        }
    };

    const handleReset = () => {
        // Reset all positions to center
        const reset = brands.map(b => ({ ...b, x: 50, y: 50 }));
        onBrandsChange(reset);
    };

    const brand1 = brands.find(b => b.id === selectedBrand);
    const brand2 = brands.find(b => b.id === comparingBrand);

    return (
        <div className={`relative ${className}`}>
            {/* Axis Selectors */}
            <div className="flex items-center justify-between mb-4">
                <AxisDropdown
                    options={DEFAULT_AXIS_OPTIONS}
                    selected={xAxis}
                    onSelect={onXAxisChange || (() => { })}
                    position="x"
                />
                <div className="flex items-center gap-2">
                    <SecondaryButton size="sm" onClick={handleReset}>
                        <RotateCcw size={12} />Reset
                    </SecondaryButton>
                </div>
            </div>

            {/* Main Canvas */}
            <div className="flex">
                {/* Y Axis Label */}
                <div className="flex flex-col items-center justify-center w-8 mr-2">
                    <AxisDropdown
                        options={DEFAULT_AXIS_OPTIONS}
                        selected={yAxis}
                        onSelect={onYAxisChange || (() => { })}
                        position="y"
                    />
                </div>

                {/* Canvas Area */}
                <div
                    ref={canvasRef}
                    className="relative flex-1 aspect-square bg-[var(--canvas)] rounded-2xl border border-[var(--border)] overflow-hidden"
                    style={{
                        backgroundImage: `
                            linear-gradient(to right, var(--border-subtle) 1px, transparent 1px),
                            linear-gradient(to bottom, var(--border-subtle) 1px, transparent 1px)
                        `,
                        backgroundSize: "10% 10%",
                    }}
                >
                    {/* Axis Lines */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-[var(--border)]" />
                    <div className="absolute top-1/2 left-0 right-0 h-px bg-[var(--border)]" />

                    {/* Quadrant Labels */}
                    <span className="absolute top-4 left-4 font-technical text-[9px] text-[var(--muted)] opacity-60">{quadrantLabels.tl}</span>
                    <span className="absolute top-4 right-4 font-technical text-[9px] text-[var(--muted)] opacity-60 text-right">{quadrantLabels.tr}</span>
                    <span className="absolute bottom-4 left-4 font-technical text-[9px] text-[var(--muted)] opacity-60">{quadrantLabels.bl}</span>
                    <span className="absolute bottom-4 right-4 font-technical text-[9px] text-[var(--muted)] opacity-60 text-right">{quadrantLabels.br}</span>

                    {/* Axis Labels */}
                    <span className="absolute bottom-2 left-1/2 -translate-x-1/2 font-technical text-[8px] text-[var(--secondary)]">
                        {xOption?.lowLabel} ← {xOption?.label} → {xOption?.highLabel}
                    </span>
                    <span className="absolute left-2 top-1/2 -translate-y-1/2 origin-center -rotate-90 font-technical text-[8px] text-[var(--secondary)]">
                        {yOption?.lowLabel} ← {yOption?.label} → {yOption?.highLabel}
                    </span>

                    {/* Brand Bubbles */}
                    {brands.map(brand => (
                        <BrandBubble
                            key={brand.id}
                            brand={brand}
                            isSelected={selectedBrand === brand.id}
                            isComparing={comparingBrand === brand.id}
                            onPositionChange={handlePositionChange}
                            onClick={() => handleBubbleClick(brand.id)}
                            onHover={(e) => showTooltip({
                                name: brand.name,
                                x: brand.x,
                                y: 100 - brand.y, // Invert Y for display
                                xLabel: xOption?.label,
                                yLabel: yOption?.label,
                                details: brand.size ? [{ label: "Market Share", value: `${brand.size}%` }] : undefined,
                            }, e)}
                            onLeave={hideTooltip}
                        />
                    ))}
                </div>
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[var(--ink)] ring-2 ring-[var(--blueprint)] ring-offset-1" />
                    <span className="font-technical text-[9px] text-[var(--muted)]">YOUR BRAND</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[var(--paper)] border-2 border-[var(--border)]" />
                    <span className="font-technical text-[9px] text-[var(--muted)]">COMPETITOR</span>
                </div>
                <span className="font-technical text-[9px] text-[var(--secondary)]">Click two brands to compare</span>
            </div>

            {/* Comparison Panel */}
            {brand1 && brand2 && (
                <ComparisonPanel
                    brand1={brand1}
                    brand2={brand2}
                    xAxis={xAxis}
                    yAxis={yAxis}
                    onClose={() => { setSelectedBrand(null); setComparingBrand(null); }}
                />
            )}

            {/* Tooltip */}
            <PositioningTooltip data={tooltip.data} position={tooltip.position} />
        </div>
    );
}

export default PerceptualMapCanvas;
