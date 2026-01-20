"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

interface Chapter {
    title: string;
    description: string;
    emoji: string;
    color: string;
}

const CHAPTERS: Chapter[] = [
    {
        title: "The Chaos",
        emoji: "😵",
        description: "Juggling 5 tools, guessing what works, staring at blank docs every Monday.",
        color: "from-red-500/20 to-orange-500/20"
    },
    {
        title: "Discovery",
        emoji: "💡",
        description: "You hear about RaptorFlow. An OS for marketing? That's different.",
        color: "from-yellow-500/20 to-amber-500/20"
    },
    {
        title: "Foundation",
        emoji: "🏗️",
        description: "20 minutes to define ICP, positioning, and voice. The clarity hits different.",
        color: "from-blue-500/20 to-cyan-500/20"
    },
    {
        title: "Execution",
        emoji: "🚀",
        description: "Weekly Moves arrive. You ship 3x more, with half the effort.",
        color: "from-purple-500/20 to-violet-500/20"
    },
    {
        title: "Mastery",
        emoji: "🎯",
        description: "Pipeline grows. Audience compounds. Marketing finally feels like a system.",
        color: "from-green-500/20 to-emerald-500/20"
    }
];

function ChapterBlock({
    chapter,
    index,
    progress
}: {
    chapter: Chapter;
    index: number;
    progress: any;
}) {
    const start = index / CHAPTERS.length;
    const end = (index + 1) / CHAPTERS.length;
    const mid = (start + end) / 2;

    const opacity = useTransform(
        progress,
        [start, mid - 0.05, mid, mid + 0.05, end],
        [0.3, 1, 1, 1, 0.3]
    );

    const y = useTransform(
        progress,
        [start, mid, end],
        [50, 0, -50]
    );

    const scale = useTransform(
        progress,
        [start, mid, end],
        [0.9, 1, 0.9]
    );

    return (
        <motion.div
            style={{ opacity, y, scale }}
            className="flex items-center gap-8"
        >
            {/* Chapter number */}
            <div className="flex-shrink-0 w-16 h-16 rounded-full border-2 border-[var(--border)] flex items-center justify-center text-2xl">
                {chapter.emoji}
            </div>

            {/* Content */}
            <div className={`flex-1 p-6 rounded-2xl bg-gradient-to-r ${chapter.color}`}>
                <h3 className="text-xl font-bold mb-2">{chapter.title}</h3>
                <p className="text-[var(--secondary)]">{chapter.description}</p>
            </div>
        </motion.div>
    );
}

export default function ScrollStoryTimeline() {
    const containerRef = useRef<HTMLDivElement>(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"]
    });

    // Progress bar
    const progressWidth = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);

    // Current chapter index
    const currentChapter = useTransform(
        scrollYProgress,
        [0, 1],
        [0, CHAPTERS.length - 1]
    );

    return (
        <div ref={containerRef} className="relative py-20">
            {/* Fixed progress bar */}
            <div className="sticky top-24 z-10 mb-12">
                <div className="max-w-2xl mx-auto px-6">
                    <div className="h-1 bg-[var(--border)] rounded-full overflow-hidden">
                        <motion.div
                            className="h-full bg-gradient-to-r from-[var(--rf-coral)] via-[var(--rf-ocean)] to-[var(--rf-mint)]"
                            style={{ width: progressWidth }}
                        />
                    </div>

                    {/* Chapter markers */}
                    <div className="flex justify-between mt-2">
                        {CHAPTERS.map((chapter, i) => (
                            <motion.span
                                key={i}
                                className="text-xs text-[var(--muted)]"
                                style={{
                                    opacity: useTransform(
                                        scrollYProgress,
                                        [(i - 0.5) / CHAPTERS.length, i / CHAPTERS.length, (i + 0.5) / CHAPTERS.length],
                                        [0.4, 1, 0.4]
                                    )
                                }}
                            >
                                {chapter.emoji}
                            </motion.span>
                        ))}
                    </div>
                </div>
            </div>

            {/* Chapters */}
            <div className="max-w-2xl mx-auto px-6 space-y-32">
                {CHAPTERS.map((chapter, index) => (
                    <ChapterBlock
                        key={chapter.title}
                        chapter={chapter}
                        index={index}
                        progress={scrollYProgress}
                    />
                ))}
            </div>

            {/* End state */}
            <motion.div
                className="mt-20 text-center"
                style={{
                    opacity: useTransform(scrollYProgress, [0.8, 1], [0, 1])
                }}
            >
                <p className="text-2xl font-editorial">
                    Ready to write your story?
                </p>
            </motion.div>
        </div>
    );
}
