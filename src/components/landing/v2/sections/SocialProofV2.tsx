"use client";

import React from "react";
import { motion } from "framer-motion";

// ═══════════════════════════════════════════════════════════════
// SocialProofV2 - Logo marquee with infinite scroll
// ═══════════════════════════════════════════════════════════════

const LOGOS = [
    "ProductHunt",
    "Indie Hackers",
    "YC",
    "Techstars",
    "500 Global",
];

export function SocialProofV2() {
    return (
        <section className="py-12 border-y border-[var(--border)] bg-[var(--surface)] overflow-hidden">
            <div className="max-w-7xl mx-auto px-6">
                <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16">
                    {/* Label */}
                    <motion.p
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        viewport={{ once: true }}
                        className="text-sm text-[var(--muted)] uppercase tracking-wider whitespace-nowrap"
                    >
                        Trusted by 500+ founders
                    </motion.p>

                    {/* Logo Marquee - TODO: Add infinite scroll animation */}
                    <div className="relative flex-1 overflow-hidden">
                        <motion.div
                            initial={{ opacity: 0 }}
                            whileInView={{ opacity: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            className="flex items-center gap-10"
                        >
                            {LOGOS.map((name, i) => (
                                <span
                                    key={i}
                                    className="text-sm font-medium text-[var(--muted)] whitespace-nowrap hover:text-[var(--ink)] transition-colors cursor-default"
                                >
                                    {name}
                                </span>
                            ))}
                        </motion.div>
                    </div>
                </div>
            </div>
        </section>
    );
}

// ═══════════════════════════════════════════════════════════════
// ProblemStatement - Editorial pull-quote style
// ═══════════════════════════════════════════════════════════════

export function ProblemStatement() {
    return (
        <section className="py-32">
            <div className="max-w-4xl mx-auto px-6">
                {/* Main Quote - TODO: Add word-by-word reveal */}
                <motion.p
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                    className="text-3xl md:text-4xl lg:text-5xl font-editorial leading-[1.3] text-[var(--ink)]"
                >
                    You've tried Buffer. Notion. ChatGPT. Five different tools that don't
                    talk to each other.{" "}
                    <span className="text-[var(--muted)]">
                        Six months of posting. Twelve followers. Zero pipeline.
                    </span>
                </motion.p>

                {/* Supporting text */}
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2, duration: 0.5 }}
                    className="mt-8 text-xl text-[var(--secondary)]"
                >
                    Marketing shouldn't feel like shouting into the void.
                </motion.p>
            </div>
        </section>
    );
}
