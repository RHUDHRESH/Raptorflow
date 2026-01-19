"use client";

import { useMemo } from "react";

interface StrategicRadarProps {
    scores: Record<string, number>;
}

export function StrategicRadar({ scores }: StrategicRadarProps) {
    const data = useMemo(() => {
        return Object.entries(scores).map(([key, value]) => ({ subject: key, A: value, fullMark: 100 }));
    }, [scores]);

    // Simple SVG Radar Chart Implementation
    const size = 200;
    const center = size / 2;
    const radius = size / 2 - 20;

    const points = data.map((d, i) => {
        const angle = (Math.PI * 2 * i) / data.length - Math.PI / 2;
        const val = (d.A / 100) * radius;
        const x = center + Math.cos(angle) * val;
        const y = center + Math.sin(angle) * val;
        return `${x},${y}`;
    }).join(" ");

    const bgPoints = data.map((d, i) => {
        const angle = (Math.PI * 2 * i) / data.length - Math.PI / 2;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius;
        return `${x},${y}`;
    }).join(" ");

    return (
        <div className="flex justify-center items-center h-full w-full">
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                {/* Background Polygon */}
                <polygon points={bgPoints} fill="var(--surface)" stroke="var(--structure)" strokeWidth="1" />

                {/* Data Polygon */}
                <polygon points={points} fill="rgba(58, 90, 124, 0.2)" stroke="var(--blueprint)" strokeWidth="2" />

                {/* Labels (simplified) */}
                {data.map((d, i) => {
                    const angle = (Math.PI * 2 * i) / data.length - Math.PI / 2;
                    const x = center + Math.cos(angle) * (radius + 15);
                    const y = center + Math.sin(angle) * (radius + 15);
                    return (
                        <text key={i} x={x} y={y} textAnchor="middle" dominantBaseline="middle" fontSize="10" fill="var(--ink-secondary)">
                            {d.subject.slice(0, 3).toUpperCase()}
                        </text>
                    );
                })}
            </svg>
        </div>
    );
}
