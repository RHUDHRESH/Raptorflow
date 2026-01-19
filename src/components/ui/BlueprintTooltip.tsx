"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT TOOLTIP — Technical Hover Information
   Features:
   - Measurement-style pointer
   - Blueprint background
   - Technical typography
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintTooltipProps {
    content: React.ReactNode;
    code?: string;
    position?: "top" | "bottom" | "left" | "right";
    delay?: number;
    children: React.ReactNode;
    className?: string;
}

export function BlueprintTooltip({
    content,
    code,
    position = "top",
    delay = 300,
    children,
    className,
}: BlueprintTooltipProps) {
    const [isVisible, setIsVisible] = useState(false);
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);

    const handleMouseEnter = () => {
        timeoutRef.current = setTimeout(() => setIsVisible(true), delay);
    };

    const handleMouseLeave = () => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        setIsVisible(false);
    };

    useEffect(() => {
        return () => {
            if (timeoutRef.current) clearTimeout(timeoutRef.current);
        };
    }, []);

    const positionClasses = {
        top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
        bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
        left: "right-full top-1/2 -translate-y-1/2 mr-2",
        right: "left-full top-1/2 -translate-y-1/2 ml-2",
    };

    const pointerClasses = {
        top: "top-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-[var(--ink)]",
        bottom: "bottom-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-[var(--ink)]",
        left: "left-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-[var(--ink)]",
        right: "right-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-[var(--ink)]",
    };

    return (
        <div
            className={cn("relative inline-block", className)}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {children}

            {isVisible && (
                <div
                    className={cn(
                        "absolute z-50 px-3 py-2 rounded-[var(--radius-sm)]",
                        "bg-[var(--ink)] text-[var(--paper)]",
                        "ink-bleed-md whitespace-nowrap",
                        "ink-fade-in",
                        positionClasses[position]
                    )}
                >
                    {/* Registration marks */}
                    <div className="absolute top-0 left-0 w-1.5 h-1.5 border-t border-l border-[var(--blueprint-line)]" />
                    <div className="absolute top-0 right-0 w-1.5 h-1.5 border-t border-r border-[var(--blueprint-line)]" />

                    <div className="flex items-center gap-2">
                        {code && (
                            <span className="font-technical text-[9px] text-[var(--blueprint)] bg-[var(--blueprint-light)] px-1 rounded">
                                {code}
                            </span>
                        )}
                        <span className="text-xs">{content}</span>
                    </div>

                    {/* Pointer */}
                    <div
                        className={cn(
                            "absolute w-0 h-0 border-4",
                            pointerClasses[position]
                        )}
                    />
                </div>
            )}
        </div>
    );
}

export default BlueprintTooltip;
