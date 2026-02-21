"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

interface ProgressProps {
  value: number;
  max?: number;
  size?: "sm" | "md";
  showLabel?: boolean;
  className?: string;
}

export function Progress({
  value,
  max = 100,
  size = "md",
  showLabel = false,
  className,
}: ProgressProps) {
  const fillRef = useRef<HTMLDivElement>(null);

  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  useEffect(() => {
    if (!fillRef.current) return;

    gsap.to(fillRef.current, {
      width: `${percentage}%`,
      duration: 0.6,
      ease: "power2.out",
    });
  }, [percentage]);

  const heightStyles = {
    sm: "h-[4px]",
    md: "h-[8px]",
  };

  return (
    <div className={`w-full ${className || ""}`}>
      <div
        className={`w-full bg-[var(--bg-canvas)] rounded-full overflow-hidden ${heightStyles[size]}`}
      >
        <div
          ref={fillRef}
          className="h-full bg-[var(--rf-charcoal)] rounded-full"
          style={{ width: 0 }}
        />
      </div>
      {showLabel && (
        <div className="mt-1.5 flex justify-between items-center">
          <span className="text-[12px] text-[var(--ink-3)] font-['DM_Sans',system-ui,sans-serif]">
            {Math.round(percentage)}%
          </span>
          <span className="text-[12px] text-[var(--ink-3)] font-['DM_Sans',system-ui,sans-serif]">
            {value} / {max}
          </span>
        </div>
      )}
    </div>
  );
}
