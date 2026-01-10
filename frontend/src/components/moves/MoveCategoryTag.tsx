"use client";

import { cn } from "@/lib/utils";
import { Zap, Target, Crown, Shield, Heart, TrendingUp } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE CATEGORY TAG — Unified category badges for moves
   Sharp, minimal, using RaptorFlow design tokens
   ══════════════════════════════════════════════════════════════════════════════ */

export type MoveCategoryType = "ignite" | "capture" | "authority" | "repair" | "rally" | "pulse";

interface CategoryConfig {
    name: string;
    emoji: string;
    icon: React.ElementType;
    color: string;
    bgColor: string;
}

const CATEGORY_CONFIG: Record<MoveCategoryType, CategoryConfig> = {
    ignite: {
        name: "Ignite",
        emoji: "🔥",
        icon: Zap,
        color: "var(--error)",
        bgColor: "var(--error-light)"
    },
    capture: {
        name: "Capture",
        emoji: "🎯",
        icon: Target,
        color: "var(--blueprint)",
        bgColor: "var(--blueprint-light)"
    },
    authority: {
        name: "Authority",
        emoji: "👑",
        icon: Crown,
        color: "var(--warning)",
        bgColor: "var(--warning-light)"
    },
    repair: {
        name: "Repair",
        emoji: "🔧",
        icon: Shield,
        color: "var(--success)",
        bgColor: "var(--success-light)"
    },
    rally: {
        name: "Rally",
        emoji: "📣",
        icon: Heart,
        color: "var(--blueprint)",
        bgColor: "var(--blueprint-light)"
    },
    pulse: {
        name: "Pulse",
        emoji: "📊",
        icon: TrendingUp,
        color: "var(--ink-secondary)",
        bgColor: "var(--surface)"
    }
};

interface MoveCategoryTagProps {
    category: MoveCategoryType;
    variant?: "default" | "minimal" | "full";
    size?: "sm" | "md" | "lg";
    showIcon?: boolean;
    showEmoji?: boolean;
    className?: string;
}

export function MoveCategoryTag({
    category,
    variant = "default",
    size = "md",
    showIcon = false,
    showEmoji = true,
    className
}: MoveCategoryTagProps) {
    const config = CATEGORY_CONFIG[category];
    const Icon = config.icon;

    const sizeStyles = {
        sm: "h-5 px-1.5 text-[9px] gap-1",
        md: "h-6 px-2 text-[10px] gap-1.5",
        lg: "h-7 px-3 text-xs gap-2"
    };

    const iconSizes = {
        sm: 10,
        md: 12,
        lg: 14
    };

    if (variant === "minimal") {
        return (
            <span
                className={cn(
                    "inline-flex items-center font-technical uppercase tracking-wider",
                    sizeStyles[size],
                    className
                )}
                style={{ color: config.color }}
            >
                {showEmoji && <span className="text-sm">{config.emoji}</span>}
                {config.name}
            </span>
        );
    }

    if (variant === "full") {
        return (
            <div
                className={cn(
                    "inline-flex items-center gap-2 px-3 py-1.5 rounded-[var(--radius)] border",
                    className
                )}
                style={{
                    backgroundColor: config.bgColor,
                    borderColor: config.color,
                    color: config.color
                }}
            >
                {showEmoji && <span className="text-base">{config.emoji}</span>}
                <span className="font-semibold text-sm">{config.name}</span>
                {showIcon && <Icon size={iconSizes[size]} strokeWidth={1.5} />}
            </div>
        );
    }

    // Default: compact badge
    return (
        <span
            className={cn(
                "inline-flex items-center rounded-[var(--radius)] font-technical uppercase tracking-wider border",
                sizeStyles[size],
                className
            )}
            style={{
                backgroundColor: config.bgColor,
                borderColor: `${config.color}40`,
                color: config.color
            }}
        >
            {showEmoji && <span>{config.emoji}</span>}
            {showIcon && <Icon size={iconSizes[size]} strokeWidth={1.5} />}
            <span>{config.name}</span>
        </span>
    );
}

// Export config for use in other components
export { CATEGORY_CONFIG };
