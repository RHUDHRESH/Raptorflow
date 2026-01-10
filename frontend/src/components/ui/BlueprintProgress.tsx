"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT PROGRESS — Technical Progress Indicators
   Features:
   - Progress bar as technical gauge
   - Step progress with measurements
   - Circular progress with blueprint styling
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintProgressProps {
    value: number;
    max?: number;
    label?: string;
    code?: string;
    showValue?: boolean;
    size?: "sm" | "md" | "lg";
    variant?: "bar" | "gauge" | "steps";
    steps?: number;
    className?: string;
}

export function BlueprintProgress({
    value,
    max = 100,
    label,
    code,
    showValue = true,
    size = "md",
    variant = "bar",
    steps,
    className,
}: BlueprintProgressProps) {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100));

    const sizeClasses = {
        sm: "h-1.5",
        md: "h-2.5",
        lg: "h-4",
    };

    if (variant === "steps" && steps) {
        const currentStep = Math.ceil((value / max) * steps);

        return (
            <div className={cn("w-full", className)}>
                {label && (
                    <div className="flex items-center gap-2 mb-3">
                        <span className="font-technical text-[var(--muted)]">{label.toUpperCase()}</span>
                        <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                        <span className="font-technical text-[var(--blueprint)]">
                            {currentStep}/{steps}
                        </span>
                    </div>
                )}

                <div className="flex items-center gap-2">
                    {[...Array(steps)].map((_, i) => (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                            {/* Step indicator */}
                            <div
                                className={cn(
                                    "w-full rounded-[var(--radius-xs)] transition-all duration-300",
                                    sizeClasses[size],
                                    i < currentStep
                                        ? "bg-[var(--blueprint)]"
                                        : "bg-[var(--canvas)] border border-[var(--border)]"
                                )}
                            />
                            {/* Step number */}
                            <span className="font-technical text-[8px] text-[var(--muted)]">
                                {String(i + 1).padStart(2, "0")}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (variant === "gauge") {
        return (
            <div className={cn("relative", className)}>
                {/* Circular gauge */}
                <div className="relative w-20 h-20">
                    <svg viewBox="0 0 80 80" className="w-full h-full -rotate-90">
                        {/* Background circle */}
                        <circle
                            cx="40"
                            cy="40"
                            r="35"
                            fill="none"
                            stroke="var(--canvas)"
                            strokeWidth="6"
                        />
                        {/* Progress circle */}
                        <circle
                            cx="40"
                            cy="40"
                            r="35"
                            fill="none"
                            stroke="var(--blueprint)"
                            strokeWidth="6"
                            strokeLinecap="round"
                            strokeDasharray={220}
                            strokeDashoffset={220 - (220 * percentage) / 100}
                            className="transition-all duration-500"
                        />
                        {/* Tick marks */}
                        {[...Array(12)].map((_, i) => (
                            <line
                                key={i}
                                x1="40"
                                y1="8"
                                x2="40"
                                y2={i % 3 === 0 ? "12" : "10"}
                                stroke="var(--blueprint-line)"
                                strokeWidth="1"
                                transform={`rotate(${i * 30} 40 40)`}
                            />
                        ))}
                    </svg>

                    {/* Center value */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="font-technical text-sm text-[var(--ink)]">
                            {Math.round(percentage)}%
                        </span>
                    </div>
                </div>

                {label && (
                    <div className="mt-2 text-center">
                        <span className="font-technical text-[var(--muted)]">{label}</span>
                    </div>
                )}
            </div>
        );
    }

    // Default bar variant
    return (
        <div className={cn("w-full", className)}>
            {(label || code || showValue) && (
                <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                        {label && (
                            <span className="font-technical text-[var(--muted)]">{label.toUpperCase()}</span>
                        )}
                        {code && (
                            <>
                                <div className="h-3 w-px bg-[var(--blueprint-line)]" />
                                <span className="font-technical text-[var(--blueprint)]">{code}</span>
                            </>
                        )}
                    </div>
                    {showValue && (
                        <span className="font-technical text-[var(--ink)]">{Math.round(percentage)}%</span>
                    )}
                </div>
            )}

            <div className="relative">
                {/* Background track */}
                <div
                    className={cn(
                        "w-full bg-[var(--canvas)] rounded-full border border-[var(--border)] overflow-hidden",
                        sizeClasses[size]
                    )}
                >
                    {/* Progress fill */}
                    <div
                        className="h-full bg-[var(--blueprint)] rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                    />
                </div>

                {/* Measurement ticks */}
                <div className="absolute -bottom-3 left-0 right-0 flex justify-between px-0.5">
                    {[0, 25, 50, 75, 100].map((tick) => (
                        <div key={tick} className="flex flex-col items-center">
                            <div className="h-1 w-px bg-[var(--blueprint-line)]" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default BlueprintProgress;
