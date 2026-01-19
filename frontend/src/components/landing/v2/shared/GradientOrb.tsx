"use client";

import React from "react";
import { motion } from "framer-motion";

// ═══════════════════════════════════════════════════════════════
// GradientOrb - Ambient background decoration
// ═══════════════════════════════════════════════════════════════

interface GradientOrbProps {
    /** Position - CSS values */
    top?: string;
    left?: string;
    right?: string;
    bottom?: string;
    /** Size in pixels */
    size?: number;
    /** Color - use CSS variable or hex */
    color?: string;
    /** Blur amount in pixels */
    blur?: number;
    /** Opacity 0-1 */
    opacity?: number;
    /** Whether to animate */
    animate?: boolean;
    /** Animation duration in seconds */
    duration?: number;
    className?: string;
}

export function GradientOrb({
    top,
    left,
    right,
    bottom,
    size = 500,
    color = "var(--accent)",
    blur = 150,
    opacity = 0.05,
    animate = true,
    duration = 8,
    className = "",
}: GradientOrbProps) {
    const positionStyles: React.CSSProperties = {
        position: "absolute",
        top,
        left,
        right,
        bottom,
        width: size,
        height: size,
        background: color,
        borderRadius: "50%",
        filter: `blur(${blur}px)`,
        opacity,
        pointerEvents: "none",
    };

    if (!animate) {
        return <div style={positionStyles} className={className} />;
    }

    return (
        <motion.div
            style={positionStyles}
            className={className}
            animate={{
                scale: [1, 1.1, 1],
                opacity: [opacity, opacity * 1.5, opacity],
            }}
            transition={{
                duration,
                repeat: Infinity,
                ease: "easeInOut",
            }}
        />
    );
}

// ═══════════════════════════════════════════════════════════════
// AmbientBackground - Multiple orbs composition
// ═══════════════════════════════════════════════════════════════

interface AmbientBackgroundProps {
    variant?: "hero" | "subtle" | "dramatic";
    className?: string;
}

export function AmbientBackground({
    variant = "subtle",
    className = "",
}: AmbientBackgroundProps) {
    const configs = {
        hero: [
            { top: "10%", left: "-10%", size: 800, color: "var(--accent)", opacity: 0.04, duration: 10 },
            { bottom: "20%", right: "-5%", size: 600, color: "var(--ink)", opacity: 0.03, duration: 12 },
        ],
        subtle: [
            { top: "30%", left: "20%", size: 400, color: "var(--accent)", opacity: 0.03, duration: 8 },
        ],
        dramatic: [
            { top: "-20%", left: "-10%", size: 900, color: "var(--accent)", opacity: 0.06, duration: 15 },
            { bottom: "-10%", right: "-15%", size: 700, color: "var(--ink)", opacity: 0.04, duration: 12 },
            { top: "50%", left: "50%", size: 500, color: "var(--accent)", opacity: 0.02, duration: 20 },
        ],
    };

    return (
        <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
            {configs[variant].map((config, i) => (
                <GradientOrb key={i} {...config} />
            ))}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════
// GridPattern - Subtle grid background
// ═══════════════════════════════════════════════════════════════

interface GridPatternProps {
    className?: string;
    opacity?: number;
}

export function GridPattern({ className = "", opacity = 0.03 }: GridPatternProps) {
    return (
        <div
            className={`absolute inset-0 pointer-events-none ${className}`}
            style={{
                backgroundImage: `
          linear-gradient(var(--border) 1px, transparent 1px),
          linear-gradient(90deg, var(--border) 1px, transparent 1px)
        `,
                backgroundSize: "60px 60px",
                opacity,
            }}
        />
    );
}
