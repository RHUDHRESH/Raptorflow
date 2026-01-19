"use client";

import React from "react";
import { motion } from "framer-motion";
import {
    Target02Icon,
    Rocket01Icon,
    Analytics01Icon
} from "hugeicons-react";

const STEPS = [
    {
        number: "01",
        icon: Target02Icon,
        title: "Define Your Foundation",
        description: "Answer strategic questions once. RaptorFlow builds your ICP, positioning, and 90-day war plan.",
    },
    {
        number: "02",
        icon: Rocket01Icon,
        title: "Execute Your Moves",
        description: "Get weekly execution packets with ready-to-ship content, assets, and tasks. No more blank pages.",
    },
    {
        number: "03",
        icon: Analytics01Icon,
        title: "See What Works",
        description: "Matrix shows you signal, not noise. Track real pipeline velocity and iterate with data.",
    },
];

export function HowItWorks() {
    return (
        <section className="py-24 md:py-32 bg-[var(--surface)] border-y border-[var(--border)]">
            <div className="max-w-7xl mx-auto px-6">

                {/* Header */}
                <div className="text-center mb-20">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-block px-3 py-1 bg-[var(--canvas)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--secondary)] mb-6"
                    >
                        How It Works
                    </motion.div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-5xl font-editorial text-[var(--ink)]"
                    >
                        From chaos to clarity. <span className="italic text-[var(--muted)]">In 3 steps.</span>
                    </motion.h2>
                </div>

                {/* Steps */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-4 relative">

                    {/* Connecting Line (Desktop Only) */}
                    <div className="hidden md:block absolute top-24 left-[16.66%] right-[16.66%] h-px bg-gradient-to-r from-transparent via-[var(--border)] to-transparent" />

                    {STEPS.map((step, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-50px" }}
                            transition={{ delay: i * 0.15 }}
                            className="relative flex flex-col items-center text-center p-8"
                        >
                            {/* Number Badge */}
                            <div className="relative mb-6">
                                <div className="w-16 h-16 rounded-full bg-[var(--canvas)] border-2 border-[var(--border)] flex items-center justify-center shadow-lg">
                                    {React.createElement(step.icon as any, { className: "w-7 h-7 text-[var(--ink)]" })}
                                </div>
                                <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-[var(--ink)] text-[var(--canvas)] text-xs font-bold flex items-center justify-center font-mono">
                                    {step.number}
                                </span>
                            </div>

                            {/* Content */}
                            <h3 className="text-xl font-bold text-[var(--ink)] mb-3">
                                {step.title}
                            </h3>
                            <p className="text-[var(--secondary)] leading-relaxed max-w-xs">
                                {step.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
