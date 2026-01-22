"use client";

import React, { ReactNode, forwardRef, HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   BLUEPRINT CARD ΓÇö Architectural Drawing Style Container
   Features:
   - Registration marks on all 4 corners
   - Figure annotation (FIG. 01, FIG. 02)
   - Section title with underline rule
   - Blueprint grid background option
   - Ink bleed shadow system
   - Technical measurement annotations
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface BlueprintCardProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
    className?: string;
    figure?: string;
    title?: string;
    subtitle?: string;
    icon?: ReactNode;
    actions?: ReactNode;
    code?: string;
    showGrid?: boolean;
    showCorners?: boolean;
    showMeasurements?: boolean;
    variant?: "default" | "elevated" | "inset";
    padding?: "none" | "sm" | "md" | "lg";
}

export const BlueprintCard = forwardRef<HTMLDivElement, BlueprintCardProps>(({
    children,
    className,
    figure,
    title,
    subtitle,
    icon,
    actions,
    code,
    showGrid = false,
    showCorners = false,  // Disabled by default for clean Technical Minimalist style
    showMeasurements = false,
    variant = "default",
    padding = "md",
    ...props
}, ref) => {
    const paddingClasses = { none: "", sm: "p-4", md: "p-6", lg: "p-10" };
    const variantClasses = {
        default: "bg-[var(--paper)]", // Shadows removed for flat paper look
        elevated: "bg-[var(--paper)] shadow-card",
        inset: "bg-[var(--surface-hover)] border-transparent",
    };

    // Ensure consistent alignment using design tokens
    const alignmentClasses = cn(
        "flex flex-col",
        padding === "none" ? "" : "gap-6" // Increased gap
    );

    return (
        <div
            ref={ref}
            className={cn(
                "relative rounded-xl border border-[var(--border)]", // rounded-xl for premium feel
                "transition-all duration-300",
                variantClasses[variant],
                showGrid && "bg-grid-blueprint",
                paddingClasses[padding],
                alignmentClasses,
                className
            )}
            {...props}
        >
            {/* Title - clean minimalist style */}
            {title && (
                <div className="mb-4">
                    <h3 className="font-semibold text-base text-[var(--ink)]">{title}</h3>
                    {subtitle && <p className="text-sm text-[var(--ink-secondary)] mt-1">{subtitle}</p>}
                </div>
            )}

            {/* Measurements */}
            {showMeasurements && (
                <>
                    <div className="absolute left-0 top-1/2 -translate-x-full -translate-y-1/2 flex flex-col items-end gap-6 pr-2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="flex items-center gap-1">
                                <span className="font-mono text-[8px] text-[var(--ink-secondary)]">{(i + 1) * 24}</span>
                                <div className="w-2 h-px bg-[var(--structure)]" />
                            </div>
                        ))}
                    </div>
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full flex items-start gap-6 pt-2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="flex flex-col items-center gap-1">
                                <div className="h-2 w-px bg-[var(--structure)]" />
                                <span className="font-mono text-[8px] text-[var(--ink-secondary)]">{(i + 1) * 24}</span>
                            </div>
                        ))}
                    </div>
                </>
            )}

            {/* Card Content */}
            <div className="relative z-10">{children}</div>
        </div>
    );
});

BlueprintCard.displayName = "BlueprintCard";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   CARD SECTION
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface CardSectionProps {
    children: ReactNode;
    title?: string;
    className?: string;
}

export function CardSection({ children, title, className }: CardSectionProps) {
    return (
        <div className={cn("space-y-3", className)}>
            {title && (
                <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px] tracking-widest text-[var(--ink)]/40 uppercase">{title}</span>
                    <div className="flex-1 h-px bg-[var(--structure)]/30" />
                </div>
            )}
            <div>{children}</div>
        </div>
    );
}

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   CARD FOOTER
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface CardFooterProps {
    children: ReactNode;
    className?: string;
}

export function CardFooter({ children, className }: CardFooterProps) {
    return (
        <div className={cn(
            "mt-6 pt-4 border-t border-[var(--structure)]/30",
            "flex items-center gap-2",
            className
        )}>
            <div className="w-6 h-px bg-[var(--structure)]" />
            <div className="flex-1">{children}</div>
        </div>
    );
}

export default BlueprintCard;
