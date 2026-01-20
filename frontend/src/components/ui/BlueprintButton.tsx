"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { Button, ButtonProps } from "@/components/ui/button";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT BUTTON — Refactored for Quiet Luxury
   Features:
   - Solid, reliable construction (no "pencil animations")
   - Subtle "Tech Marks" (corners) for the Blueprint feel
   - Strict adherence to Ink and Foundation colors
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintButtonProps extends ButtonProps {
    showCorners?: boolean;
    label?: string; // Technical label like "BTN-01"
}

export function BlueprintButton({
    className,
    children,
    variant = "default",
    size = "default",
    showCorners = false,
    label,
    ...props
}: BlueprintButtonProps) {
    if (props.asChild) {
        return (
            <Button
                variant={variant}
                size={size}
                className={cn(
                    "relative overflow-visible",
                    className
                )}
                {...props}
            >
                {children}
            </Button>
        );
    }

    const buttonContent = (
        <Button
            variant={variant}
            size={size}
            className={cn(
                "relative overflow-visible", // Allow corners to sit outside if needed
                className
            )}
            {...props}
        >
            {/* Corner Registration Marks - Pure CSS, no SVGs */}
            {showCorners && (
                <>
                    <span className="absolute -top-[1px] -left-[1px] w-2 h-2 border-t border-l border-current opacity-30 group-hover:opacity-100 transition-opacity" />
                    <span className="absolute -top-[1px] -right-[1px] w-2 h-2 border-t border-r border-current opacity-30 group-hover:opacity-100 transition-opacity" />
                    <span className="absolute -bottom-[1px] -left-[1px] w-2 h-2 border-b border-l border-current opacity-30 group-hover:opacity-100 transition-opacity" />
                    <span className="absolute -bottom-[1px] -right-[1px] w-2 h-2 border-b border-r border-current opacity-30 group-hover:opacity-100 transition-opacity" />
                </>
            )}

            {children}
        </Button>
    );

    return (
        <div className="relative inline-flex flex-col items-start gap-1 group">
            {/* Technical Label - Top Left (Optional) */}
            {label && (
                <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground opacity-60 group-hover:opacity-100 transition-opacity absolute -top-4 left-0">
                    {label}
                </span>
            )}
            {buttonContent}
        </div>
    );
}

// Re-export specific variants for backward compatibility or ease of use
export function PrimaryButton(props: ButtonProps) {
    return <BlueprintButton variant="default" {...props} />;
}

export function SecondaryButton(props: ButtonProps) {
    return <BlueprintButton variant="secondary" {...props} />;
}

export function GhostButton(props: ButtonProps) {
    return <BlueprintButton variant="ghost" {...props} />;
}

export function IconButton(props: ButtonProps) {
    return <BlueprintButton size="icon" variant="ghost" {...props} />;
}

export default BlueprintButton;
