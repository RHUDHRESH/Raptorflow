"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

export type SignalTone = "amber" | "success" | "danger" | "neutral";

interface SignalDotProps {
  tone?: SignalTone;
  pulse?: boolean;
  label?: string;
  className?: string;
}

const toneMap: Record<SignalTone, string> = {
  amber: "bg-[var(--primary)] shadow-[0_0_0_3px_rgba(217,119,87,0.18)]",
  success: "bg-[var(--leaf-confirm)] shadow-[0_0_0_3px_rgba(92,138,90,0.18)]",
  danger: "bg-[var(--destructive)] shadow-[0_0_0_3px_rgba(196,74,63,0.18)]",
  neutral: "bg-[var(--ink-400)] shadow-none",
};

export function SignalDot({ tone = "amber", pulse = false, label, className }: SignalDotProps) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <span
        className={cn(
          "inline-block w-2 h-2 rounded-full",
          toneMap[tone],
          pulse && "animate-[amberPulse_2.4s_cubic-bezier(0.4,0,0.2,1)_infinite]",
        )}
        aria-hidden={!label}
        aria-label={label}
      />
      {label && <span className="text-[11px] text-[var(--ink-500)]">{label}</span>}
    </span>
  );
}
