"use client";

import React from "react";
import { motion } from "framer-motion";
import { StarIcon } from "hugeicons-react";

/**
 * Testimonials section with multiple review cards
 * Professional structure with realistic placeholder content
 */

const TESTIMONIALS = [
    {
        quote: "Finally, a marketing system that doesn't require a full-time marketer. I went from random posting to a real strategy in one afternoon.",
        name: "Sarah Chen",
        role: "Founder",
        company: "ProductLabs",
        initials: "SC"
    },
    {
        quote: "RaptorFlow replaced 4 different tools for us. The weekly Moves feature alone saves me 5 hours a week.",
        name: "Marcus Rodriguez",
        role: "CEO",
        company: "Clarity AI",
        initials: "MR"
    },
    {
        quote: "The Foundation module forced me to think clearly about positioning for the first time. Now every piece of content feels intentional.",
        name: "Emma Thompson",
        role: "Solo Founder",
        company: "DesignPro",
        initials: "ET"
    }
];

export function Testimonial() {
    return (
        <section className="py-24 md:py-32 bg-[var(--surface)] border-y border-[var(--border)]">
            <div className="max-w-7xl mx-auto px-6">

                {/* Header */}
                <div className="text-center mb-16">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-4xl md:text-5xl font-editorial text-[var(--ink)] mb-4"
                    >
                        Founders who <span className="italic text-[var(--muted)]">ship</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-lg text-[var(--secondary)]"
                    >
                        Real results from real founders building real companies.
                    </motion.p>
                </div>

                {/* Testimonial Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {TESTIMONIALS.map((testimonial, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            className="p-8 rounded-2xl border border-[var(--border)] bg-[var(--canvas)]"
                        >
                            {/* Stars */}
                            <div className="flex gap-1 mb-6">
                                {[1, 2, 3, 4, 5].map((star) => (
                                    <span key={star}>
                                        {React.createElement(StarIcon as any, {
                                            className: "w-4 h-4 text-[var(--accent)]"
                                        })}
                                    </span>
                                ))}
                            </div>

                            {/* Quote */}
                            <p className="text-[var(--ink)] leading-relaxed mb-8">
                                "{testimonial.quote}"
                            </p>

                            {/* Author */}
                            <div className="flex items-center gap-3">
                                {/* Avatar */}
                                <div className="w-10 h-10 rounded-full bg-[var(--ink)] text-[var(--canvas)] flex items-center justify-center font-semibold text-sm">
                                    {testimonial.initials}
                                </div>
                                <div>
                                    <p className="font-semibold text-[var(--ink)]">{testimonial.name}</p>
                                    <p className="text-sm text-[var(--secondary)]">
                                        {testimonial.role}, {testimonial.company}
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
