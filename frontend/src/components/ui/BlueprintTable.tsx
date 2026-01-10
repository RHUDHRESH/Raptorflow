"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT TABLE — Technical Data Table
   Features:
   - Grid lines that feel architectural
   - Row numbers like technical specifications
   - Column headers in technical caps
   - Zebra striping with paper texture
   - Ink bleed shadows
   - Registration corner marks
   ══════════════════════════════════════════════════════════════════════════════ */

export interface Column<T> {
    key: keyof T | string;
    header: string;
    code?: string; // e.g., "COL-01"
    width?: string;
    align?: "left" | "center" | "right";
    render?: (value: unknown, row: T, index: number) => React.ReactNode;
}

interface BlueprintTableProps<T> {
    data: T[];
    columns: Column<T>[];
    figure?: string; // e.g., "FIG. 05"
    title?: string;
    showRowNumbers?: boolean;
    showCorners?: boolean;
    showGrid?: boolean;
    emptyMessage?: string;
    className?: string;
    onRowClick?: (row: T, index: number) => void;
}

export function BlueprintTable<T extends Record<string, unknown>>({
    data,
    columns,
    figure,
    title,
    showRowNumbers = true,
    showCorners = true,
    showGrid = true,
    emptyMessage = "No data available",
    className,
    onRowClick,
}: BlueprintTableProps<T>) {
    const getValue = (row: T, key: keyof T | string): unknown => {
        if (typeof key === "string" && key.includes(".")) {
            return key.split(".").reduce((obj: unknown, k) => {
                return (obj as Record<string, unknown>)?.[k];
            }, row);
        }
        return row[key as keyof T];
    };

    return (
        <div className={cn("relative", className)}>
            {/* Figure annotation */}
            {figure && (
                <div className="flex items-center gap-3 mb-4">
                    <span className="font-technical text-[var(--blueprint)]">{figure}</span>
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    {title && (
                        <span className="font-technical text-[var(--muted)]">{title.toUpperCase()}</span>
                    )}
                </div>
            )}

            {/* Table container */}
            <div className={cn(
                "relative overflow-hidden rounded-[var(--radius-md)] border border-[var(--border)]",
                "bg-[var(--paper)] ink-bleed-sm"
            )}>
                {/* Corner marks */}
                {showCorners && (
                    <>
                        <div className="absolute -top-px -left-px w-4 h-4 border-t border-l border-[var(--blueprint)] z-10" />
                        <div className="absolute -top-px -right-px w-4 h-4 border-t border-r border-[var(--blueprint)] z-10" />
                        <div className="absolute -bottom-px -left-px w-4 h-4 border-b border-l border-[var(--blueprint)] z-10" />
                        <div className="absolute -bottom-px -right-px w-4 h-4 border-b border-r border-[var(--blueprint)] z-10" />
                    </>
                )}

                {/* Blueprint grid background */}
                {showGrid && (
                    <div className="absolute inset-0 blueprint-grid opacity-30 pointer-events-none" />
                )}

                <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                        {/* Header */}
                        <thead>
                            <tr className="border-b-2 border-[var(--border)]">
                                {/* Row number column */}
                                {showRowNumbers && (
                                    <th className="w-12 px-3 py-3 text-left bg-[var(--canvas)]">
                                        <span className="font-technical text-[var(--muted)]">#</span>
                                    </th>
                                )}

                                {columns.map((col) => (
                                    <th
                                        key={String(col.key)}
                                        className={cn(
                                            "px-4 py-3 bg-[var(--canvas)] border-l border-[var(--border-subtle)] first:border-l-0",
                                            col.align === "center" && "text-center",
                                            col.align === "right" && "text-right"
                                        )}
                                        style={{ width: col.width }}
                                    >
                                        <div className="flex items-center gap-2">
                                            <span className="font-technical text-[var(--ink)]">
                                                {col.header.toUpperCase()}
                                            </span>
                                            {col.code && (
                                                <span className="font-technical text-[8px] text-[var(--blueprint)] bg-[var(--blueprint-light)] px-1 py-0.5 rounded-[var(--radius-xs)]">
                                                    {col.code}
                                                </span>
                                            )}
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>

                        {/* Body */}
                        <tbody>
                            {data.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={columns.length + (showRowNumbers ? 1 : 0)}
                                        className="px-4 py-12 text-center"
                                    >
                                        <span className="font-technical text-[var(--muted)]">
                                            {emptyMessage.toUpperCase()}
                                        </span>
                                    </td>
                                </tr>
                            ) : (
                                data.map((row, rowIndex) => (
                                    <tr
                                        key={rowIndex}
                                        className={cn(
                                            "border-b border-[var(--border-subtle)] last:border-b-0",
                                            "transition-colors duration-150",
                                            rowIndex % 2 === 0 ? "bg-[var(--paper)]" : "bg-[var(--canvas-elevated)]",
                                            onRowClick && "cursor-pointer hover:bg-[var(--blueprint-light)]"
                                        )}
                                        onClick={() => onRowClick?.(row, rowIndex)}
                                    >
                                        {/* Row number */}
                                        {showRowNumbers && (
                                            <td className="w-12 px-3 py-3 border-r border-[var(--border-subtle)]">
                                                <span className="font-technical text-[var(--muted)]">
                                                    {String(rowIndex + 1).padStart(2, "0")}
                                                </span>
                                            </td>
                                        )}

                                        {columns.map((col) => {
                                            const value = getValue(row, col.key);
                                            return (
                                                <td
                                                    key={String(col.key)}
                                                    className={cn(
                                                        "px-4 py-3 border-l border-[var(--border-subtle)] first:border-l-0",
                                                        "text-sm text-[var(--ink)]",
                                                        col.align === "center" && "text-center",
                                                        col.align === "right" && "text-right"
                                                    )}
                                                >
                                                    {col.render
                                                        ? col.render(value, row, rowIndex)
                                                        : String(value ?? "—")}
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Footer with row count */}
                <div className="px-4 py-2 bg-[var(--canvas)] border-t border-[var(--border)] flex items-center justify-between">
                    <span className="font-technical text-[var(--muted)]">
                        ROWS: {data.length.toString().padStart(3, "0")}
                    </span>
                    <div className="flex items-center gap-1">
                        {[...Array(Math.min(10, Math.ceil(data.length / 10)))].map((_, i) => (
                            <div
                                key={i}
                                className={cn(
                                    "w-1 bg-[var(--blueprint-line)]",
                                    i === 0 ? "h-3" : "h-1.5"
                                )}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   TABLE CELL HELPERS
   ══════════════════════════════════════════════════════════════════════════════ */

interface CellBadgeProps {
    children: React.ReactNode;
    variant?: "default" | "success" | "warning" | "error" | "info";
}

export function CellBadge({ children, variant = "default" }: CellBadgeProps) {
    const variants = {
        default: "bg-[var(--canvas)] text-[var(--ink)] border-[var(--border)]",
        success: "bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]/20",
        warning: "bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]/20",
        error: "bg-[var(--error-light)] text-[var(--error)] border-[var(--error)]/20",
        info: "bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/20",
    };

    return (
        <span className={cn(
            "inline-flex items-center px-2 py-0.5 rounded-[var(--radius-xs)]",
            "font-technical text-[10px] border",
            variants[variant]
        )}>
            {children}
        </span>
    );
}

interface CellCodeProps {
    children: React.ReactNode;
}

export function CellCode({ children }: CellCodeProps) {
    return (
        <code className="font-mono text-xs text-[var(--blueprint)] bg-[var(--blueprint-light)] px-1.5 py-0.5 rounded-[var(--radius-xs)]">
            {children}
        </code>
    );
}

interface CellProgressProps {
    value: number;
    max?: number;
}

export function CellProgress({ value, max = 100 }: CellProgressProps) {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100));

    return (
        <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-[var(--canvas)] rounded-full overflow-hidden border border-[var(--border-subtle)]">
                <div
                    className="h-full bg-[var(--blueprint)] transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                />
            </div>
            <span className="font-technical text-[10px] text-[var(--muted)] w-8">
                {Math.round(percentage)}%
            </span>
        </div>
    );
}

export default BlueprintTable;
