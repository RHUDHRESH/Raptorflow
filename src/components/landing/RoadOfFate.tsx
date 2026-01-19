"use client";

import React, { useState, useRef } from "react";
import { motion, useScroll, useTransform, useSpring, AnimatePresence } from "framer-motion";
import {
    Alert02Icon,
    CheckmarkCircle02Icon,
    Analytics01Icon,
    Rocket01Icon,
    Cancel01Icon,
    Search01Icon
} from "hugeicons-react";

const MILESTONES = [
    {
        stage: "The Strategy",
        left: {
            title: "Guessing Game",
            desc: "Throwing random posts at LinkedIn. Targeting 'everyone'. Hoping for viral luck.",
            expandedDesc: "You spend hours crafting posts with no data. You target 'founders' hoping someone bites. There's no system, just vibes.",
            icon: Search01Icon,
        },
        right: {
            title: "Precision Foundation",
            desc: "ICP defined. Positioning locked. 90-day war plan generated instantly.",
            expandedDesc: "RaptorFlow's onboarding builds your ICP, messaging framework, and strategic calendar in under 20 minutes. No guesswork.",
            icon: Rocket01Icon,
        }
    },
    {
        stage: "The Execution",
        left: {
            title: "Tool Hell",
            desc: "5 different subscriptions. Copy-pasting data. Context switching fatigue.",
            expandedDesc: "Notion for tasks, Buffer for scheduling, ChatGPT for writing, Google Sheets for tracking. All disconnected. All wasting your time.",
            icon: Alert02Icon,
        },
        right: {
            title: "Unified Moves",
            desc: "One dashboard. Weekly execution packets. Content, assets, and tasks in one view.",
            expandedDesc: "Every Monday, Moves delivers your week's marketing tasks: ready-to-post content, email drafts, and clear priorities. Just ship.",
            icon: CheckmarkCircle02Icon,
        }
    },
    {
        stage: "The Outcome",
        left: {
            title: "Radio Silence",
            desc: "No leads. Burnout. 'Marketing doesn't work for us'.",
            expandedDesc: "After 6 months of effort, you have 12 followers and zero pipeline. You conclude marketing is broken. Your startup dies.",
            icon: Cancel01Icon,
        },
        right: {
            title: "Compounding Growth",
            desc: "Data-backed iterations. Pipeline velocity. Predictable revenue.",
            expandedDesc: "Matrix shows you what's actually driving pipeline. You double down on what works. Revenue becomes predictable.",
            icon: Analytics01Icon,
        }
    }
];

function MilestoneNode({
    data,
    side,
    index
}: {
    data: typeof MILESTONES[0]["left"];
    side: "left" | "right";
    index: number;
}) {
    const [isExpanded, setIsExpanded] = useState(false);
    const isFailure = side === "left";

    return (
        <motion.div
            initial={{ opacity: 0, x: isFailure ? -50 : 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ delay: index * 0.15 }}
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => setIsExpanded(false)}
            className={`relative p-6 md:p-8 rounded-2xl border transition-all duration-500 cursor-pointer ${isFailure
                    ? "border-red-200/30 bg-red-50/5 hover:bg-red-50/10 hover:border-red-300/50 hover:shadow-lg hover:shadow-red-500/5"
                    : "border-[var(--border)] bg-[var(--surface)] hover:border-[var(--accent)] hover:shadow-xl hover:shadow-[var(--accent)]/10"
                } ${side === "left" ? "md:text-right" : ""}`}
        >
            <div className={`flex flex-col gap-4 ${side === "left" ? "md:items-end" : "items-start"}`}>
                <div className={`p-3 rounded-xl w-fit ${isFailure
                        ? "bg-red-100/20 text-red-400"
                        : "bg-[var(--accent)]/10 text-[var(--accent)]"
                    }`}>
                    {React.createElement(data.icon as any, { className: "w-6 h-6" })}
                </div>
                <div>
                    <h3 className={`text-xl font-bold mb-2 transition-colors ${isFailure
                            ? "text-[var(--secondary)] group-hover:text-red-500"
                            : "text-[var(--ink)]"
                        }`}>
                        {data.title}
                    </h3>
                    <p className={`leading-relaxed transition-colors ${isFailure
                            ? "text-[var(--muted)] font-mono text-sm"
                            : "text-[var(--secondary)]"
                        }`}>
                        {data.desc}
                    </p>
                </div>
            </div>

            {/* Expanded Tooltip */}
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className={`absolute ${side === "left" ? "right-0 md:right-full md:mr-4" : "left-0 md:left-full md:ml-4"} top-1/2 -translate-y-1/2 z-20 w-64 p-4 rounded-xl border shadow-2xl ${isFailure
                                ? "bg-[#1a0a0a] border-red-500/30 text-red-200"
                                : "bg-[var(--ink)] border-[var(--accent)]/30 text-[var(--canvas)]"
                            }`}
                    >
                        <div className="text-xs uppercase tracking-widest mb-2 opacity-60">
                            {isFailure ? "The Reality" : "With RaptorFlow"}
                        </div>
                        <p className="text-sm leading-relaxed">
                            {data.expandedDesc}
                        </p>
                        {/* Arrow */}
                        <div className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 rotate-45 ${isFailure ? "bg-[#1a0a0a] border-red-500/30" : "bg-[var(--ink)] border-[var(--accent)]/30"
                            } ${side === "left" ? "-right-1.5 border-r border-t" : "-left-1.5 border-l border-b"}`} />
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

export function RoadOfFate() {
    const containerRef = useRef<HTMLDivElement>(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end center"]
    });

    const lineHeight = useSpring(useTransform(scrollYProgress, [0, 1], ["0%", "100%"]), {
        stiffness: 50,
        damping: 15
    });

    return (
        <section ref={containerRef} className="relative py-32 bg-[var(--canvas)] overflow-hidden">

            <div className="max-w-7xl mx-auto px-6 relative">

                {/* Header */}
                <div className="text-center mb-24">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-4xl md:text-5xl font-editorial text-[var(--ink)] mb-6"
                    >
                        Two paths. <span className="italic text-[var(--muted)]">One choice.</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-lg text-[var(--secondary)] max-w-2xl mx-auto"
                    >
                        Most founders walk the path of chaos. RaptorFlow builds you a highway to revenue.
                        <span className="block mt-2 text-sm text-[var(--muted)]">Hover over each step to see the full story.</span>
                    </motion.p>
                </div>

                {/* The Road Container */}
                <div className="relative">

                    {/* Central Spine with Glow */}
                    <div className="hidden md:block absolute left-1/2 top-0 bottom-0 -translate-x-1/2 w-1">
                        {/* Background Track */}
                        <div className="absolute inset-0 bg-[var(--border)]/30 rounded-full" />

                        {/* Animated Glowing Fill */}
                        <motion.div
                            style={{ height: lineHeight }}
                            className="relative w-full bg-gradient-to-b from-[var(--accent)] to-[var(--ink)] origin-top rounded-full"
                        >
                            {/* Glow Effect */}
                            <div className="absolute inset-0 bg-[var(--accent)] blur-md opacity-50 rounded-full" />
                            <div className="absolute inset-0 bg-[var(--accent)] blur-lg opacity-30 rounded-full" />

                            {/* Pulsing Head */}
                            <motion.div
                                animate={{ scale: [1, 1.5, 1], opacity: [0.8, 1, 0.8] }}
                                transition={{ duration: 2, repeat: Infinity }}
                                className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-4 h-4 bg-[var(--accent)] rounded-full shadow-[0_0_20px_var(--accent)]"
                            />
                        </motion.div>
                    </div>

                    {/* Milestones Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-[1fr_60px_1fr] gap-8 md:gap-0">
                        {MILESTONES.map((milestone, i) => (
                            <React.Fragment key={i}>
                                {/* Left Side (Failure) */}
                                <div className="md:pr-8">
                                    <MilestoneNode data={milestone.left} side="left" index={i} />
                                </div>

                                {/* Center Node */}
                                <div className="hidden md:flex items-center justify-center relative z-10 py-8">
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        whileInView={{ scale: 1 }}
                                        viewport={{ once: true }}
                                        className="w-12 h-12 rounded-full bg-[var(--canvas)] border-2 border-[var(--border)] flex items-center justify-center shadow-lg"
                                    >
                                        <span className="text-sm font-bold text-[var(--ink)] font-mono">0{i + 1}</span>
                                    </motion.div>
                                </div>

                                {/* Right Side (Success) */}
                                <div className="md:pl-8">
                                    <MilestoneNode data={milestone.right} side="right" index={i} />
                                </div>
                            </React.Fragment>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
