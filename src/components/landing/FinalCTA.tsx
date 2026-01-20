"use client";

import React from "react";
import { motion } from "framer-motion";
import { ArrowRight01Icon } from "hugeicons-react";
import Link from "next/link";

/**
 * FinalCTA - Strong pre-footer call to action section
 * Compelling final push before the footer
 */
export function FinalCTA() {
    return (
        <section className="py-24 md:py-32 bg-[var(--ink)]">
            <div className="max-w-4xl mx-auto px-6 text-center">

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                >
                    {/* Headline */}
                    <h2 className="text-4xl md:text-5xl lg:text-6xl font-editorial text-[var(--canvas)] mb-6 leading-tight">
                        Stop shouting into the void.
                    </h2>

                    {/* Subtext */}
                    <p className="text-lg md:text-xl text-[var(--canvas)]/70 mb-10 max-w-2xl mx-auto leading-relaxed">
                        Join 500+ founders who replaced "marketing by vibes" with a system that tracks every dollar and every Move.
                    </p>

                    {/* CTA Buttons */}
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link
                            href="/signup"
                            className="group inline-flex items-center gap-2 px-8 py-4 bg-[var(--canvas)] text-[var(--ink)] font-semibold rounded-xl hover:bg-[var(--canvas)]/90 transition-all"
                        >
                            Initialize Your OS
                            {React.createElement(ArrowRight01Icon as any, {
                                className: "w-5 h-5 transition-transform group-hover:translate-x-1"
                            })}
                        </Link>

                        <Link
                            href="#pricing"
                            className="inline-flex items-center gap-2 px-8 py-4 text-[var(--canvas)]/80 hover:text-[var(--canvas)] font-medium transition-colors"
                        >
                            View Pricing
                        </Link>
                    </div>

                    {/* Trust note */}
                    <p className="mt-8 text-sm text-[var(--canvas)]/50">
                        14-day free trial. No credit card required.
                    </p>
                </motion.div>
            </div>
        </section>
    );
}
