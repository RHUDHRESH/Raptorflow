"use client";

import { useEffect, useCallback } from "react";
import gsap from "gsap";

// ══════════════════════════════════════════════════════════════════════════════
// GSAP Animation Hooks & Utilities - Premium SaaS Animations
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Staggered card entrance animation
 */
export function useStaggerCards(
  containerRef: React.RefObject<HTMLElement | null>,
  selector: string = "[data-animate='card']",
  deps: React.DependencyList = []
) {
  const depsKey = JSON.stringify(deps);

  useEffect(() => {
    if (!containerRef.current) return;

    const cards = containerRef.current.querySelectorAll(selector);
    if (cards.length === 0) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        cards,
        {
          opacity: 0,
          y: 24,
          scale: 0.96,
        },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.5,
          stagger: 0.08,
          ease: "power3.out",
          delay: 0.1,
        }
      );
    }, containerRef);

    return () => ctx.revert();
  }, [containerRef, selector, depsKey]);
}

/**
 * Page entrance animation with header and content
 */
export function usePageEntrance(
  headerRef: React.RefObject<HTMLElement | null>,
  contentRef: React.RefObject<HTMLElement | null>
) {
  useEffect(() => {
    if (!headerRef.current || !contentRef.current) return;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline();

      // Header slides in from top
      tl.fromTo(
        headerRef.current,
        { opacity: 0, y: -20 },
        { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }
      );

      // Content fades in
      tl.fromTo(
        contentRef.current,
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" },
        "-=0.2"
      );
    });

    return () => ctx.revert();
  }, [headerRef, contentRef]);
}

/**
 * Sidebar navigation item animation
 */
export function useSidebarAnimation(
  sidebarRef: React.RefObject<HTMLElement | null>,
  isCollapsed: boolean
) {
  useEffect(() => {
    if (!sidebarRef.current) return;

    const ctx = gsap.context(() => {
      const labels = sidebarRef.current?.querySelectorAll("[data-sidebar-label]");

      if (labels) {
        gsap.to(labels, {
          opacity: isCollapsed ? 0 : 1,
          x: isCollapsed ? -10 : 0,
          duration: 0.2,
          stagger: 0.02,
          ease: "power2.out",
        });
      }
    }, sidebarRef);

    return () => ctx.revert();
  }, [sidebarRef, isCollapsed]);
}

/**
 * Card hover animation
 */
export function useCardHover() {
  const onMouseEnter = useCallback((e: React.MouseEvent<HTMLElement>) => {
    gsap.to(e.currentTarget, {
      y: -4,
      scale: 1.01,
      duration: 0.3,
      ease: "power2.out",
    });
  }, []);

  const onMouseLeave = useCallback((e: React.MouseEvent<HTMLElement>) => {
    gsap.to(e.currentTarget, {
      y: 0,
      scale: 1,
      duration: 0.3,
      ease: "power2.out",
    });
  }, []);

  return { onMouseEnter, onMouseLeave };
}

/**
 * Number counter animation
 */
export function useCounterAnimation(
  elementRef: React.RefObject<HTMLElement | null>,
  targetValue: number,
  duration: number = 1.5
) {
  useEffect(() => {
    if (!elementRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        elementRef.current,
        { innerText: 0 },
        {
          innerText: targetValue,
          duration,
          ease: "power2.out",
          snap: { innerText: 1 },
          onUpdate: function () {
            if (elementRef.current) {
              const val = Math.round(
                parseFloat(elementRef.current.innerText || "0")
              );
              elementRef.current.innerText = val.toLocaleString();
            }
          },
        }
      );
    }, elementRef);

    return () => ctx.revert();
  }, [elementRef, targetValue, duration]);
}

/**
 * Modal/Dialog entrance animation
 */
export function animateModalIn(element: HTMLElement) {
  return gsap.fromTo(
    element,
    {
      opacity: 0,
      scale: 0.95,
      y: 20,
    },
    {
      opacity: 1,
      scale: 1,
      y: 0,
      duration: 0.35,
      ease: "power3.out",
    }
  );
}

/**
 * Modal/Dialog exit animation
 */
export function animateModalOut(element: HTMLElement) {
  return gsap.to(element, {
    opacity: 0,
    scale: 0.95,
    y: 10,
    duration: 0.2,
    ease: "power2.in",
  });
}

/**
 * List item stagger animation
 */
export function animateListItems(
  container: HTMLElement,
  selector: string = "li"
) {
  const items = container.querySelectorAll(selector);
  return gsap.fromTo(
    items,
    { opacity: 0, x: -10 },
    {
      opacity: 1,
      x: 0,
      duration: 0.3,
      stagger: 0.05,
      ease: "power2.out",
    }
  );
}

/**
 * Tab content transition
 */
export function animateTabChange(
  outgoing: HTMLElement | null,
  incoming: HTMLElement
) {
  const tl = gsap.timeline();

  if (outgoing) {
    tl.to(outgoing, {
      opacity: 0,
      y: -10,
      duration: 0.2,
      ease: "power2.in",
    });
  }

  tl.fromTo(
    incoming,
    { opacity: 0, y: 10 },
    { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" },
    outgoing ? "-=0.1" : 0
  );

  return tl;
}

/**
 * Button press animation
 */
export function animateButtonPress(element: HTMLElement) {
  const tl = gsap.timeline();
  tl.to(element, { scale: 0.95, duration: 0.1, ease: "power2.out" });
  tl.to(element, { scale: 1, duration: 0.2, ease: "elastic.out(1, 0.5)" });
  return tl;
}

/**
 * Success checkmark animation
 */
export function animateSuccess(element: HTMLElement) {
  return gsap.fromTo(
    element,
    { scale: 0, rotation: -45 },
    {
      scale: 1,
      rotation: 0,
      duration: 0.5,
      ease: "elastic.out(1, 0.5)",
    }
  );
}

/**
 * Shimmer loading effect
 */
export function createShimmer(element: HTMLElement) {
  return gsap.to(element, {
    backgroundPosition: "200% 0",
    duration: 1.5,
    ease: "none",
    repeat: -1,
  });
}

/**
 * Notification toast animation
 */
export function animateToastIn(element: HTMLElement) {
  return gsap.fromTo(
    element,
    { opacity: 0, y: -20, scale: 0.9 },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.4,
      ease: "back.out(1.7)",
    }
  );
}

export function animateToastOut(element: HTMLElement) {
  return gsap.to(element, {
    opacity: 0,
    y: -10,
    scale: 0.9,
    duration: 0.25,
    ease: "power2.in",
  });
}

/**
 * Chart animation
 */
export function animateChart(
  container: HTMLElement,
  barSelector: string = "[data-bar]"
) {
  const bars = container.querySelectorAll(barSelector);
  return gsap.fromTo(
    bars,
    { scaleY: 0, transformOrigin: "bottom" },
    {
      scaleY: 1,
      duration: 0.6,
      stagger: 0.05,
      ease: "power3.out",
    }
  );
}

/**
 * Progress ring animation
 */
export function animateProgressRing(
  element: SVGCircleElement,
  percentage: number
) {
  const circumference = 2 * Math.PI * parseFloat(element.getAttribute("r") || "0");
  const offset = circumference - (percentage / 100) * circumference;

  return gsap.fromTo(
    element,
    { strokeDashoffset: circumference },
    {
      strokeDashoffset: offset,
      duration: 1,
      ease: "power2.out",
    }
  );
}
