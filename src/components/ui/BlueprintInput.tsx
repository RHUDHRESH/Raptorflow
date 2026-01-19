"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT INPUT — Technical Form Field
   Features:
   - Label positioned like architectural callout
   - Input field with ruled lines (graph paper)
   - Focus state with pencil stroke animation
   - Placeholder in JetBrains Mono
   - Measurement indicators
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size"> {
    label?: string;
    code?: string; // e.g., "INP-01"
    hint?: string;
    error?: string;
    showRuler?: boolean;
    size?: "sm" | "md" | "lg";
    startIcon?: React.ReactNode;
    endIcon?: React.ReactNode;
}

export function BlueprintInput({
    label,
    code,
    hint,
    error,
    showRuler = false,
    size = "md",
    startIcon,
    endIcon,
    className,
    ...props
}: BlueprintInputProps) {
    const inputRef = useRef<HTMLInputElement>(null);
    const [isFocused, setIsFocused] = useState(false);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    useEffect(() => {
        if (!inputRef.current) return;
        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                setDimensions({
                    width: entry.contentRect.width + 2,
                    height: entry.contentRect.height + 2
                });
            }
        });
        observer.observe(inputRef.current);
        return () => observer.disconnect();
    }, []);

    const sizeClasses = {
        sm: "h-8 text-sm px-3",
        md: "h-10 text-sm px-4",
        lg: "h-12 text-base px-5",
    };

    const pathLength = 2 * (dimensions.width + dimensions.height);

    return (
        <div className="relative">
            {/* Label as architectural callout */}
            {label && (
                <div className="flex items-center gap-2 mb-2">
                    <label className="font-mono text-[10px] tracking-widest text-ink/40 uppercase">
                        {label}
                    </label>
                    {code && (
                        <>
                            <div className="h-px flex-1 bg-structure/30" />
                            <span className="font-mono text-[10px] text-accent-blue">{code}</span>
                        </>
                    )}
                </div>
            )}

            {/* Input container */}
            <div className="relative">
                {/* Pencil stroke border on focus */}
                {dimensions.width > 0 && (
                    <svg
                        className="absolute inset-0 pointer-events-none overflow-visible z-10"
                        style={{ left: -1, top: -1, width: dimensions.width, height: dimensions.height }}
                    >
                        <rect
                            x="0.5"
                            y="0.5"
                            width={dimensions.width - 1}
                            height={dimensions.height - 1}
                            rx="4"
                            ry="4"
                            fill="none"
                            stroke="var(--accent-blue)"
                            strokeWidth="1.5"
                            strokeDasharray={pathLength}
                            strokeDashoffset={isFocused ? 0 : pathLength}
                            style={{
                                transition: "stroke-dashoffset 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                            }}
                        />
                    </svg>
                )}

                {/* Start Icon */}
                {startIcon && (
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted pointer-events-none z-20">
                        {startIcon}
                    </div>
                )}

                {/* The actual input */}
                <input
                    ref={inputRef}
                    className={cn(
                        // Base
                        "w-full rounded-sm",
                        "bg-paper border border-structure",
                        "text-ink placeholder:text-ink/20",
                        "placeholder:font-mono placeholder:text-xs",
                        "transition-all duration-200",

                        // Focus
                        "focus:outline-none focus:border-accent-blue",
                        "focus:ring-2 focus:ring-accent-blue/10",

                        // States
                        error && "border-error focus:border-error focus:ring-error/10",

                        // Size
                        sizeClasses[size],

                        // Icon Padding
                        startIcon ? "pl-10" : "",
                        endIcon ? "pr-10" : "",

                        // Shadow
                        "shadow-ink-sm",

                        className
                    )}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    {...props}
                />

                {/* End Icon */}
                {endIcon && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted z-20">
                        {endIcon}
                    </div>
                )}

                {/* Ruler marks on focus */}
                {showRuler && isFocused && (
                    <div className="absolute -bottom-4 left-0 right-0 flex justify-between px-1 pointer-events-none">
                        {[...Array(10)].map((_, i) => (
                            <div key={i} className="flex flex-col items-center">
                                <div className={cn(
                                    "w-px bg-structure/50",
                                    i % 5 === 0 ? "h-2" : "h-1"
                                )} />
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Hint text */}
            {hint && !error && (
                <p className="mt-1.5 font-mono text-[10px] text-ink-muted">{hint}</p>
            )}

            {/* Error text */}
            {error && (
                <p className="mt-1.5 font-mono text-[10px] text-error">{error}</p>
            )}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT TEXTAREA
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
    label?: string;
    code?: string;
    hint?: string;
    error?: string;
}

export function BlueprintTextarea({
    label,
    code,
    hint,
    error,
    className,
    ...props
}: BlueprintTextareaProps) {
    return (
        <div className="relative">
            {label && (
                <div className="flex items-center gap-2 mb-2">
                    <label className="font-mono text-[10px] tracking-widest text-ink/40 uppercase">
                        {label}
                    </label>
                    {code && (
                        <>
                            <div className="h-px flex-1 bg-structure/30" />
                            <span className="font-mono text-[10px] text-accent-blue">{code}</span>
                        </>
                    )}
                </div>
            )}

            <textarea
                className={cn(
                    "w-full min-h-[120px] p-4 rounded-sm",
                    "bg-paper border border-structure",
                    "text-ink placeholder:text-ink/20",
                    "placeholder:font-mono placeholder:text-xs",
                    "transition-all duration-200",
                    "focus:outline-none focus:border-accent-blue",
                    "focus:ring-2 focus:ring-accent-blue/10",
                    "shadow-ink-sm",
                    "resize-none",

                    // Lined paper effect
                    "bg-[length:100%_24px]",
                    "bg-[linear-gradient(transparent_23px,rgba(45,53,56,0.05)_23px)]",

                    error && "border-error",
                    className
                )}
                {...props}
            />

            {hint && !error && (
                <p className="mt-1.5 font-mono text-[10px] text-ink-muted">{hint}</p>
            )}

            {error && (
                <p className="mt-1.5 font-mono text-[10px] text-error">{error}</p>
            )}
        </div>
    );
}

export default BlueprintInput;
