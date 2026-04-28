"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

export type StatusTone = "neutral" | "success" | "warning" | "danger" | "amber" | "muse";

interface StatusPillProps {
  status: string;
  tone?: StatusTone;
  className?: string;
}

const toneMap: Record<StatusTone, string> = {
  neutral: "bg-[var(--paper-200)] text-[var(--ink-700)] border-[var(--paper-300)]",
  success: "bg-[var(--leaf-wash)] text-[var(--leaf)] border-[var(--leaf)]/20",
  warning: "bg-[var(--amber-wash)] text-[var(--primary)] border-[var(--amber-stroke)]/30",
  danger: "bg-[var(--destructive-wash)] text-[var(--destructive)] border-[var(--destructive)]/20",
  amber: "bg-[var(--amber-wash)] text-[var(--primary)] border-[var(--amber-stroke)]/30",
  muse: "bg-[var(--indigo-wash)] text-[var(--indigo-muse)] border-[var(--indigo-muse)]/20",
};

export function StatusPill({ status, tone = "neutral", className }: StatusPillProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border",
        toneMap[tone],
        className,
      )}
    >
      {status}
    </span>
  );
}
