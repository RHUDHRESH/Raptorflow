"use client";

import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MODERN PROGRESS BAR — Rounded gradient progress bars
   ══════════════════════════════════════════════════════════════════════════════ */

interface ModernProgressProps {
    value: number; // 0-100
    max?: number;
    size?: "sm" | "md" | "lg";
    variant?: "default" | "success" | "warning" | "error" | "blue" | "purple";
    showLabel?: boolean;
    label?: string;
    className?: string;
    animated?: boolean;
}

export function ModernProgress({
    value,
    max = 100,
    size = "md",
    variant = "default",
    showLabel = false,
    label,
    className,
    animated = true,
}: ModernProgressProps) {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100));

    const sizeClasses = {
        sm: "h-1.5",
        md: "h-2",
        lg: "h-3",
    };

    const gradients = {
        default: "from-emerald-400 to-emerald-500",
        success: "from-emerald-400 to-emerald-500",
        warning: "from-amber-400 to-amber-500",
        error: "from-red-400 to-red-500",
        blue: "from-blue-400 to-blue-500",
        purple: "from-violet-400 to-violet-500",
    };

    return (
        <div className={cn("w-full", className)}>
            {/* Label row */}
            {(showLabel || label) && (
                <div className="flex items-center justify-between mb-2">
                    {label && (
                        <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            {label}
                        </span>
                    )}
                    {showLabel && (
                        <span className="text-sm font-semibold text-slate-900 dark:text-white">
                            {Math.round(percentage)}%
                        </span>
                    )}
                </div>
            )}

            {/* Progress bar track */}
            <div
                className={cn(
                    "w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden",
                    sizeClasses[size]
                )}
            >
                {/* Progress bar fill */}
                <div
                    className={cn(
                        "h-full rounded-full bg-gradient-to-r",
                        gradients[variant],
                        animated && "transition-all duration-500 ease-out"
                    )}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   CIRCULAR PROGRESS — Ring-style progress indicator
   ══════════════════════════════════════════════════════════════════════════════ */

interface CircularProgressProps {
    value: number;
    max?: number;
    size?: number;
    strokeWidth?: number;
    variant?: "default" | "success" | "warning" | "error" | "blue";
    showValue?: boolean;
    className?: string;
}

export function CircularProgress({
    value,
    max = 100,
    size = 60,
    strokeWidth = 6,
    variant = "default",
    showValue = true,
    className,
}: CircularProgressProps) {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100));
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (percentage / 100) * circumference;

    const colors = {
        default: "#10B981",
        success: "#10B981",
        warning: "#F59E0B",
        error: "#EF4444",
        blue: "#3B82F6",
    };

    return (
        <div className={cn("relative inline-flex", className)} style={{ width: size, height: size }}>
            <svg width={size} height={size} className="transform -rotate-90">
                {/* Track */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="none"
                    className="text-slate-100 dark:text-slate-800"
                />
                {/* Progress */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke={colors[variant]}
                    strokeWidth={strokeWidth}
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className="transition-all duration-500 ease-out"
                />
            </svg>
            {showValue && (
                <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-bold text-slate-900 dark:text-white">
                        {Math.round(percentage)}%
                    </span>
                </div>
            )}
        </div>
    );
}
