"use client";

import { useEffect, useRef, ReactNode } from "react";
import gsap from "gsap";
import { usePathname } from "next/navigation";

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

/**
 * PageTransition - Wraps page content with GSAP transition animations
 * 
 * Animation specs:
 * - Incoming page: opacity 0→1, y: 20→0, duration 0.4s
 * - Outgoing page: opacity 1→0, y: 0→-20, duration 0.3s
 * - Easing: power2.out
 * 
 * Supports prefers-reduced-motion for accessibility
 */
export function PageTransition({ children, className = "" }: PageTransitionProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
  const prevPathRef = useRef(pathname);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Initial load animation
    if (prevPathRef.current === pathname) {
      if (prefersReducedMotion) {
        gsap.set(container, { opacity: 1, y: 0 });
      } else {
        gsap.fromTo(
          container,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }
        );
      }
      return;
    }

    // Page change animation
    const isNavigatingForward = true; // You can implement logic to detect back/forward

    if (prefersReducedMotion) {
      // Simple fade for reduced motion
      gsap.fromTo(
        container,
        { opacity: 0.8 },
        { opacity: 1, duration: 0.2 }
      );
    } else {
      // Full slide + fade animation
      gsap.fromTo(
        container,
        { opacity: 0, y: 20 },
        { 
          opacity: 1, 
          y: 0, 
          duration: 0.4, 
          ease: "power2.out",
          delay: 0.05 // Slight delay for smooth handoff
        }
      );
    }

    prevPathRef.current = pathname;

    return () => {
      // Cleanup any ongoing animations
      gsap.killTweensOf(container);
    };
  }, [pathname]);

  return (
    <div 
      ref={containerRef} 
      className={className}
      data-page-content
      style={{ opacity: 0 }} // Start hidden to prevent flash
    >
      {children}
    </div>
  );
}
