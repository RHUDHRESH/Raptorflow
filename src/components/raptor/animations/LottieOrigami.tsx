"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

interface LottieOrigamiProps {
  size?: number;
  color?: string;
  animate?: boolean;
  className?: string;
}

/**
 * Origami Bird Animation Component
 * 
 * RaptorFlow's mascot - appears in:
 * - Loading states (subtle flap)
 * - Empty states (minimal)
 * - Lock emblem (tiny seal)
 * 
 * Rare usage like a seal, not a screaming mascot.
 */
export function LottieOrigami({
  size = 48,
  color = "currentColor",
  animate = true,
  className = "",
}: LottieOrigamiProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wingsRef = useRef<SVGPathElement>(null);
  const bodyRef = useRef<SVGPathElement>(null);

  useEffect(() => {
    if (!animate || !wingsRef.current || !bodyRef.current) return;

    // Gentle floating animation
    const tl = gsap.timeline({ repeat: -1, yoyo: true });

    // Body subtle float
    tl.to(
      bodyRef.current,
      {
        y: -2,
        duration: 2,
        ease: "sine.inOut",
      },
      0
    );

    // Wings gentle flap
    tl.to(
      wingsRef.current,
      {
        scaleY: 0.95,
        transformOrigin: "center",
        duration: 1,
        ease: "sine.inOut",
      },
      0
    );

    return () => {
      tl.kill();
    };
  }, [animate]);

  return (
    <div
      ref={containerRef}
      className={`inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Origami Bird - Geometric, Clean */}
        <g stroke={color} strokeWidth="1.5" strokeLinejoin="round">
          {/* Left Wing */}
          <path
            ref={wingsRef}
            d="M24 8L8 40L24 32V8Z"
            fill={color}
            fillOpacity="0.1"
          />
          
          {/* Right Wing */}
          <path
            d="M24 8L40 40L24 32V8Z"
            fill={color}
            fillOpacity="0.2"
          />
          
          {/* Body / Fold line */}
          <path
            ref={bodyRef}
            d="M24 8V32"
            strokeLinecap="round"
          />
          
          {/* Tail detail */}
          <path
            d="M18 36L24 32L30 36"
            fill="none"
            strokeLinecap="round"
          />
        </g>
      </svg>
    </div>
  );
}

/**
 * Loading Spinner with Origami Bird
 */
export function LoadingOrigami({
  size = 64,
  message = "Loading...",
}: {
  size?: number;
  message?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Rotation animation
    const tl = gsap.timeline({ repeat: -1 });
    
    tl.to(containerRef.current, {
      rotation: 360,
      duration: 2,
      ease: "none",
    });

    return () => {
      tl.kill();
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div
        ref={containerRef}
        className="text-[var(--ink-1)]"
      >
        <svg
          width={size}
          height={size}
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Simplified bird for loading */}
          <path
            d="M24 4L4 44L24 36L44 44L24 4Z"
            fill="currentColor"
            fillOpacity="0.2"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinejoin="round"
          />
          <path
            d="M24 4V36"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </div>
      {message && (
        <span className="rf-body-sm text-[var(--ink-2)]">{message}</span>
      )}
    </div>
  );
}

/**
 * Empty State with Origami Bird
 */
export function EmptyStateOrigami({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="w-16 h-16 mb-6 text-[var(--ink-3)]">
        <svg
          viewBox="0 0 48 48"
          fill="none"
          className="w-full h-full"
        >
          {/* Minimal origami outline */}
          <path
            d="M24 12L12 36L24 30L36 36L24 12Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinejoin="round"
            fill="none"
          />
          <path
            d="M24 12V30"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
      </div>
      <h3 className="rf-h4 text-[var(--ink-1)] mb-2">{title}</h3>
      <p className="rf-body-sm text-[var(--ink-2)] max-w-sm mb-6">
        {description}
      </p>
      {action && (
        <button onClick={action.onClick} className="rf-btn rf-btn-primary">
          {action.label}
        </button>
      )}
    </div>
  );
}

/**
 * Lock Seal - Tiny origami for locked items
 */
export function LockSeal({
  size = 16,
  className = "",
}: {
  size?: number;
  className?: string;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      fill="none"
      className={`inline-block ${className}`}
    >
      {/* Tiny seal mark */}
      <path
        d="M8 2L2 14L8 11L14 14L8 2Z"
        fill="currentColor"
        fillOpacity="0.2"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}
