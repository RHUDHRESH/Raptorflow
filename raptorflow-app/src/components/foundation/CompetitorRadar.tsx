'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface RadarDataPoint {
    subject: string;
    A: number; // Brand
    B: number; // Competitor
    fullMark: number;
}

interface CompetitorRadarProps {
    data: RadarDataPoint[];
    brandName?: string;
    competitorName?: string;
    className?: string;
}

export function CompetitorRadar({
    data,
    brandName = "Brand",
    competitorName = "Competitor",
    className
}: CompetitorRadarProps) {
    const size = 300;
    const center = size / 2;
    const radius = size * 0.35;
    const totalPillars = data.length;

    // Calculate points for Brand (A)
    const brandPoints = data.map((d, i) => {
        const angle = (Math.PI * 2 * i) / totalPillars - Math.PI / 2;
        const r = (d.A / d.fullMark) * radius;
        return {
            x: center + r * Math.cos(angle),
            y: center + r * Math.sin(angle),
        };
    });

    // Calculate points for Competitor (B)
    const competitorPoints = data.map((d, i) => {
        const angle = (Math.PI * 2 * i) / totalPillars - Math.PI / 2;
        const r = (d.B / d.fullMark) * radius;
        return {
            x: center + r * Math.cos(angle),
            y: center + r * Math.sin(angle),
        };
    });

    const brandPointsString = brandPoints.map(p => `${p.x},${p.y}`).join(' ');
    const competitorPointsString = competitorPoints.map(p => `${p.x},${p.y}`).join(' ');

    return (
        <div className={cn(
            "p-8 rounded-[24px] bg-card border border-border flex flex-col items-center justify-center transition-all duration-300",
            className
        )}>
            <div className="w-full flex justify-between items-center mb-8">
                <h3 className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground/80 font-sans">
                    Competitor Comparison
                </h3>
                <div className="flex gap-4">
                    <div className="flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-foreground" />
                        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">{brandName}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-accent" />
                        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">{competitorName}</span>
                    </div>
                </div>
            </div>

            <div className="relative">
                <svg width={size} height={size} className="overflow-visible">
                    {/* Background rings */}
                    {[0.25, 0.5, 0.75, 1].map((r) => (
                        <circle
                            key={r}
                            cx={center}
                            cy={center}
                            r={radius * r}
                            fill="none"
                            stroke="currentColor"
                            className="text-border/30"
                            strokeWidth="0.5"
                            strokeDasharray={r === 1 ? "0" : "2 2"}
                        />
                    ))}

                    {/* Axis lines */}
                    {data.map((_, i) => {
                        const angle = (Math.PI * 2 * i) / totalPillars - Math.PI / 2;
                        return (
                            <line
                                key={i}
                                x1={center}
                                y1={center}
                                x2={center + radius * Math.cos(angle)}
                                y2={center + radius * Math.sin(angle)}
                                stroke="currentColor"
                                className="text-border/30"
                                strokeWidth="0.5"
                            />
                        );
                    })}

                    {/* Competitor Area (B) - Accent Layer */}
                    <motion.polygon
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                        points={competitorPointsString}
                        fill="currentColor"
                        className="text-accent/20"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinejoin="round"
                    />

                    {/* Brand Area (A) - Primary Layer */}
                    <motion.polygon
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                        points={brandPointsString}
                        fill="currentColor"
                        className="text-foreground/10"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinejoin="round"
                    />

                    {/* Points and Labels */}
                    {data.map((d, i) => {
                        const angle = (Math.PI * 2 * i) / totalPillars - Math.PI / 2;
                        const labelRadius = radius + 35;
                        const x = center + labelRadius * Math.cos(angle);
                        const y = center + labelRadius * Math.sin(angle);

                        return (
                            <g key={i}>
                                <text
                                    x={x}
                                    y={y}
                                    textAnchor="middle"
                                    className="text-[9px] font-sans font-semibold fill-muted-foreground uppercase tracking-[0.05em]"
                                >
                                    {d.subject}
                                </text>
                                {/* Mini points for Brand */}
                                <circle
                                    cx={brandPoints[i].x}
                                    cy={brandPoints[i].y}
                                    r="3"
                                    className="fill-foreground shadow-sm"
                                />
                                {/* Mini points for Competitor */}
                                <circle
                                    cx={competitorPoints[i].x}
                                    cy={competitorPoints[i].y}
                                    r="2.5"
                                    className="fill-accent shadow-sm"
                                />
                            </g>
                        );
                    })}
                </svg>
            </div>

            <div className="mt-12 w-full grid grid-cols-2 gap-4 border-t border-border/50 pt-6">
                <div className="text-center">
                    <span className="block text-[18px] font-display font-medium text-foreground">
                        {Math.round(data.reduce((acc, curr) => acc + curr.A, 0) / data.length)}
                    </span>
                    <span className="text-[9px] uppercase tracking-widest text-muted-foreground font-sans">Brand Avg</span>
                </div>
                <div className="text-center border-l border-border/50">
                    <span className="block text-[18px] font-display font-medium text-accent">
                        {Math.round(data.reduce((acc, curr) => acc + curr.B, 0) / data.length)}
                    </span>
                    <span className="text-[9px] uppercase tracking-widest text-muted-foreground font-sans">Comp Avg</span>
                </div>
            </div>
        </div>
    );
}
