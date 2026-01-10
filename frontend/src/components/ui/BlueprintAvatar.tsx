"use client";

import React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT AVATAR — Technical User Representation
   Features:
   - Registration corner marks
   - Status indicator
   - Multiple sizes
   - Ink bleed shadows
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintAvatarProps {
    src?: string | null;
    alt?: string;
    initials?: string;
    size?: "xs" | "sm" | "md" | "lg" | "xl";
    status?: "online" | "offline" | "busy" | "away";
    showCorner?: boolean;
    className?: string;
}

export function BlueprintAvatar({
    src,
    alt,
    initials,
    size = "md",
    status,
    showCorner = true,
    className,
}: BlueprintAvatarProps) {
    const sizeClasses = {
        xs: "w-6 h-6 text-[9px]",
        sm: "w-8 h-8 text-[10px]",
        md: "w-10 h-10 text-xs",
        lg: "w-14 h-14 text-sm",
        xl: "w-20 h-20 text-lg",
    };

    const statusColors = {
        online: "bg-[var(--success)]",
        offline: "bg-[var(--muted)]",
        busy: "bg-[var(--error)]",
        away: "bg-[var(--warning)]",
    };

    const statusSizes = {
        xs: "w-1.5 h-1.5",
        sm: "w-2 h-2",
        md: "w-2.5 h-2.5",
        lg: "w-3 h-3",
        xl: "w-4 h-4",
    };

    return (
        <div className={cn("relative inline-flex group", className)}>
            {/* Avatar */}
            <div
                className={cn(
                    "rounded-[var(--radius-sm)] bg-[var(--blueprint-light)] flex items-center justify-center",
                    "text-[var(--blueprint)] font-semibold ink-bleed-sm overflow-hidden",
                    "transition-transform duration-300 group-hover:scale-105",
                    sizeClasses[size]
                )}
            >
                {src ? (
                    <Image
                        src={src}
                        alt={alt || "Avatar"}
                        fill
                        className="object-cover"
                        sizes="40px"
                    />
                ) : (
                    <span className="font-technical">{initials || "?"}</span>
                )}
            </div>

            {/* Registration corner mark */}
            {showCorner && (
                <div className="absolute -top-0.5 -right-0.5 w-2 h-2 border-t border-r border-[var(--blueprint)]" />
            )}

            {/* Status indicator */}
            {status && (
                <span
                    className={cn(
                        "absolute bottom-0 right-0 rounded-full border-2 border-[var(--paper)] z-10",
                        statusColors[status],
                        statusSizes[size]
                    )}
                />
            )}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   AVATAR GROUP
   ══════════════════════════════════════════════════════════════════════════════ */

interface AvatarGroupProps {
    avatars: { src?: string; initials?: string }[];
    max?: number;
    size?: BlueprintAvatarProps["size"];
    className?: string;
}

export function AvatarGroup({ avatars, max = 4, size = "sm", className }: AvatarGroupProps) {
    const visible = avatars.slice(0, max);
    const remaining = avatars.length - max;

    return (
        <div className={cn("flex -space-x-2", className)}>
            {visible.map((avatar, i) => (
                <BlueprintAvatar
                    key={i}
                    src={avatar.src}
                    initials={avatar.initials}
                    size={size}
                    showCorner={false}
                    className="ring-2 ring-[var(--paper)]"
                />
            ))}
            {remaining > 0 && (
                <div
                    className={cn(
                        "flex items-center justify-center rounded-[var(--radius-sm)]",
                        "bg-[var(--canvas)] border border-[var(--border)]",
                        "text-[var(--muted)] font-technical ring-2 ring-[var(--paper)]",
                        size === "xs" && "w-6 h-6 text-[8px]",
                        size === "sm" && "w-8 h-8 text-[9px]",
                        size === "md" && "w-10 h-10 text-[10px]",
                        size === "lg" && "w-14 h-14 text-xs",
                        size === "xl" && "w-20 h-20 text-sm"
                    )}
                >
                    +{remaining}
                </div>
            )}
        </div>
    );
}

export default BlueprintAvatar;
