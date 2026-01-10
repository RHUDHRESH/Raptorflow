"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import gsap from "gsap";
import { Download, Filter, RotateCcw, Eye, EyeOff, Info, Zap, Target, TrendingUp } from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   COMPETITIVE GAP ANALYSIS HEATMAP

   Blue Ocean / Red Ocean visualization showing:
   - Hot zones (crowded competitive areas)
   - Opportunity zones (gaps in the market)
   - Competitor positions
   ══════════════════════════════════════════════════════════════════════════════ */

export interface CompetitorDot {
    id: string;
    name: string;
    x: number; // 0-100
    y: number; // 0-100
    size?: number; // Market share
    type?: "direct" | "indirect" | "alternative";
}

export interface HeatmapConfig {
    xAxis: { label: string; lowLabel: string; highLabel: string };
    yAxis: { label: string; lowLabel: string; highLabel: string };
}

interface CompetitiveHeatmapProps {
    competitors: CompetitorDot[];
    yourPosition?: { x: number; y: number };
    config?: HeatmapConfig;
    onYourPositionChange?: (x: number, y: number) => void;
    className?: string;
}

// Default configuration
const DEFAULT_CONFIG: HeatmapConfig = {
    xAxis: { label: "Price", lowLabel: "Affordable", highLabel: "Premium" },
    yAxis: { label: "Features", lowLabel: "Simple", highLabel: "Comprehensive" },
};

// Calculate heat intensity at a point
function calculateHeatIntensity(x: number, y: number, competitors: CompetitorDot[]): number {
    let heat = 0;
    competitors.forEach((comp) => {
        const distance = Math.sqrt(Math.pow(x - comp.x, 2) + Math.pow(y - comp.y, 2));
        const influence = Math.max(0, 1 - distance / 30) * (comp.size || 50); // Radius of 30%
        heat += influence;
    });
    return Math.min(100, heat);
}

// Generate heatmap grid
function generateHeatGrid(competitors: CompetitorDot[], resolution: number = 20): number[][] {
    const grid: number[][] = [];
    for (let y = 0; y <= 100; y += 100 / resolution) {
        const row: number[] = [];
        for (let x = 0; x <= 100; x += 100 / resolution) {
            row.push(calculateHeatIntensity(x, y, competitors));
        }
        grid.push(row);
    }
    return grid;
}

// Heatmap Canvas Component
function HeatmapCanvas({
    competitors,
    yourPosition,
    config,
    heatGrid,
    showHeat,
    showOpportunities,
    selectedType,
    onCompetitorClick,
}: {
    competitors: CompetitorDot[];
    yourPosition?: { x: number; y: number };
    config: HeatmapConfig;
    heatGrid: number[][];
    showHeat: boolean;
    showOpportunities: boolean;
    selectedType: string | null;
    onCompetitorClick: (id: string) => void;
}) {
    const canvasRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!canvasRef.current) return;
        gsap.fromTo(canvasRef.current, { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.out" });
    }, []);

    // Find opportunity zones (low heat areas)
    const opportunities = useMemo(() => {
        const zones: { x: number; y: number; score: number }[] = [];
        const step = 100 / heatGrid.length;

        heatGrid.forEach((row, yi) => {
            row.forEach((heat, xi) => {
                if (heat < 20) { // Low competition
                    zones.push({ x: xi * step, y: yi * step, score: 100 - heat });
                }
            });
        });

        // Return top 3 opportunities
        return zones.sort((a, b) => b.score - a.score).slice(0, 3);
    }, [heatGrid]);

    const filteredCompetitors = selectedType
        ? competitors.filter(c => c.type === selectedType)
        : competitors;

    return (
        <div
            ref={canvasRef}
            className="relative w-full aspect-square rounded-2xl overflow-hidden border border-[var(--border)]"
            style={{
                background: "var(--canvas)",
            }}
        >
            {/* Heat Layer */}
            {showHeat && (
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="heatGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="var(--success)" stopOpacity="0.1" />
                            <stop offset="30%" stopColor="var(--warning)" stopOpacity="0.3" />
                            <stop offset="60%" stopColor="var(--error)" stopOpacity="0.4" />
                            <stop offset="100%" stopColor="var(--error)" stopOpacity="0.6" />
                        </linearGradient>
                    </defs>
                    {heatGrid.map((row, yi) =>
                        row.map((heat, xi) => {
                            const step = 100 / (heatGrid.length - 1);
                            const opacity = heat / 150;
                            const color = heat > 60 ? "var(--error)" : heat > 30 ? "var(--warning)" : "var(--success)";
                            return (
                                <rect
                                    key={`${xi}-${yi}`}
                                    x={xi * step - step / 2}
                                    y={yi * step - step / 2}
                                    width={step}
                                    height={step}
                                    fill={color}
                                    opacity={opacity}
                                />
                            );
                        })
                    )}
                </svg>
            )}

            {/* Grid Lines */}
            <div className="absolute inset-0 pointer-events-none" style={{
                backgroundImage: `
                    linear-gradient(to right, var(--border-subtle) 1px, transparent 1px),
                    linear-gradient(to bottom, var(--border-subtle) 1px, transparent 1px)
                `,
                backgroundSize: "20% 20%",
            }} />

            {/* Axis Lines */}
            <div className="absolute left-1/2 top-0 bottom-0 w-px bg-[var(--border)]" />
            <div className="absolute top-1/2 left-0 right-0 h-px bg-[var(--border)]" />

            {/* Opportunity Zones */}
            {showOpportunities && opportunities.map((opp, i) => (
                <div
                    key={i}
                    className="absolute flex flex-col items-center justify-center"
                    style={{
                        left: `${opp.x}%`,
                        top: `${opp.y}%`,
                        transform: "translate(-50%, -50%)",
                    }}
                >
                    <div className="w-16 h-16 rounded-full bg-[var(--success)]/20 border-2 border-dashed border-[var(--success)] flex items-center justify-center animate-pulse">
                        <Zap size={16} className="text-[var(--success)]" />
                    </div>
                    <span className="mt-1 font-technical text-[8px] text-[var(--success)]">OPPORTUNITY</span>
                </div>
            ))}

            {/* Competitor Dots */}
            {filteredCompetitors.map((comp) => {
                const size = 8 + (comp.size || 50) / 10;
                const typeColor = comp.type === "direct" ? "var(--error)" : comp.type === "indirect" ? "var(--warning)" : "var(--muted)";

                return (
                    <button
                        key={comp.id}
                        onClick={() => onCompetitorClick(comp.id)}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2 transition-all hover:scale-125 group"
                        style={{ left: `${comp.x}%`, top: `${100 - comp.y}%` }}
                    >
                        <div
                            className="rounded-full shadow-md border-2 border-[var(--paper)]"
                            style={{ width: size * 2, height: size * 2, backgroundColor: typeColor }}
                        />
                        <div className="absolute left-1/2 -translate-x-1/2 top-full mt-1 opacity-0 group-hover:opacity-100 transition-opacity bg-[var(--ink)] text-[var(--paper)] px-2 py-1 rounded text-[9px] font-technical whitespace-nowrap z-10">
                            {comp.name}
                        </div>
                    </button>
                );
            })}

            {/* Your Position */}
            {yourPosition && (
                <div
                    className="absolute transform -translate-x-1/2 -translate-y-1/2 z-20"
                    style={{ left: `${yourPosition.x}%`, top: `${100 - yourPosition.y}%` }}
                >
                    <div className="w-10 h-10 rounded-full bg-[var(--ink)] border-4 border-[var(--blueprint)] shadow-xl flex items-center justify-center">
                        <Target size={14} className="text-[var(--paper)]" />
                    </div>
                    <span className="absolute left-1/2 -translate-x-1/2 top-full mt-2 font-technical text-[9px] text-[var(--blueprint)]">YOU</span>
                </div>
            )}

            {/* Axis Labels */}
            <span className="absolute bottom-2 left-1/2 -translate-x-1/2 font-technical text-[8px] text-[var(--secondary)]">
                {config.xAxis.lowLabel} ← {config.xAxis.label} → {config.xAxis.highLabel}
            </span>
            <span className="absolute left-2 top-1/2 -translate-y-1/2 origin-center -rotate-90 font-technical text-[8px] text-[var(--secondary)]">
                {config.yAxis.lowLabel} ← {config.yAxis.label} → {config.yAxis.highLabel}
            </span>

            {/* Quadrant Labels */}
            <span className="absolute top-3 left-3 font-technical text-[8px] text-[var(--muted)]/50">NICHE LEADERS</span>
            <span className="absolute top-3 right-3 font-technical text-[8px] text-[var(--muted)]/50 text-right">PREMIUM FULL-STACK</span>
            <span className="absolute bottom-8 left-3 font-technical text-[8px] text-[var(--muted)]/50">BUDGET BASICS</span>
            <span className="absolute bottom-8 right-3 font-technical text-[8px] text-[var(--muted)]/50 text-right">PREMIUM SIMPLE</span>
        </div>
    );
}

// Main Component
export function CompetitiveHeatmap({
    competitors,
    yourPosition,
    config = DEFAULT_CONFIG,
    onYourPositionChange,
    className = "",
}: CompetitiveHeatmapProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [showHeat, setShowHeat] = useState(true);
    const [showOpportunities, setShowOpportunities] = useState(true);
    const [selectedType, setSelectedType] = useState<string | null>(null);
    const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null);

    const heatGrid = useMemo(() => generateHeatGrid(competitors), [competitors]);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    }, []);

    // Stats
    const directCount = competitors.filter(c => c.type === "direct").length;
    const indirectCount = competitors.filter(c => c.type === "indirect").length;
    const hotZones = heatGrid.flat().filter(h => h > 60).length;
    const coldZones = heatGrid.flat().filter(h => h < 20).length;

    const handleExport = () => {
        // Placeholder for export functionality
        alert("Export functionality coming soon!");
    };

    const selectedComp = competitors.find(c => c.id === selectedCompetitor);

    return (
        <div ref={containerRef} className={className}>
            {/* Header */}
            <div data-animate className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="font-serif text-2xl text-[var(--ink)]">Competitive Landscape</h2>
                    <p className="text-sm text-[var(--secondary)]">Blue Ocean / Red Ocean gap analysis</p>
                </div>
                <div className="flex items-center gap-2">
                    <SecondaryButton size="sm" onClick={handleExport}>
                        <Download size={12} />Export
                    </SecondaryButton>
                </div>
            </div>

            {/* Stats Bar */}
            <div data-animate className="grid grid-cols-4 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-[var(--canvas)] text-center">
                    <span className="text-2xl font-serif text-[var(--ink)]">{competitors.length}</span>
                    <p className="font-technical text-[8px] text-[var(--muted)]">COMPETITORS</p>
                </div>
                <div className="p-4 rounded-xl bg-[var(--error-light)] text-center">
                    <span className="text-2xl font-serif text-[var(--error)]">{hotZones}</span>
                    <p className="font-technical text-[8px] text-[var(--error)]">HOT ZONES</p>
                </div>
                <div className="p-4 rounded-xl bg-[var(--success-light)] text-center">
                    <span className="text-2xl font-serif text-[var(--success)]">{coldZones}</span>
                    <p className="font-technical text-[8px] text-[var(--success)]">OPPORTUNITIES</p>
                </div>
                <div className="p-4 rounded-xl bg-[var(--blueprint-light)] text-center">
                    <span className="text-2xl font-serif text-[var(--blueprint)]">{directCount}</span>
                    <p className="font-technical text-[8px] text-[var(--blueprint)]">DIRECT</p>
                </div>
            </div>

            {/* Controls */}
            <div data-animate className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowHeat(!showHeat)}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-technical text-[10px] transition-all ${showHeat ? "bg-[var(--ink)] text-[var(--paper)]" : "bg-[var(--canvas)] text-[var(--muted)]"
                            }`}
                    >
                        {showHeat ? <Eye size={12} /> : <EyeOff size={12} />}HEAT MAP
                    </button>
                    <button
                        onClick={() => setShowOpportunities(!showOpportunities)}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-technical text-[10px] transition-all ${showOpportunities ? "bg-[var(--success)] text-[var(--paper)]" : "bg-[var(--canvas)] text-[var(--muted)]"
                            }`}
                    >
                        <Zap size={12} />OPPORTUNITIES
                    </button>
                </div>
                <div className="flex items-center gap-2">
                    {["direct", "indirect", "alternative"].map((type) => (
                        <button
                            key={type}
                            onClick={() => setSelectedType(selectedType === type ? null : type)}
                            className={`px-3 py-1.5 rounded-lg font-technical text-[10px] transition-all ${selectedType === type ? "bg-[var(--ink)] text-[var(--paper)]" : "bg-[var(--canvas)] text-[var(--muted)]"
                                }`}
                        >
                            {type.toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Heatmap Canvas */}
            <div data-animate>
                <HeatmapCanvas
                    competitors={competitors}
                    yourPosition={yourPosition}
                    config={config}
                    heatGrid={heatGrid}
                    showHeat={showHeat}
                    showOpportunities={showOpportunities}
                    selectedType={selectedType}
                    onCompetitorClick={setSelectedCompetitor}
                />
            </div>

            {/* Legend */}
            <div data-animate className="flex items-center justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[var(--error)]" />
                    <span className="font-technical text-[9px] text-[var(--muted)]">DIRECT</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[var(--warning)]" />
                    <span className="font-technical text-[9px] text-[var(--muted)]">INDIRECT</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[var(--muted)]" />
                    <span className="font-technical text-[9px] text-[var(--muted)]">ALTERNATIVE</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-[var(--ink)] ring-2 ring-[var(--blueprint)]" />
                    <span className="font-technical text-[9px] text-[var(--muted)]">YOU</span>
                </div>
            </div>

            {/* Selected Competitor Info */}
            {selectedComp && (
                <BlueprintCard data-animate showCorners padding="md" className="mt-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${selectedComp.type === "direct" ? "bg-[var(--error-light)]" :
                                    selectedComp.type === "indirect" ? "bg-[var(--warning-light)]" : "bg-[var(--canvas)]"
                                }`}>
                                <TrendingUp size={18} className={
                                    selectedComp.type === "direct" ? "text-[var(--error)]" :
                                        selectedComp.type === "indirect" ? "text-[var(--warning)]" : "text-[var(--muted)]"
                                } />
                            </div>
                            <div>
                                <h3 className="font-serif text-lg text-[var(--ink)]">{selectedComp.name}</h3>
                                <p className="font-technical text-[9px] text-[var(--muted)]">{selectedComp.type?.toUpperCase()} COMPETITOR</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-6">
                            <div className="text-center">
                                <span className="font-serif text-xl text-[var(--ink)]">{selectedComp.x}%</span>
                                <p className="font-technical text-[8px] text-[var(--muted)]">{config.xAxis.label.toUpperCase()}</p>
                            </div>
                            <div className="text-center">
                                <span className="font-serif text-xl text-[var(--ink)]">{selectedComp.y}%</span>
                                <p className="font-technical text-[8px] text-[var(--muted)]">{config.yAxis.label.toUpperCase()}</p>
                            </div>
                            <div className="text-center">
                                <span className="font-serif text-xl text-[var(--ink)]">{selectedComp.size || 50}%</span>
                                <p className="font-technical text-[8px] text-[var(--muted)]">MARKET SHARE</p>
                            </div>
                        </div>
                    </div>
                </BlueprintCard>
            )}
        </div>
    );
}

export default CompetitiveHeatmap;
