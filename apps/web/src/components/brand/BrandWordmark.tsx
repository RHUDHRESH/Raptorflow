"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface BrandWordmarkProps {
  size?: number;
  className?: string;
  "aria-label"?: string;
}

export function BrandWordmark({
  size = 120,
  className,
  "aria-label": ariaLabel = "RaptorFlow",
}: BrandWordmarkProps) {
  return (
    <svg
      width={size}
      height={size * 0.25}
      viewBox="0 0 200 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0", className)}
      aria-label={ariaLabel}
      role="img"
    >
      <text
        x="0"
        y="28"
        fontFamily="'Instrument Serif', 'DM Serif Display', ui-serif, serif"
        fontSize="28"
        fill="currentColor"
        letterSpacing="-0.02em"
        className="text-[#2a2622]"
      >
        RaptorFlow
      </text>
      <circle cx="188" cy="20" r="5" fill="#d97757" />
    </svg>
  );
}
