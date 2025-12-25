'use client';

import { createContext, useContext, useEffect, useRef, ReactNode } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

// Register GSAP plugins
if (typeof window !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

// Animation Context
interface AnimationContextType {
    lenis: Lenis | null;
}

const AnimationContext = createContext<AnimationContextType>({ lenis: null });

export function useAnimation() {
    return useContext(AnimationContext);
}

// ============================================================================
// ANIMATION PROVIDER
// ============================================================================

interface AnimationProviderProps {
    children: ReactNode;
}

export function AnimationProvider({ children }: AnimationProviderProps) {
    const lenisRef = useRef<Lenis | null>(null);

    useEffect(() => {
        // Check for reduced motion preference
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (prefersReducedMotion) {
            return;
        }

        // Initialize Lenis for smooth scrolling
        lenisRef.current = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            orientation: 'vertical',
            gestureOrientation: 'vertical',
            smoothWheel: true,
            touchMultiplier: 2,
        });

        // Connect Lenis to GSAP ScrollTrigger
        lenisRef.current.on('scroll', ScrollTrigger.update);

        gsap.ticker.add((time) => {
            lenisRef.current?.raf(time * 1000);
        });

        gsap.ticker.lagSmoothing(0);

        // GSAP defaults for smooth animations
        gsap.defaults({
            ease: 'power3.out',
            duration: 0.8,
        });

        return () => {
            lenisRef.current?.destroy();
            gsap.ticker.remove(() => { });
        };
    }, []);

    return (
        <AnimationContext.Provider value={{ lenis: lenisRef.current }}>
            {children}
        </AnimationContext.Provider>
    );
}

// ============================================================================
// ANIMATION HOOKS
// ============================================================================

/**
 * Hook for scroll-triggered reveal animations
 */
export function useScrollReveal(options?: {
    y?: number;
    opacity?: number;
    duration?: number;
    delay?: number;
    stagger?: number;
}) {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const { y = 60, opacity = 0, duration = 0.8, delay = 0, stagger = 0.1 } = options || {};

        // Set initial state
        gsap.set(element.children.length > 0 ? element.children : element, {
            y,
            opacity,
        });

        // Create scroll trigger animation
        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: element,
                start: 'top 85%',
                end: 'bottom 15%',
                toggleActions: 'play none none reverse',
            },
        });

        tl.to(element.children.length > 0 ? element.children : element, {
            y: 0,
            opacity: 1,
            duration,
            delay,
            stagger,
            ease: 'power3.out',
        });

        return () => {
            tl.kill();
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === element) {
                    trigger.kill();
                }
            });
        };
    }, [options]);

    return elementRef;
}

/**
 * Hook for magnetic button effect
 */
export function useMagneticEffect(strength: number = 0.3) {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const handleMouseMove = (e: MouseEvent) => {
            const rect = element.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            const deltaX = (e.clientX - centerX) * strength;
            const deltaY = (e.clientY - centerY) * strength;

            gsap.to(element, {
                x: deltaX,
                y: deltaY,
                duration: 0.3,
                ease: 'power2.out',
            });
        };

        const handleMouseLeave = () => {
            gsap.to(element, {
                x: 0,
                y: 0,
                duration: 0.5,
                ease: 'elastic.out(1, 0.3)',
            });
        };

        element.addEventListener('mousemove', handleMouseMove);
        element.addEventListener('mouseleave', handleMouseLeave);

        return () => {
            element.removeEventListener('mousemove', handleMouseMove);
            element.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, [strength]);

    return elementRef;
}

/**
 * Hook for text reveal animation
 */
export function useTextReveal(options?: {
    delay?: number;
    stagger?: number;
    y?: number;
}) {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const { delay = 0, stagger = 0.02, y = 100 } = options || {};

        // Split text into words
        const text = element.textContent || '';
        const words = text.split(' ');

        element.innerHTML = words
            .map((word) => `<span class="word-wrapper" style="display: inline-block; overflow: hidden;"><span class="word" style="display: inline-block;">${word}</span></span>`)
            .join(' ');

        const wordElements = element.querySelectorAll('.word');

        gsap.set(wordElements, { y, opacity: 0 });

        gsap.to(wordElements, {
            y: 0,
            opacity: 1,
            duration: 0.8,
            delay,
            stagger,
            ease: 'power3.out',
        });

        return () => {
            element.innerHTML = text;
        };
    }, [options]);

    return elementRef;
}

/**
 * Hook for parallax effect
 */
export function useParallax(speed: number = 0.5) {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        gsap.to(element, {
            yPercent: -50 * speed,
            ease: 'none',
            scrollTrigger: {
                trigger: element,
                start: 'top bottom',
                end: 'bottom top',
                scrub: true,
            },
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === element) {
                    trigger.kill();
                }
            });
        };
    }, [speed]);

    return elementRef;
}
