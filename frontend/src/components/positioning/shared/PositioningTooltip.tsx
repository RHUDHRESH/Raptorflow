"use client";

import { useState, useRef, useEffect } from "react";

/* ══════════════════════════════════════════════════════════════════════════════
   POSITIONING TOOLTIP — Hover tooltip for positioning elements
   ══════════════════════════════════════════════════════════════════════════════ */

interface TooltipData {
    name: string;
    x: number;
    y: number;
    xLabel?: string;
    yLabel?: string;
    details?: { label: string; value: string }[];
}

interface PositioningTooltipProps {
    data: TooltipData | null;
    position: { x: number; y: number };
}

export function PositioningTooltip({ data, position }: PositioningTooltipProps) {
    const tooltipRef = useRef<HTMLDivElement>(null);

    if (!data) return null;

    return (
        <div
            ref={tooltipRef}
            style={{
                position: "fixed",
                left: position.x + 15,
                top: position.y + 15,
                zIndex: 1000,
            }}
            className="bg-[var(--ink)] text-[var(--paper)] px-4 py-3 rounded-xl shadow-2xl max-w-xs pointer-events-none"
        >
            <h4 className="font-serif text-sm mb-2">{data.name}</h4>
            <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div>
                    <span className="font-technical opacity-70">{data.xLabel || "X"}</span>
                    <p className="font-medium">{data.x.toFixed(0)}%</p>
                </div>
                <div>
                    <span className="font-technical opacity-70">{data.yLabel || "Y"}</span>
                    <p className="font-medium">{data.y.toFixed(0)}%</p>
                </div>
            </div>
            {data.details && data.details.length > 0 && (
                <div className="mt-2 pt-2 border-t border-[var(--paper)]/20 space-y-1">
                    {data.details.map((d, i) => (
                        <div key={i} className="flex justify-between text-[10px]">
                            <span className="opacity-70">{d.label}</span>
                            <span>{d.value}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// Hook for managing tooltip state
export function usePositioningTooltip() {
    const [tooltip, setTooltip] = useState<{ data: TooltipData | null; position: { x: number; y: number } }>({
        data: null,
        position: { x: 0, y: 0 },
    });

    const showTooltip = (data: TooltipData, e: React.MouseEvent) => {
        setTooltip({ data, position: { x: e.clientX, y: e.clientY } });
    };

    const hideTooltip = () => {
        setTooltip({ data: null, position: { x: 0, y: 0 } });
    };

    const updatePosition = (e: React.MouseEvent) => {
        if (tooltip.data) {
            setTooltip(prev => ({ ...prev, position: { x: e.clientX, y: e.clientY } }));
        }
    };

    return { tooltip, showTooltip, hideTooltip, updatePosition };
}
