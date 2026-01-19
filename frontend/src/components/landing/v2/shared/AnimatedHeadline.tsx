"use client";

import React, { useRef, useEffect, ReactNode } from "react";
import { motion, useInView } from "framer-motion";

// ═══════════════════════════════════════════════════════════════
// AnimatedHeadline - Text reveal animations
// ═══════════════════════════════════════════════════════════════

interface AnimatedHeadlineProps {
    children: string;
    as?: "h1" | "h2" | "h3" | "p" | "span";
    className?: string;
    animation?: "fadeUp" | "slideUp" | "charReveal" | "wordReveal";
    delay?: number;
    stagger?: number;
}

export function AnimatedHeadline({
    children,
    as: Tag = "h2",
    className = "",
    animation = "fadeUp",
    delay = 0,
    stagger = 0.03,
}: AnimatedHeadlineProps) {
    const ref = useRef<HTMLElement>(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });

    // For simple animations
    if (animation === "fadeUp") {
        return (
            <motion.div
                ref={ref as any}
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
            >
                <Tag className={className}>{children}</Tag>
            </motion.div>
        );
    }

    // For word-by-word reveal
    if (animation === "wordReveal") {
        const words = children.split(" ");
        return (
            <Tag ref={ref as any} className={className}>
                {words.map((word, i) => (
                    <motion.span
                        key={i}
                        className="inline-block overflow-hidden"
                        style={{ marginRight: "0.25em" }}
                    >
                        <motion.span
                            className="inline-block"
                            initial={{ y: "100%" }}
                            animate={isInView ? { y: 0 } : {}}
                            transition={{
                                duration: 0.5,
                                delay: delay + i * stagger,
                                ease: [0.16, 1, 0.3, 1],
                            }}
                        >
                            {word}
                        </motion.span>
                    </motion.span>
                ))}
            </Tag>
        );
    }

    // For character reveal
    if (animation === "charReveal") {
        const chars = children.split("");
        return (
            <Tag ref={ref as any} className={className}>
                {chars.map((char, i) => (
                    <motion.span
                        key={i}
                        className="inline-block"
                        initial={{ opacity: 0, y: 20 }}
                        animate={isInView ? { opacity: 1, y: 0 } : {}}
                        transition={{
                            duration: 0.3,
                            delay: delay + i * stagger,
                            ease: [0.16, 1, 0.3, 1],
                        }}
                    >
                        {char === " " ? "\u00A0" : char}
                    </motion.span>
                ))}
            </Tag>
        );
    }

    // Default slideUp
    return (
        <div className="overflow-hidden" ref={ref as any}>
            <motion.div
                initial={{ y: "100%" }}
                animate={isInView ? { y: 0 } : {}}
                transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
            >
                <Tag className={className}>{children}</Tag>
            </motion.div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════
// GradientText - Accent gradient on text
// ═══════════════════════════════════════════════════════════════

interface GradientTextProps {
    children: ReactNode;
    className?: string;
}

export function GradientText({ children, className = "" }: GradientTextProps) {
    return (
        <span
            className={`bg-gradient-to-r from-[var(--ink)] via-[var(--accent)] to-[var(--ink)] bg-clip-text text-transparent bg-[length:200%_auto] ${className}`}
            style={{
                animation: "shimmer 3s linear infinite",
            }}
        >
            {children}
        </span>
    );
}

// ═══════════════════════════════════════════════════════════════
// MutedText - Secondary color text span
// ═══════════════════════════════════════════════════════════════

interface MutedTextProps {
    children: ReactNode;
    className?: string;
}

export function MutedText({ children, className = "" }: MutedTextProps) {
    return (
        <span className={`text-[var(--muted)] ${className}`}>
            {children}
        </span>
    );
}
