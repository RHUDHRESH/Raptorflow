"use client";

import React from "react";
import {
    BoardMathIcon,
    Analytics01Icon,
    Target02Icon,
    Layers01Icon,
    Settings01Icon,
    Message01Icon
} from "hugeicons-react";
import { motion } from "framer-motion";

/**
 * FeatureGrid - The core modules
 * Clean card-based layout showing the system components
 */

interface Feature {
    icon: any;
    title: string;
    desc: string;
}

const FEATURES: Feature[] = [
    {
        icon: Target02Icon,
        title: "Foundation",
        desc: "Define your positioning once. Use it everywhere. ICP, messaging, and 90-day plans generated automatically."
    },
    {
        icon: Layers01Icon,
        title: "Cohorts",
        desc: "Segment your audience with data, not hunches. Behavioral targeting that actually converts."
    },
    {
        icon: BoardMathIcon,
        title: "Moves",
        desc: "Weekly execution packets ready to ship. Content, assets, and tasks all in one view."
    },
    {
        icon: Message01Icon,
        title: "Muse",
        desc: "Generate content in your actual voice. No more sounding like a generic AI robot."
    },
    {
        icon: Analytics01Icon,
        title: "Matrix",
        desc: "See signal, not noise. Pipeline attribution that shows what's actually working."
    },
    {
        icon: Settings01Icon,
        title: "Blackbox",
        desc: "Never lose a learning. Your permanent vault for experiments and outcomes."
    }
];

export function FeatureGrid() {
    return (
        <section id="features" className="py-24 md:py-32 bg-[var(--canvas)] border-t border-[var(--border)]">
            <div className="max-w-7xl mx-auto px-6">

                {/* Section Header */}
                <div className="max-w-3xl mb-16">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-block px-3 py-1 bg-[var(--surface)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--secondary)] mb-6"
                    >
                        The System
                    </motion.div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.6 }}
                        className="text-3xl md:text-5xl font-editorial text-[var(--ink)] mb-6"
                    >
                        Six modules.{" "}
                        <span className="italic text-[var(--muted)]">One operating system.</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="text-lg text-[var(--secondary)] leading-relaxed max-w-xl"
                    >
                        Everything you need to go from strategy to execution without the friction of multiple tools.
                    </motion.p>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {FEATURES.map((feature, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.05, duration: 0.4, ease: "easeOut" }}
                            className="group p-8 rounded-2xl border border-[var(--border)] bg-[var(--surface)] hover:border-[var(--ink)]/30 transition-colors duration-300"
                        >
                            {/* Icon */}
                            <div className="w-12 h-12 mb-6 rounded-xl bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center group-hover:border-[var(--ink)]/30 transition-colors">
                                {React.createElement(feature.icon as any, {
                                    className: "w-6 h-6 text-[var(--ink)]"
                                })}
                            </div>

                            {/* Title */}
                            <h3 className="text-xl font-semibold text-[var(--ink)] mb-3">
                                {feature.title}
                            </h3>

                            {/* Description */}
                            <p className="text-[var(--secondary)] leading-relaxed">
                                {feature.desc}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
