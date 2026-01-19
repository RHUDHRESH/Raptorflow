"use client";

import React from "react";
import { motion } from "framer-motion";

/**
 * Social Proof Bar - Trust indicator section after hero
 * Shows credibility markers without requiring real logos yet
 */
export function SocialProofBar() {
    return (
        <section className="py-12 bg-[var(--surface)] border-y border-[var(--border)]">
            <div className="max-w-7xl mx-auto px-6">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16"
                >
                    {/* Trust statement */}
                    <p className="text-sm font-medium text-[var(--secondary)] tracking-wide uppercase">
                        Trusted by 500+ founders building in public
                    </p>

                    {/* Placeholder logos - abstract shapes */}
                    <div className="flex items-center gap-8">
                        {[1, 2, 3, 4, 5].map((i) => (
                            <div
                                key={i}
                                className="w-20 h-6 bg-[var(--border)] rounded opacity-50"
                                style={{
                                    width: `${60 + i * 8}px`,
                                }}
                            />
                        ))}
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
