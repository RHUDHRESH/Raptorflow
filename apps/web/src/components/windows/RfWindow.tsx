"use client";

import * as React from "react";
import { cn } from "@/lib/cn";
import { RfWindowHeader } from "./RfWindowHeader";
import { RfWindowBody } from "./RfWindowBody";

export type WindowVariant = "default" | "highlight" | "quiet" | "danger";
export type WindowDensity = "comfortable" | "compact";

interface RfWindowProps {
  title?: string;
  eyebrow?: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  variant?: WindowVariant;
  density?: WindowDensity;
}

const variantMap: Record<WindowVariant, string> = {
  default: "paper-card",
  highlight: "card-highlight",
  quiet: "bg-[var(--paper-150)] border border-[var(--border)] rounded-[var(--radius-lg)]",
  danger:
    "bg-[var(--destructive-wash)] border border-[var(--destructive)]/20 rounded-[var(--radius-lg)]",
};

export function RfWindow({
  title,
  eyebrow,
  description,
  actions,
  children,
  className,
  variant = "default",
  density = "comfortable",
}: RfWindowProps) {
  const hasHeader = title || eyebrow || description || actions;

  return (
    <div
      className={cn(
        variantMap[variant],
        "overflow-hidden transition-all duration-[240ms]",
        className,
      )}
    >
      {hasHeader && (
        <RfWindowHeader
          eyebrow={eyebrow}
          title={title}
          description={description}
          actions={actions}
        />
      )}
      <RfWindowBody density={density}>{children}</RfWindowBody>
    </div>
  );
}
