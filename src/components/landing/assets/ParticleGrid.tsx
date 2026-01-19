"use client";

import React from "react";
import { motion } from "framer-motion";

/**
 * A subtle animated dot grid background, inspired by Linear/Vercel.
 * Uses CSS for the grid pattern and Framer Motion for a subtle floating animation.
 */
export function ParticleGrid() {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
            {/* The main dot grid pattern */}
            <div
                className="absolute inset-0 opacity-[0.4]"
                style={{
                    backgroundImage: `radial-gradient(circle at center, var(--border) 1px, transparent 1px)`,
                    backgroundSize: '32px 32px',
                }}
            />

            {/* Subtle animated glow spots */}
            <motion.div
                animate={{
                    x: [0, 50, 0],
                    y: [0, -30, 0],
                    opacity: [0.1, 0.3, 0.1],
                }}
                transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                className="absolute top-[20%] left-[15%] w-64 h-64 bg-[var(--accent)]/10 rounded-full blur-3xl"
            />
            <motion.div
                animate={{
                    x: [0, -40, 0],
                    y: [0, 40, 0],
                    opacity: [0.05, 0.2, 0.05],
                }}
                transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 2
                }}
                className="absolute bottom-[30%] right-[20%] w-80 h-80 bg-[var(--ink)]/5 rounded-full blur-3xl"
            />
        </div>
    );
}
