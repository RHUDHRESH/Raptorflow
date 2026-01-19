"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckmarkCircle02Icon } from "hugeicons-react";

import { ContentContainer } from "../shared/SectionWrapper";
import { fadeUp, staggerContainer } from "../animations/presets";

// ═══════════════════════════════════════════════════════════════
// BenefitsV2 - Why founders switch (dark section)
// ═══════════════════════════════════════════════════════════════

const BENEFITS = [
    {
        title: "Save 10+ hours per week",
        desc: "Stop context-switching between tools. Everything lives in one place.",
    },
    {
        title: "Ship content that converts",
        desc: "No more guessing what to post. Every Move is backed by your strategy.",
    },
    {
        title: "Know what's working",
        desc: "Real attribution, not vanity metrics. See the full pipeline picture.",
    },
    {
        title: "Build institutional memory",
        desc: "Every experiment, every outcome. Never repeat the same mistakes.",
    },
];

export function BenefitsV2() {
    return (
        <section className="py-32 bg-[var(--ink)] text-[var(--canvas)]">
            <ContentContainer>
                {/* Header */}
                <div className="max-w-3xl mb-16">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-4xl md:text-5xl font-editorial mb-6 text-[var(--canvas)]"
                    >
                        Why founders switch.
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-[var(--canvas)]/70"
                    >
                        RaptorFlow isn't another tool. It's the tool that replaces five
                        others.
                    </motion.p>
                </div>

                {/* Benefits Grid */}
                <motion.div
                    variants={staggerContainer}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    className="grid md:grid-cols-2 gap-8"
                >
                    {BENEFITS.map((benefit, i) => (
                        <motion.div
                            key={i}
                            variants={fadeUp}
                            className="flex gap-4 p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/8 transition-colors"
                        >
                            <div className="flex-shrink-0 mt-1">
                                {React.createElement(CheckmarkCircle02Icon as any, {
                                    className: "w-6 h-6 text-[var(--accent)]",
                                })}
                            </div>
                            <div>
                                {/* Title - Fixed visibility issue */}
                                <h3 className="text-xl font-bold mb-2 text-[var(--canvas)]">
                                    {benefit.title}
                                </h3>
                                <p className="text-[var(--canvas)]/70">{benefit.desc}</p>
                            </div>
                        </motion.div>
                    ))}
                </motion.div>
            </ContentContainer>
        </section>
    );
}
