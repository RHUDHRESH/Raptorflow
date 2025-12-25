'use client';

import { useEffect, useRef, ReactNode } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register plugin
if (typeof window !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

// ============================================================================
// SECTION REVEAL - Scroll-triggered section animation wrapper
// ============================================================================

interface SectionRevealProps {
    children: ReactNode;
    className?: string;
    animation?: 'fade-up' | 'fade' | 'scale' | 'blur' | 'slide-left' | 'slide-right';
    delay?: number;
    duration?: number;
    stagger?: number;
    threshold?: number;
}

export function SectionReveal({
    children,
    className = '',
    animation = 'fade-up',
    delay = 0,
    duration = 0.8,
    stagger = 0.1,
    threshold = 0.2,
}: SectionRevealProps) {
    const sectionRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const section = sectionRef.current;
        if (!section) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        // Get children for staggered animations
        const children = section.querySelectorAll(':scope > *');
        const targets = children.length > 0 ? children : [section];

        // Initial states based on animation type
        const initialState: gsap.TweenVars = { opacity: 0 };
        const finalState: gsap.TweenVars = { opacity: 1, duration, delay, stagger };

        switch (animation) {
            case 'fade-up':
                Object.assign(initialState, { y: 60 });
                Object.assign(finalState, { y: 0, ease: 'power3.out' });
                break;
            case 'fade':
                Object.assign(finalState, { ease: 'power2.out' });
                break;
            case 'scale':
                Object.assign(initialState, { scale: 0.9 });
                Object.assign(finalState, { scale: 1, ease: 'power2.out' });
                break;
            case 'blur':
                Object.assign(initialState, { filter: 'blur(20px)', y: 40 });
                Object.assign(finalState, { filter: 'blur(0px)', y: 0, ease: 'power3.out' });
                break;
            case 'slide-left':
                Object.assign(initialState, { x: 100 });
                Object.assign(finalState, { x: 0, ease: 'power3.out' });
                break;
            case 'slide-right':
                Object.assign(initialState, { x: -100 });
                Object.assign(finalState, { x: 0, ease: 'power3.out' });
                break;
        }

        gsap.set(targets, initialState);

        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: section,
                start: `top ${100 - threshold * 100}%`,
                toggleActions: 'play none none reverse',
            },
        });

        tl.to(targets, finalState);

        return () => {
            tl.kill();
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === section) {
                    trigger.kill();
                }
            });
        };
    }, [animation, delay, duration, stagger, threshold]);

    return (
        <div ref={sectionRef} className={className}>
            {children}
        </div>
    );
}

// ============================================================================
// STAGGER REVEAL - Container that staggers children animation
// ============================================================================

interface StaggerRevealProps {
    children: ReactNode;
    className?: string;
    stagger?: number;
    delay?: number;
    direction?: 'up' | 'down' | 'left' | 'right';
}

export function StaggerReveal({
    children,
    className = '',
    stagger = 0.1,
    delay = 0,
    direction = 'up',
}: StaggerRevealProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const items = container.children;

        const initialState: gsap.TweenVars = { opacity: 0 };

        switch (direction) {
            case 'up':
                Object.assign(initialState, { y: 50 });
                break;
            case 'down':
                Object.assign(initialState, { y: -50 });
                break;
            case 'left':
                Object.assign(initialState, { x: 50 });
                break;
            case 'right':
                Object.assign(initialState, { x: -50 });
                break;
        }

        gsap.set(items, initialState);

        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: container,
                start: 'top 85%',
                toggleActions: 'play none none reverse',
            },
        });

        tl.to(items, {
            opacity: 1,
            x: 0,
            y: 0,
            duration: 0.7,
            delay,
            stagger,
            ease: 'power3.out',
        });

        return () => {
            tl.kill();
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === container) {
                    trigger.kill();
                }
            });
        };
    }, [stagger, delay, direction]);

    return (
        <div ref={containerRef} className={className}>
            {children}
        </div>
    );
}

// ============================================================================
// PARALLAX SECTION - Scroll-linked parallax movement
// ============================================================================

interface ParallaxSectionProps {
    children: ReactNode;
    className?: string;
    speed?: number;
    direction?: 'up' | 'down';
}

export function ParallaxSection({
    children,
    className = '',
    speed = 0.3,
    direction = 'up',
}: ParallaxSectionProps) {
    const sectionRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const section = sectionRef.current;
        if (!section) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const yPercent = direction === 'up' ? -30 * speed : 30 * speed;

        gsap.to(section, {
            yPercent,
            ease: 'none',
            scrollTrigger: {
                trigger: section,
                start: 'top bottom',
                end: 'bottom top',
                scrub: true,
            },
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === section) {
                    trigger.kill();
                }
            });
        };
    }, [speed, direction]);

    return (
        <div ref={sectionRef} className={className}>
            {children}
        </div>
    );
}
