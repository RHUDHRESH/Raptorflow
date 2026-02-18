"use client";

import React, { useRef, useEffect } from "react";
import gsap from "gsap";

export type ModeType = "draft" | "locked" | "live";

interface TopBarProps {
  brandName?: string;
  objective?: string;
  mode?: ModeType;
}

const modeConfig: Record<
  ModeType,
  { label: string; bg: string; text: string; border: string }
> = {
  draft: {
    label: "Draft",
    bg: "#F5F0E6",
    text: "#8B6B3D",
    border: "#E8DCC8",
  },
  locked: {
    label: "Locked",
    bg: "#E8F0E9",
    text: "#3D5A42",
    border: "#C8D8CB",
  },
  live: {
    label: "Live",
    bg: "#F3F0E7",
    text: "#2A2529",
    border: "#2A2529",
  },
};

export function TopBar({
  brandName = "Acme Corp",
  objective = "Launch Q1 retention campaign with 15% lift target",
  mode = "draft",
}: TopBarProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const leftRef = useRef<HTMLDivElement>(null);
  const centerRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLDivElement>(null);
  const modeBadgeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initial state
      gsap.set([leftRef.current, centerRef.current, rightRef.current], {
        opacity: 0,
        y: -10,
      });

      gsap.set(modeBadgeRef.current, {
        scale: 0.9,
        opacity: 0,
      });

      // Entrance animation
      gsap.to([leftRef.current, centerRef.current, rightRef.current], {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out",
        stagger: 0.08,
        delay: 0.2,
      });

      gsap.to(modeBadgeRef.current, {
        scale: 1,
        opacity: 1,
        duration: 0.4,
        ease: "back.out(1.7)",
        delay: 0.5,
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  // Mode change animation
  useEffect(() => {
    if (modeBadgeRef.current) {
      gsap.fromTo(
        modeBadgeRef.current,
        { scale: 0.95, opacity: 0.7 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.3,
          ease: "power2.out",
        }
      );
    }
  }, [mode]);

  const currentMode = modeConfig[mode];

  return (
    <header
      ref={containerRef}
      className="flex items-center justify-between px-6 flex-shrink-0"
      style={{
        height: "var(--shell-topbar, 56px)",
        backgroundColor: "var(--bg-canvas, #EFEDE6)",
        borderBottom: "1px solid var(--border-1, #E3DED3)",
      }}
    >
      {/* Left: Brand Name */}
      <div ref={leftRef} className="flex items-center flex-1">
        <span
          className="text-sm font-medium"
          style={{
            color: "var(--ink-1, #2A2529)",
            fontFamily: "'DM Sans', system-ui, sans-serif",
          }}
        >
          {brandName}
        </span>
      </div>

      {/* Center: Objective */}
      <div ref={centerRef} className="flex items-center justify-center flex-1">
        <p
          className="text-sm text-center truncate max-w-md"
          style={{
            color: "var(--ink-2, #5C565B)",
            fontFamily: "'DM Sans', system-ui, sans-serif",
          }}
        >
          {objective}
        </p>
      </div>

      {/* Right: Mode Indicator */}
      <div ref={rightRef} className="flex items-center justify-end flex-1">
        <div
          ref={modeBadgeRef}
          className="flex items-center px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
          style={{
            backgroundColor: currentMode.bg,
            color: currentMode.text,
            border: `1px solid ${currentMode.border}`,
            fontFamily: "'DM Sans', system-ui, sans-serif",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full mr-2"
            style={{
              backgroundColor: currentMode.text,
              animation: mode === "live" ? "pulse 2s infinite" : "none",
            }}
          />
          {currentMode.label}
        </div>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>
    </header>
  );
}
