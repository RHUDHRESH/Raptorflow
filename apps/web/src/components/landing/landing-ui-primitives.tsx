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
        "text-xs uppercase tracking-[0.28em] text-amber-500 font-mono font-bold",
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
    "inline-flex items-center justify-center gap-2 bg-amber-500 text-black font-semibold text-sm px-7 py-3 hover:bg-amber-400 transition-colors duration-200 rounded-none";
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
    "inline-flex items-center justify-center gap-2 border border-zinc-700 text-zinc-300 font-medium text-sm px-7 py-3 hover:bg-zinc-900 hover:border-zinc-600 transition-colors duration-200 rounded-none";
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
        "bg-[#1a1a1a] border border-zinc-800 rounded-2xl p-5",
        glowAmber && "border-amber-500/40 shadow-[0_0_32px_rgba(245,158,11,0.12)]",
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
        "inline-flex items-center gap-3 bg-[#1f1f1f] border border-zinc-800 px-4 py-2 rounded-full",
        className
      )}
    >
      <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">
        {label}
      </span>
      <span className="text-sm font-semibold text-amber-500">{value}</span>
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
        "bg-amber-500/50",
        vertical ? "w-px h-full" : "h-px w-full",
        className
      )}
    />
  );
}
