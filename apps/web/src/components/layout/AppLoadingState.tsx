"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface AppLoadingStateProps {
  label?: string;
  className?: string;
}

export function AppLoadingState({ label = "Loading...", className }: AppLoadingStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16", className)}>
      <div className="relative w-8 h-8 mb-4">
        <span className="absolute inset-0 rounded-full bg-[var(--primary)] opacity-20 animate-ping" />
        <span className="absolute inset-1.5 rounded-full bg-[var(--primary)] opacity-40" />
        <span className="absolute inset-3 rounded-full bg-[var(--primary)]" />
      </div>
      <span className="mono-label">{label}</span>
    </div>
  );
}
