"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    BoardMathIcon,
    Analytics01Icon,
    Target02Icon,
    Layers01Icon,
    Settings01Icon,
    Message01Icon,
} from "hugeicons-react";

import { SectionWrapper, SectionHeader, ContentContainer } from "../shared/SectionWrapper";
import { fadeUp } from "../animations/presets";

// ═══════════════════════════════════════════════════════════════
// SystemGrid - Interactive module showcase
// ═══════════════════════════════════════════════════════════════

interface Module {
    name: string;
    tag: string;
    desc: string;
    icon: any;
    details?: string;
}

const MODULES: Module[] = [
    {
        name: "Foundation",
        tag: "Strategy",
        icon: Target02Icon,
        desc: "Define your ICP, positioning, and messaging once. Use it everywhere.",
        details: "Build your 90-day war plan in 20 minutes. Never start from scratch again.",
    },
    {
        name: "Cohorts",
        tag: "Intelligence",
        icon: Layers01Icon,
        desc: "Segment by behavior, not demographics. Know exactly who converts—and why.",
        details: "Target with surgical precision. Stop wasting budget on the wrong audience.",
    },
    {
        name: "Moves",
        tag: "Execution",
        icon: BoardMathIcon,
        desc: "Get weekly execution packets delivered every Monday.",
        details: "Content drafted. Tasks clear. Just ship. No more blank page syndrome.",
    },
    {
        name: "Muse",
        tag: "Creation",
        icon: Message01Icon,
        desc: "Generate content that sounds like you, not a robot.",
        details: "Train it on your voice. Scale your ideas without losing authenticity.",
    },
    {
        name: "Matrix",
        tag: "Analytics",
        icon: Analytics01Icon,
        desc: "Signal, not noise. See what's actually driving pipeline.",
        details: "Cut what isn't working. Decide in seconds, not hours.",
    },
    {
        name: "Blackbox",
        tag: "Memory",
        icon: Settings01Icon,
        desc: "Never lose a learning. Every experiment, every outcome.",
        details: "Your permanent vault of marketing intelligence. Preserved forever.",
    },
];

export function SystemGrid() {
    const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

    return (
        <SectionWrapper id="system" variant="surface" bordered>
            <ContentContainer>
                <SectionHeader
                    eyebrow="The System"
                    title={
                        <>
                            Six modules.
                            <br />
                            <span className="text-[var(--muted)]">One operating system.</span>
                        </>
                    }
                    subtitle="Everything you need to go from strategy to execution. No more tool-switching. No more context-switching."
                />

                {/* Module Grid */}
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {MODULES.map((module, i) => (
                        <motion.div
                            key={i}
                            variants={fadeUp}
                            onClick={() =>
                                setExpandedIndex(expandedIndex === i ? null : i)
                            }
                            className={`
                group relative p-8 rounded-2xl border cursor-pointer
                bg-[var(--canvas)] transition-all duration-300
                ${expandedIndex === i
                                    ? "border-[var(--ink)] shadow-lg"
                                    : "border-[var(--border)] hover:border-[var(--ink)]/30"
                                }
              `}
                        >
                            {/* Tag */}
                            <span className="inline-block px-2 py-1 text-xs uppercase tracking-wider text-[var(--muted)] bg-[var(--surface)] rounded mb-4">
                                {module.tag}
                            </span>

                            {/* Icon + Title */}
                            <div className="flex items-start gap-4 mb-3">
                                <div className="w-10 h-10 rounded-xl bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center flex-shrink-0">
                                    {React.createElement(module.icon as any, {
                                        className: "w-5 h-5 text-[var(--ink)]",
                                    })}
                                </div>
                                <h3 className="text-2xl font-bold group-hover:text-[var(--accent)] transition-colors">
                                    {module.name}
                                </h3>
                            </div>

                            {/* Description */}
                            <p className="text-[var(--secondary)] leading-relaxed mb-2">
                                {module.desc}
                            </p>

                            {/* Expanded Details - TODO: Smooth expand animation */}
                            <AnimatePresence>
                                {expandedIndex === i && module.details && (
                                    <motion.p
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                        transition={{ duration: 0.2 }}
                                        className="text-sm text-[var(--muted)] mt-2 pt-2 border-t border-[var(--border)]"
                                    >
                                        {module.details}
                                    </motion.p>
                                )}
                            </AnimatePresence>

                            {/* Click indicator */}
                            <div className="absolute bottom-4 right-4 text-xs text-[var(--muted)] opacity-0 group-hover:opacity-100 transition-opacity">
                                {expandedIndex === i ? "Click to collapse" : "Click to expand"}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </ContentContainer>
        </SectionWrapper>
    );
}
