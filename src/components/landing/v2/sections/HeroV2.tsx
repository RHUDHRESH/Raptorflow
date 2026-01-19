"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight01Icon } from "hugeicons-react";

import { AmbientBackground } from "../shared/GradientOrb";
import { ScrollIndicator } from "../shared/ScrollProgress";
import { AnimatedHeadline, MutedText } from "../shared/AnimatedHeadline";

// ═══════════════════════════════════════════════════════════════
// HeroV2 - Cinematic hero section
// ═══════════════════════════════════════════════════════════════

export function HeroV2() {
    const scrollToContent = () => {
        const systemSection = document.getElementById("system");
        if (systemSection) {
            systemSection.scrollIntoView({ behavior: "smooth" });
        }
    };

    return (
        <section className="relative min-h-screen flex items-center justify-center px-6 pt-20 overflow-hidden bg-[var(--canvas)]">
            {/* Ambient Background */}
            <AmbientBackground variant="hero" />

            {/* Main Content */}
            <div className="relative z-10 max-w-5xl mx-auto text-center">
                {/* Eyebrow Badge */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--surface)] border border-[var(--border)] rounded-full mb-10"
                >
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm text-[var(--secondary)]">
                        Now in public beta
                    </span>
                </motion.div>

                {/* Main Headline - TODO: Replace with dramatic animation */}
                <motion.h1
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                    className="text-6xl md:text-7xl lg:text-8xl font-editorial font-medium leading-[0.95] tracking-tight mb-8"
                >
                    Stop posting.
                    <br />
                    <MutedText>Start building.</MutedText>
                </motion.h1>

                {/* Subheadline */}
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2, duration: 0.5 }}
                    className="text-xl md:text-2xl text-[var(--secondary)] max-w-2xl mx-auto mb-12 leading-relaxed"
                >
                    The first operating system for{" "}
                    <span className="text-[var(--ink)] font-medium">
                        founder-led marketing
                    </span>
                    .
                    <br />
                    Strategy, content, and execution—unified at last.
                </motion.p>

                {/* CTA Buttons */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3, duration: 0.5 }}
                    className="flex flex-col sm:flex-row gap-4 justify-center mb-8"
                >
                    <Link
                        href="/signup"
                        className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-[var(--ink)] text-[var(--canvas)] text-lg font-medium rounded-xl hover:opacity-90 transition-all duration-200 hover:scale-[1.02]"
                    >
                        Start your free trial
                        {React.createElement(ArrowRight01Icon as any, {
                            className:
                                "w-5 h-5 group-hover:translate-x-1 transition-transform",
                        })}
                    </Link>
                    <Link
                        href="#how"
                        className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-[var(--border)] text-[var(--ink)] text-lg font-medium rounded-xl hover:border-[var(--ink)] transition-colors"
                    >
                        See how it works
                    </Link>
                </motion.div>

                {/* Trust Note */}
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 0.5 }}
                    className="text-sm text-[var(--muted)]"
                >
                    No credit card required · 14 days free · Cancel anytime
                </motion.p>
            </div>

            {/* Scroll Indicator - Editorial Style */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
                <ScrollIndicator onClick={scrollToContent} />
            </div>
        </section>
    );
}
