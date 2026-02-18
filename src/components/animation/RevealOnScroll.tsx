"use client";

import { useEffect, useRef, ReactNode } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register ScrollTrigger plugin
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

interface RevealOnScrollProps {
  children: ReactNode;
  direction?: "up" | "down" | "left" | "right";
  delay?: number;
  duration?: number;
  distance?: number;
  className?: string;
  once?: boolean;
  threshold?: string;
}

/**
 * RevealOnScroll - Reveals children when scrolled into view
 * 
 * Uses GSAP ScrollTrigger for smooth, performant scroll-based animations
 * Supports multiple directions and customizable timing
 * Respects prefers-reduced-motion
 */
export function RevealOnScroll({
  children,
  direction = "up",
  delay = 0,
  duration = 0.5,
  distance = 30,
  className = "",
  once = true,
  threshold = "top 85%",
}: RevealOnScrollProps) {
  const elementRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<ScrollTrigger | null>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (prefersReducedMotion) {
      gsap.set(element, { opacity: 1, x: 0, y: 0 });
      return;
    }

    // Determine animation direction
    const fromVars: gsap.TweenVars = { opacity: 0 };
    
    switch (direction) {
      case "up":
        fromVars.y = distance;
        break;
      case "down":
        fromVars.y = -distance;
        break;
      case "left":
        fromVars.x = distance;
        break;
      case "right":
        fromVars.x = -distance;
        break;
    }

    // Set initial state
    gsap.set(element, fromVars);

    // Create scroll-triggered animation
    const animation = gsap.to(element, {
      opacity: 1,
      x: 0,
      y: 0,
      duration,
      delay,
      ease: "power2.out",
      scrollTrigger: {
        trigger: element,
        start: threshold,
        toggleActions: once ? "play none none none" : "play reverse play reverse",
        onEnter: (self) => {
          triggerRef.current = self;
        },
      },
    });

    return () => {
      animation.kill();
      if (triggerRef.current) {
        triggerRef.current.kill();
      }
    };
  }, [direction, delay, duration, distance, once, threshold]);

  return (
    <div ref={elementRef} className={className}>
      {children}
    </div>
  );
}
