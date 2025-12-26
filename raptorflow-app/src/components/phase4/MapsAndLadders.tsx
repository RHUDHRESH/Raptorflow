'use client';

import React, { useState } from 'react';
import { Phase4Visuals, PerceptualMap, CategoryLadder, StrategyCanvas, ERRCGrid } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, Grid3X3, Layers, TrendingUp, LayoutGrid } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MapsAndLaddersProps {
    visuals: Phase4Visuals;
    onChange: (visuals: Phase4Visuals) => void;
    onContinue: () => void;
}

type VisualTab = 'perceptual' | 'ladder' | 'canvas' | 'errc';

// Perceptual Map (2x2)
function PerceptualMapView({ map }: { map: PerceptualMap }) {
    return (
        <div className="relative aspect-square max-w-lg mx-auto bg-card border rounded-xl p-4">
            {/* Axes Labels */}
            <div className="absolute left-1/2 bottom-2 -translate-x-1/2 text-xs text-muted-foreground">
                {map.xAxis.label}
            </div>
            <div className="absolute left-2 top-1/2 -translate-y-1/2 -rotate-90 origin-center text-xs text-muted-foreground whitespace-nowrap">
                {map.yAxis.label}
            </div>

            {/* Quadrant Lines */}
            <div className="absolute inset-8 border-l border-b border-dashed border-muted">
                <div className="absolute left-1/2 top-0 bottom-0 border-l border-dashed border-muted" />
                <div className="absolute top-1/2 left-0 right-0 border-t border-dashed border-muted" />
            </div>

            {/* Points */}
            {map.points.map(point => {
                const left = ((point.x + 1) / 2) * 80 + 10; // Map -1,1 to 10%,90%
                const top = ((1 - point.y) / 2) * 80 + 10; // Invert Y axis

                return (
                    <div
                        key={point.id}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2"
                        style={{ left: `${left}%`, top: `${top}%` }}
                    >
                        <div className={cn(
                            "w-4 h-4 rounded-full border-2",
                            point.isYou
                                ? "bg-primary border-primary"
                                : "bg-muted border-muted-foreground/50"
                        )} />
                        <span className={cn(
                            "absolute top-5 left-1/2 -translate-x-1/2 text-xs whitespace-nowrap",
                            point.isYou ? "font-bold text-primary" : "text-muted-foreground"
                        )}>
                            {point.name}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}

// Category Ladder
function LadderView({ ladder }: { ladder: CategoryLadder }) {
    return (
        <div className="max-w-md mx-auto space-y-4">
            <h3 className="text-center font-semibold text-muted-foreground">{ladder.category}</h3>
            <div className="space-y-2">
                {ladder.rungs
                    .sort((a, b) => a.position - b.position)
                    .map((rung, i) => (
                        <div
                            key={rung.brand}
                            className={cn(
                                "p-4 rounded-lg border-2 flex items-center gap-4",
                                rung.isYou
                                    ? "border-primary bg-primary/5"
                                    : "border-border bg-card"
                            )}
                        >
                            <span className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold",
                                rung.isYou ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                            )}>
                                #{rung.position}
                            </span>
                            <span className={cn("font-medium", rung.isYou && "text-primary")}>
                                {rung.brand}
                            </span>
                        </div>
                    ))}
            </div>
            {ladder.whyDifferentLadder && (
                <p className="text-sm text-muted-foreground text-center italic mt-4">
                    {ladder.whyDifferentLadder}
                </p>
            )}
        </div>
    );
}

// Strategy Canvas
function CanvasView({ canvas }: { canvas: StrategyCanvas }) {
    const height = 200;
    const factors = canvas.factors.filter(f => f.mattersToUs).slice(0, 8);
    const n = factors.length;

    if (n === 0) return <p className="text-center text-muted-foreground">No factors defined</p>;

    return (
        <div className="max-w-2xl mx-auto">
            <svg viewBox={`0 0 ${n * 80 + 40} ${height + 60}`} className="w-full">
                {/* Grid */}
                {[1, 2, 3, 4, 5].map(level => {
                    const y = height - ((level - 1) / 4) * (height - 40);
                    return (
                        <line
                            key={level}
                            x1="40"
                            y1={y}
                            x2={n * 80 + 20}
                            y2={y}
                            stroke="currentColor"
                            strokeOpacity="0.1"
                        />
                    );
                })}

                {/* Factor labels */}
                {factors.map((f, i) => (
                    <text
                        key={f.id}
                        x={i * 80 + 60}
                        y={height + 20}
                        textAnchor="middle"
                        className="text-xs fill-muted-foreground"
                    >
                        {f.name.slice(0, 10)}
                    </text>
                ))}

                {/* Target curve */}
                {canvas.curves.youTarget.length >= n && (
                    <polyline
                        points={factors.map((f, i) => {
                            const x = i * 80 + 60;
                            const y = height - ((canvas.curves.youTarget[i] - 1) / 4) * (height - 40);
                            return `${x},${y}`;
                        }).join(' ')}
                        fill="none"
                        stroke="#10B981"
                        strokeWidth="3"
                    />
                )}
            </svg>
        </div>
    );
}

// ERRC Grid
function ERRCView({ errc }: { errc: ERRCGrid }) {
    const columns = [
        { key: 'eliminate', label: 'Eliminate', color: 'text-red-600 bg-red-50 dark:bg-red-950/30' },
        { key: 'reduce', label: 'Reduce', color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/30' },
        { key: 'raise', label: 'Raise', color: 'text-blue-600 bg-blue-50 dark:bg-blue-950/30' },
        { key: 'create', label: 'Create', color: 'text-green-600 bg-green-50 dark:bg-green-950/30' },
    ] as const;

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {columns.map(({ key, label, color }) => (
                <div key={key} className={cn("rounded-xl p-4", color.split(' ').slice(1).join(' '))}>
                    <h4 className={cn("font-semibold text-sm mb-3", color.split(' ')[0])}>{label}</h4>
                    <ul className="space-y-2">
                        {(errc[key] || []).map((item, i) => (
                            <li key={i} className="text-sm">{item.factor}</li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
}

export function MapsAndLadders({ visuals, onChange, onContinue }: MapsAndLaddersProps) {
    const [activeTab, setActiveTab] = useState<VisualTab>('perceptual');

    const tabs = [
        { key: 'perceptual' as const, label: 'Perceptual Map', icon: Grid3X3 },
        { key: 'ladder' as const, label: 'Ladder', icon: Layers },
        { key: 'canvas' as const, label: 'Strategy Canvas', icon: TrendingUp },
        { key: 'errc' as const, label: 'ERRC', icon: LayoutGrid },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Maps & Ladders
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Visual positioning tools that make your strategy memorable.
                </p>
            </div>

            {/* Tab Navigation */}
            <div className="flex justify-center gap-2">
                {tabs.map(({ key, label, icon: Icon }) => (
                    <button
                        key={key}
                        onClick={() => setActiveTab(key)}
                        className={cn(
                            "px-4 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors",
                            activeTab === key
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted text-muted-foreground hover:text-foreground"
                        )}
                    >
                        <Icon className="h-4 w-4" />
                        {label}
                    </button>
                ))}
            </div>

            {/* Active Visual */}
            <div className="min-h-[400px]">
                {activeTab === 'perceptual' && <PerceptualMapView map={visuals.perceptualMap} />}
                {activeTab === 'ladder' && <LadderView ladder={visuals.ladder} />}
                {activeTab === 'canvas' && <CanvasView canvas={visuals.strategyCanvas} />}
                {activeTab === 'errc' && <ERRCView errc={visuals.errc} />}
            </div>

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button size="lg" onClick={onContinue} className="px-8 py-6 text-lg rounded-xl">
                    Continue <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
