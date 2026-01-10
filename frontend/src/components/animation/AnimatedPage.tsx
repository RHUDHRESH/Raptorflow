"use client";

import { useRef, useEffect, ReactNode } from "react";
import gsap from "gsap";

interface AnimatedPageProps {
    children: ReactNode;
    className?: string;
}

/**
 * AnimatedPage - Wrapper that provides entrance animations for page content
 * Uses GSAP for smooth, performant animations
 */
export function AnimatedPage({ children, className = "" }: AnimatedPageProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const ctx = gsap.context(() => {
            // Animate the page container
            gsap.fromTo(
                containerRef.current,
                { opacity: 0, y: 12 },
                { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }
            );

            // Animate header (if exists)
            const header = containerRef.current?.querySelector("[data-animate='header']");
            if (header) {
                gsap.fromTo(
                    header,
                    { opacity: 0, y: -8 },
                    { opacity: 1, y: 0, duration: 0.4, delay: 0.1, ease: "power2.out" }
                );
            }

            // Animate cards with stagger
            const cards = containerRef.current?.querySelectorAll("[data-animate='card']");
            if (cards && cards.length > 0) {
                gsap.fromTo(
                    cards,
                    { opacity: 0, y: 16, scale: 0.98 },
                    {
                        opacity: 1,
                        y: 0,
                        scale: 1,
                        duration: 0.45,
                        stagger: 0.06,
                        delay: 0.15,
                        ease: "power2.out"
                    }
                );
            }

            // Animate stats with stagger
            const stats = containerRef.current?.querySelectorAll("[data-animate='stat']");
            if (stats && stats.length > 0) {
                gsap.fromTo(
                    stats,
                    { opacity: 0, y: 12, scale: 0.96 },
                    {
                        opacity: 1,
                        y: 0,
                        scale: 1,
                        duration: 0.4,
                        stagger: 0.08,
                        delay: 0.1,
                        ease: "back.out(1.2)"
                    }
                );
            }

            // Animate list items
            const items = containerRef.current?.querySelectorAll("[data-animate='item']");
            if (items && items.length > 0) {
                gsap.fromTo(
                    items,
                    { opacity: 0, x: -8 },
                    {
                        opacity: 1,
                        x: 0,
                        duration: 0.35,
                        stagger: 0.04,
                        delay: 0.2,
                        ease: "power2.out"
                    }
                );
            }

        }, containerRef);

        return () => ctx.revert();
    }, []);

    return (
        <div ref={containerRef} className={`relative z-10 ${className}`}>
            {children}
        </div>
    );
}

/**
 * AnimatedCard - Individual card with hover animation
 */
export function AnimatedCard({
    children,
    className = "",
    delay = 0
}: {
    children: ReactNode;
    className?: string;
    delay?: number;
}) {
    const cardRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!cardRef.current) return;

        gsap.fromTo(
            cardRef.current,
            { opacity: 0, y: 16, scale: 0.98 },
            {
                opacity: 1,
                y: 0,
                scale: 1,
                duration: 0.45,
                delay: delay,
                ease: "power2.out"
            }
        );
    }, [delay]);

    const handleMouseEnter = () => {
        if (!cardRef.current) return;
        gsap.to(cardRef.current, {
            y: -2,
            boxShadow: "0 10px 30px rgba(0, 0, 0, 0.08)",
            duration: 0.25,
            ease: "power2.out"
        });
    };

    const handleMouseLeave = () => {
        if (!cardRef.current) return;
        gsap.to(cardRef.current, {
            y: 0,
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)",
            duration: 0.25,
            ease: "power2.out"
        });
    };

    return (
        <div
            ref={cardRef}
            className={`card ${className}`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{ opacity: 0 }}
        >
            {children}
        </div>
    );
}

/**
 * AnimatedList - Staggered list animation
 */
export function AnimatedList({
    children,
    className = "",
    staggerDelay = 0.04
}: {
    children: ReactNode;
    className?: string;
    staggerDelay?: number;
}) {
    const listRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!listRef.current) return;

        const items = listRef.current.children;
        if (items.length === 0) return;

        gsap.fromTo(
            items,
            { opacity: 0, x: -12 },
            {
                opacity: 1,
                x: 0,
                duration: 0.35,
                stagger: staggerDelay,
                delay: 0.1,
                ease: "power2.out"
            }
        );
    }, [staggerDelay]);

    return (
        <div ref={listRef} className={className}>
            {children}
        </div>
    );
}

/**
 * FadeInView - Simple fade in wrapper
 */
export function FadeInView({
    children,
    delay = 0,
    direction = "up",
    className = ""
}: {
    children: ReactNode;
    delay?: number;
    direction?: "up" | "down" | "left" | "right";
    className?: string;
}) {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!ref.current) return;

        const fromVars: gsap.TweenVars = { opacity: 0 };
        const toVars: gsap.TweenVars = { opacity: 1, duration: 0.4, delay, ease: "power2.out" };

        switch (direction) {
            case "up":
                fromVars.y = 12;
                toVars.y = 0;
                break;
            case "down":
                fromVars.y = -12;
                toVars.y = 0;
                break;
            case "left":
                fromVars.x = 12;
                toVars.x = 0;
                break;
            case "right":
                fromVars.x = -12;
                toVars.x = 0;
                break;
        }

        gsap.fromTo(ref.current, fromVars, toVars);
    }, [delay, direction]);

    return (
        <div ref={ref} className={className} style={{ opacity: 0 }}>
            {children}
        </div>
    );
}
