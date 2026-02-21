"use client";

import React from "react";

interface BadgeProps {
  variant?: "default" | "success" | "warning" | "error" | "info";
  size?: "sm" | "md";
  children: React.ReactNode;
  dot?: boolean;
}

export function Badge({
  variant = "default",
  size = "md",
  children,
  dot = true,
}: BadgeProps) {
  const baseStyles =
    "inline-flex items-center gap-1.5 font-semibold uppercase tracking-wide";

  const sizeStyles = {
    sm: "h-[20px] px-1.5 text-[10px] rounded-[8px]",
    md: "h-[24px] px-2 text-[10px] rounded-[10px]",
  };

  const variantStyles = {
    default: "bg-[var(--state-selected)] text-[var(--ink-2)]",
    success: "bg-[var(--status-success-bg)] text-[var(--status-success)]",
    warning: "bg-[var(--status-warning-bg)] text-[var(--status-warning)]",
    error: "bg-[var(--status-error-bg)] text-[var(--status-error)]",
    info: "bg-[var(--status-info-bg)] text-[var(--status-info)]",
  };

  const dotColors = {
    default: "bg-[var(--ink-2)]",
    success: "bg-[var(--status-success)]",
    warning: "bg-[var(--status-warning)]",
    error: "bg-[var(--status-error)]",
    info: "bg-[var(--status-info)]",
  };

  return (
    <span
      className={`
        ${baseStyles}
        ${sizeStyles[size]}
        ${variantStyles[variant]}
        font-['JetBrains_Mono',monospace]
      `}
    >
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`}
        />
      )}
      {children}
    </span>
  );
}
