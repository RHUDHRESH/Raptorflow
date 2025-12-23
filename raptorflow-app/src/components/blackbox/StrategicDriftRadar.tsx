'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface RadarData {
    pillar: string;
    value: number; // 0 to 100
}

interface StrategicDriftRadarProps {
    data?: RadarData[];
}

const DEFAULT_DATA: RadarData[] = [
    { pillar: 'Clarity', value: 85 },
    { pillar: 'Control', value: 70 },
    { pillar: 'Speed', value: 90 },
    { pillar: 'Proof', value: 65 },
    { pillar: 'Momentum', value: 80 },
];

export function StrategicDriftRadar({ data = DEFAULT_DATA }: StrategicDriftRadarProps) {
    const size = 300;
    const center = size / 2;
    const radius = size * 0.4;
    const totalPillars = data.length;

    // Calculate points for the radar shape
    const points = data.map((d, i) => {
        const angle = (Math.PI * 2 * i) / totalPillars - Math.PI / 2;
        const r = (d.value / 100) * radius;
        return {
            x: center + r * Math.cos(angle),
            y: center + r * Math.sin(angle),
        };
    });

    const pointsString = points.map(p => `${p.x},${p.y}`).join(' ');

    return (
        <div className="p-6 rounded-2xl bg-card border border-border flex flex-col items-center justify-center">
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground font-sans mb-6">
                Strategic Alignment
            </h3>

            <div className="relative">
                <svg width={size} height={size} className="overflow-visible">
                    {/* Background circles */}
                    {[0.2, 0.4, 0.6, 0.8, 1].map((r) => (
                        <circle
                            key={r}
                            cx={center}
                            cy={center}
                            r={radius * r}
                            fill="none"
                            stroke="currentColor"
                            className="text-border/40"
                            strokeWidth="1"
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
                                className="text-border/40"
                                strokeWidth="1"
                            />
                        );
                    })}

                    {/* Radar polygon */}
                    <motion.polygon
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        points={pointsString}
                        fill="currentColor"
                        className="text-accent/20"
                        stroke="currentColor"
                        strokeWidth="2"
                    />

                    {/* Labels */}
                    {data.map((d, i) => {
                        const angle = (Math.PI * 2 * i) / totalPillars - Math.PI / 2;
                        const x = center + (radius + 25) * Math.cos(angle);
                        const y = center + (radius + 20) * Math.sin(angle);
                        return (
                            <text
                                key={i}
                                x={x}
                                y={y}
                                textAnchor="middle"
                                className="text-[10px] font-sans font-medium fill-muted-foreground uppercase tracking-tighter"
                            >
                                {d.pillar}
                            </text>
                        );
                    })}
                </svg>
            </div>

            <div className="mt-6 flex items-center gap-4 text-[10px] font-sans text-muted-foreground">
                <div className="flex items-center gap-1.5">
                    <div className="h-2 w-2 rounded-full bg-accent" />
                    <span>Target Profile</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className="h-2 w-2 rounded-full bg-border" />
                    <span>Baseline</span>
                </div>
            </div>
        </div>
    );
}
