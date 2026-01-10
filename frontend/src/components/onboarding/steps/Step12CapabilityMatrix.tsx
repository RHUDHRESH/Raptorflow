"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Check, ChevronDown, Eye, EyeOff, Lock, Sparkles, Target,
    TrendingUp, Users, Layers, Star, Zap, Crown, Crosshair,
    Award, Diamond, Hexagon, Circle
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   STEP 12: COMPETITIVE POSITIONING

   RaptorFlow Quiet Luxury — "Calm, Expensive, Decisive"
   Premium editorial design with subtle animations
   ══════════════════════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

interface Brand {
    id: string;
    name: string;
    x: number;
    y: number;
    size: number;
    isYou?: boolean;
}

interface GridChoice {
    id: string;
    label: string;
    selected: boolean;
}

interface GridQuadrant {
    id: string;
    title: string;
    question: string;
    choices: GridChoice[];
}

type ViewMode = "map" | "grid" | "gaps";

// ═══════════════════════════════════════════════════════════════════════════════
// PERCEPTUAL MAP — Premium 2D Canvas
// ═══════════════════════════════════════════════════════════════════════════════

const AXES = [
    { id: "price", label: "Price", low: "Value", high: "Premium" },
    { id: "features", label: "Depth", low: "Focused", high: "Comprehensive" },
    { id: "speed", label: "Speed", low: "Methodical", high: "Rapid" },
    { id: "experience", label: "Experience", low: "Utilitarian", high: "Delightful" },
];

function PerceptualMap({
    brands,
    setBrands,
    xAxis,
    yAxis,
    setXAxis,
    setYAxis
}: {
    brands: Brand[];
    setBrands: (b: Brand[]) => void;
    xAxis: string;
    yAxis: string;
    setXAxis: (a: string) => void;
    setYAxis: (a: string) => void;
}) {
    const canvasRef = useRef<HTMLDivElement>(null);
    const [dragging, setDragging] = useState<string | null>(null);
    const [hovered, setHovered] = useState<string | null>(null);
    const [axisDropdown, setAxisDropdown] = useState<"x" | "y" | null>(null);

    const xOpt = AXES.find(a => a.id === xAxis) || AXES[0];
    const yOpt = AXES.find(a => a.id === yAxis) || AXES[1];

    const handleMouseDown = (id: string, e: React.MouseEvent) => {
        e.preventDefault();
        setDragging(id);
    };

    const handleMouseMove = useCallback((e: MouseEvent) => {
        if (!dragging || !canvasRef.current) return;
        const rect = canvasRef.current.getBoundingClientRect();
        const x = Math.max(5, Math.min(95, ((e.clientX - rect.left) / rect.width) * 100));
        const y = Math.max(5, Math.min(95, 100 - ((e.clientY - rect.top) / rect.height) * 100));
        setBrands(brands.map(b => b.id === dragging ? { ...b, x, y } : b));
    }, [dragging, brands, setBrands]);

    const handleMouseUp = useCallback(() => setDragging(null), []);

    useEffect(() => {
        if (dragging) {
            window.addEventListener("mousemove", handleMouseMove);
            window.addEventListener("mouseup", handleMouseUp);
            return () => {
                window.removeEventListener("mousemove", handleMouseMove);
                window.removeEventListener("mouseup", handleMouseUp);
            };
        }
    }, [dragging, handleMouseMove, handleMouseUp]);

    const yourBrand = brands.find(b => b.isYou);

    return (
        <div className="space-y-8">
            {/* Canvas Header */}
            <div className="flex items-end justify-between">
                <div>
                    <span className="font-technical text-[10px] text-[var(--ink-muted)] tracking-widest">FIG. 01</span>
                    <h3 className="font-serif text-3xl text-[var(--ink)] mt-1">Perceptual Map</h3>
                    <p className="text-[var(--secondary)] text-sm mt-2 max-w-md">
                        Drag to position. Your brand is marked with a crown.
                    </p>
                </div>

                {/* Coordinates Display */}
                {yourBrand && (
                    <div className="flex items-center gap-8 border-l border-[var(--structure)] pl-8">
                        <div>
                            <span className="font-technical text-[9px] text-[var(--ink-muted)] tracking-widest block">X POSITION</span>
                            <span className="font-serif text-4xl text-[var(--ink)]">{yourBrand.x.toFixed(0)}</span>
                        </div>
                        <div>
                            <span className="font-technical text-[9px] text-[var(--ink-muted)] tracking-widest block">Y POSITION</span>
                            <span className="font-serif text-4xl text-[var(--ink)]">{yourBrand.y.toFixed(0)}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Axis Selectors */}
            <div className="flex items-center justify-between">
                <div className="relative">
                    <button
                        onClick={() => setAxisDropdown(axisDropdown === "x" ? null : "x")}
                        className="flex items-center gap-3 text-left group"
                    >
                        <span className="font-technical text-[9px] text-[var(--ink-muted)] tracking-widest">X-AXIS</span>
                        <span className="font-serif text-lg text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">{xOpt.label}</span>
                        <ChevronDown size={14} className="text-[var(--ink-muted)]" />
                    </button>
                    {axisDropdown === "x" && (
                        <div className="absolute top-full left-0 mt-2 w-56 bg-[var(--canvas)] border border-[var(--structure)] rounded-lg shadow-2xl z-30 overflow-hidden">
                            {AXES.filter(a => a.id !== yAxis).map(a => (
                                <button
                                    key={a.id}
                                    onClick={() => { setXAxis(a.id); setAxisDropdown(null); }}
                                    className={`w-full px-4 py-3 text-left text-sm transition-colors ${xAxis === a.id ? "bg-[var(--ink)] text-[var(--canvas)]" : "hover:bg-[var(--surface)] text-[var(--ink)]"}`}
                                >
                                    {a.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                <span className="font-technical text-[9px] text-[var(--ink-muted)] tracking-widest">DRAG TO REPOSITION</span>

                <div className="relative">
                    <button
                        onClick={() => setAxisDropdown(axisDropdown === "y" ? null : "y")}
                        className="flex items-center gap-3 text-right group"
                    >
                        <span className="font-technical text-[9px] text-[var(--ink-muted)] tracking-widest">Y-AXIS</span>
                        <span className="font-serif text-lg text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">{yOpt.label}</span>
                        <ChevronDown size={14} className="text-[var(--ink-muted)]" />
                    </button>
                    {axisDropdown === "y" && (
                        <div className="absolute top-full right-0 mt-2 w-56 bg-[var(--canvas)] border border-[var(--structure)] rounded-lg shadow-2xl z-30 overflow-hidden">
                            {AXES.filter(a => a.id !== xAxis).map(a => (
                                <button
                                    key={a.id}
                                    onClick={() => { setYAxis(a.id); setAxisDropdown(null); }}
                                    className={`w-full px-4 py-3 text-left text-sm transition-colors ${yAxis === a.id ? "bg-[var(--ink)] text-[var(--canvas)]" : "hover:bg-[var(--surface)] text-[var(--ink)]"}`}
                                >
                                    {a.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* The Canvas */}
            <div
                ref={canvasRef}
                className="relative aspect-[4/3] rounded-xl border border-[var(--structure)] overflow-hidden"
                style={{ background: "var(--canvas)" }}
            >
                {/* Subtle grid */}
                <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                    <defs>
                        <pattern id="grid" width="10%" height="10%" patternUnits="userSpaceOnUse">
                            <path d="M 100 0 L 0 0 0 100" fill="none" stroke="var(--structure-subtle)" strokeWidth="0.5" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    <line x1="50%" y1="0" x2="50%" y2="100%" stroke="var(--structure)" strokeWidth="1" />
                    <line x1="0" y1="50%" x2="100%" y2="50%" stroke="var(--structure)" strokeWidth="1" />
                </svg>

                {/* Axis endpoints */}
                <div className="absolute bottom-4 left-4 font-technical text-[10px] text-[var(--ink-muted)]">{xOpt.low}</div>
                <div className="absolute bottom-4 right-4 font-technical text-[10px] text-[var(--ink-muted)]">{xOpt.high}</div>
                <div className="absolute top-4 left-4 font-technical text-[10px] text-[var(--ink-muted)]">{yOpt.high}</div>
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 font-technical text-[10px] text-[var(--ink-muted)]">{xOpt.label}</div>

                {/* Brand bubbles */}
                {brands.map(brand => {
                    const size = 32 + (brand.size / 100) * 32;
                    const isHovered = hovered === brand.id;
                    const isDragging = dragging === brand.id;

                    return (
                        <div
                            key={brand.id}
                            onMouseDown={(e) => handleMouseDown(brand.id, e)}
                            onMouseEnter={() => setHovered(brand.id)}
                            onMouseLeave={() => setHovered(null)}
                            className="absolute cursor-grab active:cursor-grabbing transition-transform duration-100"
                            style={{
                                left: `${brand.x}%`,
                                bottom: `${brand.y}%`,
                                transform: `translate(-50%, 50%) scale(${isDragging ? 1.15 : isHovered ? 1.08 : 1})`,
                                zIndex: isDragging ? 50 : brand.isYou ? 40 : 10,
                            }}
                        >
                            {/* Your brand glow */}
                            {brand.isYou && (
                                <div
                                    className="absolute inset-0 rounded-full opacity-30"
                                    style={{
                                        width: size + 16,
                                        height: size + 16,
                                        left: -8,
                                        top: -8,
                                        background: "var(--accent)",
                                        filter: "blur(12px)",
                                    }}
                                />
                            )}

                            {/* Bubble */}
                            <div
                                className={`
                                    rounded-full flex items-center justify-center transition-shadow duration-200
                                    ${brand.isYou
                                        ? "bg-[var(--ink)] shadow-2xl"
                                        : "bg-[var(--surface)] border border-[var(--structure)]"}
                                    ${isDragging ? "shadow-2xl" : ""}
                                `}
                                style={{ width: size, height: size }}
                            >
                                {brand.isYou ? (
                                    <Crown size={size * 0.45} className="text-[var(--accent)]" />
                                ) : (
                                    <span className="font-technical text-[9px] text-[var(--ink-muted)]">
                                        {brand.name.split(" ").map(w => w[0]).join("")}
                                    </span>
                                )}
                            </div>

                            {/* Label on hover */}
                            {isHovered && (
                                <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-3 pointer-events-none">
                                    <div className="px-3 py-2 rounded-lg bg-[var(--ink)] text-[var(--canvas)] whitespace-nowrap shadow-xl">
                                        <span className="font-medium text-sm">{brand.name}</span>
                                    </div>
                                    <div className="w-2 h-2 bg-[var(--ink)] rotate-45 absolute left-1/2 -translate-x-1/2 -bottom-1" />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-12 pt-2">
                <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-[var(--ink)] flex items-center justify-center">
                        <Crown size={12} className="text-[var(--accent)]" />
                    </div>
                    <span className="font-technical text-[10px] text-[var(--ink-muted)] tracking-wide">YOUR BRAND</span>
                </div>
                <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-[var(--surface)] border border-[var(--structure)]" />
                    <span className="font-technical text-[10px] text-[var(--ink-muted)] tracking-wide">COMPETITOR</span>
                </div>
            </div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// POSITIONING GRID — Editorial 4-Coordinate System
// ═══════════════════════════════════════════════════════════════════════════════

function PositioningGrid({
    quadrants,
    setQuadrants,
}: {
    quadrants: GridQuadrant[];
    setQuadrants: (q: GridQuadrant[]) => void;
}) {
    const [expanded, setExpanded] = useState<string | null>(null);
    const [customInput, setCustomInput] = useState("");

    const toggleChoice = (qId: string, cId: string) => {
        setQuadrants(quadrants.map(q =>
            q.id === qId
                ? { ...q, choices: q.choices.map(c => c.id === cId ? { ...c, selected: !c.selected } : c) }
                : q
        ));
    };

    const addCustom = (qId: string) => {
        if (!customInput.trim()) return;
        setQuadrants(quadrants.map(q =>
            q.id === qId
                ? { ...q, choices: [...q.choices, { id: `custom-${Date.now()}`, label: customInput.trim(), selected: true }] }
                : q
        ));
        setCustomInput("");
    };

    const completion = quadrants.filter(q => q.choices.some(c => c.selected)).length;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-end justify-between">
                <div>
                    <span className="font-technical text-[10px] text-[var(--ink-muted)] tracking-widest">FIG. 02</span>
                    <h3 className="font-serif text-3xl text-[var(--ink)] mt-1">Position Grid</h3>
                    <p className="text-[var(--secondary)] text-sm mt-2 max-w-md">
                        Define your four coordinates. Click to expand each dimension.
                    </p>
                </div>

                {/* Completion */}
                <div className="flex items-center gap-4 border-l border-[var(--structure)] pl-8">
                    <div className="flex gap-2">
                        {[0, 1, 2, 3].map(i => (
                            <div
                                key={i}
                                className={`w-3 h-3 rounded-full transition-colors duration-300 ${i < completion ? "bg-[var(--success)]" : "bg-[var(--structure)]"}`}
                            />
                        ))}
                    </div>
                    <span className="font-technical text-[10px] text-[var(--ink-muted)] tracking-widest">{completion}/4</span>
                </div>
            </div>

            {/* The Grid */}
            <div className="grid grid-cols-2 gap-6">
                {quadrants.map((q, i) => {
                    const selected = q.choices.filter(c => c.selected);
                    const isComplete = selected.length > 0;
                    const icons = [Users, Layers, Award, Star];
                    const Icon = icons[i];

                    return (
                        <button
                            key={q.id}
                            onClick={() => setExpanded(q.id)}
                            className={`
                                relative text-left p-8 rounded-xl border transition-all duration-300 group
                                ${isComplete
                                    ? "border-[var(--success)]/40 bg-[var(--success)]/5"
                                    : "border-[var(--structure)] bg-[var(--canvas)] hover:border-[var(--ink)]/20"}
                            `}
                        >
                            {/* Complete indicator */}
                            {isComplete && (
                                <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[var(--success)] flex items-center justify-center shadow-md">
                                    <Check size={12} className="text-white" />
                                </div>
                            )}

                            <div className="flex items-start gap-4">
                                <div className="w-12 h-12 rounded-xl bg-[var(--surface)] flex items-center justify-center">
                                    <Icon size={20} className="text-[var(--ink)]" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-serif text-xl text-[var(--ink)]">{q.title}</h4>
                                    <p className="text-sm text-[var(--secondary)] mt-1">{q.question}</p>

                                    {selected.length > 0 ? (
                                        <div className="flex flex-wrap gap-2 mt-4">
                                            {selected.slice(0, 2).map(c => (
                                                <span key={c.id} className="px-3 py-1 rounded-full bg-[var(--ink)] text-[var(--canvas)] text-xs font-medium">
                                                    {c.label}
                                                </span>
                                            ))}
                                            {selected.length > 2 && (
                                                <span className="px-3 py-1 rounded-full bg-[var(--surface)] text-[var(--ink-muted)] text-xs">
                                                    +{selected.length - 2}
                                                </span>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="mt-4 text-sm text-[var(--ink-muted)] group-hover:text-[var(--ink)] transition-colors">
                                            Click to define →
                                        </div>
                                    )}
                                </div>
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* Expanded Modal */}
            {expanded && (
                <div
                    className="fixed inset-0 bg-[var(--ink)]/20 backdrop-blur-sm z-50 flex items-center justify-center p-8"
                    onClick={() => setExpanded(null)}
                >
                    <div
                        className="w-full max-w-lg bg-[var(--canvas)] rounded-2xl shadow-2xl overflow-hidden"
                        onClick={e => e.stopPropagation()}
                    >
                        {(() => {
                            const q = quadrants.find(q => q.id === expanded);
                            if (!q) return null;
                            const icons = [Users, Layers, Award, Star];
                            const Icon = icons[quadrants.findIndex(x => x.id === q.id)];

                            return (
                                <>
                                    <div className="p-8 border-b border-[var(--structure)]">
                                        <div className="flex items-center gap-4">
                                            <div className="w-14 h-14 rounded-xl bg-[var(--surface)] flex items-center justify-center">
                                                <Icon size={24} className="text-[var(--ink)]" />
                                            </div>
                                            <div>
                                                <h3 className="font-serif text-2xl text-[var(--ink)]">{q.title}</h3>
                                                <p className="text-sm text-[var(--secondary)]">{q.question}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="p-8 space-y-3 max-h-80 overflow-y-auto">
                                        {q.choices.map(c => (
                                            <button
                                                key={c.id}
                                                onClick={() => toggleChoice(q.id, c.id)}
                                                className={`
                                                    w-full flex items-center justify-between p-4 rounded-xl text-left transition-all
                                                    ${c.selected
                                                        ? "bg-[var(--ink)] text-[var(--canvas)]"
                                                        : "bg-[var(--surface)] text-[var(--ink)] hover:bg-[var(--surface-hover)]"}
                                                `}
                                            >
                                                <span>{c.label}</span>
                                                {c.selected && <Check size={16} />}
                                            </button>
                                        ))}
                                    </div>

                                    <div className="p-8 border-t border-[var(--structure)] flex gap-3">
                                        <input
                                            type="text"
                                            value={customInput}
                                            onChange={e => setCustomInput(e.target.value)}
                                            onKeyDown={e => e.key === "Enter" && addCustom(q.id)}
                                            placeholder="Add custom..."
                                            className="flex-1 px-4 py-3 rounded-xl bg-[var(--surface)] border border-[var(--structure)] text-sm focus:outline-none focus:border-[var(--ink)]"
                                        />
                                        <BlueprintButton onClick={() => addCustom(q.id)}>Add</BlueprintButton>
                                    </div>
                                </>
                            );
                        })()}
                    </div>
                </div>
            )}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// GAP ANALYSIS — Clear Competitive Landscape View
// ═══════════════════════════════════════════════════════════════════════════════

function GapAnalysis({
    competitors,
    yourPosition,
}: {
    competitors: { id: string; name: string; x: number; y: number; size: number; type: "direct" | "indirect" | "alt" }[];
    yourPosition: { x: number; y: number };
}) {
    const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null);

    // Categorize competitors
    const direct = competitors.filter(c => c.type === "direct");
    const indirect = competitors.filter(c => c.type === "indirect");
    const alternatives = competitors.filter(c => c.type === "alt");

    // Calculate your competitive situation
    const nearbyCompetitors = competitors.filter(c => {
        const dist = Math.sqrt(Math.pow(yourPosition.x - c.x, 2) + Math.pow(yourPosition.y - c.y, 2));
        return dist < 25;
    });

    const isCrowded = nearbyCompetitors.length >= 2;
    const mainThreat = direct.length > 0 ? direct.reduce((a, b) => a.size > b.size ? a : b) : null;

    // Find best opportunity quadrant
    const quadrants = [
        { name: "Premium + Comprehensive", x: 75, y: 75 },
        { name: "Value + Comprehensive", x: 25, y: 75 },
        { name: "Premium + Focused", x: 75, y: 25 },
        { name: "Value + Focused", x: 25, y: 25 },
    ];

    const leastCrowded = quadrants.map(q => ({
        ...q,
        competitors: competitors.filter(c =>
            Math.sqrt(Math.pow(c.x - q.x, 2) + Math.pow(c.y - q.y, 2)) < 30
        ).length
    })).sort((a, b) => a.competitors - b.competitors)[0];

    return (
        <div className="space-y-8">
            {/* Header with explanation */}
            <div>
                <span className="font-technical text-[10px] text-[var(--ink-muted)] tracking-widest">FIG. 03</span>
                <h3 className="font-serif text-3xl text-[var(--ink)] mt-1">Competitive Landscape</h3>
                <p className="text-[var(--secondary)] text-sm mt-2 max-w-2xl">
                    This shows where you and your competitors stand. Your goal: find spaces with fewer competitors.
                </p>
            </div>

            {/* What You're Looking At - Plain Language Explainer */}
            <div className="p-6 rounded-xl bg-[var(--surface)] border border-[var(--structure)]">
                <h4 className="font-medium text-sm text-[var(--ink)] mb-4">What You're Looking At</h4>
                <div className="grid grid-cols-3 gap-6 text-sm">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-4 h-4 rounded-full bg-[#ef4444]" />
                            <span className="font-medium text-[var(--ink)]">Direct Competitors</span>
                        </div>
                        <p className="text-[var(--secondary)] text-xs leading-relaxed">
                            Companies selling similar products to your same audience. These are your main rivals.
                        </p>
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-4 h-4 rounded-full bg-[#f97316]" />
                            <span className="font-medium text-[var(--ink)]">Indirect Competitors</span>
                        </div>
                        <p className="text-[var(--secondary)] text-xs leading-relaxed">
                            Different solutions that could solve your customer's problem in another way.
                        </p>
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-4 h-4 rounded-full bg-[#9ca3af]" />
                            <span className="font-medium text-[var(--ink)]">Alternatives</span>
                        </div>
                        <p className="text-[var(--secondary)] text-xs leading-relaxed">
                            What people do instead of buying any product (agencies, DIY, spreadsheets, etc).
                        </p>
                    </div>
                </div>
            </div>

            {/* Two Column Layout: Competitor List + Insight */}
            <div className="grid grid-cols-2 gap-6">
                {/* Competitor List */}
                <div className="space-y-4">
                    <h4 className="font-medium text-sm text-[var(--ink)]">Your Competitors ({competitors.length})</h4>

                    {/* Direct */}
                    {direct.length > 0 && (
                        <div className="space-y-2">
                            <span className="font-technical text-[9px] text-[#ef4444] tracking-widest">DIRECT THREATS</span>
                            {direct.map(c => (
                                <button
                                    key={c.id}
                                    onClick={() => setSelectedCompetitor(selectedCompetitor === c.id ? null : c.id)}
                                    className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all text-left ${selectedCompetitor === c.id ? "border-[#ef4444] bg-[#ef4444]/5" : "border-[var(--structure)] hover:border-[var(--ink)]/30"}`}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-[#ef4444]" />
                                        <span className="text-sm text-[var(--ink)]">{c.name}</span>
                                    </div>
                                    <span className="text-xs text-[var(--ink-muted)]">{c.size}% share</span>
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Indirect */}
                    {indirect.length > 0 && (
                        <div className="space-y-2">
                            <span className="font-technical text-[9px] text-[#f97316] tracking-widest">INDIRECT</span>
                            {indirect.map(c => (
                                <button
                                    key={c.id}
                                    onClick={() => setSelectedCompetitor(selectedCompetitor === c.id ? null : c.id)}
                                    className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all text-left ${selectedCompetitor === c.id ? "border-[#f97316] bg-[#f97316]/5" : "border-[var(--structure)] hover:border-[var(--ink)]/30"}`}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-[#f97316]" />
                                        <span className="text-sm text-[var(--ink)]">{c.name}</span>
                                    </div>
                                    <span className="text-xs text-[var(--ink-muted)]">{c.size}% share</span>
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Alternatives */}
                    {alternatives.length > 0 && (
                        <div className="space-y-2">
                            <span className="font-technical text-[9px] text-[#9ca3af] tracking-widest">ALTERNATIVES</span>
                            {alternatives.map(c => (
                                <button
                                    key={c.id}
                                    onClick={() => setSelectedCompetitor(selectedCompetitor === c.id ? null : c.id)}
                                    className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all text-left ${selectedCompetitor === c.id ? "border-[#9ca3af] bg-[#9ca3af]/5" : "border-[var(--structure)] hover:border-[var(--ink)]/30"}`}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-[#9ca3af]" />
                                        <span className="text-sm text-[var(--ink)]">{c.name}</span>
                                    </div>
                                    <span className="text-xs text-[var(--ink-muted)]">{c.size}% share</span>
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Your Insight Panel */}
                <div className="space-y-4">
                    <h4 className="font-medium text-sm text-[var(--ink)]">Your Insight</h4>

                    {/* Situation Assessment */}
                    <div className={`p-5 rounded-xl border ${isCrowded ? "border-[#f97316]/40 bg-[#f97316]/5" : "border-[var(--success)]/40 bg-[var(--success)]/5"}`}>
                        <div className="flex items-start gap-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isCrowded ? "bg-[#f97316]" : "bg-[var(--success)]"}`}>
                                {isCrowded ? <Users size={16} className="text-white" /> : <Target size={16} className="text-white" />}
                            </div>
                            <div>
                                <h5 className="font-medium text-sm text-[var(--ink)]">
                                    {isCrowded ? "Crowded Territory" : "Clear Space"}
                                </h5>
                                <p className="text-xs text-[var(--secondary)] mt-1 leading-relaxed">
                                    {isCrowded
                                        ? `You have ${nearbyCompetitors.length} competitor(s) nearby. Consider differentiating on features, price, or target audience.`
                                        : "Your current position has few direct competitors. This is a good sign for differentiation."}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Main Threat */}
                    {mainThreat && (
                        <div className="p-5 rounded-xl border border-[var(--structure)] bg-[var(--surface)]">
                            <span className="font-technical text-[9px] text-[var(--ink-muted)] tracking-widest">BIGGEST THREAT</span>
                            <div className="flex items-center gap-3 mt-2">
                                <div className="w-10 h-10 rounded-lg bg-[#ef4444]/10 flex items-center justify-center">
                                    <span className="font-serif text-lg text-[#ef4444]">{mainThreat.size}%</span>
                                </div>
                                <div>
                                    <span className="font-medium text-sm text-[var(--ink)] block">{mainThreat.name}</span>
                                    <span className="text-xs text-[var(--secondary)]">Largest direct competitor</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Opportunity */}
                    <div className="p-5 rounded-xl border border-[var(--success)]/40 bg-[var(--success)]/5">
                        <span className="font-technical text-[9px] text-[var(--success)] tracking-widest">OPPORTUNITY ZONE</span>
                        <div className="mt-2">
                            <span className="font-medium text-sm text-[var(--ink)] block">{leastCrowded.name}</span>
                            <span className="text-xs text-[var(--secondary)]">
                                Only {leastCrowded.competitors} competitor(s) in this quadrant
                            </span>
                        </div>
                    </div>

                    {/* What to Do */}
                    <div className="p-5 rounded-xl bg-[var(--ink)] text-[var(--canvas)]">
                        <span className="font-technical text-[9px] tracking-widest opacity-60">RECOMMENDED ACTION</span>
                        <p className="text-sm mt-2 leading-relaxed">
                            {isCrowded
                                ? "Focus your messaging on what makes you different from nearby competitors. Emphasize unique benefits."
                                : "Lean into your unique position. Your messaging can be bolder since you have less direct competition."}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// DATA
// ═══════════════════════════════════════════════════════════════════════════════

const INITIAL_BRANDS: Brand[] = [
    { id: "you", name: "Your Brand", x: 45, y: 62, size: 40, isYou: true },
    { id: "a", name: "Market Leader", x: 78, y: 85, size: 80 },
    { id: "b", name: "Budget Player", x: 22, y: 28, size: 50 },
    { id: "c", name: "Premium Niche", x: 88, y: 38, size: 35 },
    { id: "d", name: "Rising Star", x: 52, y: 55, size: 25 },
    { id: "e", name: "Legacy Tool", x: 65, y: 18, size: 45 },
];

const INITIAL_COMPETITORS = [
    { id: "c1", name: "Market Leader", x: 78, y: 85, size: 80, type: "direct" as const },
    { id: "c2", name: "Budget Player", x: 22, y: 28, size: 50, type: "direct" as const },
    { id: "c3", name: "Premium Niche", x: 88, y: 38, size: 35, type: "indirect" as const },
    { id: "c4", name: "Rising Star", x: 52, y: 55, size: 25, type: "direct" as const },
    { id: "c5", name: "Legacy Tool", x: 65, y: 18, size: 45, type: "alt" as const },
    { id: "c6", name: "Agencies", x: 90, y: 72, size: 40, type: "alt" as const },
    { id: "c7", name: "DIY", x: 15, y: 48, size: 30, type: "alt" as const },
];

const INITIAL_QUADRANTS: GridQuadrant[] = [
    {
        id: "market", title: "Market", question: "Who do you serve?", choices: [
            { id: "m1", label: "SMB (1-50)", selected: false },
            { id: "m2", label: "Mid-Market (50-500)", selected: false },
            { id: "m3", label: "Enterprise (500+)", selected: false },
            { id: "m4", label: "Startups", selected: false },
            { id: "m5", label: "Solopreneurs", selected: false },
        ]
    },
    {
        id: "category", title: "Category", question: "What are you?", choices: [
            { id: "c1", label: "Marketing OS", selected: false },
            { id: "c2", label: "Analytics Platform", selected: false },
            { id: "c3", label: "Content Engine", selected: false },
            { id: "c4", label: "Strategy Tool", selected: false },
            { id: "c5", label: "Automation", selected: false },
        ]
    },
    {
        id: "tribe", title: "Tribe", question: "Your community?", choices: [
            { id: "t1", label: "Growth Teams", selected: false },
            { id: "t2", label: "Founders", selected: false },
            { id: "t3", label: "Marketing Leaders", selected: false },
            { id: "t4", label: "Operators", selected: false },
            { id: "t5", label: "Builders", selected: false },
        ]
    },
    {
        id: "story", title: "Story", question: "Your narrative?", choices: [
            { id: "s1", label: "From chaos to clarity", selected: false },
            { id: "s2", label: "David vs Goliath", selected: false },
            { id: "s3", label: "Built by practitioners", selected: false },
            { id: "s4", label: "Opinionated", selected: false },
            { id: "s5", label: "Simplify complexity", selected: false },
        ]
    },
];

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function Step12CapabilityMatrix() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(12)?.data as Record<string, unknown> | undefined;

    const [view, setView] = useState<ViewMode>((stepData?.view as ViewMode) || "map");
    const [brands, setBrands] = useState<Brand[]>((stepData?.brands as Brand[]) || INITIAL_BRANDS);
    const [xAxis, setXAxis] = useState((stepData?.xAxis as string) || "price");
    const [yAxis, setYAxis] = useState((stepData?.yAxis as string) || "features");
    const [quadrants, setQuadrants] = useState<GridQuadrant[]>((stepData?.quadrants as GridQuadrant[]) || INITIAL_QUADRANTS);
    const [locked, setLocked] = useState((stepData?.locked as boolean) || false);

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-anim]"),
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power3.out" }
        );
    }, []);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelector("[data-view]"),
            { opacity: 0 },
            { opacity: 1, duration: 0.4, ease: "power2.out" }
        );
    }, [view]);

    useEffect(() => {
        updateStepData(12, { view, brands, xAxis, yAxis, quadrants, locked } as Record<string, unknown>);
    }, [view, brands, xAxis, yAxis, quadrants, locked, updateStepData]);

    const handleLock = () => {
        setLocked(true);
        updateStepStatus(12, "complete");
    };

    const yourBrand = brands.find(b => b.isYou);

    return (
        <div ref={containerRef} className="max-w-5xl mx-auto space-y-12 pb-12">
            {/* Header */}
            <div data-anim className="text-center">
                <span className="inline-block font-technical text-[10px] text-[var(--ink-muted)] tracking-[0.3em] mb-4">
                    STEP 12 OF 25
                </span>
                <h1 className="font-serif text-5xl text-[var(--ink)] leading-tight">
                    Competitive Positioning
                </h1>
                <p className="text-lg text-[var(--secondary)] mt-4 max-w-2xl mx-auto leading-relaxed">
                    Map your territory. Define your coordinates. Find the gaps.
                </p>
            </div>

            {/* View Selector */}
            <div data-anim className="flex justify-center">
                <div className="inline-flex border border-[var(--structure)] rounded-lg overflow-hidden">
                    {[
                        { id: "map" as ViewMode, label: "Perceptual Map" },
                        { id: "grid" as ViewMode, label: "Position Grid" },
                        { id: "gaps" as ViewMode, label: "Gap Analysis" },
                    ].map(v => (
                        <button
                            key={v.id}
                            onClick={() => setView(v.id)}
                            className={`px-8 py-3 text-sm font-medium transition-colors ${view === v.id ? "bg-[var(--ink)] text-[var(--canvas)]" : "text-[var(--ink)] hover:bg-[var(--surface)]"}`}
                        >
                            {v.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* View Content */}
            <div data-view className="min-h-[500px]">
                {view === "map" && (
                    <PerceptualMap
                        brands={brands}
                        setBrands={setBrands}
                        xAxis={xAxis}
                        yAxis={yAxis}
                        setXAxis={setXAxis}
                        setYAxis={setYAxis}
                    />
                )}
                {view === "grid" && (
                    <PositioningGrid
                        quadrants={quadrants}
                        setQuadrants={setQuadrants}
                    />
                )}
                {view === "gaps" && yourBrand && (
                    <GapAnalysis
                        competitors={INITIAL_COMPETITORS}
                        yourPosition={{ x: yourBrand.x, y: yourBrand.y }}
                    />
                )}
            </div>

            {/* Lock Section */}
            {!locked && (
                <div data-anim className="flex flex-col items-center gap-6 pt-8 border-t border-[var(--structure)]">
                    <p className="text-sm text-[var(--secondary)] text-center max-w-md">
                        When you're satisfied with your positioning, lock it to proceed.
                    </p>
                    <BlueprintButton size="lg" onClick={handleLock}>
                        <Lock size={16} />
                        Lock Position
                    </BlueprintButton>
                </div>
            )}

            {locked && (
                <div data-anim className="p-8 rounded-xl bg-[var(--success)]/5 border border-[var(--success)]/30">
                    <div className="flex items-center gap-6">
                        <div className="w-14 h-14 rounded-xl bg-[var(--success)] flex items-center justify-center">
                            <Check size={24} className="text-white" />
                        </div>
                        <div>
                            <h3 className="font-serif text-2xl text-[var(--ink)]">Position Locked</h3>
                            <p className="text-sm text-[var(--secondary)]">Your competitive coordinates are set.</p>
                        </div>
                        <BlueprintBadge variant="success" className="ml-auto">COMPLETE</BlueprintBadge>
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="text-center">
                <span className="font-technical text-[9px] text-[var(--ink-muted)] tracking-[0.25em]">
                    RAPTORFLOW • POSITIONING
                </span>
            </div>
        </div>
    );
}
