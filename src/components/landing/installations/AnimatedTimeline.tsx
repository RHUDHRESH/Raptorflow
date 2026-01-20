"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Step {
    step: string;
    title: string;
    desc: string;
}

const STEPS: Step[] = [
    {
        step: "01",
        title: "Synchronize Context",
        desc: "Connect your specific business context. We build your RICP, positioning, and 90-day execution plan automatically."
    },
    {
        step: "02",
        title: "Deploy Weekly Moves",
        desc: "Every Monday, get your ready-to-ship packet: assets, strategic tasks, and maneuvers. No more blank pages."
    },
    {
        step: "03",
        title: "Execute & Track",
        desc: "The Matrix shows the signal. See what's driving pipeline. Double down on winners. Scale with absolute certainty."
    }
];

export default function AnimatedTimeline() {
    const [activeStep, setActiveStep] = useState(0);
    const [hoveredStep, setHoveredStep] = useState<number | null>(null);

    return (
        <div className="relative max-w-4xl mx-auto">
            {/* Desktop Layout */}
            <div className="hidden md:block">
                {/* Animated progress line */}
                <div className="absolute top-8 left-0 right-0 h-0.5 bg-[var(--border)]">
                    <motion.div
                        className="h-full bg-gradient-to-r from-[var(--rf-coral)] via-[var(--rf-ocean)] to-[var(--rf-mint)]"
                        initial={{ width: "0%" }}
                        whileInView={{ width: `${((activeStep + 1) / STEPS.length) * 100}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.5, delay: 0.5, ease: "easeOut" }}
                    />

                    {/* Animated dot traveling along the line */}
                    <motion.div
                        className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[var(--rf-coral)]"
                        style={{ filter: "drop-shadow(0 0 6px rgba(224, 141, 121, 0.6))" }}
                        initial={{ left: "0%" }}
                        animate={{ left: `${(activeStep / (STEPS.length - 1)) * 100}%` }}
                        transition={{ type: "spring", stiffness: 100, damping: 20 }}
                    />
                </div>

                {/* Steps */}
                <div className="grid grid-cols-3 gap-8">
                    {STEPS.map((step, i) => {
                        const isActive = activeStep === i;
                        const isHovered = hoveredStep === i;
                        const isPast = i < activeStep;

                        return (
                            <motion.div
                                key={i}
                                className="relative pt-16 text-center cursor-pointer"
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.2 }}
                                onMouseEnter={() => setHoveredStep(i)}
                                onMouseLeave={() => setHoveredStep(null)}
                                onClick={() => setActiveStep(i)}
                            >
                                {/* Step circle */}
                                <motion.div
                                    className={`
                                        absolute top-0 left-1/2 -translate-x-1/2 w-16 h-16 rounded-full 
                                        flex items-center justify-center border-2 transition-all duration-300
                                        ${isActive || isPast
                                            ? "bg-[var(--ink)] border-[var(--ink)] text-[var(--canvas)]"
                                            : "bg-[var(--surface)] border-[var(--border)] text-[var(--ink)]"
                                        }
                                    `}
                                    animate={{
                                        scale: isActive || isHovered ? 1.1 : 1,
                                        boxShadow: isActive
                                            ? "0 0 30px rgba(224, 141, 121, 0.4)"
                                            : isHovered
                                                ? "0 0 20px rgba(140, 169, 179, 0.3)"
                                                : "0 4px 20px rgba(0, 0, 0, 0.05)"
                                    }}
                                >
                                    <span className="text-xl font-mono font-bold">{step.step}</span>

                                    {/* Ripple effect */}
                                    {(isActive || isHovered) && (
                                        <motion.div
                                            className="absolute inset-0 rounded-full border-2 border-[var(--rf-ocean)]"
                                            initial={{ scale: 1, opacity: 0.6 }}
                                            animate={{ scale: 1.8, opacity: 0 }}
                                            transition={{ duration: 1, repeat: Infinity }}
                                        />
                                    )}
                                </motion.div>

                                {/* Content */}
                                <motion.h3
                                    className="text-xl font-bold mb-3"
                                    animate={{ color: isActive ? "var(--ink)" : "var(--secondary)" }}
                                >
                                    {step.title}
                                </motion.h3>

                                <AnimatePresence mode="wait">
                                    {(isActive || isHovered) && (
                                        <motion.p
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: "auto" }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="text-[var(--secondary)] leading-relaxed overflow-hidden"
                                        >
                                            {step.desc}
                                        </motion.p>
                                    )}
                                </AnimatePresence>

                                {!isActive && !isHovered && (
                                    <p className="text-[var(--muted)] text-sm">Click to explore</p>
                                )}
                            </motion.div>
                        );
                    })}
                </div>
            </div>

            {/* Mobile Layout - Vertical */}
            <div className="md:hidden space-y-6">
                {STEPS.map((step, i) => {
                    const isActive = activeStep === i;

                    return (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.15 }}
                            className={`
                                relative pl-20 py-4 cursor-pointer
                                ${isActive ? "bg-[var(--surface)] rounded-2xl" : ""}
                            `}
                            onClick={() => setActiveStep(i)}
                        >
                            {/* Connecting line */}
                            {i < STEPS.length - 1 && (
                                <div className="absolute left-8 top-16 bottom-0 w-0.5 bg-[var(--border)]">
                                    <motion.div
                                        className="w-full bg-gradient-to-b from-[var(--rf-coral)] to-[var(--rf-ocean)]"
                                        initial={{ height: 0 }}
                                        animate={{ height: isActive || i < activeStep ? "100%" : "0%" }}
                                        transition={{ duration: 0.5 }}
                                    />
                                </div>
                            )}

                            {/* Step circle */}
                            <motion.div
                                className={`
                                    absolute left-4 top-4 w-10 h-10 rounded-full flex items-center justify-center
                                    border-2 transition-all
                                    ${isActive || i < activeStep
                                        ? "bg-[var(--ink)] border-[var(--ink)] text-[var(--canvas)]"
                                        : "bg-[var(--surface)] border-[var(--border)]"
                                    }
                                `}
                                animate={{ scale: isActive ? 1.1 : 1 }}
                            >
                                <span className="text-sm font-mono font-bold">{step.step}</span>
                            </motion.div>

                            <h3 className="text-lg font-bold mb-2">{step.title}</h3>
                            <AnimatePresence>
                                {isActive && (
                                    <motion.p
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="text-[var(--secondary)] text-sm leading-relaxed"
                                    >
                                        {step.desc}
                                    </motion.p>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
