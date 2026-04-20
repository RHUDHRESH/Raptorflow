"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

// ─── Section Label (eyebrow) ──────────────────────────────────────────────────
export function SectionLabel({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <p
      className={cn(
        "text-xs uppercase tracking-[0.28em] text-[#D97757] font-mono font-bold",
        className
      )}
    >
      {children}
    </p>
  );
}

// ─── Amber Button ─────────────────────────────────────────────────────────────
export function AmberButton({
  href,
  children,
  className,
  onClick,
}: {
  href?: string;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}) {
  const base =
    "inline-flex items-center justify-center gap-2 bg-[#D97757] text-[#2A2622] font-semibold text-sm px-7 py-3 hover:bg-[#C46A4D] transition-colors duration-200 rounded-none";
  if (href) {
    return (
      <a href={href} className={cn(base, className)}>
        {children}
      </a>
    );
  }
  return (
    <button onClick={onClick} className={cn(base, className)}>
      {children}
    </button>
  );
}

// ─── Ghost Button ─────────────────────────────────────────────────────────────
export function GhostButton({
  href,
  children,
  className,
}: {
  href?: string;
  children: React.ReactNode;
  className?: string;
}) {
  const base =
    "inline-flex items-center justify-center gap-2 border border-[#E5DED4] text-[#6B655E] font-medium text-sm px-7 py-3 hover:bg-[#F5F0E8] hover:border-[#D5CBC0] transition-colors duration-200 rounded-none";
  if (href) {
    return (
      <a href={href} className={cn(base, className)}>
        {children}
      </a>
    );
  }
  return <button className={cn(base, className)}>{children}</button>;
}

// ─── Diagram Card ─────────────────────────────────────────────────────────────
export function DiagramCard({
  children,
  className,
  glowAmber,
}: {
  children: React.ReactNode;
  className?: string;
  glowAmber?: boolean;
}) {
  return (
    <div
      className={cn(
        "bg-white border border-[#E5DED4] rounded-2xl p-5",
        glowAmber && "border-[#D97757]/40 shadow-[0_0_32px_rgba(217,119,87,0.12)]",
        className
      )}
    >
      {children}
    </div>
  );
}

// ─── Metric Pill ──────────────────────────────────────────────────────────────
export function MetricPill({
  label,
  value,
  className,
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-3 bg-[#F5F0E8] border border-[#E5DED4] px-4 py-2 rounded-full",
        className
      )}
    >
      <span className="text-xs font-mono text-[#9A948C] uppercase tracking-widest">
        {label}
      </span>
      <span className="text-sm font-semibold text-[#D97757]">{value}</span>
    </div>
  );
}

// ─── Amber Line ───────────────────────────────────────────────────────────────
export function AmberLine({
  className,
  vertical,
}: {
  className?: string;
  vertical?: boolean;
}) {
  return (
    <div
      className={cn(
        "bg-[#D97757]/50",
        vertical ? "w-px h-full" : "h-px w-full",
        className
      )}
    />
  );
}
