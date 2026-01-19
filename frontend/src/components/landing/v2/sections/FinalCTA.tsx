"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight01Icon } from "hugeicons-react";

import { ContentContainer } from "../shared/SectionWrapper";
import { fadeUp } from "../animations/presets";

// ═══════════════════════════════════════════════════════════════
// FinalCTA - Dramatic closing call-to-action
// ═══════════════════════════════════════════════════════════════

export function FinalCTA() {
    return (
        <section className="py-32 bg-[var(--ink)] text-[var(--canvas)]">
            <ContentContainer size="md" className="text-center">
                {/* Headline */}
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-5xl md:text-6xl lg:text-7xl font-editorial mb-6 text-[var(--canvas)]"
                >
                    Ready to stop guessing?
                </motion.h2>

                {/* Subtext */}
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                    className="text-xl text-[var(--canvas)]/70 mb-10"
                >
                    Join 500+ founders who replaced marketing chaos with a system that
                    works.
                </motion.p>

                {/* CTA Button */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                >
                    <Link
                        href="/signup"
                        className="group inline-flex items-center gap-2 px-10 py-5 bg-[var(--canvas)] text-[var(--ink)] text-lg font-semibold rounded-xl hover:opacity-90 transition-all hover:scale-[1.02]"
                    >
                        Start your free trial
                        {React.createElement(ArrowRight01Icon as any, {
                            className: "w-5 h-5 group-hover:translate-x-1 transition-transform",
                        })}
                    </Link>
                </motion.div>
            </ContentContainer>
        </section>
    );
}

// ═══════════════════════════════════════════════════════════════
// FAQ Section
// ═══════════════════════════════════════════════════════════════

const FAQS = [
    {
        q: "How is RaptorFlow different from other marketing tools?",
        a: "RaptorFlow isn't a tool—it's an operating system. Others give you features in isolation. We connect strategy to execution in one unified workflow.",
    },
    {
        q: "Do I need a marketing team?",
        a: "No. Built specifically for founders and lean teams. The system generates your weekly execution packets—no dedicated marketer needed.",
    },
    {
        q: "What if I don't know my positioning yet?",
        a: "That's what Foundation is for. Our onboarding synthesizes your ICP, positioning, and 90-day plan in under 20 minutes.",
    },
    {
        q: "How long until I see results?",
        a: "Most users ship their first Move within a week. Measurable pipeline impact typically shows within 4-6 weeks of consistent execution.",
    },
];

export function FAQSection() {
    return (
        <section className="py-32">
            <ContentContainer size="md">
                {/* Header */}
                <div className="text-center mb-16">
                    <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">
                        FAQ
                    </p>
                    <h2 className="text-4xl md:text-5xl font-editorial text-[var(--ink)]">
                        Questions?{" "}
                        <span className="text-[var(--muted)]">Answered.</span>
                    </h2>
                </div>

                {/* FAQ Items */}
                <div className="space-y-6">
                    {FAQS.map((faq, i) => (
                        <motion.div
                            key={i}
                            variants={fadeUp}
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            className="p-6 border border-[var(--border)] rounded-xl hover:border-[var(--ink)]/30 transition-colors"
                        >
                            <h3 className="text-lg font-bold mb-3 text-[var(--ink)]">
                                {faq.q}
                            </h3>
                            <p className="text-[var(--secondary)]">{faq.a}</p>
                        </motion.div>
                    ))}
                </div>
            </ContentContainer>
        </section>
    );
}
