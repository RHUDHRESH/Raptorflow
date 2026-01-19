"use client";

import React, { useState } from "react";
import { ArrowRight01Icon, PlayCircle02Icon } from "hugeicons-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { VideoModal } from "./VideoModal";
import { motion } from "framer-motion";

/**
 * HeroSection - Simplified, high-impact hero
 * Focus: Clear headline, prominent CTA, minimal distraction
 */
export function HeroSection() {
    const [isVideoOpen, setIsVideoOpen] = useState(false);

    return (
        <>
            <section className="relative w-full min-h-[85vh] flex items-center justify-center px-6 overflow-hidden bg-[var(--canvas)] border-b border-[var(--border)]">

                {/* Subtle background ambience */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[var(--accent)]/3 blur-[150px] rounded-full" />
                    <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-[var(--ink)]/3 blur-[120px] rounded-full" />
                </div>

                <div className="relative z-10 max-w-4xl mx-auto text-center">

                    {/* Eyebrow Badge */}
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--surface)] border border-[var(--border)] rounded-full mb-8"
                    >
                        <span className="w-2 h-2 rounded-full bg-[var(--accent)] animate-pulse" />
                        <span className="text-sm font-medium tracking-wide text-[var(--secondary)]">
                            Founder Marketing OS
                        </span>
                    </motion.div>

                    {/* Main Headline */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="text-5xl md:text-6xl lg:text-7xl font-editorial font-medium leading-[1.1] text-[var(--ink)] tracking-tight mb-6"
                    >
                        Marketing.{" "}
                        <span className="italic text-[var(--muted)]">Finally</span>{" "}
                        under control.
                    </motion.h1>

                    {/* Subheadline */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="text-lg md:text-xl text-[var(--secondary)] leading-relaxed max-w-2xl mx-auto mb-10"
                    >
                        Stop guessing what to post. Start executing a proven system.{" "}
                        <span className="text-[var(--ink)] font-medium">
                            One platform for strategy, content, and execution.
                        </span>
                    </motion.p>

                    {/* CTA Buttons - Prominent */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="flex flex-col sm:flex-row items-center justify-center gap-4"
                    >
                        <BlueprintButton
                            size="lg"
                            label="Start Free Trial"
                            variant="blueprint"
                            onClick={() => window.location.href = '/signup'}
                            className="group min-w-[200px]"
                        >
                            <span className="flex items-center gap-2">
                                Start Free Trial
                                {React.createElement(ArrowRight01Icon as any, {
                                    className: "w-5 h-5 transition-transform group-hover:translate-x-1"
                                })}
                            </span>
                        </BlueprintButton>

                        <button
                            onClick={() => setIsVideoOpen(true)}
                            className="flex items-center gap-3 px-6 py-3 text-[var(--ink)] hover:text-[var(--secondary)] transition-colors group"
                        >
                            <div className="relative flex items-center justify-center w-10 h-10 border border-[var(--border)] rounded-full group-hover:border-[var(--ink)] bg-[var(--canvas)] transition-colors">
                                {React.createElement(PlayCircle02Icon as any, { className: "w-5 h-5 text-[var(--ink)]" })}
                            </div>
                            <span className="text-sm font-medium">Watch Demo</span>
                        </button>
                    </motion.div>

                    {/* Trust note */}
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.6, delay: 0.5 }}
                        className="mt-8 text-sm text-[var(--muted)]"
                    >
                        14-day free trial. No credit card required. Cancel anytime.
                    </motion.p>
                </div>
            </section>

            {/* Video Modal */}
            <VideoModal isOpen={isVideoOpen} onClose={() => setIsVideoOpen(false)} />
        </>
    );
}
