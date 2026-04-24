"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(useGSAP);
}

interface GsapBridgeProps {
  children: React.ReactNode;
  className?: string;
  animation?: (
    tl: gsap.core.Timeline,
    container: React.MutableRefObject<HTMLDivElement | null>,
  ) => void;
  stagger?: boolean;
  duration?: number;
  staggerDelay?: number;
  y?: number;
}

export function GsapBridge({
  children,
  className,
  animation,
  stagger = false,
  duration = 0.7,
  staggerDelay = 0.08,
  y = 16,
}: GsapBridgeProps) {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const tl = gsap.timeline();

      if (animation && container.current) {
        animation(tl, container);
      } else if (stagger && container.current) {
        // Default stagger reveals for any element with .gsap-reveal inside
        tl.fromTo(
          ".gsap-reveal",
          { y, opacity: 0, visibility: "hidden" },
          {
            y: 0,
            opacity: 1,
            visibility: "visible",
            duration,
            ease: "power3.out",
            stagger: staggerDelay,
          },
        );
      }
    },
    { scope: container },
  );

  return (
    <div ref={container} className={className}>
      {children}
    </div>
  );
}

/**
 * PageTransition — Wraps page content with a smooth entrance animation.
 */
export function PageTransition({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (container.current) {
        gsap.fromTo(
          container.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" },
        );
      }
    },
    { scope: container },
  );

  return (
    <div ref={container} className={className}>
      {children}
    </div>
  );
}

/**
 * FadeIn — Simple fade-in wrapper for individual elements.
 */
export function FadeIn({
  children,
  className,
  delay = 0,
  duration = 0.7,
  y = 16,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  duration?: number;
  y?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (ref.current) {
        gsap.fromTo(
          ref.current,
          { opacity: 0, y },
          { opacity: 1, y: 0, duration, delay, ease: "power3.out" },
        );
      }
    },
    { scope: ref },
  );

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
