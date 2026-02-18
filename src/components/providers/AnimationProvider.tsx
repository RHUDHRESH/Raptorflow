"use client";

import { createContext, useContext, useEffect, useRef, useCallback } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register GSAP plugins
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

interface AnimationContextType {
  pageTransition: (direction?: "in" | "out") => gsap.core.Timeline;
  fadeInUp: (element: string | Element, delay?: number) => void;
  staggerChildren: (container: string | Element, childSelector: string) => void;
  prefersReducedMotion: boolean;
}

const AnimationContext = createContext<AnimationContextType | null>(null);

export function AnimationProvider({ children }: { children: React.ReactNode }) {
  const reducedMotionRef = useRef(false);

  useEffect(() => {
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    reducedMotionRef.current = mediaQuery.matches;

    const handleChange = (e: MediaQueryListEvent) => {
      reducedMotionRef.current = e.matches;
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  /**
   * Page transition animation - slide + fade effect
   * Creates a timeline for smooth page transitions
   */
  const pageTransition = useCallback((direction: "in" | "out" = "in"): gsap.core.Timeline => {
    const tl = gsap.timeline();
    
    if (reducedMotionRef.current) {
      // Simple fade for reduced motion
      if (direction === "in") {
        tl.fromTo("body", { opacity: 0.8 }, { opacity: 1, duration: 0.2 });
      } else {
        tl.fromTo("body", { opacity: 1 }, { opacity: 0.8, duration: 0.2 });
      }
      return tl;
    }

    if (direction === "in") {
      // Incoming page: opacity 0→1, y: 20→0, duration 0.4s
      tl.fromTo(
        "main, [data-page-content]",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }
      );
    } else {
      // Outgoing page: opacity 1→0, y: 0→-20, duration 0.3s
      tl.fromTo(
        "main, [data-page-content]",
        { opacity: 1, y: 0 },
        { opacity: 0, y: -20, duration: 0.3, ease: "power2.in" }
      );
    }

    return tl;
  }, []);

  /**
   * Fade in up animation helper
   * Animates a single element with fade + upward movement
   */
  const fadeInUp = useCallback((element: string | Element, delay: number = 0) => {
    if (reducedMotionRef.current) {
      gsap.set(element, { opacity: 1, y: 0 });
      return;
    }

    gsap.fromTo(
      element,
      { opacity: 0, y: 20 },
      { 
        opacity: 1, 
        y: 0, 
        duration: 0.5, 
        delay, 
        ease: "power2.out" 
      }
    );
  }, []);

  /**
   * Stagger children animation helper
   * Animates children of a container with staggered timing
   */
  const staggerChildren = useCallback((container: string | Element, childSelector: string) => {
    if (reducedMotionRef.current) {
      gsap.set(`${container} ${childSelector}`, { opacity: 1, y: 0 });
      return;
    }

    const ctx = gsap.context(() => {
      gsap.fromTo(
        childSelector,
        { opacity: 0, y: 16 },
        {
          opacity: 1,
          y: 0,
          duration: 0.4,
          stagger: 0.08,
          ease: "power2.out",
          scrollTrigger: {
            trigger: container,
            start: "top 85%",
            toggleActions: "play none none reverse",
          },
        }
      );
    }, container as Element);

    return () => ctx.revert();
  }, []);

  // Set GSAP defaults for smooth 60fps animations
  useEffect(() => {
    gsap.defaults({
      ease: "power2.out",
      duration: 0.4,
    });
  }, []);

  const value: AnimationContextType = {
    pageTransition,
    fadeInUp,
    staggerChildren,
    prefersReducedMotion: reducedMotionRef.current,
  };

  return (
    <AnimationContext.Provider value={value}>
      {children}
    </AnimationContext.Provider>
  );
}

/**
 * Hook to access animation context
 * Must be used within AnimationProvider
 */
export function useAnimation() {
  const context = useContext(AnimationContext);
  if (!context) {
    throw new Error("useAnimation must be used within AnimationProvider");
  }
  return context;
}
