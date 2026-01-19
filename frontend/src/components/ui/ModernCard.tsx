"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MODERN CARD — Clean elevated cards with soft shadows
   ══════════════════════════════════════════════════════════════════════════════ */

interface ModernCardProps {
    children: ReactNode;
    className?: string;
    padding?: "none" | "sm" | "md" | "lg";
    hover?: boolean;
    onClick?: () => void;
}

export function ModernCard({
    children,
    className,
    padding = "md",
    hover = false,
    onClick,
}: ModernCardProps) {
    const paddingClasses = {
        none: "",
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
    };

    return (
        <div
            className={cn(
                "bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800",
                "shadow-sm transition-all duration-300",
                hover && "hover:shadow-lg hover:-translate-y-1 cursor-pointer",
                onClick && "cursor-pointer",
                paddingClasses[padding],
                className
            )}
            onClick={onClick}
        >
            {children}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   MODERN CARD HEADER
   ══════════════════════════════════════════════════════════════════════════════ */

interface ModernCardHeaderProps {
    title: string;
    subtitle?: string;
    action?: ReactNode;
    icon?: ReactNode;
    className?: string;
}

export function ModernCardHeader({
    title,
    subtitle,
    action,
    icon,
    className,
}: ModernCardHeaderProps) {
    return (
        <div className={cn("flex items-center justify-between mb-6", className)}>
            <div className="flex items-center gap-3">
                {icon && (
                    <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center text-slate-600 dark:text-slate-300">
                        {icon}
                    </div>
                )}
                <div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                        {title}
                    </h3>
                    {subtitle && (
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                            {subtitle}
                        </p>
                    )}
                </div>
            </div>
            {action && <div>{action}</div>}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   MODERN CARD FOOTER
   ══════════════════════════════════════════════════════════════════════════════ */

interface ModernCardFooterProps {
    children: ReactNode;
    className?: string;
    border?: boolean;
}

export function ModernCardFooter({
    children,
    className,
    border = true,
}: ModernCardFooterProps) {
    return (
        <div
            className={cn(
                "pt-4 mt-4",
                border && "border-t border-slate-200 dark:border-slate-800",
                className
            )}
        >
            {children}
        </div>
    );
}
