"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { scrollTriggerDefaults, scrollTriggerOnce, TIMING, EASING } from "./presets";

// Register GSAP plugins
if (typeof window !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
}

// ═══════════════════════════════════════════════════════════════
// useScrollReveal - Reveal elements on scroll
// ═══════════════════════════════════════════════════════════════

interface ScrollRevealOptions {
    animation?: "fadeUp" | "fadeIn" | "scaleIn" | "slideLeft" | "slideRight";
    delay?: number;
    duration?: number;
    once?: boolean;
    start?: string;
}

export function useScrollReveal<T extends HTMLElement>(
    options: ScrollRevealOptions = {}
) {
    const ref = useRef<T>(null);
    const {
        animation = "fadeUp",
        delay = 0,
        duration = TIMING.medium,
        once = true,
        start = "top 85%",
    } = options;

    useEffect(() => {
        if (!ref.current) return;

        const element = ref.current;

        // Initial state based on animation type
        const initialStates: Record<string, gsap.TweenVars> = {
            fadeUp: { opacity: 0, y: 50 },
            fadeIn: { opacity: 0 },
            scaleIn: { opacity: 0, scale: 0.9 },
            slideLeft: { opacity: 0, x: -50 },
            slideRight: { opacity: 0, x: 50 },
        };

        const finalStates: Record<string, gsap.TweenVars> = {
            fadeUp: { opacity: 1, y: 0 },
            fadeIn: { opacity: 1 },
            scaleIn: { opacity: 1, scale: 1 },
            slideLeft: { opacity: 1, x: 0 },
            slideRight: { opacity: 1, x: 0 },
        };

        gsap.set(element, initialStates[animation]);

        const tween = gsap.to(element, {
            ...finalStates[animation],
            duration,
            delay,
            ease: EASING.gsapDramatic,
            scrollTrigger: {
                trigger: element,
                start,
                toggleActions: once ? "play none none none" : "play none none reverse",
            },
        });

        return () => {
            tween.kill();
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === element) {
                    trigger.kill();
                }
            });
        };
    }, [animation, delay, duration, once, start]);

    return ref;
}

// ═══════════════════════════════════════════════════════════════
// useStaggerReveal - Reveal children with stagger
// ═══════════════════════════════════════════════════════════════

interface StaggerRevealOptions {
    stagger?: number;
    animation?: "fadeUp" | "fadeIn" | "scaleIn";
    childSelector?: string;
    once?: boolean;
}

export function useStaggerReveal<T extends HTMLElement>(
    options: StaggerRevealOptions = {}
) {
    const ref = useRef<T>(null);
    const {
        stagger = TIMING.stagger,
        animation = "fadeUp",
        childSelector = "> *",
        once = true,
    } = options;

    useEffect(() => {
        if (!ref.current) return;

        const container = ref.current;
        const children = container.querySelectorAll(childSelector);

        if (children.length === 0) return;

        const initialStates: Record<string, gsap.TweenVars> = {
            fadeUp: { opacity: 0, y: 30 },
            fadeIn: { opacity: 0 },
            scaleIn: { opacity: 0, scale: 0.95 },
        };

        const finalStates: Record<string, gsap.TweenVars> = {
            fadeUp: { opacity: 1, y: 0 },
            fadeIn: { opacity: 1 },
            scaleIn: { opacity: 1, scale: 1 },
        };

        gsap.set(children, initialStates[animation]);

        const tween = gsap.to(children, {
            ...finalStates[animation],
            duration: TIMING.medium,
            stagger,
            ease: EASING.gsapSmooth,
            scrollTrigger: {
                trigger: container,
                start: "top 80%",
                toggleActions: once ? "play none none none" : "play none none reverse",
            },
        });

        return () => {
            tween.kill();
        };
    }, [stagger, animation, childSelector, once]);

    return ref;
}

// ═══════════════════════════════════════════════════════════════
// useSplitText - Character/word animation (simplified)
// ═══════════════════════════════════════════════════════════════

interface SplitTextOptions {
    type?: "chars" | "words" | "lines";
    stagger?: number;
    duration?: number;
}

export function useSplitText<T extends HTMLElement>(
    options: SplitTextOptions = {}
) {
    const ref = useRef<T>(null);
    const {
        type = "words",
        stagger = 0.03,
        duration = TIMING.fast,
    } = options;

    useEffect(() => {
        if (!ref.current) return;

        const element = ref.current;
        const text = element.textContent || "";

        // Split based on type
        let parts: string[] = [];
        if (type === "chars") {
            parts = text.split("");
        } else if (type === "words") {
            parts = text.split(" ");
        } else {
            parts = [text]; // lines - simplified
        }

        // Create span wrapper for each part
        element.innerHTML = parts
            .map((part, i) =>
                `<span class="split-text-part" style="display: inline-block; opacity: 0; transform: translateY(20px);">${part}${type === "words" ? "&nbsp;" : ""}</span>`
            )
            .join("");

        const spans = element.querySelectorAll(".split-text-part");

        const tween = gsap.to(spans, {
            opacity: 1,
            y: 0,
            duration,
            stagger,
            ease: EASING.gsapDramatic,
            scrollTrigger: {
                trigger: element,
                start: "top 85%",
                toggleActions: "play none none none",
            },
        });

        return () => {
            tween.kill();
            element.textContent = text; // Restore original
        };
    }, [type, stagger, duration]);

    return ref;
}

// ═══════════════════════════════════════════════════════════════
// useParallax - Simple parallax effect
// ═══════════════════════════════════════════════════════════════

interface ParallaxOptions {
    speed?: number; // -1 to 1, negative = opposite direction
    start?: string;
    end?: string;
}

export function useParallax<T extends HTMLElement>(
    options: ParallaxOptions = {}
) {
    const ref = useRef<T>(null);
    const { speed = 0.3, start = "top bottom", end = "bottom top" } = options;

    useEffect(() => {
        if (!ref.current) return;

        const element = ref.current;
        const yDistance = speed * 100;

        const tween = gsap.fromTo(
            element,
            { y: -yDistance },
            {
                y: yDistance,
                ease: "none",
                scrollTrigger: {
                    trigger: element,
                    start,
                    end,
                    scrub: true,
                },
            }
        );

        return () => {
            tween.kill();
        };
    }, [speed, start, end]);

    return ref;
}

// ═══════════════════════════════════════════════════════════════
// useCountUp - Number counter animation
// ═══════════════════════════════════════════════════════════════

interface CountUpOptions {
    end: number;
    start?: number;
    duration?: number;
    suffix?: string;
    prefix?: string;
}

export function useCountUp<T extends HTMLElement>(options: CountUpOptions) {
    const ref = useRef<T>(null);
    const { end, start = 0, duration = 2, suffix = "", prefix = "" } = options;

    useEffect(() => {
        if (!ref.current) return;

        const element = ref.current;
        const obj = { value: start };

        const tween = gsap.to(obj, {
            value: end,
            duration,
            ease: EASING.gsapSmooth,
            scrollTrigger: {
                trigger: element,
                start: "top 85%",
                toggleActions: "play none none none",
            },
            onUpdate: () => {
                element.textContent = `${prefix}${Math.round(obj.value)}${suffix}`;
            },
        });

        return () => {
            tween.kill();
        };
    }, [end, start, duration, suffix, prefix]);

    return ref;
}
