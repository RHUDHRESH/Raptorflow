"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { RaptorLogo } from "@/components/ui/CompassLogo";
import { CheckmarkCircle02Icon } from "hugeicons-react";

const BEFORE_ITEMS = [
    "Staring at a blank cursor every Monday morning.",
    "Guessing which channels are actually driving growth.",
    "Switching between Buffer, Notion, and generic AI prompts.",
    "Spending 15+ hours a week on 'marketing activities'.",
    "Zero pipeline visibility and inconsistent messaging."
];

const AFTER_ITEMS = [
    "Ready-to-ship Move packets delivered every Monday.",
    "Surgical precision in ICP and behavior targeting.",
    "A single, unified OS for strategy and execution.",
    "Save 10+ hours a week through technical automation.",
    "Full pipeline tracking and institutional memory."
];

export default function ParallaxTransformation() {
    const containerRef = useRef<HTMLDivElement>(null);

    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"]
    });

    // Parallax effects
    const beforeY = useTransform(scrollYProgress, [0, 1], [60, -60]);
    const afterY = useTransform(scrollYProgress, [0, 1], [-60, 60]);
    const dividerScale = useTransform(scrollYProgress, [0.3, 0.5, 0.7], [0.8, 1.1, 0.8]);
    const dividerRotate = useTransform(scrollYProgress, [0, 1], [-5, 5]);

    return (
        <div ref={containerRef} className="relative">
            {/* Animated background gradient */}
            <motion.div
                className="absolute inset-0 rounded-3xl overflow-hidden"
                style={{
                    background: "linear-gradient(135deg, rgba(139, 58, 58, 0.03) 0%, transparent 50%, rgba(45, 90, 61, 0.03) 100%)"
                }}
            />

            <div className="grid md:grid-cols-2 gap-px bg-[var(--border)] border border-[var(--border)] rounded-3xl overflow-hidden shadow-2xl relative">
                {/* Before - with parallax */}
                <motion.div
                    className="bg-[var(--surface)] p-12 space-y-8 relative overflow-hidden"
                    style={{ y: beforeY }}
                >
                    {/* Floating X marks in background */}
                    <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-5">
                        {[...Array(6)].map((_, i) => (
                            <motion.span
                                key={i}
                                className="absolute text-6xl font-bold text-red-600"
                                style={{
                                    left: `${15 + (i % 3) * 30}%`,
                                    top: `${20 + Math.floor(i / 3) * 40}%`,
                                }}
                                animate={{
                                    y: [0, -10, 0],
                                    opacity: [0.3, 0.6, 0.3],
                                }}
                                transition={{
                                    duration: 3,
                                    delay: i * 0.5,
                                    repeat: Infinity,
                                }}
                            >
                                ×
                            </motion.span>
                        ))}
                    </div>

                    <motion.h3
                        className="text-2xl font-bold text-[var(--muted)] flex items-center gap-3 relative z-10"
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                    >
                        <motion.span
                            className="w-10 h-10 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-lg font-mono font-bold"
                            whileHover={{ scale: 1.1, rotate: 180 }}
                            transition={{ type: "spring" }}
                        >
                            ×
                        </motion.span>
                        Before RaptorFlow
                    </motion.h3>

                    <ul className="space-y-5 relative z-10">
                        {BEFORE_ITEMS.map((item, i) => (
                            <motion.li
                                key={i}
                                initial={{ opacity: 0, x: -30 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                whileHover={{ x: 5 }}
                                className="flex gap-4 text-lg text-[var(--secondary)] group cursor-default"
                            >
                                <span className="text-[var(--muted)]/50 group-hover:text-red-400 transition-colors">—</span>
                                <span className="line-through decoration-[var(--muted)]/30 group-hover:decoration-red-300 transition-all">
                                    {item}
                                </span>
                            </motion.li>
                        ))}
                    </ul>
                </motion.div>

                {/* Center divider with animation */}
                <motion.div
                    className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20 hidden md:block"
                    style={{ scale: dividerScale, rotate: dividerRotate }}
                >
                    <motion.div
                        className="w-16 h-16 rounded-full bg-[var(--canvas)] border-4 border-[var(--border)] flex items-center justify-center shadow-xl"
                        animate={{
                            boxShadow: [
                                "0 0 20px rgba(224, 141, 121, 0.2)",
                                "0 0 40px rgba(140, 169, 179, 0.3)",
                                "0 0 20px rgba(224, 141, 121, 0.2)"
                            ]
                        }}
                        transition={{ duration: 3, repeat: Infinity }}
                    >
                        <motion.span
                            className="text-2xl"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                        >
                            →
                        </motion.span>
                    </motion.div>
                </motion.div>

                {/* After - with inverse parallax */}
                <motion.div
                    className="bg-[var(--canvas)] p-12 space-y-8 relative overflow-hidden"
                    style={{ y: afterY }}
                >
                    {/* Background logo */}
                    <div className="absolute top-0 right-0 p-4 opacity-5">
                        <RaptorLogo size={200} />
                    </div>

                    {/* Floating checkmarks */}
                    <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-10">
                        {[...Array(6)].map((_, i) => (
                            <motion.span
                                key={i}
                                className="absolute text-4xl text-green-600"
                                style={{
                                    right: `${15 + (i % 3) * 25}%`,
                                    top: `${15 + Math.floor(i / 3) * 35}%`,
                                }}
                                animate={{
                                    y: [0, -15, 0],
                                    scale: [1, 1.1, 1],
                                }}
                                transition={{
                                    duration: 2.5,
                                    delay: i * 0.4,
                                    repeat: Infinity,
                                }}
                            >
                                ✓
                            </motion.span>
                        ))}
                    </div>

                    <motion.h3
                        className="text-2xl font-bold text-[var(--ink)] flex items-center gap-3 relative z-10"
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                    >
                        <motion.span
                            className="w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-lg font-mono font-bold"
                            whileHover={{ scale: 1.1, rotate: 360 }}
                            transition={{ type: "spring" }}
                        >
                            ✓
                        </motion.span>
                        After RaptorFlow
                    </motion.h3>

                    <ul className="space-y-5 relative z-10">
                        {AFTER_ITEMS.map((item, i) => (
                            <motion.li
                                key={i}
                                initial={{ opacity: 0, x: 30 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                whileHover={{ x: 5 }}
                                className="flex gap-4 text-lg text-[var(--ink)] font-medium group cursor-default"
                            >
                                <motion.span
                                    whileHover={{ scale: 1.2, rotate: 360 }}
                                    transition={{ type: "spring" }}
                                >
                                    {React.createElement(CheckmarkCircle02Icon as any, {
                                        className: "w-6 h-6 text-green-600 flex-shrink-0 mt-0.5 group-hover:text-green-500 transition-colors"
                                    })}
                                </motion.span>
                                {item}
                            </motion.li>
                        ))}
                    </ul>
                </motion.div>
            </div>
        </div>
    );
}
