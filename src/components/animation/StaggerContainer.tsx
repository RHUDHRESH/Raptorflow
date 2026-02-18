"use client";

import { useEffect, useRef, ReactNode, Children, isValidElement, cloneElement } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register ScrollTrigger plugin
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

interface StaggerContainerProps {
  children: ReactNode;
  stagger?: number;
  delay?: number;
  duration?: number;
  distance?: number;
  className?: string;
  childClassName?: string;
  triggerOnScroll?: boolean;
  threshold?: string;
}

/**
 * StaggerContainer - Container that staggers entrance of children
 * 
 * Automatically wraps each child with animation capabilities
 * Children animate in sequence with staggered timing
 * Respects prefers-reduced-motion
 */
export function StaggerContainer({
  children,
  stagger = 0.1,
  delay = 0,
  duration = 0.4,
  distance = 20,
  className = "",
  childClassName = "",
  triggerOnScroll = true,
  threshold = "top 85%",
}: StaggerContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<gsap.core.Tween | null>(null);
  const triggerRef = useRef<ScrollTrigger | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Get all direct children
    const childElements = container.querySelectorAll("[data-stagger-child]");
    if (childElements.length === 0) return;

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (prefersReducedMotion) {
      gsap.set(childElements, { opacity: 1, y: 0 });
      return;
    }

    // Set initial state
    gsap.set(childElements, { opacity: 0, y: distance });

    // Create animation
    const tween = gsap.to(childElements, {
      opacity: 1,
      y: 0,
      duration,
      stagger,
      delay,
      ease: "power2.out",
      paused: triggerOnScroll, // Pause if waiting for scroll trigger
      scrollTrigger: triggerOnScroll
        ? {
            trigger: container,
            start: threshold,
            toggleActions: "play none none none",
            onEnter: (self) => {
              triggerRef.current = self;
            },
          }
        : undefined,
    });

    animationRef.current = tween;

    // If not scroll-triggered, play immediately
    if (!triggerOnScroll) {
      tween.play();
    }

    return () => {
      tween.kill();
      if (triggerRef.current) {
        triggerRef.current.kill();
      }
    };
  }, [stagger, delay, duration, distance, triggerOnScroll, threshold]);

  // Wrap children with data attribute for targeting
  const wrappedChildren = Children.map(children, (child, index) => {
    if (!isValidElement(child)) return child;

    return cloneElement(child as React.ReactElement, {
      "data-stagger-child": index,
      className: `${child.props.className || ""} ${childClassName}`.trim(),
    });
  });

  return (
    <div ref={containerRef} className={className}>
      {wrappedChildren}
    </div>
  );
}
