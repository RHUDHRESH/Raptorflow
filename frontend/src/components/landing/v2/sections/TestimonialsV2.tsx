"use client";

import React from "react";
import { motion } from "framer-motion";

import { SectionWrapper, SectionHeader, ContentContainer } from "../shared/SectionWrapper";
import { fadeUp } from "../animations/presets";

// ═══════════════════════════════════════════════════════════════
// TestimonialsV2 - Founders who ship
// ═══════════════════════════════════════════════════════════════

const TESTIMONIALS = [
    {
        quote:
            "I went from random posting to a real strategy in one afternoon. This is what founder marketing should feel like.",
        name: "Sarah Chen",
        role: "Founder, ProductLabs",
        initials: "SC",
    },
    {
        quote:
            "RaptorFlow replaced Notion, Buffer, and ChatGPT for me. The weekly Moves alone save me 5 hours.",
        name: "Marcus Rodriguez",
        role: "CEO, Clarity AI",
        initials: "MR",
    },
    {
        quote:
            "Finally understand what's driving pipeline vs. what's just vanity metrics. Game changer.",
        name: "Emma Thompson",
        role: "Founder, DesignPro",
        initials: "ET",
    },
];

export function TestimonialsV2() {
    return (
        <SectionWrapper>
            <ContentContainer>
                <SectionHeader
                    eyebrow="Testimonials"
                    title="Founders who ship."
                    centered
                />

                {/* Testimonials Grid */}
                <div className="grid md:grid-cols-3 gap-6">
                    {TESTIMONIALS.map((testimonial, i) => (
                        <motion.div
                            key={i}
                            variants={fadeUp}
                            className="p-8 border border-[var(--border)] rounded-2xl bg-[var(--canvas)] hover:border-[var(--ink)]/30 transition-colors"
                        >
                            {/* Quote */}
                            <p className="text-lg leading-relaxed mb-6 text-[var(--ink)]">
                                "{testimonial.quote}"
                            </p>

                            {/* Author */}
                            <div className="flex items-center gap-3">
                                {/* Avatar */}
                                <div className="w-10 h-10 rounded-full bg-[var(--ink)] text-[var(--canvas)] flex items-center justify-center font-bold text-sm">
                                    {testimonial.initials}
                                </div>
                                <div>
                                    <p className="font-semibold text-[var(--ink)]">
                                        {testimonial.name}
                                    </p>
                                    <p className="text-sm text-[var(--muted)]">
                                        {testimonial.role}
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </ContentContainer>
        </SectionWrapper>
    );
}
