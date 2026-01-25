"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   STAT CARD — Modern Dashboard Statistics
   Large display numbers with optional trend indicators and icons
   ══════════════════════════════════════════════════════════════════════════════ */

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: {
    value: number;
    label: string;
    direction: "up" | "down" | "neutral";
  };
  icon?: React.ElementType;
  className?: string;
  variant?: "default" | "accent" | "success" | "warning";
}

export function StatCard({
  label,
  value,
  trend,
  icon: Icon,
  className,
  variant = "default",
}: StatCardProps) {
  const variantStyles = {
    default: "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/20 dark:text-indigo-400",
    accent: "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400",
    success: "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400",
    warning: "bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400",
  };

  const iconColor = variantStyles[variant];

  return (
    <div className={cn("card-diffused p-6 relative overflow-hidden group animate-fade-in", className)}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex flex-col gap-1">
          <span className="text-sm font-medium text-ink-muted uppercase tracking-wider">{label}</span>
          <h3 className="text-3xl font-bold text-ink tracking-tight mt-1 group-hover:scale-105 transition-transform origin-left duration-300">
            {value}
          </h3>
        </div>
        {Icon && (
          <div className={cn("p-2.5 rounded-xl transition-all duration-300 group-hover:scale-110 shadow-sm", iconColor)}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      {trend && (
        <div className="flex items-center gap-2 mt-2">
          {trend.direction === "up" && <ArrowUpRight className="w-4 h-4 text-emerald-500" />}
          {trend.direction === "down" && <ArrowDownRight className="w-4 h-4 text-red-500" />}
          {trend.direction === "neutral" && <Minus className="w-4 h-4 text-slate-400" />}
          <span className="text-sm text-slate-600 dark:text-slate-400">
            {trend.value}% {trend.label}
          </span>
        </div>
      )}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   STAT CARD ROW — Grid of stat cards
   ══════════════════════════════════════════════════════════════════════════════ */

interface StatCardRowProps {
  children: React.ReactNode;
  columns?: 2 | 3 | 4 | 5;
  className?: string;
}

export function StatCardRow({ children, columns = 4, className }: StatCardRowProps) {
    const gridCols = {
        2: "grid-cols-1 sm:grid-cols-2",
        3: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
        4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4",
        5: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-5",
    };

    return (
        <div className={cn("grid gap-4", gridCols[columns], className)}>
            {children}
        </div>
    );
}
