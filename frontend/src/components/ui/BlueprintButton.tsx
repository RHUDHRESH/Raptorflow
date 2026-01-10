"use client";

import React, { useRef, useEffect, useState } from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT BUTTON — The Paper Terminal Hero Component
   Features:
   - Pencil stroke animation on hover (SVG border drawing)
   - Ink bleed shadow system (5-layer organic shadows)
   - Registration corner marks
   - Technical label annotation
   - Press effect (ink press into paper)
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost";
    size?: "sm" | "md" | "lg";
    label?: string; // Technical label like "BTN-01"
    showCorners?: boolean;
    showPencilStroke?: boolean;
    children: React.ReactNode;
}

export function BlueprintButton({
    variant = "primary",
    size = "md",
    label,
    showCorners = true,
    showPencilStroke = true,
    className,
    children,
    ...props
}: BlueprintButtonProps) {
    const buttonRef = useRef<HTMLButtonElement>(null);
    const [isHovered, setIsHovered] = useState(false);
    const [isPressed, setIsPressed] = useState(false);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    // Get button dimensions for SVG stroke
    useEffect(() => {
        if (buttonRef.current) {
            const { width, height } = buttonRef.current.getBoundingClientRect();
            setDimensions({ width, height });
        }
    }, []);

    // Resize observer for dynamic sizing
    useEffect(() => {
        if (!buttonRef.current) return;

        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                const rect = entry.target.getBoundingClientRect();
                setDimensions({ width: rect.width, height: rect.height });
            }
        });

        observer.observe(buttonRef.current);
        return () => observer.disconnect();
    }, []);

    // Calculate path length for animation (full perimeter + extra for corners)
    const cornerRadius = 6;
    const pathLength = 2 * (dimensions.width + dimensions.height) - 8 * cornerRadius + 2 * Math.PI * cornerRadius;

    // Size classes
    const sizeClasses = {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-5 text-sm",
        lg: "h-12 px-8 text-base",
    };

    // Variant classes
    const variantClasses = {
        primary: cn(
            "bg-[var(--ink)] text-[var(--paper)]",
            "hover:bg-[var(--ink)]/90",
            isPressed ? "ink-press" : "ink-bleed-md"
        ),
        secondary: cn(
            "bg-[var(--paper)] text-[var(--ink)] border-2 border-[var(--ink)]",
            "hover:bg-[var(--canvas)]",
            isPressed ? "ink-press" : "ink-bleed-sm"
        ),
        ghost: cn(
            "bg-transparent text-[var(--ink)]",
            "hover:bg-[var(--canvas)]",
            isPressed && "ink-press"
        ),
    };

    return (
        <div className="relative inline-flex flex-col items-start gap-1">
            {/* Technical Label */}
            {label && (
                <span className="font-technical text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-opacity">
                    {label}
                </span>
            )}

            <button
                ref={buttonRef}
                className={cn(
                    // Base styles
                    "group relative inline-flex items-center justify-center gap-2",
                    "font-medium rounded-[var(--radius-sm)]",
                    "transition-all duration-200",
                    "focus-visible:outline-none blueprint-focus",

                    // Size
                    sizeClasses[size],

                    // Variant
                    variantClasses[variant],

                    className
                )}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                onMouseDown={() => setIsPressed(true)}
                onMouseUp={() => setIsPressed(false)}
                {...props}
            >
                {/* Pencil Stroke SVG Border - Full Coverage with Glow */}
                {showPencilStroke && dimensions.width > 0 && (
                    <svg
                        className="absolute pointer-events-none"
                        style={{
                            left: 0,
                            top: 0,
                            width: dimensions.width,
                            height: dimensions.height,
                            overflow: 'visible'
                        }}
                    >
                        <defs>
                            {/* Glow filter for premium effect */}
                            <filter id="blueprint-glow" x="-50%" y="-50%" width="200%" height="200%">
                                <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur" />
                                <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0.32  0 0 0 0 0.55  0 0 0 0 0.75  0 0 0 1 0" result="glow" />
                                <feMerge>
                                    <feMergeNode in="glow" />
                                    <feMergeNode in="glow" />
                                    <feMergeNode in="SourceGraphic" />
                                </feMerge>
                            </filter>
                        </defs>

                        {/* Outer glow layer - appears first */}
                        <rect
                            x="1"
                            y="1"
                            width={dimensions.width - 2}
                            height={dimensions.height - 2}
                            rx={cornerRadius}
                            ry={cornerRadius}
                            fill="none"
                            stroke="var(--blueprint)"
                            strokeWidth="3"
                            opacity={isHovered ? 0.15 : 0}
                            filter="url(#blueprint-glow)"
                            style={{
                                transition: "opacity 0.2s ease-out",
                            }}
                        />

                        {/* Main animated stroke - draws around the full button */}
                        <rect
                            x="1"
                            y="1"
                            width={dimensions.width - 2}
                            height={dimensions.height - 2}
                            rx={cornerRadius}
                            ry={cornerRadius}
                            fill="none"
                            stroke="var(--blueprint)"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeDasharray={pathLength}
                            strokeDashoffset={isHovered ? 0 : pathLength}
                            filter={isHovered ? "url(#blueprint-glow)" : "none"}
                            style={{
                                transition: "stroke-dashoffset 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), filter 0.2s ease-out",
                            }}
                        />

                        {/* Inner crisp stroke for sharpness */}
                        <rect
                            x="1"
                            y="1"
                            width={dimensions.width - 2}
                            height={dimensions.height - 2}
                            rx={cornerRadius}
                            ry={cornerRadius}
                            fill="none"
                            stroke="var(--blueprint)"
                            strokeWidth="1"
                            strokeLinecap="round"
                            strokeDasharray={pathLength}
                            strokeDashoffset={isHovered ? 0 : pathLength}
                            opacity={isHovered ? 1 : 0}
                            style={{
                                transition: "stroke-dashoffset 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) 0.05s, opacity 0.15s ease-out",
                            }}
                        />
                    </svg>
                )}

                {/* Corner Registration Marks */}
                {showCorners && (
                    <>
                        {/* Top-left corner */}
                        <div className={cn(
                            "absolute -top-1 -left-1 w-3 h-3",
                            "border-t border-l border-[var(--blueprint)]",
                            "opacity-0 group-hover:opacity-100",
                            "transition-opacity duration-200"
                        )} />

                        {/* Top-right corner */}
                        <div className={cn(
                            "absolute -top-1 -right-1 w-3 h-3",
                            "border-t border-r border-[var(--blueprint)]",
                            "opacity-0 group-hover:opacity-100",
                            "transition-opacity duration-200 delay-75"
                        )} />

                        {/* Bottom-left corner */}
                        <div className={cn(
                            "absolute -bottom-1 -left-1 w-3 h-3",
                            "border-b border-l border-[var(--blueprint)]",
                            "opacity-0 group-hover:opacity-100",
                            "transition-opacity duration-200 delay-100"
                        )} />

                        {/* Bottom-right corner */}
                        <div className={cn(
                            "absolute -bottom-1 -right-1 w-3 h-3",
                            "border-b border-r border-[var(--blueprint)]",
                            "opacity-0 group-hover:opacity-100",
                            "transition-opacity duration-200 delay-150"
                        )} />
                    </>
                )}

                {/* Button Content */}
                <span className="relative z-10 flex items-center gap-2">
                    {children}
                </span>

                {/* Ink Press Overlay */}
                <div
                    className={cn(
                        "absolute inset-0 rounded-[var(--radius-sm)]",
                        "bg-[var(--ink)] opacity-0",
                        "transition-opacity duration-100",
                        isPressed && "opacity-5"
                    )}
                />
            </button>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT BUTTON VARIANTS FOR COMMON USE CASES
   ══════════════════════════════════════════════════════════════════════════════ */

// Primary action button
export function PrimaryButton({ children, ...props }: Omit<BlueprintButtonProps, "variant">) {
    return (
        <BlueprintButton variant="primary" {...props}>
            {children}
        </BlueprintButton>
    );
}

// Secondary/outline button
export function SecondaryButton({ children, ...props }: Omit<BlueprintButtonProps, "variant">) {
    return (
        <BlueprintButton variant="secondary" {...props}>
            {children}
        </BlueprintButton>
    );
}

// Ghost/text button
export function GhostButton({ children, ...props }: Omit<BlueprintButtonProps, "variant">) {
    return (
        <BlueprintButton variant="ghost" showCorners={false} showPencilStroke={false} {...props}>
            {children}
        </BlueprintButton>
    );
}

// Icon-only button
export function IconButton({
    children,
    label,
    ...props
}: Omit<BlueprintButtonProps, "size"> & { label?: string }) {
    return (
        <BlueprintButton
            variant="ghost"
            size="sm"
            showCorners={false}
            showPencilStroke={false}
            className="!px-2 !h-8 !w-8"
            label={label}
            {...props}
        >
            {children}
        </BlueprintButton>
    );
}

export default BlueprintButton;
