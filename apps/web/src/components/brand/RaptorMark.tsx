"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface RaptorMarkProps {
  size?: number;
  className?: string;
  "aria-label"?: string;
}

export function RaptorMark({
  size = 32,
  className,
  "aria-label": ariaLabel = "RaptorFlow",
}: RaptorMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0", className)}
      aria-label={ariaLabel}
      role="img"
    >
      <rect
        x="2"
        y="2"
        width="28"
        height="28"
        rx="6"
        fill="currentColor"
        className="text-[#2a2622]"
      />
      <path d="M16 8L24 16L16 24L8 16Z" fill="#d97757" />
      <circle cx="16" cy="16" r="3" fill="#fbf8f2" />
    </svg>
  );
}
