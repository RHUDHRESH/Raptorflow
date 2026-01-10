"use client";

import { ReactNode } from "react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   SETTINGS SECTION CARD — Paper Terminal Style
   ══════════════════════════════════════════════════════════════════════════════ */

interface SettingsSectionCardProps {
    title: string;
    description?: string;
    children: ReactNode;
    footer?: ReactNode;
    className?: string;
}

export function SettingsSectionCard({
    title,
    description,
    children,
    footer,
    className,
}: SettingsSectionCardProps) {
    return (
        <BlueprintCard
            title={title}
            subtitle={description}
            className={cn("", className)}
        >
            <div className="space-y-4">
                {children}
            </div>
            {footer && (
                <div className="flex items-center justify-end gap-3 border-t border-[var(--structure)] mt-6 pt-4">
                    {footer}
                </div>
            )}
        </BlueprintCard>
    );
}
