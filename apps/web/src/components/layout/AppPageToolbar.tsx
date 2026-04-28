"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface AppPageToolbarProps {
  children: React.ReactNode;
  className?: string;
}

export function AppPageToolbar({ children, className }: AppPageToolbarProps) {
  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-3 mb-6 p-3 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)]",
        className,
      )}
    >
      {children}
    </div>
  );
}
