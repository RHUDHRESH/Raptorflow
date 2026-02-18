"use client";

import { gsap } from "gsap";

// Register GSAP plugins if needed (for scroll trigger, etc.)
export const initGSAP = () => {
  // Configure GSAP defaults
  gsap.config({
    nullTargetWarn: false,
  });
  
  // Set default ease
  gsap.defaults({
    ease: "power3.out",
    duration: 0.6,
  });
};

// Custom easings
export const customEase = {
  // Smooth exit - fast start, slow end
  smoothExit: "power2.inOut",
  // Elastic pop - for buttons
  elasticPop: "back.out(1.7)",
  // Gentle float - for ambient animations
  gentleFloat: "sine.inOut",
  // Sharp snap - for validations
  sharpSnap: "power4.out",
  // Luxury ease - for premium feel
  luxury: "power3.inOut",
};

// Stagger configurations
export const staggerConfig = {
  // Quick cascade
  quick: {
    amount: 0.3,
    from: "start",
    grid: "auto",
  },
  // Slow reveal
  slow: {
    amount: 0.8,
    from: "start",
  },
  // Wave effect
  wave: {
    amount: 0.5,
    from: "center",
  },
  // Random scatter
  scatter: {
    amount: 0.5,
    from: "random",
  },
};

// Animation presets
export const animations = {
  // Fade in from below
  fadeUp: (element: string | Element, delay = 0) =>
    gsap.fromTo(
      element,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.7, delay, ease: "power3.out" }
    ),

  // Fade in from above
  fadeDown: (element: string | Element, delay = 0) =>
    gsap.fromTo(
      element,
      { opacity: 0, y: -30 },
      { opacity: 1, y: 0, duration: 0.7, delay, ease: "power3.out" }
    ),

  // Scale in
  scaleIn: (element: string | Element, delay = 0) =>
    gsap.fromTo(
      element,
      { opacity: 0, scale: 0.9 },
      { opacity: 1, scale: 1, duration: 0.5, delay, ease: "back.out(1.4)" }
    ),

  // Slide from left
  slideLeft: (element: string | Element, delay = 0) =>
    gsap.fromTo(
      element,
      { opacity: 0, x: -50 },
      { opacity: 1, x: 0, duration: 0.6, delay, ease: "power3.out" }
    ),

  // Slide from right
  slideRight: (element: string | Element, delay = 0) =>
    gsap.fromTo(
      element,
      { opacity: 0, x: 50 },
      { opacity: 1, x: 0, duration: 0.6, delay, ease: "power3.out" }
    ),

  // Rotate in
  rotateIn: (element: string | Element, delay = 0) =>
    gsap.fromTo(
      element,
      { opacity: 0, rotation: -15, scale: 0.9 },
      { opacity: 1, rotation: 0, scale: 1, duration: 0.8, delay, ease: "back.out(1.7)" }
    ),

  // Character stagger for text
  charReveal: (element: string | Element, delay = 0) =>
    gsap.fromTo(
      element,
      { opacity: 0, y: 20 },
      {
        opacity: 1,
        y: 0,
        duration: 0.4,
        stagger: 0.02,
        delay,
        ease: "power2.out",
      }
    ),

  // Magnetic hover effect
  magneticHover: (element: HTMLElement, strength = 0.3) => {
    const xTo = gsap.quickTo(element, "x", { duration: 0.3, ease: "power2.out" });
    const yTo = gsap.quickTo(element, "y", { duration: 0.3, ease: "power2.out" });

    const handleMouseMove = (e: MouseEvent) => {
      const rect = element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const deltaX = (e.clientX - centerX) * strength;
      const deltaY = (e.clientY - centerY) * strength;
      xTo(deltaX);
      yTo(deltaY);
    };

    const handleMouseLeave = () => {
      xTo(0);
      yTo(0);
    };

    element.addEventListener("mousemove", handleMouseMove);
    element.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      element.removeEventListener("mousemove", handleMouseMove);
      element.removeEventListener("mouseleave", handleMouseLeave);
    };
  },

  // Breathing animation for ambient elements
  breathing: (element: string | Element, intensity = 1) =>
    gsap.to(element, {
      scale: 1 + 0.02 * intensity,
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
    }),

  // Pulse animation
  pulse: (element: string | Element, intensity = 1.05) =>
    gsap.to(element, {
      scale: intensity,
      duration: 0.3,
      yoyo: true,
      repeat: 1,
      ease: "power2.inOut",
    }),

  // Shake animation for errors
  shake: (element: string | Element) =>
    gsap.to(element, {
      x: "+=10",
      duration: 0.1,
      repeat: 5,
      yoyo: true,
      ease: "power2.inOut",
      onComplete: () => {
        gsap.set(element, { x: 0 });
      },
    }),

  // Ripple effect
  ripple: (element: HTMLElement) => {
    const ripple = document.createElement("span");
    ripple.className = "absolute inset-0 rounded-inherit bg-[var(--rf-charcoal)] opacity-10 scale-0";
    element.appendChild(ripple);
    
    return gsap.to(ripple, {
      scale: 2,
      opacity: 0,
      duration: 0.6,
      ease: "power2.out",
      onComplete: () => ripple.remove(),
    });
  },

  // Page transition - slide out
  pageOut: (element: string | Element, direction: "left" | "right" | "up" | "down" = "left") => {
    const directions = {
      left: { x: -100, y: 0 },
      right: { x: 100, y: 0 },
      up: { x: 0, y: -100 },
      down: { x: 0, y: 100 },
    };
    
    return gsap.to(element, {
      ...directions[direction],
      opacity: 0,
      duration: 0.4,
      ease: "power2.in",
    });
  },

  // Page transition - slide in
  pageIn: (element: string | Element, direction: "left" | "right" | "up" | "down" = "right") => {
    const fromDirections = {
      left: { x: -100, y: 0 },
      right: { x: 100, y: 0 },
      up: { x: 0, y: -100 },
      down: { x: 0, y: 100 },
    };
    
    return gsap.fromTo(
      element,
      { ...fromDirections[direction], opacity: 0 },
      { x: 0, y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }
    );
  },

  // Morph path animation
  morphPath: (element: SVGPathElement, path: string, duration = 0.6) =>
    gsap.to(element, {
      attr: { d: path },
      duration,
      ease: "power2.inOut",
    }),

  // Draw SVG line
  drawLine: (element: SVGElement, duration = 1) =>
    gsap.fromTo(
      element,
      { strokeDashoffset: (element as any).getTotalLength?.() || 100 },
      {
        strokeDashoffset: 0,
        duration,
        ease: "power2.inOut",
      }
    ),

  // Counter animation
  counter: (element: HTMLElement, target: number, duration = 1) => {
    const obj = { value: 0 };
    return gsap.to(obj, {
      value: target,
      duration,
      ease: "power2.out",
      onUpdate: () => {
        element.textContent = Math.round(obj.value).toString();
      },
    });
  },

  // Spotlight/highlight effect
  spotlight: (element: string | Element, intensity = 1) =>
    gsap.fromTo(
      element,
      { boxShadow: "0 0 0 rgba(42, 37, 41, 0)" },
      {
        boxShadow: `0 0 ${30 * intensity}px rgba(42, 37, 41, ${0.1 * intensity})`,
        duration: 0.3,
        yoyo: true,
        repeat: 1,
      }
    ),
};

// Create a timeline with preset configuration
export const createTimeline = (defaults?: gsap.TimelineVars) =>
  gsap.timeline({
    defaults: { ease: "power3.out", duration: 0.6, ...defaults },
  });

// Utility: Split text into characters for stagger animation
export const splitText = (text: string): string[] => text.split("");

// Utility: Split text into words
export const splitWords = (text: string): string[] => text.split(" ");

// Utility: Create staggered children animation
export const staggerChildren = (
  container: string | Element,
  childSelector: string,
  animation: gsap.TweenVars,
  staggerAmount = 0.05
) =>
  gsap.fromTo(
    `${container} ${childSelector}`,
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, stagger: staggerAmount, ...animation }
  );

// Performance optimization: Pause animations when tab is hidden
if (typeof document !== "undefined") {
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      gsap.globalTimeline.pause();
    } else {
      gsap.globalTimeline.resume();
    }
  });
}
