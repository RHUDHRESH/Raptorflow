"use client";

import React, { ReactNode, forwardRef, HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT CARD — Architectural Drawing Style Container
   Features:
   - Registration marks on all 4 corners
   - Figure annotation (FIG. 01, FIG. 02)
   - Section title with underline rule
   - Blueprint grid background option
   - Ink bleed shadow system
   - Technical measurement annotations
   ══════════════════════════════════════════════════════════════════════════════ */

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
    showCorners = true,
    showMeasurements = false,
    variant = "default",
    padding = "md",
    ...props
}, ref) => {
    const paddingClasses = { none: "", sm: "p-4", md: "p-6", lg: "p-8" };
    const variantClasses = {
        default: "bg-[var(--paper)] ink-bleed-sm",
        elevated: "bg-[var(--paper)] ink-bleed-md",
        inset: "bg-[var(--canvas)] ink-press",
    };

    // Ensure consistent alignment using design tokens
    const alignmentClasses = cn(
        "flex flex-col",
        padding === "none" ? "" : "gap-md"
    );

    return (
        <div
            ref={ref}
            className={cn(
                "relative rounded-[var(--radius-md)] border border-[var(--border)]",
                "transition-all duration-300",
                "group",
                variantClasses[variant],
                showGrid && "blueprint-grid",
                paddingClasses[padding],
                alignmentClasses,
                className
            )}
            {...props}
        >
            {/* Registration Corner Marks */}
            {showCorners && (
                <>
                    <div className="absolute -top-px -left-px w-4 h-4 pointer-events-none">
                        <div className="absolute top-0 left-0 w-full h-px bg-[var(--blueprint)]" />
                        <div className="absolute top-0 left-0 h-full w-px bg-[var(--blueprint)]" />
                        <div className="absolute top-[6px] left-0 w-1.5 h-px bg-[var(--blueprint)] opacity-50" />
                        <div className="absolute top-0 left-[6px] w-px h-1.5 bg-[var(--blueprint)] opacity-50" />
                    </div>
                    <div className="absolute -top-px -right-px w-4 h-4 pointer-events-none">
                        <div className="absolute top-0 right-0 w-full h-px bg-[var(--blueprint)]" />
                        <div className="absolute top-0 right-0 h-full w-px bg-[var(--blueprint)]" />
                        <div className="absolute top-[6px] right-0 w-1.5 h-px bg-[var(--blueprint)] opacity-50" />
                        <div className="absolute top-0 right-[6px] w-px h-1.5 bg-[var(--blueprint)] opacity-50" />
                    </div>
                    <div className="absolute -bottom-px -left-px w-4 h-4 pointer-events-none">
                        <div className="absolute bottom-0 left-0 w-full h-px bg-[var(--blueprint)]" />
                        <div className="absolute bottom-0 left-0 h-full w-px bg-[var(--blueprint)]" />
                        <div className="absolute bottom-[6px] left-0 w-1.5 h-px bg-[var(--blueprint)] opacity-50" />
                        <div className="absolute bottom-0 left-[6px] w-px h-1.5 bg-[var(--blueprint)] opacity-50" />
                    </div>
                    <div className="absolute -bottom-px -right-px w-4 h-4 pointer-events-none">
                        <div className="absolute bottom-0 right-0 w-full h-px bg-[var(--blueprint)]" />
                        <div className="absolute bottom-0 right-0 h-full w-px bg-[var(--blueprint)]" />
                        <div className="absolute bottom-[6px] right-0 w-1.5 h-px bg-[var(--blueprint)] opacity-50" />
                        <div className="absolute bottom-0 right-[6px] w-px h-1.5 bg-[var(--blueprint)] opacity-50" />
                    </div>
                </>
            )}

            {/* Figure Annotation */}
            {figure && (
                <div className="absolute -top-6 left-0 flex items-center gap-2">
                    <span className="font-technical text-[var(--blueprint)]">{figure}</span>
                    <div className="h-px w-8 bg-[var(--blueprint-line)]" />
                </div>
            )}

            {/* Code Badge */}
            {code && (
                <div className="absolute top-3 right-3">
                    <span className="font-technical text-[var(--blueprint)] bg-[var(--blueprint-light)] px-2 py-0.5 rounded-[var(--radius-xs)]">
                        {code}
                    </span>
                </div>
            )}

            {/* Title */}
            {title && (
                <div className="mb-4">
                    <h3 className="font-serif text-lg text-[var(--ink)] mb-2">{title}</h3>
                    <div className="h-px bg-gradient-to-r from-[var(--blueprint)] via-[var(--blueprint-line)] to-transparent" />
                </div>
            )}

            {/* Measurements */}
            {showMeasurements && (
                <>
                    <div className="absolute left-0 top-1/2 -translate-x-full -translate-y-1/2 flex flex-col items-end gap-6 pr-2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="flex items-center gap-1">
                                <span className="font-technical text-[8px] text-[var(--muted)]">{(i + 1) * 24}</span>
                                <div className="w-2 h-px bg-[var(--blueprint-line)]" />
                            </div>
                        ))}
                    </div>
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full flex items-start gap-6 pt-2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="flex flex-col items-center gap-1">
                                <div className="h-2 w-px bg-[var(--blueprint-line)]" />
                                <span className="font-technical text-[8px] text-[var(--muted)]">{(i + 1) * 24}</span>
                            </div>
                        ))}
                    </div>
                </>
            )}

            {/* Card Content */}
            <div className="relative z-10">{children}</div>

            {/* Hover border highlight */}
            <div className="absolute inset-0 rounded-[var(--radius-md)] border border-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        </div>
    );
});

BlueprintCard.displayName = "BlueprintCard";

/* ══════════════════════════════════════════════════════════════════════════════
   CARD SECTION
   ══════════════════════════════════════════════════════════════════════════════ */

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
                    <span className="font-technical text-[var(--muted)]">{title}</span>
                    <div className="flex-1 h-px bg-[var(--border-subtle)]" />
                </div>
            )}
            <div>{children}</div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   CARD FOOTER
   ══════════════════════════════════════════════════════════════════════════════ */

interface CardFooterProps {
    children: ReactNode;
    className?: string;
}

export function CardFooter({ children, className }: CardFooterProps) {
    return (
        <div className={cn(
            "mt-6 pt-4 border-t border-[var(--border-subtle)]",
            "flex items-center gap-2",
            className
        )}>
            <div className="w-6 h-px bg-[var(--blueprint-line)]" />
            <div className="flex-1">{children}</div>
        </div>
    );
}

export default BlueprintCard;
