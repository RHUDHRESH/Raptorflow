"use client";

import { ButtonHTMLAttributes, forwardRef, ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   MODERN BUTTON — Clean, accessible buttons with variants
   ══════════════════════════════════════════════════════════════════════════════ */

interface ModernButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost" | "danger" | "success";
    size?: "sm" | "md" | "lg";
    loading?: boolean;
    icon?: ReactNode;
    iconPosition?: "left" | "right";
}

export const ModernButton = forwardRef<HTMLButtonElement, ModernButtonProps>(
    (
        {
            children,
            variant = "primary",
            size = "md",
            loading = false,
            icon,
            iconPosition = "left",
            className,
            disabled,
            ...props
        },
        ref
    ) => {
        const variants = {
            primary: "bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 shadow-sm hover:shadow-md",
            secondary: "bg-white dark:bg-slate-800 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700",
            ghost: "bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white",
            danger: "bg-red-500 text-white hover:bg-red-600 shadow-sm hover:shadow-md",
            success: "bg-emerald-500 text-white hover:bg-emerald-600 shadow-sm hover:shadow-md",
        };

        const sizes = {
            sm: "px-3 py-1.5 text-xs gap-1.5",
            md: "px-4 py-2.5 text-sm gap-2",
            lg: "px-6 py-3 text-base gap-2",
        };

        return (
            <button
                ref={ref}
                className={cn(
                    "inline-flex items-center justify-center font-medium rounded-xl",
                    "transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                    variants[variant],
                    sizes[size],
                    className
                )}
                disabled={disabled || loading}
                {...props}
            >
                {loading && <Loader2 size={16} className="animate-spin" />}
                {!loading && icon && iconPosition === "left" && icon}
                {children}
                {!loading && icon && iconPosition === "right" && icon}
            </button>
        );
    }
);

ModernButton.displayName = "ModernButton";

/* ══════════════════════════════════════════════════════════════════════════════
   ICON BUTTON — Circular icon-only button
   ══════════════════════════════════════════════════════════════════════════════ */

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    icon: ReactNode;
    variant?: "primary" | "secondary" | "ghost";
    size?: "sm" | "md" | "lg";
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
    ({ icon, variant = "ghost", size = "md", className, ...props }, ref) => {
        const variants = {
            primary: "bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100",
            secondary: "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700",
            ghost: "bg-transparent text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white",
        };

        const sizes = {
            sm: "w-8 h-8",
            md: "w-10 h-10",
            lg: "w-12 h-12",
        };

        return (
            <button
                ref={ref}
                className={cn(
                    "inline-flex items-center justify-center rounded-xl",
                    "transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                    variants[variant],
                    sizes[size],
                    className
                )}
                {...props}
            >
                {icon}
            </button>
        );
    }
);

IconButton.displayName = "IconButton";

/* ══════════════════════════════════════════════════════════════════════════════
   BUTTON GROUP — Group of related buttons
   ══════════════════════════════════════════════════════════════════════════════ */

interface ButtonGroupProps {
    children: ReactNode;
    className?: string;
}

export function ButtonGroup({ children, className }: ButtonGroupProps) {
    return (
        <div className={cn("inline-flex items-center gap-1", className)}>
            {children}
        </div>
    );
}
