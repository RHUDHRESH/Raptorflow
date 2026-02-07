'use client';

import React from 'react';
import { StrategyCanvas as StrategyCanvasType, CanvasFactor } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, Eye, EyeOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StrategyCanvasProps {
    canvas: StrategyCanvasType;
    onChange: (canvas: StrategyCanvasType) => void;
    onContinue: () => void;
}

const CURVE_COLORS = {
    statusQuo: '#9CA3AF',     // gray
    categoryLeader: '#3B82F6', // blue
    youCurrent: '#F59E0B',     // amber
    youTarget: '#10B981',      // green
};

export function StrategyCanvasScreen({ canvas, onChange, onContinue }: StrategyCanvasProps) {
    const [showCurrent, setShowCurrent] = React.useState(true);

    const toggleFactor = (factorId: string) => {
        onChange({
            ...canvas,
            factors: canvas.factors.map(f =>
                f.id === factorId ? { ...f, mattersToUs: !f.mattersToUs } : f
            )
        });
    };

    const updateFactorLevel = (factorId: string, level: 1 | 2 | 3 | 4 | 5) => {
        onChange({
            ...canvas,
            factors: canvas.factors.map(f =>
                f.id === factorId ? { ...f, targetLevel: level } : f
            ),
            curves: {
                ...canvas.curves,
                youTarget: canvas.factors.map(f =>
                    f.id === factorId ? level : f.targetLevel
                )
            }
        });
    };

    const visibleFactors = canvas.factors.filter(f => f.mattersToUs);
    const chartHeight = 200;
    const chartWidth = Math.max(600, visibleFactors.length * 80);

    // SVG Path generator for curves
    const generatePath = (values: number[], factors: CanvasFactor[]) => {
        const visibleValues = factors.map((f, i) =>
            f.mattersToUs ? values[i] : null
        ).filter(v => v !== null) as number[];

        if (visibleValues.length === 0) return '';

        const stepX = chartWidth / (visibleValues.length + 1);
        const points = visibleValues.map((v, i) => {
            const x = stepX * (i + 1);
            const y = chartHeight - ((v - 1) / 4) * (chartHeight - 40);
            return `${x},${y}`;
        });

        return `M ${points.join(' L ')}`;
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Strategy Canvas
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Your value curve shows where you compete high vs. low. Create differentiation by diverging from the pack.
                </p>
            </div>

            {/* Legend */}
            <div className="flex justify-center gap-6 text-sm">
                {[
                    { key: 'statusQuo', label: 'Status Quo', color: CURVE_COLORS.statusQuo },
                    { key: 'categoryLeader', label: 'Leader', color: CURVE_COLORS.categoryLeader },
                    ...(showCurrent ? [{ key: 'youCurrent', label: 'You (Current)', color: CURVE_COLORS.youCurrent }] : []),
                    { key: 'youTarget', label: 'You (Target)', color: CURVE_COLORS.youTarget },
                ].map(({ key, label, color }) => (
                    <div key={key} className="flex items-center gap-2">
                        <div className="w-4 h-1 rounded" style={{ backgroundColor: color }} />
                        <span className="text-muted-foreground">{label}</span>
                    </div>
                ))}
                <button
                    onClick={() => setShowCurrent(!showCurrent)}
                    className="flex items-center gap-1 text-muted-foreground hover:text-foreground ml-4"
                >
                    {showCurrent ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                    <span className="text-xs">Current</span>
                </button>
            </div>

            {/* Chart */}
            <div className="overflow-x-auto pb-4">
                <div className="min-w-[600px] max-w-4xl mx-auto">
                    <svg
                        viewBox={`0 0 ${chartWidth} ${chartHeight + 60}`}
                        className="w-full"
                        preserveAspectRatio="xMidYMid meet"
                    >
                        {/* Y-axis labels */}
                        {[1, 2, 3, 4, 5].map(level => {
                            const y = chartHeight - ((level - 1) / 4) * (chartHeight - 40);
                            return (
                                <g key={level}>
                                    <line
                                        x1="40"
                                        y1={y}
                                        x2={chartWidth - 20}
                                        y2={y}
                                        stroke="currentColor"
                                        strokeOpacity="0.1"
                                    />
                                    <text
                                        x="30"
                                        y={y + 4}
                                        textAnchor="end"
                                        className="text-xs fill-muted-foreground"
                                    >
                                        {level}
                                    </text>
                                </g>
                            );
                        })}

                        {/* Curves */}
                        <path
                            d={generatePath(canvas.curves.statusQuo, canvas.factors)}
                            fill="none"
                            stroke={CURVE_COLORS.statusQuo}
                            strokeWidth="2"
                            strokeDasharray="4 4"
                        />
                        <path
                            d={generatePath(canvas.curves.categoryLeader, canvas.factors)}
                            fill="none"
                            stroke={CURVE_COLORS.categoryLeader}
                            strokeWidth="2"
                        />
                        {showCurrent && (
                            <path
                                d={generatePath(canvas.curves.youCurrent, canvas.factors)}
                                fill="none"
                                stroke={CURVE_COLORS.youCurrent}
                                strokeWidth="2"
                                strokeDasharray="2 2"
                            />
                        )}
                        <path
                            d={generatePath(canvas.curves.youTarget, canvas.factors)}
                            fill="none"
                            stroke={CURVE_COLORS.youTarget}
                            strokeWidth="3"
                        />

                        {/* X-axis labels */}
                        {visibleFactors.map((factor, i) => {
                            const stepX = chartWidth / (visibleFactors.length + 1);
                            const x = stepX * (i + 1);
                            return (
                                <text
                                    key={factor.id}
                                    x={x}
                                    y={chartHeight + 20}
                                    textAnchor="middle"
                                    className="text-xs fill-muted-foreground"
                                >
                                    {factor.name.length > 12
                                        ? factor.name.slice(0, 10) + '...'
                                        : factor.name
                                    }
                                </text>
                            );
                        })}
                    </svg>
                </div>
            </div>

            {/* Factor Controls */}
            <div className="max-w-3xl mx-auto space-y-3">
                <h3 className="text-sm font-medium text-muted-foreground">Adjust Your Target Level</h3>
                <div className="grid gap-3">
                    {canvas.factors.map(factor => (
                        <div
                            key={factor.id}
                            className={cn(
                                "flex items-center gap-4 p-3 rounded-lg border transition-all",
                                factor.mattersToUs ? "border-border bg-card" : "border-dashed border-muted opacity-50"
                            )}
                        >
                            <button
                                onClick={() => toggleFactor(factor.id)}
                                className="p-1 hover:bg-muted rounded"
                            >
                                {factor.mattersToUs ? (
                                    <Eye className="h-4 w-4 text-foreground" />
                                ) : (
                                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                                )}
                            </button>
                            <span className="flex-1 text-sm font-medium">{factor.name}</span>
                            <div className="flex gap-1">
                                {([1, 2, 3, 4, 5] as const).map(level => (
                                    <button
                                        key={level}
                                        onClick={() => updateFactorLevel(factor.id, level)}
                                        className={cn(
                                            "w-8 h-8 rounded-lg text-xs font-medium transition-all",
                                            factor.targetLevel === level
                                                ? "bg-primary text-primary-foreground"
                                                : "bg-muted hover:bg-muted/80 text-muted-foreground"
                                        )}
                                    >
                                        {level}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
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
