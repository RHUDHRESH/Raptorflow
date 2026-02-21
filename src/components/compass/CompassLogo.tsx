"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";

interface CompassLogoProps {
  size?: number;
  className?: string;
  animate?: boolean;
  variant?: "default" | "compact" | "micro" | "minimal" | "mark";
}

/**
 * RaptorFlow Logo — Two-triangle navigation pointer
 * Inspired by Google Maps pin. Top triangle = north (primary),
 * bottom triangle = south (secondary), center dot = pivot.
 */
export function CompassLogo({
  size = 48,
  className = "",
  animate = true,
  variant = "default",
}: CompassLogoProps) {
  const containerRef = useRef<SVGSVGElement>(null);
  const pointerRef = useRef<SVGGElement>(null);

  useEffect(() => {
    if (!animate || !containerRef.current || !pointerRef.current) return;

    const ctx = gsap.context(() => {
      gsap.set(pointerRef.current, { transformOrigin: "50% 54%" });

      // Gentle compass-needle sway
      const swayTl = gsap.timeline({ repeat: -1, yoyo: true });
      swayTl.to(pointerRef.current, {
        rotation: 4,
        duration: 3,
        ease: "sine.inOut",
      });
      swayTl.to(pointerRef.current, {
        rotation: -4,
        duration: 3,
        ease: "sine.inOut",
      });

      // Hover: speed up sway
      containerRef.current?.addEventListener("mouseenter", () => {
        gsap.to(swayTl, { timeScale: 2.5, duration: 0.3 });
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

  return (
    <svg
      ref={containerRef}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="RaptorFlow"
    >
      <g ref={pointerRef} style={{ transformOrigin: "12px 13px" }}>
        {/* Top triangle — north / primary */}
        <path
          d="M12 2L18.5 13H5.5L12 2Z"
          fill="currentColor"
        />
        {/* Bottom triangle — south / secondary */}
        <path
          d="M12 22L18.5 13H5.5L12 22Z"
          fill="currentColor"
          opacity={isMicro ? "0.3" : "0.45"}
        />
        {/* Center pivot dot */}
        <circle
          cx="12"
          cy="13"
          r="1.8"
          fill="var(--bg-canvas, #EFEDE6)"
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

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path d="M12 2L18.5 13H5.5L12 2Z" fill="currentColor" />
      <path
        d="M12 22L18.5 13H5.5L12 22Z"
        fill="currentColor"
        opacity={isMicro ? "0.3" : "0.45"}
      />
      <circle cx="12" cy="13" r="1.8" fill="var(--bg-canvas, #EFEDE6)" />
    </svg>
  );
}
