"use client";

import React from "react";
import { motion } from "framer-motion";
import {
    CheckmarkCircle02Icon,
    Cancel01Icon,
    Target02Icon,
    Clock01Icon,
    Analytics01Icon
} from "hugeicons-react";

/**
 * WhyRaptorFlow - Clean benefits comparison section
 * Replaces the complex RoadOfFate with a scannable card layout
 */

const BENEFITS = [
    {
        icon: Target02Icon,
        title: "Strategy, Not Guessing",
        without: "Random posts hoping something sticks",
        with: "Data-backed positioning and ICP clarity",
    },
    {
        icon: Clock01Icon,
        title: "Execution, Not Planning",
        without: "Hours lost to tool switching and blank pages",
        with: "Weekly Moves ready to ship every Monday",
    },
    {
        icon: Analytics01Icon,
        title: "Signal, Not Noise",
        without: "Vanity metrics that mean nothing",
        with: "Pipeline velocity and real attribution",
    },
];

export function WhyRaptorFlow() {
    return (
        <section className="py-24 md:py-32 bg-[var(--canvas)]">
            <div className="max-w-7xl mx-auto px-6">

                {/* Header */}
                <div className="text-center mb-16">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-4xl md:text-5xl font-editorial text-[var(--ink)] mb-4"
                    >
                        Why founders choose <span className="italic text-[var(--muted)]">RaptorFlow</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-lg text-[var(--secondary)] max-w-2xl mx-auto"
                    >
                        The difference between marketing chaos and marketing clarity.
                    </motion.p>
                </div>

                {/* Benefits Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {BENEFITS.map((benefit, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            className="p-8 rounded-2xl border border-[var(--border)] bg-[var(--surface)]"
                        >
                            {/* Icon */}
                            <div className="w-12 h-12 mb-6 rounded-xl bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center">
                                {React.createElement(benefit.icon as any, { className: "w-6 h-6 text-[var(--ink)]" })}
                            </div>

                            {/* Title */}
                            <h3 className="text-xl font-bold text-[var(--ink)] mb-6">
                                {benefit.title}
                            </h3>

                            {/* Without */}
                            <div className="flex items-start gap-3 mb-3">
                                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-red-50 flex items-center justify-center mt-0.5">
                                    {React.createElement(Cancel01Icon as any, { className: "w-3 h-3 text-red-400" })}
                                </div>
                                <p className="text-sm text-[var(--muted)] leading-relaxed">
                                    {benefit.without}
                                </p>
                            </div>

                            {/* With */}
                            <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-[var(--accent)]/10 flex items-center justify-center mt-0.5">
                                    {React.createElement(CheckmarkCircle02Icon as any, { className: "w-3 h-3 text-[var(--accent)]" })}
                                </div>
                                <p className="text-sm text-[var(--ink)] leading-relaxed font-medium">
                                    {benefit.with}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
