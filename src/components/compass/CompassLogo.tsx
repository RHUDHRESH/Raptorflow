"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";

interface CompassLogoProps {
  size?: number;
  className?: string;
  animate?: boolean;
  variant?: "default" | "compact" | "micro" | "minimal" | "mark";
}

export function CompassLogo({
  size = 48,
  className = "",
  animate = true,
  variant = "default",
}: CompassLogoProps) {
  const containerRef = useRef<SVGSVGElement>(null);
  const needleRef = useRef<SVGPathElement>(null);
  const pulseRef = useRef<SVGCircleElement>(null);

  useEffect(() => {
    if (!animate || !containerRef.current) return;

    const ctx = gsap.context(() => {
      // Initial compass needle orientation - pointing North
      gsap.set(needleRef.current, { transformOrigin: "50% 50%" });

      // Subtle breathing animation for the pulse ring
      if (pulseRef.current) {
        gsap.to(pulseRef.current, {
          attr: { r: 42 },
          opacity: 0,
          duration: 2,
          repeat: -1,
          ease: "power2.out",
        });
      }

      // Gentle needle sway - like a real compass finding north
      const swayTl = gsap.timeline({ repeat: -1, yoyo: true });
      swayTl.to(needleRef.current, {
        rotation: 3,
        duration: 3,
        ease: "sine.inOut",
      });
      swayTl.to(needleRef.current, {
        rotation: -3,
        duration: 3,
        ease: "sine.inOut",
      });

      // On hover, speed up the sway
      containerRef.current?.addEventListener("mouseenter", () => {
        gsap.to(swayTl, { timeScale: 2, duration: 0.3 });
      });
      containerRef.current?.addEventListener("mouseleave", () => {
        gsap.to(swayTl, { timeScale: 1, duration: 0.3 });
      });
    }, containerRef);

    return () => ctx.revert();
  }, [animate]);

  const normalizedVariant =
    variant === "minimal" ? "compact" : variant === "mark" ? "micro" : variant;
  const isMicro = normalizedVariant === "micro";
  const viewBox = isMicro ? "0 0 32 32" : "0 0 100 100";
  const center = isMicro ? 16 : 50;
  const radius = isMicro ? 14 : 40;
  const strokeWidth = isMicro ? 1.5 : 2;

  return (
    <svg
      ref={containerRef}
      width={size}
      height={size}
      viewBox={viewBox}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`${className}`}
      aria-label="RaptorFlow Compass"
    >
      {/* Outer ring - subtle gradient */}
      <circle
        cx={center}
        cy={center}
        r={radius}
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeOpacity={0.9}
        fill="none"
      />

      {/* Inner decorative ring */}
      <circle
        cx={center}
        cy={center}
        r={radius - (isMicro ? 4 : 8)}
        stroke="currentColor"
        strokeWidth={isMicro ? 0.5 : 1}
        strokeOpacity={0.2}
        fill="none"
        strokeDasharray={isMicro ? "2 2" : "4 4"}
      />

      {/* Cardinal markers */}
      <g opacity={0.6}>
        <line
          x1={center}
          y1={center - radius + (isMicro ? 3 : 6)}
          x2={center}
          y2={center - radius + (isMicro ? 6 : 14)}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
      </g>

      {/* Animated pulse ring (only on larger variants) */}
      {!isMicro && (
        <circle
          ref={pulseRef}
          cx={center}
          cy={center}
          r={38}
          stroke="currentColor"
          strokeWidth={1}
          fill="none"
          opacity={0.3}
        />
      )}

      {/* The Needle - Modern minimalist single pointer design */}
      <g ref={needleRef} style={{ transformOrigin: `${center}px ${center}px` }}>
        {/* Needle shaft - diamond shape, thicker body */}
        <path
          d={
            isMicro
              ? `M${center} ${center - 10} L${center + 3} ${center} L${center} ${center + 8} L${center - 3} ${center} Z`
              : `M${center} ${center - 32} L${center + 8} ${center} L${center} ${center + 24} L${center - 8} ${center} Z`
          }
          fill="currentColor"
        />
        
        {/* Center pivot */}
        <circle
          cx={center}
          cy={center}
          r={isMicro ? 2 : 5}
          fill="var(--bg-canvas, #EFEDE6)"
          stroke="currentColor"
          strokeWidth={strokeWidth}
        />
        
        {/* Inner pivot dot */}
        <circle
          cx={center}
          cy={center}
          r={isMicro ? 1 : 2.5}
          fill="currentColor"
        />
      </g>
    </svg>
  );
}

// Static version for SSR/pre-rendered content
export function CompassLogoStatic({
  size = 48,
  className = "",
  variant = "default",
}: Omit<CompassLogoProps, "animate">) {
  const normalizedVariant =
    variant === "minimal" ? "compact" : variant === "mark" ? "micro" : variant;
  const isMicro = normalizedVariant === "micro";
  const viewBox = isMicro ? "0 0 32 32" : "0 0 100 100";
  const center = isMicro ? 16 : 50;
  const radius = isMicro ? 14 : 40;
  const strokeWidth = isMicro ? 1.5 : 2;

  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <circle
        cx={center}
        cy={center}
        r={radius}
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeOpacity={0.9}
        fill="none"
      />
      <circle
        cx={center}
        cy={center}
        r={radius - (isMicro ? 4 : 8)}
        stroke="currentColor"
        strokeWidth={isMicro ? 0.5 : 1}
        strokeOpacity={0.2}
        fill="none"
        strokeDasharray={isMicro ? "2 2" : "4 4"}
      />
      <g opacity={0.6}>
        <line
          x1={center}
          y1={center - radius + (isMicro ? 3 : 6)}
          x2={center}
          y2={center - radius + (isMicro ? 6 : 14)}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
      </g>
      <g>
        <path
          d={
            isMicro
              ? `M${center} ${center - 10} L${center + 3} ${center} L${center} ${center + 8} L${center - 3} ${center} Z`
              : `M${center} ${center - 32} L${center + 8} ${center} L${center} ${center + 24} L${center - 8} ${center} Z`
          }
          fill="currentColor"
        />
        <circle
          cx={center}
          cy={center}
          r={isMicro ? 2 : 5}
          fill="var(--bg-canvas, #EFEDE6)"
          stroke="currentColor"
          strokeWidth={strokeWidth}
        />
        <circle cx={center} cy={center} r={isMicro ? 1 : 2.5} fill="currentColor" />
      </g>
    </svg>
  );
}
