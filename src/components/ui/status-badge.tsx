"use client";

import { cn } from "@/lib/utils";

type StatusVariant = "success" | "warning" | "error" | "info" | "pending" | "default" | "active" | "testing" | "archived";

interface StatusBadgeProps {
  variant: StatusVariant;
  children: React.ReactNode;
  size?: "sm" | "md";
  dot?: boolean;
  className?: string;
}

const variantStyles: Record<StatusVariant, string> = {
  success: "bg-[var(--success-light)] text-[var(--status-done)] border-[var(--status-done)]/20",
  warning: "bg-[var(--warning-light)] text-[var(--status-attention)] border-[var(--status-attention)]/20",
  error: "bg-[var(--error-light)] text-[var(--status-blocked)] border-[var(--status-blocked)]/20",
  info: "bg-[var(--blueprint-light)] text-[var(--status-in-progress)] border-[var(--status-in-progress)]/20",
  pending: "bg-[var(--warning-light)] text-[var(--status-attention)] border-[var(--status-attention)]/20",
  default: "bg-[var(--surface)] text-[var(--ink-secondary)] border-[var(--structure)]",
  active: "bg-[var(--success-light)] text-[var(--status-done)] border-[var(--status-done)]/20",
  testing: "bg-[var(--blueprint-light)] text-[var(--status-in-progress)] border-[var(--status-in-progress)]/20",
  archived: "bg-[var(--canvas)] text-[var(--ink-muted)] border-[var(--structure)]",
};

const dotColors: Record<StatusVariant, string> = {
  success: "bg-[var(--status-done)]",
  warning: "bg-[var(--status-attention)]",
  error: "bg-[var(--status-blocked)]",
  info: "bg-[var(--status-in-progress)]",
  pending: "bg-[var(--status-attention)]",
  default: "bg-[var(--ink-muted)]",
  active: "bg-[var(--status-done)]",
  testing: "bg-[var(--status-in-progress)]",
  archived: "bg-[var(--ink-muted)]",
};

export function StatusBadge({
  variant,
  children,
  size = "sm",
  dot = false,
  className,
}: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        size === "sm" && "px-2 py-0.5 text-[11px]",
        size === "md" && "px-2.5 py-1 text-[12px]",
        variantStyles[variant],
        className
      )}
    >
      {dot && (
        <span className={cn("h-1.5 w-1.5 rounded-full", dotColors[variant])} />
      )}
      {children}
    </span>
  );
}
