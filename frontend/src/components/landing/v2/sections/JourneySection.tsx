"use client";

import React from "react";
import { motion } from "framer-motion";

import { SectionWrapper, SectionHeader, ContentContainer } from "../shared/SectionWrapper";
import { fadeUp } from "../animations/presets";

// ═══════════════════════════════════════════════════════════════
// JourneySection - How It Works with scroll-driven reveal
// ═══════════════════════════════════════════════════════════════

const STEPS = [
    {
        step: "01",
        title: "Define your foundation",
        desc: "Answer strategic questions once. RaptorFlow builds your ICP, positioning, and 90-day execution plan automatically.",
        // TODO: Add illustration or product screenshot
    },
    {
        step: "02",
        title: "Execute weekly Moves",
        desc: "Every Monday, get a ready-to-ship packet: content, assets, and tasks. No more blank pages. Just execute.",
    },
    {
        step: "03",
        title: "Track what works",
        desc: "Matrix shows you signal, not noise. See what's driving pipeline. Double down on winners. Cut the rest.",
    },
];

export function JourneySection() {
    return (
        <SectionWrapper id="how">
            <ContentContainer>
                <SectionHeader
                    eyebrow="How It Works"
                    title={
                        <>
                            From chaos to clarity.
                            <br />
                            <span className="text-[var(--muted)]">In three steps.</span>
                        </>
                    }
                    centered
                />

                {/* Steps Grid */}
                <div className="grid md:grid-cols-3 gap-12">
                    {STEPS.map((item, i) => (
                        <motion.div
                            key={i}
                            variants={fadeUp}
                            className="text-center"
                        >
                            {/* Step Number - TODO: Add counter animation */}
                            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                                <span className="text-2xl font-mono font-bold text-[var(--ink)]">
                                    {item.step}
                                </span>
                            </div>

                            {/* Title */}
                            <h3 className="text-xl font-bold mb-3 text-[var(--ink)]">
                                {item.title}
                            </h3>

                            {/* Description */}
                            <p className="text-[var(--secondary)] leading-relaxed">
                                {item.desc}
                            </p>
                        </motion.div>
                    ))}
                </div>

                {/* TODO: Add connecting line/arrows between steps */}
                {/* TODO: Add progress indicator synced to scroll */}
            </ContentContainer>
        </SectionWrapper>
    );
}
