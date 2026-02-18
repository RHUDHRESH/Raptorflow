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
    default: "bg-[#EFEDE6] text-[#5C565B]",
    success: "bg-[#E8F0E9] text-[#3D5A42]",
    warning: "bg-[#F5F0E6] text-[#8B6B3D]",
    error: "bg-[#F5E6E6] text-[#8B3D3D]",
    info: "bg-[#E6F0F5] text-[#3D5A6B]",
  };

  const dotColors = {
    default: "bg-[#5C565B]",
    success: "bg-[#3D5A42]",
    warning: "bg-[#8B6B3D]",
    error: "bg-[#8B3D3D]",
    info: "bg-[#3D5A6B]",
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
