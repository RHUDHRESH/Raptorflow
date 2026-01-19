"use client";

import { useEffect } from "react";
import gsap from "gsap";

// Register GSAP plugins if needed
// gsap.registerPlugin(ScrollTrigger);

/**
 * Hook for staggered entrance animation on mount
 */
export function useStaggeredEntrance(
    containerRef: React.RefObject<HTMLElement | null>,
    selector: string = ".stagger-item",
    options: {
        y?: number;
        opacity?: number;
        stagger?: number;
        duration?: number;
        delay?: number;
    } = {}
) {
    const {
        y = 6,
        opacity = 0,
        stagger = 0.05,
        duration = 0.4,
        delay = 0.1
    } = options;

    useEffect(() => {
        if (!containerRef.current) return;

        const items = containerRef.current.querySelectorAll(selector);
        if (items.length === 0) return;

        const ctx = gsap.context(() => {
            gsap.fromTo(
                items,
                { y, opacity },
                {
                    y: 0,
                    opacity: 1,
                    duration,
                    stagger,
                    delay,
                    ease: "power2.out"
                }
            );
        }, containerRef);

        return () => ctx.revert();
    }, [containerRef, selector, y, opacity, stagger, duration, delay]);
}

/**
 * Hook for header + content cascade animation
 */
export function useHeaderCascade(
    headerRef: React.RefObject<HTMLElement | null>,
    contentRef: React.RefObject<HTMLElement | null>
) {
    useEffect(() => {
        if (!headerRef.current || !contentRef.current) return;

        const ctx = gsap.context(() => {
            const tl = gsap.timeline();

            // Header enters first
            tl.fromTo(
                headerRef.current,
                { opacity: 0, y: -10 },
                { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }
            );

            // Content follows
            tl.fromTo(
                contentRef.current,
                { opacity: 0 },
                { opacity: 1, duration: 0.3, ease: "power2.out" },
                "-=0.2"
            );
        });

        return () => ctx.revert();
    }, [headerRef, contentRef]);
}

/**
 * Hook for card completion animation
 */
export function useCompletionAnimation() {
    const animateCompletion = (element: HTMLElement) => {
        gsap.to(element, {
            opacity: 0.7,
            scale: 0.98,
            duration: 0.3,
            ease: "power2.out"
        });
    };

    const animateRestore = (element: HTMLElement) => {
        gsap.to(element, {
            opacity: 1,
            scale: 1,
            duration: 0.3,
            ease: "power2.out"
        });
    };

    return { animateCompletion, animateRestore };
}

/**
 * Standalone function for timeline animations
 */
export function createEntranceTimeline(container: HTMLElement, items: string) {
    const tl = gsap.timeline();

    tl.fromTo(
        container.querySelectorAll(items),
        { opacity: 0, y: 8 },
        {
            opacity: 1,
            y: 0,
            duration: 0.4,
            stagger: 0.05,
            ease: "power2.out"
        }
    );

    return tl;
}
